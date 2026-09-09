"""
Schemas Pydantic des photos produit.
Chemin : backend/app/schemas/photo_produit.py
"""
from pydantic import BaseModel, ConfigDict, Field


class PhotoLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    ordre: int
    est_principale: bool


class PhotoMiseAJour(BaseModel):
    """Mise a jour d'une photo : position et/ou statut de photo principale."""
    ordre: int | None = Field(default=None, ge=0)
    est_principale: bool | None = None


class ReordonnerPhotos(BaseModel):
    """Nouvel ordre des photos d'un produit (liste complete de leurs identifiants)."""
    ordre: list[int] = Field(min_length=1)