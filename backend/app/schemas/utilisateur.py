"""
Schemas Pydantic de l'utilisateur.
Chemin : backend/app/schemas/utilisateur.py
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.role import RoleLecture


class UtilisateurBase(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    prenom: str = Field(min_length=1, max_length=100)
    nom_utilisateur: str = Field(min_length=3, max_length=50)
    email: EmailStr | None = None
    telephone: str | None = Field(default=None, max_length=30)


class UtilisateurCreation(UtilisateurBase):
    mot_de_passe: str = Field(min_length=6, max_length=72)
    role_id: int


class UtilisateurLecture(UtilisateurBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actif: bool
    role: RoleLecture
    date_creation: datetime

class UtilisateurMiseAJour(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenom: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    telephone: str | None = Field(default=None, max_length=30)
    role_id: int | None = None
    actif: bool | None = None


class MotDePasseMaj(BaseModel):
    mot_de_passe: str = Field(min_length=6, max_length=72)