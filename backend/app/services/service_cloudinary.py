"""
Envoi et suppression des photos produits sur Cloudinary.
Chemin : backend/app/services/service_cloudinary.py
"""
import io

import cloudinary
import cloudinary.uploader

from app.config import parametres

_configure = False


def est_configure() -> bool:
    """Vrai si les trois cles Cloudinary sont presentes dans la configuration."""
    return all([
        parametres.cloudinary_cloud_name,
        parametres.cloudinary_api_key,
        parametres.cloudinary_api_secret,
    ])


def _assurer_configuration() -> None:
    global _configure
    if not _configure:
        cloudinary.config(
            cloud_name=parametres.cloudinary_cloud_name,
            api_key=parametres.cloudinary_api_key,
            api_secret=parametres.cloudinary_api_secret,
            secure=True,
        )
        _configure = True


def televerser_image(contenu: bytes, dossier: str = "boutique/produits") -> dict:
    """Envoie une image (octets) sur Cloudinary. Retourne {url, public_id}."""
    _assurer_configuration()
    resultat = cloudinary.uploader.upload(
        io.BytesIO(contenu),
        folder=dossier,
        resource_type="image",
    )
    return {"url": resultat["secure_url"], "public_id": resultat["public_id"]}


def supprimer_image(public_id: str) -> None:
    """Supprime une image de Cloudinary a partir de son public_id."""
    _assurer_configuration()
    cloudinary.uploader.destroy(public_id, resource_type="image")