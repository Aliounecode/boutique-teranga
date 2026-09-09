import { Injectable, computed, effect, signal } from '@angular/core';

export interface LignePanier {
  variante_id: number;
  produit_id: number;
  produit_nom: string;
  couleur: string | null;
  taille: string | null;
  prix_unitaire: number;
  quantite: number;
  photo: string | null;
}

@Injectable({ providedIn: 'root' })
export class PanierService {
  private readonly cle = 'boutique_panier';

  readonly lignes = signal<LignePanier[]>(this.charger());
  readonly nombre = computed(() => this.lignes().reduce((somme, l) => somme + l.quantite, 0));
  readonly total = computed(() =>
    this.lignes().reduce((somme, l) => somme + l.prix_unitaire * l.quantite, 0),
  );

  constructor() {
    // Persistance automatique à chaque changement.
    effect(() => localStorage.setItem(this.cle, JSON.stringify(this.lignes())));
  }

  ajouter(ligne: LignePanier): void {
    const lignes = [...this.lignes()];
    const existante = lignes.find((l) => l.variante_id === ligne.variante_id);
    if (existante) {
      existante.quantite += ligne.quantite;
    } else {
      lignes.push(ligne);
    }
    this.lignes.set(lignes);
  }

  modifierQuantite(varianteId: number, quantite: number): void {
    if (quantite <= 0) {
      this.retirer(varianteId);
      return;
    }
    this.lignes.set(
      this.lignes().map((l) => (l.variante_id === varianteId ? { ...l, quantite } : l)),
    );
  }

  retirer(varianteId: number): void {
    this.lignes.set(this.lignes().filter((l) => l.variante_id !== varianteId));
  }

  vider(): void {
    this.lignes.set([]);
  }

  private charger(): LignePanier[] {
    try {
      return JSON.parse(localStorage.getItem(this.cle) ?? '[]') as LignePanier[];
    } catch {
      return [];
    }
  }
}
