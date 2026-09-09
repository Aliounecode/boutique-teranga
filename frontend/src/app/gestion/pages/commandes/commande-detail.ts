import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { Observable } from 'rxjs';

import { CommandeService } from '../../../coeur/services/commande';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import {
  CommandeLecture,
  LIBELLES_COMMANDE,
  LIBELLES_MOYEN,
  LigneCommandeLecture,
  MoyenPaiement,
  StatutCommande,
} from '../../../coeur/modeles/modeles';

@Component({
  selector: 'g-commande-detail',
  imports: [RouterLink, DatePipe, FcfaPipe],
  templateUrl: './commande-detail.html',
  styleUrl: './commande-detail.scss',
})
export class CommandeDetail {
  private readonly srv = inject(CommandeService);
  private readonly route = inject(ActivatedRoute);

  readonly commande = signal<CommandeLecture | null | undefined>(undefined);
  readonly message = signal<string | null>(null);
  readonly erreur = signal<string | null>(null);
  readonly action = signal(false);

  constructor() {
    this.charger(Number(this.route.snapshot.paramMap.get('id')));
  }

  private charger(id: number): void {
    this.srv.detail(id).subscribe({
      next: (c) => this.commande.set(c),
      error: () => this.commande.set(null),
    });
  }

  libelleStatut(s: StatutCommande): string {
    return LIBELLES_COMMANDE[s];
  }
  libelleMoyen(m: MoyenPaiement): string {
    return LIBELLES_MOYEN[m];
  }
  libelleVariante(l: LigneCommandeLecture): string {
    return [l.couleur, l.taille].filter(Boolean).join(' · ') || 'Modèle unique';
  }

  accepter(): void {
    this.agir((id) => this.srv.accepter(id), 'Commande acceptée. Stock décrémenté.');
  }
  refuser(): void {
    this.agir((id) => this.srv.refuser(id), 'Commande refusée.');
  }
  annuler(): void {
    const c = this.commande();
    if (!c) return;
    if (!confirm(`Annuler la commande ${c.numero} ? Le stock sera reapprovisionne.`)) return;
    this.agir((id) => this.srv.annuler(id), 'Commande annulée. Stock rétabli.');
  }

  private agir(fn: (id: number) => Observable<CommandeLecture>, succes: string): void {
    const c = this.commande();
    if (!c) return;
    this.action.set(true);
    this.message.set(null);
    this.erreur.set(null);
    fn(c.id).subscribe({
      next: (maj) => {
        this.commande.set(maj);
        this.message.set(succes);
        this.action.set(false);
      },
      error: (e) => {
        this.erreur.set(this.msg(e));
        this.action.set(false);
      },
    });
  }

  telechargerFacture(): void {
    const c = this.commande();
    if (!c) return;
    this.srv.factureCommande(c.id).subscribe((blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `facture-${c.numero}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  private msg(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string' ? detail : 'Une erreur est survenue.';
  }
}
