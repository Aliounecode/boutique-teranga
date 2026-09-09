"""
Endpoints du tableau de bord (reserves au gerant).
Chemin : backend/app/routeurs/dashboard.py

Periode par defaut : aujourd'hui (parametres date_debut / date_fin).
"""
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.schemas.dashboard import (
    ResumeTableauBord,
    TopCategorie,
    TopProduit,
    VentesPeriodiques,
)
from app.securite.dependances import exiger_gerant
from app.services import service_dashboard

routeur = APIRouter(
    prefix="/tableau-bord", tags=["Tableau de bord"],
    dependencies=[Depends(exiger_gerant)],
)

Session_ = Annotated[Session, Depends(obtenir_session)]


@routeur.get("/resume", response_model=ResumeTableauBord)
def resume(session: Session_, date_debut: date | None = None, date_fin: date | None = None):
    return service_dashboard.resume(session, date_debut, date_fin)


@routeur.get("/ventes-periodiques", response_model=VentesPeriodiques)
def ventes_periodiques(
    session: Session_,
    granularite: Literal["jour", "semaine", "mois"] = "jour",
    date_debut: date | None = None,
    date_fin: date | None = None,
):
    return service_dashboard.ventes_periodiques(session, granularite, date_debut, date_fin)


@routeur.get("/top-produits", response_model=list[TopProduit])
def top_produits(
    session: Session_,
    date_debut: date | None = None,
    date_fin: date | None = None,
    limite: int = Query(default=10, ge=1, le=50),
):
    return service_dashboard.top_produits(session, date_debut, date_fin, limite)


@routeur.get("/top-categories", response_model=list[TopCategorie])
def top_categories(
    session: Session_,
    date_debut: date | None = None,
    date_fin: date | None = None,
    limite: int = Query(default=10, ge=1, le=50),
):
    return service_dashboard.top_categories(session, date_debut, date_fin, limite)