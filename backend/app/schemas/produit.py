"""
Schemas Pydantic des produits.
Chemin : backend/app/schemas/produit.py
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.modeles.enumerations import StatutProduit
from app.schemas.categorie import CategorieLecture
from app.schemas.photo_produit import PhotoLecture
from app.schemas.variante_produit import VarianteCreation, VarianteLecture


class ProduitBase(BaseModel):
    nom: str = Field(min_length=1, max_length=200)
    description: str | None = None
    categorie_id: int
    prix: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    prix_promo: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    en_promotion: bool = False
    a_tailles: bool = False
    statut: StatutProduit = StatutProduit.DISPONIBLE


class ProduitCreation(ProduitBase):
    reference: str | None = Field(default=None, max_length=50)
    variantes: list[VarianteCreation] = Field(min_length=1)


class ProduitMiseAJour(BaseModel):
    """Mise a jour partielle du produit (les variantes ont leurs propres endpoints)."""
    nom: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    categorie_id: int | None = None
    prix: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    prix_promo: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    en_promotion: bool | None = None
    a_tailles: bool | None = None
    statut: StatutProduit | None = None
    actif: bool | None = None


class ProduitResume(BaseModel):
    """Vue allegee pour les listes et les cartes produit de la boutique."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    nom: str
    categorie_id: int
    prix: Decimal
    prix_promo: Decimal | None
    en_promotion: bool
    statut: StatutProduit
    actif: bool
    photo_principale: str | None = None
    quantite_totale: int = 0

    @computed_field
    @property
    def prix_effectif(self) -> Decimal:
        if self.en_promotion and self.prix_promo is not None:
            return self.prix_promo
        return self.prix

    @computed_field
    @property
    def en_rupture(self) -> bool:
        return self.quantite_totale <= 0

    @computed_field
    @property
    def disponible_achat(self) -> bool:
        return self.actif and self.statut == StatutProduit.DISPONIBLE and self.quantite_totale > 0


class ProduitLecture(ProduitBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reference: str
    actif: bool
    date_creation: datetime
    date_modification: datetime
    categorie: CategorieLecture
    variantes: list[VarianteLecture] = []
    photos: list[PhotoLecture] = []

    @computed_field
    @property
    def prix_effectif(self) -> Decimal:
        if self.en_promotion and self.prix_promo is not None:
            return self.prix_promo
        return self.prix

    @computed_field
    @property
    def quantite_totale(self) -> int:
        return sum(v.quantite_disponible for v in self.variantes if v.actif)

    @computed_field
    @property
    def en_rupture(self) -> bool:
        return self.quantite_totale <= 0

    @computed_field
    @property
    def disponible_achat(self) -> bool:
        return self.actif and self.statut == StatutProduit.DISPONIBLE and self.quantite_totale > 0


class ProduitPage(BaseModel):
    total: int
    page: int
    taille_page: int
    elements: list[ProduitResume]