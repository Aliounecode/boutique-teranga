"""
Modele Commande : commandes passees depuis la boutique en ligne (numero, statut, total, client).

Chemin : backend/app/modeles/commande.py
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base
from app.modeles.enumerations import MoyenPaiement, StatutCommande


class Commande(Base):
    __tablename__ = "commandes"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)   # ex : CMD-000123
    # Coordonnees du client saisies a la commande (achat sans compte) :
    client_nom: Mapped[str] = mapped_column(String(100), nullable=False)
    client_prenom: Mapped[str | None] = mapped_column(String(100))
    client_telephone: Mapped[str] = mapped_column(String(30), nullable=False)
    moyen_paiement: Mapped[MoyenPaiement] = mapped_column(Enum(MoyenPaiement), nullable=False)
    montant_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    statut: Mapped[StatutCommande] = mapped_column(
        Enum(StatutCommande), default=StatutCommande.NOUVELLE, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(String(255))
    utilisateur_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateurs.id"))  # gerant ayant traite
    client_id: Mapped[int | None] = mapped_column(ForeignKey("clients.id"))  # compte client si connecte

    date_commande: Mapped[datetime] = mapped_column(server_default=func.now())

    lignes: Mapped[list["LigneCommande"]] = relationship(
        back_populates="commande", cascade="all, delete-orphan"
    )