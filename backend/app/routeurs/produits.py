"""
Endpoints de gestion des produits et de leurs variantes.
Chemin : backend/app/routeurs/produits.py

Lecture (liste boutique, detail) : publique (produits actifs uniquement).
Liste de gestion + creation / modification / suppression : reservees au gerant.
"""
import uuid
from collections import defaultdict
from decimal import Decimal
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, case, exists, func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.base_donnees import obtenir_session
from app.modeles import Categorie, MouvementStock, Produit, VarianteProduit
from app.schemas.produit import (
    ProduitCreation,
    ProduitLecture,
    ProduitMiseAJour,
    ProduitPage,
    ProduitResume,
)
from app.schemas.variante_produit import (
    VarianteCreation,
    VarianteLecture,
    VarianteMiseAJour,
)
from app.securite.dependances import exiger_gerant
from app.utils.pagination import calculer_bornes
from app.utils.references import reference_produit, reference_variante

routeur = APIRouter(prefix="/produits", tags=["Produits"])

Session_ = Annotated[Session, Depends(obtenir_session)]

TypeTri = Literal["recent", "prix_asc", "prix_desc", "nom"]


# --- Fonctions internes ------------------------------------------------------
def _charger_produit_complet(session: Session, produit_id: int) -> Produit:
    produit = session.scalar(
        select(Produit)
        .where(Produit.id == produit_id)
        .options(
            joinedload(Produit.categorie),
            selectinload(Produit.variantes),
            selectinload(Produit.photos),
        )
    )
    if produit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produit introuvable")
    return produit


def _valider_categorie(session: Session, categorie_id: int) -> None:
    if session.get(Categorie, categorie_id) is None:
        raise HTTPException(status_code=422, detail="Categorie introuvable")


def _valider_prix_promo(prix: Decimal | None, prix_promo: Decimal | None, en_promotion: bool) -> None:
    if en_promotion and prix_promo is None:
        raise HTTPException(status_code=422, detail="Un produit en promotion doit avoir un prix promotionnel")
    if prix_promo is not None and prix is not None and prix_promo >= prix:
        raise HTTPException(status_code=422, detail="Le prix promotionnel doit etre inferieur au prix normal")


def _normaliser_variantes(variantes: list[VarianteCreation], a_tailles: bool) -> list[dict]:
    """Valide les tailles selon a_tailles, refuse les doublons, normalise couleur/taille."""
    vues: set[tuple[str, str]] = set()
    resultat: list[dict] = []
    for v in variantes:
        couleur = (v.couleur or "").strip() or None
        taille = (v.taille or "").strip() or None
        if a_tailles and not taille:
            raise HTTPException(
                status_code=422,
                detail="Chaque variante doit avoir une taille pour un produit a tailles (chaussures)",
            )
        if not a_tailles:
            taille = None  # les tailles sont ignorees pour les produits sans pointure (sacs)
        cle = (couleur or "", taille or "")
        if cle in vues:
            raise HTTPException(
                status_code=422,
                detail=f"Variante en double (couleur={couleur}, taille={taille})",
            )
        vues.add(cle)
        resultat.append({
            "couleur": couleur,
            "taille": taille,
            "quantite_disponible": v.quantite_disponible,
            "stock_minimum": v.stock_minimum,
        })
    return resultat


def _egal_null(colonne, valeur):
    """Egalite compatible avec les valeurs NULL (couleur/taille peuvent etre None)."""
    return colonne.is_(None) if valeur is None else colonne == valeur


def _ids_categorie_et_descendants(session: Session, categorie_id: int) -> list[int]:
    lignes = session.execute(select(Categorie.id, Categorie.parent_id)).all()
    enfants: dict[int | None, list[int]] = defaultdict(list)
    for cid, pid in lignes:
        enfants[pid].append(cid)
    resultat: list[int] = []
    pile = [categorie_id]
    while pile:
        courant = pile.pop()
        resultat.append(courant)
        pile.extend(enfants.get(courant, []))
    return resultat


def _quantite_totale(produit: Produit) -> int:
    return sum(v.quantite_disponible for v in produit.variantes if v.actif)


def _photo_principale(produit: Produit) -> str | None:
    if not produit.photos:
        return None
    principale = next((ph for ph in produit.photos if ph.est_principale), None)
    return (principale or produit.photos[0]).url


