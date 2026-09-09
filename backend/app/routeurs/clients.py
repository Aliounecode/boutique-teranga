"""
Endpoints de gestion des clients.
Chemin : backend/app/routeurs/clients.py

Lister / consulter / creer / modifier : gerant ou vendeur (utile en caisse).
Supprimer : gerant uniquement (refuse si le client a des ventes).
"""
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.modeles import Client, Vente
from app.modeles.enumerations import StatutVente
from app.schemas.client import (
    ClientCreation,
    ClientDetail,
    ClientLecture,
    ClientMiseAJour,
    ClientPage,
)
from app.securite.dependances import exiger_gerant, exiger_gerant_ou_vendeur
from app.utils.pagination import calculer_bornes

routeur = APIRouter(prefix="/clients", tags=["Clients"])

Session_ = Annotated[Session, Depends(obtenir_session)]


def _obtenir_client(session: Session, client_id: int) -> Client:
    client = session.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client introuvable")
    return client


def _statistiques_client(session: Session, client_id: int) -> tuple[int, Decimal]:
    """Retourne (nombre d'achats valides, total depense) pour un client."""
    nombre = session.scalar(
        select(func.count()).select_from(Vente).where(
            Vente.client_id == client_id, Vente.statut == StatutVente.VALIDEE
        )
    ) or 0
    total = session.scalar(
        select(func.coalesce(func.sum(Vente.montant_total), 0)).where(
            Vente.client_id == client_id, Vente.statut == StatutVente.VALIDEE
        )
    )
    return nombre, Decimal(total)


# --- Liste / recherche -------------------------------------------------------
@routeur.get("", response_model=ClientPage, dependencies=[Depends(exiger_gerant_ou_vendeur)])
def lister(
    session: Session_,
    recherche: str | None = None,
    inclure_inactifs: bool = False,
    page: int = Query(default=1, ge=1),
    taille_page: int = Query(default=20, ge=1, le=100),
):
    requete = select(Client)
    if not inclure_inactifs:
        requete = requete.where(Client.actif.is_(True))
    if recherche and recherche.strip():
        motif = f"%{recherche.strip()}%"
        requete = requete.where(or_(
            Client.nom.ilike(motif),
            Client.prenom.ilike(motif),
            Client.telephone.ilike(motif),
        ))

    total = session.scalar(select(func.count()).select_from(requete.subquery())) or 0
    limite, decalage = calculer_bornes(page, taille_page)
    clients = session.scalars(
        requete.order_by(Client.nom.asc(), Client.id.asc()).limit(limite).offset(decalage)
    ).all()
    return ClientPage(total=total, page=page, taille_page=taille_page, elements=clients)


# --- Detail (avec statistiques) ---------------------------------------------
@routeur.get("/{client_id}", response_model=ClientDetail, dependencies=[Depends(exiger_gerant_ou_vendeur)])
def obtenir(client_id: int, session: Session_):
    client = _obtenir_client(session, client_id)
    nombre, total = _statistiques_client(session, client_id)
    return ClientDetail(
        id=client.id, nom=client.nom, prenom=client.prenom, telephone=client.telephone,
        actif=client.actif, date_creation=client.date_creation,
        nombre_achats=nombre, total_depense=total,
    )


# --- Creation / modification (gerant ou vendeur) -----------------------------
@routeur.post("", response_model=ClientLecture, status_code=status.HTTP_201_CREATED,
              dependencies=[Depends(exiger_gerant_ou_vendeur)])
def creer(donnees: ClientCreation, session: Session_):
    client = Client(
        nom=donnees.nom.strip(),
        prenom=(donnees.prenom or "").strip() or None,
        telephone=(donnees.telephone or "").strip() or None,
        actif=True,
    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


@routeur.patch("/{client_id}", response_model=ClientLecture,
               dependencies=[Depends(exiger_gerant_ou_vendeur)])
def mettre_a_jour(client_id: int, donnees: ClientMiseAJour, session: Session_):
    client = _obtenir_client(session, client_id)
    champs = donnees.model_dump(exclude_unset=True)
    if "nom" in champs:
        client.nom = champs["nom"].strip()
    if "prenom" in champs:
        client.prenom = (champs["prenom"] or "").strip() or None
    if "telephone" in champs:
        client.telephone = (champs["telephone"] or "").strip() or None
    if "actif" in champs:
        client.actif = champs["actif"]
    session.commit()
    session.refresh(client)
    return client


# --- Suppression (gerant uniquement) ----------------------------------------
@routeur.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT,
                dependencies=[Depends(exiger_gerant)])
def supprimer(client_id: int, session: Session_):
    client = _obtenir_client(session, client_id)
    nb_ventes = session.scalar(
        select(func.count()).select_from(Vente).where(Vente.client_id == client_id)
    )
    if nb_ventes:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Suppression impossible : ce client a des ventes. Desactivez-le (actif=false) plutot.",
        )
    session.delete(client)
    session.commit()