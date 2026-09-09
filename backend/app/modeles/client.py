from datetime import datetime

from sqlalchemy import Boolean, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.base_donnees import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(100), nullable=False)
    prenom: Mapped[str | None] = mapped_column(String(100))
    telephone: Mapped[str | None] = mapped_column(String(30))
    actif: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    date_creation: Mapped[datetime] = mapped_column(server_default=func.now())

    # Compte en ligne (espace client). Nul pour un client cree en caisse par le gerant.
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    mot_de_passe_hash: Mapped[str | None] = mapped_column(String(255))
    email_verifie: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    ventes: Mapped[list["Vente"]] = relationship(back_populates="client")