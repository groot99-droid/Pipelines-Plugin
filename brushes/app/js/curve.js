// curve.js - the pressure-curve editor.
//
// A curve is a list of on-curve points, stored in the file as
// {"points": ["{0.250000, 0.330000}", ...]} (F3 "JSON value forms"). The editor
// works on [x, y] pairs sorted by x and hands back the value the server expects
// (schema.curveValue: end points first, the others after). How Procreate draws
// the curve between the points is not known; the line drawn here is a monotone
// cubic through them (a guess, labelled as such in the UI).
//
// Mouse, touch and pen: pointer events on the canvas. Keyboard: the canvas is
// focusable; the points table below it is the fully accessible alternative.

import {el, uid} from './dom.js';
import {curvePairs, curveValue, clamp01, trim} from './schema.js';

export const MAX_POINTS = 24;                  // the codec allows 64; a pressure curve needs far fewer
const MIN_GAP = 0.002;

export const CURVE_PRESETS = [
  {name: 'Linear', points: [[0, 0], [1, 1]]},
  {name: 'Ease in', points: [[0, 0], [0.5, 0.25], [1, 1]]},
  {name: 'Ease out', points: [[0, 0], [0.5, 0.75], [1, 1]]},
  {name: 'S curve', points: [[0, 0], [0.25, 0.1], [0.75, 0.9], [1, 1]]},
];

/** Monotone cubic (Fritsch-Carlson) through sorted points: y at x. Flat outside the end points. */
export function monotoneAt(points, x) {
  const n = points.length;
  if (n === 0) return 0;
  if (n === 1 || x <= points[0][0]) return points[0][1];
  if (x >= points[n - 1][0]) return points[n - 1][1];
  const dx = []; const slope = [];
  for (let i = 0; i < n - 1; i += 1) {
    dx.push(points[i + 1][0] - points[i][0]);
    slope.push((points[i + 1][1] - points[i][1]) / (dx[i] || 1e-9));
  }
  const tangent = [slope[0]];
  for (let i = 1; i < n - 1; i += 1) tangent.push(slope[i - 1] * slope[i] <= 0 ? 0 : (slope[i - 1] + slope[i]) / 2);
  tangent.push(slope[n - 2]);
  for (let i = 0; i < n - 1; i += 1) {
    if (slope[i] === 0) { tangent[i] = 0; tangent[i + 1] = 0; continue; }
    const a = tangent[i] / slope[i]; const b = tangent[i + 1] / slope[i];
    const h = Math.hypot(a, b);
    if (h > 3) { tangent[i] = (3 * a / h) * slope[i]; tangent[i + 1] = (3 * b / h) * slope[i]; }
  }
  let i = 0;
  while (i < n - 2 && x > points[i + 1][0]) i += 1;
  const t = (x - points[i][0]) / dx[i];
  const t2 = t * t; const t3 = t2 * t;
  return (2 * t3 - 3 * t2 + 1) * points[i][1] + (t3 - 2 * t2 + t) * dx[i] * tangent[i]
    + (-2 * t3 + 3 * t2) * points[i + 1][1] + (t3 - t2) * dx[i] * tangent[i + 1];
}

/** Pure editing steps on sorted pairs; each returns new pairs (and the new selected index). */
export function addPoint(pairs, x, y) {
  if (pairs.length >= MAX_POINTS) return {pairs, selected: -1};
  const next = [...pairs, [clamp01(x), clamp01(y)]].sort((a, b) => a[0] - b[0]);
  const selected = next.findIndex((p) => p[0] === clamp01(x) && p[1] === clamp01(y));
  return {pairs: next, selected};
}

export function removePoint(pairs, i) {
  if (pairs.length <= 2 || i < 0 || i >= pairs.length) return {pairs, selected: i};
  const next = pairs.filter((_, k) => k !== i);
  return {pairs: next, selected: Math.min(i, next.length - 1)};
}

export function movePoint(pairs, i, x, y) {
  const lo = i > 0 ? pairs[i - 1][0] + MIN_GAP : 0;
  const hi = i < pairs.length - 1 ? pairs[i + 1][0] - MIN_GAP : 1;
  const next = pairs.map((p) => [p[0], p[1]]);
  next[i] = [Math.min(hi, Math.max(lo, x)), clamp01(y)];
  return next;
}

