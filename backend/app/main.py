"""
Point d'entree de l'API FastAPI.
Chemin : backend/app/main.py
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import parametres
from app.routeurs import (
    auth,
    categories,
    clients,
    commandes,
    comptes_client,
    dashboard,
    factures,
    photos,
    produits,
    rapports,
    stock,
    utilisateurs,
    ventes,
)

application = FastAPI(
    title="API Boutique — Sacs & Chaussures",
    version="0.1.0",
    debug=parametres.mode_debug,
)

application.add_middleware(
    CORSMiddleware,
    allow_origins=parametres.liste_origines,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@application.get("/")
def racine():
    return {"message": "API Boutique en ligne", "version": application.version}


application.include_router(auth.routeur)
application.include_router(categories.routeur)
application.include_router(produits.routeur)
application.include_router(photos.routeur)
application.include_router(stock.routeur)
application.include_router(clients.routeur)
application.include_router(ventes.routeur)
application.include_router(commandes.routeur)
application.include_router(dashboard.routeur)
application.include_router(rapports.routeur)
application.include_router(factures.routeur)
application.include_router(comptes_client.routeur)
application.include_router(utilisateurs.routeur)