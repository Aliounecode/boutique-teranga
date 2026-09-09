"""
Agregations du tableau de bord (lecture seule).
Chemin : backend/app/services/service_dashboard.py

Le chiffre d'affaires combine deux canaux : ventes physiques VALIDEE et
commandes en ligne VALIDEE. Les ventes/commandes ANNULEE alimentent les
remboursements. Le bucketing temporel est fait en Python pour rester
portable (pas de date_trunc/strftime specifique a un dialecte).

Note : la periode des commandes est filtree sur date_commande (la date de
validation n'est pas stockee separement ; pour une boutique traitant ses
commandes le jour meme, c'est une bonne approximation).
"""
from collections import defaultdict
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from sqlalchemy import func, select

from app.modeles import (
    Categorie,
    Commande,
    LigneCommande,
    LigneVente,
    Paiement,
    Produit,
    VarianteProduit,
    Vente,
)
from app.modeles.enumerations import StatutCommande, StatutVente


def _dec(valeur) -> Decimal:
    return Decimal(str(valeur))


def _bornes(date_debut: date | None, date_fin: date | None):
    aujourdhui = date.today()
    date_debut = date_debut or aujourdhui
    date_fin = date_fin or aujourdhui
    debut = datetime.combine(date_debut, time.min)
    fin = datetime.combine(date_fin + timedelta(days=1), time.min)
    return date_debut, date_fin, debut, fin


def resume(session, date_debut=None, date_fin=None) -> dict:
    d0, d1, debut, fin = _bornes(date_debut, date_fin)

    montant_phys, nb_phys = session.execute(
        select(func.coalesce(func.sum(Vente.montant_total), 0), func.count())
        .where(Vente.statut == StatutVente.VALIDEE, Vente.date_vente >= debut, Vente.date_vente < fin)
    ).one()

    montant_ligne, nb_cmd = session.execute(
        select(func.coalesce(func.sum(Commande.montant_total), 0), func.count())
        .where(Commande.statut == StatutCommande.VALIDEE, Commande.date_commande >= debut, Commande.date_commande < fin)
    ).one()

    articles_phys = session.scalar(
        select(func.coalesce(func.sum(LigneVente.quantite), 0))
        .join(Vente, LigneVente.vente_id == Vente.id)
        .where(Vente.statut == StatutVente.VALIDEE, Vente.date_vente >= debut, Vente.date_vente < fin)
    ) or 0
    articles_ligne = session.scalar(
        select(func.coalesce(func.sum(LigneCommande.quantite), 0))
        .join(Commande, LigneCommande.commande_id == Commande.id)
        .where(Commande.statut == StatutCommande.VALIDEE, Commande.date_commande >= debut, Commande.date_commande < fin)
    ) or 0

    remb_phys = session.scalar(
        select(func.coalesce(func.sum(Vente.montant_total), 0))
        .where(Vente.statut == StatutVente.ANNULEE, Vente.date_vente >= debut, Vente.date_vente < fin)
    ) or 0
    remb_ligne = session.scalar(
        select(func.coalesce(func.sum(Commande.montant_total), 0))
        .where(Commande.statut == StatutCommande.ANNULEE, Commande.date_commande >= debut, Commande.date_commande < fin)
    ) or 0

    commandes_en_attente = session.scalar(
        select(func.count()).select_from(Commande).where(Commande.statut == StatutCommande.NOUVELLE)
    ) or 0
    commandes_annulees = session.scalar(
        select(func.count()).select_from(Commande)
        .where(Commande.statut == StatutCommande.ANNULEE, Commande.date_commande >= debut, Commande.date_commande < fin)
    ) or 0

    # Encaissements par moyen : paiements des ventes validees + commandes validees
    par_moyen: dict = defaultdict(lambda: [Decimal("0"), 0])
    for moyen, montant, nombre in session.execute(
        select(Paiement.moyen, func.coalesce(func.sum(Paiement.montant), 0), func.count())
        .join(Vente, Paiement.vente_id == Vente.id)
        .where(Vente.statut == StatutVente.VALIDEE, Vente.date_vente >= debut, Vente.date_vente < fin)
        .group_by(Paiement.moyen)
    ).all():
        par_moyen[moyen][0] += _dec(montant)
        par_moyen[moyen][1] += nombre
    for moyen, montant, nombre in session.execute(
        select(Commande.moyen_paiement, func.coalesce(func.sum(Commande.montant_total), 0), func.count())
        .where(Commande.statut == StatutCommande.VALIDEE, Commande.date_commande >= debut, Commande.date_commande < fin)
        .group_by(Commande.moyen_paiement)
    ).all():
        par_moyen[moyen][0] += _dec(montant)
        par_moyen[moyen][1] += nombre

    paiements = [
        {"moyen": moyen, "montant": valeurs[0], "nombre": valeurs[1]}
        for moyen, valeurs in par_moyen.items()
    ]
    paiements.sort(key=lambda element: element["montant"], reverse=True)

    return {
        "date_debut": d0,
        "date_fin": d1,
        "chiffre_affaires": _dec(montant_phys) + _dec(montant_ligne),
        "total_ventes_physiques": _dec(montant_phys),
        "nombre_ventes_physiques": nb_phys,
        "total_ventes_en_ligne": _dec(montant_ligne),
        "nombre_commandes_validees": nb_cmd,
        "nombre_articles_vendus": int(articles_phys) + int(articles_ligne),
        "remboursements": _dec(remb_phys) + _dec(remb_ligne),
        "commandes_en_attente": commandes_en_attente,
        "commandes_annulees": commandes_annulees,
        "paiements_par_moyen": paiements,
    }


