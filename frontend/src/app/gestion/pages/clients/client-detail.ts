import { Component, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { ClientService } from '../../../coeur/services/client';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import { ClientDetailLecture } from '../../../coeur/modeles/modeles';

@Component({
  selector: 'g-client-detail',
  imports: [RouterLink, DatePipe, FcfaPipe, ReactiveFormsModule],
  templateUrl: './client-detail.html',
  styleUrl: './client-detail.scss',
})
export class ClientDetail {
  private readonly srv = inject(ClientService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly fb = inject(FormBuilder);

  readonly client = signal<ClientDetailLecture | null | undefined>(undefined);
  readonly message = signal<string | null>(null);
  readonly erreur = signal<string | null>(null);
  readonly envoi = signal(false);

  readonly form = this.fb.nonNullable.group({
    nom: ['', Validators.required],
    prenom: [''],
    telephone: [''],
    actif: [true],
  });

  constructor() {
    this.charger(Number(this.route.snapshot.paramMap.get('id')));
  }

  private charger(id: number): void {
    this.srv.detail(id).subscribe({
      next: (c) => {
        this.client.set(c);
        this.form.patchValue({ nom: c.nom, prenom: c.prenom ?? '', telephone: c.telephone ?? '', actif: c.actif });
      },
      error: () => this.client.set(null),
    });
  }

  enregistrer(): void {
    const c = this.client();
    if (!c) return;
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    this.envoi.set(true);
    this.erreur.set(null);
    this.message.set(null);
    const v = this.form.getRawValue();
    this.srv.mettreAJour(c.id, {
      nom: v.nom.trim(),
      prenom: v.prenom.trim() || null,
      telephone: v.telephone.trim() || null,
      actif: v.actif,
    }).subscribe({
      next: () => { this.envoi.set(false); this.message.set('Modifications enregistrées.'); this.charger(c.id); },
      error: (e) => { this.envoi.set(false); this.erreur.set(this.msg(e)); },
    });
  }

  supprimer(): void {
    const c = this.client();
    if (!c) return;
    if (!confirm(`Supprimer « ${c.nom} » ?`)) return;
    this.srv.supprimer(c.id).subscribe({
      next: () => this.router.navigate(['/gestion/clients']),
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  private msg(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string' ? detail : 'Une erreur est survenue.';
  }
}
