"""
Endpoints de gestion des photos produits (stockage Cloudinary).
Chemin : backend/app/routeurs/photos.py

Lecture : publique. Upload / modification / suppression : reservees au gerant.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.modeles import PhotoProduit, Produit
from app.schemas.photo_produit import PhotoLecture, PhotoMiseAJour, ReordonnerPhotos
from app.securite.dependances import exiger_gerant
from app.services import service_cloudinary

routeur = APIRouter(tags=["Photos"])

Session_ = Annotated[Session, Depends(obtenir_session)]

TYPES_IMAGE_AUTORISES = {"image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"}
TAILLE_MAX_OCTETS = 10 * 1024 * 1024          # 10 Mo par image
MAX_PHOTOS_PAR_PRODUIT = 10


def _obtenir_produit(session: Session, produit_id: int) -> Produit:
    produit = session.get(Produit, produit_id)
    if produit is None:
        raise HTTPException(status_code=404, detail="Produit introuvable")
    return produit


def _obtenir_photo(session: Session, photo_id: int) -> PhotoProduit:
    photo = session.get(PhotoProduit, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo introuvable")
    return photo


def _photos_du_produit(session: Session, produit_id: int) -> list[PhotoProduit]:
    return session.scalars(
        select(PhotoProduit).where(PhotoProduit.produit_id == produit_id).order_by(PhotoProduit.ordre)
    ).all()


def _valider_fichier(fichier: UploadFile, contenu: bytes) -> None:
    if fichier.content_type not in TYPES_IMAGE_AUTORISES:
        raise HTTPException(
            status_code=422,
            detail=f"Format non supporte ({fichier.content_type}). Formats acceptes : JPEG, PNG, WEBP, GIF.",
        )
    if len(contenu) > TAILLE_MAX_OCTETS:
        raise HTTPException(status_code=413, detail="Image trop volumineuse (10 Mo maximum)")
    if len(contenu) == 0:
        raise HTTPException(status_code=422, detail="Fichier vide")


# --- Lecture (publique) ------------------------------------------------------
@routeur.get("/produits/{produit_id}/photos", response_model=list[PhotoLecture])
def lister_photos(produit_id: int, session: Session_):
    _obtenir_produit(session, produit_id)
    return _photos_du_produit(session, produit_id)


# --- Upload (gerant) ---------------------------------------------------------
@routeur.post(
    "/produits/{produit_id}/photos", response_model=list[PhotoLecture],
    status_code=status.HTTP_201_CREATED, dependencies=[Depends(exiger_gerant)],
)
def televerser_photos(
    produit_id: int,
    session: Session_,
    fichiers: list[UploadFile] = File(...),
):
    produit = _obtenir_produit(session, produit_id)
    if not fichiers:
        raise HTTPException(status_code=422, detail="Aucun fichier fourni")
    if not service_cloudinary.est_configure():
        raise HTTPException(
            status_code=503,
            detail="Stockage des images non configure (cles Cloudinary manquantes dans .env)",
        )

    existantes = _photos_du_produit(session, produit_id)
    if len(existantes) + len(fichiers) > MAX_PHOTOS_PAR_PRODUIT:
        raise HTTPException(
            status_code=422,
            detail=f"Un produit ne peut pas depasser {MAX_PHOTOS_PAR_PRODUIT} photos",
        )

    y_a_principale = any(p.est_principale for p in existantes)
    ordre_courant = max((p.ordre for p in existantes), default=-1)

    creees: list[PhotoProduit] = []
    for fichier in fichiers:
        contenu = fichier.file.read()
        _valider_fichier(fichier, contenu)
        resultat = service_cloudinary.televerser_image(contenu, dossier=f"boutique/produits/{produit.id}")
        ordre_courant += 1
        photo = PhotoProduit(
            produit_id=produit_id,
            url=resultat["url"],
            public_id=resultat["public_id"],
            ordre=ordre_courant,
            est_principale=False,
        )
        session.add(photo)
        creees.append(photo)

    # La toute premiere photo d'un produit devient la photo principale.
    if not y_a_principale and creees:
        creees[0].est_principale = True

    session.commit()
    for photo in creees:
        session.refresh(photo)
    return creees


# --- Modification / reordonnancement / suppression (gerant) ------------------
@routeur.patch("/photos/{photo_id}", response_model=PhotoLecture, dependencies=[Depends(exiger_gerant)])
def modifier_photo(photo_id: int, donnees: PhotoMiseAJour, session: Session_):
    photo = _obtenir_photo(session, photo_id)
    champs = donnees.model_dump(exclude_unset=True)

    if champs.get("est_principale") is True:
        autres = session.scalars(
            select(PhotoProduit).where(
                PhotoProduit.produit_id == photo.produit_id,
                PhotoProduit.id != photo_id,
            )
        ).all()
        for autre in autres:
            autre.est_principale = False
        photo.est_principale = True
    elif champs.get("est_principale") is False:
        photo.est_principale = False

    if "ordre" in champs:
        photo.ordre = champs["ordre"]

    session.commit()
    session.refresh(photo)
    return photo


@routeur.post(
    "/produits/{produit_id}/photos/reordonner", response_model=list[PhotoLecture],
    dependencies=[Depends(exiger_gerant)],
)
def reordonner_photos(produit_id: int, donnees: ReordonnerPhotos, session: Session_):
    _obtenir_produit(session, produit_id)
    photos = {p.id: p for p in _photos_du_produit(session, produit_id)}
    if set(donnees.ordre) != set(photos.keys()):
        raise HTTPException(
            status_code=422,
            detail="La liste doit contenir exactement les identifiants des photos de ce produit",
        )
    for position, photo_id in enumerate(donnees.ordre):
        photos[photo_id].ordre = position
    session.commit()
    return _photos_du_produit(session, produit_id)


@routeur.delete("/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(exiger_gerant)])
def supprimer_photo(photo_id: int, session: Session_):
    photo = _obtenir_photo(session, photo_id)
    produit_id = photo.produit_id
    etait_principale = photo.est_principale

    # Suppression sur Cloudinary (au mieux : on n'empeche pas la suppression en base si Cloudinary echoue).
    if photo.public_id and service_cloudinary.est_configure():
        try:
            service_cloudinary.supprimer_image(photo.public_id)
        except Exception:
            pass

    session.delete(photo)
    session.flush()

    # Si on a supprime la photo principale, on promeut la premiere restante.
    if etait_principale:
        remplacante = session.scalar(
            select(PhotoProduit).where(PhotoProduit.produit_id == produit_id).order_by(PhotoProduit.ordre)
        )
        if remplacante is not None:
            remplacante.est_principale = True

    session.commit()