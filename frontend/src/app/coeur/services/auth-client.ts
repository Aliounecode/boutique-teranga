import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, switchMap, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ClientCompte, CommandeLecture, InscriptionClient, Jeton } from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class AuthClientService {
  private readonly http = inject(HttpClient);
  private readonly cleJeton = 'boutique_jeton_client';
  private readonly base = `${environment.apiUrl}/compte`;

  readonly jeton = signal<string | null>(localStorage.getItem(this.cleJeton));
  readonly client = signal<ClientCompte | null>(null);
  readonly estConnecte = computed(() => this.jeton() !== null);

  inscription(donnees: InscriptionClient): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.base}/inscription`, donnees);
  }

  verifierEmail(token: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.base}/verifier-email`, { token });
  }

  renvoyerVerification(email: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.base}/renvoyer-verification`, { email });
  }

  connexion(email: string, motDePasse: string): Observable<ClientCompte> {
    return this.http
      .post<Jeton>(`${this.base}/connexion`, { email, mot_de_passe: motDePasse })
      .pipe(
        tap((reponse) => this.definirJeton(reponse.access_token)),
        switchMap(() => this.chargerProfil()),
      );
  }

  chargerProfil(): Observable<ClientCompte> {
    return this.http
      .get<ClientCompte>(`${this.base}/moi`)
      .pipe(tap((client) => this.client.set(client)));
  }

  mesCommandes(): Observable<CommandeLecture[]> {
    return this.http.get<CommandeLecture[]>(`${this.base}/commandes`);
  }

  motDePasseOublie(email: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.base}/mot-de-passe-oublie`, { email });
  }

  reinitialiser(token: string, motDePasse: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.base}/reinitialiser-mot-de-passe`, {
      token,
      mot_de_passe: motDePasse,
    });
  }

  deconnexion(): void {
    this.jeton.set(null);
    this.client.set(null);
    localStorage.removeItem(this.cleJeton);
  }

  private definirJeton(jeton: string): void {
    this.jeton.set(jeton);
    localStorage.setItem(this.cleJeton, jeton);
  }
}
