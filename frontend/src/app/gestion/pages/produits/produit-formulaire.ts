import { Component, computed, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormArray, FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { PhotoService } from '../../../coeur/services/photo';

import { ProduitAdminService } from '../../../coeur/services/produit-admin';
import { CatalogueService } from '../../../coeur/services/catalogue';
import { GestionPhotos } from '../../composants/gestion-photos/gestion-photos';
import {
  CategorieArbre,
  ProduitCreation,
  ProduitMiseAJour,
  StatutProduit,
} from '../../../coeur/modeles/modeles';

interface CategoriePlate {
  id: number;
  nom: string;
  niveau: number;
}

@Component({
  selector: 'g-produit-formulaire',
  imports: [ReactiveFormsModule, RouterLink, GestionPhotos],
  templateUrl: './produit-formulaire.html',
  styleUrl: './produit-formulaire.scss',
})
export class ProduitFormulaire {
  private readonly fb = inject(FormBuilder);
  private readonly admin = inject(ProduitAdminService);
  private readonly catalogue = inject(CatalogueService);
  private readonly photos = inject(PhotoService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly categories = toSignal(
    this.catalogue.arbreCategories().pipe(map((arbre) => this.aplatir(arbre))),
    { initialValue: [] as CategoriePlate[] },
  );

  readonly id = signal<number | null>(null);
  readonly estEdition = computed(() => this.id() !== null);
  readonly envoi = signal(false);
  readonly erreur = signal<string | null>(null);
  readonly variantesLecture = signal<{ libelle: string; stock: number }[]>([]);
  readonly photosEnAttente = signal<{ fichier: File; apercu: string }[]>([]);

  readonly form = this.fb.nonNullable.group({
    nom: ['', [Validators.required, Validators.maxLength(200)]],
    description: [''],
    categorie_id: [0, [Validators.required, Validators.min(1)]],
    prix: [0, [Validators.required, Validators.min(1)]],
    en_promotion: [false],
    prix_promo: [0],
    a_tailles: [false],
    statut: ['disponible' as StatutProduit],
    actif: [true],
    variantes: this.fb.array([this.nouvelleVariante()]),
  });

  get variantes(): FormArray {
    return this.form.get('variantes') as FormArray;
  }

  constructor() {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (idParam) {
      const id = Number(idParam);
      this.id.set(id);
      this.catalogue.detailProduit(id).subscribe((p) => {
        this.form.patchValue({
          nom: p.nom,
          description: p.description ?? '',
          categorie_id: p.categorie_id,
          prix: Number(p.prix),
          en_promotion: p.en_promotion,
          prix_promo: p.prix_promo ? Number(p.prix_promo) : 0,
          a_tailles: p.a_tailles,
          statut: p.statut,
          actif: p.actif,
        });
        this.variantesLecture.set(
          p.variantes.map((v) => ({
            libelle: [v.couleur, v.taille].filter(Boolean).join(' · ') || 'Modèle unique',
            stock: v.quantite_disponible,
          })),
        );
      });
    }
  }

  nouvelleVariante() {
    return this.fb.nonNullable.group({
      couleur: [''],
      taille: [''],
      quantite_disponible: [0, [Validators.min(0)]],
      stock_minimum: [0, [Validators.min(0)]],
    });
  }
  ajouterVariante(): void {
    this.variantes.push(this.nouvelleVariante());
  }
  retirerVariante(i: number): void {
    if (this.variantes.length > 1) this.variantes.removeAt(i);
  }
  ajouterPhotos(evenement: Event): void {
    const input = evenement.target as HTMLInputElement;
    const nouvelles = Array.from(input.files ?? []).map((fichier) => ({
      fichier,
      apercu: URL.createObjectURL(fichier),
    }));
    this.photosEnAttente.update((liste) => [...liste, ...nouvelles]);
    input.value = '';
  }

  retirerPhoto(i: number): void {
    this.photosEnAttente.update((liste) => {
      URL.revokeObjectURL(liste[i].apercu);
      return liste.filter((_, idx) => idx !== i);
    });
  }

  soumettre(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.envoi.set(true);
    this.erreur.set(null);
    const v = this.form.getRawValue();
    const id = this.id();

    if (id === null) {
      const payload: ProduitCreation = {
        nom: v.nom.trim(),
        description: v.description.trim() || undefined,
        categorie_id: v.categorie_id,
        prix: v.prix,
        prix_promo: v.en_promotion ? v.prix_promo || undefined : undefined,
        en_promotion: v.en_promotion,
        a_tailles: v.a_tailles,
        statut: v.statut,
        variantes: v.variantes.map((vn) => ({
          couleur: vn.couleur.trim() || undefined,
          taille: vn.taille.trim() || undefined,
          quantite_disponible: vn.quantite_disponible,
          stock_minimum: vn.stock_minimum,
        })),
      };
      this.admin.creer(payload).subscribe({
        next: (nouveau) => {
          const fichiers = this.photosEnAttente().map((ph) => ph.fichier);
          if (fichiers.length === 0) {
            this.router.navigate(['/gestion/produits']);
            return;
          }
          this.photos.televerser(nouveau.id, fichiers).subscribe({
            next: () => this.router.navigate(['/gestion/produits']),
            error: () => {
              this.envoi.set(false);
              this.erreur.set(
                "Produit créé, mais l'envoi des photos a échoué. Ouverture de la fiche pour réessayer…",
              );
              setTimeout(
                () => this.router.navigate(['/gestion/produits', nouveau.id, 'modifier']),
                1600,
              );
            },
          });
        },
        error: (e) => {
          this.envoi.set(false);
          this.erreur.set(this.msg(e));
        },
      });
    } else {
      const payload: ProduitMiseAJour = {
        nom: v.nom.trim(),
        description: v.description.trim() || null,
        categorie_id: v.categorie_id,
        prix: v.prix,
        prix_promo: v.en_promotion ? v.prix_promo || null : null,
        en_promotion: v.en_promotion,
        statut: v.statut,
        actif: v.actif,
      };
      this.admin.mettreAJour(id, payload).subscribe({
        next: () => this.router.navigate(['/gestion/produits']),
        error: (e) => {
          this.envoi.set(false);
          this.erreur.set(this.msg(e));
        },
      });
    }
  }

  private msg(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string' ? detail : 'Vérifiez les champs et réessayez.';
  }

  private aplatir(arbre: CategorieArbre[], niveau = 0): CategoriePlate[] {
    const resultat: CategoriePlate[] = [];
    for (const c of arbre) {
      resultat.push({ id: c.id, nom: c.nom, niveau });
      resultat.push(...this.aplatir(c.sous_categories, niveau + 1));
    }
    return resultat;
  }
}
