"""
Schemas Pydantic des variantes de produit.
Chemin : backend/app/schemas/variante_produit.py
"""
from pydantic import BaseModel, ConfigDict, Field, computed_field


class VarianteBase(BaseModel):
    couleur: str | None = Field(default=None, max_length=50)
    taille: str | None = Field(default=None, max_length=20)
    quantite_disponible: int = Field(default=0, ge=0)
    stock_minimum: int = Field(default=0, ge=0)


class VarianteCreation(VarianteBase):
    """Donnees pour creer une variante (la reference est generee cote serveur)."""
    pass


class VarianteMiseAJour(BaseModel):
    """Mise a jour partielle : seuls les champs fournis sont modifies.

    Note : la quantite en stock ne se modifie PAS ici. Elle passe par les
    endpoints audites /stock/reapprovisionner et /stock/corriger, qui
    enregistrent un mouvement de stock (tracabilite).
    """
    couleur: str | None = Field(default=None, max_length=50)
    taille: str | None = Field(default=None, max_length=20)
    stock_minimum: int | None = Field(default=None, ge=0)
    actif: bool | None = None


class VarianteLecture(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    produit_id: int
    couleur: str | None
    taille: str | None
    reference_variante: str | None
    quantite_disponible: int
    stock_minimum: int
    actif: bool

    @computed_field
    @property
    def en_rupture(self) -> bool:
        return self.quantite_disponible <= 0

    @computed_field
    @property
    def stock_faible(self) -> bool:
        return 0 < self.quantite_disponible <= self.stock_minimum