import { Routes } from '@angular/router';
import { BoutiqueLayout } from './mise-en-page/boutique-layout';
import { Accueil } from './pages/accueil/accueil';
import { Catalogue } from './pages/catalogue/catalogue';
import { ProduitDetail } from './pages/produit-detail/produit-detail';
import { Panier } from './pages/panier/panier';
import { Commande } from './pages/commande/commande';
import { Inscription } from './pages/compte/inscription';
import { ConnexionClient } from './pages/compte/connexion';
import { VerifierEmail } from './pages/compte/verifier-email';
import { MonCompte } from './pages/compte/mon-compte';
import { clientGarde } from '../coeur/gardes/client-garde';
import { MotDePasseOublie } from './pages/compte/mot-de-passe-oublie';
import { ReinitialiserMotDePasse } from './pages/compte/reinitialiser-mot-de-passe';

export const routesBoutique: Routes = [
  {
    path: '',
    component: BoutiqueLayout,
    children: [
      { path: '', component: Accueil, title: 'Pape Alé et Bamba — Sacs & Chaussures' },
      { path: 'catalogue', component: Catalogue, title: 'Catalogue — Pape Alé et Bamba' },
      { path: 'produit/:id', component: ProduitDetail, title: 'Produit — Pape Alé et Bamba' },
      { path: 'panier', component: Panier, title: 'Mon panier — Pape Alé et Bamba' },
      {
        path: 'commande',
        component: Commande,
        canActivate: [clientGarde],
        title: 'Ma commande — Pape Ale et Bamba',
      },
      { path: 'inscription', component: Inscription, title: 'Créer un compte — Pape Alé et Bamba' },
      { path: 'connexion', component: ConnexionClient, title: 'Connexion — Pape Alé et Bamba' },
      {
        path: 'verifier-email',
        component: VerifierEmail,
        title: 'Vérification — Pape Alé et Bamba',
      },
      {
        path: 'mot-de-passe-oublie',
        component: MotDePasseOublie,
        title: 'Mot de passe oublié — Pape Alé et Bamba',
      },
      {
        path: 'reinitialiser-mot-de-passe',
        component: ReinitialiserMotDePasse,
        title: 'Nouveau mot de passe — Pape Alé et Bamba',
      },
      {
        path: 'mon-compte',
        component: MonCompte,
        canActivate: [clientGarde],
        title: 'Mon compte — Pape Alé et Bamba',
      },
    ],
  },
];