def _resume(produit: Produit) -> ProduitResume:
    return ProduitResume(
        id=produit.id,
        reference=produit.reference,
        nom=produit.nom,
        categorie_id=produit.categorie_id,
        prix=produit.prix,
        prix_promo=produit.prix_promo,
        en_promotion=produit.en_promotion,
        statut=produit.statut,
        actif=produit.actif,
        photo_principale=_photo_principale(produit),
        quantite_totale=_quantite_totale(produit),
    )


def _construire_requete_liste(
    session: Session,
    recherche: str | None,
    categorie_id: int | None,
    prix_min: int | None,
    prix_max: int | None,
    couleur: str | None,
    taille: str | None,
    en_stock: bool | None,
    en_promotion: bool | None,
    inclure_inactifs: bool,
):
    requete = select(Produit)
    if not inclure_inactifs:
        requete = requete.where(Produit.actif.is_(True))

    if recherche and recherche.strip():
        motif = f"%{recherche.strip()}%"
        requete = requete.where(or_(Produit.nom.ilike(motif), Produit.reference.ilike(motif)))

    if categorie_id is not None:
        ids = _ids_categorie_et_descendants(session, categorie_id)
        requete = requete.where(Produit.categorie_id.in_(ids))

    prix_effectif = case(
        (and_(Produit.en_promotion.is_(True), Produit.prix_promo.isnot(None)), Produit.prix_promo),
        else_=Produit.prix,
    )
    if prix_min is not None:
        requete = requete.where(prix_effectif >= prix_min)
    if prix_max is not None:
        requete = requete.where(prix_effectif <= prix_max)

    if en_promotion is not None:
        requete = requete.where(Produit.en_promotion.is_(en_promotion))

    if couleur and couleur.strip():
        requete = requete.where(exists(
            select(VarianteProduit.id).where(
                VarianteProduit.produit_id == Produit.id,
                VarianteProduit.actif.is_(True),
                func.lower(VarianteProduit.couleur) == couleur.strip().lower(),
            )
        ))
    if taille and taille.strip():
        requete = requete.where(exists(
            select(VarianteProduit.id).where(
                VarianteProduit.produit_id == Produit.id,
                VarianteProduit.actif.is_(True),
                func.lower(VarianteProduit.taille) == taille.strip().lower(),
            )
        ))
    if en_stock is not None:
        condition_stock = exists(
            select(VarianteProduit.id).where(
                VarianteProduit.produit_id == Produit.id,
                VarianteProduit.actif.is_(True),
                VarianteProduit.quantite_disponible > 0,
            )
        )
        requete = requete.where(condition_stock if en_stock else ~condition_stock)

    return requete, prix_effectif


def _paginer_produits(session, requete, prix_effectif, tri: str, page: int, taille_page: int) -> ProduitPage:
    total = session.scalar(select(func.count()).select_from(requete.subquery())) or 0

    ordres = {
        "recent": (Produit.date_creation.desc(), Produit.id.desc()),
        "prix_asc": (prix_effectif.asc(), Produit.id.asc()),
        "prix_desc": (prix_effectif.desc(), Produit.id.desc()),
        "nom": (Produit.nom.asc(), Produit.id.asc()),
    }[tri]

    limite, decalage = calculer_bornes(page, taille_page)
    produits = session.scalars(
        requete.order_by(*ordres)
        .options(selectinload(Produit.variantes), selectinload(Produit.photos))
        .limit(limite)
        .offset(decalage)
    ).all()

    return ProduitPage(
        total=total,
        page=page,
        taille_page=taille_page,
        elements=[_resume(p) for p in produits],
    )


# --- Lecture : liste boutique (publique) ------------------------------------
@routeur.get("", response_model=ProduitPage)
def lister(
    session: Session_,
    recherche: str | None = None,
    categorie_id: int | None = None,
    prix_min: int | None = Query(default=None, ge=0),
    prix_max: int | None = Query(default=None, ge=0),
    couleur: str | None = None,
    taille: str | None = None,
    en_stock: bool | None = None,
    en_promotion: bool | None = None,
    tri: TypeTri = "recent",
    page: int = Query(default=1, ge=1),
    taille_page: int = Query(default=20, ge=1, le=100),
):
    requete, prix_effectif = _construire_requete_liste(
        session, recherche, categorie_id, prix_min, prix_max,
        couleur, taille, en_stock, en_promotion, inclure_inactifs=False,
    )
    return _paginer_produits(session, requete, prix_effectif, tri, page, taille_page)


