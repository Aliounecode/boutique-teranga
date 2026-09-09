"""
Schemas Pydantic des ventes (caisse/POS).
Chemin : backend/app/schemas/vente.py
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modeles.enumerations import MoyenPaiement, StatutVente
from app.schemas.client import ClientLecture
from app.schemas.paiement import PaiementLecture


class LigneVenteEntree(BaseModel):
    variante_id: int
    quantite: int = Field(gt=0)


class VenteCreation(BaseModel):
    client_id: int | None = None
    notes: str | None = Field(default=None, max_length=255)
    moyen_paiement: MoyenPaiement
    reference_paiement: str | None = Field(default=None, max_length=100)
    lignes: list[LigneVenteEntree] = Field(min_length=1)


class LigneVenteLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    variante_id: int
    produit_nom: str
    couleur: str | None
    taille: str | None
    prix_unitaire: Decimal
    quantite: int
    sous_total: Decimal


class VenteLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    client_id: int | None
    client: ClientLecture | None
    utilisateur_id: int
    montant_total: Decimal
    statut: StatutVente
    notes: str | None
    date_vente: datetime
    lignes: list[LigneVenteLecture]
    paiements: list[PaiementLecture]


class VenteResume(BaseModel):
    id: int
    numero: str
    date_vente: datetime
    client_nom: str | None
    montant_total: Decimal
    statut: StatutVente
    nombre_articles: int


class VentePage(BaseModel):
    total: int
    page: int
    taille_page: int
    elements: list[VenteResume]