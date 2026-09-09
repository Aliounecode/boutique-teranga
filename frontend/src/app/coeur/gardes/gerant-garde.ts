import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { AuthService } from '../services/auth';

export const gardeGerant: CanActivateFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.estConnecte()) {
    return router.parseUrl('/gestion/connexion');
  }
  if (auth.utilisateur()) {
    return auth.estGerant() ? true : router.parseUrl('/gestion/connexion');
  }
  // Jeton présent mais profil pas encore chargé (ex. après rafraîchissement).
  return auth.chargerProfil().pipe(
    map(() => (auth.estGerant() ? true : router.parseUrl('/gestion/connexion'))),
    catchError(() => {
      auth.deconnexion();
      return of(router.parseUrl('/gestion/connexion'));
    }),
  );
};
