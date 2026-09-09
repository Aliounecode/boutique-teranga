"""
Schemas Pydantic du tableau de bord.
Chemin : backend/app/schemas/dashboard.py
"""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.modeles.enumerations import MoyenPaiement


class MontantParMoyen(BaseModel):
    moyen: MoyenPaiement
    montant: Decimal
    nombre: int


class ResumeTableauBord(BaseModel):
    date_debut: date
    date_fin: date
    chiffre_affaires: Decimal
    total_ventes_physiques: Decimal
    nombre_ventes_physiques: int
    total_ventes_en_ligne: Decimal
    nombre_commandes_validees: int
    nombre_articles_vendus: int
    remboursements: Decimal
    commandes_en_attente: int   # commandes nouvelles a traiter (temps reel, hors periode)
    commandes_annulees: int
    paiements_par_moyen: list[MontantParMoyen]


class PointPeriode(BaseModel):
    periode: str
    montant: Decimal
    nombre: int


class VentesPeriodiques(BaseModel):
    granularite: str
    points: list[PointPeriode]


class TopProduit(BaseModel):
    produit_id: int
    produit_nom: str
    quantite_vendue: int
    montant: Decimal


class TopCategorie(BaseModel):
    categorie_id: int
    categorie_nom: str
    quantite_vendue: int
    montant: Decimal