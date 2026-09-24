import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';

import { AuthService } from '../services/auth';

/**
 * Charge le profil au besoin, puis autorise selon `autorise`.
 * `siRefuse` = page de repli pour un utilisateur connecté mais non autorisé.
 */
function controler(autorise: (auth: AuthService) => boolean, siRefuse: string) {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (!auth.jeton()) {
    return router.createUrlTree(['/gestion/connexion']);
  }
  const decider = () => (autorise(auth) ? true : router.createUrlTree([siRefuse]));

  if (auth.utilisateur()) {
    return decider();
  }
  return auth.chargerProfil().pipe(
    map(() => decider()),
    catchError(() => {
      auth.deconnexion();
      return of(router.createUrlTree(['/gestion/connexion']));
    }),
  );
}

/** Accès à l'espace de gestion : gérant OU vendeur connecté. */
export const gardePersonnel: CanActivateFn = () =>
  controler((a) => a.estGerant() || a.estVendeur(), '/gestion/connexion');

/** Pages réservées au gérant ; un vendeur connecté est renvoyé vers la caisse. */
export const gardeGerant: CanActivateFn = () => controler((a) => a.estGerant(), '/gestion/caisse');
