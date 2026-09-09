"""
Environnement de migration Alembic — pre-configure pour ce projet.
Chemin : backend/alembic/env.py
Pas besoin de lancer « alembic init » : ce fichier est deja pret.
"""
import sys
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Rend le paquet « app » importable quel que soit le dossier de lancement.
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import parametres
from app.base_donnees import Base
import app.modeles  # noqa: F401  (enregistre tous les modeles sur Base)

config = context.config
config.set_main_option("sqlalchemy.url", parametres.url_base_donnees)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
