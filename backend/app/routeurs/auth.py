"""
Endpoints d'authentification.
Chemin : backend/app/routeurs/auth.py
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.base_donnees import obtenir_session
from app.modeles import Utilisateur
from app.schemas.auth import Jeton
from app.schemas.utilisateur import UtilisateurLecture
from app.securite.dependances import utilisateur_courant
from app.securite.securite import creer_jeton_acces, verifier_mot_de_passe

routeur = APIRouter(prefix="/auth", tags=["Authentification"])


@routeur.post("/connexion", response_model=Jeton)
def connexion(
    identifiants: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(obtenir_session)],
) -> Jeton:
    """Connexion par nom d'utilisateur + mot de passe. Renvoie un jeton JWT."""
    utilisateur = session.scalar(
        select(Utilisateur).where(Utilisateur.nom_utilisateur == identifiants.username)
    )
    if utilisateur is None or not verifier_mot_de_passe(
        identifiants.password, utilisateur.mot_de_passe_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not utilisateur.actif:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte est desactive",
        )

    jeton = creer_jeton_acces({"sub": str(utilisateur.id), "role": utilisateur.role.nom})
    return Jeton(access_token=jeton)


@routeur.get("/moi", response_model=UtilisateurLecture)
def profil_courant(
    utilisateur: Annotated[Utilisateur, Depends(utilisateur_courant)],
) -> Utilisateur:
    """Renvoie le profil de l'utilisateur connecte."""
    return utilisateur