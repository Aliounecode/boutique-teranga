from datetime import datetime

from sqlalchemy import String, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class Categorie(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"))  # sous-categorie eventuelle
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())

    # Hierarchie : "Sacs" (racine) -> "Sacs a main" (enfant)
    parent: Mapped["Categorie | None"] = relationship(
        remote_side=[id], back_populates="sous_categories"
    )
    sous_categories: Mapped[list["Categorie"]] = relationship(back_populates="parent")
    produits: Mapped[list["Produit"]] = relationship(back_populates="categorie")
