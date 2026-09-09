import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { VenteCreation, VenteLecture } from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class VenteService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/ventes`;

  creer(donnees: VenteCreation): Observable<VenteLecture> {
    return this.http.post<VenteLecture>(this.base, donnees);
  }

  /** Facture PDF d'une vente (avec le jeton via l'intercepteur), en Blob. */
  factureVente(id: number): Observable<Blob> {
    return this.http.get(`${environment.apiUrl}/factures/vente/${id}`, { responseType: 'blob' });
  }
}
