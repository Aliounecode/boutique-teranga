"""
Script d'initialisation des donnees de base (idempotent).
Chemin : backend/initialiser_donnees.py

Lancement (depuis le dossier backend, venv active, apres la migration) :
    python initialiser_donnees.py

Cree, s'ils n'existent pas deja :
  - les roles : gerant, vendeur
  - un compte gerant par defaut (voir identifiants ci-dessous)
  - les categories racines (Sacs, Chaussures) et leurs sous-categories
Peut etre relance sans risque : rien n'est duplique.
"""
import os

from sqlalchemy import select

from app.base_donnees import SessionLocale
from app.modeles import Role, Categorie, Utilisateur
from app.securite.securite import hacher_mot_de_passe
from app.utils.texte import creer_slug


# --- Compte gerant par defaut -----------------------------------------------
# Le mot de passe peut etre defini via la variable d'environnement
# MOT_DE_PASSE_GERANT ; sinon la valeur par defaut ci-dessous est utilisee.
NOM_UTILISATEUR_GERANT = "admin"
MOT_DE_PASSE_GERANT = os.environ.get("MOT_DE_PASSE_GERANT", "admin1234")


ROLES: list[tuple[str, str]] = [
    ("gerant", "Acces complet a la gestion du commerce."),
    ("vendeur", "Enregistre les ventes et consulte les produits et le stock."),
]

CATEGORIES: dict[str, list[str]] = {
    "Sacs": [
        "Sacs à main", "Sacs à bandoulière", "Sacs à dos", "Sacs de soirée",
        "Sacs professionnels", "Mini-sacs", "Sacs de voyage",
    ],
    "Chaussures": [
        "Talons", "Baskets", "Sandales", "Mocassins", "Escarpins",
        "Bottines", "Chaussures de soirée",
    ],
}


def initialiser_roles(session) -> None:
    for nom, description in ROLES:
        existe = session.scalar(select(Role).where(Role.nom == nom))
        if existe is None:
            session.add(Role(nom=nom, description=description))
            print(f"  + role cree : {nom}")
        else:
            print(f"  = role deja present : {nom}")
    session.commit()


def initialiser_gerant(session) -> None:
    existe = session.scalar(
        select(Utilisateur).where(Utilisateur.nom_utilisateur == NOM_UTILISATEUR_GERANT)
    )
    if existe is not None:
        print(f"  = compte gerant deja present : {NOM_UTILISATEUR_GERANT}")
        return
    role_gerant = session.scalar(select(Role).where(Role.nom == "gerant"))
    session.add(
        Utilisateur(
            nom="Administrateur",
            prenom="Boutique",
            nom_utilisateur=NOM_UTILISATEUR_GERANT,
            mot_de_passe_hash=hacher_mot_de_passe(MOT_DE_PASSE_GERANT),
            actif=True,
            role_id=role_gerant.id,
        )
    )
    session.commit()
    print(f"  + compte gerant cree : {NOM_UTILISATEUR_GERANT}  (mot de passe : {MOT_DE_PASSE_GERANT})")
    print("    >>> Change ce mot de passe des la premiere connexion.")


def obtenir_ou_creer_categorie(session, nom: str, parent: Categorie | None = None) -> Categorie:
    slug = creer_slug(nom)
    categorie = session.scalar(select(Categorie).where(Categorie.slug == slug))
    if categorie is None:
        categorie = Categorie(nom=nom, slug=slug, parent=parent)
        session.add(categorie)
        session.flush()  # obtient l'id avant de creer les enfants
        print(f"  + categorie creee : {nom}")
    else:
        print(f"  = categorie deja presente : {nom}")
    return categorie


def initialiser_categories(session) -> None:
    for nom_racine, enfants in CATEGORIES.items():
        racine = obtenir_ou_creer_categorie(session, nom_racine)
        for nom_enfant in enfants:
            obtenir_ou_creer_categorie(session, nom_enfant, parent=racine)
    session.commit()


def main() -> None:
    session = SessionLocale()
    try:
        print("Initialisation des roles...")
        initialiser_roles(session)
        print("Initialisation du compte gerant...")
        initialiser_gerant(session)
        print("Initialisation des categories...")
        initialiser_categories(session)
        print("\nInitialisation terminee.")
    finally:
        session.close()


if __name__ == "__main__":
    main()