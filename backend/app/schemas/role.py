"""
Schemas Pydantic du role.
Chemin : backend/app/schemas/role.py
"""
from pydantic import BaseModel, ConfigDict


class RoleLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nom: str
    description: str | None = None