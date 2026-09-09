import { Component, computed, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { catchError, forkJoin, of, switchMap } from 'rxjs';

import { TableauBordService } from '../../../coeur/services/tableau-bord';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import {
  LIBELLES_MOYEN,
  MoyenPaiement,
  ResumeTableauBord,
  TopCategorie,
  TopProduit,
} from '../../../coeur/modeles/modeles';

interface Periode { libelle: string; debut: string; fin: string; }
interface DonneesTb { resume: ResumeTableauBord; topProduits: TopProduit[]; topCategories: TopCategorie[]; }

@Component({
  selector: 'g-tableau-bord',
  imports: [FcfaPipe],
  templateUrl: './tableau-bord.html',
  styleUrl: './tableau-bord.scss',
})
export class TableauBord {
  private readonly service = inject(TableauBordService);

  readonly periodes: Periode[] = this.construirePeriodes();
  readonly periodeActive = signal<string>(this.periodes[0].libelle);
  private readonly periode = signal<Periode>(this.periodes[0]);

  readonly donnees = toSignal(
    toObservable(this.periode).pipe(
      switchMap((p) =>
        forkJoin({
          resume: this.service.resume(p.debut, p.fin),
          topProduits: this.service.topProduits(p.debut, p.fin, 5),
          topCategories: this.service.topCategories(p.debut, p.fin, 5),
        }).pipe(catchError(() => of(null))),
      ),
    ),
  );

  readonly maxProduit = computed(() => {
    const d = this.donnees();
    return d ? Math.max(1, ...d.topProduits.map((t) => t.quantite_vendue)) : 1;
  });

  choisir(p: Periode): void {
    this.periodeActive.set(p.libelle);
    this.periode.set(p);
  }

  libelleMoyen(moyen: MoyenPaiement): string {
    return LIBELLES_MOYEN[moyen];
  }

  pourcentage(valeur: number, max: number): number {
    return Math.round((valeur / max) * 100);
  }

  private construirePeriodes(): Periode[] {
    const fmt = (d: Date) => d.toISOString().slice(0, 10);
    const aujourdhui = new Date();
    const ilYa7 = new Date();
    ilYa7.setDate(aujourdhui.getDate() - 6);
    const debutMois = new Date(aujourdhui.getFullYear(), aujourdhui.getMonth(), 1);
    return [
      { libelle: "Aujourd'hui", debut: fmt(aujourdhui), fin: fmt(aujourdhui) },
      { libelle: '7 jours', debut: fmt(ilYa7), fin: fmt(aujourdhui) },
      { libelle: 'Ce mois', debut: fmt(debutMois), fin: fmt(aujourdhui) },
    ];
  }
}
