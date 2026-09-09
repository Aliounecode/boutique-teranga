import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';

import { AuthService } from '../services/auth';
import { AuthClientService } from '../services/auth-client';

/**
 * Ajoute l'en-tete Authorization selon la cible :
 *  - endpoints /compte/* et creation de commande (POST /commandes) -> jeton CLIENT ;
 *  - tout le reste (espace gerant) -> jeton PERSONNEL.
 */
export const jetonIntercepteur: HttpInterceptorFn = (requete, suivant) => {
  const estRequeteClient =
    requete.url.includes('/compte') ||
    (requete.method === 'POST' && /\/commandes$/.test(requete.url));

  const jeton = estRequeteClient ? inject(AuthClientService).jeton() : inject(AuthService).jeton();

  if (jeton) {
    requete = requete.clone({ setHeaders: { Authorization: `Bearer ${jeton}` } });
  }
  return suivant(requete);
};
