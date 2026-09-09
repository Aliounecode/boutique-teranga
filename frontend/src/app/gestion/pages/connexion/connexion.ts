import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { AuthService } from '../../../coeur/services/auth';

@Component({
  selector: 'g-connexion',
  imports: [ReactiveFormsModule],
  templateUrl: './connexion.html',
  styleUrl: './connexion.scss',
})
export class Connexion {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  readonly envoi = signal(false);
  readonly erreur = signal<string | null>(null);
  readonly motDePasseVisible = signal(false);

  readonly formulaire = this.fb.nonNullable.group({
    nom_utilisateur: ['', Validators.required],
    mot_de_passe: ['', Validators.required],
  });

  basculerMotDePasse(): void {
    this.motDePasseVisible.update((v) => !v);
  }

  soumettre(): void {
    if (this.formulaire.invalid) {
      this.formulaire.markAllAsTouched();
      return;
    }
    this.envoi.set(true);
    this.erreur.set(null);
    const { nom_utilisateur, mot_de_passe } = this.formulaire.getRawValue();
    this.auth.connexion(nom_utilisateur, mot_de_passe).subscribe({
      next: () => {
        this.envoi.set(false);
        if (this.auth.estGerant()) {
          this.router.navigate(['/gestion']);
        } else {
          this.auth.deconnexion();
          this.erreur.set("Ce compte n'a pas accès à l'espace gérant.");
        }
      },
      error: () => {
        this.envoi.set(false);
        this.erreur.set('Nom d’utilisateur ou mot de passe incorrect.');
      },
    });
  }
}
