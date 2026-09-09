"""
Endpoints de gestion du stock (reserves au gerant).
Chemin : backend/app/routeurs/stock.py

- Reapprovisionnement et correction : audites (chaque operation ecrit un
  MouvementStock et enregistre l'utilisateur).
- Historique des mouvements : tracabilite complete, filtrable.
- Alertes : produits en rupture ou proches de la rupture.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.modeles import MouvementStock, Produit, Utilisateur, VarianteProduit
from app.modeles.enumerations import TypeMouvementStock
from app.schemas.mouvement_stock import (
    AlerteStock,
    DemandeCorrection,
    DemandeReapprovisionnement,
    MouvementLecture,
    MouvementPage,
)
from app.securite.dependances import exiger_gerant
from app.services import service_stock
from app.utils.pagination import calculer_bornes

routeur = APIRouter(prefix="/stock", tags=["Stock"])

Session_ = Annotated[Session, Depends(obtenir_session)]
Gerant_ = Annotated[Utilisateur, Depends(exiger_gerant)]


def _requete_mouvements_jointe():
    return (
        select(MouvementStock, VarianteProduit, Produit)
        .join(VarianteProduit, MouvementStock.variante_id == VarianteProduit.id)
        .join(Produit, VarianteProduit.produit_id == Produit.id)
    )


def _ligne_en_lecture(mouvement: MouvementStock, variante: VarianteProduit, produit: Produit) -> MouvementLecture:
    return MouvementLecture(
        id=mouvement.id,
        date_mouvement=mouvement.date_mouvement,
        type_mouvement=mouvement.type_mouvement,
        quantite=mouvement.quantite,
        quantite_avant=mouvement.quantite_avant,
        quantite_apres=mouvement.quantite_apres,
        motif=mouvement.motif,
        reference_document=mouvement.reference_document,
        variante_id=variante.id,
        produit_id=produit.id,
        produit_nom=produit.nom,
        reference_variante=variante.reference_variante,
        couleur=variante.couleur,
        taille=variante.taille,
        utilisateur_id=mouvement.utilisateur_id,
    )


def _charger_mouvement(session: Session, mouvement_id: int) -> MouvementLecture:
    ligne = session.execute(
        _requete_mouvements_jointe().where(MouvementStock.id == mouvement_id)
    ).one()
    return _ligne_en_lecture(*ligne)


def _traduire_erreur(erreur: service_stock.ErreurStock) -> HTTPException:
    if isinstance(erreur, service_stock.VarianteIntrouvable):
        return HTTPException(status_code=404, detail=str(erreur))
    return HTTPException(status_code=409, detail=str(erreur))


# --- Réapprovisionnement -----------------------------------------------------
@routeur.post("/reapprovisionner", response_model=MouvementLecture, status_code=status.HTTP_201_CREATED)
def reapprovisionner(demande: DemandeReapprovisionnement, session: Session_, gerant: Gerant_):
    try:
        mouvement = service_stock.reapprovisionner(
            session, demande.variante_id, demande.quantite,
            utilisateur_id=gerant.id, motif=demande.motif,
        )
    except service_stock.ErreurStock as erreur:
        raise _traduire_erreur(erreur)
    session.commit()
    return _charger_mouvement(session, mouvement.id)


# --- Correction d'inventaire (valeur absolue) --------------------------------
@routeur.post("/corriger", response_model=MouvementLecture, status_code=status.HTTP_201_CREATED)
def corriger(demande: DemandeCorrection, session: Session_, gerant: Gerant_):
    try:
        mouvement = service_stock.corriger(
            session, demande.variante_id, demande.nouvelle_quantite,
            utilisateur_id=gerant.id, motif=demande.motif,
        )
    except service_stock.ErreurStock as erreur:
        raise _traduire_erreur(erreur)
    session.commit()
    return _charger_mouvement(session, mouvement.id)


# --- Historique des mouvements ----------------------------------------------
@routeur.get("/mouvements", response_model=MouvementPage, dependencies=[Depends(exiger_gerant)])
def lister_mouvements(
    session: Session_,
    variante_id: int | None = None,
    produit_id: int | None = None,
    type_mouvement: TypeMouvementStock | None = None,
    page: int = Query(default=1, ge=1),
    taille_page: int = Query(default=20, ge=1, le=100),
):
    requete = _requete_mouvements_jointe()
    if variante_id is not None:
        requete = requete.where(MouvementStock.variante_id == variante_id)
    if produit_id is not None:
        requete = requete.where(Produit.id == produit_id)
    if type_mouvement is not None:
        requete = requete.where(MouvementStock.type_mouvement == type_mouvement)

    total = session.scalar(select(func.count()).select_from(requete.subquery())) or 0
    limite, decalage = calculer_bornes(page, taille_page)
    lignes = session.execute(
        requete.order_by(MouvementStock.date_mouvement.desc(), MouvementStock.id.desc())
        .limit(limite)
        .offset(decalage)
    ).all()

    return MouvementPage(
        total=total, page=page, taille_page=taille_page,
        elements=[_ligne_en_lecture(*ligne) for ligne in lignes],
    )


# --- Alertes (rupture / stock faible) ---------------------------------------
@routeur.get("/alertes", response_model=list[AlerteStock], dependencies=[Depends(exiger_gerant)])
def alertes_stock(session: Session_, inclure_inactifs: bool = False):
    requete = select(VarianteProduit, Produit).join(Produit, VarianteProduit.produit_id == Produit.id)
    if not inclure_inactifs:
        requete = requete.where(VarianteProduit.actif.is_(True), Produit.actif.is_(True))
    requete = requete.where(
        or_(
            VarianteProduit.quantite_disponible <= 0,
            and_(
                VarianteProduit.stock_minimum > 0,
                VarianteProduit.quantite_disponible <= VarianteProduit.stock_minimum,
            ),
        )
    ).order_by(VarianteProduit.quantite_disponible.asc())

    resultat: list[AlerteStock] = []
    for variante, produit in session.execute(requete).all():
        resultat.append(AlerteStock(
            variante_id=variante.id,
            produit_id=produit.id,
            produit_nom=produit.nom,
            reference_variante=variante.reference_variante,
            couleur=variante.couleur,
            taille=variante.taille,
            quantite_disponible=variante.quantite_disponible,
            stock_minimum=variante.stock_minimum,
            en_rupture=variante.quantite_disponible <= 0,
            stock_faible=0 < variante.quantite_disponible <= variante.stock_minimum,
        ))
    return resultat