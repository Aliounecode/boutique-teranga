"""
Schemas Pydantic des commandes en ligne.
Chemin : backend/app/schemas/commande.py
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.modeles.enumerations import MoyenPaiement, StatutCommande


class LigneCommandeEntree(BaseModel):
    variante_id: int
    quantite: int = Field(gt=0)


class CommandeCreation(BaseModel):
    client_nom: str = Field(min_length=1, max_length=100)
    client_prenom: str | None = Field(default=None, max_length=100)
    client_telephone: str = Field(min_length=1, max_length=30)
    moyen_paiement: MoyenPaiement
    notes: str | None = Field(default=None, max_length=255)
    lignes: list[LigneCommandeEntree] = Field(min_length=1)


class LigneCommandeLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    variante_id: int
    produit_nom: str
    couleur: str | None
    taille: str | None
    prix_unitaire: Decimal
    quantite: int
    sous_total: Decimal


class CommandeLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    client_nom: str
    client_prenom: str | None
    client_telephone: str
    moyen_paiement: MoyenPaiement
    montant_total: Decimal
    statut: StatutCommande
    notes: str | None
    utilisateur_id: int | None
    date_commande: datetime
    lignes: list[LigneCommandeLecture]


class CommandeResume(BaseModel):
    id: int
    numero: str
    date_commande: datetime
    client_nom: str
    client_telephone: str
    moyen_paiement: MoyenPaiement
    montant_total: Decimal
    statut: StatutCommande
    nombre_articles: int


class CommandePage(BaseModel):
    total: int
    page: int
    taille_page: int
    elements: list[CommandeResume]