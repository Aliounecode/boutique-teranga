"""
Rapport de la journee : donnees + generation PDF.
Chemin : backend/app/services/service_rapport.py

Reutilise service_dashboard pour les chiffres partages, et ajoute les
compteurs propres au rapport (commandes recues/refusees, reapprovisionnements,
ruptures). Le PDF est genere en memoire avec reportlab.
"""
import io
from datetime import date, datetime, time, timedelta
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import func, select

from app.modeles import Commande, MouvementStock, Produit, VarianteProduit
from app.modeles.enumerations import MoyenPaiement, StatutCommande, TypeMouvementStock
from app.services import service_dashboard
from app.utils.formatage import LIBELLES_MOYEN, formater_fcfa


def donnees_rapport(session, jour: date | None = None) -> dict:
    jour = jour or date.today()
    base = service_dashboard.resume(session, jour, jour)
    debut = datetime.combine(jour, time.min)
    fin = datetime.combine(jour + timedelta(days=1), time.min)

    recues = session.scalar(
        select(func.count()).select_from(Commande)
        .where(Commande.date_commande >= debut, Commande.date_commande < fin)
    ) or 0
    refusees = session.scalar(
        select(func.count()).select_from(Commande)
        .where(Commande.statut == StatutCommande.REFUSEE, Commande.date_commande >= debut, Commande.date_commande < fin)
    ) or 0
    reapprovisionnes = session.scalar(
        select(func.coalesce(func.sum(MouvementStock.quantite), 0))
        .where(
            MouvementStock.type_mouvement == TypeMouvementStock.REAPPROVISIONNEMENT,
            MouvementStock.date_mouvement >= debut,
            MouvementStock.date_mouvement < fin,
        )
    ) or 0

    en_rupture = session.scalar(
        select(func.count()).select_from(VarianteProduit)
        .join(Produit, VarianteProduit.produit_id == Produit.id)
        .where(VarianteProduit.actif.is_(True), Produit.actif.is_(True), VarianteProduit.quantite_disponible <= 0)
    ) or 0
    proches_rupture = session.scalar(
        select(func.count()).select_from(VarianteProduit)
        .join(Produit, VarianteProduit.produit_id == Produit.id)
        .where(
            VarianteProduit.actif.is_(True), Produit.actif.is_(True),
            VarianteProduit.stock_minimum > 0,
            VarianteProduit.quantite_disponible > 0,
            VarianteProduit.quantite_disponible <= VarianteProduit.stock_minimum,
        )
    ) or 0

    presents = {p["moyen"]: p["montant"] for p in base["paiements_par_moyen"]}
    paiements = [{"moyen": moyen, "montant": presents.get(moyen, Decimal("0"))} for moyen in MoyenPaiement]

    return {
        "date": jour,
        "ventes": {
            "nombre_total": base["nombre_ventes_physiques"] + base["nombre_commandes_validees"],
            "physiques_nombre": base["nombre_ventes_physiques"],
            "physiques_montant": base["total_ventes_physiques"],
            "en_ligne_nombre": base["nombre_commandes_validees"],
            "en_ligne_montant": base["total_ventes_en_ligne"],
            "chiffre_affaires": base["chiffre_affaires"],
        },
        "paiements": paiements,
        "commandes": {
            "recues": recues,
            "validees": base["nombre_commandes_validees"],
            "refusees": refusees,
            "annulees": base["commandes_annulees"],
        },
        "stock": {
            "articles_vendus": base["nombre_articles_vendus"],
            "reapprovisionnes": int(reapprovisionnes),
            "en_rupture": en_rupture,
            "proches_rupture": proches_rupture,
        },
    }


def _section(titre: str, lignes: list[tuple[str, str]], styles) -> list:
    elements = [Paragraph(titre, styles["Heading3"])]
    corps = [
        [Paragraph(f"<b>{libelle}</b>", styles["Normal"]), Paragraph(valeur, styles["Normal"])]
        for libelle, valeur in lignes
    ]
    table = Table(corps, colWidths=[9 * cm, 8 * cm])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f5f5f5")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 14))
    return elements


def generer_pdf_rapport(donnees: dict, nom_boutique: str, adresse: str | None = None, telephone: str | None = None) -> bytes:
    tampon = io.BytesIO()
    doc = SimpleDocTemplate(
        tampon, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
        title=f"Rapport du {donnees['date'].isoformat()}",
    )
    styles = getSampleStyleSheet()
    story: list = []

    story.append(Paragraph(nom_boutique, styles["Title"]))
    coordonnees = " · ".join(x for x in (adresse, telephone) if x)
    if coordonnees:
        story.append(Paragraph(coordonnees, styles["Normal"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Rapport de la journée — {donnees['date'].strftime('%d/%m/%Y')}", styles["Heading2"]))
    story.append(Spacer(1, 12))

    v = donnees["ventes"]
    story += _section("Ventes", [
        ("Ventes physiques", f"{v['physiques_nombre']}  ({formater_fcfa(v['physiques_montant'])})"),
        ("Ventes en ligne", f"{v['en_ligne_nombre']}  ({formater_fcfa(v['en_ligne_montant'])})"),
        ("Nombre total de ventes", str(v["nombre_total"])),
        ("Chiffre d'affaires", formater_fcfa(v["chiffre_affaires"])),
    ], styles)

    story += _section("Encaissements par moyen de paiement", [
        (LIBELLES_MOYEN[p["moyen"]], formater_fcfa(p["montant"])) for p in donnees["paiements"]
    ], styles)

    c = donnees["commandes"]
    story += _section("Commandes en ligne", [
        ("Reçues", str(c["recues"])),
        ("Validées", str(c["validees"])),
        ("Refusées", str(c["refusees"])),
        ("Annulées", str(c["annulees"])),
    ], styles)

    s = donnees["stock"]
    story += _section("Stock", [
        ("Articles vendus", str(s["articles_vendus"])),
        ("Articles réapprovisionnés", str(s["reapprovisionnes"])),
        ("Variantes en rupture", str(s["en_rupture"])),
        ("Variantes proches de la rupture", str(s["proches_rupture"])),
    ], styles)

    story.append(Spacer(1, 18))
    story.append(Paragraph(
        f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles["Italic"]
    ))

    doc.build(story)
    return tampon.getvalue()