"""
Endpoints de gestion de l'equipe (reserve au gerant).
Chemin : backend/app/routeurs/utilisateurs.py
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.base_donnees import obtenir_session
from app.modeles import Role, Utilisateur
from app.schemas.role import RoleLecture
from app.schemas.utilisateur import (
    MotDePasseMaj,
    UtilisateurCreation,
    UtilisateurLecture,
    UtilisateurMiseAJour,
)
from app.securite.dependances import exiger_gerant, utilisateur_courant
from app.securite.securite import hacher_mot_de_passe

routeur = APIRouter(
    prefix="/utilisateurs",
    tags=["Utilisateurs"],
    dependencies=[Depends(exiger_gerant)],
)

Session_ = Annotated[Session, Depends(obtenir_session)]
Courant_ = Annotated[Utilisateur, Depends(utilisateur_courant)]


def _charger(session: Session, utilisateur_id: int) -> Utilisateur | None:
    return session.scalars(
        select(Utilisateur).options(selectinload(Utilisateur.role)).where(Utilisateur.id == utilisateur_id)
    ).one_or_none()


def _id_role_gerant(session: Session) -> int:
    role = session.scalar(select(Role).where(Role.nom == "gerant"))
    return role.id if role else -1


def _nb_gerants_actifs(session: Session, exclure_id: int | None = None) -> int:
    requete = (
        select(func.count())
        .select_from(Utilisateur)
        .join(Role)
        .where(Role.nom == "gerant", Utilisateur.actif.is_(True))
    )
    if exclure_id is not None:
        requete = requete.where(Utilisateur.id != exclure_id)
    return session.scalar(requete) or 0


@routeur.get("/roles", response_model=list[RoleLecture])
def lister_roles(session: Session_):
    return session.scalars(select(Role).order_by(Role.id)).all()


@routeur.get("", response_model=list[UtilisateurLecture])
def lister(session: Session_):
    return session.scalars(
        select(Utilisateur).options(selectinload(Utilisateur.role)).order_by(Utilisateur.date_creation)
    ).all()


@routeur.post("", response_model=UtilisateurLecture, status_code=status.HTTP_201_CREATED)
def creer(donnees: UtilisateurCreation, session: Session_):
    if session.scalar(select(Utilisateur).where(Utilisateur.nom_utilisateur == donnees.nom_utilisateur)):
        raise HTTPException(status_code=409, detail="Ce nom d'utilisateur est deja pris.")
    if donnees.email and session.scalar(select(Utilisateur).where(Utilisateur.email == donnees.email)):
        raise HTTPException(status_code=409, detail="Cet e-mail est deja utilise.")
    if session.get(Role, donnees.role_id) is None:
        raise HTTPException(status_code=422, detail="Role invalide.")

    utilisateur = Utilisateur(
        nom=donnees.nom.strip(),
        prenom=donnees.prenom.strip(),
        nom_utilisateur=donnees.nom_utilisateur.strip(),
        email=donnees.email,
        telephone=(donnees.telephone or "").strip() or None,
        mot_de_passe_hash=hacher_mot_de_passe(donnees.mot_de_passe),
        role_id=donnees.role_id,
        actif=True,
    )
    session.add(utilisateur)
    session.commit()
    return _charger(session, utilisateur.id)


@routeur.get("/{utilisateur_id}", response_model=UtilisateurLecture)
def obtenir(utilisateur_id: int, session: Session_):
    utilisateur = _charger(session, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return utilisateur


@routeur.patch("/{utilisateur_id}", response_model=UtilisateurLecture)
def mettre_a_jour(utilisateur_id: int, donnees: UtilisateurMiseAJour, session: Session_, courant: Courant_):
    utilisateur = _charger(session, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    champs = donnees.model_dump(exclude_unset=True)

    if champs.get("email"):
        autre = session.scalar(
            select(Utilisateur).where(Utilisateur.email == champs["email"], Utilisateur.id != utilisateur.id)
        )
        if autre is not None:
            raise HTTPException(status_code=409, detail="Cet e-mail est deja utilise.")
    if champs.get("role_id") is not None and session.get(Role, champs["role_id"]) is None:
        raise HTTPException(status_code=422, detail="Role invalide.")

    id_gerant = _id_role_gerant(session)

    # Protection : ne pas se verrouiller soi-meme.
    if utilisateur.id == courant.id:
        if champs.get("actif") is False:
            raise HTTPException(status_code=422, detail="Vous ne pouvez pas desactiver votre propre compte.")
        if "role_id" in champs and champs["role_id"] != id_gerant:
            raise HTTPException(status_code=422, detail="Vous ne pouvez pas retirer votre propre role de gerant.")

    # Protection : conserver au moins un gerant actif.
    if utilisateur.role.nom == "gerant":
        devient_non_gerant = "role_id" in champs and champs["role_id"] != id_gerant
        devient_inactif = champs.get("actif") is False
        if (devient_non_gerant or devient_inactif) and _nb_gerants_actifs(session, exclure_id=utilisateur.id) == 0:
            raise HTTPException(status_code=422, detail="Impossible : il doit rester au moins un gerant actif.")

    for cle, valeur in champs.items():
        if cle in {"nom", "prenom", "telephone"} and isinstance(valeur, str):
            valeur = valeur.strip() or None if cle == "telephone" else valeur.strip()
        setattr(utilisateur, cle, valeur)
    session.commit()
    return _charger(session, utilisateur.id)


@routeur.post("/{utilisateur_id}/mot-de-passe")
def changer_mot_de_passe(utilisateur_id: int, donnees: MotDePasseMaj, session: Session_):
    utilisateur = session.get(Utilisateur, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    utilisateur.mot_de_passe_hash = hacher_mot_de_passe(donnees.mot_de_passe)
    session.commit()
    return {"message": "Mot de passe mis a jour."}