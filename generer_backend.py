"""
generer_backend.py — Génère l'arborescence complète du backend (FastAPI).

À placer dans le dossier RACINE du projet, à côté du futur dossier backend/ :
    boutique-sacs/
    ├── generer_backend.py   <-- ici
    └── backend/             <-- créé par ce script

Lancement :
    python generer_backend.py

IMPORTANT : ré-exécutable sans risque. Un fichier qui existe déjà (et donc
qui contient peut-être du code que nous avons écrit) n'est JAMAIS écrasé.
"""
from pathlib import Path

# Le backend est généré à côté de ce script.
RACINE = Path(__file__).resolve().parent / "backend"


# ---------------------------------------------------------------------------
# Générateurs de contenu pour les fichiers "vides" (placeholders)
# ---------------------------------------------------------------------------
def placeholder(description: str, chemin: str) -> str:
    """Contenu d'un module non encore implémenté : un en-tête + un TODO."""
    return (
        '"""\n'
        f"{description}\n\n"
        f"Chemin : backend/{chemin}\n"
        "À compléter lors de l'étape correspondante.\n"
        '"""\n\n'
        "# TODO : implémentation à venir.\n"
    )


def paquet(nom: str) -> str:
    """Contenu minimal d'un fichier __init__.py de sous-paquet."""
    return f"# Paquet : {nom}\n"


