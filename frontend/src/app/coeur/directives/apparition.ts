import { Directive, ElementRef, inject, input, OnDestroy, OnInit } from '@angular/core';

/**
 * Revele un element quand il entre dans le viewport (fondu + leger glissement).
 * Usage : <div apparition> ou <div apparition [delai]="120">
 */
@Directive({
  selector: '[apparition]',
  host: { class: 'app-apparition' },
})
export class Apparition implements OnInit, OnDestroy {
  /** Retard avant l'animation, en millisecondes (pour les cascades). */
  readonly delai = input(0);

  private readonly element = inject(ElementRef<HTMLElement>);
  private observateur?: IntersectionObserver;

  ngOnInit(): void {
    const noeud = this.element.nativeElement as HTMLElement;
    noeud.style.transitionDelay = `${this.delai()}ms`;

    // Respecte la preference systeme « animations reduites ».
    const reduit = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
    if (reduit || typeof IntersectionObserver === 'undefined') {
      noeud.classList.add('est-visible');
      return;
    }

    this.observateur = new IntersectionObserver(
      (entrees) => {
        for (const entree of entrees) {
          if (entree.isIntersecting) {
            noeud.classList.add('est-visible');
            this.observateur?.unobserve(noeud); // une seule fois
          }
        }
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' },
    );
    this.observateur.observe(noeud);
  }

  ngOnDestroy(): void {
    this.observateur?.disconnect();
  }
}
