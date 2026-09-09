"""
Modele Vente : ventes physiques enregistrees en caisse (POS).

Chemin : backend/app/modeles/vente.py
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base
from app.modeles.enumerations import StatutVente


class Vente(Base):
    __tablename__ = "ventes"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)   # ex : V-000123
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"))        # null = vente anonyme
    utilisateur_id: Mapped[int] = mapped_column(ForeignKey("utilisateurs.id"), nullable=False)  # vendeur/gerant
    montant_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    statut: Mapped[StatutVente] = mapped_column(Enum(StatutVente), default=StatutVente.VALIDEE, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255))
    date_vente: Mapped[datetime] = mapped_column(server_default=func.now())

    client: Mapped["Client | None"] = relationship(back_populates="ventes")
    utilisateur: Mapped["Utilisateur"] = relationship()  # sens unique (pas de back_populates)
    lignes: Mapped[list["LigneVente"]] = relationship(
        back_populates="vente", cascade="all, delete-orphan"
    )
    paiements: Mapped[list["Paiement"]] = relationship(
        back_populates="vente", cascade="all, delete-orphan"
    )

