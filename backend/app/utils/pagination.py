"""
Utilitaires de pagination.
Chemin : backend/app/utils/pagination.py
"""
TAILLE_PAGE_MAX = 100


def calculer_bornes(page: int, taille_page: int) -> tuple[int, int]:
    """Retourne (limite, decalage) a partir d'un numero de page (1-based)."""
    page = max(page, 1)
    taille_page = max(1, min(taille_page, TAILLE_PAGE_MAX))
    return taille_page, (page - 1) * taille_page