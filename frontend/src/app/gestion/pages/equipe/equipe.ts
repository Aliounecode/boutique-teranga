import { Component, inject, signal } from '@angular/core';
import { FormBuilder, FormControl, ReactiveFormsModule, Validators } from '@angular/forms';

import { UtilisateurService } from '../../../coeur/services/utilisateur';
import { Role, Utilisateur } from '../../../coeur/modeles/modeles';

@Component({
  selector: 'g-equipe',
  imports: [ReactiveFormsModule],
  template: `
    <section class="page">
      <div class="tete">
        <div>
          <p class="surtitre">Gestion</p>
          <h1 class="titre">Équipe</h1>
        </div>
        <button type="button" class="btn accent" (click)="basculerNouveau()">
          {{ modeNouveau() ? 'Fermer' : '+ Nouveau membre' }}
        </button>
      </div>

      @if (message()) {
        <div class="ok">{{ message() }}</div>
      }
      @if (erreur()) {
        <div class="alerte">{{ erreur() }}</div>
      }

      @if (modeNouveau()) {
        <div class="carte formulaire">
          <h2>Nouveau membre</h2>
          <form [formGroup]="form" (ngSubmit)="creer()">
            <div class="grille">
              <label><span>Nom *</span><input formControlName="nom" /></label>
              <label><span>Prénom *</span><input formControlName="prenom" /></label>
              <label
                ><span>Identifiant *</span
                ><input formControlName="nom_utilisateur" autocomplete="off"
              /></label>
              <label
                ><span>Rôle *</span>
                <select formControlName="role_id">
                  @for (r of roles(); track r.id) {
                    <option [ngValue]="r.id">{{ libelleRole(r.nom) }}</option>
                  }
                </select>
              </label>
              <label><span>E-mail</span><input type="email" formControlName="email" /></label>
              <label><span>Téléphone</span><input formControlName="telephone" /></label>
              <label class="pleine"
                ><span>Mot de passe *</span>
                <div class="champ-mdp">
                  <input
                    [type]="afficherMdp() ? 'text' : 'password'"
                    formControlName="mot_de_passe"
                    autocomplete="new-password"
                  />
                  <button
                    type="button"
                    class="oeil"
                    (click)="afficherMdp.set(!afficherMdp())"
                    aria-label="Afficher/masquer"
                  >
                    @if (afficherMdp()) {
                      <svg
                        width="19"
                        height="19"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.4"
                      >
                        <path d="M3 3l18 18" />
                        <path d="M10.6 10.6a2 2 0 002.8 2.8" />
                        <path
                          d="M9.9 4.2A9.5 9.5 0 0112 4c5 0 9 4.5 10 8-.4 1.2-1.1 2.4-2 3.4M6.1 6.1C4 7.4 2.6 9.4 2 12c1 3.5 5 8 10 8 1.5 0 2.9-.3 4.1-.9"
                        />
                      </svg>
                    } @else {
                      <svg
                        width="19"
                        height="19"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="1.4"
                      >
                        <path d="M2 12s3.5-8 10-8 10 8 10 8-3.5 8-10 8-10-8-10-8z" />
                        <circle cx="12" cy="12" r="3" />
                      </svg>
                    }
                  </button>
                </div>
                <small>6 caractères minimum.</small>
              </label>
            </div>
            <button type="submit" class="btn accent" [disabled]="enCours()">
              {{ enCours() ? 'Création…' : 'Créer le membre' }}
            </button>
          </form>
        </div>
      }

      <div class="carte">
        <table>
          <thead>
            <tr>
              <th>Membre</th>
              <th>Identifiant</th>
              <th>Contact</th>
              <th>Rôle</th>
              <th>Statut</th>
              <th class="ta-d">Actions</th>
            </tr>
          </thead>
          <tbody>
            @for (u of membres(); track u.id) {
              <tr [class.inactif]="!u.actif">
                <td class="nom">{{ u.prenom }} {{ u.nom }}</td>
                <td>{{ u.nom_utilisateur }}</td>
                <td class="contact">
                  {{ u.email || '—' }}
                  @if (u.telephone) {
                    <br />{{ u.telephone }}
                  }
                </td>
                <td>
                  <select class="role-select" (change)="changerRole(u, $event)">
                    @for (r of roles(); track r.id) {
                      <option [value]="r.id" [selected]="r.id === u.role.id">
                        {{ libelleRole(r.nom) }}
                      </option>
                    }
                  </select>
                </td>
                <td>
                  <span class="badge" [class.on]="u.actif">{{
                    u.actif ? 'Actif' : 'Inactif'
                  }}</span>
                </td>
                <td class="actions">
                  <button type="button" (click)="basculer(u)">
                    {{ u.actif ? 'Désactiver' : 'Activer' }}
                  </button>
                  <button type="button" (click)="ouvrirReset(u.id)">Mot de passe</button>
                </td>
              </tr>
              @if (resetPour() === u.id) {
                <tr class="ligne-reset">
                  <td colspan="6">
                    <div class="reset">
                      <div class="champ-mdp">
                        <input
                          [type]="afficherReset() ? 'text' : 'password'"
                          [formControl]="ctrlReset"
                          placeholder="Nouveau mot de passe (6+)"
                        />
                        <button
                          type="button"
                          class="oeil"
                          (click)="afficherReset.set(!afficherReset())"
                          aria-label="Afficher/masquer"
                        >
                          @if (afficherReset()) {
                            <svg
                              width="18"
                              height="18"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              stroke-width="1.4"
                            >
                              <path d="M3 3l18 18" />
                              <path d="M10.6 10.6a2 2 0 002.8 2.8" />
                              <path
                                d="M9.9 4.2A9.5 9.5 0 0112 4c5 0 9 4.5 10 8-.4 1.2-1.1 2.4-2 3.4M6.1 6.1C4 7.4 2.6 9.4 2 12c1 3.5 5 8 10 8 1.5 0 2.9-.3 4.1-.9"
                              />
                            </svg>
                          } @else {
                            <svg
                              width="18"
                              height="18"
                              viewBox="0 0 24 24"
                              fill="none"
                              stroke="currentColor"
                              stroke-width="1.4"
                            >
                              <path d="M2 12s3.5-8 10-8 10 8 10 8-3.5 8-10 8-10-8-10-8z" />
                              <circle cx="12" cy="12" r="3" />
                            </svg>
                          }
                        </button>
                      </div>
                      <button type="button" class="btn accent pt" (click)="validerReset(u.id)">
                        Valider
                      </button>
                      <button type="button" class="btn clair pt" (click)="fermerReset()">
                        Annuler
                      </button>
                    </div>
                  </td>
                </tr>
              }
            } @empty {
              <tr>
                <td colspan="6" class="vide">Aucun membre.</td>
              </tr>
            }
          </tbody>
        </table>
      </div>
    </section>
  `,
  styles: [
    `
      .page {
        max-width: 1000px;
      }
      .tete {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 22px;
      }
      .titre {
        font-family: var(--serif);
        font-weight: 500;
        font-size: 2rem;
        margin-top: 4px;
      }
      .btn {
        font-size: 0.72rem;
        padding: 12px 20px;
      }
      .btn.pt {
        padding: 9px 16px;
      }
      .carte {
        background: var(--surface);
        border: 1px solid var(--bordure);
        box-shadow: var(--ombre);
      }
      .formulaire {
        padding: 26px;
        margin-bottom: 22px;
      }
      .formulaire h2 {
        font-family: var(--serif);
        font-weight: 500;
        font-size: 1.3rem;
        margin-bottom: 18px;
      }
      .grille {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-bottom: 20px;
      }
      label {
        display: grid;
        gap: 6px;
      }
      label.pleine {
        grid-column: 1 / -1;
      }
      label span {
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--texte-doux);
      }
      input,
      select {
        font-family: var(--sans);
        font-size: 0.92rem;
        padding: 10px 12px;
        border: 1px solid var(--bordure);
        background: var(--fond);
        color: var(--texte);
      }
      input:focus,
      select:focus {
        outline: none;
        border-color: var(--accent);
      }
      small {
        font-size: 0.72rem;
        color: var(--texte-doux);
      }
      .champ-mdp {
        position: relative;
      }
      .champ-mdp input {
        width: 100%;
        padding-right: 44px;
      }
      .oeil {
        position: absolute;
        right: 6px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        padding: 6px;
        cursor: pointer;
        color: var(--texte-doux);
        display: inline-flex;
      }
      .oeil:hover {
        color: var(--accent);
      }
      table {
        width: 100%;
        border-collapse: collapse;
      }
      th,
      td {
        text-align: left;
        padding: 14px 18px;
        font-size: 0.9rem;
        border-bottom: 1px solid var(--bordure);
        vertical-align: middle;
      }
      th {
        font-size: 0.68rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--texte-doux);
        font-weight: 500;
      }
      .ta-d {
        text-align: right;
      }
      tr.inactif td {
        opacity: 0.5;
      }
      .nom {
        font-weight: 500;
      }
      .contact {
        color: var(--texte-doux);
        font-size: 0.82rem;
      }
      .role-select {
        padding: 6px 10px;
        font-size: 0.82rem;
      }
      .badge {
        font-size: 0.66rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 4px 11px;
        border-radius: 20px;
        background: #fbeae6;
        color: #8a3a2b;
      }
      .badge.on {
        background: #e7f1e3;
        color: #40663a;
      }
      .actions {
        text-align: right;
        white-space: nowrap;
      }
      .actions button {
        background: none;
        border: 1px solid var(--bordure);
        padding: 7px 12px;
        margin-left: 8px;
        font-family: var(--sans);
        font-size: 0.74rem;
        cursor: pointer;
        color: var(--texte-doux);
        transition: all var(--transi);
      }
      .actions button:hover {
        border-color: var(--accent);
        color: var(--accent);
      }
      .ligne-reset td {
        background: var(--surface-2);
      }
      .reset {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      .reset .champ-mdp {
        min-width: 260px;
      }
      .vide {
        text-align: center;
        color: var(--texte-doux);
        padding: 30px;
      }
      .ok {
        background: #eef4ec;
        border: 1px solid #bcd6b6;
        color: #40663a;
        padding: 12px 16px;
        margin-bottom: 16px;
        font-size: 0.88rem;
      }
      .alerte {
        background: #fbeae6;
        border: 1px solid #e6b7ad;
        color: #8a3a2b;
        padding: 12px 16px;
        margin-bottom: 16px;
        font-size: 0.88rem;
      }
      @media (max-width: 680px) {
        .grille {
          grid-template-columns: 1fr;
        }
        .contact {
          display: none;
        }
      }
    `,
  ],
})
export class Equipe {
  private readonly srv = inject(UtilisateurService);
  private readonly fb = inject(FormBuilder);

