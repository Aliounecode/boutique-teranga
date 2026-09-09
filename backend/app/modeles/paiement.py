"""
Modele Paiement : enregistrement du moyen de paiement (especes, Wave, OM...), sans passerelle.

Chemin : backend/app/modeles/paiement.py
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base
from app.modeles.enumerations import MoyenPaiement


class Paiement(Base):
    __tablename__ = "paiements"

    id: Mapped[int] = mapped_column(primary_key=True)
    vente_id: Mapped[int | None] = mapped_column(ForeignKey("ventes.id"))  # (commande_id ajoute plus tard)
    montant: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    moyen: Mapped[MoyenPaiement] = mapped_column(Enum(MoyenPaiement), nullable=False)
    utilisateur_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateurs.id"))
    reference_externe: Mapped[str | None] = mapped_column(String(100))  # ex : id de transaction Wave
    date_paiement: Mapped[datetime] = mapped_column(server_default=func.now())

    vente: Mapped["Vente | None"] = relationship(back_populates="paiements")