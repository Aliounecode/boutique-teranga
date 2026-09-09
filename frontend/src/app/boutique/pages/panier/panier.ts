import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import { LignePanier, PanierService } from '../../../coeur/services/panier';

@Component({
  selector: 'bq-panier',
  imports: [RouterLink, FcfaPipe],
  templateUrl: './panier.html',
  styleUrl: './panier.scss',
})
export class Panier {
  private readonly panier = inject(PanierService);
  readonly lignes = this.panier.lignes;
  readonly total = this.panier.total;

  libelle(ligne: LignePanier): string {
    return [ligne.couleur, ligne.taille].filter(Boolean).join(' · ');
  }
  augmenter(ligne: LignePanier): void { this.panier.modifierQuantite(ligne.variante_id, ligne.quantite + 1); }
  diminuer(ligne: LignePanier): void { this.panier.modifierQuantite(ligne.variante_id, ligne.quantite - 1); }
  retirer(varianteId: number): void { this.panier.retirer(varianteId); }
  vider(): void { this.panier.vider(); }
}
