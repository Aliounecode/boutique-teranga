from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import parametres

moteur = create_engine(
    parametres.url_base_donnees,
    echo=parametres.mode_debug,
    pool_pre_ping=True,
)

SessionLocale = sessionmaker(bind=moteur, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def obtenir_session():
    """Dependance FastAPI : fournit une session et la ferme apres usage."""
    session = SessionLocale()
    try:
        yield session
    finally:
        session.close()

