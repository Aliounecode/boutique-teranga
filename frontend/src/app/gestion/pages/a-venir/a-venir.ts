import { Component, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';

@Component({
  selector: 'g-avenir',
  template: `
    <div class="avenir">
      <span class="st">Section</span>
      <h1>{{ titre() }}</h1>
      <p>Cette section arrive à une prochaine étape.</p>
    </div>
  `,
  styles: [`
    .avenir { background: var(--surface); border: 1px solid var(--bordure); padding: 70px 40px; text-align: center; }
    .st { font-size: 0.7rem; letter-spacing: 0.24em; text-transform: uppercase; color: var(--accent); }
    h1 { font-family: var(--serif); font-size: 2.2rem; font-weight: 500; margin: 10px 0 12px; }
    p { color: var(--texte-doux); }
  `],
})
export class AVenir {
  private readonly route = inject(ActivatedRoute);
  readonly titre = toSignal(this.route.data.pipe(map((d) => (d['titre'] as string) ?? 'Section')), {
    initialValue: 'Section',
  });
}