# ---------------------------------------------------------------------------
# 1) FICHIERS AVEC CONTENU (déjà définis ensemble)
# ---------------------------------------------------------------------------
CONTENUS: dict[str, str] = {

    # ---- Racine du backend -------------------------------------------------
    ".gitignore": '''venv/
__pycache__/
*.pyc
.env
''',

    ".env.example": '''URL_BASE_DONNEES=postgresql+psycopg://boutique_user:motdepasse@localhost:5432/boutique_db
CLE_SECRETE_JWT=change-moi-avec-une-cle-longue-et-aleatoire
ALGORITHME_JWT=HS256
DUREE_TOKEN_MINUTES=1440
MODE_DEBUG=true
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=
''',

    "requirements.txt": '''fastapi
uvicorn[standard]
sqlalchemy
psycopg[binary]
pydantic
pydantic-settings
email-validator
alembic
pyjwt
bcrypt
python-multipart
cloudinary
reportlab
''',

    # ---- Alembic (déjà configuré : pas besoin de « alembic init ») ----------
    "alembic.ini": '''[alembic]
script_location = alembic
prepend_sys_path = .
# L'URL de la base est definie dynamiquement dans alembic/env.py a partir du .env

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname =

[logger_sqlalchemy]
level = WARNING
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
''',

    "alembic/env.py": '''"""
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
''',

    "alembic/script.py.mako": '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# identifiants de revision, utilises par Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
''',

    # ---- Application --------------------------------------------------------
    "app/__init__.py": "# Package principal de l'application\n",

    "app/main.py": '''"""
Point d'entree de l'API FastAPI.
Chemin : backend/app/main.py
Lancement en developpement :
    uvicorn app.main:application --reload
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import parametres

application = FastAPI(
    title="API Boutique — Sacs & Chaussures",
    version="0.1.0",
    debug=parametres.mode_debug,
)

# Autorise le frontend Angular (developpement) a appeler l'API.
application.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@application.get("/")
def racine():
    return {"message": "API Boutique en ligne", "version": application.version}


# ---------------------------------------------------------------------------
# Les routeurs seront inclus ici au fur et a mesure de leur implementation :
#
# from app.routeurs import auth, categories, produits, ventes, commandes, ...
# application.include_router(auth.routeur)
# application.include_router(produits.routeur)
# ...
# ---------------------------------------------------------------------------
''',

    "app/config.py": '''from pydantic_settings import BaseSettings, SettingsConfigDict


class Parametres(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    url_base_donnees: str
    cle_secrete_jwt: str
    algorithme_jwt: str = "HS256"
    duree_token_minutes: int = 1440
    mode_debug: bool = False

    # Cloudinary — utilise a l'etape "photos produits"
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None


parametres = Parametres()
''',

    "app/base_donnees.py": '''from sqlalchemy import create_engine
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
''',

    # ---- Modèles (couche déjà écrite : Phase 1) ----------------------------
    "app/modeles/__init__.py": '''"""
Importe les modeles pour que SQLAlchemy les enregistre sur la meme Base.
Chemin : backend/app/modeles/__init__.py

Au fur et a mesure que les modeles suivants seront implementes, ajouter leur
import ici pour qu'Alembic les detecte automatiquement :
    client, commande, ligne_commande, vente, ligne_vente,
    paiement, facture, journal_audit
"""
from app.modeles.role import Role
from app.modeles.utilisateur import Utilisateur
from app.modeles.categorie import Categorie
from app.modeles.produit import Produit
from app.modeles.variante_produit import VarianteProduit
from app.modeles.photo_produit import PhotoProduit
from app.modeles.mouvement_stock import MouvementStock

__all__ = [
    "Role", "Utilisateur", "Categorie", "Produit",
    "VarianteProduit", "PhotoProduit", "MouvementStock",
]
''',

    "app/modeles/enumerations.py": '''import enum


class StatutProduit(str, enum.Enum):
    DISPONIBLE = "disponible"
    BIENTOT_DISPONIBLE = "bientot_disponible"
    # La rupture n'est PAS ici : elle est calculee depuis le stock des variantes.


class TypeMouvementStock(str, enum.Enum):
    VENTE = "vente"
    REAPPROVISIONNEMENT = "reapprovisionnement"
    RETOUR = "retour"
    CORRECTION = "correction"
    PERTE = "perte"
''',

    "app/modeles/role.py": '''from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # "gerant" / "vendeur"
    description: Mapped[str | None] = mapped_column(String(255))

    utilisateurs: Mapped[list["Utilisateur"]] = relationship(back_populates="role")
''',

    "app/modeles/utilisateur.py": '''from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str] = mapped_column(String(100), nullable=False)
    nom_utilisateur: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    telephone: Mapped[str | None] = mapped_column(String(30))
    mot_de_passe_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=False)
    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())

    role: Mapped["Role"] = relationship(back_populates="utilisateurs")
    mouvements_stock: Mapped[list["MouvementStock"]] = relationship(back_populates="utilisateur")
''',

    "app/modeles/categorie.py": '''from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class Categorie(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))  # sous-categorie eventuelle
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())

    # Hierarchie : "Sacs" (racine) -> "Sacs a main" (enfant)
    parent: Mapped["Categorie | None"] = relationship(
        remote_side=[id], back_populates="sous_categories"
    )
    sous_categories: Mapped[list["Categorie"]] = relationship(back_populates="parent")
    produits: Mapped[list["Produit"]] = relationship(back_populates="categorie")
''',

    "app/modeles/produit.py": '''from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Boolean, ForeignKey, Numeric, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base
from app.modeles.enumerations import StatutProduit


class Produit(Base):
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    prix: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)          # FCFA (montants entiers)
    prix_promo: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    en_promotion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    a_tailles: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # True pour les chaussures
    statut: Mapped[StatutProduit] = mapped_column(
        Enum(StatutProduit), default=StatutProduit.DISPONIBLE, nullable=False
    )
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)       # desactivation != suppression
    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())
    date_modification: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    categorie: Mapped["Categorie"] = relationship(back_populates="produits")
    variantes: Mapped[list["VarianteProduit"]] = relationship(
        back_populates="produit", cascade="all, delete-orphan"
    )
    photos: Mapped[list["PhotoProduit"]] = relationship(
        back_populates="produit", cascade="all, delete-orphan", order_by="PhotoProduit.ordre"
    )
''',

    "app/modeles/variante_produit.py": '''from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class VarianteProduit(Base):
    __tablename__ = "variantes_produit"
    __table_args__ = (
        UniqueConstraint("produit_id", "couleur", "taille", name="uq_variante_produit"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    produit_id: Mapped[int] = mapped_column(ForeignKey("produits.id"), nullable=False)
    couleur: Mapped[str | None] = mapped_column(String(50))
    taille: Mapped[str | None] = mapped_column(String(20))                 # pointure pour les chaussures
    reference_variante: Mapped[str | None] = mapped_column(String(60), unique=True)
    quantite_disponible: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # SOURCE DE VERITE du stock
    stock_minimum: Mapped[int] = mapped_column(Integer, default=0, nullable=False)        # seuil d'alerte
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    produit: Mapped["Produit"] = relationship(back_populates="variantes")
    mouvements_stock: Mapped[list["MouvementStock"]] = relationship(back_populates="variante")
''',

    "app/modeles/photo_produit.py": '''from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class PhotoProduit(Base):
    __tablename__ = "photos_produit"

    id: Mapped[int] = mapped_column(primary_key=True)
    produit_id: Mapped[int] = mapped_column(ForeignKey("produits.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)          # URL publique (Cloudinary)
    public_id: Mapped[str | None] = mapped_column(String(255))            # identifiant Cloudinary (pour suppression)
    ordre: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # ordre dans la galerie
    est_principale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    produit: Mapped["Produit"] = relationship(back_populates="photos")
''',

    "app/modeles/mouvement_stock.py": '''from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base
from app.modeles.enumerations import TypeMouvementStock


class MouvementStock(Base):
    """Journal append-only de tous les mouvements de stock (tracabilite)."""
    __tablename__ = "mouvements_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    variante_id: Mapped[int] = mapped_column(ForeignKey("variantes_produit.id"), nullable=False)
    type_mouvement: Mapped[TypeMouvementStock] = mapped_column(Enum(TypeMouvementStock), nullable=False)
    quantite: Mapped[int] = mapped_column(Integer, nullable=False)          # magnitude (valeur positive)
    quantite_avant: Mapped[int] = mapped_column(Integer, nullable=False)
    quantite_apres: Mapped[int] = mapped_column(Integer, nullable=False)
    motif: Mapped[str | None] = mapped_column(String(255))
    reference_document: Mapped[str | None] = mapped_column(String(60))      # ex : n° de vente / commande liee
    utilisateur_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateurs.id"))
    date_mouvement: Mapped[datetime] = mapped_column(server_default=func.now())

    variante: Mapped["VarianteProduit"] = relationship(back_populates="mouvements_stock")
    utilisateur: Mapped["Utilisateur | None"] = relationship(back_populates="mouvements_stock")
''',
}


# ---------------------------------------------------------------------------
# 2) SOUS-PAQUETS (fichiers __init__.py)
# ---------------------------------------------------------------------------
PAQUETS: list[tuple[str, str]] = [
    ("app/securite/__init__.py", "securite"),
    ("app/schemas/__init__.py", "schemas"),
    ("app/routeurs/__init__.py", "routeurs"),
    ("app/services/__init__.py", "services"),
    ("app/utils/__init__.py", "utils"),
]


# ---------------------------------------------------------------------------
# 3) MODULES À REMPLIR PLUS TARD (placeholders)  ->  (chemin, description)
# ---------------------------------------------------------------------------
PLACEHOLDERS: list[tuple[str, str]] = [

    # --- Modèles restants (a ajouter dans modeles/__init__.py une fois ecrits)
    ("app/modeles/client.py",
     "Modele Client : clients en ligne et clients physiques enregistres (nom, telephone, historique)."),
    ("app/modeles/commande.py",
     "Modele Commande : commandes passees depuis la boutique en ligne (numero, statut, total, client)."),
    ("app/modeles/ligne_commande.py",
     "Modele LigneCommande : detail des variantes commandees dans une commande en ligne."),
    ("app/modeles/vente.py",
     "Modele Vente : ventes physiques enregistrees en caisse (POS)."),
    ("app/modeles/ligne_vente.py",
     "Modele LigneVente : detail des variantes vendues dans une vente physique."),
    ("app/modeles/paiement.py",
     "Modele Paiement : enregistrement du moyen de paiement (especes, Wave, OM...), sans passerelle."),
    ("app/modeles/facture.py",
     "Modele Facture : factures generees pour les ventes physiques et les commandes en ligne."),
    ("app/modeles/journal_audit.py",
     "Modele JournalAudit : tracabilite inviolable des operations sensibles (financieres, droits...)."),

    # --- Sécurité / RBAC
    ("app/securite/securite.py",
     "Hachage des mots de passe (bcrypt) et creation/decodage des jetons JWT."),
    ("app/securite/dependances.py",
     "Dependances FastAPI : recuperation de l'utilisateur courant et controle des roles (RBAC)."),

    # --- Schémas Pydantic
    ("app/schemas/auth.py",
     "Schemas d'authentification : connexion (identifiants) et jeton d'acces."),
    ("app/schemas/role.py", "Schemas Pydantic du role."),
    ("app/schemas/utilisateur.py", "Schemas Pydantic de l'utilisateur (creation, lecture, mise a jour)."),
    ("app/schemas/categorie.py", "Schemas Pydantic des categories (avec hierarchie)."),
    ("app/schemas/produit.py", "Schemas Pydantic du produit (avec variantes et photos)."),
    ("app/schemas/variante_produit.py", "Schemas Pydantic des variantes (couleur, taille, stock)."),
    ("app/schemas/photo_produit.py", "Schemas Pydantic des photos produit."),
    ("app/schemas/client.py", "Schemas Pydantic du client."),
    ("app/schemas/commande.py", "Schemas Pydantic des commandes en ligne."),
    ("app/schemas/vente.py", "Schemas Pydantic des ventes physiques (POS)."),
    ("app/schemas/paiement.py", "Schemas Pydantic des paiements."),
    ("app/schemas/facture.py", "Schemas Pydantic des factures."),
    ("app/schemas/mouvement_stock.py", "Schemas Pydantic des mouvements de stock et reapprovisionnements."),
    ("app/schemas/dashboard.py", "Schemas des statistiques du tableau de bord gerant."),
    ("app/schemas/rapport.py", "Schemas du rapport journalier."),

    # --- Routeurs (endpoints API)
    ("app/routeurs/auth.py", "Endpoints d'authentification (connexion, profil courant)."),
    ("app/routeurs/utilisateurs.py", "Endpoints de gestion des utilisateurs (reserve au gerant)."),
    ("app/routeurs/categories.py", "Endpoints CRUD des categories."),
    ("app/routeurs/produits.py", "Endpoints CRUD des produits (+ recherche et filtres cote boutique)."),
    ("app/routeurs/variantes.py", "Endpoints de gestion des variantes d'un produit."),
    ("app/routeurs/photos.py", "Endpoints d'ajout/suppression des photos produit (Cloudinary)."),
    ("app/routeurs/clients.py", "Endpoints de gestion des clients."),
    ("app/routeurs/commandes.py", "Endpoints des commandes en ligne (creation client, suivi gerant)."),
    ("app/routeurs/ventes.py", "Endpoints de la caisse (POS) : enregistrement des ventes physiques."),
    ("app/routeurs/paiements.py", "Endpoints de consultation des paiements."),
    ("app/routeurs/factures.py", "Endpoints de generation et telechargement des factures PDF."),
    ("app/routeurs/stock.py", "Endpoints du stock : mouvements, reapprovisionnement, alertes de rupture."),
    ("app/routeurs/dashboard.py", "Endpoints des statistiques du tableau de bord."),
    ("app/routeurs/rapports.py", "Endpoints du rapport journalier (consultation, export PDF)."),

    # --- Services (logique métier)
    ("app/services/service_stock.py",
     "Coeur metier du stock : decrement sur (produit occupe), reapprovisionnement, journalisation."),
    ("app/services/service_vente.py",
     "Logique des ventes physiques (POS) : creation d'une vente et decrement du stock."),
    ("app/services/service_commande.py",
     "Cycle de vie des commandes en ligne (machine a etats : nouvelle -> validee -> ...)."),
    ("app/services/service_paiement.py",
     "Enregistrement et agregation des paiements par moyen."),
    ("app/services/service_facture.py",
     "Generation des factures PDF (reportlab) a partir d'une vente ou d'une commande."),
    ("app/services/service_dashboard.py",
     "Agregations statistiques du tableau de bord (CA, ventes, top produits...)."),
    ("app/services/service_rapport.py",
     "Construction et export du rapport journalier."),
    ("app/services/service_cloudinary.py",
     "Envoi et suppression des photos produits sur Cloudinary."),
    ("app/services/service_audit.py",
     "Ecriture des entrees du journal d'audit."),

    # --- Utilitaires
    ("app/utils/references.py",
     "Generation des references uniques (produits, commandes, ventes, factures)."),
    ("app/utils/pagination.py",
     "Utilitaires de pagination des listes (limite, decalage, total)."),
]


# ---------------------------------------------------------------------------
# Écriture (ne remplace jamais un fichier existant)
# ---------------------------------------------------------------------------
def ecrire(chemin_relatif: str, contenu: str) -> str:
    chemin = RACINE / chemin_relatif
    chemin.parent.mkdir(parents=True, exist_ok=True)
    if chemin.exists():
        return "ignore"
    chemin.write_text(contenu, encoding="utf-8")
    return "cree"


def main() -> None:
    print(f"Generation du backend dans : {RACINE}\n")

    # Assemble tous les fichiers dans un ordre lisible.
    fichiers: list[tuple[str, str]] = []
    fichiers += list(CONTENUS.items())
    fichiers += [(chemin, paquet(nom)) for chemin, nom in PAQUETS]
    fichiers += [(chemin, placeholder(desc, chemin)) for chemin, desc in PLACEHOLDERS]

    # Dossier vide a versionner (migrations Alembic).
    fichiers.append(("alembic/versions/.gitkeep", ""))

    nb_crees = nb_ignores = 0
    for chemin, contenu in fichiers:
        etat = ecrire(chemin, contenu)
        if etat == "cree":
            nb_crees += 1
            marque = "avec code" if chemin in CONTENUS else "placeholder"
            print(f"  + {chemin}  ({marque})")
        else:
            nb_ignores += 1
            print(f"  = {chemin}  (deja present, conserve)")

    print(f"\nTermine : {nb_crees} fichier(s) cree(s), {nb_ignores} conserve(s).")
    print("\nProchaines commandes utiles :")
    print("  cd backend")
    print("  source venv/bin/activate        # Windows : venv\\Scripts\\activate")
    print("  pip install -r requirements.txt")
    print("  uvicorn app.main:application --reload   # verifie que l'API demarre (GET /)")


if __name__ == "__main__":
    main()
