import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { AuthClientService } from '../services/auth-client';

export const CLE_REDIRECTION = 'redirection_post_connexion';

/** Protege une page reservee aux clients connectes ; memorise la cible pour y revenir apres connexion. */
export const clientGarde: CanActivateFn = (route, state) => {
  const auth = inject(AuthClientService);
  const router = inject(Router);

  const versConnexion = () => {
    try {
      localStorage.setItem(CLE_REDIRECTION, state.url);
    } catch {
      /* stockage indisponible : on ignore */
    }
    return router.createUrlTree(['/connexion']);
  };

  if (!auth.jeton()) {
    return versConnexion();
  }
  if (auth.client()) {
    return true;
  }
  return auth.chargerProfil().pipe(
    map(() => true),
    catchError(() => {
      auth.deconnexion();
      return of(versConnexion());
    }),
  );
};
