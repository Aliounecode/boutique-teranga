import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { AlerteStock, MouvementLecture, MouvementPage, TypeMouvementStock } from '../modeles/modeles';

interface FiltresMouvements {
  variante_id?: number;
  produit_id?: number;
  type_mouvement?: TypeMouvementStock;
  page?: number;
  taille_page?: number;
}

@Injectable({ providedIn: 'root' })
export class StockService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/stock`;

  alertes(): Observable<AlerteStock[]> {
    return this.http.get<AlerteStock[]>(`${this.base}/alertes`);
  }

  mouvements(filtres: FiltresMouvements = {}): Observable<MouvementPage> {
    let params = new HttpParams();
    for (const [cle, valeur] of Object.entries(filtres)) {
      if (valeur !== undefined && valeur !== null && valeur !== '') {
        params = params.set(cle, String(valeur));
      }
    }
    return this.http.get<MouvementPage>(`${this.base}/mouvements`, { params });
  }

  reapprovisionner(donnees: { variante_id: number; quantite: number; motif?: string }): Observable<MouvementLecture> {
    return this.http.post<MouvementLecture>(`${this.base}/reapprovisionner`, donnees);
  }

  corriger(donnees: { variante_id: number; nouvelle_quantite: number; motif?: string }): Observable<MouvementLecture> {
    return this.http.post<MouvementLecture>(`${this.base}/corriger`, donnees);
  }
}
