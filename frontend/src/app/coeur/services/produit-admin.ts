import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import {
  FiltresProduits,
  PageProduits,
  Produit,
  ProduitCreation,
  ProduitMiseAJour,
} from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class ProduitAdminService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiUrl}/produits`;

  /** Liste de gestion (inclut les produits desactives). */
  listerGestion(filtres: FiltresProduits = {}): Observable<PageProduits> {
    let params = new HttpParams();
    for (const [cle, valeur] of Object.entries(filtres)) {
      if (valeur !== undefined && valeur !== null && valeur !== '') {
        params = params.set(cle, String(valeur));
      }
    }
    return this.http.get<PageProduits>(`${this.base}/gestion`, { params });
  }

  creer(donnees: ProduitCreation): Observable<Produit> {
    return this.http.post<Produit>(this.base, donnees);
  }

  mettreAJour(id: number, donnees: ProduitMiseAJour): Observable<Produit> {
    return this.http.patch<Produit>(`${this.base}/${id}`, donnees);
  }

  supprimer(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
