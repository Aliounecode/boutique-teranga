"""
Endpoints de gestion des categories.
Chemin : backend/app/routeurs/categories.py

Lecture (arbre, detail) : publique.
Creation / modification / suppression : reservees au gerant.
"""
from collections import defaultdict
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.modeles import Categorie, Produit
from app.schemas.categorie import (
    CategorieArbre,
    CategorieCreation,
    CategorieLecture,
    CategorieMiseAJour,
)
from app.securite.dependances import exiger_gerant
from app.utils.texte import creer_slug

routeur = APIRouter(prefix="/categories", tags=["Categories"])

Session_ = Annotated[Session, Depends(obtenir_session)]


# --- Fonctions internes ------------------------------------------------------
def _obtenir_categorie(session: Session, categorie_id: int) -> Categorie:
    categorie = session.get(Categorie, categorie_id)
    if categorie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categorie introuvable")
    return categorie


def _verifier_slug_unique(session: Session, slug: str, exclure_id: int | None = None) -> None:
    requete = select(Categorie).where(Categorie.slug == slug)
    if exclure_id is not None:
        requete = requete.where(Categorie.id != exclure_id)
    if session.scalar(requete) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Une categorie equivalente existe deja (slug « {slug} »)",
        )


def _verifier_parent(session: Session, parent_id: int | None, categorie_id: int | None = None) -> None:
    """Valide le parent : il existe, n'est pas la categorie elle-meme, ne cree pas de cycle."""
    if parent_id is None:
        return
    if parent_id == categorie_id:
        raise HTTPException(status_code=400, detail="Une categorie ne peut pas etre son propre parent")
    parent = session.get(Categorie, parent_id)
    if parent is None:
        raise HTTPException(status_code=404, detail="Categorie parente introuvable")
    if categorie_id is not None:
        courant = parent
        while courant is not None:
            if courant.id == categorie_id:
                raise HTTPException(
                    status_code=400,
                    detail="Deplacement invalide : la categorie deviendrait sa propre descendante",
                )
            courant = courant.parent


# --- Lecture (publique) ------------------------------------------------------
@routeur.get("", response_model=list[CategorieArbre])
def lister_arbre(session: Session_):
    """Arbre des categories actives (racines + sous-categories)."""
    categories = session.scalars(
        select(Categorie).where(Categorie.actif.is_(True)).order_by(Categorie.nom)
    ).all()

    par_parent: dict[int | None, list[Categorie]] = defaultdict(list)
    for categorie in categories:
        par_parent[categorie.parent_id].append(categorie)

    def construire_noeud(categorie: Categorie) -> CategorieArbre:
        return CategorieArbre(
            id=categorie.id,
            nom=categorie.nom,
            slug=categorie.slug,
            description=categorie.description,
            actif=categorie.actif,
            sous_categories=[construire_noeud(enfant) for enfant in par_parent[categorie.id]],
        )

    return [construire_noeud(racine) for racine in par_parent[None]]


# --- Liste complete (gerant) -- declaree AVANT /{categorie_id} ---------------
@routeur.get("/toutes", response_model=list[CategorieLecture], dependencies=[Depends(exiger_gerant)])
def lister_toutes(session: Session_):
    """Liste plate de toutes les categories (actives et inactives)."""
    return session.scalars(select(Categorie).order_by(Categorie.nom)).all()


@routeur.get("/{categorie_id}", response_model=CategorieLecture)
def obtenir(categorie_id: int, session: Session_):
    return _obtenir_categorie(session, categorie_id)


# --- Ecriture (gerant) -------------------------------------------------------
@routeur.post(
    "", response_model=CategorieLecture, status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(exiger_gerant)],
)
def creer(donnees: CategorieCreation, session: Session_):
    _verifier_parent(session, donnees.parent_id)
    slug = creer_slug(donnees.nom)
    if not slug:
        raise HTTPException(status_code=422, detail="Nom de categorie invalide")
    _verifier_slug_unique(session, slug)

    categorie = Categorie(
        nom=donnees.nom,
        slug=slug,
        description=donnees.description,
        parent_id=donnees.parent_id,
        actif=True,
    )
    session.add(categorie)
    session.commit()
    session.refresh(categorie)
    return categorie


@routeur.patch(
    "/{categorie_id}", response_model=CategorieLecture,
    dependencies=[Depends(exiger_gerant)],
)
def mettre_a_jour(categorie_id: int, donnees: CategorieMiseAJour, session: Session_):
    categorie = _obtenir_categorie(session, categorie_id)
    champs = donnees.model_dump(exclude_unset=True)

    if "parent_id" in champs:
        _verifier_parent(session, champs["parent_id"], categorie_id)
        categorie.parent_id = champs["parent_id"]
    if "nom" in champs:
        nouveau_slug = creer_slug(champs["nom"])
        if not nouveau_slug:
            raise HTTPException(status_code=422, detail="Nom de categorie invalide")
        _verifier_slug_unique(session, nouveau_slug, exclure_id=categorie_id)
        categorie.nom = champs["nom"]
        categorie.slug = nouveau_slug
    if "description" in champs:
        categorie.description = champs["description"]
    if "actif" in champs:
        categorie.actif = champs["actif"]

    session.commit()
    session.refresh(categorie)
    return categorie


@routeur.delete(
    "/{categorie_id}", status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(exiger_gerant)],
)
def supprimer(categorie_id: int, session: Session_):
    categorie = _obtenir_categorie(session, categorie_id)

    nb_sous = session.scalar(
        select(func.count()).select_from(Categorie).where(Categorie.parent_id == categorie_id)
    )
    if nb_sous:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Suppression impossible : cette categorie contient des sous-categories",
        )

    nb_produits = session.scalar(
        select(func.count()).select_from(Produit).where(Produit.categorie_id == categorie_id)
    )
    if nb_produits:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Suppression impossible : {nb_produits} produit(s) rattache(s). "
                   "Desactivez la categorie ou reassignez les produits.",
        )

    session.delete(categorie)
    session.commit()