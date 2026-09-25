import { Component, signal } from '@angular/core';

@Component({
  selector: 'bq-bouton-whatsapp',
  template: `
    class="wa" [class.visible]="visible()" [href]="lien" target="_blank" rel="noopener"
    aria-label="Nous contacter sur WhatsApp"
    <a>
      <svg width="27" height="27" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path
          d="M17.47 14.38c-.3-.15-1.75-.86-2.02-.96-.27-.1-.47-.15-.67.15-.2.3-.77.96-.94 1.16-.17.2-.35.22-.64.07-.3-.15-1.25-.46-2.38-1.47-.88-.78-1.47-1.75-1.64-2.05-.17-.3-.02-.46.13-.6.13-.13.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.08-.15-.67-1.6-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.22 3.08.15.2 2.1 3.2 5.08 4.49.71.3 1.26.49 1.69.63.71.22 1.36.19 1.87.12.57-.09 1.75-.72 2-1.41.25-.69.25-1.28.17-1.41-.07-.13-.27-.2-.57-.35z"
        />
        <path
          d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.45 1.32 4.95L2 22l5.25-1.38a9.87 9.87 0 0 0 4.79 1.22h.01c5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.84 9.84 0 0 0 12.04 2zm0 18.15h-.01a8.2 8.2 0 0 1-4.18-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.17 8.17 0 0 1-1.25-4.38c0-4.53 3.7-8.23 8.24-8.23a8.2 8.2 0 0 1 8.23 8.24c0 4.54-3.7 8.23-8.24 8.23z"
        />
      </svg>
    </a>
  `,
  styles: [
    `
      .wa {
        position: fixed;
        right: 20px;
        bottom: 20px;
        z-index: 90;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: #25d366;
        color: #fff;
        display: grid;
        place-items: center;
        box-shadow: 0 8px 24px rgba(37, 211, 102, 0.38);
        opacity: 0;
        transform: translateY(16px) scale(0.85);
        transition:
          opacity 0.45s cubic-bezier(0.22, 1, 0.36, 1),
          transform 0.45s cubic-bezier(0.22, 1, 0.36, 1),
          box-shadow 0.3s ease;
      }
      .wa.visible {
        opacity: 1;
        transform: none;
      }
      .wa:hover {
        box-shadow: 0 12px 30px rgba(37, 211, 102, 0.5);
        transform: translateY(-3px);
      }
      .wa::after {
        content: '';
        position: absolute;
        inset: 0;
        border-radius: 50%;
        border: 2px solid #25d366;
        opacity: 0.55;
        animation: onde 2.4s ease-out infinite;
      }
      @keyframes onde {
        0% {
          transform: scale(1);
          opacity: 0.55;
        }
        70%,
        100% {
          transform: scale(1.55);
          opacity: 0;
        }
      }
      @media (max-width: 520px) {
        .wa {
          right: 16px;
          bottom: 16px;
          width: 52px;
          height: 52px;
        }
      }
      @media (prefers-reduced-motion: reduce) {
        .wa,
        .wa::after {
          animation: none;
          transition: none;
          opacity: 1;
          transform: none;
        }
      }
    `,
  ],
})
export class BoutonWhatsapp {
  private readonly numero = '221774715257'; // +221 77 471 52 57
  private readonly message = encodeURIComponent(
    'Bonjour, je vous écris depuis votre boutique en ligne.',
  );
  readonly lien = `https://wa.me/${this.numero}?text=${this.message}`;

  readonly visible = signal(false);

  constructor() {
    // Petite apparition différée, pour ne pas surgir pendant le chargement.
    setTimeout(() => this.visible.set(true), 900);
  }
}
