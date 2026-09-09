"""Tables commerce : clients, ventes, lignes de vente, paiements

Revision ID: 0002_commerce
Revises: 0001_initiale
Create Date: 2026-09-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_commerce"
down_revision: Union[str, None] = "0001_initiale"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


statut_vente = sa.Enum("VALIDEE", "ANNULEE", name="statutvente")
moyen_paiement = sa.Enum(
    "ESPECES", "WAVE", "ORANGE_MONEY", "FREE_MONEY", "CARTE", "AUTRE",
    name="moyenpaiement",
)

MAINTENANT = sa.text("CURRENT_TIMESTAMP")


def upgrade() -> None:
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("prenom", sa.String(length=100), nullable=True),
        sa.Column("telephone", sa.String(length=30), nullable=True),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.Column("date_creation", sa.DateTime(), server_default=MAINTENANT, nullable=False),
    )

    op.create_table(
        "ventes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("numero", sa.String(length=50), nullable=False),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=True),
        sa.Column("utilisateur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id"), nullable=False),
        sa.Column("montant_total", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("statut", statut_vente, nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("date_vente", sa.DateTime(), server_default=MAINTENANT, nullable=False),
        sa.UniqueConstraint("numero", name="uq_ventes_numero"),
    )

    op.create_table(
        "lignes_vente",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vente_id", sa.Integer(), sa.ForeignKey("ventes.id"), nullable=False),
        sa.Column("variante_id", sa.Integer(), sa.ForeignKey("variantes_produit.id"), nullable=False),
        sa.Column("produit_nom", sa.String(length=200), nullable=False),
        sa.Column("couleur", sa.String(length=50), nullable=True),
        sa.Column("taille", sa.String(length=20), nullable=True),
        sa.Column("prix_unitaire", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("quantite", sa.Integer(), nullable=False),
        sa.Column("sous_total", sa.Numeric(precision=12, scale=2), nullable=False),
    )

    op.create_table(
        "paiements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("vente_id", sa.Integer(), sa.ForeignKey("ventes.id"), nullable=True),
        sa.Column("montant", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("moyen", moyen_paiement, nullable=False),
        sa.Column("utilisateur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id"), nullable=True),
        sa.Column("reference_externe", sa.String(length=100), nullable=True),
        sa.Column("date_paiement", sa.DateTime(), server_default=MAINTENANT, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("paiements")
    op.drop_table("lignes_vente")
    op.drop_table("ventes")
    op.drop_table("clients")
    moyen_paiement.drop(op.get_bind(), checkfirst=True)
    statut_vente.drop(op.get_bind(), checkfirst=True)