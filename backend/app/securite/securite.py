"""
Securite : hachage des mots de passe (bcrypt) et jetons JWT.
Chemin : backend/app/securite/securite.py
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import parametres

LIMITE_OCTETS = 72


def _en_octets(mot_de_passe: str) -> bytes:
    return mot_de_passe.encode("utf-8")[:LIMITE_OCTETS]


def hacher_mot_de_passe(mot_de_passe: str) -> str:
    hache = bcrypt.hashpw(_en_octets(mot_de_passe), bcrypt.gensalt())
    return hache.decode("utf-8")


def verifier_mot_de_passe(mot_de_passe: str, hache: str) -> bool:
    try:
        return bcrypt.checkpw(_en_octets(mot_de_passe), hache.encode("utf-8"))
    except ValueError:
        return False


def _creer_jeton(donnees: dict, duree_minutes: int) -> str:
    a_encoder = donnees.copy()
    a_encoder["exp"] = datetime.now(timezone.utc) + timedelta(minutes=duree_minutes)
    return jwt.encode(a_encoder, parametres.cle_secrete_jwt, algorithm=parametres.algorithme_jwt)


def creer_jeton_acces(donnees: dict) -> str:
    """Jeton d'acces gerant/vendeur (utilise par /auth/connexion)."""
    return _creer_jeton(donnees, parametres.duree_token_minutes)


def creer_jeton_client(client_id: int) -> str:
    """Jeton d'acces d'un client de la boutique."""
    return _creer_jeton({"sub": str(client_id), "type": "client"}, parametres.duree_token_minutes)


def creer_jeton_verification(client_id: int) -> str:
    """Jeton de verification d'e-mail (valable 24 h)."""
    return _creer_jeton({"sub": str(client_id), "type": "verif_email"}, 60 * 24)


def creer_jeton_reset(client_id: int) -> str:
    """Jeton de reinitialisation de mot de passe (valable 1 h)."""
    return _creer_jeton({"sub": str(client_id), "type": "reset_mdp"}, 60)

def decoder_jeton(jeton: str) -> dict:
    return jwt.decode(jeton, parametres.cle_secrete_jwt, algorithms=[parametres.algorithme_jwt])