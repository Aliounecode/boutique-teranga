"""
Endpoints des rapports.
Chemin : backend/app/routeurs/rapports.py

- /journalier      : rapport global de la boutique (gerant uniquement).
- /mes-ventes      : ventes realisees par l'utilisateur connecte (gerant ou vendeur).
"""
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.config import parametres
from app.modeles import Utilisateur
from app.schemas.rapport import RapportJournalier
from app.securite.dependances import exiger_gerant, exiger_gerant_ou_vendeur
from app.services import service_rapport

routeur = APIRouter(prefix="/rapports", tags=["Rapports"])

Session_ = Annotated[Session, Depends(obtenir_session)]
Personnel_ = Annotated[Utilisateur, Depends(exiger_gerant_ou_vendeur)]


@routeur.get("/journalier/donnees", response_model=RapportJournalier, dependencies=[Depends(exiger_gerant)])
def rapport_donnees(session: Session_, jour: date | None = None):
    """Donnees du rapport de la journee (JSON, pour l'apercu a l'ecran)."""
    return service_rapport.donnees_rapport(session, jour)


@routeur.get(
    "/journalier",
    dependencies=[Depends(exiger_gerant)],
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


@routeur.get("/mes-ventes/donnees")
def mes_ventes_donnees(session: Session_, courant: Personnel_, jour: date | None = None):
    """Apercu JSON des ventes de l'utilisateur connecte (aucun chiffre global)."""
    return service_rapport.donnees_mes_ventes(session, courant.id, jour)


@routeur.get(
    "/mes-ventes",
    responses={200: {"content": {"application/pdf": {}}, "description": "Mes ventes du jour au format PDF"}},
)
def mes_ventes_pdf(session: Session_, courant: Personnel_, jour: date | None = None):
    """Mes ventes du jour au format PDF (telechargeable)."""
    donnees = service_rapport.donnees_mes_ventes(session, courant.id, jour)
    pdf = service_rapport.generer_pdf_mes_ventes(
        donnees,
        f"{courant.prenom} {courant.nom}",
        parametres.nom_boutique,
        parametres.adresse_boutique,
        parametres.telephone_boutique,
    )
    nom_fichier = f"mes-ventes-{donnees['date'].isoformat()}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nom_fichier}"'},
    )