// Types reflétant les réponses de l'API backend.
// Note : les montants (Decimal côté API) sont sérialisés en CHAÎNE (ex. "45000.00").

export type StatutProduit = 'disponible' | 'bientot_disponible';
export type MoyenPaiement = 'especes' | 'wave' | 'orange_money' | 'free_money' | 'carte' | 'autre';
export type StatutVente = 'validee' | 'annulee';
export type StatutCommande = 'nouvelle' | 'validee' | 'refusee' | 'annulee';
export type TriProduits = 'recent' | 'prix_asc' | 'prix_desc' | 'nom';

export interface CategorieArbre {
  id: number;
  nom: string;
  slug: string;
  description: string | null;
  actif: boolean;
  sous_categories: CategorieArbre[];
}

export interface Categorie {
  id: number;
  nom: string;
  slug: string;
  description: string | null;
  parent_id: number | null;
  actif: boolean;
  date_creation: string;
}

export interface Photo {
  id: number;
  url: string;
  ordre: number;
  est_principale: boolean;
}

export interface Variante {
  id: number;
  produit_id: number;
  couleur: string | null;
  taille: string | null;
  reference_variante: string | null;
  quantite_disponible: number;
  stock_minimum: number;
  actif: boolean;
  en_rupture: boolean;
  stock_faible: boolean;
}

export interface ProduitResume {
  id: number;
  reference: string;
  nom: string;
  categorie_id: number;
  prix: string;
  prix_promo: string | null;
  en_promotion: boolean;
  statut: StatutProduit;
  actif: boolean;
  photo_principale: string | null;
  quantite_totale: number;
  prix_effectif: string;
  en_rupture: boolean;
  disponible_achat: boolean;
}

export interface Produit {
  id: number;
  reference: string;
  nom: string;
  description: string | null;
  categorie_id: number;
  prix: string;
  prix_promo: string | null;
  en_promotion: boolean;
  a_tailles: boolean;
  statut: StatutProduit;
  actif: boolean;
  date_creation: string;
  date_modification: string;
  categorie: Categorie;
  variantes: Variante[];
  photos: Photo[];
  prix_effectif: string;
  quantite_totale: number;
  en_rupture: boolean;
  disponible_achat: boolean;
}

export interface PageProduits {
  total: number;
  page: number;
  taille_page: number;
  elements: ProduitResume[];
}

export interface FiltresProduits {
  recherche?: string;
  categorie_id?: number;
  prix_min?: number;
  prix_max?: number;
  couleur?: string;
  taille?: string;
  en_stock?: boolean;
  en_promotion?: boolean;
  tri?: TriProduits;
  page?: number;
  taille_page?: number;
}

export interface Jeton {
  access_token: string;
  token_type: string;
}

export interface Role {
  id: number;
  nom: string;
  description: string | null;
}

export interface Utilisateur {
  id: number;
  nom: string;
  prenom: string;
  nom_utilisateur: string;
  email: string | null;
  telephone: string | null;
  actif: boolean;
  role: Role;
  date_creation: string;
}

// ----- Commandes en ligne -----
export interface LigneCommandeEntree {
  variante_id: number;
  quantite: number;
}

export interface CommandeCreation {
  client_nom: string;
  client_prenom?: string;
  client_telephone: string;
  moyen_paiement: MoyenPaiement;
  notes?: string;
  lignes: LigneCommandeEntree[];
}

export interface LigneCommandeLecture {
  id: number;
  variante_id: number;
  produit_nom: string;
  couleur: string | null;
  taille: string | null;
  prix_unitaire: string;
  quantite: number;
  sous_total: string;
}

export interface CommandeLecture {
  id: number;
  numero: string;
  client_nom: string;
  client_prenom: string | null;
  client_telephone: string;
  moyen_paiement: MoyenPaiement;
  montant_total: string;
  statut: StatutCommande;
  notes: string | null;
  utilisateur_id: number | null;
  date_commande: string;
  lignes: LigneCommandeLecture[];
}

