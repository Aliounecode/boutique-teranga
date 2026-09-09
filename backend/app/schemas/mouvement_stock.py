"""
Schemas Pydantic du stock (mouvements, reapprovisionnement, alertes).
Chemin : backend/app/schemas/mouvement_stock.py
"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.modeles.enumerations import TypeMouvementStock


class DemandeReapprovisionnement(BaseModel):
    variante_id: int
    quantite: int = Field(gt=0)
    motif: str | None = Field(default=None, max_length=255)


class DemandeCorrection(BaseModel):
    variante_id: int
    nouvelle_quantite: int = Field(ge=0)
    motif: str | None = Field(default=None, max_length=255)


class MouvementLecture(BaseModel):
    id: int
    date_mouvement: datetime
    type_mouvement: TypeMouvementStock
    quantite: int
    quantite_avant: int
    quantite_apres: int
    motif: str | None
    reference_document: str | None
    variante_id: int
    produit_id: int
    produit_nom: str
    reference_variante: str | None
    couleur: str | None
    taille: str | None
    utilisateur_id: int | None


class MouvementPage(BaseModel):
    total: int
    page: int
    taille_page: int
    elements: list[MouvementLecture]


class AlerteStock(BaseModel):
    variante_id: int
    produit_id: int
    produit_nom: str
    reference_variante: str | None
    couleur: str | None
    taille: str | None
    quantite_disponible: int
    stock_minimum: int
    en_rupture: bool
    stock_faible: bool