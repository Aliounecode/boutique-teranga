import { Pipe, PipeTransform } from '@angular/core';

/** Formate un montant (chaîne ou nombre) en « 45 000 FCFA ». */
@Pipe({ name: 'fcfa' })
export class FcfaPipe implements PipeTransform {
  transform(valeur: string | number | null | undefined): string {
    if (valeur === null || valeur === undefined || valeur === '') {
      return '';
    }
    const nombre = Math.round(Number(valeur));
    if (Number.isNaN(nombre)) {
      return '';
    }
    // Espaces fines/insécables → espace simple pour un rendu homogène.
    const formate = nombre.toLocaleString('fr-FR').replace(/[\u202f\u00a0]/g, ' ');
    return `${formate} FCFA`;
  }
}
