import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';

import { AuthClientService } from '../../../coeur/services/auth-client';

@Component({
  selector: 'bq-verifier-email',
  imports: [RouterLink],
  template: `
    <section class="page-auth">
      <div class="carte">
        <p class="surtitre">Espace client</p>
        <h1 class="titre">Confirmation de l'e-mail</h1>
        <hr class="filet" />

        @switch (etat()) {
          @case ('chargement') {
            <p class="intro">Vérification en cours…</p>
          }
          @case ('succes') {
            <p class="intro">{{ message() }}</p>
            <a routerLink="/connexion" class="btn accent pleine">Se connecter</a>
          }
          @case ('erreur') {
            <div class="alerte">{{ message() }}</div>
            <p class="intro">
              Le lien est peut-être expiré. Vous pouvez en demander un nouveau depuis la page de
              connexion.
            </p>
            <a routerLink="/connexion" class="btn clair pleine">Retour à la connexion</a>
          }
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
        max-width: 460px;
        background: var(--surface);
        border: 1px solid var(--bordure);
        padding: 46px 42px;
        box-shadow: var(--ombre);
        text-align: center;
      }
      .titre {
        font-family: var(--serif);
        font-weight: 500;
        font-size: 2rem;
        margin-top: 6px;
      }
      .filet {
        margin: 18px auto 26px;
      }
      .intro {
        color: var(--texte-doux);
        margin-bottom: 24px;
      }
      .alerte {
        background: #fbeae6;
        border: 1px solid #e6b7ad;
        color: #8a3a2b;
        padding: 12px 15px;
        font-size: 0.9rem;
        margin-bottom: 18px;
      }
      .btn.pleine {
        width: 100%;
        justify-content: center;
      }
    `,
  ],
})
export class VerifierEmail {
  private readonly route = inject(ActivatedRoute);
  private readonly auth = inject(AuthClientService);

  protected readonly etat = signal<'chargement' | 'succes' | 'erreur'>('chargement');
  protected readonly message = signal('');

  constructor() {
    const token = this.route.snapshot.queryParamMap.get('token');
    if (!token) {
      this.etat.set('erreur');
      this.message.set('Lien de vérification invalide.');
      return;
    }
    this.auth.verifierEmail(token).subscribe({
      next: (r) => {
        this.etat.set('succes');
        this.message.set(r.message);
      },
      error: (e) => {
        this.etat.set('erreur');
        this.message.set(e?.error?.detail ?? 'Lien de vérification invalide ou expiré.');
      },
    });
  }
}
