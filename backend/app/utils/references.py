"""
Generation des references (produits, variantes, ventes, commandes).
Chemin : backend/app/utils/references.py
"""

PREFIXE_PRODUIT = "PRD"
PREFIXE_VENTE = "V"
PREFIXE_COMMANDE = "CMD"


def reference_produit(produit_id: int) -> str:
    """Reference lisible d'un produit, ex. PRD-000123."""
    return f"{PREFIXE_PRODUIT}-{produit_id:06d}"


def reference_variante(reference_produit_: str, variante_id: int) -> str:
    """Reference d'une variante, ex. PRD-000123-V045."""
    return f"{reference_produit_}-V{variante_id:03d}"


def numero_vente(vente_id: int) -> str:
    """Numero lisible d'une vente, ex. V-000123."""
    return f"{PREFIXE_VENTE}-{vente_id:06d}"


def numero_commande(commande_id: int) -> str:
    """Numero lisible d'une commande en ligne, ex. CMD-000123."""
    return f"{PREFIXE_COMMANDE}-{commande_id:06d}"