import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { AuthClientService } from '../../../coeur/services/auth-client';

@Component({
  selector: 'bq-reinitialiser-mot-de-passe',
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <section class="page-auth">
      <div class="carte">
        <p class="surtitre">Espace client</p>
        <h1 class="titre">Nouveau mot de passe</h1>
        <hr class="filet" />

        @if (!token) {
          <div class="alerte">Lien de réinitialisation invalide.</div>
          <a routerLink="/mot-de-passe-oublie" class="btn clair pleine">Demander un nouveau lien</a>
        } @else if (succes()) {
          <p class="intro">{{ message() }}</p>
          <a routerLink="/connexion" class="btn accent pleine">Se connecter</a>
        } @else {
          @if (erreur()) {
            <div class="alerte">{{ erreur() }}</div>
          }
          <form [formGroup]="form" (ngSubmit)="soumettre()">
            <label>
              <span>Nouveau mot de passe</span>
              <div class="champ-mdp">
                <input
                  [type]="afficherMdp() ? 'text' : 'password'"
                  formControlName="mot_de_passe"
                  autocomplete="new-password"
                />
                <button
                  type="button"
                  class="oeil"
                  (click)="afficherMdp.set(!afficherMdp())"
                  [attr.aria-label]="
                    afficherMdp() ? 'Masquer le mot de passe' : 'Afficher le mot de passe'
                  "
                >
                  @if (afficherMdp()) {
                    <svg
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.4"
                    >
                      <path d="M3 3l18 18" />
                      <path d="M10.6 10.6a2 2 0 002.8 2.8" />
                      <path
                        d="M9.9 4.2A9.5 9.5 0 0112 4c5 0 9 4.5 10 8-.4 1.2-1.1 2.4-2 3.4M6.1 6.1C4 7.4 2.6 9.4 2 12c1 3.5 5 8 10 8 1.5 0 2.9-.3 4.1-.9"
                      />
                    </svg>
                  } @else {
                    <svg
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.4"
                    >
                      <path d="M2 12s3.5-8 10-8 10 8 10 8-3.5 8-10 8-10-8-10-8z" />
                      <circle cx="12" cy="12" r="3" />
                    </svg>
                  }
                </button>
              </div>
              <small>6 caractères minimum.</small>
            </label>
            <button type="submit" class="btn accent pleine" [disabled]="enCours()">
              {{ enCours() ? 'Enregistrement…' : 'Valider le nouveau mot de passe' }}
            </button>
          </form>
        }
      </div>
    </section>
  `,
  styles: [
    `
      .page-auth {
        display: grid;
        place-items: center;
        padding: 70px 20px;
        min-height: 70vh;
      }
      .carte {
        width: 100%;
        max-width: 420px;
        background: var(--surface);
        border: 1px solid var(--bordure);
        padding: 46px 42px;
        box-shadow: var(--ombre);
      }
      .titre {
        font-family: var(--serif);
        font-weight: 500;
        font-size: 2rem;
        margin-top: 6px;
      }
      .intro {
        color: var(--texte-doux);
        margin: 22px 0 26px;
      }
      form {
        display: grid;
        gap: 18px;
        margin-top: 8px;
      }
      label {
        display: grid;
        gap: 7px;
      }
      label span {
        font-size: 0.72rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--texte-doux);
      }
      input {
        font-family: var(--sans);
        font-size: 0.95rem;
        padding: 12px 14px;
        border: 1px solid var(--bordure);
        background: var(--fond);
        color: var(--texte);
        transition: border-color var(--transi);
      }
      input:focus {
        outline: none;
        border-color: var(--accent);
      }
      small {
        font-size: 0.72rem;
        color: var(--texte-doux);
      }
      .champ-mdp {
        position: relative;
      }
      .champ-mdp input {
        width: 100%;
        padding-right: 46px;
      }
      .oeil {
        position: absolute;
        right: 8px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        padding: 6px;
        cursor: pointer;
        color: var(--texte-doux);
        display: inline-flex;
        transition: color var(--transi);
      }
      .oeil:hover {
        color: var(--accent);
      }
      .btn.pleine {
        width: 100%;
        justify-content: center;
      }
      .alerte {
        background: #fbeae6;
        border: 1px solid #e6b7ad;
        color: #8a3a2b;
        padding: 12px 15px;
        font-size: 0.9rem;
        margin-bottom: 16px;
      }
    `,
  ],
})
export class ReinitialiserMotDePasse {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthClientService);
  private readonly route = inject(ActivatedRoute);

  protected readonly token = this.route.snapshot.queryParamMap.get('token');
  protected readonly enCours = signal(false);
  protected readonly succes = signal(false);
  protected readonly erreur = signal<string | null>(null);
  protected readonly message = signal('');
  protected readonly afficherMdp = signal(false);

  protected readonly form = this.fb.nonNullable.group({
    mot_de_passe: ['', [Validators.required, Validators.minLength(6)]],
  });

  soumettre(): void {
    if (!this.token || this.form.invalid || this.enCours()) {
      this.form.markAllAsTouched();
      return;
    }
    this.enCours.set(true);
    this.erreur.set(null);
    this.auth.reinitialiser(this.token, this.form.getRawValue().mot_de_passe).subscribe({
      next: (r) => {
        this.enCours.set(false);
        this.message.set(r.message);
        this.succes.set(true);
      },
      error: (e) => {
        this.enCours.set(false);
        this.erreur.set(e?.error?.detail ?? 'Lien invalide ou expiré. Demandez-en un nouveau.');
      },
    });
  }
}
