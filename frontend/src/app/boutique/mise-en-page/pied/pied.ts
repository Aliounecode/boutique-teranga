import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'bq-pied',
  imports: [RouterLink],
  template: `
    <footer>
      <div class="conteneur">
        <div class="grille">
          <div>
            <a routerLink="/" class="logo">PAPE ALE ET BAMBA<span class="point">.</span></a>
            <p class="desc">
              Votre boutique de sacs et chaussures pour femmes à Dakar. L'élégance accessible, en
              ligne et en boutique.
            </p>
          </div>
          <div>
            <h4>Boutique</h4>
            <ul>
              <li><a routerLink="/">Sacs</a></li>
              <li><a routerLink="/">Chaussures</a></li>
              <li><a routerLink="/">Nouveautés</a></li>
              <li><a routerLink="/">Promotions</a></li>
            </ul>
          </div>
          <div>
            <h4>Aide</h4>
            <ul>
              <li><a routerLink="/">Livraison</a></li>
              <li><a routerLink="/">Retours</a></li>
              <li><a routerLink="/">Suivi de commande</a></li>
              <li><a routerLink="/">FAQ</a></li>
            </ul>
          </div>
          <div>
            <h4>Contact</h4>
            <ul>
              <li>Médina , Centenaire , Dakar</li>
              <li>
                78 596 94 22 / 76 849 40 69 /// 77 668 40 41 / 77 668 40 41 /// 77 471 52 57 / 76
                841 28 10
              </li>
              <li><a routerLink="/">Instagram</a></li>
            </ul>
          </div>
        </div>
      </div>
      <div class="bas">© 2026 — Tous droits réservés</div>
    </footer>
  `,
  styles: [
    `
      footer {
        background: var(--texte);
        color: #d9cfc6;
        padding: 72px 0 0;
        margin-top: 40px;
      }
      .grille {
        display: grid;
        grid-template-columns: 1.6fr 1fr 1fr 1fr;
        gap: 40px;
        padding-bottom: 54px;
      }
      .logo {
        font-family: var(--serif);
        font-size: 1.7rem;
        font-weight: 600;
        color: var(--fond);
        display: inline-block;
        margin-bottom: 16px;
      }
      .logo .point {
        color: var(--accent);
      }
      .desc {
        font-size: 0.9rem;
        color: #a99c92;
        max-width: 300px;
      }
      h4 {
        font-size: 0.74rem;
        font-weight: 500;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--fond);
        margin-bottom: 18px;
      }
      ul {
        list-style: none;
      }
      ul li {
        margin-bottom: 11px;
        font-size: 0.9rem;
        color: #a99c92;
      }
      ul li a {
        color: #a99c92;
        transition: color var(--transi);
      }
      ul li a:hover {
        color: var(--fond);
      }
      .paiements {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-top: 8px;
      }
      .paiements span {
        font-size: 0.64rem;
        letter-spacing: 0.06em;
        border: 1px solid #4a413b;
        padding: 5px 9px;
        color: #c4b8ae;
      }
      .bas {
        border-top: 1px solid #423934;
        padding: 22px 0;
        text-align: center;
        font-size: 0.76rem;
        color: #8b7f76;
        letter-spacing: 0.08em;
      }
      @media (max-width: 860px) {
        .grille {
          grid-template-columns: 1fr 1fr;
        }
      }
      @media (max-width: 520px) {
        .grille {
          grid-template-columns: 1fr;
        }
      }
    `,
  ],
})
export class Pied {}