# --- Liste de gestion (gerant) -- declaree AVANT /{produit_id} ---------------
@routeur.get("/gestion", response_model=ProduitPage, dependencies=[Depends(exiger_gerant)])
def lister_gestion(
    session: Session_,
    recherche: str | None = None,
    categorie_id: int | None = None,
    prix_min: int | None = Query(default=None, ge=0),
    prix_max: int | None = Query(default=None, ge=0),
    couleur: str | None = None,
    taille: str | None = None,
    en_stock: bool | None = None,
    en_promotion: bool | None = None,
    tri: TypeTri = "recent",
    page: int = Query(default=1, ge=1),
    taille_page: int = Query(default=20, ge=1, le=100),
):
    """Comme la liste boutique, mais inclut aussi les produits desactives."""
    requete, prix_effectif = _construire_requete_liste(
        session, recherche, categorie_id, prix_min, prix_max,
        couleur, taille, en_stock, en_promotion, inclure_inactifs=True,
    )
    return _paginer_produits(session, requete, prix_effectif, tri, page, taille_page)


# --- Creation produit (gerant) ----------------------------------------------
@routeur.post(
    "", response_model=ProduitLecture, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exiger_gerant)],
)
def creer(donnees: ProduitCreation, session: Session_):
    _valider_categorie(session, donnees.categorie_id)
    _valider_prix_promo(donnees.prix, donnees.prix_promo, donnees.en_promotion)
    variantes = _normaliser_variantes(donnees.variantes, donnees.a_tailles)

    reference = donnees.reference.strip() if donnees.reference else None
    if reference and session.scalar(select(Produit).where(Produit.reference == reference)):
        raise HTTPException(status_code=409, detail=f"La reference « {reference} » existe deja")

    produit = Produit(
        nom=donnees.nom,
        description=donnees.description,
        categorie_id=donnees.categorie_id,
        prix=donnees.prix,
        prix_promo=donnees.prix_promo,
        en_promotion=donnees.en_promotion,
        a_tailles=donnees.a_tailles,
        statut=donnees.statut,
        actif=True,
        reference=reference or uuid.uuid4().hex,  # provisoire si generee automatiquement
    )
    session.add(produit)
    session.flush()  # obtient l'id du produit
    if not reference:
        produit.reference = reference_produit(produit.id)

    for v in variantes:
        variante = VarianteProduit(
            produit_id=produit.id,
            couleur=v["couleur"],
            taille=v["taille"],
            quantite_disponible=v["quantite_disponible"],
            stock_minimum=v["stock_minimum"],
            actif=True,
        )
        session.add(variante)
        session.flush()  # obtient l'id de la variante
        variante.reference_variante = reference_variante(produit.reference, variante.id)

    session.commit()
    return _charger_produit_complet(session, produit.id)


# --- Gestion des variantes (gerant) -----------------------------------------
@routeur.post(
    "/{produit_id}/variantes", response_model=VarianteLecture,
    status_code=status.HTTP_201_CREATED, dependencies=[Depends(exiger_gerant)],
)
def ajouter_variante(produit_id: int, donnees: VarianteCreation, session: Session_):
    produit = session.get(Produit, produit_id)
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    v = _normaliser_variantes([donnees], produit.a_tailles)[0]
    doublon = session.scalar(
        select(VarianteProduit).where(
            VarianteProduit.produit_id == produit_id,
            _egal_null(VarianteProduit.couleur, v["couleur"]),
            _egal_null(VarianteProduit.taille, v["taille"]),
        )
    )
    if doublon is not None:
        raise HTTPException(status_code=409, detail="Cette combinaison couleur/taille existe deja pour ce produit")

    variante = VarianteProduit(
        produit_id=produit_id,
        couleur=v["couleur"],
        taille=v["taille"],
        quantite_disponible=v["quantite_disponible"],
        stock_minimum=v["stock_minimum"],
        actif=True,
    )
    session.add(variante)
    session.flush()
    variante.reference_variante = reference_variante(produit.reference, variante.id)
    session.commit()
    session.refresh(variante)
    return variante


