import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { RapportJournalier } from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class RapportService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/rapports`;

  donnees(jour?: string): Observable<RapportJournalier> {
    let params = new HttpParams();
    if (jour) params = params.set('jour', jour);
    return this.http.get<RapportJournalier>(`${this.base}/journalier/donnees`, { params });
  }

  pdf(jour?: string): Observable<Blob> {
    let params = new HttpParams();
    if (jour) params = params.set('jour', jour);
    return this.http.get(`${this.base}/journalier`, { params, responseType: 'blob' });
  }
}
