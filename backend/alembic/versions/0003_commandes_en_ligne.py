"""Commandes en ligne : commandes et lignes de commande

Revision ID: 0003_commandes
Revises: 0002_commerce
Create Date: 2026-09-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_commandes"
down_revision: Union[str, None] = "0002_commerce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


VALEURS_MOYEN_PAIEMENT = ("ESPECES", "WAVE", "ORANGE_MONEY", "FREE_MONEY", "CARTE", "AUTRE")

# statutcommande est un NOUVEAU type : on le cree normalement (les deux dialectes).
statut_commande = sa.Enum("NOUVELLE", "VALIDEE", "REFUSEE", "ANNULEE", name="statutcommande")

MAINTENANT = sa.text("CURRENT_TIMESTAMP")


def _type_moyen_paiement():
    """Reference le type moyenpaiement DEJA cree en 0002.

    Sur PostgreSQL, on utilise postgresql.ENUM(create_type=False) pour NE PAS
    tenter de recreer le type (le drapeau create_type n'est respecte que par le
    type du dialecte, pas par sa.Enum generique). Sur SQLite, un enum generique
    (VARCHAR + CHECK) suffit.
    """
    if op.get_bind().dialect.name == "postgresql":
        return postgresql.ENUM(*VALEURS_MOYEN_PAIEMENT, name="moyenpaiement", create_type=False)
    return sa.Enum(*VALEURS_MOYEN_PAIEMENT, name="moyenpaiement")


def upgrade() -> None:
    op.create_table(
        "commandes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numero", sa.String(length=50), nullable=False),
        sa.Column("client_nom", sa.String(length=100), nullable=False),
        sa.Column("client_prenom", sa.String(length=100), nullable=True),
        sa.Column("client_telephone", sa.String(length=30), nullable=False),
        sa.Column("moyen_paiement", _type_moyen_paiement(), nullable=False),
        sa.Column("montant_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("statut", statut_commande, nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("utilisateur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id"), nullable=True),
        sa.Column("date_commande", sa.DateTime(), server_default=MAINTENANT, nullable=False),
        sa.UniqueConstraint("numero", name="uq_commandes_numero"),
    )

    op.create_table(
        "lignes_commande",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("commande_id", sa.Integer(), sa.ForeignKey("commandes.id"), nullable=False),
        sa.Column("variante_id", sa.Integer(), sa.ForeignKey("variantes_produit.id"), nullable=False),
        sa.Column("produit_nom", sa.String(length=200), nullable=False),
        sa.Column("couleur", sa.String(length=50), nullable=True),
        sa.Column("taille", sa.String(length=20), nullable=True),
        sa.Column("prix_unitaire", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("quantite", sa.Integer(), nullable=False),
        sa.Column("sous_total", sa.Numeric(precision=12, scale=2), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("lignes_commande")
    op.drop_table("commandes")
    # On supprime uniquement le type cree ici. moyenpaiement appartient a 0002.
    statut_commande.drop(op.get_bind(), checkfirst=True)