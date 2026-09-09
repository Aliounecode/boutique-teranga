import { Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { toObservable, toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { catchError, combineLatest, of, switchMap } from 'rxjs';

import { ClientService } from '../../../coeur/services/client';
import { ClientLecture } from '../../../coeur/modeles/modeles';

@Component({
  selector: 'g-clients-liste',
  imports: [RouterLink, DatePipe, ReactiveFormsModule],
  templateUrl: './clients-liste.html',
  styleUrl: './clients-liste.scss',
})
export class ClientsListe {
  private readonly srv = inject(ClientService);
  private readonly fb = inject(FormBuilder);

  readonly recherche = signal('');
  readonly pageNum = signal(1);
  private readonly tic = signal(0);
  readonly message = signal<string | null>(null);
  readonly erreur = signal<string | null>(null);
  readonly modeNouveau = signal(false);

  readonly formNouveau = this.fb.nonNullable.group({
    nom: ['', Validators.required],
    prenom: [''],
    telephone: [''],
  });

  readonly page = toSignal(
    combineLatest([toObservable(this.recherche), toObservable(this.pageNum), toObservable(this.tic)]).pipe(
      switchMap(([r, page]) => this.srv.lister(r || undefined, page, 15, true).pipe(catchError(() => of(null)))),
    ),
  );
  readonly nombrePages = computed(() => {
    const p = this.page();
    return p ? Math.max(1, Math.ceil(p.total / p.taille_page)) : 1;
  });

  chercher(v: string): void { this.recherche.set(v); this.pageNum.set(1); }
  allerPage(n: number): void { this.pageNum.set(n); }
  recharger(): void { this.tic.update((n) => n + 1); }

  creer(): void {
    if (this.formNouveau.invalid) { this.formNouveau.markAllAsTouched(); return; }
    const v = this.formNouveau.getRawValue();
    this.erreur.set(null); this.message.set(null);
    this.srv.creer({ nom: v.nom.trim(), prenom: v.prenom.trim() || undefined, telephone: v.telephone.trim() || undefined }).subscribe({
      next: () => { this.message.set('Client créé.'); this.formNouveau.reset(); this.modeNouveau.set(false); this.recharger(); },
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  basculerActif(c: ClientLecture): void {
    this.erreur.set(null); this.message.set(null);
    this.srv.mettreAJour(c.id, { actif: !c.actif }).subscribe({ next: () => this.recharger(), error: (e) => this.erreur.set(this.msg(e)) });
  }

  supprimer(c: ClientLecture): void {
    if (!confirm(`Supprimer « ${c.nom} » ?`)) return;
    this.erreur.set(null); this.message.set(null);
    this.srv.supprimer(c.id).subscribe({ next: () => { this.message.set('Client supprimé.'); this.recharger(); }, error: (e) => this.erreur.set(this.msg(e)) });
  }

  private msg(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string' ? detail : 'Une erreur est survenue.';
  }
}
