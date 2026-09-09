import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { ResumeTableauBord, TopCategorie, TopProduit } from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class TableauBordService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/tableau-bord`;

  private avecDates(debut?: string, fin?: string, extra?: Record<string, string | number>): HttpParams {
    let params = new HttpParams();
    if (debut) params = params.set('date_debut', debut);
    if (fin) params = params.set('date_fin', fin);
    for (const [cle, valeur] of Object.entries(extra ?? {})) {
      params = params.set(cle, String(valeur));
    }
    return params;
  }

  resume(debut?: string, fin?: string): Observable<ResumeTableauBord> {
    return this.http.get<ResumeTableauBord>(`${this.base}/resume`, { params: this.avecDates(debut, fin) });
  }

  topProduits(debut?: string, fin?: string, limite = 5): Observable<TopProduit[]> {
    return this.http.get<TopProduit[]>(`${this.base}/top-produits`, { params: this.avecDates(debut, fin, { limite }) });
  }

  topCategories(debut?: string, fin?: string, limite = 5): Observable<TopCategorie[]> {
    return this.http.get<TopCategorie[]>(`${this.base}/top-categories`, { params: this.avecDates(debut, fin, { limite }) });
  }
}
