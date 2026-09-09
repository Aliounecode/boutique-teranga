import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { PanierService } from '../../../coeur/services/panier';
import { AuthClientService } from '../../../coeur/services/auth-client';

@Component({
  selector: 'bq-entete',
  imports: [RouterLink],
  template: `
    <div class="annonce">
      Livraison à Dakar<span class="sep">·</span>Paiement Wave &amp; Orange Money<span
        class="sep masque"
        >·</span
      ><span class="masque">Retours sous 7 jours</span>
    </div>
    <header>
      <div class="conteneur barre">
        <a routerLink="/" class="logo">PAPE ALE ET BAMBA<span class="point">.</span></a>
        <nav class="principale">
          <a routerLink="/catalogue">Sacs</a>
          <a routerLink="/catalogue">Chaussures</a>
          <a routerLink="/catalogue">Nouveautés</a>
          <a routerLink="/catalogue" [queryParams]="{ promo: 'true' }">Promotions</a>
        </nav>
        <div class="actions">
          <a routerLink="/catalogue" class="ic" title="Rechercher">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.3"
            >
              <circle cx="11" cy="11" r="7" />
              <line x1="21" y1="21" x2="16.5" y2="16.5" />
            </svg>
          </a>
          <a [routerLink]="compteLien()" class="ic" title="Mon compte">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.3"
            >
              <circle cx="12" cy="8" r="4" />
              <path d="M4 21c0-4 3.5-7 8-7s8 3 8 7" />
            </svg>
          </a>
          <a routerLink="/panier" class="ic panier" title="Panier">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.3"
            >
              <path d="M6 7h12l-1 13H7L6 7z" />
              <path d="M9 7a3 3 0 0 1 6 0" />
            </svg>
            @if (panier.nombre() > 0) {
              <span class="pastille">{{ panier.nombre() }}</span>
            }
          </a>
        </div>
      </div>
    </header>
  `,
  styles: [
    `
      .annonce {
        background: var(--texte);
        color: var(--fond);
        text-align: center;
        font-size: 0.72rem;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        padding: 10px 16px;
      }
      .annonce .sep {
        opacity: 0.5;
        margin: 0 8px;
      }
      header {
        position: sticky;
        top: 0;
        z-index: 50;
        background: rgba(250, 246, 241, 0.9);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--bordure);
      }
      .barre {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 78px;
      }
      .logo {
        font-family: var(--serif);
        font-size: 1.7rem;
        font-weight: 600;
        letter-spacing: 0.04em;
      }
      .logo .point {
        color: var(--accent);
      }
      nav.principale {
        display: flex;
        gap: 34px;
      }
      nav.principale a {
        font-size: 0.82rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--texte-doux);
        padding: 6px 0;
        position: relative;
        transition: color var(--transi);
      }
      nav.principale a::after {
        content: '';
        position: absolute;
        left: 0;
        bottom: 0;
        width: 0;
        height: 1px;
        background: var(--accent);
        transition: width var(--transi);
      }
      nav.principale a:hover {
        color: var(--texte);
      }
      nav.principale a:hover::after {
        width: 100%;
      }
      .actions {
        display: flex;
        align-items: center;
        gap: 22px;
      }
      .actions .ic {
        cursor: pointer;
        color: var(--texte);
        transition: color var(--transi);
        display: inline-flex;
      }
      .actions .ic:hover {
        color: var(--accent);
      }
      .panier {
        position: relative;
      }
      .panier .pastille {
        position: absolute;
        top: -7px;
        right: -9px;
        background: var(--accent);
        color: #fff;
        font-size: 0.62rem;
        font-weight: 500;
        min-width: 17px;
        height: 17px;
        padding: 0 4px;
        border-radius: 9px;
        display: grid;
        place-items: center;
      }
      @media (max-width: 860px) {
        nav.principale {
          display: none;
        }
        .annonce .masque {
          display: none;
        }
      }
    `,
  ],
})
export class Entete {
  protected readonly panier = inject(PanierService);
  private readonly authClient = inject(AuthClientService);
  protected readonly compteLien = computed(() =>
    this.authClient.estConnecte() ? '/mon-compte' : '/connexion',
  );
}
