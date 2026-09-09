"""
Schemas Pydantic des categories.
Chemin : backend/app/schemas/categorie.py
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CategorieBase(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    parent_id: int | None = None


class CategorieCreation(CategorieBase):
    """Donnees pour creer une categorie (le slug est genere cote serveur)."""
    pass


class CategorieMiseAJour(BaseModel):
    """Mise a jour partielle : seuls les champs fournis sont modifies."""
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    parent_id: int | None = None
    actif: bool | None = None


class CategorieLecture(CategorieBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    actif: bool
    date_creation: datetime


class CategorieArbre(BaseModel):
    """Categorie avec ses sous-categories imbriquees (navigation boutique)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    slug: str
    description: str | None = None
    actif: bool
    sous_categories: list[CategorieArbre] = []


# Resolution de la reference recursive (list[CategorieArbre]).
CategorieArbre.model_rebuild()