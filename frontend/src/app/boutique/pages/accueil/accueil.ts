import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { Apparition } from '../../../coeur/directives/apparition';

import { CatalogueService } from '../../../coeur/services/catalogue';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';

import { CategorieArbre, FiltresProduits, ProduitResume } from '../../../coeur/modeles/modeles';

@Component({
  selector: 'bq-accueil',
  imports: [RouterLink, FcfaPipe],
  templateUrl: './accueil.html',
  styleUrl: './accueil.scss',
})
export class Accueil {
  private readonly catalogue = inject(CatalogueService);

  // =========================================================
  // CATÉGORIES
  // =========================================================

  readonly categories = toSignal(this.catalogue.arbreCategories(), {
    initialValue: [] as CategorieArbre[],
  });

  // =========================================================
  // NOUVEAUTÉS
  // =========================================================

  readonly nouveautes = toSignal(
    this.catalogue
      .listerProduits({
        tri: 'recent',
        taille_page: 4,
      })
      .pipe(map((page) => page.elements)),
    {
      initialValue: [] as ProduitResume[],
    },
  );

  // =========================================================
  // PROMOTIONS
  // =========================================================

  readonly promotions = toSignal(
    this.catalogue
      .listerProduits({
        en_promotion: true,
        taille_page: 8,
      })
      .pipe(map((page) => page.elements)),
    {
      initialValue: [] as ProduitResume[],
    },
  );

  // =========================================================
  // IMAGE DES CATÉGORIES
  // =========================================================

  getImageCategorie(nom: string): string {
    const nomNormalise = nom.trim().toLowerCase();

    const images: Record<string, string> = {
      sacs: 'images/univers/sacs.jpg',

      chaussures: 'images/univers/chaussures.jpg',

      accessoires: 'images/univers/accessoires.jpg',
    };

    return images[nomNormalise] ?? 'images/univers/default.jpg';
  }
}
