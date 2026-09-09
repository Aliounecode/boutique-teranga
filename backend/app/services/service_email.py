"""
Envoi d'e-mails transactionnels via Brevo.
Chemin : backend/app/services/service_email.py
"""
import httpx

from app.config import parametres

API_BREVO = "https://api.brevo.com/v3/smtp/email"


def est_configure() -> bool:
    return bool(parametres.brevo_api_key)


def envoyer_email(destinataire_email: str, destinataire_nom: str, sujet: str, contenu_html: str) -> None:
    """Envoie un e-mail via Brevo. Leve une erreur si non configure ou si Brevo refuse."""
    if not est_configure():
        raise RuntimeError("Service d'e-mail non configure (BREVO_API_KEY manquante).")
    reponse = httpx.post(
        API_BREVO,
        headers={
            "api-key": parametres.brevo_api_key,
            "accept": "application/json",
            "content-type": "application/json",
        },
        json={
            "sender": {"email": parametres.email_expediteur, "name": parametres.nom_expediteur},
            "to": [{"email": destinataire_email, "name": destinataire_nom}],
            "subject": sujet,
            "htmlContent": contenu_html,
        },
        timeout=15.0,
    )
    reponse.raise_for_status()  # 201/202 = succes ; 4xx/5xx leve une exception


def envoyer_verification_email(destinataire_email: str, destinataire_nom: str, lien: str) -> None:
    contenu = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; color: #2B2320;">
      <h2 style="font-family: Georgia, serif; color:#2B2320;">Bienvenue chez {parametres.nom_expediteur}</h2>
      <p>Bonjour {destinataire_nom},</p>
      <p>Merci de votre inscription. Cliquez sur le bouton ci-dessous pour confirmer votre adresse e-mail :</p>
      <p style="text-align:center; margin: 28px 0;">
        <a href="{lien}" style="background:#B76E5B; color:#fff; padding:13px 26px; text-decoration:none; letter-spacing:0.05em; border-radius:2px;">Confirmer mon e-mail</a>
      </p>
      <p style="font-size: 13px; color:#6E6058;">Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>{lien}</p>
      <p style="font-size: 13px; color:#6E6058;">Ce lien expire dans 24 heures. Si vous n'etes pas a l'origine de cette inscription, ignorez cet e-mail.</p>
    </div>
    """
    envoyer_email(destinataire_email, destinataire_nom, f"Confirmez votre e-mail — {parametres.nom_expediteur}", contenu)

def envoyer_reinitialisation_email(destinataire_email: str, destinataire_nom: str, lien: str) -> None:
    contenu = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; color: #2B2320;">
      <h2 style="font-family: Georgia, serif; color:#2B2320;">Reinitialisation du mot de passe</h2>
      <p>Bonjour {destinataire_nom},</p>
      <p>Vous avez demande a reinitialiser votre mot de passe. Cliquez sur le bouton ci-dessous :</p>
      <p style="text-align:center; margin: 28px 0;">
        <a href="{lien}" style="background:#B76E5B; color:#fff; padding:13px 26px; text-decoration:none; letter-spacing:0.05em; border-radius:2px;">Choisir un nouveau mot de passe</a>
      </p>
      <p style="font-size: 13px; color:#6E6058;">Si le bouton ne fonctionne pas, copiez ce lien :<br>{lien}</p>
      <p style="font-size: 13px; color:#6E6058;">Ce lien expire dans 1 heure. Si vous n'etes pas a l'origine de cette demande, ignorez cet e-mail : votre mot de passe reste inchange.</p>
    </div>
    """
    envoyer_email(destinataire_email, destinataire_nom, f"Reinitialisation du mot de passe — {parametres.nom_expediteur}", contenu)