import { Component, effect, inject, input, signal } from '@angular/core';
import { PhotoService } from '../../../coeur/services/photo';
import { Photo } from '../../../coeur/modeles/modeles';

@Component({
  selector: 'g-photos',
  imports: [],
  template: `
    <div class="photos-gestion">
      <div class="grille-photos">
        @for (p of photos(); track p.id; let i = $index) {
          <div class="ph" [class.princ]="p.est_principale">
            <img [src]="p.url" alt="" />
            @if (p.est_principale) {
              <span class="etiq-princ">Principale</span>
            }
            <div class="actions-ph">
              @if (!p.est_principale) {
                <button
                  type="button"
                  (click)="definirPrincipale(p)"
                  title="Définir comme principale"
                >
                  ★
                </button>
              }
              <button
                type="button"
                (click)="deplacer(i, -1)"
                [disabled]="i === 0"
                title="Déplacer avant"
              >
                ←
              </button>
              <button
                type="button"
                (click)="deplacer(i, 1)"
                [disabled]="i === photos().length - 1"
                title="Déplacer après"
              >
                →
              </button>
              <button type="button" class="sup" (click)="supprimer(p)" title="Supprimer">✕</button>
            </div>
          </div>
        } @empty {
          <p class="aucune">Aucune photo pour l'instant.</p>
        }
      </div>

      <label class="televerser" [class.charge]="envoi()">
        <input
          type="file"
          accept="image/*"
          multiple
          (change)="televerser($event)"
          [disabled]="envoi()"
          hidden
        />
        {{ envoi() ? 'Envoi en cours…' : '+ Ajouter des photos' }}
      </label>
      @if (erreur()) {
        <p class="erreur-b">{{ erreur() }}</p>
      }
      <p class="aide-ph">JPEG, PNG, WEBP ou GIF · 10 Mo max par image · 10 photos max.</p>
    </div>
  `,
  styles: [
    `
      .grille-photos {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 16px;
      }
      .ph {
        position: relative;
        width: 110px;
      }
      .ph img {
        width: 110px;
        height: 138px;
        object-fit: contain;
        background: var(--surface);
        border: 1px solid var(--bordure);
        display: block;
      }
      .ph.princ img {
        border-color: var(--accent);
        border-width: 2px;
      }
      .etiq-princ {
        position: absolute;
        top: 6px;
        left: 6px;
        background: var(--accent);
        color: #fff;
        font-size: 0.6rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 3px 7px;
      }
      .actions-ph {
        display: flex;
        gap: 4px;
        margin-top: 6px;
      }
      .actions-ph button {
        flex: 1;
        background: var(--surface);
        border: 1px solid var(--bordure);
        cursor: pointer;
        padding: 5px 0;
        font-size: 0.82rem;
        color: var(--texte-doux);
        transition: all var(--transi);
      }
      .actions-ph button:hover:not(:disabled) {
        border-color: var(--accent);
        color: var(--accent);
      }
      .actions-ph button:disabled {
        opacity: 0.3;
        cursor: not-allowed;
      }
      .aucune {
        color: var(--texte-doux);
        font-size: 0.9rem;
      }
      .televerser {
        display: inline-block;
        background: none;
        border: 1px dashed var(--bordure);
        padding: 12px 22px;
        font-size: 0.86rem;
        cursor: pointer;
        color: var(--texte-doux);
        transition: all var(--transi);
      }
      .televerser:hover {
        border-color: var(--accent);
        color: var(--accent);
      }
      .televerser.charge {
        opacity: 0.6;
        cursor: default;
      }
      .erreur-b {
        background: #f7e4de;
        border: 1px solid var(--accent);
        color: var(--accent-fonce);
        padding: 11px 14px;
        font-size: 0.88rem;
        margin-top: 12px;
      }
      .aide-ph {
        font-size: 0.78rem;
        color: var(--texte-doux);
        margin-top: 10px;
      }
    `,
  ],
})
export class GestionPhotos {
  private readonly service = inject(PhotoService);
  readonly produitId = input.required<number>();

  readonly photos = signal<Photo[]>([]);
  readonly envoi = signal(false);
  readonly erreur = signal<string | null>(null);

  constructor() {
    effect(() => {
      const id = this.produitId();
      if (id) {
        this.charger(id);
      }
    });
  }

  private charger(id: number): void {
    this.service.lister(id).subscribe({
      next: (photos) => this.photos.set(photos),
      error: () => this.photos.set([]),
    });
  }

  televerser(evenement: Event): void {
    const champ = evenement.target as HTMLInputElement;
    const fichiers = champ.files ? Array.from(champ.files) : [];
    if (!fichiers.length) return;
    this.envoi.set(true);
    this.erreur.set(null);
    this.service.televerser(this.produitId(), fichiers).subscribe({
      next: () => {
        this.envoi.set(false);
        this.charger(this.produitId());
        champ.value = '';
      },
      error: (e) => {
        this.envoi.set(false);
        this.erreur.set(this.msg(e));
        champ.value = '';
      },
    });
  }

  definirPrincipale(photo: Photo): void {
    this.erreur.set(null);
    this.service.definirPrincipale(photo.id).subscribe({
      next: () => this.charger(this.produitId()),
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  supprimer(photo: Photo): void {
    if (!confirm('Supprimer cette photo ?')) return;
    this.erreur.set(null);
    this.service.supprimer(photo.id).subscribe({
      next: () => this.charger(this.produitId()),
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  deplacer(index: number, sens: number): void {
    const ordre = this.photos().map((p) => p.id);
    const cible = index + sens;
    if (cible < 0 || cible >= ordre.length) return;
    [ordre[index], ordre[cible]] = [ordre[cible], ordre[index]];
    this.service.reordonner(this.produitId(), ordre).subscribe({
      next: () => this.charger(this.produitId()),
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  private msg(e: unknown): string {
    const detail = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof detail === 'string' ? detail : "Échec de l'opération sur la photo.";
  }
}
