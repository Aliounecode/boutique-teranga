"""
Endpoints de la caisse (ventes physiques / POS).
Chemin : backend/app/routeurs/ventes.py

Creer / lister / consulter : gerant ou vendeur.
Annuler (rembourse le stock) : gerant uniquement.
"""
from datetime import date, datetime, time, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.base_donnees import obtenir_session
from app.modeles import LigneVente, Utilisateur, Vente
from app.modeles.enumerations import StatutVente
from app.schemas.vente import VenteCreation, VenteLecture, VentePage, VenteResume
from app.securite.dependances import exiger_gerant, exiger_gerant_ou_vendeur
from app.services import service_stock, service_vente
from app.utils.pagination import calculer_bornes

routeur = APIRouter(prefix="/ventes", tags=["Ventes (caisse)"])

Session_ = Annotated[Session, Depends(obtenir_session)]
GerantOuVendeur_ = Annotated[Utilisateur, Depends(exiger_gerant_ou_vendeur)]
Gerant_ = Annotated[Utilisateur, Depends(exiger_gerant)]


def _resume_vente(vente: Vente) -> VenteResume:
    return VenteResume(
        id=vente.id,
        numero=vente.numero,
        date_vente=vente.date_vente,
        client_nom=(vente.client.nom if vente.client else None),
        montant_total=vente.montant_total,
        statut=vente.statut,
        nombre_articles=sum(ligne.quantite for ligne in vente.lignes),
    )


# --- Création d'une vente (caisse) ------------------------------------------
@routeur.post("", response_model=VenteLecture, status_code=status.HTTP_201_CREATED)
def creer_vente(donnees: VenteCreation, session: Session_, utilisateur: GerantOuVendeur_):
    try:
        vente = service_vente.enregistrer_vente(session, donnees, utilisateur.id)
        vente_id = vente.id
        session.commit()
    except service_vente.VenteErreur as erreur:
        session.rollback()
        raise HTTPException(status_code=erreur.code, detail=str(erreur))
    return service_vente.charger_vente(session, vente_id)


# --- Liste des ventes --------------------------------------------------------
@routeur.get("", response_model=VentePage, dependencies=[Depends(exiger_gerant_ou_vendeur)])
def lister_ventes(
    session: Session_,
    date_debut: date | None = None,
    date_fin: date | None = None,
    client_id: int | None = None,
    statut: StatutVente | None = None,
    page: int = Query(default=1, ge=1),
    taille_page: int = Query(default=20, ge=1, le=100),
):
    requete = select(Vente)
    if statut is not None:
        requete = requete.where(Vente.statut == statut)
    if client_id is not None:
        requete = requete.where(Vente.client_id == client_id)
    if date_debut is not None:
        requete = requete.where(Vente.date_vente >= datetime.combine(date_debut, time.min))
    if date_fin is not None:
        requete = requete.where(Vente.date_vente < datetime.combine(date_fin + timedelta(days=1), time.min))

    total = session.scalar(select(func.count()).select_from(requete.subquery())) or 0
    limite, decalage = calculer_bornes(page, taille_page)
    ventes = session.scalars(
        requete.order_by(Vente.date_vente.desc(), Vente.id.desc())
        .options(joinedload(Vente.client), selectinload(Vente.lignes))
        .limit(limite)
        .offset(decalage)
    ).all()

    return VentePage(
        total=total, page=page, taille_page=taille_page,
        elements=[_resume_vente(v) for v in ventes],
    )


# --- Détail d'une vente ------------------------------------------------------
@routeur.get("/{vente_id}", response_model=VenteLecture, dependencies=[Depends(exiger_gerant_ou_vendeur)])
def obtenir_vente(vente_id: int, session: Session_):
    try:
        return service_vente.charger_vente(session, vente_id)
    except service_vente.VenteErreur as erreur:
        raise HTTPException(status_code=erreur.code, detail=str(erreur))


# --- Annulation (rembourse le stock) ----------------------------------------
@routeur.post("/{vente_id}/annuler", response_model=VenteLecture)
def annuler_vente(vente_id: int, session: Session_, gerant: Gerant_):
    vente = session.get(Vente, vente_id)
    if vente is None:
        raise HTTPException(status_code=404, detail="Vente introuvable")
    if vente.statut == StatutVente.ANNULEE:
        raise HTTPException(status_code=409, detail="Cette vente est deja annulee")

    lignes = session.scalars(select(LigneVente).where(LigneVente.vente_id == vente_id)).all()
    for ligne in lignes:
        service_stock.retourner(
            session, ligne.variante_id, ligne.quantite,
            utilisateur_id=gerant.id,
            motif=f"Annulation vente {vente.numero}",
            reference_document=vente.numero,
        )
    vente.statut = StatutVente.ANNULEE
    session.commit()
    return service_vente.charger_vente(session, vente_id)