export function createCurveEditor({label, onChange, onCommit, id = uid('curve'), size = 240}) {
  const state = {pairs: [[0, 0], [1, 1]], selected: 0, editable: true, drag: false};
  const dpr = Math.min(2, window.devicePixelRatio || 1);
  const canvas = el('canvas', {class: 'curve-canvas', width: Math.round(size * dpr), height: Math.round(size * dpr),
    tabIndex: 0, role: 'application', 'aria-roledescription': 'curve editor', 'aria-label': `${label}. Arrow keys select and move points.`});
  canvas.style.setProperty('--curve-size', `${size}px`);
  const status = el('p', {class: 'curve-status', 'aria-live': 'polite'});
  const table = el('div', {class: 'curve-table'});
  const presets = el('div', {class: 'btn-row'});
  const details = el('details', {class: 'curve-details'}, el('summary', {text: 'Points table and presets'}), presets, table);
  const root = el('div', {class: 'curve', id}, canvas, status, details);

  function emit(commit) {
    const value = curveValue(state.pairs);
    onChange(value);
    if (commit && onCommit) onCommit();
  }

  function colours() {
    const cs = getComputedStyle(canvas);
    const get = (name, fallback) => cs.getPropertyValue(name).trim() || fallback;
    return {text: get('--text', '#222'), line: get('--line', '#ccc'), accent: get('--accent', '#a50'), surface: get('--surface-2', '#eee')};
  }

  function toPx(x, y) {
    const pad = 16 * dpr; const w = canvas.width - 2 * pad;
    return [pad + x * w, canvas.height - pad - y * w];
  }
  function fromPx(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const w = (rect.width - 32) || 1;
    return [clamp01((clientX - rect.left - 16) / w), clamp01((rect.bottom - 16 - clientY) / w)];
  }

  function draw() {
    const g = canvas.getContext('2d');
    const c = colours();
    g.clearRect(0, 0, canvas.width, canvas.height);
    g.fillStyle = c.surface; g.fillRect(0, 0, canvas.width, canvas.height);
    g.strokeStyle = c.line; g.lineWidth = dpr;
    for (let k = 0; k <= 4; k += 1) {
      const [x0, y0] = toPx(k / 4, 0); const [x1, y1] = toPx(k / 4, 1);
      g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
      const [a0, b0] = toPx(0, k / 4); const [a1, b1] = toPx(1, k / 4);
      g.beginPath(); g.moveTo(a0, b0); g.lineTo(a1, b1); g.stroke();
    }
    g.setLineDash([4 * dpr, 4 * dpr]);
    const [lx0, ly0] = toPx(0, 0); const [lx1, ly1] = toPx(1, 1);
    g.beginPath(); g.moveTo(lx0, ly0); g.lineTo(lx1, ly1); g.stroke();
    g.setLineDash([]);
    g.strokeStyle = state.editable ? c.accent : c.text; g.lineWidth = 2.5 * dpr;
    g.beginPath();
    const first = state.pairs[0][0]; const last = state.pairs[state.pairs.length - 1][0];
    for (let s = 0; s <= 96; s += 1) {
      const x = first + (last - first) * (s / 96);
      const [px, py] = toPx(x, monotoneAt(state.pairs, x));
      if (s === 0) g.moveTo(px, py); else g.lineTo(px, py);
    }
    g.stroke();
    state.pairs.forEach((p, i) => {
      const [px, py] = toPx(p[0], p[1]);
      g.beginPath(); g.arc(px, py, (i === state.selected ? 7 : 5) * dpr, 0, Math.PI * 2);
      g.fillStyle = i === state.selected ? c.accent : c.surface; g.fill();
      g.strokeStyle = state.editable ? c.accent : c.text; g.lineWidth = 2 * dpr; g.stroke();
    });
  }

  function describe() {
    const p = state.pairs[state.selected];
    status.textContent = p ? `Point ${state.selected + 1} of ${state.pairs.length}: input ${trim(p[0], 3)}, output ${trim(p[1], 3)}.` : '';
  }

  function rebuildTable() {
    table.replaceChildren(...state.pairs.map((p, i) => {
      const num = (value, which) => el('input', {type: 'number', min: 0, max: 1, step: 0.01, value: trim(value, 4), disabled: !state.editable,
        'aria-label': `${label}, point ${i + 1}, ${which === 0 ? 'input' : 'output'}`,
        onchange: (e) => {
          const v = Number(e.target.value);
          if (!Number.isFinite(v)) { e.target.value = trim(p[which], 4); return; }
          state.pairs = which === 0 ? movePoint(state.pairs, i, v, p[1]) : movePoint(state.pairs, i, p[0], v);
          state.selected = i; refresh(); emit(true);
        }});
      return el('div', {class: 'curve-point'}, el('span', {class: 'muted', text: `${i + 1}`}), num(p[0], 0), num(p[1], 1),
        el('button', {class: 'btn btn-small', type: 'button', text: 'Remove', disabled: !state.editable || state.pairs.length <= 2,
          'aria-label': `Remove point ${i + 1}`,
          onclick: () => { ({pairs: state.pairs, selected: state.selected} = removePoint(state.pairs, i)); refresh(); emit(true); }}));
    }));
    presets.replaceChildren(
      ...CURVE_PRESETS.map((preset) => el('button', {class: 'btn btn-small', type: 'button', text: preset.name, disabled: !state.editable,
        onclick: () => { state.pairs = preset.points.map((p) => [...p]); state.selected = 0; refresh(); emit(true); }})),
      el('button', {class: 'btn btn-small', type: 'button', text: 'Add point', disabled: !state.editable || state.pairs.length >= MAX_POINTS,
        onclick: () => { addMid(); }}));
  }

  function addMid() {
    const i = Math.min(Math.max(state.selected, 0), state.pairs.length - 2);
    const a = state.pairs[i]; const b = state.pairs[i + 1];
    ({pairs: state.pairs, selected: state.selected} = addPoint(state.pairs, (a[0] + b[0]) / 2, monotoneAt(state.pairs, (a[0] + b[0]) / 2)));
    refresh(); emit(true);
  }

  function refresh() { draw(); describe(); rebuildTable(); }

  function nearest(clientX, clientY) {
    const rect = canvas.getBoundingClientRect();
    const w = rect.width - 32;
    let best = -1; let bestDistance = 24;
    state.pairs.forEach((p, i) => {
      const d = Math.hypot(rect.left + 16 + p[0] * w - clientX, rect.bottom - 16 - p[1] * w - clientY);
      if (d < bestDistance) { best = i; bestDistance = d; }
    });
    return best;
  }

  canvas.addEventListener('pointerdown', (event) => {
    if (!state.editable) return;
    canvas.focus();
    let i = nearest(event.clientX, event.clientY);
    if (i < 0) {
      const [x, y] = fromPx(event.clientX, event.clientY);
      const added = addPoint(state.pairs, x, y);
      if (added.selected < 0) return;
      state.pairs = added.pairs; i = added.selected; rebuildTable();
      emit(false);
    }
    state.selected = i; state.drag = true;
    canvas.setPointerCapture(event.pointerId);
    draw(); describe();
    event.preventDefault();
  });
  canvas.addEventListener('pointermove', (event) => {
    if (!state.drag) return;
    const [x, y] = fromPx(event.clientX, event.clientY);
    state.pairs = movePoint(state.pairs, state.selected, x, y);
    draw(); describe(); emit(false);
  });
  const end = () => { if (state.drag) { state.drag = false; rebuildTable(); emit(true); } };
  canvas.addEventListener('pointerup', end);
  canvas.addEventListener('pointercancel', end);
  canvas.addEventListener('dblclick', (event) => {
    if (!state.editable) return;
    const i = nearest(event.clientX, event.clientY);
    if (i >= 0 && state.pairs.length > 2) { ({pairs: state.pairs, selected: state.selected} = removePoint(state.pairs, i)); refresh(); emit(true); }
  });
  canvas.addEventListener('keydown', (event) => {
    const i = state.selected;
    const fine = event.shiftKey ? 0.05 : 0.01;
    let handled = true;
    if (event.key === 'ArrowLeft' && !event.altKey) state.selected = Math.max(0, i - 1);
    else if (event.key === 'ArrowRight' && !event.altKey) state.selected = Math.min(state.pairs.length - 1, i + 1);
    else if (!state.editable) handled = false;
    else if (event.key === 'ArrowUp') { state.pairs = movePoint(state.pairs, i, state.pairs[i][0], state.pairs[i][1] + fine); emit(true); }
    else if (event.key === 'ArrowDown') { state.pairs = movePoint(state.pairs, i, state.pairs[i][0], state.pairs[i][1] - fine); emit(true); }
    else if (event.key === 'ArrowLeft' && event.altKey) { state.pairs = movePoint(state.pairs, i, state.pairs[i][0] - fine, state.pairs[i][1]); emit(true); }
    else if (event.key === 'ArrowRight' && event.altKey) { state.pairs = movePoint(state.pairs, i, state.pairs[i][0] + fine, state.pairs[i][1]); emit(true); }
    else if (event.key === 'Enter') { addMid(); return event.preventDefault(); }
    else if (event.key === 'Delete' || event.key === 'Backspace') { ({pairs: state.pairs, selected: state.selected} = removePoint(state.pairs, i)); emit(true); }
    else handled = false;
    if (handled) { event.preventDefault(); refresh(); }
  });
  const scheme = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  if (scheme && scheme.addEventListener) scheme.addEventListener('change', draw);

  refresh();
  // the canvas is drawn before it is in the page (no colours yet): draw again once it has a size
  if (typeof ResizeObserver === 'function') new ResizeObserver(() => draw()).observe(canvas);

  return {
    el: root,
    /** Show a curve value (from the doc). Does not call onChange. */
    setValue(value) {
      const pairs = curvePairs(value);
      if (!pairs || pairs.length < 2) return;
      if (state.drag) return;
      state.pairs = [...pairs].sort((a, b) => a[0] - b[0]);
      state.selected = Math.min(state.selected, state.pairs.length - 1);
      refresh();
    },
    setEditable(flag) { state.editable = !!flag; canvas.classList.toggle('is-locked', !flag); refresh(); },
    canvas,
  };
}
