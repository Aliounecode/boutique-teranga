"""
Schemas Pydantic des paiements.
Chemin : backend/app/schemas/paiement.py
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.modeles.enumerations import MoyenPaiement


class PaiementLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    montant: Decimal
    moyen: MoyenPaiement
    reference_externe: str | None
    date_paiement: datetime
    utilisateur_id: int | None