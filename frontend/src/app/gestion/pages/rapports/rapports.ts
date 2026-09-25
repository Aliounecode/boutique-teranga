import { Component, inject, signal } from '@angular/core';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { catchError, of, switchMap } from 'rxjs';

import { RapportService } from '../../../coeur/services/rapport';
import { AuthService } from '../../../coeur/services/auth';
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
  private readonly auth = inject(AuthService);

  readonly estGerant = this.auth.estGerant;

  readonly jour = signal<string>(this.aujourdhui());
  readonly telechargement = signal(false);
  readonly telechargementMes = signal(false);
  readonly erreur = signal<string | null>(null);

  /** Rapport global de la boutique — gérant uniquement. */
  readonly rapport = toSignal(
    toObservable(this.jour).pipe(
      switchMap((j) =>
        this.estGerant() ? this.srv.donnees(j).pipe(catchError(() => of(null))) : of(null),
      ),
    ),
  );

  /** Mes ventes du jour — gérant ou vendeur. */
  readonly mesVentes = toSignal(
    toObservable(this.jour).pipe(
      switchMap((j) => this.srv.mesVentesDonnees(j).pipe(catchError(() => of(null)))),
    ),
  );

  choisirJour(v: string): void {
    this.jour.set(v || this.aujourdhui());
  }

  libelleMoyen(m: MoyenPaiement): string {
    return LIBELLES_MOYEN[m];
  }

  telecharger(): void {
    this.telechargement.set(true);
    this.erreur.set(null);
    this.srv.pdf(this.jour()).subscribe({
      next: (blob) => {
        this.enregistrer(blob, `rapport-${this.jour()}.pdf`);
        this.telechargement.set(false);
      },
      error: () => {
        this.telechargement.set(false);
        this.erreur.set('Impossible de générer le PDF.');
      },
    });
  }

  telechargerMesVentes(): void {
    this.telechargementMes.set(true);
    this.erreur.set(null);
    this.srv.mesVentesPdf(this.jour()).subscribe({
      next: (blob) => {
        this.enregistrer(blob, `mes-ventes-${this.jour()}.pdf`);
        this.telechargementMes.set(false);
      },
      error: () => {
        this.telechargementMes.set(false);
        this.erreur.set('Impossible de générer le PDF.');
      },
    });
  }

  private enregistrer(blob: Blob, nom: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nom;
    a.click();
    URL.revokeObjectURL(url);
  }

  private aujourdhui(): string {
    return new Date().toISOString().slice(0, 10);
  }
}
