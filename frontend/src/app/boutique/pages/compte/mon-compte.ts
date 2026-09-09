import { DatePipe } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';

import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import { AuthClientService } from '../../../coeur/services/auth-client';
import { CommandeLecture, LIBELLES_COMMANDE } from '../../../coeur/modeles/modeles';

@Component({
  selector: 'bq-mon-compte',
  imports: [RouterLink, DatePipe, FcfaPipe],
  template: `
    <section class="conteneur bloc">
      <div class="entete">
        <div>
          <p class="surtitre">Espace client</p>
          <h1 class="titre">Bonjour {{ auth.client()?.prenom || auth.client()?.nom }}</h1>
          <p class="mail">{{ auth.client()?.email }}</p>
        </div>
        <button type="button" class="btn clair" (click)="seDeconnecter()">Se déconnecter</button>
      </div>
      <hr class="filet" />

      <h2 class="sous-titre">Mes commandes</h2>

      @if (chargement()) {
        <p class="vide">Chargement…</p>
      } @else if (commandes().length === 0) {
        <div class="vide-carte">
          <p>Vous n'avez pas encore passé de commande.</p>
          <a routerLink="/catalogue" class="btn accent">Découvrir la boutique</a>
        </div>
      } @else {
        <div class="liste">
          @for (cmd of commandes(); track cmd.id) {
            <article class="commande">
              <div class="tete">
                <div>
                  <span class="num">{{ cmd.numero }}</span>
                  <span class="date">{{ cmd.date_commande | date: 'dd/MM/yyyy' }}</span>
                </div>
                <span class="badge" [attr.data-statut]="cmd.statut">{{ libelle(cmd.statut) }}</span>
              </div>
              <ul class="articles">
                @for (ligne of cmd.lignes; track ligne.id) {
                  <li>
                    <span
                      >{{ ligne.quantite }} × {{ ligne.produit_nom }}
                      @if (detailVariante(ligne)) {
                        <em>({{ detailVariante(ligne) }})</em>
                      }
                    </span>
                    <span>{{ ligne.sous_total | fcfa }}</span>
                  </li>
                }
              </ul>
              <div class="pied">
                <span>Total</span>
                <strong>{{ cmd.montant_total | fcfa }}</strong>
              </div>
            </article>
          }
        </div>
      }
    </section>
  `,
  styles: [
    `
      .bloc {
        padding: 60px 28px 90px;
      }
      .entete {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 20px;
        flex-wrap: wrap;
      }
      .titre {
        font-family: var(--serif);
        font-weight: 500;
        font-size: 2.4rem;
        margin-top: 6px;
      }
      .mail {
        color: var(--texte-doux);
        margin-top: 4px;
      }
      .sous-titre {
        font-family: var(--serif);
        font-weight: 500;
        font-size: 1.5rem;
        margin: 12px 0 24px;
      }
      .vide {
        color: var(--texte-doux);
      }
      .vide-carte {
        background: var(--surface);
        border: 1px solid var(--bordure);
        padding: 44px;
        text-align: center;
        display: grid;
        gap: 20px;
        justify-items: center;
        color: var(--texte-doux);
      }
      .liste {
        display: grid;
        gap: 20px;
      }
      .commande {
        background: var(--surface);
        border: 1px solid var(--bordure);
        padding: 24px 26px;
      }
      .tete {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding-bottom: 14px;
        border-bottom: 1px solid var(--bordure);
      }
      .num {
        font-weight: 500;
        letter-spacing: 0.04em;
      }
      .date {
        color: var(--texte-doux);
        margin-left: 14px;
        font-size: 0.85rem;
      }
      .badge {
        font-size: 0.68rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 5px 12px;
        border-radius: 20px;
        background: var(--surface-2);
        color: var(--texte-doux);
      }
      .badge[data-statut='validee'] {
        background: #e7f1e3;
        color: #40663a;
      }
      .badge[data-statut='nouvelle'] {
        background: #eef0f6;
        color: #4a5578;
      }
      .badge[data-statut='refusee'],
      .badge[data-statut='annulee'] {
        background: #fbeae6;
        color: #8a3a2b;
      }
      .articles {
        list-style: none;
        margin: 14px 0;
        display: grid;
        gap: 8px;
      }
      .articles li {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        font-size: 0.9rem;
      }
      .articles em {
        color: var(--texte-doux);
        font-style: normal;
      }
      .pied {
        display: flex;
        justify-content: space-between;
        padding-top: 14px;
        border-top: 1px solid var(--bordure);
      }
      .pied strong {
        font-family: var(--serif);
        font-size: 1.25rem;
      }
      @media (max-width: 520px) {
        .titre {
          font-size: 1.9rem;
        }
      }
    `,
  ],
})
export class MonCompte {
  protected readonly auth = inject(AuthClientService);
  private readonly router = inject(Router);

  protected readonly commandes = signal<CommandeLecture[]>([]);
  protected readonly chargement = signal(true);

  constructor() {
    if (!this.auth.client()) {
      this.auth.chargerProfil().subscribe();
    }
    this.auth.mesCommandes().subscribe({
      next: (liste) => {
        this.commandes.set(liste);
        this.chargement.set(false);
      },
      error: () => this.chargement.set(false),
    });
  }

  protected libelle(statut: CommandeLecture['statut']): string {
    return LIBELLES_COMMANDE[statut];
  }

  protected detailVariante(ligne: { couleur: string | null; taille: string | null }): string {
    return [ligne.couleur, ligne.taille].filter((x) => !!x).join(' / ');
  }

  seDeconnecter(): void {
    this.auth.deconnexion();
    this.router.navigateByUrl('/');
  }
}
