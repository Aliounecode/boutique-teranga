"""
Dependances FastAPI : utilisateur courant (gerant/vendeur), controle des roles,
et client courant (espace client).
Chemin : backend/app/securite/dependances.py
"""
from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.modeles import Client, Utilisateur
from app.securite.securite import decoder_jeton

schema_oauth2 = OAuth2PasswordBearer(tokenUrl="/auth/connexion")
schema_bearer_client = HTTPBearer(auto_error=True)
schema_bearer_client_opt = HTTPBearer(auto_error=False)

def _erreur_identifiants() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides ou session expiree",
        headers={"WWW-Authenticate": "Bearer"},
    )


def utilisateur_courant(
    jeton: Annotated[str, Depends(schema_oauth2)],
    session: Annotated[Session, Depends(obtenir_session)],
) -> Utilisateur:
    """Personnel (gerant/vendeur). Refuse les jetons de type client / verification."""
    try:
        charge = decoder_jeton(jeton)
        if charge.get("type") not in (None, "utilisateur"):
            raise _erreur_identifiants()
        identifiant = charge.get("sub")
        if identifiant is None:
            raise _erreur_identifiants()
        identifiant = int(identifiant)
    except (jwt.PyJWTError, ValueError, TypeError):
        raise _erreur_identifiants()

    utilisateur = session.get(Utilisateur, identifiant)
    if utilisateur is None or not utilisateur.actif:
        raise _erreur_identifiants()
    return utilisateur


def exiger_roles(*roles_autorises: str) -> Callable[..., Utilisateur]:
    def verificateur(
        utilisateur: Annotated[Utilisateur, Depends(utilisateur_courant)],
    ) -> Utilisateur:
        if utilisateur.role.nom not in roles_autorises:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Droits insuffisants pour cette action",
            )
        return utilisateur

    return verificateur


exiger_gerant = exiger_roles("gerant")
exiger_gerant_ou_vendeur = exiger_roles("gerant", "vendeur")


def client_courant(
    identifiants: Annotated[HTTPAuthorizationCredentials, Depends(schema_bearer_client)],
    session: Annotated[Session, Depends(obtenir_session)],
) -> Client:
    """Client de la boutique. Exige un jeton de type 'client'."""
    try:
        charge = decoder_jeton(identifiants.credentials)
        if charge.get("type") != "client":
            raise _erreur_identifiants()
        identifiant = int(charge.get("sub"))
    except (jwt.PyJWTError, ValueError, TypeError):
        raise _erreur_identifiants()

    client = session.get(Client, identifiant)
    if client is None or not client.actif:
        raise _erreur_identifiants()
    return client
def client_courant_optionnel(
    identifiants: Annotated[HTTPAuthorizationCredentials | None, Depends(schema_bearer_client_opt)],
    session: Annotated[Session, Depends(obtenir_session)],
) -> Client | None:
    """Comme client_courant mais tolerant : renvoie None si pas/plus authentifie."""
    if identifiants is None:
        return None
    try:
        charge = decoder_jeton(identifiants.credentials)
        if charge.get("type") != "client":
            return None
        identifiant = int(charge.get("sub"))
    except (jwt.PyJWTError, ValueError, TypeError):
        return None
    client = session.get(Client, identifiant)
    if client is None or not client.actif:
        return None
    return client