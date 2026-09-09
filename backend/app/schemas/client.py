"""
Schemas Pydantic des clients.
Chemin : backend/app/schemas/client.py
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ClientBase(BaseModel):
    nom: str = Field(min_length=1, max_length=100)
    prenom: str | None = Field(default=None, max_length=100)
    telephone: str | None = Field(default=None, max_length=30)


class ClientCreation(ClientBase):
    pass


class ClientMiseAJour(BaseModel):
    nom: str | None = Field(default=None, min_length=1, max_length=100)
    prenom: str | None = Field(default=None, max_length=100)
    telephone: str | None = Field(default=None, max_length=30)
    actif: bool | None = None


class ClientLecture(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actif: bool
    date_creation: datetime


class ClientDetail(ClientLecture):
    nombre_achats: int = 0
    total_depense: Decimal = Decimal("0")


class ClientPage(BaseModel):
    total: int
    page: int
    taille_page: int
    elements: list[ClientLecture]