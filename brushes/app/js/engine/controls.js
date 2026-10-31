// controls.js - the preview's small control panel (stroke, input, pressure, tilt,
// background, seed, compare, size). DOM; it changes the engine's view and the
// engine redraws. The values are remembered per browser (localStorage, optional).

import {el, uid} from '../dom.js';
import {createNotes, NOTE} from './notes.js';

export const VIEW_DEFAULTS = {stroke: 'auto', level: 'heavy', speed: 'medium', pointer: 'pencil', tilt: 0, bg: 'dark', compare: false, tall: false, seed: 1, sizeSource: 'preview'};
const STORE = 'rosw.brushes.engine.view.v1';

const STROKES = [['auto', 'Auto (a stamp brush shows one stamp)'], ['s-curve', 'S-curve (Procreate’s thumbnail path)'], ['line', 'Line'], ['scribble', 'Scribble'],
  ['tap', 'Tap'], ['drawn', 'Drawn (draw on the preview)']];

export function loadView() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORE) || 'null');
    if (saved && typeof saved === 'object') {
      const out = {...VIEW_DEFAULTS};
      for (const key of Object.keys(VIEW_DEFAULTS)) if (typeof saved[key] === typeof VIEW_DEFAULTS[key]) out[key] = saved[key];
      if (out.stroke === 'drawn') out.stroke = 'auto';                      // the drawn samples are not saved
      return out;
    }
  } catch (_) { /* no storage: the defaults */ }
  return {...VIEW_DEFAULTS};
}

export function saveView(view) {
  try { localStorage.setItem(STORE, JSON.stringify(view)); } catch (_) { /* private window: nothing remembered */ }
}

/**
 * createControls({view, onChange(partial), backgrounds}) -> {el, sync(view), setStatus(text)}
 * onChange receives only what the user changed.
 */
export function createControls({view, onChange, backgrounds}) {
  const labelled = (text, control) => { control.id = control.id || uid('eng'); return el('div', {class: 'field'}, el('label', {htmlFor: control.id, text}), control); };
  const select = (name, options, value, key, convert = (v) => v) => {
    const node = el('select', {class: 'select', 'aria-label': name, onchange: (e) => onChange({[key]: convert(e.target.value)})},
      options.map(([v, t]) => el('option', {value: v, text: t})));
    node.value = String(value);
    return node;
  };

  const stroke = select('Stroke', STROKES, view.stroke, 'stroke');
  const pointer = select('Input', [['pencil', 'Apple Pencil (pressure, tilt)'], ['touch', 'Finger (no pressure)']], view.pointer, 'pointer');
  const level = select('Pressure', [['light', 'Light'], ['medium', 'Medium'], ['heavy', 'Full (like the thumbnails)']], view.level, 'level');
  const speed = select('Speed', [['slow', 'Slow'], ['medium', 'Medium'], ['fast', 'Fast']], view.speed, 'speed');
  const tilt = el('input', {type: 'range', min: 0, max: 1, step: 0.05, value: view.tilt, 'aria-label': 'Simulated pen tilt', oninput: (e) => onChange({tilt: Number(e.target.value)})});
  const bg = select('Background', Object.entries(backgrounds).map(([k, v]) => [k, v.label]), view.bg, 'bg');
  const size = select('Size from', [['preview', 'Preview size (like the thumbnail)'], ['paint', 'Paint size']], view.sizeSource, 'sizeSource');
  const seed = el('input', {type: 'number', class: 'num', min: 0, max: 99999, step: 1, value: view.seed, 'aria-label': 'Random seed',
    onchange: (e) => onChange({seed: Math.max(0, Math.min(99999, Math.round(Number(e.target.value) || 0)))})});
  const reseed = el('button', {class: 'btn btn-small', type: 'button', text: 'New seed', onclick: () => onChange({seed: 1 + Math.floor(Math.random() * 99998)})});
  const compare = el('input', {type: 'checkbox', checked: view.compare, onchange: (e) => onChange({compare: e.target.checked})});
  const tall = el('input', {type: 'checkbox', checked: view.tall, onchange: (e) => onChange({tall: e.target.checked})});
  const status = el('p', {class: 'small muted engine-status', role: 'status'});

  const root = el('div', {class: 'engine-controls'},
    el('details', {class: 'engine-options'},
      el('summary', {class: 'small', text: 'Preview options'}),
      el('div', {class: 'engine-grid'},
        labelled('Stroke', stroke), labelled('Input', pointer), labelled('Pressure', level), labelled('Speed', speed), labelled('Tilt', tilt),
        labelled('Background', bg), labelled('Size from', size),
        el('div', {class: 'field'}, el('label', {htmlFor: seed.id || (seed.id = uid('eng')), text: 'Seed'}), el('div', {class: 'btn-row'}, seed, reseed))),
      el('label', {class: 'check'}, compare, el('span', {text: 'Show Procreate’s own thumbnail below'})),
      el('label', {class: 'check'}, tall, el('span', {text: 'Taller preview'}))),
    status,
    el('p', {class: 'small muted engine-approx', text: NOTE}),
    createNotes());

  return {
    el: root,
    sync(next) {
      stroke.value = next.stroke; pointer.value = next.pointer; level.value = next.level; speed.value = next.speed; tilt.value = String(next.tilt);
      bg.value = next.bg; size.value = next.sizeSource; seed.value = String(next.seed); compare.checked = next.compare; tall.checked = next.tall;
      tilt.disabled = next.pointer !== 'pencil'; level.disabled = next.pointer !== 'pencil';
    },
    setStatus(text) { status.textContent = text; },
  };
}
