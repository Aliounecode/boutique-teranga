"""
Endpoints des commandes en ligne.
Chemin : backend/app/routeurs/commandes.py

Passer une commande : PUBLIC (le client de la boutique n'a pas de compte).
Lister / consulter / accepter / refuser / annuler : gerant uniquement.
"""
from datetime import date, datetime, time, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.base_donnees import obtenir_session
from app.modeles import Commande, Utilisateur ,Client
from app.modeles.enumerations import StatutCommande
from app.schemas.commande import (
    CommandeCreation,
    CommandeLecture,
    CommandePage,
    CommandeResume,
)
from app.securite.dependances import exiger_gerant , client_courant_optionnel
from app.services import service_commande
from app.utils.pagination import calculer_bornes

routeur = APIRouter(prefix="/commandes", tags=["Commandes en ligne"])

Session_ = Annotated[Session, Depends(obtenir_session)]
Gerant_ = Annotated[Utilisateur, Depends(exiger_gerant)]


def _resume_commande(commande: Commande) -> CommandeResume:
    return CommandeResume(
        id=commande.id,
        numero=commande.numero,
        date_commande=commande.date_commande,
        client_nom=commande.client_nom,
        client_telephone=commande.client_telephone,
        moyen_paiement=commande.moyen_paiement,
        montant_total=commande.montant_total,
        statut=commande.statut,
        nombre_articles=sum(ligne.quantite for ligne in commande.lignes),
    )


# --- Passer une commande (PUBLIC) -------------------------------------------
@routeur.post("", response_model=CommandeLecture, status_code=status.HTTP_201_CREATED)
def creer_commande(
    donnees: CommandeCreation,
    session: Session_,
    client: Annotated[Client | None, Depends(client_courant_optionnel)] = None,
):
    try:
        commande = service_commande.enregistrer_commande(
            session, donnees, client_id=client.id if client else None
        )
        commande_id = commande.id
        session.commit()
    except service_commande.CommandeErreur as erreur:
        session.rollback()
        raise HTTPException(status_code=erreur.code, detail=str(erreur))
    return service_commande.charger_commande(session, commande_id)

# --- Liste (gerant) ----------------------------------------------------------
@routeur.get("", response_model=CommandePage, dependencies=[Depends(exiger_gerant)])
def lister_commandes(
    session: Session_,
    statut: StatutCommande | None = None,
    date_debut: date | None = None,
    date_fin: date | None = None,
    page: int = Query(default=1, ge=1),
    taille_page: int = Query(default=20, ge=1, le=100),
):
    requete = select(Commande)
    if statut is not None:
        requete = requete.where(Commande.statut == statut)
    if date_debut is not None:
        requete = requete.where(Commande.date_commande >= datetime.combine(date_debut, time.min))
    if date_fin is not None:
        requete = requete.where(Commande.date_commande < datetime.combine(date_fin + timedelta(days=1), time.min))

    total = session.scalar(select(func.count()).select_from(requete.subquery())) or 0
    limite, decalage = calculer_bornes(page, taille_page)
    commandes = session.scalars(
        requete.order_by(Commande.date_commande.desc(), Commande.id.desc())
        .options(selectinload(Commande.lignes))
        .limit(limite)
        .offset(decalage)
    ).all()

    return CommandePage(
        total=total, page=page, taille_page=taille_page,
        elements=[_resume_commande(c) for c in commandes],
    )


# --- Détail (gerant) ---------------------------------------------------------
@routeur.get("/{commande_id}", response_model=CommandeLecture, dependencies=[Depends(exiger_gerant)])
def obtenir_commande(commande_id: int, session: Session_):
    try:
        return service_commande.charger_commande(session, commande_id)
    except service_commande.CommandeErreur as erreur:
        raise HTTPException(status_code=erreur.code, detail=str(erreur))


# --- Actions du gerant -------------------------------------------------------
def _appliquer_action(action, session: Session, commande_id: int, gerant: Utilisateur) -> CommandeLecture:
    try:
        action(session, commande_id, gerant.id)
        session.commit()
    except service_commande.CommandeErreur as erreur:
        session.rollback()
        raise HTTPException(status_code=erreur.code, detail=str(erreur))
    return service_commande.charger_commande(session, commande_id)


@routeur.post("/{commande_id}/accepter", response_model=CommandeLecture)
def accepter_commande(commande_id: int, session: Session_, gerant: Gerant_):
    return _appliquer_action(service_commande.accepter_commande, session, commande_id, gerant)


@routeur.post("/{commande_id}/refuser", response_model=CommandeLecture)
def refuser_commande(commande_id: int, session: Session_, gerant: Gerant_):
    return _appliquer_action(service_commande.refuser_commande, session, commande_id, gerant)


@routeur.post("/{commande_id}/annuler", response_model=CommandeLecture)
def annuler_commande(commande_id: int, session: Session_, gerant: Gerant_):
    return _appliquer_action(service_commande.annuler_commande, session, commande_id, gerant)