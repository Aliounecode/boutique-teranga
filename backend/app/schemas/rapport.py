"""
Schemas Pydantic du rapport journalier.
Chemin : backend/app/schemas/rapport.py
"""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.modeles.enumerations import MoyenPaiement


class VentesRapport(BaseModel):
    nombre_total: int
    physiques_nombre: int
    physiques_montant: Decimal
    en_ligne_nombre: int
    en_ligne_montant: Decimal
    chiffre_affaires: Decimal


class PaiementRapport(BaseModel):
    moyen: MoyenPaiement
    montant: Decimal


class CommandesRapport(BaseModel):
    recues: int
    validees: int
    refusees: int
    annulees: int


class StockRapport(BaseModel):
    articles_vendus: int
    reapprovisionnes: int
    en_rupture: int
    proches_rupture: int


class RapportJournalier(BaseModel):
    date: date
    ventes: VentesRapport
    paiements: list[PaiementRapport]
    commandes: CommandesRapport
    stock: StockRapport