import { Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { Observable, catchError, combineLatest, of, switchMap } from 'rxjs';

import { CommandeService } from '../../../coeur/services/commande';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import {
  CommandeResume,
  LIBELLES_COMMANDE,
  LIBELLES_MOYEN,
  MoyenPaiement,
  StatutCommande,
} from '../../../coeur/modeles/modeles';

@Component({
  selector: 'g-commandes-liste',
  imports: [RouterLink, DatePipe, FcfaPipe],
  templateUrl: './commandes-liste.html',
  styleUrl: './commandes-liste.scss',
})
export class CommandesListe {
  private readonly srv = inject(CommandeService);

  readonly filtreStatut = signal<StatutCommande | ''>('');
  readonly pageNum = signal(1);
  private readonly tic = signal(0);
  readonly message = signal<string | null>(null);
  readonly erreur = signal<string | null>(null);

  readonly page = toSignal(
    combineLatest([toObservable(this.filtreStatut), toObservable(this.pageNum), toObservable(this.tic)]).pipe(
      switchMap(([statut, page]) =>
        this.srv.lister({ statut: statut || undefined, page, taille_page: 15 }).pipe(catchError(() => of(null))),
      ),
    ),
  );

  readonly nombrePages = computed(() => {
    const p = this.page();
    return p ? Math.max(1, Math.ceil(p.total / p.taille_page)) : 1;
  });

  readonly statuts: { valeur: StatutCommande | ''; libelle: string }[] = [
    { valeur: '', libelle: 'Toutes' },
    { valeur: 'nouvelle', libelle: 'Nouvelles' },
    { valeur: 'validee', libelle: 'Validées' },
    { valeur: 'refusee', libelle: 'Refusées' },
    { valeur: 'annulee', libelle: 'Annulées' },
  ];

  filtrer(s: string): void { this.filtreStatut.set(s as StatutCommande | ''); this.pageNum.set(1); }
  allerPage(n: number): void { this.pageNum.set(n); }
  recharger(): void { this.tic.update((n) => n + 1); }
  libelleStatut(s: StatutCommande): string { return LIBELLES_COMMANDE[s]; }
  libelleMoyen(m: MoyenPaiement): string { return LIBELLES_MOYEN[m]; }

  accepter(c: CommandeResume): void { this.agir(this.srv.accepter(c.id), `Commande ${c.numero} acceptée. Stock décrémenté.`); }
  refuser(c: CommandeResume): void { this.agir(this.srv.refuser(c.id), `Commande ${c.numero} refusée.`); }
  annuler(c: CommandeResume): void {
    if (!confirm(`Annuler la commande ${c.numero} ? Le stock sera reapprovisionne.`)) return;
    this.agir(this.srv.annuler(c.id), `Commande ${c.numero} annulée. Stock rétabli.`);
  }

  private agir(obs: Observable<unknown>, succes: string): void {
    this.message.set(null);
    this.erreur.set(null);
    obs.subscribe({
      next: () => { this.message.set(succes); this.recharger(); },
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  private msg(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string' ? detail : 'Une erreur est survenue.';
  }
}
