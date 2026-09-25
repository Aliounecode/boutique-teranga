import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Entete } from './entete/entete';
import { Pied } from './pied/pied';
import { BoutonWhatsapp } from './bouton-whatsapp';

@Component({
  selector: 'bq-layout',
  imports: [RouterOutlet, Entete, Pied, BoutonWhatsapp],
  template: `
    <bq-entete />
    <main><router-outlet /></main>
    <bq-pied />
    <bq-bouton-whatsapp />
  `,
})
export class BoutiqueLayout {}
