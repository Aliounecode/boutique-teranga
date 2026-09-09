"""
Endpoints des rapports (reserves au gerant).
Chemin : backend/app/routeurs/rapports.py
"""
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.config import parametres
from app.schemas.rapport import RapportJournalier
from app.securite.dependances import exiger_gerant
from app.services import service_rapport

routeur = APIRouter(prefix="/rapports", tags=["Rapports"], dependencies=[Depends(exiger_gerant)])

Session_ = Annotated[Session, Depends(obtenir_session)]


@routeur.get("/journalier/donnees", response_model=RapportJournalier)
def rapport_donnees(session: Session_, jour: date | None = None):
    """Donnees du rapport de la journee (JSON, pour l'apercu a l'ecran)."""
    return service_rapport.donnees_rapport(session, jour)


@routeur.get(
    "/journalier",
    responses={200: {"content": {"application/pdf": {}}, "description": "Rapport de la journee au format PDF"}},
)
def rapport_pdf(session: Session_, jour: date | None = None):
    """Rapport de la journee au format PDF (telechargeable)."""
    donnees = service_rapport.donnees_rapport(session, jour)
    pdf = service_rapport.generer_pdf_rapport(
        donnees,
        parametres.nom_boutique,
        parametres.adresse_boutique,
        parametres.telephone_boutique,
    )
    nom_fichier = f"rapport-{donnees['date'].isoformat()}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nom_fichier}"'},
    )