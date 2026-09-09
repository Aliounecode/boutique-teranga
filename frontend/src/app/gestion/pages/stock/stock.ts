import { Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { catchError, combineLatest, of, switchMap } from 'rxjs';

import { StockService } from '../../../coeur/services/stock';
import { ProduitAdminService } from '../../../coeur/services/produit-admin';
import { CatalogueService } from '../../../coeur/services/catalogue';
import {
  AlerteStock,
  LIBELLES_MOUVEMENT,
  Produit,
  ProduitResume,
  TypeMouvementStock,
} from '../../../coeur/modeles/modeles';

@Component({
  selector: 'g-stock',
  imports: [DatePipe],
  templateUrl: './stock.html',
  styleUrl: './stock.scss',
})
export class StockPage {
  private readonly stock = inject(StockService);
  private readonly admin = inject(ProduitAdminService);
  private readonly catalogue = inject(CatalogueService);

  readonly alertes = signal<AlerteStock[]>([]);
  readonly resultats = signal<ProduitResume[]>([]);
  readonly produitSel = signal<Produit | null>(null);
  readonly message = signal<string | null>(null);
  readonly erreur = signal<string | null>(null);

  readonly filtreType = signal<TypeMouvementStock | ''>('');
  readonly pageMvt = signal(1);
  private readonly ticMvt = signal(0);

  readonly mouvements = toSignal(
    combineLatest([toObservable(this.filtreType), toObservable(this.pageMvt), toObservable(this.ticMvt)]).pipe(
      switchMap(([type, page]) =>
        this.stock
          .mouvements({ type_mouvement: type || undefined, page, taille_page: 12 })
          .pipe(catchError(() => of(null))),
      ),
    ),
  );

  readonly nombrePagesMvt = computed(() => {
    const m = this.mouvements();
    return m ? Math.max(1, Math.ceil(m.total / m.taille_page)) : 1;
  });

  readonly typesMouvement: { valeur: TypeMouvementStock | ''; libelle: string }[] = [
    { valeur: '', libelle: 'Tous les mouvements' },
    { valeur: 'reapprovisionnement', libelle: 'Réapprovisionnements' },
    { valeur: 'vente', libelle: 'Ventes' },
    { valeur: 'retour', libelle: 'Retours' },
    { valeur: 'correction', libelle: 'Corrections' },
    { valeur: 'perte', libelle: 'Pertes' },
  ];

  constructor() {
    this.chargerAlertes();
  }

  chargerAlertes(): void {
    this.stock.alertes().subscribe({ next: (a) => this.alertes.set(a), error: () => this.alertes.set([]) });
  }

  chercher(valeur: string): void {
    if (!valeur.trim()) { this.resultats.set([]); return; }
    this.admin.listerGestion({ recherche: valeur, taille_page: 8 }).subscribe({
      next: (p) => this.resultats.set(p.elements),
      error: () => this.resultats.set([]),
    });
  }

  selectionner(produitId: number): void {
    this.resultats.set([]);
    this.message.set(null);
    this.erreur.set(null);
    this.catalogue.detailProduit(produitId).subscribe({
      next: (p) => this.produitSel.set(p),
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  reapprovisionner(varianteId: number, quantite: number): void {
    if (!quantite || quantite <= 0) { this.erreur.set('Indiquez une quantité positive.'); return; }
    this.erreur.set(null);
    this.message.set(null);
    this.stock.reapprovisionner({ variante_id: varianteId, quantite }).subscribe({
      next: (m) => { this.message.set(`Réapprovisionnement : +${m.quantite} → ${m.quantite_apres} en stock.`); this.apresMouvement(); },
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  corriger(varianteId: number, nouvelle: number): void {
    if (nouvelle === null || nouvelle === undefined || nouvelle < 0 || Number.isNaN(nouvelle)) {
      this.erreur.set('Indiquez une quantité valide.');
      return;
    }
    this.erreur.set(null);
    this.message.set(null);
    this.stock.corriger({ variante_id: varianteId, nouvelle_quantite: nouvelle }).subscribe({
      next: (m) => { this.message.set(`Stock corrigé → ${m.quantite_apres} en stock.`); this.apresMouvement(); },
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  filtrer(type: string): void { this.filtreType.set(type as TypeMouvementStock | ''); this.pageMvt.set(1); }
  allerPageMvt(n: number): void { this.pageMvt.set(n); }
  libelleMouvement(t: TypeMouvementStock): string { return LIBELLES_MOUVEMENT[t]; }
  libelleVariante(v: { couleur: string | null; taille: string | null }): string {
    return [v.couleur, v.taille].filter(Boolean).join(' · ') || 'Modèle unique';
  }

  private apresMouvement(): void {
    const p = this.produitSel();
    if (p) this.catalogue.detailProduit(p.id).subscribe((x) => this.produitSel.set(x));
    this.chargerAlertes();
    this.ticMvt.update((n) => n + 1);
  }

  private msg(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string' ? detail : 'Une erreur est survenue.';
  }
}