  protected readonly membres = signal<Utilisateur[]>([]);
  protected readonly roles = signal<Role[]>([]);
  protected readonly modeNouveau = signal(false);
  protected readonly enCours = signal(false);
  protected readonly message = signal<string | null>(null);
  protected readonly erreur = signal<string | null>(null);
  protected readonly afficherMdp = signal(false);

  protected readonly resetPour = signal<number | null>(null);
  protected readonly afficherReset = signal(false);
  protected readonly ctrlReset = new FormControl('', {
    nonNullable: true,
    validators: [Validators.required, Validators.minLength(6)],
  });

  protected readonly form = this.fb.nonNullable.group({
    nom: ['', [Validators.required]],
    prenom: ['', [Validators.required]],
    nom_utilisateur: ['', [Validators.required, Validators.minLength(3)]],
    email: [''],
    telephone: [''],
    mot_de_passe: ['', [Validators.required, Validators.minLength(6)]],
    role_id: [0, [Validators.required]],
  });

  constructor() {
    this.srv.roles().subscribe((r) => {
      this.roles.set(r);
      const vendeur = r.find((x) => x.nom === 'vendeur') ?? r[0];
      if (vendeur) this.form.patchValue({ role_id: vendeur.id });
    });
    this.recharger();
  }

  private recharger(): void {
    this.srv.lister().subscribe((liste) => this.membres.set(liste));
  }

