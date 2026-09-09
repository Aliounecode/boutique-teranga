"""Rattachement des commandes au compte client (client_id)

Revision ID: 0005_commande_client
Revises: 0004_comptes_client
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_commande_client"
down_revision: Union[str, None] = "0004_comptes_client"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("commandes") as batch:
        batch.add_column(sa.Column("client_id", sa.Integer(), nullable=True))
        batch.create_foreign_key("fk_commandes_client", "clients", ["client_id"], ["id"])


def downgrade() -> None:
    with op.batch_alter_table("commandes") as batch:
        batch.drop_constraint("fk_commandes_client", type_="foreignkey")
        batch.drop_column("client_id")