@routeur.patch(
    "/variantes/{variante_id}", response_model=VarianteLecture,
    dependencies=[Depends(exiger_gerant)],
)
def modifier_variante(variante_id: int, donnees: VarianteMiseAJour, session: Session_):
    variante = session.get(VarianteProduit, variante_id)
    if variante is None:
        raise HTTPException(status_code=404, detail="Variante introuvable")
    produit = session.get(Produit, variante.produit_id)
    champs = donnees.model_dump(exclude_unset=True)

    nouvelle_couleur = variante.couleur
    if "couleur" in champs:
        nouvelle_couleur = (champs["couleur"] or "").strip() or None
    nouvelle_taille = variante.taille
    if "taille" in champs:
        nouvelle_taille = (champs["taille"] or "").strip() or None

    if produit.a_tailles and nouvelle_taille is None:
        raise HTTPException(status_code=422, detail="Une taille est requise pour ce produit (chaussures)")
    if not produit.a_tailles:
        nouvelle_taille = None

    if (nouvelle_couleur, nouvelle_taille) != (variante.couleur, variante.taille):
        doublon = session.scalar(
            select(VarianteProduit).where(
                VarianteProduit.produit_id == variante.produit_id,
                VarianteProduit.id != variante_id,
                _egal_null(VarianteProduit.couleur, nouvelle_couleur),
                _egal_null(VarianteProduit.taille, nouvelle_taille),
            )
        )
        if doublon is not None:
            raise HTTPException(status_code=409, detail="Cette combinaison couleur/taille existe deja pour ce produit")

    variante.couleur = nouvelle_couleur
    variante.taille = nouvelle_taille
    if "stock_minimum" in champs:
        variante.stock_minimum = champs["stock_minimum"]
    if "actif" in champs:
        variante.actif = champs["actif"]

    session.commit()
    session.refresh(variante)
    return variante


@routeur.delete(
    "/variantes/{variante_id}", status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(exiger_gerant)],
)
def supprimer_variante(variante_id: int, session: Session_):
    variante = session.get(VarianteProduit, variante_id)
    if variante is None:
        raise HTTPException(status_code=404, detail="Variante introuvable")

    nb_variantes = session.scalar(
        select(func.count()).select_from(VarianteProduit)
        .where(VarianteProduit.produit_id == variante.produit_id)
    )
    if nb_variantes <= 1:
        raise HTTPException(
            status_code=409,
            detail="Un produit doit garder au moins une variante. Desactivez-la (actif=false) plutot.",
        )

    nb_mouvements = session.scalar(
        select(func.count()).select_from(MouvementStock)
        .where(MouvementStock.variante_id == variante_id)
    )
    if nb_mouvements:
        raise HTTPException(
            status_code=409,
            detail="Cette variante a un historique de stock. Desactivez-la (actif=false) plutot.",
        )

    session.delete(variante)
    session.commit()


# --- Detail / modification / suppression produit -----------------------------
@routeur.get("/{produit_id}", response_model=ProduitLecture)
def obtenir(produit_id: int, session: Session_):
    return _charger_produit_complet(session, produit_id)


@routeur.patch("/{produit_id}", response_model=ProduitLecture, dependencies=[Depends(exiger_gerant)])
def mettre_a_jour(produit_id: int, donnees: ProduitMiseAJour, session: Session_):
    produit = session.get(Produit, produit_id)
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    champs = donnees.model_dump(exclude_unset=True)

    if "categorie_id" in champs:
        _valider_categorie(session, champs["categorie_id"])
        produit.categorie_id = champs["categorie_id"]

    prix = champs.get("prix", produit.prix)
    prix_promo = champs["prix_promo"] if "prix_promo" in champs else produit.prix_promo
    en_promotion = champs.get("en_promotion", produit.en_promotion)
    if any(cle in champs for cle in ("prix", "prix_promo", "en_promotion")):
        _valider_prix_promo(prix, prix_promo, en_promotion)

    for cle in ("nom", "description", "prix", "prix_promo", "en_promotion", "a_tailles", "statut", "actif"):
        if cle in champs:
            setattr(produit, cle, champs[cle])

    session.commit()
    return _charger_produit_complet(session, produit_id)


@routeur.delete("/{produit_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(exiger_gerant)])
def supprimer(produit_id: int, session: Session_):
    produit = session.get(Produit, produit_id)
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    ids_variantes = session.scalars(
        select(VarianteProduit.id).where(VarianteProduit.produit_id == produit_id)
    ).all()
    if ids_variantes:
        nb_mouvements = session.scalar(
            select(func.count()).select_from(MouvementStock)
            .where(MouvementStock.variante_id.in_(ids_variantes))
        )
        if nb_mouvements:
            raise HTTPException(
                status_code=409,
                detail="Suppression impossible : ce produit a un historique de stock. Desactivez-le (actif=false).",
            )

    session.delete(produit)  # cascade : supprime aussi variantes et photos
    session.commit()