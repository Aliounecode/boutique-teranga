import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../../environments/environment';
import { Photo } from '../modeles/modeles';

@Injectable({ providedIn: 'root' })
export class PhotoService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiUrl;

  lister(produitId: number): Observable<Photo[]> {
    return this.http.get<Photo[]>(`${this.base}/produits/${produitId}/photos`);
  }

  /** Upload multi-fichiers (multipart). Ne pas fixer le Content-Type : Angular le gere. */
  televerser(produitId: number, fichiers: File[]): Observable<Photo[]> {
    const donnees = new FormData();
    for (const fichier of fichiers) {
      donnees.append('fichiers', fichier);
    }
    return this.http.post<Photo[]>(`${this.base}/produits/${produitId}/photos`, donnees);
  }

  definirPrincipale(photoId: number): Observable<Photo> {
    return this.http.patch<Photo>(`${this.base}/photos/${photoId}`, { est_principale: true });
  }

  reordonner(produitId: number, ordre: number[]): Observable<Photo[]> {
    return this.http.post<Photo[]>(`${this.base}/produits/${produitId}/photos/reordonner`, { ordre });
  }

  supprimer(photoId: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/photos/${photoId}`);
  }
}
