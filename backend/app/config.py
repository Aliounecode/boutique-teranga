from pydantic_settings import BaseSettings, SettingsConfigDict


class Parametres(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    url_base_donnees: str
    cle_secrete_jwt: str
    algorithme_jwt: str = "HS256"
    duree_token_minutes: int = 1440
    mode_debug: bool = False

    # Cloudinary — photos produits
    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None

    # Identite de la boutique (en-tete des rapports et factures PDF)
    nom_boutique: str = "Ma Boutique"
    adresse_boutique: str | None = None
    telephone_boutique: str | None = None

    # Brevo — envoi d'e-mails transactionnels
    brevo_api_key: str | None = None
    email_expediteur: str = "no-reply@exemple.com"   # doit etre un expediteur VERIFIE dans Brevo
    nom_expediteur: str = "Ma Boutique"

    # URL publique du frontend (pour les liens de verification d'e-mail)
    url_frontend: str = "http://localhost:4200"
    origines_cors: str = "http://localhost:4200"
    @property
    def liste_origines(self) -> list[str]:
        return [o.strip() for o in self.origines_cors.split(",") if o.strip()]



parametres = Parametres()