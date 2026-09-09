import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'gestion',
    loadChildren: () => import('./gestion/gestion.routes').then((m) => m.routesGestion),
  },
  {
    path: '',
    loadChildren: () => import('./boutique/boutique.routes').then((m) => m.routesBoutique),
  },
  { path: '**', redirectTo: '' },
];
