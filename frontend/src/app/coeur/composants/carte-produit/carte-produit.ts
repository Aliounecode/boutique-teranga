import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FcfaPipe } from '../../pipes/fcfa-pipe';
import { ProduitResume } from '../../modeles/modeles';

@Component({
  selector: 'bq-carte-produit',
  imports: [RouterLink, FcfaPipe],
  template: `
    <a class="produit" [routerLink]="['/produit', produit().id]">
      <div class="visuel">
        @if (produit().en_promotion) {
          <span class="badge">Promo</span>
        }
        @if (!produit().disponible_achat) {
          <span class="badge rupture">Rupture</span>
        }
        @if (produit().photo_principale) {
          <img [src]="produit().photo_principale" [alt]="produit().nom" />
        } @else {
          <span class="initiale">{{ produit().nom.charAt(0) }}</span>
        }
      </div>
      <div class="nom">{{ produit().nom }}</div>
      <div class="prix">
        @if (produit().en_promotion && produit().prix_promo) {
          <span class="barre">{{ produit().prix | fcfa }}</span>
          <span class="promo">{{ produit().prix_promo | fcfa }}</span>
        } @else {
          {{ produit().prix_effectif | fcfa }}
        }
      </div>
    </a>
  `,
  styles: [
    `
      .produit {
        display: block;
      }
      .produit .visuel {
        position: relative;
        aspect-ratio: 3 / 4;
        overflow: hidden;
        background: linear-gradient(160deg, #f1e4db 0%, #e3cdc0 100%);
        display: grid;
        place-items: center;
        margin-bottom: 16px;
      }
      .produit .visuel img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        background: var(--surface);
      }
      .produit .visuel .initiale {
        font-family: var(--serif);
        font-style: italic;
        font-size: 4.5rem;
        color: rgba(154, 86, 69, 0.28);
      }
      .produit .visuel .badge {
        position: absolute;
        top: 14px;
        left: 14px;
        z-index: 2;
        background: var(--accent);
        color: #fff;
        font-size: 0.64rem;
        font-weight: 500;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 5px 10px;
      }
      .produit .visuel .badge.rupture {
        background: var(--texte-doux);
        left: auto;
        right: 14px;
      }
      .produit .nom {
        font-family: var(--serif);
        font-size: 1.3rem;
        font-weight: 500;
        margin: 3px 0 6px;
      }
      .produit .prix {
        font-size: 0.95rem;
      }
      .produit .prix .barre {
        color: var(--texte-doux);
        text-decoration: line-through;
        margin-right: 8px;
      }
      .produit .prix .promo {
        color: var(--accent);
      }
    `,
  ],
})
export class CarteProduit {
  readonly produit = input.required<ProduitResume>();
}