  protected libelleRole(nom: string): string {
    return nom === 'gerant' ? 'Gérant' : nom === 'vendeur' ? 'Vendeur' : nom;
  }

  basculerNouveau(): void {
    this.modeNouveau.update((v) => !v);
    this.message.set(null);
    this.erreur.set(null);
  }

  creer(): void {
    if (this.form.invalid || !this.form.getRawValue().role_id) {
      this.form.markAllAsTouched();
      return;
    }
    this.enCours.set(true);
    this.erreur.set(null);
    this.message.set(null);
    const v = this.form.getRawValue();
    this.srv
      .creer({
        nom: v.nom.trim(),
        prenom: v.prenom.trim(),
        nom_utilisateur: v.nom_utilisateur.trim(),
        email: v.email.trim() || undefined,
        telephone: v.telephone.trim() || undefined,
        mot_de_passe: v.mot_de_passe,
        role_id: v.role_id,
      })
      .subscribe({
        next: () => {
          this.enCours.set(false);
          this.message.set('Membre créé.');
          this.form.reset({ role_id: v.role_id });
          this.modeNouveau.set(false);
          this.recharger();
        },
        error: (e) => {
          this.enCours.set(false);
          this.erreur.set(this.msg(e));
        },
      });
  }

  changerRole(u: Utilisateur, evenement: Event): void {
    const role_id = Number((evenement.target as HTMLSelectElement).value);
    if (!role_id || role_id === u.role.id) return;
    this.majSimple(u.id, { role_id }, 'Rôle mis à jour.');
  }

  basculer(u: Utilisateur): void {
    this.majSimple(u.id, { actif: !u.actif }, u.actif ? 'Membre désactivé.' : 'Membre réactivé.');
  }

  private majSimple(id: number, donnees: { role_id?: number; actif?: boolean }, ok: string): void {
    this.erreur.set(null);
    this.message.set(null);
    this.srv.mettreAJour(id, donnees).subscribe({
      next: () => {
        this.message.set(ok);
        this.recharger();
      },
      error: (e) => {
        this.erreur.set(this.msg(e));
        this.recharger();
      },
    });
  }

  ouvrirReset(id: number): void {
    this.resetPour.set(id);
    this.afficherReset.set(false);
    this.ctrlReset.reset('');
    this.message.set(null);
    this.erreur.set(null);
  }

  fermerReset(): void {
    this.resetPour.set(null);
  }

  validerReset(id: number): void {
    if (this.ctrlReset.invalid) {
      this.ctrlReset.markAsTouched();
      return;
    }
    this.srv.changerMotDePasse(id, this.ctrlReset.getRawValue()).subscribe({
      next: () => {
        this.message.set('Mot de passe mis à jour.');
        this.fermerReset();
      },
      error: (e) => this.erreur.set(this.msg(e)),
    });
  }

  private msg(e: unknown): string {
    const d = (e as { error?: { detail?: unknown } })?.error?.detail;
    return typeof d === 'string' ? d : 'Une erreur est survenue.';
  }
}
