import { Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { CommandeService } from '../../../coeur/services/commande';
import { LignePanier, PanierService } from '../../../coeur/services/panier';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import { CommandeCreation, CommandeLecture, MoyenPaiement } from '../../../coeur/modeles/modeles';
import { AuthClientService } from '../../../coeur/services/auth-client';

@Component({
  selector: 'bq-commande',
  imports: [RouterLink, ReactiveFormsModule, FcfaPipe],
  templateUrl: './commande.html',
  styleUrl: './commande.scss',
})
export class Commande {
  private readonly fb = inject(FormBuilder);
  private readonly commandeService = inject(CommandeService);
  private readonly panier = inject(PanierService);
  private readonly authClient = inject(AuthClientService);

  readonly lignes = this.panier.lignes;
  readonly total = this.panier.total;

  readonly envoi = signal(false);
  readonly erreur = signal<string | null>(null);
  readonly confirmee = signal<CommandeLecture | null>(null);

  readonly moyens: { valeur: MoyenPaiement; libelle: string }[] = [
    { valeur: 'wave', libelle: 'Wave' },
    { valeur: 'orange_money', libelle: 'Orange Money' },
    { valeur: 'free_money', libelle: 'Free Money' },
    { valeur: 'especes', libelle: 'Espèces' },
    { valeur: 'carte', libelle: 'Carte bancaire' },
    { valeur: 'autre', libelle: 'Autre' },
  ];

  readonly formulaire = this.fb.nonNullable.group({
    client_nom: ['', [Validators.required, Validators.maxLength(100)]],
    client_prenom: [''],
    client_telephone: ['', [Validators.required, Validators.maxLength(30)]],
    moyen_paiement: ['wave' as MoyenPaiement, Validators.required],
    notes: [''],
  });
  readonly NUMEROS_VENDEUR = ['77 471 52 57', '78 481 98 09'];
  readonly moyenChoisi = toSignal(this.formulaire.controls.moyen_paiement.valueChanges, {
    initialValue: this.formulaire.controls.moyen_paiement.value,
  });
  readonly paiementMobile = computed(() =>
    ['wave', 'orange_money', 'free_money'].includes(this.moyenChoisi()),
  );
  constructor() {
    if (this.authClient.estConnecte()) {
      if (this.authClient.client()) {
        this.preremplir();
      } else {
        this.authClient.chargerProfil().subscribe({ next: () => this.preremplir() });
      }
    }
  }

  private preremplir(): void {
    const c = this.authClient.client();
    if (!c) return;
    this.formulaire.patchValue({
      client_nom: c.nom ?? '',
      client_prenom: c.prenom ?? '',
      client_telephone: c.telephone ?? '',
    });
  }
  libelle(ligne: LignePanier): string {
    return [ligne.couleur, ligne.taille].filter(Boolean).join(' · ');
  }

  estInvalide(nom: string): boolean {
    const controle = this.formulaire.get(nom);
    return !!controle && controle.invalid && controle.touched;
  }

  soumettre(): void {
    if (this.formulaire.invalid || this.lignes().length === 0) {
      this.formulaire.markAllAsTouched();
      return;
    }
    this.envoi.set(true);
    this.erreur.set(null);
    const v = this.formulaire.getRawValue();
    const donnees: CommandeCreation = {
      client_nom: v.client_nom.trim(),
      client_prenom: v.client_prenom.trim() || undefined,
      client_telephone: v.client_telephone.trim(),
      moyen_paiement: v.moyen_paiement,
      notes: v.notes.trim() || undefined,
      lignes: this.lignes().map((l) => ({ variante_id: l.variante_id, quantite: l.quantite })),
    };
    this.commandeService.creer(donnees).subscribe({
      next: (commande) => {
        this.confirmee.set(commande);
        this.panier.vider();
        this.envoi.set(false);
      },
      error: (err) => {
        this.erreur.set(this.messageErreur(err));
        this.envoi.set(false);
      },
    });
  }

  private messageErreur(err: unknown): string {
    const detail = (err as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string'
      ? detail
      : "Une erreur est survenue lors de l'envoi de la commande. Veuillez réessayer.";
  }
}
