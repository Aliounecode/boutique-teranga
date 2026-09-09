"""
Utilitaires de formatage (montants, libelles).
Chemin : backend/app/utils/formatage.py
"""
from app.modeles.enumerations import MoyenPaiement


def formater_fcfa(montant) -> str:
    """Formate un montant en FCFA avec separateur de milliers, ex. 70 000 FCFA."""
    return f"{int(montant):,}".replace(",", " ") + " FCFA"


LIBELLES_MOYEN = {
    MoyenPaiement.ESPECES: "Espèces",
    MoyenPaiement.WAVE: "Wave",
    MoyenPaiement.ORANGE_MONEY: "Orange Money",
    MoyenPaiement.FREE_MONEY: "Free Money",
    MoyenPaiement.CARTE: "Carte bancaire",
    MoyenPaiement.AUTRE: "Autre",
}