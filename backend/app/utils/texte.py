"""
Utilitaires de manipulation de texte.
Chemin : backend/app/utils/texte.py
"""
import unicodedata


def creer_slug(texte: str) -> str:
    """Transforme un libelle en slug : minuscules, sans accents, tirets.

    Exemples : "Sacs à main" -> "sacs-a-main", "Chaussures de soirée" -> "chaussures-de-soiree".
    """
    texte = unicodedata.normalize("NFKD", texte)
    texte = texte.encode("ascii", "ignore").decode("ascii").lower().strip()
    caracteres = [
        c if c.isalnum() else "-"
        for c in texte
        if c.isalnum() or c in (" ", "-", "_", "'")
    ]
    slug = "".join(caracteres)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")