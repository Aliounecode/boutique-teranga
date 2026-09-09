import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Role, Utilisateur, UtilisateurCreation, UtilisateurMiseAJour } from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class UtilisateurService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/utilisateurs`;

  lister(): Observable<Utilisateur[]> {
    return this.http.get<Utilisateur[]>(this.base);
  }

  roles(): Observable<Role[]> {
    return this.http.get<Role[]>(`${this.base}/roles`);
  }

  creer(donnees: UtilisateurCreation): Observable<Utilisateur> {
    return this.http.post<Utilisateur>(this.base, donnees);
  }

  mettreAJour(id: number, donnees: UtilisateurMiseAJour): Observable<Utilisateur> {
    return this.http.patch<Utilisateur>(`${this.base}/${id}`, donnees);
  }

  changerMotDePasse(id: number, motDePasse: string): Observable<{ message: string }> {
    return this.http.post<{ message: string }>(`${this.base}/${id}/mot-de-passe`, {
      mot_de_passe: motDePasse,
    });
  }
}
