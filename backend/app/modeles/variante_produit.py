from sqlalchemy import String, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class VarianteProduit(Base):
    __tablename__ = "variantes_produit"
    __table_args__ = (
        UniqueConstraint("produit_id", "couleur", "taille", name="uq_variante_produit"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    produit_id: Mapped[int] = mapped_column(ForeignKey("produits.id"), nullable=False)
    couleur: Mapped[str | None] = mapped_column(String(50))
    taille: Mapped[str | None] = mapped_column(String(20))                 # pointure pour les chaussures
    reference_variante: Mapped[str | None] = mapped_column(String(60), unique=True)
    quantite_disponible: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # SOURCE DE VERITE du stock
    stock_minimum: Mapped[int] = mapped_column(Integer, default=0, nullable=False)        # seuil d'alerte
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    produit: Mapped["Produit"] = relationship(back_populates="variantes")
    mouvements_stock: Mapped[list["MouvementStock"]] = relationship(back_populates="variante")
