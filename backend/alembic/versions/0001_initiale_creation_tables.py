"""Creation des tables initiales (Phase 1 : auth, catalogue, stock)

Revision ID: 0001_initiale
Revises:
Create Date: 2026-09-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# identifiants de revision, utilises par Alembic.
revision: str = "0001_initiale"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Types enumeres PostgreSQL. Les libelles correspondent aux NOMS des membres
# des enums Python (comportement par defaut de SQLAlchemy pour un Enum).
statut_produit = sa.Enum(
    "DISPONIBLE", "BIENTOT_DISPONIBLE",
    name="statutproduit",
)
type_mouvement_stock = sa.Enum(
    "VENTE", "REAPPROVISIONNEMENT", "RETOUR", "CORRECTION", "PERTE",
    name="typemouvementstock",
)

# Valeur par defaut portable (PostgreSQL comme SQLite) pour les dates.
MAINTENANT = sa.text("CURRENT_TIMESTAMP")


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(length=50), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.UniqueConstraint("nom", name="uq_roles_nom"),
    )

    op.create_table(
        "utilisateurs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("prenom", sa.String(length=100), nullable=False),
        sa.Column("nom_utilisateur", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("telephone", sa.String(length=30), nullable=True),
        sa.Column("mot_de_passe_hash", sa.String(length=255), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.Column("role_id", sa.Integer(), sa.ForeignKey("roles.id"), nullable=False),
        sa.Column("date_creation", sa.DateTime(), server_default=MAINTENANT, nullable=False),
        sa.UniqueConstraint("nom_utilisateur", name="uq_utilisateurs_nom_utilisateur"),
        sa.UniqueConstraint("email", name="uq_utilisateurs_email"),
    )

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=True),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.Column("date_creation", sa.DateTime(), server_default=MAINTENANT, nullable=False),
        sa.UniqueConstraint("slug", name="uq_categories_slug"),
    )

    op.create_table(
        "produits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nom", sa.String(length=200), nullable=False),
        sa.Column("reference", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("categorie_id", sa.Integer(), sa.ForeignKey("categories.id"), nullable=False),
        sa.Column("prix", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("prix_promo", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("en_promotion", sa.Boolean(), nullable=False),
        sa.Column("a_tailles", sa.Boolean(), nullable=False),
        sa.Column("statut", statut_produit, nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.Column("date_creation", sa.DateTime(), server_default=MAINTENANT, nullable=False),
        sa.Column("date_modification", sa.DateTime(), server_default=MAINTENANT, nullable=False),
        sa.UniqueConstraint("reference", name="uq_produits_reference"),
    )

    op.create_table(
        "variantes_produit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("produit_id", sa.Integer(), sa.ForeignKey("produits.id"), nullable=False),
        sa.Column("couleur", sa.String(length=50), nullable=True),
        sa.Column("taille", sa.String(length=20), nullable=True),
        sa.Column("reference_variante", sa.String(length=60), nullable=True),
        sa.Column("quantite_disponible", sa.Integer(), nullable=False),
        sa.Column("stock_minimum", sa.Integer(), nullable=False),
        sa.Column("actif", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("reference_variante", name="uq_variantes_reference"),
        sa.UniqueConstraint("produit_id", "couleur", "taille", name="uq_variante_produit"),
    )

    op.create_table(
        "photos_produit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("produit_id", sa.Integer(), sa.ForeignKey("produits.id"), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("public_id", sa.String(length=255), nullable=True),
        sa.Column("ordre", sa.Integer(), nullable=False),
        sa.Column("est_principale", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "mouvements_stock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("variante_id", sa.Integer(), sa.ForeignKey("variantes_produit.id"), nullable=False),
        sa.Column("type_mouvement", type_mouvement_stock, nullable=False),
        sa.Column("quantite", sa.Integer(), nullable=False),
        sa.Column("quantite_avant", sa.Integer(), nullable=False),
        sa.Column("quantite_apres", sa.Integer(), nullable=False),
        sa.Column("motif", sa.String(length=255), nullable=True),
        sa.Column("reference_document", sa.String(length=60), nullable=True),
        sa.Column("utilisateur_id", sa.Integer(), sa.ForeignKey("utilisateurs.id"), nullable=True),
        sa.Column("date_mouvement", sa.DateTime(), server_default=MAINTENANT, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("mouvements_stock")
    op.drop_table("photos_produit")
    op.drop_table("variantes_produit")
    op.drop_table("produits")
    op.drop_table("categories")
    op.drop_table("utilisateurs")
    op.drop_table("roles")
    # Suppression des types enumeres PostgreSQL (sans effet sur SQLite).
    type_mouvement_stock.drop(op.get_bind(), checkfirst=True)
    statut_produit.drop(op.get_bind(), checkfirst=True)