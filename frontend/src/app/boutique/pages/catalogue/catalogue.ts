import { Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute } from '@angular/router';
import { catchError, of, switchMap, tap } from 'rxjs';

import { CatalogueService } from '../../../coeur/services/catalogue';
import { CarteProduit } from '../../../coeur/composants/carte-produit/carte-produit';
import { Apparition } from '../../../coeur/directives/apparition';
import { CategorieArbre, FiltresProduits, PageProduits } from '../../../coeur/modeles/modeles';

interface CategoriePlate {
  id: number;
  nom: string;
  niveau: number;
}

@Component({
  selector: 'bq-catalogue',
  imports: [CarteProduit, Apparition],
  templateUrl: './catalogue.html',
  styleUrl: './catalogue.scss',
})
export class Catalogue {
  private readonly catalogue = inject(CatalogueService);
  private readonly route = inject(ActivatedRoute);

  /** Blocs fantomes affiches pendant le chargement. */
  readonly squelettes = Array.from({ length: 8 });

  readonly categories = toSignal(this.catalogue.arbreCategories(), {
    initialValue: [] as CategorieArbre[],
  });
  readonly categoriesPlates = computed(() => this.aplatir(this.categories()));

  readonly filtres = signal<FiltresProduits>({ tri: 'recent', page: 1, taille_page: 12 });
  readonly chargement = signal(true);

  readonly page = toSignal(
    toObservable(this.filtres).pipe(
      tap(() => this.chargement.set(true)),
      switchMap((f) =>
        this.catalogue.listerProduits(f).pipe(
          catchError(() =>
            of({
              total: 0,
              page: f.page ?? 1,
              taille_page: f.taille_page ?? 12,
              elements: [],
            } as PageProduits),
          ),
        ),
      ),
      tap(() => this.chargement.set(false)),
    ),
  );

  readonly nombrePages = computed(() => {
    const p = this.page();
    return p ? Math.max(1, Math.ceil(p.total / p.taille_page)) : 1;
  });

  constructor() {
    const params = this.route.snapshot.queryParamMap;
    const maj: FiltresProduits = { ...this.filtres() };
    if (params.get('categorie')) maj.categorie_id = Number(params.get('categorie'));
    if (params.get('promo') === 'true') maj.en_promotion = true;
    if (params.get('recherche')) maj.recherche = params.get('recherche') ?? undefined;
    if (params.get('tri')) maj.tri = params.get('tri') as FiltresProduits['tri'];
    this.filtres.set(maj);
  }

  private appliquer(partiel: Partial<FiltresProduits>): void {
    this.filtres.set({ ...this.filtres(), ...partiel, page: 1 });
  }

  definirCategorie(id: number | undefined): void {
    this.appliquer({ categorie_id: id });
  }
  definirTri(tri: string): void {
    this.appliquer({ tri: tri as FiltresProduits['tri'] });
  }
  definirRecherche(valeur: string): void {
    this.appliquer({ recherche: valeur || undefined });
  }
  definirPrixMin(valeur: string): void {
    this.appliquer({ prix_min: valeur ? Number(valeur) : undefined });
  }
  definirPrixMax(valeur: string): void {
    this.appliquer({ prix_max: valeur ? Number(valeur) : undefined });
  }
  basculerPromo(): void {
    this.appliquer({ en_promotion: this.filtres().en_promotion ? undefined : true });
  }
  basculerStock(): void {
    this.appliquer({ en_stock: this.filtres().en_stock ? undefined : true });
  }
  reinitialiser(): void {
    this.filtres.set({ tri: 'recent', page: 1, taille_page: 12 });
  }
  allerPage(n: number): void {
    this.filtres.set({ ...this.filtres(), page: n });
  }

  private aplatir(arbre: CategorieArbre[], niveau = 0): CategoriePlate[] {
    const resultat: CategoriePlate[] = [];
    for (const categorie of arbre) {
      resultat.push({ id: categorie.id, nom: categorie.nom, niveau });
      resultat.push(...this.aplatir(categorie.sous_categories, niveau + 1));
    }
    return resultat;
  }
}
