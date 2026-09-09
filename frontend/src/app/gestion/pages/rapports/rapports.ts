import { Component, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { catchError, combineLatest, of, switchMap } from 'rxjs';

import { RapportService } from '../../../coeur/services/rapport';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import { LIBELLES_MOYEN, MoyenPaiement } from '../../../coeur/modeles/modeles';

@Component({
  selector: 'g-rapports',
  imports: [FcfaPipe],
  templateUrl: './rapports.html',
  styleUrl: './rapports.scss',
})
export class Rapports {
  private readonly srv = inject(RapportService);

  readonly jour = signal<string>(this.aujourdhui());
  readonly telechargement = signal(false);
  readonly erreur = signal<string | null>(null);

  readonly rapport = toSignal(
    toObservable(this.jour).pipe(
      switchMap((j) => this.srv.donnees(j).pipe(catchError(() => of(null)))),
    ),
  );

  choisirJour(v: string): void { this.jour.set(v || this.aujourdhui()); }
  libelleMoyen(m: MoyenPaiement): string { return LIBELLES_MOYEN[m]; }

  telecharger(): void {
    this.telechargement.set(true);
    this.erreur.set(null);
    this.srv.pdf(this.jour()).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rapport-${this.jour()}.pdf`;
        a.click();
        URL.revokeObjectURL(url);
        this.telechargement.set(false);
      },
      error: () => { this.telechargement.set(false); this.erreur.set('Impossible de générer le PDF.'); },
    });
  }

  private aujourdhui(): string {
    return new Date().toISOString().slice(0, 10);
  }
}
