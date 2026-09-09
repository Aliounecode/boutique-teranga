"""Comptes client en ligne : email, mot de passe, verification

Revision ID: 0004_comptes_client
Revises: 0003_commandes
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_comptes_client"
down_revision: Union[str, None] = "0003_commandes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("email", sa.String(length=255), nullable=True))
    op.add_column("clients", sa.Column("mot_de_passe_hash", sa.String(length=255), nullable=True))
    op.add_column(
        "clients",
        sa.Column("email_verifie", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.create_index("uq_clients_email", "clients", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_clients_email", table_name="clients")
    op.drop_column("clients", "email_verifie")
    op.drop_column("clients", "mot_de_passe_hash")
    op.drop_column("clients", "email")