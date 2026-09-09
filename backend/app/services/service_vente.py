"""
Enregistrement d'une vente physique (caisse/POS).
Chemin : backend/app/services/service_vente.py

Compose service_stock : chaque ligne decremente le stock de facon audite.
Tout se deroule dans la transaction de l'appelant (atomique) : si une ligne
manque de stock, RIEN n'est enregistre (l'appelant fait rollback). Ne commite
pas lui-meme.
"""
import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from app.modeles import Client, LigneVente, Paiement, Produit, Vente, VarianteProduit
from app.services import service_stock
from app.utils.references import numero_vente


class VenteErreur(Exception):
    """Erreur metier lors de l'enregistrement d'une vente (porte un code HTTP)."""

    def __init__(self, message: str, code: int = 422):
        super().__init__(message)
        self.code = code


def _prix_effectif(produit: Produit) -> Decimal:
    if produit.en_promotion and produit.prix_promo is not None:
        return produit.prix_promo
    return produit.prix


def _libelle_variante(variante: VarianteProduit) -> str:
    parties = [p for p in (variante.couleur, variante.taille) if p]
    return " / ".join(parties) if parties else "unique"


def enregistrer_vente(session, donnees, utilisateur_id: int) -> Vente:
    if not donnees.lignes:
        raise VenteErreur("La vente doit contenir au moins une ligne")

    ids = [ligne.variante_id for ligne in donnees.lignes]
    if len(ids) != len(set(ids)):
        raise VenteErreur("Une meme variante apparait plusieurs fois ; regroupez les quantites")

    if donnees.client_id is not None:
        client = session.get(Client, donnees.client_id)
        if client is None:
            raise VenteErreur("Client introuvable", code=404)
        if not client.actif:
            raise VenteErreur("Ce client est desactive")

    # Validation + preparation (aucune mutation de stock a ce stade)
    lignes_preparees: list[dict] = []
    montant_total = Decimal("0")
    for entree in donnees.lignes:
        variante = session.get(VarianteProduit, entree.variante_id)
        if variante is None:
            raise VenteErreur(f"Variante {entree.variante_id} introuvable", code=404)
        if not variante.actif:
            raise VenteErreur(f"La variante {entree.variante_id} est desactivee")
        produit = session.get(Produit, variante.produit_id)
        if not produit.actif:
            raise VenteErreur(f"Le produit « {produit.nom} » est desactive")

        prix = _prix_effectif(produit)
        sous_total = prix * entree.quantite
        montant_total += sous_total
        lignes_preparees.append({
            "variante": variante,
            "produit": produit,
            "prix_unitaire": prix,
            "quantite": entree.quantite,
            "sous_total": sous_total,
        })

    # Creation de la vente (numero provisoire, puis definitif une fois l'id connu)
    vente = Vente(
        numero=uuid.uuid4().hex,
        client_id=donnees.client_id,
        utilisateur_id=utilisateur_id,
        montant_total=montant_total,
        notes=donnees.notes,
    )
    session.add(vente)
    session.flush()
    vente.numero = numero_vente(vente.id)

    # Decrement du stock (audite) + creation des lignes
    for preparee in lignes_preparees:
        variante = preparee["variante"]
        produit = preparee["produit"]
        try:
            service_stock.sortir_pour_vente(
                session, variante.id, preparee["quantite"],
                utilisateur_id=utilisateur_id, reference_document=vente.numero,
            )
        except service_stock.StockInsuffisant:
            raise VenteErreur(
                f"Stock insuffisant pour « {produit.nom} » ({_libelle_variante(variante)}) : "
                f"disponible {variante.quantite_disponible}, demande {preparee['quantite']}",
                code=409,
            )
        session.add(LigneVente(
            vente_id=vente.id,
            variante_id=variante.id,
            produit_nom=produit.nom,
            couleur=variante.couleur,
            taille=variante.taille,
            prix_unitaire=preparee["prix_unitaire"],
            quantite=preparee["quantite"],
            sous_total=preparee["sous_total"],
        ))

    # Paiement unique (= montant total)
    session.add(Paiement(
        vente_id=vente.id,
        montant=montant_total,
        moyen=donnees.moyen_paiement,
        utilisateur_id=utilisateur_id,
        reference_externe=donnees.reference_paiement,
    ))

    session.flush()
    return vente


def charger_vente(session, vente_id: int) -> Vente:
    vente = session.scalar(
        select(Vente).where(Vente.id == vente_id).options(
            joinedload(Vente.client),
            selectinload(Vente.lignes),
            selectinload(Vente.paiements),
        )
    )
    if vente is None:
        raise VenteErreur("Vente introuvable", code=404)
    return vente