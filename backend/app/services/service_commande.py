"""
Cycle de vie des commandes en ligne.
Chemin : backend/app/services/service_commande.py

Regle metier : le stock N'EST PAS decremente a la commande. Il l'est
uniquement a l'ACCEPTATION par le gerant (via service_stock, audite et
atomique). Le refus ne touche pas au stock ; l'annulation d'une commande
deja validee rembourse le stock. Ne commite pas (l'appelant gere la
transaction).
"""
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.modeles import Commande, LigneCommande, Produit, VarianteProduit
from app.modeles.enumerations import StatutCommande, StatutProduit
from app.services import service_stock
from app.utils.references import numero_commande


class CommandeErreur(Exception):
    """Erreur metier sur une commande (porte un code HTTP)."""

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


def enregistrer_commande(session, donnees , client_id=None) -> Commande:
    ids = [ligne.variante_id for ligne in donnees.lignes]
    if len(ids) != len(set(ids)):
        raise CommandeErreur("Une meme variante apparait plusieurs fois ; regroupez les quantites")

    lignes_preparees: list[dict] = []
    montant_total = Decimal("0")
    for entree in donnees.lignes:
        variante = session.get(VarianteProduit, entree.variante_id)
        if variante is None:
            raise CommandeErreur(f"Variante {entree.variante_id} introuvable", code=404)
        produit = session.get(Produit, variante.produit_id)
        if not variante.actif or not produit.actif or produit.statut != StatutProduit.DISPONIBLE:
            raise CommandeErreur(f"Le produit « {produit.nom} » n'est pas disponible a la commande")
        if variante.quantite_disponible < entree.quantite:
            raise CommandeErreur(
                f"Stock insuffisant pour « {produit.nom} » ({_libelle_variante(variante)}) : "
                f"disponible {variante.quantite_disponible}, demande {entree.quantite}",
                code=409,
            )
        prix = _prix_effectif(produit)
        sous_total = prix * entree.quantite
        montant_total += sous_total
        lignes_preparees.append({
            "variante": variante, "produit": produit,
            "prix_unitaire": prix, "quantite": entree.quantite, "sous_total": sous_total,
        })

    import uuid
    commande = Commande(
        numero=uuid.uuid4().hex,
        client_nom=donnees.client_nom.strip(),
        client_prenom=(donnees.client_prenom or "").strip() or None,
        client_telephone=donnees.client_telephone.strip(),
        moyen_paiement=donnees.moyen_paiement,
        montant_total=montant_total,
        statut=StatutCommande.NOUVELLE,
        notes=donnees.notes,
        client_id=client_id,
    )
    session.add(commande)
    session.flush()
    commande.numero = numero_commande(commande.id)

    for preparee in lignes_preparees:
        variante = preparee["variante"]
        session.add(LigneCommande(
            commande_id=commande.id,
            variante_id=variante.id,
            produit_nom=preparee["produit"].nom,
            couleur=variante.couleur,
            taille=variante.taille,
            prix_unitaire=preparee["prix_unitaire"],
            quantite=preparee["quantite"],
            sous_total=preparee["sous_total"],
        ))

    session.flush()
    return commande


def _obtenir(session, commande_id: int) -> Commande:
    commande = session.get(Commande, commande_id)
    if commande is None:
        raise CommandeErreur("Commande introuvable", code=404)
    return commande


def accepter_commande(session, commande_id: int, utilisateur_id: int) -> Commande:
    commande = _obtenir(session, commande_id)
    if commande.statut != StatutCommande.NOUVELLE:
        raise CommandeErreur(
            f"Seule une commande nouvelle peut etre acceptee (statut actuel : {commande.statut.value})",
            code=409,
        )
    lignes = session.scalars(select(LigneCommande).where(LigneCommande.commande_id == commande_id)).all()
    for ligne in lignes:
        try:
            service_stock.sortir_pour_vente(
                session, ligne.variante_id, ligne.quantite,
                utilisateur_id=utilisateur_id, reference_document=commande.numero,
            )
        except service_stock.StockInsuffisant:
            variante = session.get(VarianteProduit, ligne.variante_id)
            raise CommandeErreur(
                f"Stock insuffisant pour « {ligne.produit_nom} » : "
                f"disponible {variante.quantite_disponible}, demande {ligne.quantite}",
                code=409,
            )
    commande.statut = StatutCommande.VALIDEE
    commande.utilisateur_id = utilisateur_id
    return commande


def refuser_commande(session, commande_id: int, utilisateur_id: int) -> Commande:
    commande = _obtenir(session, commande_id)
    if commande.statut != StatutCommande.NOUVELLE:
        raise CommandeErreur(
            f"Seule une commande nouvelle peut etre refusee (statut actuel : {commande.statut.value})",
            code=409,
        )
    commande.statut = StatutCommande.REFUSEE
    commande.utilisateur_id = utilisateur_id
    return commande


def annuler_commande(session, commande_id: int, utilisateur_id: int) -> Commande:
    commande = _obtenir(session, commande_id)
    if commande.statut in (StatutCommande.REFUSEE, StatutCommande.ANNULEE):
        raise CommandeErreur(
            f"Cette commande ne peut plus etre annulee (statut actuel : {commande.statut.value})",
            code=409,
        )
    # Si elle etait validee, le stock avait ete decremente : on le rembourse.
    if commande.statut == StatutCommande.VALIDEE:
        lignes = session.scalars(select(LigneCommande).where(LigneCommande.commande_id == commande_id)).all()
        for ligne in lignes:
            service_stock.retourner(
                session, ligne.variante_id, ligne.quantite,
                utilisateur_id=utilisateur_id,
                motif=f"Annulation commande {commande.numero}",
                reference_document=commande.numero,
            )
    commande.statut = StatutCommande.ANNULEE
    commande.utilisateur_id = utilisateur_id
    return commande


def charger_commande(session, commande_id: int) -> Commande:
    commande = session.scalar(
        select(Commande).where(Commande.id == commande_id).options(selectinload(Commande.lignes))
    )
    if commande is None:
        raise CommandeErreur("Commande introuvable", code=404)
    return commande