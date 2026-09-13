import { Component, HostListener, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { catchError, of, switchMap, tap } from 'rxjs';

import { CatalogueService } from '../../../coeur/services/catalogue';
import { PanierService } from '../../../coeur/services/panier';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import { Produit, Variante } from '../../../coeur/modeles/modeles';

@Component({
  selector: 'bq-produit-detail',
  imports: [RouterLink, FcfaPipe],
  templateUrl: './produit-detail.html',
  styleUrl: './produit-detail.scss',
})
export class ProduitDetail {
  private readonly catalogue = inject(CatalogueService);
  private readonly route = inject(ActivatedRoute);
  private readonly panier = inject(PanierService);

  // undefined = en cours de chargement ; null = introuvable
  readonly produit = toSignal(
    this.route.paramMap.pipe(
      switchMap((params) =>
        this.catalogue.detailProduit(Number(params.get('id'))).pipe(catchError(() => of(null))),
      ),
      tap((produit) => this.reinitialiserSelection(produit)),
    ),
  );

  readonly varianteSelectionnee = signal<Variante | null>(null);
  readonly indexPhoto = signal(0);
  readonly message = signal<string | null>(null);

  readonly photos = computed(() => this.produit()?.photos ?? []);
  readonly photoActive = computed(() => this.photos()[this.indexPhoto()]?.url ?? null);

  readonly variantesActives = computed(() =>
    (this.produit()?.variantes ?? []).filter((v) => v.actif),
  );
  readonly peutAjouter = computed(() => {
    const variante = this.varianteSelectionnee();
    return !!variante && variante.quantite_disponible > 0;
  });

  precedente(): void {
    const n = this.photos().length;
    if (n > 1) this.indexPhoto.update((i) => (i - 1 + n) % n);
  }

  suivante(): void {
    const n = this.photos().length;
    if (n > 1) this.indexPhoto.update((i) => (i + 1) % n);
  }

  @HostListener('document:keydown', ['$event'])
  clavier(evenement: KeyboardEvent): void {
    const cible = evenement.target as HTMLElement | null;
    if (cible && ['INPUT', 'TEXTAREA', 'SELECT'].includes(cible.tagName)) return;
    if (this.photos().length < 2) return;
    if (evenement.key === 'ArrowLeft') {
      this.precedente();
    } else if (evenement.key === 'ArrowRight') {
      this.suivante();
    }
  }

  libelleVariante(variante: Variante): string {
    const parties = [variante.couleur, variante.taille].filter(Boolean);
    return parties.length ? parties.join(' · ') : 'Modèle unique';
  }

  ajouter(): void {
    const produit = this.produit();
    const variante = this.varianteSelectionnee();
    if (!produit || !variante || variante.quantite_disponible <= 0) {
      return;
    }
    const photo =
      produit.photos.find((p) => p.est_principale)?.url ?? produit.photos[0]?.url ?? null;
    this.panier.ajouter({
      variante_id: variante.id,
      produit_id: produit.id,
      produit_nom: produit.nom,
      couleur: variante.couleur,
      taille: variante.taille,
      prix_unitaire: Number(produit.prix_effectif),
      quantite: 1,
      photo,
    });
    this.message.set('Ajouté au panier ✓');
    setTimeout(() => this.message.set(null), 2500);
  }

  private reinitialiserSelection(produit: Produit | null): void {
    this.varianteSelectionnee.set(null);
    this.message.set(null);
    if (produit && produit.photos.length) {
      const idx = produit.photos.findIndex((p) => p.est_principale);
      this.indexPhoto.set(idx >= 0 ? idx : 0);
    } else {
      this.indexPhoto.set(0);
    }
  }
}
