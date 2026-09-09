import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';

import { AuthClientService } from '../../../coeur/services/auth-client';

@Component({
  selector: 'bq-connexion-client',
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <section class="page-auth">
      <div class="carte">
        <p class="surtitre">Espace client</p>
        <h1 class="titre">Connexion</h1>
        <hr class="filet" />

        @if (erreur()) {
          <div class="alerte">
            {{ erreur() }}
            @if (nonVerifie()) {
              <button type="button" class="lien-renvoi" (click)="renvoyer()" [disabled]="enCours()">
                Renvoyer l'e-mail de confirmation
              </button>
            }
          </div>
        }
        @if (info()) {
          <div class="info">{{ info() }}</div>
        }

        <form [formGroup]="form" (ngSubmit)="soumettre()">
          <label>
            <span>E-mail</span>
            <input type="email" formControlName="email" autocomplete="email" />
          </label>
          <label>
            <span>Mot de passe</span>
            <input type="password" formControlName="mot_de_passe" autocomplete="current-password" />
          </label>
          <button type="submit" class="btn accent pleine" [disabled]="enCours()">
            {{ enCours() ? 'Connexion…' : 'Se connecter' }}
          </button>
        </form>
        <p class="oublie"><a routerLink="/mot-de-passe-oublie">Mot de passe oublié ?</a></p>
        <p class="bas">Pas encore de compte ? <a routerLink="/inscription">Créer un compte</a></p>
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
        font-size: 2.1rem;
        margin-top: 6px;
      }
      form {
        display: grid;
        gap: 18px;
        margin-top: 26px;
      }
      .oublie {
        text-align: center;
        margin-top: 16px;
        font-size: 0.85rem;
      }
      .oublie a {
        color: var(--texte-doux);
        text-decoration: underline;
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
      .btn.pleine {
        width: 100%;
        justify-content: center;
        margin-top: 4px;
      }
      .alerte {
        background: #fbeae6;
        border: 1px solid #e6b7ad;
        color: #8a3a2b;
        padding: 12px 15px;
        font-size: 0.85rem;
        display: grid;
        gap: 8px;
      }
      .info {
        background: #eef4ec;
        border: 1px solid #bcd6b6;
        color: #40663a;
        padding: 12px 15px;
        font-size: 0.85rem;
      }
      .lien-renvoi {
        justify-self: start;
        background: none;
        border: none;
        color: #8a3a2b;
        text-decoration: underline;
        cursor: pointer;
        font-size: 0.82rem;
        padding: 0;
      }
      .bas {
        text-align: center;
        margin-top: 24px;
        font-size: 0.9rem;
        color: var(--texte-doux);
      }
      .bas a {
        color: var(--accent);
      }
      @media (max-width: 520px) {
        .carte {
          padding: 36px 24px;
        }
      }
    `,
  ],
})
export class ConnexionClient {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthClientService);
  private readonly router = inject(Router);

  protected readonly enCours = signal(false);
  protected readonly erreur = signal<string | null>(null);
  protected readonly info = signal<string | null>(null);
  protected readonly nonVerifie = signal(false);

  protected readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    mot_de_passe: ['', [Validators.required]],
  });

  soumettre(): void {
    if (this.form.invalid || this.enCours()) {
      this.form.markAllAsTouched();
      return;
    }
    this.enCours.set(true);
    this.erreur.set(null);
    this.info.set(null);
    this.nonVerifie.set(false);
    const { email, mot_de_passe } = this.form.getRawValue();
    this.auth.connexion(email, mot_de_passe).subscribe({
      next: () => {
        this.enCours.set(false);
        this.router.navigateByUrl('/mon-compte');
      },
      error: (e) => {
        this.enCours.set(false);
        const detail: string = e?.error?.detail ?? 'Connexion impossible. Réessayez.';
        this.erreur.set(detail);
        this.nonVerifie.set(detail.toLowerCase().includes('confirmer'));
      },
    });
  }

  renvoyer(): void {
    const email = this.form.getRawValue().email;
    if (!email) return;
    this.enCours.set(true);
    this.auth.renvoyerVerification(email).subscribe({
      next: (r) => {
        this.enCours.set(false);
        this.erreur.set(null);
        this.nonVerifie.set(false);
        this.info.set(r.message);
      },
      error: () => this.enCours.set(false),
    });
  }
}
