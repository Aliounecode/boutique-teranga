from sqlalchemy import String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class PhotoProduit(Base):
    __tablename__ = "photos_produit"

    id: Mapped[int] = mapped_column(primary_key=True)
    produit_id: Mapped[int] = mapped_column(ForeignKey("produits.id"), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)          # URL publique (Cloudinary)
    public_id: Mapped[str | None] = mapped_column(String(255))            # identifiant Cloudinary (pour suppression)
    ordre: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # ordre dans la galerie
    est_principale: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    produit: Mapped["Produit"] = relationship(back_populates="photos")
