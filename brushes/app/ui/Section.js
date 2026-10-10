/**
 * Section.js - Collapsible panel section (disclosure)
 *
 * A header button plus a region it owns. `aria-expanded` on the button is the
 * single source of truth for open/closed: CSS follows the attribute, so the
 * visual and the accessibility tree cannot disagree.
 *
 * Open/closed survives a panel switch and a reload — collapsing a section you
 * are not tuning is only useful if it stays collapsed.
 */

const STORE_KEY = 'brushDesigner.sections.v1';

function readStore() {
  try {
    return JSON.parse(localStorage.getItem(STORE_KEY)) || {};
  } catch {
    return {};
  }
}

function writeStore(state) {
  try {
    localStorage.setItem(STORE_KEY, JSON.stringify(state));
  } catch {
    /* private window, quota, storage disabled — the UI still works, it just forgets */
  }
}

let seq = 0;

export class Section {
  /**
   * @param {object}  opts
   * @param {string}  opts.id        stable id, used as the persistence key
   * @param {string}  opts.title     header text
   * @param {string} [opts.hint]     short right-aligned readout in the header
   * @param {boolean}[opts.defaultOpen=true]
   */
  constructor({ id, title, hint = '', defaultOpen = true }) {
    this.id = id;
    this.uid = `sect-${++seq}`;

    const store = readStore();
    const open = Object.prototype.hasOwnProperty.call(store, id) ? !!store[id] : defaultOpen;

    this.el = document.createElement('section');
    this.el.className = 'sect';

    this.header = document.createElement('button');
    this.header.type = 'button';
    this.header.className = 'sect-header';
    this.header.setAttribute('aria-expanded', String(open));
    this.header.setAttribute('aria-controls', this.uid);
    this.header.innerHTML = `
      <span class="sect-marker" aria-hidden="true"></span>
      <span class="sect-title"></span>
      <span class="sect-hint"></span>
    `;
    this.header.querySelector('.sect-title').textContent = title;
    this.header.querySelector('.sect-hint').textContent = hint;

    this.body = document.createElement('div');
    this.body.className = 'sect-body';
    this.body.id = this.uid;
    this.body.hidden = !open;

    this.header.addEventListener('click', () => this.toggle());

    this.el.appendChild(this.header);
    this.el.appendChild(this.body);
  }

  /** Append one or more nodes to the section body. */
  add(...nodes) {
    nodes.filter(Boolean).forEach(n => this.body.appendChild(n));
    return this;
  }

  get open() {
    return this.header.getAttribute('aria-expanded') === 'true';
  }

  setOpen(open, persist = true) {
    this.header.setAttribute('aria-expanded', String(open));
    this.body.hidden = !open;
    if (persist) {
      const store = readStore();
      store[this.id] = open;
      writeStore(store);
    }
  }

  toggle() {
    this.setOpen(!this.open);
  }

  setHint(text) {
    this.header.querySelector('.sect-hint').textContent = text;
  }
}

/**
 * The expand/collapse-all control that sits under a panel title.
 * Reflects the current state rather than blindly toggling: if anything is
 * collapsed the button opens everything, otherwise it closes everything.
 */
export function createSectionToolbar(getSections) {
  const bar = document.createElement('div');
  bar.className = 'sect-toolbar';

  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'sect-toolbar-btn';

  const sync = () => {
    const sections = getSections();
    const anyClosed = sections.some(s => !s.open);
    btn.textContent = anyClosed ? 'Expand all' : 'Collapse all';
    btn.dataset.action = anyClosed ? 'expand' : 'collapse';
  };

  btn.addEventListener('click', () => {
    const open = btn.dataset.action === 'expand';
    getSections().forEach(s => s.setOpen(open));
    sync();
  });

  bar.appendChild(btn);
  bar.sync = sync;
  return bar;
}

export default Section;
