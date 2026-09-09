"""
Schemas Pydantic d'authentification.
Chemin : backend/app/schemas/auth.py
"""
from pydantic import BaseModel


class Jeton(BaseModel):
    access_token: str
    token_type: str = "bearer"