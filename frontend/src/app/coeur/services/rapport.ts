import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { MesVentes, RapportJournalier } from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class RapportService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/rapports`;

  private parametres(jour?: string): HttpParams {
    let params = new HttpParams();
    if (jour) params = params.set('jour', jour);
    return params;
  }

  // --- Rapport global de la boutique (gérant uniquement) ---
  donnees(jour?: string): Observable<RapportJournalier> {
    return this.http.get<RapportJournalier>(`${this.base}/journalier/donnees`, {
      params: this.parametres(jour),
    });
  }

  pdf(jour?: string): Observable<Blob> {
    return this.http.get(`${this.base}/journalier`, {
      params: this.parametres(jour),
      responseType: 'blob',
    });
  }

  // --- Mes ventes du jour (gérant ou vendeur) ---
  mesVentesDonnees(jour?: string): Observable<MesVentes> {
    return this.http.get<MesVentes>(`${this.base}/mes-ventes/donnees`, {
      params: this.parametres(jour),
    });
  }

  mesVentesPdf(jour?: string): Observable<Blob> {
    return this.http.get(`${this.base}/mes-ventes`, {
      params: this.parametres(jour),
      responseType: 'blob',
    });
  }
}
