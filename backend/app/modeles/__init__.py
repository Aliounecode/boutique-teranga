"""
Importe les modeles pour que SQLAlchemy les enregistre sur la meme Base.
Chemin : backend/app/modeles/__init__.py
"""
from app.modeles.role import Role
from app.modeles.utilisateur import Utilisateur
from app.modeles.categorie import Categorie
from app.modeles.produit import Produit
from app.modeles.variante_produit import VarianteProduit
from app.modeles.photo_produit import PhotoProduit
from app.modeles.mouvement_stock import MouvementStock
from app.modeles.client import Client
from app.modeles.vente import Vente
from app.modeles.ligne_vente import LigneVente
from app.modeles.paiement import Paiement
from app.modeles.commande import Commande
from app.modeles.ligne_commande import LigneCommande

__all__ = [
    "Role", "Utilisateur", "Categorie", "Produit",
    "VarianteProduit", "PhotoProduit", "MouvementStock",
    "Client", "Vente", "LigneVente", "Paiement",
    "Commande", "LigneCommande",
]