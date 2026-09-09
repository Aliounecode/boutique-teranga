import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  ClientCreation,
  ClientDetailLecture,
  ClientLecture,
  ClientMiseAJour,
  ClientPage,
} from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class ClientService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/clients`;

  lister(recherche?: string, page = 1, taillePage = 15, inclureInactifs = false): Observable<ClientPage> {
    let params = new HttpParams().set('page', String(page)).set('taille_page', String(taillePage));
    if (recherche) params = params.set('recherche', recherche);
    if (inclureInactifs) params = params.set('inclure_inactifs', 'true');
    return this.http.get<ClientPage>(this.base, { params });
  }

  /** Recherche courte (utilisee par la caisse). */
  rechercher(recherche: string): Observable<ClientPage> {
    const params = new HttpParams().set('recherche', recherche).set('taille_page', '8');
    return this.http.get<ClientPage>(this.base, { params });
  }

  detail(id: number): Observable<ClientDetailLecture> {
    return this.http.get<ClientDetailLecture>(`${this.base}/${id}`);
  }

  creer(donnees: ClientCreation): Observable<ClientLecture> {
    return this.http.post<ClientLecture>(this.base, donnees);
  }

  mettreAJour(id: number, donnees: ClientMiseAJour): Observable<ClientLecture> {
    return this.http.patch<ClientLecture>(`${this.base}/${id}`, donnees);
  }

  supprimer(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
