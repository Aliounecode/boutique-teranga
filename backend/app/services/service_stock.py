"""
Moteur de stock : variations sures + journalisation (tracabilite).
Chemin : backend/app/services/service_stock.py

Toute modification de stock passe par ici : la quantite de la variante est
mise a jour ET un MouvementStock est enregistre. Les fonctions NE COMMITENT
PAS : l'appelant controle la transaction (une vente touchant plusieurs
variantes doit etre atomique). La variante est verrouillee (SELECT ... FOR
UPDATE sur PostgreSQL) pour empecher toute vente concurrente en surnombre.
"""
from app.modeles import MouvementStock, VarianteProduit
from app.modeles.enumerations import TypeMouvementStock


class ErreurStock(Exception):
    """Erreur metier liee au stock."""


class StockInsuffisant(ErreurStock):
    pass


class VarianteIntrouvable(ErreurStock):
    pass


def _variante_verrouillee(session, variante_id: int) -> VarianteProduit:
    variante = session.get(VarianteProduit, variante_id, with_for_update=True)
    if variante is None:
        raise VarianteIntrouvable(f"Variante {variante_id} introuvable")
    return variante


def _enregistrer(
    session,
    variante: VarianteProduit,
    variation: int,
    type_mouvement: TypeMouvementStock,
    *,
    utilisateur_id: int | None = None,
    motif: str | None = None,
    reference_document: str | None = None,
) -> MouvementStock:
    avant = variante.quantite_disponible
    apres = avant + variation
    if apres < 0:
        raise StockInsuffisant(f"Stock insuffisant : disponible {avant}, demande {-variation}")

    variante.quantite_disponible = apres
    mouvement = MouvementStock(
        variante_id=variante.id,
        type_mouvement=type_mouvement,
        quantite=abs(variation),
        quantite_avant=avant,
        quantite_apres=apres,
        motif=motif,
        reference_document=reference_document,
        utilisateur_id=utilisateur_id,
    )
    session.add(mouvement)
    session.flush()
    return mouvement


def reapprovisionner(session, variante_id: int, quantite: int, *, utilisateur_id=None, motif=None) -> MouvementStock:
    if quantite <= 0:
        raise ErreurStock("La quantite de reapprovisionnement doit etre positive")
    variante = _variante_verrouillee(session, variante_id)
    return _enregistrer(
        session, variante, +quantite, TypeMouvementStock.REAPPROVISIONNEMENT,
        utilisateur_id=utilisateur_id, motif=motif,
    )


def sortir_pour_vente(session, variante_id: int, quantite: int, *, utilisateur_id=None, reference_document=None) -> MouvementStock:
    if quantite <= 0:
        raise ErreurStock("La quantite vendue doit etre positive")
    variante = _variante_verrouillee(session, variante_id)
    return _enregistrer(
        session, variante, -quantite, TypeMouvementStock.VENTE,
        utilisateur_id=utilisateur_id, reference_document=reference_document,
    )


def retourner(session, variante_id: int, quantite: int, *, utilisateur_id=None, motif=None, reference_document=None) -> MouvementStock:
    if quantite <= 0:
        raise ErreurStock("La quantite retournee doit etre positive")
    variante = _variante_verrouillee(session, variante_id)
    return _enregistrer(
        session, variante, +quantite, TypeMouvementStock.RETOUR,
        utilisateur_id=utilisateur_id, motif=motif, reference_document=reference_document,
    )


def corriger(session, variante_id: int, nouvelle_quantite: int, *, utilisateur_id=None, motif=None) -> MouvementStock:
    if nouvelle_quantite < 0:
        raise ErreurStock("La nouvelle quantite ne peut pas etre negative")
    variante = _variante_verrouillee(session, variante_id)
    variation = nouvelle_quantite - variante.quantite_disponible
    if variation == 0:
        raise ErreurStock("Le stock est deja a cette valeur")
    return _enregistrer(
        session, variante, variation, TypeMouvementStock.CORRECTION,
        utilisateur_id=utilisateur_id, motif=motif,
    )