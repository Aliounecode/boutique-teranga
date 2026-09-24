import { Routes } from '@angular/router';
import { gardeGerant, gardePersonnel } from '../coeur/gardes/gerant-garde';
import { GestionLayout } from './mise-en-page/gestion-layout';
import { Connexion } from './pages/connexion/connexion';
import { TableauBord } from './pages/tableau-bord/tableau-bord';
import { ProduitsListe } from './pages/produits/produits-liste';
import { ProduitFormulaire } from './pages/produits/produit-formulaire';
import { StockPage } from './pages/stock/stock';
import { CommandesListe } from './pages/commandes/commandes-liste';
import { CommandeDetail } from './pages/commandes/commande-detail';
import { Caisse } from './pages/caisse/caisse';
import { ClientsListe } from './pages/clients/clients-liste';
import { ClientDetail } from './pages/clients/client-detail';
import { Rapports } from './pages/rapports/rapports';
import { Equipe } from './pages/equipe/equipe';

export const routesGestion: Routes = [
  { path: 'connexion', component: Connexion, title: 'Connexion — Gestion' },
  {
    path: '',
    component: GestionLayout,
    canActivate: [gardePersonnel],
    children: [
      {
        path: '',
        component: TableauBord,
        canActivate: [gardeGerant],
        title: 'Tableau de bord — Gestion',
      },
      {
        path: 'produits',
        component: ProduitsListe,
        canActivate: [gardeGerant],
        title: 'Produits — Gestion',
      },
      {
        path: 'produits/nouveau',
        component: ProduitFormulaire,
        canActivate: [gardeGerant],
        title: 'Nouveau produit — Gestion',
      },
      {
        path: 'produits/:id/modifier',
        component: ProduitFormulaire,
        canActivate: [gardeGerant],
        title: 'Modifier un produit — Gestion',
      },
      { path: 'stock', component: StockPage, canActivate: [gardeGerant], title: 'Stock — Gestion' },
      {
        path: 'commandes',
        component: CommandesListe,
        canActivate: [gardeGerant],
        title: 'Commandes — Gestion',
      },
      {
        path: 'commandes/:id',
        component: CommandeDetail,
        canActivate: [gardeGerant],
        title: 'Commande — Gestion',
      },
      { path: 'caisse', component: Caisse, title: 'Caisse — Gestion' },
      { path: 'clients', component: ClientsListe, title: 'Clients — Gestion' },
      { path: 'clients/:id', component: ClientDetail, title: 'Client — Gestion' },
      {
        path: 'rapports',
        component: Rapports,
        canActivate: [gardeGerant],
        title: 'Rapports — Gestion',
      },
      { path: 'equipe', component: Equipe, canActivate: [gardeGerant], title: 'Équipe — Gestion' },
    ],
  },
  { path: '**', redirectTo: '' },
];
