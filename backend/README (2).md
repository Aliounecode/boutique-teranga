# API Boutique — Sacs & Chaussures

Backend (API REST) d'une plateforme qui réunit, sur une seule base, une **boutique e-commerce** et un **système de gestion commerciale** : catalogue, stock audité, caisse physique (POS), commandes en ligne, clients, tableau de bord et documents PDF (rapport journalier, factures).

Pensé pour une petite/moyenne boutique réelle (contexte sénégalais : montants en **FCFA**, moyens de paiement mobiles Wave / Orange Money / Free Money).

---

## Sommaire

1. [Fonctionnalités](#fonctionnalités)
2. [Stack technique](#stack-technique)
3. [Architecture du projet](#architecture-du-projet)
4. [Modèle de données](#modèle-de-données)
5. [Installation & démarrage](#installation--démarrage)
6. [Configuration (.env)](#configuration-env)
7. [Authentification & rôles](#authentification--rôles)
8. [Référence de l'API](#référence-de-lapi)
9. [Décisions de conception clés](#décisions-de-conception-clés)
10. [Migrations de base de données](#migrations-de-base-de-données)
11. [Limites connues & évolutions](#limites-connues--évolutions)

---

## Fonctionnalités

- **Authentification JWT** avec contrôle d'accès par rôles (**gérant** / **vendeur**).
- **Catalogue** : catégories hiérarchiques, produits, **variantes** (couleur × taille), photos hébergées sur Cloudinary.
- **Stock audité** : moteur centralisé qui verrouille la variante, met à jour la quantité **et** journalise chaque mouvement (traçabilité inviolable). Réapprovisionnement, correction d'inventaire, alertes de rupture.
- **Caisse (POS)** : enregistrement d'une vente physique en une **transaction atomique** (décrément du stock + lignes + paiement), vente anonyme ou nominative, annulation avec remboursement du stock.
- **Commandes en ligne** : passage de commande public (sans compte), cycle de vie _nouvelle → validée / refusée → annulée_ ; le stock n'est décrémenté qu'à l'**acceptation** par le gérant.
- **Clients** : fiche client avec historique et **total dépensé** calculé.
- **Tableau de bord** : chiffre d'affaires, ventes physiques vs en ligne, **encaissements par moyen de paiement**, top produits / catégories, séries temporelles.
- **Documents PDF** : **rapport de la journée** et **factures** (vente ou commande).

---

## Stack technique

| Composant                  | Choix                            |
| -------------------------- | -------------------------------- |
| Langage                    | Python 3.11+                     |
| Framework web              | FastAPI                          |
| ORM                        | SQLAlchemy 2.0 (mapping typé)    |
| Base de données            | PostgreSQL (pilote `psycopg` v3) |
| Migrations                 | Alembic                          |
| Validation / sérialisation | Pydantic v2                      |
| Authentification           | JWT (`pyjwt`) + hachage `bcrypt` |
| Stockage images            | Cloudinary                       |
| Génération PDF             | ReportLab                        |

Le code (noms de variables, fonctions, dossiers) est rédigé **en français** pour la lisibilité.

---

## Architecture du projet

Organisation en couches : **modèles** (tables) → **schémas** (contrats d'entrée/sortie) → **services** (logique métier) → **routeurs** (endpoints HTTP).

```
backend/
├── alembic/
│   ├── env.py                     # environnement de migration (pré-configuré)
│   └── versions/
│       ├── 0001_initiale_creation_tables.py
│       ├── 0002_commerce_ventes_clients.py
│       └── 0003_commandes_en_ligne.py
├── alembic.ini
├── requirements.txt
├── .env                           # configuration locale (NON versionné)
├── .env.example                   # modèle de configuration
├── initialiser_donnees.py         # script de seed (rôles, gérant, catégories)
└── app/
    ├── main.py                    # point d'entrée FastAPI (montage des routeurs + CORS)
    ├── config.py                  # paramètres lus depuis .env (Pydantic Settings)
    ├── base_donnees.py            # moteur SQLAlchemy, session, Base
    ├── modeles/                   # tables (SQLAlchemy)
    │   ├── enumerations.py        # StatutProduit, TypeMouvementStock, StatutVente,
    │   │                          #   MoyenPaiement, StatutCommande
    │   ├── role.py  utilisateur.py
    │   ├── categorie.py  produit.py  variante_produit.py  photo_produit.py
    │   ├── mouvement_stock.py
    │   ├── client.py  vente.py  ligne_vente.py  paiement.py
    │   └── commande.py  ligne_commande.py
    ├── schemas/                   # modèles Pydantic (validation + réponses)
    │   ├── auth.py  utilisateur.py  role.py
    │   ├── categorie.py  produit.py  variante_produit.py  photo_produit.py
    │   ├── client.py  vente.py  paiement.py  commande.py
    │   ├── mouvement_stock.py  dashboard.py  rapport.py
    ├── securite/
    │   ├── securite.py            # hachage bcrypt + création/décodage JWT
    │   └── dependances.py         # utilisateur_courant + RBAC (exiger_gerant…)
    ├── routeurs/                  # endpoints par domaine
    │   ├── auth.py  categories.py  produits.py  photos.py  stock.py
    │   ├── clients.py  ventes.py  commandes.py
    │   └── dashboard.py  rapports.py  factures.py
    ├── services/                  # logique métier
    │   ├── service_stock.py       # moteur de stock audité (cœur du système)
    │   ├── service_vente.py       # enregistrement d'une vente (atomique)
    │   ├── service_commande.py    # cycle de vie des commandes
    │   ├── service_dashboard.py   # agrégations du tableau de bord
    │   ├── service_rapport.py     # rapport journalier (données + PDF)
    │   ├── service_facture.py     # factures (données + PDF)
    │   └── service_cloudinary.py  # upload / suppression des photos
    └── utils/
        ├── references.py          # génération des références (PRD-, V-, CMD-)
        ├── pagination.py          # bornes limite/décalage
        ├── texte.py               # creer_slug
        └── formatage.py           # formater_fcfa + libellés des moyens de paiement
```

---

## Modèle de données

### Tables

| Table               | Rôle                                   | Points clés                                                                                                                                        |
| ------------------- | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `roles`             | Rôles applicatifs                      | `gerant`, `vendeur`                                                                                                                                |
| `utilisateurs`      | Comptes internes                       | mot de passe **haché** (bcrypt), rattaché à un rôle                                                                                                |
| `categories`        | Catégories du catalogue                | **hiérarchiques** (`parent_id` auto-référencé), `slug` unique                                                                                      |
| `produits`          | Produits                               | `reference` unique, `prix`/`prix_promo`, `en_promotion`, `a_tailles`, `statut`, `actif`                                                            |
| `variantes_produit` | Déclinaisons d'un produit              | **couleur × taille**, `quantite_disponible` = **source de vérité du stock**, `stock_minimum` (seuil d'alerte) ; unicité (produit, couleur, taille) |
| `photos_produit`    | Photos produit                         | `url` + `public_id` Cloudinary, `ordre`, `est_principale`                                                                                          |
| `mouvements_stock`  | **Journal d'audit du stock**           | type, quantité, quantité avant/après, motif, utilisateur, horodatage                                                                               |
| `clients`           | Clients enregistrés (ventes physiques) | historique/total **dérivés** des ventes                                                                                                            |
| `ventes`            | Ventes physiques (caisse)              | `numero` unique, client optionnel (**vente anonyme**), vendeur, montant, statut                                                                    |
| `lignes_vente`      | Détail d'une vente                     | **snapshots** : nom produit, couleur/taille, **prix unitaire figé**                                                                                |
| `paiements`         | Paiement d'une vente                   | montant, moyen, utilisateur, référence externe (ex. tx Wave)                                                                                       |
| `commandes`         | Commandes en ligne                     | `numero` unique, coordonnées client inline (guest), moyen de paiement, statut                                                                      |
| `lignes_commande`   | Détail d'une commande                  | mêmes snapshots que `lignes_vente`                                                                                                                 |

### Énumérations

- **StatutProduit** : `disponible`, `bientot_disponible` — _la rupture n'est pas un statut, elle est calculée depuis le stock._
- **TypeMouvementStock** : `vente`, `reapprovisionnement`, `retour`, `correction`, `perte`.
- **StatutVente** : `validee`, `annulee`.
- **MoyenPaiement** : `especes`, `wave`, `orange_money`, `free_money`, `carte`, `autre`.
- **StatutCommande** : `nouvelle`, `validee`, `refusee`, `annulee`.

### Relations principales

```
Role 1───n Utilisateur
Categorie 1───n Categorie (sous-catégories)   Categorie 1───n Produit
Produit 1───n VarianteProduit                 Produit 1───n PhotoProduit
VarianteProduit 1───n MouvementStock
Client 1───n Vente     Vente 1───n LigneVente     Vente 1───n Paiement
Commande 1───n LigneCommande
```

---

## Installation & démarrage

### 1. Prérequis

- Python 3.11 ou supérieur
- PostgreSQL 14+ (testé avec la série 15/16)
- Un compte **Cloudinary** (offre gratuite) si l'on utilise les photos produits

### 2. Environnement virtuel + dépendances

```bash
cd backend
python -m venv venv
# Windows :
venv\Scripts\activate
# macOS / Linux :
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Base de données PostgreSQL

Dans `psql` (connecté en superutilisateur `postgres`) :

```sql
-- Rôle en minuscules pour éviter les guillemets. Adaptez le mot de passe.
CREATE ROLE boutique_user WITH LOGIN PASSWORD 'MotDePasse';
CREATE DATABASE boutique_db OWNER boutique_user;
```

> **PostgreSQL 15+** : le rôle doit être **propriétaire** de la base (`OWNER boutique_user`), sinon la création des tables échoue sur _« droit refusé pour le schéma public »_. Si la base existe déjà sans propriétaire adéquat, corriger avec, **connecté à la base** (`psql -U postgres -d boutique_db`) :
>
> ```sql
> ALTER SCHEMA public OWNER TO boutique_user;
> GRANT ALL ON SCHEMA public TO boutique_user;
> ALTER DATABASE boutique_db OWNER TO boutique_user;
> ```

### 4. Fichier `.env`

Copier le modèle puis le remplir :

```bash
cp .env.example .env
```

Le rôle, le mot de passe et le nom de base doivent être **identiques** entre PostgreSQL et `URL_BASE_DONNEES` (voir la section [Configuration](#configuration-env)).

### 5. Migrations + données initiales

```bash
alembic upgrade head            # crée toutes les tables
python initialiser_donnees.py   # rôles, compte gérant par défaut, catégories
```

Le seed crée un compte **gérant** par défaut :

- identifiant : `admin`
- mot de passe : `mdp` (ou la valeur de `MOT_DE_PASSE_GERANT` si définie dans `.env`)

> **Changez ce mot de passe après la première connexion.**

### 6. Lancer le serveur

```bash
uvicorn app.main:application --reload
```

- API : `http://localhost:8000`
- Documentation interactive (Swagger) : `http://localhost:8000/docs`

Sur `/docs`, cliquer sur **Authorize** puis se connecter (`admin` / mot de passe) pour tester les endpoints protégés.

---

## Configuration (.env)

| Variable                | Obligatoire     | Défaut        | Description                                                                    |
| ----------------------- | --------------- | ------------- | ------------------------------------------------------------------------------ |
| `URL_BASE_DONNEES`      | oui             | —             | ex. `postgresql+psycopg://boutique_user:MotDePasse@localhost:5432/boutique_db` |
| `CLE_SECRETE_JWT`       | oui             | —             | clé longue et aléatoire pour signer les jetons                                 |
| `ALGORITHME_JWT`        | non             | `HS256`       | algorithme de signature JWT                                                    |
| `DUREE_TOKEN_MINUTES`   | non             | `1440`        | durée de validité d'un jeton (minutes)                                         |
| `MODE_DEBUG`            | non             | `false`       | logs SQL et mode debug                                                         |
| `CLOUDINARY_CLOUD_NAME` | pour les photos | —             | identifiant de l'environnement Cloudinary                                      |
| `CLOUDINARY_API_KEY`    | pour les photos | —             | clé API Cloudinary                                                             |
| `CLOUDINARY_API_SECRET` | pour les photos | —             | secret API Cloudinary (**ne jamais exposer**)                                  |
| `NOM_BOUTIQUE`          | non             | `Ma Boutique` | nom affiché dans l'en-tête des PDF                                             |
| `ADRESSE_BOUTIQUE`      | non             | —             | adresse affichée dans les PDF                                                  |
| `TELEPHONE_BOUTIQUE`    | non             | —             | téléphone affiché dans les PDF                                                 |
| `MOT_DE_PASSE_GERANT`   | non             | ``            | mot de passe du compte gérant créé par le seed                                 |

`.env` est ignoré par Git (`.gitignore`) — les secrets ne partent jamais dans le dépôt.

---

## Authentification & rôles

- Connexion via `POST /auth/connexion` (flux OAuth2 standard, corps `x-www-form-urlencoded` avec `username` / `password`). Réponse : un **jeton JWT**.
- Les requêtes protégées envoient l'en-tête `Authorization: Bearer <jeton>`.
- Le jeton contient l'`id` de l'utilisateur (dans `sub`, en texte) et son `role`.

### Rôles (RBAC)

| Rôle        | Peut faire                                                                                           |
| ----------- | ---------------------------------------------------------------------------------------------------- |
| **gérant**  | tout : catalogue, stock, paramètres, suppressions, tableau de bord, rapports                         |
| **vendeur** | enregistrer des ventes, consulter produits/stock, créer/consulter des clients, imprimer des factures |

Les endpoints appliquent le contrôle via les dépendances `exiger_gerant` et `exiger_gerant_ou_vendeur`. Un jeton vendeur sur une route réservée au gérant renvoie **403**.

---

## Référence de l'API

Légende des accès : **Public** (sans authentification) · **Vendeur+** (gérant ou vendeur) · **Gérant**.

### Authentification — `/auth`

| Méthode | Route             | Accès    | Description                     |
| ------- | ----------------- | -------- | ------------------------------- |
| POST    | `/auth/connexion` | Public   | Connexion, renvoie un jeton JWT |
| GET     | `/auth/moi`       | Connecté | Profil de l'utilisateur courant |

### Catégories — `/categories`

| Méthode | Route                | Accès  | Description                                       |
| ------- | -------------------- | ------ | ------------------------------------------------- |
| GET     | `/categories`        | Public | Arbre des catégories actives                      |
| GET     | `/categories/toutes` | Gérant | Liste plate (actives + inactives)                 |
| GET     | `/categories/{id}`   | Public | Détail d'une catégorie                            |
| POST    | `/categories`        | Gérant | Créer (slug auto)                                 |
| PATCH   | `/categories/{id}`   | Gérant | Modifier (nom, description, parent, actif)        |
| DELETE  | `/categories/{id}`   | Gérant | Supprimer **si** aucune sous-catégorie ni produit |

### Produits — `/produits`

| Méthode | Route                      | Accès  | Description                                 |
| ------- | -------------------------- | ------ | ------------------------------------------- |
| GET     | `/produits`                | Public | Liste boutique (filtres, tri, pagination)   |
| GET     | `/produits/gestion`        | Gérant | Liste incluant les produits désactivés      |
| GET     | `/produits/{id}`           | Public | Détail (variantes, photos, catégorie)       |
| POST    | `/produits`                | Gérant | Créer un produit **avec ses variantes**     |
| PATCH   | `/produits/{id}`           | Gérant | Modifier le produit                         |
| DELETE  | `/produits/{id}`           | Gérant | Supprimer **si** aucun historique de stock  |
| POST    | `/produits/{id}/variantes` | Gérant | Ajouter une variante                        |
| PATCH   | `/produits/variantes/{id}` | Gérant | Modifier une variante (hors quantité)       |
| DELETE  | `/produits/variantes/{id}` | Gérant | Supprimer une variante (jamais la dernière) |

**Filtres de `GET /produits`** : `recherche`, `categorie_id` (inclut les sous-catégories), `prix_min`, `prix_max`, `couleur`, `taille`, `en_stock`, `en_promotion`, `tri` (`recent` / `prix_asc` / `prix_desc` / `nom`), `page`, `taille_page`.

### Photos produit

| Méthode | Route                              | Accès  | Description                                   |
| ------- | ---------------------------------- | ------ | --------------------------------------------- |
| GET     | `/produits/{id}/photos`            | Public | Liste ordonnée des photos                     |
| POST    | `/produits/{id}/photos`            | Gérant | Upload **multi-fichiers** (Cloudinary)        |
| PATCH   | `/photos/{id}`                     | Gérant | Définir la photo principale / changer l'ordre |
| POST    | `/produits/{id}/photos/reordonner` | Gérant | Réordonner (liste d'identifiants)             |
| DELETE  | `/photos/{id}`                     | Gérant | Supprimer (Cloudinary + base)                 |

### Stock — `/stock`

| Méthode | Route                     | Accès  | Description                                      |
| ------- | ------------------------- | ------ | ------------------------------------------------ |
| POST    | `/stock/reapprovisionner` | Gérant | Ajouter du stock (audité)                        |
| POST    | `/stock/corriger`         | Gérant | Fixer une quantité exacte (inventaire, audité)   |
| GET     | `/stock/mouvements`       | Gérant | Historique filtrable (variante / produit / type) |
| GET     | `/stock/alertes`          | Gérant | Ruptures et stocks faibles                       |

### Clients — `/clients`

| Méthode | Route           | Accès    | Description                                  |
| ------- | --------------- | -------- | -------------------------------------------- |
| GET     | `/clients`      | Vendeur+ | Liste + recherche (nom / prénom / téléphone) |
| GET     | `/clients/{id}` | Vendeur+ | Détail + **total dépensé** + nombre d'achats |
| POST    | `/clients`      | Vendeur+ | Créer                                        |
| PATCH   | `/clients/{id}` | Vendeur+ | Modifier                                     |
| DELETE  | `/clients/{id}` | Gérant   | Supprimer **si** aucune vente                |

### Ventes (caisse / POS) — `/ventes`

| Méthode | Route                  | Accès    | Description                            |
| ------- | ---------------------- | -------- | -------------------------------------- |
| POST    | `/ventes`              | Vendeur+ | **Enregistrer une vente** (atomique)   |
| GET     | `/ventes`              | Vendeur+ | Liste (filtres date / client / statut) |
| GET     | `/ventes/{id}`         | Vendeur+ | Détail (lignes + paiement)             |
| POST    | `/ventes/{id}/annuler` | Gérant   | Annuler + **rembourser le stock**      |

### Commandes en ligne — `/commandes`

| Méthode | Route                      | Accès      | Description                             |
| ------- | -------------------------- | ---------- | --------------------------------------- |
| POST    | `/commandes`               | **Public** | Passer une commande (checkout invité)   |
| GET     | `/commandes`               | Gérant     | Liste (filtres statut / date)           |
| GET     | `/commandes/{id}`          | Gérant     | Détail                                  |
| POST    | `/commandes/{id}/accepter` | Gérant     | Valider + **décrémenter le stock**      |
| POST    | `/commandes/{id}/refuser`  | Gérant     | Refuser (sans toucher au stock)         |
| POST    | `/commandes/{id}/annuler`  | Gérant     | Annuler (rembourse le stock si validée) |

### Tableau de bord — `/tableau-bord`

| Méthode | Route                              | Accès  | Description                                                                                           |
| ------- | ---------------------------------- | ------ | ----------------------------------------------------------------------------------------------------- |
| GET     | `/tableau-bord/resume`             | Gérant | CA, ventes physiques/en ligne, encaissements par moyen, remboursements, commandes en attente/annulées |
| GET     | `/tableau-bord/ventes-periodiques` | Gérant | Série `jour` / `semaine` / `mois` (graphiques)                                                        |
| GET     | `/tableau-bord/top-produits`       | Gérant | Produits les plus vendus                                                                              |
| GET     | `/tableau-bord/top-categories`     | Gérant | Catégories les plus vendues                                                                           |

Paramètres de période : `date_debut`, `date_fin` (défaut : aujourd'hui).

### Rapports — `/rapports`

| Méthode | Route                          | Accès  | Description                               |
| ------- | ------------------------------ | ------ | ----------------------------------------- |
| GET     | `/rapports/journalier/donnees` | Gérant | Rapport du jour en **JSON** (aperçu)      |
| GET     | `/rapports/journalier`         | Gérant | Rapport du jour en **PDF** téléchargeable |

### Factures — `/factures`

| Méthode | Route                     | Accès    | Description                    |
| ------- | ------------------------- | -------- | ------------------------------ |
| GET     | `/factures/vente/{id}`    | Vendeur+ | Facture **PDF** d'une vente    |
| GET     | `/factures/commande/{id}` | Vendeur+ | Facture **PDF** d'une commande |

---

## Décisions de conception clés

1. **Le stock vit au niveau de la variante.** Tout produit possède au moins une variante (même un sac sans pointure). La quantité est portée par `variantes_produit.quantite_disponible` : c'est l'unique source de vérité.

2. **La rupture n'est jamais stockée, elle est calculée.** Le `statut` produit ne stocke que _disponible_ / _bientôt disponible_ ; la rupture et la disponibilité à l'achat sont déduites du stock, ce qui évite tout statut périmé.

3. **Moteur de stock unique et audité (`service_stock`).** Toute variation de stock passe par ce service, qui **verrouille la variante** (`SELECT … FOR UPDATE` sur PostgreSQL), met à jour la quantité **et** écrit un `MouvementStock` (avant/après, type, motif, utilisateur, date). Il est **impossible** de modifier une quantité sans laisser de trace — la modification directe de la quantité via le PATCH variante a été volontairement retirée.

4. **Transactions atomiques.** Une vente ou l'acceptation d'une commande valident, décrémentent le stock et créent les lignes/paiements **en un seul bloc**. Si une seule ligne manque de stock, tout est annulé (rollback) : aucune vente, aucun décrément.

5. **Prix figés (snapshots).** Les lignes de vente et de commande copient le **nom du produit, la couleur/taille et le prix unitaire** au moment de la transaction. Les factures et l'historique restent exacts même si le produit change de prix plus tard. Le prix appliqué est le **prix effectif** (prix promotionnel si `en_promotion`).

6. **Stock décrémenté à la bonne étape.** En caisse, le stock baisse immédiatement (paiement sur place). En ligne, il ne baisse qu'à l'**acceptation** de la commande par le gérant — conforme au cahier des charges et robuste face aux ventes concurrentes.

7. **Suppressions protégées.** Catégorie, produit, variante et client ne sont supprimés **que** s'ils n'ont pas de dépendances (sous-catégories, produits, historique de stock, ventes). Sinon, on **désactive** (`actif = false`) pour préserver l'intégrité et l'historique.

8. **Deux canaux, une seule vérité financière.** Le tableau de bord fusionne ventes physiques et commandes validées ; les annulées alimentent les remboursements et sont exclues du chiffre d'affaires.

9. **PDF générés en mémoire.** Rapports et factures sont produits à la volée avec ReportLab et renvoyés en flux — aucun fichier temporaire sur le serveur.

---

## Migrations de base de données

Les migrations Alembic sont **pré-configurées** (pas besoin de `alembic init`) : `alembic/env.py` lit la Base et l'URL depuis la configuration.

```bash
alembic upgrade head          # applique toutes les migrations
alembic downgrade -1          # revient d'une migration
alembic downgrade base        # supprime tout
alembic history               # historique des révisions
alembic revision --autogenerate -m "description"   # nouvelle migration (base existante requise)
```

Historique des révisions :

- `0001_initiale` — auth, catalogue, stock (7 tables + enums produit/mouvement)
- `0002_commerce` — clients, ventes, lignes de vente, paiements (+ enums vente/paiement)
- `0003_commandes` — commandes en ligne et lignes de commande (+ enum commande)

> **Point d'attention PostgreSQL** : lorsqu'une migration **réutilise** un type ENUM déjà créé (ex. `moyenpaiement` réutilisé par `commandes`), il faut le référencer via `postgresql.ENUM(..., create_type=False)` — sinon PostgreSQL tente de recréer le type et échoue (_« le type existe déjà »_). Ce motif est appliqué dans `0003`.

---

## Limites connues & évolutions

- **Logo image sur les PDF** : l'en-tête est actuellement textuel (nom + coordonnées). Ajouter un logo nécessiterait de stocker l'image (upload Cloudinary ou fichier local + chemin en configuration).
- **Date de validation des commandes** : les statistiques filtrent les commandes sur `date_commande` (date de passage), faute d'une date de validation stockée séparément. Exact pour une boutique traitant ses commandes le jour même ; une colonne `date_validation` permettrait une comptabilité au cordeau sur la date d'acceptation.
- **Statut de paiement des commandes** : les commandes enregistrent un moyen de paiement _prévu_ mais pas un état « payé / en attente » (pas de passerelle — simple enregistrement). Un suivi d'encaissement pourrait être ajouté.
- **Numérotation légale des factures** : la facture dérive son numéro de la vente/commande source, sans table dédiée. Une table `Facture` avec numérotation séquentielle pourra être introduite si la réglementation l'exige.
- **Livraison** : hors périmètre de cette version (la conception la prévoit : modes et frais).
- **Tests automatisés** : chaque module a été validé manuellement ; l'intégration d'une suite `pytest` au dépôt reste à faire.
- **Facture côté client** : les factures sont pour l'instant accessibles au personnel (gérant/vendeur). Un accès client sécurisé (jeton/lien) permettrait au client de télécharger la sienne.

---

_Backend développé par étapes, chaque brique testée avant intégration. Frontend Angular à venir pour consommer cette API (boutique client + interface gérant)._
