import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Entete } from './entete/entete';
import { Pied } from './pied/pied';

@Component({
  selector: 'bq-layout',
  imports: [RouterOutlet, Entete, Pied],
  template: `
    <bq-entete />
    <main><router-outlet /></main>
    <bq-pied />
  `,
})
export class BoutiqueLayout {}
