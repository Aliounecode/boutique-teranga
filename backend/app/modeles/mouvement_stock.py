from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base
from app.modeles.enumerations import TypeMouvementStock


class MouvementStock(Base):
    """Journal append-only de tous les mouvements de stock (tracabilite)."""
    __tablename__ = "mouvements_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    variante_id: Mapped[int] = mapped_column(ForeignKey("variantes_produit.id"), nullable=False)
    type_mouvement: Mapped[TypeMouvementStock] = mapped_column(Enum(TypeMouvementStock), nullable=False)
    quantite: Mapped[int] = mapped_column(Integer, nullable=False)          # magnitude (valeur positive)
    quantite_avant: Mapped[int] = mapped_column(Integer, nullable=False)
    quantite_apres: Mapped[int] = mapped_column(Integer, nullable=False)
    motif: Mapped[str | None] = mapped_column(String(255))
    reference_document: Mapped[str | None] = mapped_column(String(60))      # ex : n° de vente / commande liee
    utilisateur_id: Mapped[int | None] = mapped_column(ForeignKey("utilisateurs.id"))
    date_mouvement: Mapped[datetime] = mapped_column(server_default=func.now())

    variante: Mapped["VarianteProduit"] = relationship(back_populates="mouvements_stock")
    utilisateur: Mapped["Utilisateur | None"] = relationship(back_populates="mouvements_stock")