// ----- Tableau de bord -----
export interface MontantParMoyen {
  moyen: MoyenPaiement;
  montant: string;
  nombre: number;
}

export interface ResumeTableauBord {
  date_debut: string;
  date_fin: string;
  chiffre_affaires: string;
  total_ventes_physiques: string;
  nombre_ventes_physiques: number;
  total_ventes_en_ligne: string;
  nombre_commandes_validees: number;
  nombre_articles_vendus: number;
  remboursements: string;
  commandes_en_attente: number;
  commandes_annulees: number;
  paiements_par_moyen: MontantParMoyen[];
}

export interface TopProduit {
  produit_id: number;
  produit_nom: string;
  quantite_vendue: number;
  montant: string;
}

export interface TopCategorie {
  categorie_id: number;
  categorie_nom: string;
  quantite_vendue: number;
  montant: string;
}

export interface PointPeriode {
  periode: string;
  montant: string;
  nombre: number;
}

export interface VentesPeriodiques {
  granularite: string;
  points: PointPeriode[];
}

export const LIBELLES_MOYEN: Record<MoyenPaiement, string> = {
  especes: 'Espèces',
  wave: 'Wave',
  orange_money: 'Orange Money',
  free_money: 'Free Money',
  carte: 'Carte bancaire',
  autre: 'Autre',
};

// ----- Gestion des produits (payloads) -----
export interface VarianteCreation {
  couleur?: string;
  taille?: string;
  quantite_disponible: number;
  stock_minimum: number;
}

export interface ProduitCreation {
  nom: string;
  description?: string;
  categorie_id: number;
  prix: number;
  prix_promo?: number;
  en_promotion: boolean;
  a_tailles: boolean;
  statut: StatutProduit;
  reference?: string;
  variantes: VarianteCreation[];
}

export interface ProduitMiseAJour {
  nom?: string;
  description?: string | null;
  categorie_id?: number;
  prix?: number;
  prix_promo?: number | null;
  en_promotion?: boolean;
  a_tailles?: boolean;
  statut?: StatutProduit;
  actif?: boolean;
}

// ----- Stock -----
export type TypeMouvementStock =
  | 'vente'
  | 'reapprovisionnement'
  | 'retour'
  | 'correction'
  | 'perte';

export interface AlerteStock {
  variante_id: number;
  produit_id: number;
  produit_nom: string;
  reference_variante: string | null;
  couleur: string | null;
  taille: string | null;
  quantite_disponible: number;
  stock_minimum: number;
  en_rupture: boolean;
  stock_faible: boolean;
}

export interface MouvementLecture {
  id: number;
  date_mouvement: string;
  type_mouvement: TypeMouvementStock;
  quantite: number;
  quantite_avant: number;
  quantite_apres: number;
  motif: string | null;
  reference_document: string | null;
  variante_id: number;
  produit_id: number;
  produit_nom: string;
  reference_variante: string | null;
  couleur: string | null;
  taille: string | null;
  utilisateur_id: number | null;
}

export interface MouvementPage {
  total: number;
  page: number;
  taille_page: number;
  elements: MouvementLecture[];
}

export const LIBELLES_MOUVEMENT: Record<TypeMouvementStock, string> = {
  vente: 'Vente',
  reapprovisionnement: 'Réappro.',
  retour: 'Retour',
  correction: 'Correction',
  perte: 'Perte',
};

// ----- Commandes (gestion) -----
export interface CommandeResume {
  id: number;
  numero: string;
  date_commande: string;
  client_nom: string;
  client_telephone: string;
  moyen_paiement: MoyenPaiement;
  montant_total: string;
  statut: StatutCommande;
  nombre_articles: number;
}

export interface CommandePage {
  total: number;
  page: number;
  taille_page: number;
  elements: CommandeResume[];
}

export const LIBELLES_COMMANDE: Record<StatutCommande, string> = {
  nouvelle: 'Nouvelle',
  validee: 'Validée',
  refusee: 'Refusée',
  annulee: 'Annulée',
};

