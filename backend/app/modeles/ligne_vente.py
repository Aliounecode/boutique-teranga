"""
Modele LigneVente : detail des variantes vendues dans une vente physique.

Chemin : backend/app/modeles/ligne_vente.py
"""

from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class LigneVente(Base):
    __tablename__ = "lignes_vente"

    id: Mapped[int] = mapped_column(primary_key=True)
    vente_id: Mapped[int] = mapped_column(ForeignKey("ventes.id"), nullable=False)
    variante_id: Mapped[int] = mapped_column(ForeignKey("variantes_produit.id"), nullable=False)
    # Instantanes au moment de la vente (ne changent pas si le produit evolue) :
    produit_nom: Mapped[str] = mapped_column(String(200), nullable=False)
    couleur: Mapped[str | None] = mapped_column(String(50))
    taille: Mapped[str | None] = mapped_column(String(20))
    prix_unitaire: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    quantite: Mapped[int] = mapped_column(Integer, nullable=False)
    sous_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    vente: Mapped["Vente"] = relationship(back_populates="lignes")
    variante: Mapped["VarianteProduit"] = relationship()  # sens unique