"""
Factures : donnees (depuis une vente ou une commande) + generation PDF.
Chemin : backend/app/services/service_facture.py

La facture est generee a la demande, sans table dediee : son numero derive
du numero de la vente/commande source. (Une numerotation legale sequentielle
avec table Facture pourra etre ajoutee plus tard si necessaire.)
"""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.modeles.enumerations import StatutCommande, StatutVente
from app.utils.formatage import LIBELLES_MOYEN, formater_fcfa


def _lignes(source) -> list[dict]:
    return [
        {
            "produit_nom": ligne.produit_nom,
            "couleur": ligne.couleur,
            "taille": ligne.taille,
            "prix_unitaire": ligne.prix_unitaire,
            "quantite": ligne.quantite,
            "sous_total": ligne.sous_total,
        }
        for ligne in source.lignes
    ]


def donnees_facture_vente(vente) -> dict:
    client = vente.client
    moyens = ", ".join(sorted({LIBELLES_MOYEN[p.moyen] for p in vente.paiements})) or "-"
    return {
        "numero_facture": f"FACT-{vente.numero}",
        "date": vente.date_vente,
        "source_type": "Vente en caisse",
        "source_numero": vente.numero,
        "client_nom": client.nom if client else "Client anonyme",
        "client_prenom": client.prenom if client else None,
        "client_telephone": client.telephone if client else None,
        "annulee": vente.statut == StatutVente.ANNULEE,
        "lignes": _lignes(vente),
        "montant_total": vente.montant_total,
        "moyen_paiement": moyens,
    }


def donnees_facture_commande(commande) -> dict:
    return {
        "numero_facture": f"FACT-{commande.numero}",
        "date": commande.date_commande,
        "source_type": "Commande en ligne",
        "source_numero": commande.numero,
        "client_nom": commande.client_nom,
        "client_prenom": commande.client_prenom,
        "client_telephone": commande.client_telephone,
        "annulee": commande.statut in (StatutCommande.ANNULEE, StatutCommande.REFUSEE),
        "lignes": _lignes(commande),
        "montant_total": commande.montant_total,
        "moyen_paiement": LIBELLES_MOYEN[commande.moyen_paiement],
    }


def generer_pdf_facture(donnees: dict, nom_boutique: str, adresse: str | None = None, telephone: str | None = None) -> bytes:
    tampon = io.BytesIO()
    doc = SimpleDocTemplate(
        tampon, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
        title=donnees["numero_facture"],
    )
    styles = getSampleStyleSheet()
    style_droite = ParagraphStyle("droite", parent=styles["Normal"], alignment=TA_RIGHT)
    style_total = ParagraphStyle("total", parent=styles["Heading3"], alignment=TA_RIGHT)
    story: list = []

    story.append(Paragraph(nom_boutique, styles["Title"]))
    coordonnees = " · ".join(x for x in (adresse, telephone) if x)
    if coordonnees:
        story.append(Paragraph(coordonnees, styles["Normal"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("FACTURE", styles["Heading1"]))
    story.append(Paragraph(
        f"N° {donnees['numero_facture']} — {donnees['date'].strftime('%d/%m/%Y')}", styles["Normal"]))
    story.append(Paragraph(
        f"Référence : {donnees['source_numero']} ({donnees['source_type']})", styles["Normal"]))
    if donnees["annulee"]:
        style_annule = ParagraphStyle("annule", parent=styles["Normal"], textColor=colors.red)
        story.append(Paragraph("<b>DOCUMENT ANNULÉ</b>", style_annule))
    story.append(Spacer(1, 10))

    nom_client = donnees["client_nom"]
    if donnees.get("client_prenom"):
        nom_client += f" {donnees['client_prenom']}"
    ligne_client = f"<b>Facturé à :</b> {nom_client}"
    if donnees.get("client_telephone"):
        ligne_client += f" — Tél : {donnees['client_telephone']}"
    story.append(Paragraph(ligne_client, styles["Normal"]))
    story.append(Spacer(1, 12))

    corps = [["Produit", "Qté", "Prix unitaire", "Sous-total"]]
    for ligne in donnees["lignes"]:
        nom = ligne["produit_nom"]
        variante = " / ".join(x for x in (ligne["couleur"], ligne["taille"]) if x)
        if variante:
            nom += f" ({variante})"
        corps.append([
            Paragraph(nom, styles["Normal"]),
            str(ligne["quantite"]),
            formater_fcfa(ligne["prix_unitaire"]),
            formater_fcfa(ligne["sous_total"]),
        ])
    table = Table(corps, colWidths=[8.5 * cm, 1.5 * cm, 3.5 * cm, 3.5 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(table)
    story.append(Spacer(1, 10))

    story.append(Paragraph(f"Total : {formater_fcfa(donnees['montant_total'])}", style_total))
    story.append(Paragraph(f"Moyen de paiement : {donnees['moyen_paiement']}", style_droite))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Merci de votre confiance.", styles["Italic"]))
    story.append(Paragraph(
        f"Document généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles["Italic"]))

    doc.build(story)
    return tampon.getvalue()