// ----- Clients -----
export interface ClientLecture {
  id: number;
  nom: string;
  prenom: string | null;
  telephone: string | null;
  actif: boolean;
  date_creation: string;
}
export interface ClientCreation {
  nom: string;
  prenom?: string;
  telephone?: string;
}
export interface ClientPage {
  total: number;
  page: number;
  taille_page: number;
  elements: ClientLecture[];
}

// ----- Ventes (caisse / POS) -----
export interface LigneVenteEntree {
  variante_id: number;
  quantite: number;
}
export interface VenteCreation {
  client_id?: number;
  notes?: string;
  moyen_paiement: MoyenPaiement;
  reference_paiement?: string;
  lignes: LigneVenteEntree[];
}
export interface LigneVenteLecture {
  id: number;
  variante_id: number;
  produit_nom: string;
  couleur: string | null;
  taille: string | null;
  prix_unitaire: string;
  quantite: number;
  sous_total: string;
}
export interface PaiementLecture {
  id: number;
  montant: string;
  moyen: MoyenPaiement;
  reference_externe: string | null;
  date_paiement: string;
  utilisateur_id: number | null;
}
export interface VenteLecture {
  id: number;
  numero: string;
  client_id: number | null;
  client: ClientLecture | null;
  utilisateur_id: number;
  montant_total: string;
  statut: StatutVente;
  notes: string | null;
  date_vente: string;
  lignes: LigneVenteLecture[];
  paiements: PaiementLecture[];
}

// ----- Clients (gestion, détail) -----
export interface ClientDetailLecture extends ClientLecture {
  nombre_achats: number;
  total_depense: string;
}
export interface ClientMiseAJour {
  nom?: string;
  prenom?: string | null;
  telephone?: string | null;
  actif?: boolean;
}

// ----- Rapport journalier -----
export interface VentesRapport {
  nombre_total: number;
  physiques_nombre: number;
  physiques_montant: string;
  en_ligne_nombre: number;
  en_ligne_montant: string;
  chiffre_affaires: string;
}
export interface PaiementRapport {
  moyen: MoyenPaiement;
  montant: string;
}
export interface CommandesRapport {
  recues: number;
  validees: number;
  refusees: number;
  annulees: number;
}
export interface StockRapport {
  articles_vendus: number;
  reapprovisionnes: number;
  en_rupture: number;
  proches_rupture: number;
}
export interface RapportJournalier {
  date: string;
  ventes: VentesRapport;
  paiements: PaiementRapport[];
  commandes: CommandesRapport;
  stock: StockRapport;
}

// ----- Espace client -----
export interface InscriptionClient {
  nom: string;
  prenom?: string;
  telephone?: string;
  email: string;
  mot_de_passe: string;
}

export interface ClientCompte {
  id: number;
  nom: string;
  prenom: string | null;
  telephone: string | null;
  email: string | null;
  email_verifie: boolean;
  date_creation: string;
}
// ----- Gestion de l'equipe -----
export interface UtilisateurCreation {
  nom: string;
  prenom: string;
  nom_utilisateur: string;
  email?: string;
  telephone?: string;
  mot_de_passe: string;
  role_id: number;
}

export interface UtilisateurMiseAJour {
  nom?: string;
  prenom?: string;
  email?: string | null;
  telephone?: string | null;
  role_id?: number;
  actif?: boolean;
}
// ----- Rapport « mes ventes » (vendeur / gérant) -----
export interface MesVentesLigne {
  numero: string;
  heure: string;
  client: string;
  montant: string;
}

export interface MesVentesPaiement {
  moyen: MoyenPaiement;
  montant: string;
}

export interface MesVentes {
  date: string;
  nombre_ventes: number;
  total_encaisse: string;
  articles_vendus: number;
  ventes: MesVentesLigne[];
  paiements: MesVentesPaiement[];
}
