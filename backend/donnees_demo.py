"""
Donnees de demonstration : quelques produits pour tester la boutique.
Chemin : backend/donnees_demo.py

Lancement (venv active, apres les migrations et initialiser_donnees.py) :
    python donnees_demo.py

Idempotent : un produit deja present (meme nom) n'est pas recree.
Les produits n'ont pas de photo (elles s'ajouteront via l'API photos ou
l'interface gerant) : la boutique affichera un visuel de remplacement elegant.
"""
from decimal import Decimal

from sqlalchemy import select

from app.base_donnees import SessionLocale
from app.modeles import Categorie, Produit, VarianteProduit
from app.modeles.enumerations import StatutProduit
from app.utils.references import reference_produit, reference_variante

# Chaque produit : nom, slug de categorie, prix, prix_promo (ou None), a_tailles, variantes.
# Chaque variante : (couleur, taille, quantite_disponible, stock_minimum)
PRODUITS = [
    # ----- SACS (a_tailles = False : pas de pointure) -----
    ("Sac à main Aïda", "sacs-a-main", 45000, None, False, [
        ("Noir", None, 8, 2), ("Camel", None, 5, 2), ("Bordeaux", None, 3, 2)]),
    ("Sac bandoulière Linguère", "sacs-a-bandouliere", 58000, None, False, [
        ("Noir", None, 6, 2), ("Taupe", None, 4, 2)]),
    ("Mini-sac Djolof soirée", "mini-sacs", 38000, 30000, False, [
        ("Doré", None, 5, 1), ("Noir", None, 4, 1)]),
    ("Sac à dos Ndar", "sacs-a-dos", 42000, None, False, [
        ("Noir", None, 7, 2), ("Gris", None, 5, 2)]),
    ("Pochette soirée Signare", "sacs-de-soiree", 28000, None, False, [
        ("Argent", None, 6, 1), ("Noir", None, 0, 1)]),  # une couleur en rupture
    ("Sac professionnel Yoff", "sacs-professionnels", 65000, None, False, [
        ("Noir", None, 4, 2), ("Marron", None, 3, 2)]),

    # ----- CHAUSSURES (a_tailles = True : avec pointures) -----
    ("Escarpins Théodora", "escarpins", 32000, 26000, True, [
        ("Noir", "38", 4, 1), ("Noir", "39", 6, 1), ("Noir", "40", 3, 1),
        ("Rouge", "38", 2, 1), ("Rouge", "39", 0, 1)]),  # une pointure epuisee
    ("Sandales Téranga", "sandales", 25000, None, True, [
        ("Beige", "37", 5, 1), ("Beige", "38", 6, 1), ("Beige", "39", 4, 1),
        ("Noir", "38", 3, 1), ("Noir", "39", 2, 1)]),
    ("Baskets Yeewu", "baskets", 35000, None, True, [
        ("Blanc", "38", 5, 1), ("Blanc", "39", 6, 1), ("Blanc", "40", 4, 1), ("Blanc", "41", 3, 1)]),
    ("Talons Jolof", "talons", 30000, None, True, [
        ("Noir", "37", 3, 1), ("Noir", "38", 5, 1), ("Noir", "39", 4, 1), ("Noir", "40", 2, 1)]),
    ("Bottines Harmattan", "bottines", 40000, None, True, [
        ("Marron", "38", 3, 1), ("Marron", "39", 4, 1), ("Marron", "40", 2, 1)]),
]


def creer_produit(session, nom, slug, prix, prix_promo, a_tailles, variantes):
    if session.scalar(select(Produit).where(Produit.nom == nom)) is not None:
        print(f"  = produit deja present : {nom}")
        return

    categorie = session.scalar(select(Categorie).where(Categorie.slug == slug))
    if categorie is None:
        print(f"  ! categorie introuvable ({slug}) — produit ignore : {nom}")
        return

    produit = Produit(
        nom=nom,
        reference="TEMP",  # remplace apres flush par PRD-xxxxxx
        categorie_id=categorie.id,
        prix=Decimal(prix),
        prix_promo=Decimal(prix_promo) if prix_promo else None,
        en_promotion=prix_promo is not None,
        a_tailles=a_tailles,
        statut=StatutProduit.DISPONIBLE,
        actif=True,
    )
    session.add(produit)
    session.flush()
    produit.reference = reference_produit(produit.id)

    for couleur, taille, quantite, stock_min in variantes:
        variante = VarianteProduit(
            produit_id=produit.id,
            couleur=couleur,
            taille=taille,
            quantite_disponible=quantite,
            stock_minimum=stock_min,
            actif=True,
        )
        session.add(variante)
        session.flush()
        variante.reference_variante = reference_variante(produit.reference, variante.id)

    print(f"  + produit cree : {nom}  ({len(variantes)} variante(s))")


def main():
    session = SessionLocale()
    try:
        print("Insertion des produits de demonstration...")
        for nom, slug, prix, promo, a_tailles, variantes in PRODUITS:
            creer_produit(session, nom, slug, prix, promo, a_tailles, variantes)
        session.commit()
        print("\nTermine.")
    finally:
        session.close()


if __name__ == "__main__":
    main()