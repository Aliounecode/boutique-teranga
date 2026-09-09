import { Component, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';

import { ProduitAdminService } from '../../../coeur/services/produit-admin';
import { CatalogueService } from '../../../coeur/services/catalogue';
import { VenteService } from '../../../coeur/services/vente';
import { ClientService } from '../../../coeur/services/client';
import { FcfaPipe } from '../../../coeur/pipes/fcfa-pipe';
import {
  ClientLecture,
  MoyenPaiement,
  Produit,
  ProduitResume,
  Variante,
  VenteCreation,
  VenteLecture,
} from '../../../coeur/modeles/modeles';

interface LigneCaisse {
  variante_id: number;
  produit_id: number;
  produit_nom: string;
  couleur: string | null;
  taille: string | null;
  prix_unitaire: number;
  quantite: number;
  stock_max: number;
}

@Component({
  selector: 'g-caisse',
  imports: [ReactiveFormsModule, FcfaPipe],
  templateUrl: './caisse.html',
  styleUrl: './caisse.scss',
})
export class Caisse {
  private readonly admin = inject(ProduitAdminService);
  private readonly catalogue = inject(CatalogueService);
  private readonly venteSrv = inject(VenteService);
  private readonly clientSrv = inject(ClientService);
  private readonly fb = inject(FormBuilder);

  readonly lignes = signal<LigneCaisse[]>([]);
  readonly total = computed(() => this.lignes().reduce((s, l) => s + l.prix_unitaire * l.quantite, 0));

  readonly resultats = signal<ProduitResume[]>([]);
  readonly produitSel = signal<Produit | null>(null);

  readonly clientSel = signal<ClientLecture | null>(null);
  readonly resultatsClient = signal<ClientLecture[]>([]);
  readonly modeNouveauClient = signal(false);

  readonly moyen = signal<MoyenPaiement>('especes');
  readonly moyens: { valeur: MoyenPaiement; libelle: string }[] = [
    { valeur: 'especes', libelle: 'Espèces' },
    { valeur: 'wave', libelle: 'Wave' },
    { valeur: 'orange_money', libelle: 'Orange Money' },
    { valeur: 'free_money', libelle: 'Free Money' },
    { valeur: 'carte', libelle: 'Carte' },
    { valeur: 'autre', libelle: 'Autre' },
  ];

  readonly envoi = signal(false);
  readonly erreur = signal<string | null>(null);
  readonly venteConfirmee = signal<VenteLecture | null>(null);

  readonly formClient = this.fb.nonNullable.group({
    nom: ['', Validators.required],
    prenom: [''],
    telephone: [''],
  });

  // --- Produits ---
  chercher(v: string): void {
    if (!v.trim()) { this.resultats.set([]); return; }
    this.admin.listerGestion({ recherche: v, taille_page: 8 }).subscribe({
      next: (p) => this.resultats.set(p.elements.filter((x) => x.actif)),
      error: () => this.resultats.set([]),
    });
  }
  selectionnerProduit(id: number): void {
    this.resultats.set([]);
    this.catalogue.detailProduit(id).subscribe({ next: (p) => this.produitSel.set(p), error: () => {} });
  }
  ajouter(v: Variante, prod: Produit): void {
    if (v.quantite_disponible <= 0) return;
    const lignes = [...this.lignes()];
    const existante = lignes.find((l) => l.variante_id === v.id);
    if (existante) {
      if (existante.quantite < existante.stock_max) existante.quantite += 1;
    } else {
      lignes.push({
        variante_id: v.id, produit_id: prod.id, produit_nom: prod.nom,
        couleur: v.couleur, taille: v.taille,
        prix_unitaire: Number(prod.prix_effectif), quantite: 1, stock_max: v.quantite_disponible,
      });
    }
    this.lignes.set(lignes);
  }
  augmenter(l: LigneCaisse): void {
    if (l.quantite >= l.stock_max) return;
    this.lignes.set(this.lignes().map((x) => (x.variante_id === l.variante_id ? { ...x, quantite: x.quantite + 1 } : x)));
  }
  diminuer(l: LigneCaisse): void {
    const q = l.quantite - 1;
    if (q <= 0) { this.retirer(l.variante_id); return; }
    this.lignes.set(this.lignes().map((x) => (x.variante_id === l.variante_id ? { ...x, quantite: q } : x)));
  }
  retirer(varianteId: number): void {
    this.lignes.set(this.lignes().filter((l) => l.variante_id !== varianteId));
  }

  // --- Client ---
  chercherClient(v: string): void {
    if (!v.trim()) { this.resultatsClient.set([]); return; }
    this.clientSrv.rechercher(v).subscribe({ next: (p) => this.resultatsClient.set(p.elements), error: () => this.resultatsClient.set([]) });
  }
  selectionnerClient(c: ClientLecture): void {
    this.clientSel.set(c);
    this.resultatsClient.set([]);
    this.modeNouveauClient.set(false);
  }
  anonyme(): void { this.clientSel.set(null); }
  creerClient(): void {
    if (this.formClient.invalid) { this.formClient.markAllAsTouched(); return; }
    const v = this.formClient.getRawValue();
    this.clientSrv.creer({
      nom: v.nom.trim(),
      prenom: v.prenom.trim() || undefined,
      telephone: v.telephone.trim() || undefined,
    }).subscribe({
      next: (c) => { this.clientSel.set(c); this.modeNouveauClient.set(false); this.formClient.reset(); },
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  // --- Paiement / validation ---
  choisirMoyen(m: string): void { this.moyen.set(m as MoyenPaiement); }

  valider(): void {
    if (this.lignes().length === 0) { this.erreur.set('Ajoutez au moins un article.'); return; }
    this.envoi.set(true);
    this.erreur.set(null);
    const donnees: VenteCreation = {
      client_id: this.clientSel()?.id,
      moyen_paiement: this.moyen(),
      lignes: this.lignes().map((l) => ({ variante_id: l.variante_id, quantite: l.quantite })),
    };
    this.venteSrv.creer(donnees).subscribe({
      next: (v) => { this.venteConfirmee.set(v); this.envoi.set(false); },
      error: (e) => { this.erreur.set(this.msg(e)); this.envoi.set(false); },
    });
  }

  nouvelleVente(): void {
    this.venteConfirmee.set(null);
    this.lignes.set([]);
    this.produitSel.set(null);
    this.clientSel.set(null);
    this.moyen.set('especes');
    this.erreur.set(null);
    this.resultats.set([]);
    this.resultatsClient.set([]);
    this.modeNouveauClient.set(false);
  }

  telechargerFacture(v: VenteLecture): void {
    this.venteSrv.factureVente(v.id).subscribe((blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `facture-${v.numero}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    });
  }

  libelleVariante(v: { couleur: string | null; taille: string | null }): string {
    return [v.couleur, v.taille].filter(Boolean).join(' · ') || 'Modèle unique';
  }

  private msg(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string' ? detail : 'Une erreur est survenue.';
  }
}
