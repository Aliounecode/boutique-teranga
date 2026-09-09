"""
Schemas Pydantic de l'espace client (inscription, connexion, verification).
Chemin : backend/app/schemas/compte_client.py
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InscriptionClient(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    prenom: str | None = Field(default=None, max_length=100)
    telephone: str | None = Field(default=None, max_length=30)
    email: EmailStr
    mot_de_passe: str = Field(min_length=6, max_length=72)


class ConnexionClient(BaseModel):
    email: EmailStr
    mot_de_passe: str


class VerificationEmail(BaseModel):
    token: str


class RenvoiVerification(BaseModel):
    email: EmailStr

class MotDePasseOublie(BaseModel):
    email: EmailStr


class ReinitialisationMotDePasse(BaseModel):
    token: str
    mot_de_passe: str = Field(min_length=6, max_length=72)

class JetonClient(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ClientCompteLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    prenom: str | None
    telephone: str | None
    email: str | None
    email_verifie: bool
    date_creation: datetime