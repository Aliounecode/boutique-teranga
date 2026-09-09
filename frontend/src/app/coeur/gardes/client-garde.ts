import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { AuthClientService } from '../services/auth-client';

/** Protege l'espace « Mon compte » : redirige vers /connexion si non authentifie. */
export const clientGarde: CanActivateFn = () => {
  const auth = inject(AuthClientService);
  const router = inject(Router);

  if (!auth.jeton()) {
    return router.createUrlTree(['/connexion']);
  }
  if (auth.client()) {
    return true;
  }
  return auth.chargerProfil().pipe(
    map(() => true),
    catchError(() => {
      auth.deconnexion();
      return of(router.createUrlTree(['/connexion']));
    }),
  );
};
