import { Component, computed, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../../coeur/services/auth';

@Component({
  selector: 'g-layout',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="admin">
      <aside class="cote">
        <a routerLink="/gestion" class="marque">PAPE ALE ET BAMBA <span>Gestion</span></a>
        <nav>
          @for (item of menu(); track item.lien) {
            <a
              [routerLink]="item.lien"
              routerLinkActive="actif"
              [routerLinkActiveOptions]="{ exact: item.exact }"
              >{{ item.libelle }}</a
            >
          }
        </nav>
      </aside>
      <div class="principal">
        <header class="haut">
          @if (utilisateur(); as u) {
            <span class="user"
              >{{ u.prenom }} {{ u.nom }}
              <span class="role" [class.vendeur]="!estGerant()">{{
                estGerant() ? 'Gérant' : 'Vendeur'
              }}</span></span
            >
          }
          <button class="deco" (click)="deconnexion()">Déconnexion</button>
        </header>
        <main class="contenu"><router-outlet /></main>
      </div>
    </div>
  `,
  styles: [
    `
      .admin {
        display: grid;
        grid-template-columns: 244px 1fr;
        min-height: 100vh;
      }
      .cote {
        background: var(--texte);
        color: #cfc4ba;
        padding: 26px 0;
        position: sticky;
        top: 0;
        height: 100vh;
        align-self: start;
      }
      .marque {
        display: block;
        padding: 0 26px 26px;
        font-family: var(--serif);
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--fond);
      }
      .marque span {
        display: block;
        font-family: var(--sans);
        font-size: 0.62rem;
        letter-spacing: 0.26em;
        text-transform: uppercase;
        color: var(--accent);
        margin-top: 2px;
      }
      .cote nav {
        display: flex;
        flex-direction: column;
      }
      .cote nav a {
        padding: 12px 26px;
        font-size: 0.92rem;
        color: #b4a89e;
        border-left: 3px solid transparent;
        transition: all var(--transi);
      }
      .cote nav a:hover {
        color: var(--fond);
        background: rgba(255, 255, 255, 0.04);
      }
      .cote nav a.actif {
        color: var(--fond);
        border-left-color: var(--accent);
        background: rgba(183, 110, 91, 0.16);
      }
      .principal {
        display: flex;
        flex-direction: column;
      }
      .haut {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 18px;
        padding: 16px 32px;
        border-bottom: 1px solid var(--bordure);
        background: var(--surface);
      }
      .user {
        font-size: 0.9rem;
        color: var(--texte);
        display: inline-flex;
        align-items: center;
      }
      .role {
        margin-left: 8px;
        font-size: 0.6rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 3px 9px;
        border-radius: 20px;
        background: rgba(183, 110, 91, 0.16);
        color: var(--accent);
      }
      .role.vendeur {
        background: #eef0f6;
        color: #4a5578;
      }
      .deco {
        background: none;
        border: 1px solid var(--bordure);
        padding: 8px 16px;
        font-family: var(--sans);
        font-size: 0.74rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        cursor: pointer;
        color: var(--texte-doux);
        transition: all var(--transi);
      }
      .deco:hover {
        border-color: var(--accent);
        color: var(--accent);
      }
      .contenu {
        padding: 32px;
        flex: 1;
      }
      @media (max-width: 780px) {
        .admin {
          grid-template-columns: 1fr;
        }
        .cote {
          position: static;
          height: auto;
          padding: 16px 0;
        }
        .cote nav {
          flex-direction: row;
          overflow-x: auto;
        }
        .cote nav a {
          border-left: none;
          border-bottom: 3px solid transparent;
          white-space: nowrap;
        }
        .cote nav a.actif {
          border-left: none;
          border-bottom-color: var(--accent);
        }
      }
    `,
  ],
})
export class GestionLayout {
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);
  readonly utilisateur = this.auth.utilisateur;
  readonly estGerant = this.auth.estGerant;

  private readonly tousLesLiens = [
    { lien: '/gestion', libelle: 'Tableau de bord', exact: true, vendeur: false },
    { lien: '/gestion/produits', libelle: 'Produits', exact: false, vendeur: false },
    { lien: '/gestion/stock', libelle: 'Stock', exact: false, vendeur: false },
    { lien: '/gestion/caisse', libelle: 'Caisse', exact: false, vendeur: true },
    { lien: '/gestion/commandes', libelle: 'Commandes', exact: false, vendeur: false },
    { lien: '/gestion/clients', libelle: 'Clients', exact: false, vendeur: true },
    { lien: '/gestion/rapports', libelle: 'Rapports', exact: false, vendeur: true },
    { lien: '/gestion/equipe', libelle: 'Équipe', exact: false, vendeur: false },
  ];

  readonly menu = computed(() =>
    this.auth.estGerant() ? this.tousLesLiens : this.tousLesLiens.filter((i) => i.vendeur),
  );

  deconnexion(): void {
    this.auth.deconnexion();
    this.router.navigate(['/gestion/connexion']);
  }
}
