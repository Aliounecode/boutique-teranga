import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { CategorieArbre, FiltresProduits, PageProduits, Produit } from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class CatalogueService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  /** Arbre des catégories actives (racines + sous-catégories). */
  arbreCategories(): Observable<CategorieArbre[]> {
    return this.http.get<CategorieArbre[]>(`${this.base}/categories`);
  }

  /** Liste paginée des produits de la boutique (filtres, tri). */
  listerProduits(filtres: FiltresProduits = {}): Observable<PageProduits> {
    let params = new HttpParams();
    for (const [cle, valeur] of Object.entries(filtres)) {
      if (valeur !== undefined && valeur !== null && valeur !== '') {
        params = params.set(cle, String(valeur));
      }
    }
    return this.http.get<PageProduits>(`${this.base}/produits`, { params });
  }

  detailProduit(id: number): Observable<Produit> {
    return this.http.get<Produit>(`${this.base}/produits/${id}`);
  }
}
