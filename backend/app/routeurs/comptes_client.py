"""
Endpoints de l'espace client : inscription, verification d'e-mail, connexion, profil.
Chemin : backend/app/routeurs/comptes_client.py
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session , selectinload

from app.base_donnees import obtenir_session
from app.config import parametres
from app.modeles import Client , Commande
from app.schemas.commande import CommandeLecture
from app.schemas.compte_client import (
    ClientCompteLecture,
    ConnexionClient,
    InscriptionClient,
    JetonClient,
    MotDePasseOublie,
    ReinitialisationMotDePasse,
    RenvoiVerification,
    VerificationEmail,
)
from app.securite.dependances import client_courant
from app.securite.securite import (
    creer_jeton_client,
    creer_jeton_reset,
    creer_jeton_verification,
    decoder_jeton,
    hacher_mot_de_passe,
    verifier_mot_de_passe,
)
from app.services import service_email

routeur = APIRouter(prefix="/compte", tags=["Espace client"])

Session_ = Annotated[Session, Depends(obtenir_session)]


def _envoyer_verification(client: Client) -> None:
    jeton = creer_jeton_verification(client.id)
    lien = f"{parametres.url_frontend}/verifier-email?token={jeton}"
    service_email.envoyer_verification_email(client.email, client.nom, lien)


@routeur.post("/inscription", status_code=status.HTTP_201_CREATED)
def inscription(donnees: InscriptionClient, session: Session_):
    email = donnees.email.lower()
    if session.scalar(select(Client).where(Client.email == email)) is not None:
        raise HTTPException(status_code=409, detail="Un compte existe deja avec cet e-mail.")

    client = Client(
        nom=donnees.nom.strip(),
        prenom=(donnees.prenom or "").strip() or None,
        telephone=(donnees.telephone or "").strip() or None,
        email=email,
        mot_de_passe_hash=hacher_mot_de_passe(donnees.mot_de_passe),
        email_verifie=False,
        actif=True,
    )
    session.add(client)
    session.flush()  # obtient l'id pour le jeton

    try:
        _envoyer_verification(client)
    except Exception:
        session.rollback()
        raise HTTPException(status_code=502, detail="Impossible d'envoyer l'e-mail de confirmation. Reessayez plus tard.")

    session.commit()
    return {"message": "Compte cree. Verifiez votre boite mail pour confirmer votre adresse."}


@routeur.post("/verifier-email")
def verifier_email(donnees: VerificationEmail, session: Session_):
    try:
        charge = decoder_jeton(donnees.token)
        if charge.get("type") != "verif_email":
            raise ValueError()
        client_id = int(charge.get("sub"))
    except Exception:
        raise HTTPException(status_code=400, detail="Lien de verification invalide ou expire.")

    client = session.get(Client, client_id)
    if client is None:
        raise HTTPException(status_code=400, detail="Lien de verification invalide.")
    if not client.email_verifie:
        client.email_verifie = True
        session.commit()
    return {"message": "Adresse e-mail confirmee. Vous pouvez vous connecter."}


@routeur.post("/renvoyer-verification")
def renvoyer_verification(donnees: RenvoiVerification, session: Session_):
    client = session.scalar(select(Client).where(Client.email == donnees.email.lower()))
    if client is not None and client.mot_de_passe_hash and not client.email_verifie:
        try:
            _envoyer_verification(client)
        except Exception:
            pass
    # Message generique (on ne revele pas si l'e-mail existe).
    return {"message": "Si un compte non confirme existe avec cet e-mail, un nouveau lien a ete envoye."}


@routeur.post("/connexion", response_model=JetonClient)
def connexion(donnees: ConnexionClient, session: Session_):
    client = session.scalar(select(Client).where(Client.email == donnees.email.lower()))
    if client is None or not client.mot_de_passe_hash or not verifier_mot_de_passe(donnees.mot_de_passe, client.mot_de_passe_hash):
        raise HTTPException(status_code=401, detail="E-mail ou mot de passe incorrect.")
    if not client.actif:
        raise HTTPException(status_code=403, detail="Ce compte est desactive.")
    if not client.email_verifie:
        raise HTTPException(status_code=403, detail="Veuillez confirmer votre adresse e-mail avant de vous connecter.")
    return JetonClient(access_token=creer_jeton_client(client.id))


@routeur.get("/moi", response_model=ClientCompteLecture)
def profil(client: Annotated[Client, Depends(client_courant)]):
    return client

@routeur.get("/commandes", response_model=list[CommandeLecture])
def mes_commandes(client: Annotated[Client, Depends(client_courant)], session: Session_):
    commandes = session.scalars(
        select(Commande)
        .where(Commande.client_id == client.id)
        .options(selectinload(Commande.lignes))
        .order_by(Commande.date_commande.desc(), Commande.id.desc())
    ).all()
    return list(commandes)

@routeur.post("/mot-de-passe-oublie")
def mot_de_passe_oublie(donnees: MotDePasseOublie, session: Session_):
    client = session.scalar(select(Client).where(Client.email == donnees.email.lower()))
    if client is not None and client.mot_de_passe_hash and client.email_verifie:
        jeton = creer_jeton_reset(client.id)
        lien = f"{parametres.url_frontend}/reinitialiser-mot-de-passe?token={jeton}"
        try:
            service_email.envoyer_reinitialisation_email(client.email, client.nom, lien)
        except Exception:
            pass
    return {"message": "Si un compte existe avec cet e-mail, un lien de reinitialisation a ete envoye."}


@routeur.post("/reinitialiser-mot-de-passe")
def reinitialiser_mot_de_passe(donnees: ReinitialisationMotDePasse, session: Session_):
    try:
        charge = decoder_jeton(donnees.token)
        if charge.get("type") != "reset_mdp":
            raise ValueError()
        client_id = int(charge.get("sub"))
    except Exception:
        raise HTTPException(status_code=400, detail="Lien de reinitialisation invalide ou expire.")

    client = session.get(Client, client_id)
    if client is None or not client.mot_de_passe_hash:
        raise HTTPException(status_code=400, detail="Lien de reinitialisation invalide.")
    client.mot_de_passe_hash = hacher_mot_de_passe(donnees.mot_de_passe)
    session.commit()
    return {"message": "Mot de passe reinitialise. Vous pouvez vous connecter."}