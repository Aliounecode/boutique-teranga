import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, switchMap, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Jeton, Utilisateur } from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly cleJeton = 'boutique_jeton';

  readonly jeton = signal<string | null>(localStorage.getItem(this.cleJeton));
  readonly utilisateur = signal<Utilisateur | null>(null);

  readonly estConnecte = computed(() => this.jeton() !== null);
  readonly estGerant = computed(() => this.utilisateur()?.role.nom === 'gerant');

  /** Connexion OAuth2 (form-urlencoded), puis chargement du profil. */
  connexion(nomUtilisateur: string, motDePasse: string): Observable<Utilisateur> {
    const corps = new URLSearchParams();
    corps.set('username', nomUtilisateur);
    corps.set('password', motDePasse);
    return this.http
      .post<Jeton>(`${environment.apiUrl}/auth/connexion`, corps.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .pipe(
        tap((reponse) => this.definirJeton(reponse.access_token)),
        switchMap(() => this.chargerProfil()),
      );
  }

  chargerProfil(): Observable<Utilisateur> {
    return this.http
      .get<Utilisateur>(`${environment.apiUrl}/auth/moi`)
      .pipe(tap((utilisateur) => this.utilisateur.set(utilisateur)));
  }

  deconnexion(): void {
    this.jeton.set(null);
    this.utilisateur.set(null);
    localStorage.removeItem(this.cleJeton);
  }

  private definirJeton(jeton: string): void {
    this.jeton.set(jeton);
    localStorage.setItem(this.cleJeton, jeton);
  }
}