def _cle_periode(dt: datetime, granularite: str) -> str:
    jour = dt.date() if isinstance(dt, datetime) else dt
    if granularite == "mois":
        return jour.strftime("%Y-%m")
    if granularite == "semaine":
        lundi = jour - timedelta(days=jour.weekday())
        return lundi.strftime("%Y-%m-%d")
    return jour.strftime("%Y-%m-%d")


def ventes_periodiques(session, granularite="jour", date_debut=None, date_fin=None) -> dict:
    _, _, debut, fin = _bornes(date_debut, date_fin)

    enregistrements: list[tuple[datetime, Decimal]] = []
    for dt, montant in session.execute(
        select(Vente.date_vente, Vente.montant_total)
        .where(Vente.statut == StatutVente.VALIDEE, Vente.date_vente >= debut, Vente.date_vente < fin)
    ).all():
        enregistrements.append((dt, _dec(montant)))
    for dt, montant in session.execute(
        select(Commande.date_commande, Commande.montant_total)
        .where(Commande.statut == StatutCommande.VALIDEE, Commande.date_commande >= debut, Commande.date_commande < fin)
    ).all():
        enregistrements.append((dt, _dec(montant)))

    buckets: dict = defaultdict(lambda: [Decimal("0"), 0])
    for dt, montant in enregistrements:
        cle = _cle_periode(dt, granularite)
        buckets[cle][0] += montant
        buckets[cle][1] += 1

    points = [
        {"periode": cle, "montant": valeurs[0], "nombre": valeurs[1]}
        for cle, valeurs in sorted(buckets.items())
    ]
    return {"granularite": granularite, "points": points}


def _agreger_top(session, colonne_id, colonne_nom, ligne_modele, lien_id, filtre):
    """Agrege (id, nom) -> (quantite, montant) sur un modele de lignes donne."""
    return session.execute(
        select(colonne_id, colonne_nom, func.sum(ligne_modele.quantite), func.sum(ligne_modele.sous_total))
        .join(VarianteProduit, ligne_modele.variante_id == VarianteProduit.id)
        .join(Produit, VarianteProduit.produit_id == Produit.id)
        .join(lien_id[0], getattr(ligne_modele, lien_id[1]) == lien_id[0].id)
        .where(*filtre)
        .group_by(colonne_id, colonne_nom)
    ).all()


def top_produits(session, date_debut=None, date_fin=None, limite=10) -> list[dict]:
    _, _, debut, fin = _bornes(date_debut, date_fin)
    agg: dict = defaultdict(lambda: {"nom": "", "qte": 0, "montant": Decimal("0")})

    lignes_v = _agreger_top(
        session, Produit.id, Produit.nom, LigneVente, (Vente, "vente_id"),
        (Vente.statut == StatutVente.VALIDEE, Vente.date_vente >= debut, Vente.date_vente < fin),
    )
    lignes_c = _agreger_top(
        session, Produit.id, Produit.nom, LigneCommande, (Commande, "commande_id"),
        (Commande.statut == StatutCommande.VALIDEE, Commande.date_commande >= debut, Commande.date_commande < fin),
    )
    for pid, nom, qte, montant in list(lignes_v) + list(lignes_c):
        agg[pid]["nom"] = nom
        agg[pid]["qte"] += int(qte)
        agg[pid]["montant"] += _dec(montant)

    resultat = [
        {"produit_id": pid, "produit_nom": d["nom"], "quantite_vendue": d["qte"], "montant": d["montant"]}
        for pid, d in agg.items()
    ]
    resultat.sort(key=lambda element: element["quantite_vendue"], reverse=True)
    return resultat[:limite]


def top_categories(session, date_debut=None, date_fin=None, limite=10) -> list[dict]:
    _, _, debut, fin = _bornes(date_debut, date_fin)
    agg: dict = defaultdict(lambda: {"nom": "", "qte": 0, "montant": Decimal("0")})

    for ligne_modele, lien, filtre in (
        (LigneVente, (Vente, "vente_id"),
         (Vente.statut == StatutVente.VALIDEE, Vente.date_vente >= debut, Vente.date_vente < fin)),
        (LigneCommande, (Commande, "commande_id"),
         (Commande.statut == StatutCommande.VALIDEE, Commande.date_commande >= debut, Commande.date_commande < fin)),
    ):
        for cid, nom, qte, montant in session.execute(
            select(Categorie.id, Categorie.nom, func.sum(ligne_modele.quantite), func.sum(ligne_modele.sous_total))
            .join(VarianteProduit, ligne_modele.variante_id == VarianteProduit.id)
            .join(Produit, VarianteProduit.produit_id == Produit.id)
            .join(Categorie, Produit.categorie_id == Categorie.id)
            .join(lien[0], getattr(ligne_modele, lien[1]) == lien[0].id)
            .where(*filtre)
            .group_by(Categorie.id, Categorie.nom)
        ).all():
            agg[cid]["nom"] = nom
            agg[cid]["qte"] += int(qte)
            agg[cid]["montant"] += _dec(montant)

    resultat = [
        {"categorie_id": cid, "categorie_nom": d["nom"], "quantite_vendue": d["qte"], "montant": d["montant"]}
        for cid, d in agg.items()
    ]
    resultat.sort(key=lambda element: element["quantite_vendue"], reverse=True)
    return resultat[:limite]