import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';

import { AuthClientService } from '../../../coeur/services/auth-client';

@Component({
  selector: 'bq-mot-de-passe-oublie',
  imports: [ReactiveFormsModule, RouterLink],
  template: `
    <section class="page-auth">
      <div class="carte">
        <p class="surtitre">Espace client</p>
        <h1 class="titre">Mot de passe oublié</h1>
        <hr class="filet" />

        @if (envoye()) {
          <p class="intro">{{ message() }}</p>
          <a routerLink="/connexion" class="btn clair pleine">Retour à la connexion</a>
        } @else {
          <p class="intro">
            Indiquez votre e-mail : nous vous enverrons un lien pour choisir un nouveau mot de
            passe.
          </p>
          <form [formGroup]="form" (ngSubmit)="soumettre()">
            <label>
              <span>E-mail</span>
              <input type="email" formControlName="email" autocomplete="email" />
            </label>
            <button type="submit" class="btn accent pleine" [disabled]="enCours()">
              {{ enCours() ? 'Envoi…' : 'Envoyer le lien' }}
            </button>
          </form>
          <p class="bas"><a routerLink="/connexion">Retour à la connexion</a></p>
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
      }
      .bas {
        text-align: center;
        margin-top: 22px;
        font-size: 0.88rem;
      }
      .bas a {
        color: var(--texte-doux);
        text-decoration: underline;
      }
    `,
  ],
})
export class MotDePasseOublie {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthClientService);

  protected readonly enCours = signal(false);
  protected readonly envoye = signal(false);
  protected readonly message = signal('');

  protected readonly form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
  });

  soumettre(): void {
    if (this.form.invalid || this.enCours()) {
      this.form.markAllAsTouched();
      return;
    }
    this.enCours.set(true);
    this.auth.motDePasseOublie(this.form.getRawValue().email).subscribe({
      next: (r) => {
        this.enCours.set(false);
        this.message.set(r.message);
        this.envoye.set(true);
      },
      error: () => {
        this.enCours.set(false);
        this.message.set(
          'Si un compte existe avec cet e-mail, un lien de réinitialisation a été envoyé.',
        );
        this.envoye.set(true);
      },
    });
  }
}
