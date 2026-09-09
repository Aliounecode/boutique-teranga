import { Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, combineLatest, map, of, switchMap } from 'rxjs';

import { ProduitAdminService } from '../../../coeur/services/produit-admin';
import { CatalogueService } from '../../../coeur/services/catalogue';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import { CategorieArbre, FiltresProduits, ProduitResume } from '../../../coeur/modeles/modeles';

interface CategoriePlate { id: number; nom: string; niveau: number; }

@Component({
  selector: 'g-produits-liste',
  imports: [RouterLink, FcfaPipe],
  templateUrl: './produits-liste.html',
  styleUrl: './produits-liste.scss',
})
export class ProduitsListe {
  private readonly admin = inject(ProduitAdminService);
  private readonly catalogue = inject(CatalogueService);

  readonly categories = toSignal(
    this.catalogue.arbreCategories().pipe(map((arbre) => this.aplatir(arbre))),
    { initialValue: [] as CategoriePlate[] },
  );
  readonly filtres = signal<FiltresProduits>({ page: 1, taille_page: 15 });
  private readonly tic = signal(0);
  readonly erreur = signal<string | null>(null);

  readonly page = toSignal(
    combineLatest([toObservable(this.filtres), toObservable(this.tic)]).pipe(
      switchMap(([f]) => this.admin.listerGestion(f).pipe(catchError(() => of(null)))),
    ),
  );

  readonly nombrePages = computed(() => {
    const p = this.page();
    return p ? Math.max(1, Math.ceil(p.total / p.taille_page)) : 1;
  });

  recharger(): void { this.tic.update((n) => n + 1); }
  chercher(valeur: string): void { this.filtres.set({ ...this.filtres(), recherche: valeur || undefined, page: 1 }); }
  filtrerCategorie(id: string): void { this.filtres.set({ ...this.filtres(), categorie_id: id ? Number(id) : undefined, page: 1 }); }
  allerPage(n: number): void { this.filtres.set({ ...this.filtres(), page: n }); }

  basculerActif(p: ProduitResume): void {
    this.erreur.set(null);
    this.admin.mettreAJour(p.id, { actif: !p.actif }).subscribe({
      next: () => this.recharger(),
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  supprimer(p: ProduitResume): void {
    if (!confirm(`Supprimer definitivement « ${p.nom} » ?`)) return;
    this.erreur.set(null);
    this.admin.supprimer(p.id).subscribe({
      next: () => this.recharger(),
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  private msg(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string' ? detail : 'Une erreur est survenue.';
  }

  private aplatir(arbre: CategorieArbre[], niveau = 0): CategoriePlate[] {
    const resultat: CategoriePlate[] = [];
    for (const c of arbre) {
      resultat.push({ id: c.id, nom: c.nom, niveau });
      resultat.push(...this.aplatir(c.sous_categories, niveau + 1));
    }
    return resultat;
  }
}
