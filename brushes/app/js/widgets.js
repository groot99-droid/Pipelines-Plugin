// widgets.js - one control per schema `ui` kind (F4): slider, number, toggle,
// select, curve, text, readonly.
//
// buildControl(row, spec) -> {el, update(value), setEditable(flag), focus()}
//   spec.id        id for the main control (a <label for> points at it)
//   spec.label     the accessible name
//   spec.onSet(value, {coalesce})   called ONLY on user input; never while
//                  update() redraws the control, so opening a brush edits nothing.
//   spec.onCommit()  the user let go of a slider or curve (ends a history merge)
//   spec.allowUnverified   see schema.widgetFor

import {el} from './dom.js';
import {widgetFor, enumOptions, formatDisplay, rangeInfo, trim, formatValue} from './schema.js';
import {createCurveEditor} from './curve.js';

export function buildControl(row, spec) {
  const kind = widgetFor(row, {allowUnverified: spec.allowUnverified}).kind;
  const builder = {slider: slider, number: numberField, toggle, select, text, curve}[kind] || readonly;
  return builder(row, spec);
}

function slider(row, spec) {
  const range = rangeInfo(row);
  const min = range.min; const max = range.max;
  const step = row.step || (max - min) / 1000 || 0.001;
  const input = el('input', {type: 'range', class: 'range', min, max, step, 'aria-label': `${spec.label} slider`});
  const number = el('input', {type: 'number', class: 'num', id: spec.id, step: 'any', inputMode: 'decimal'});
  const out = el('output', {class: 'range-out', 'aria-hidden': 'true'});
  const band = el('div', {class: 'range-band', 'aria-hidden': 'true'});
  if (range.obsMin !== null && max > min) {
    const pct = (v) => `${Math.max(0, Math.min(100, ((v - min) / (max - min)) * 100))}%`;
    band.style.setProperty('--from', pct(range.obsMin));
    band.style.setProperty('--to', pct(range.obsMax));
  } else band.hidden = true;
  const track = el('div', {class: 'range-track'}, band, input);
  const root = el('div', {class: 'slider'}, track, number, row.display !== 'raw' ? out : null);
  let shown = null;

  input.addEventListener('input', () => spec.onSet(Number(input.value), {coalesce: true}));
  input.addEventListener('change', () => spec.onCommit && spec.onCommit());
  number.addEventListener('change', () => {
    const v = Number(number.value);
    if (number.value.trim() === '' || !Number.isFinite(v)) { number.value = shown === null ? '' : trim(shown, 6); return; }
    spec.onSet(v, {coalesce: false});
  });

  return {
    el: root,
    update(value) {
      shown = typeof value === 'number' ? value : null;
      if (shown === null) { number.value = ''; out.textContent = ''; return; }
      if (document.activeElement !== number) number.value = trim(shown, 6);
      input.value = String(Math.min(max, Math.max(min, shown)));
      out.textContent = formatDisplay(row, shown);
      root.classList.toggle('is-outside', shown < min || shown > max);
    },
    setEditable(flag) { input.disabled = !flag; number.disabled = !flag; },
    focus() { number.focus(); },
  };
}

function numberField(row, spec) {
  const input = el('input', {type: 'number', class: 'num', id: spec.id, step: row.type === 'int' ? 1 : (row.step || 'any')});
  input.addEventListener('change', () => {
    const v = Number(input.value);
    if (input.value.trim() === '' || !Number.isFinite(v)) { return; }
    spec.onSet(row.type === 'int' ? Math.round(v) : v, {coalesce: false});
  });
  return {
    el: el('div', {class: 'slider'}, input),
    update(value) { input.value = typeof value === 'number' ? trim(value, 6) : ''; },
    setEditable(flag) { input.disabled = !flag; },
    focus() { input.focus(); },
  };
}

function toggle(row, spec) {
  const input = el('input', {type: 'checkbox', role: 'switch', class: 'switch', id: spec.id});
  const text = el('span', {class: 'switch-text'});
  input.addEventListener('change', () => spec.onSet(input.checked, {coalesce: false}));
  return {
    el: el('div', {class: 'toggle'}, input, text),
    update(value) { input.checked = value === true; text.textContent = value === true ? 'On' : 'Off'; },
    setEditable(flag) { input.disabled = !flag; },
    focus() { input.focus(); },
  };
}

function select(row, spec) {
  const options = enumOptions(row);
  const input = el('select', {class: 'select', id: spec.id});
  const fill = () => options.forEach((o) => input.append(el('option', {value: String(o.value), text: o.verified ? o.label : `${o.label}`})));
  fill();
  input.addEventListener('change', () => spec.onSet(Number(input.value), {coalesce: false}));
  const note = el('span', {class: 'muted small', text: options.some((o) => o.verified) ? '' : 'Value names are not known yet.'});
  return {
    el: el('div', {class: 'selectwrap'}, input, note),
    update(value) {
      if (typeof value === 'number' && !options.some((o) => o.value === value)) {
        input.append(el('option', {value: String(value), text: `Value ${value} (not in the schema list)`}));
      }
      input.value = String(value);
    },
    setEditable(flag) { input.disabled = !flag; },
    focus() { input.focus(); },
  };
}

function text(row, spec) {
  const input = el('input', {type: 'text', class: 'text', id: spec.id, maxLength: 120, autocomplete: 'off', spellcheck: false});
  let original = null;
  input.addEventListener('change', () => spec.onSet(input.value === '' && original === null ? null : input.value, {coalesce: false}));
  return {
    el: el('div', {class: 'textwrap'}, input),
    update(value, originalValue) {
      original = originalValue === undefined ? null : originalValue;
      const shown = value && typeof value === 'object' && typeof value.string === 'string' ? value.string : value;
      input.value = typeof shown === 'string' ? shown : '';
    },
    setEditable(flag) { input.disabled = !flag; },
    focus() { input.focus(); },
  };
}

function curve(row, spec) {
  const editor = createCurveEditor({id: spec.id, label: spec.label, onChange: (value) => spec.onSet(value, {coalesce: true}), onCommit: spec.onCommit});
  return {
    el: editor.el,
    update(value) { editor.setValue(value); },
    setEditable(flag) { editor.setEditable(flag); },
    focus() { editor.canvas.focus(); },
  };
}

function readonly(row, spec) {
  const code = el('code', {class: 'value', id: spec.id, tabIndex: 0});
  return {
    el: el('div', {class: 'readonly'}, code),
    update(value) { code.textContent = formatValue(row, value); },
    setEditable() {},
    focus() { code.focus(); },
  };
}
