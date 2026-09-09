import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { CommandeCreation, CommandeLecture, CommandePage, StatutCommande } from '../modeles/modeles';

interface FiltresCommandes {
  statut?: StatutCommande;
  date_debut?: string;
  date_fin?: string;
  page?: number;
  taille_page?: number;
}

@Injectable({ providedIn: 'root' })
export class CommandeService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/commandes`;

  /** Passe une commande (checkout invité, public). */
  creer(donnees: CommandeCreation): Observable<CommandeLecture> {
    return this.http.post<CommandeLecture>(this.base, donnees);
  }

  lister(filtres: FiltresCommandes = {}): Observable<CommandePage> {
    let params = new HttpParams();
    for (const [cle, valeur] of Object.entries(filtres)) {
      if (valeur !== undefined && valeur !== null && valeur !== '') {
        params = params.set(cle, String(valeur));
      }
    }
    return this.http.get<CommandePage>(this.base, { params });
  }

  detail(id: number): Observable<CommandeLecture> {
    return this.http.get<CommandeLecture>(`${this.base}/${id}`);
  }

  accepter(id: number): Observable<CommandeLecture> {
    return this.http.post<CommandeLecture>(`${this.base}/${id}/accepter`, {});
  }

  refuser(id: number): Observable<CommandeLecture> {
    return this.http.post<CommandeLecture>(`${this.base}/${id}/refuser`, {});
  }

  annuler(id: number): Observable<CommandeLecture> {
    return this.http.post<CommandeLecture>(`${this.base}/${id}/annuler`, {});
  }

  /** Facture PDF d'une commande (avec le jeton via l'intercepteur), en Blob. */
  factureCommande(id: number): Observable<Blob> {
    return this.http.get(`${environment.apiUrl}/factures/commande/${id}`, { responseType: 'blob' });
  }
}
