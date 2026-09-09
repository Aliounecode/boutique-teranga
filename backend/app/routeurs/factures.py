"""
Endpoints des factures PDF (gerant ou vendeur).
Chemin : backend/app/routeurs/factures.py
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.config import parametres
from app.securite.dependances import exiger_gerant_ou_vendeur
from app.services import service_commande, service_facture, service_vente

routeur = APIRouter(prefix="/factures", tags=["Factures"], dependencies=[Depends(exiger_gerant_ou_vendeur)])

Session_ = Annotated[Session, Depends(obtenir_session)]

_REPONSE_PDF = {200: {"content": {"application/pdf": {}}, "description": "Facture au format PDF"}}


def _reponse_pdf(pdf: bytes, source_numero: str) -> Response:
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="facture-{source_numero}.pdf"'},
    )


@routeur.get("/vente/{vente_id}", responses=_REPONSE_PDF)
def facture_vente(vente_id: int, session: Session_):
    """Facture PDF d'une vente physique."""
    try:
        vente = service_vente.charger_vente(session, vente_id)
    except service_vente.VenteErreur as erreur:
        raise HTTPException(status_code=erreur.code, detail=str(erreur))
    donnees = service_facture.donnees_facture_vente(vente)
    pdf = service_facture.generer_pdf_facture(
        donnees, parametres.nom_boutique, parametres.adresse_boutique, parametres.telephone_boutique
    )
    return _reponse_pdf(pdf, donnees["source_numero"])


@routeur.get("/commande/{commande_id}", responses=_REPONSE_PDF)
def facture_commande(commande_id: int, session: Session_):
    """Facture PDF d'une commande en ligne."""
    try:
        commande = service_commande.charger_commande(session, commande_id)
    except service_commande.CommandeErreur as erreur:
        raise HTTPException(status_code=erreur.code, detail=str(erreur))
    donnees = service_facture.donnees_facture_commande(commande)
    pdf = service_facture.generer_pdf_facture(
        donnees, parametres.nom_boutique, parametres.adresse_boutique, parametres.telephone_boutique
    )
    return _reponse_pdf(pdf, donnees["source_numero"])