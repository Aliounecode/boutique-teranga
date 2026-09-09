from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Text, Boolean, ForeignKey, Numeric, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base
from app.modeles.enumerations import StatutProduit


class Produit(Base):
    __tablename__ = "produits"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    reference: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    categorie_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    prix: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)          # FCFA (montants entiers)
    prix_promo: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    en_promotion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    a_tailles: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # True pour les chaussures
    statut: Mapped[StatutProduit] = mapped_column(
        Enum(StatutProduit), default=StatutProduit.DISPONIBLE, nullable=False
    )
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)       # desactivation != suppression
    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())
    date_modification: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

    categorie: Mapped["Categorie"] = relationship(back_populates="produits")
    variantes: Mapped[list["VarianteProduit"]] = relationship(
        back_populates="produit", cascade="all, delete-orphan"
    )
    photos: Mapped[list["PhotoProduit"]] = relationship(
        back_populates="produit", cascade="all, delete-orphan", order_by="PhotoProduit.ordre"
    )
