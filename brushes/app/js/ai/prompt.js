// ai/prompt.js - the request the user copies to Claude, and the reading of
// Claude's reply. Pure: no DOM, no network, importable from Node.
//
// F10 "The app": the Claude route is paste only. There is no model behind this
// page and no patch inbox on the server, so the page writes a compact request
// the user pastes into a chat, and takes the reply back through the Patch box,
// where the server checks it (POST /api/validate-patch) and the user reviews
// the diff before anything changes.
//
// The request holds: the wish in the user's words, the brush's name / era /
// id, a table of the settings Claude may change (key, label, kind, range,
// value now, one line of meaning), the rules the server enforces, the exact
// envelope of F3 "Patches", two valid examples built from this brush's own
// keys, and the reply format. It never holds the access token or any file.

import {availability, heldKey, trim} from '../schema.js';
import {PATCH_SCHEMA, shorten} from '../patch.js';

export const REQUEST_LIMIT = 14000;        // characters; the request is meant to be pasted into a chat
export const WISH_LIMIT = 600;

/** One line of meaning from a row's hint: the first sentence, at most `max` characters. */
export function shortHint(hint, max = 90) {
  const flat = String(hint || '').replace(/\s+/g, ' ').trim();
  const sentence = /^(.*?[.!?])(?:\s|$)/.exec(flat);
  const first = sentence ? sentence[1] : flat;
  return first.length > max ? `${first.slice(0, max - 1)}…` : first;
}

/**
 * The rows Claude may change on this brush: schema rows with `ai: true` (or
 * every editable row with `all`), present in the brush, with a meaning that is
 * established. Returns [{row, key, value}]; `key` is the name this brush's era uses.
 */
export function changeableRows(schema, settings, era, {all = false} = {}) {
  const out = [];
  for (const row of schema.rows) {
    if (row.retired || row.key === 'name') continue;
    if (!all && !row.ai) continue;
    if (row.confidence === 'unknown' || row.ui === 'hidden' || row.ui === 'readonly') continue;
    if (!['real', 'int', 'bool', 'curve_ref'].includes(row.type)) continue;
    if (row.key === 'blendMode') continue;                       // blend-mode codes are unnamed (F4): nothing to reason about
    if (availability(row, settings, era) !== 'present') continue;
    const key = heldKey(row, settings);
    out.push({row, key, value: settings[key]});
  }
  return out;
}

/** Keys the brush's era lists but this brush lacks: a patch may add them. */
export function addableKeys(schema, settings, era, {all = false} = {}) {
  const out = [];
  for (const row of schema.rows) {
    if (row.retired || row.key === 'name' || row.confidence === 'unknown' || row.ui === 'hidden' || row.ui === 'readonly') continue;
    if (!all && !row.ai) continue;
    if (!['real', 'int', 'bool', 'curve_ref'].includes(row.type) || row.key === 'blendMode') continue;
    if (availability(row, settings, era) === 'optional') out.push(row.key);
  }
  return out;
}

function kindText(row) {
  if (row.type === 'bool') return 'on/off';
  if (row.type === 'curve_ref') return 'curve';
  const r = Array.isArray(row.limits) && row.limits.length === 2 ? `${row.type} ${trim(row.limits[0], 4)}..${trim(row.limits[1], 4)}` : row.type;
  return r;
}

function valueText(row, value) {
  if (value === undefined || value === null) return 'unset';
  if (row.type === 'bool') return value ? 'true' : 'false';
  if (row.type === 'curve_ref') {
    const pts = (value && value.points) || [];
    return pts.length > 8 ? `${JSON.stringify(pts.slice(0, 8))} (+${pts.length - 8} more)` : JSON.stringify(pts);
  }
  if (typeof value === 'number') return trim(shorten(value), 5);
  return JSON.stringify(value);
}

/** One table line: `key | Label | kind | now | default | meaning`. */
export function tableLine({row, key, value}, edited) {
  const def = row.type === 'curve_ref' ? '' : ` (default ${row.default === undefined ? '?' : valueText(row, row.default)})`;
  return `${key}${edited ? '*' : ''} | ${row.label} | ${kindText(row)} | now ${valueText(row, value)}${def} | ${shortHint(row.hint)}`;
}

/** A curve value in the form the server wants. */
const CURVE_EXAMPLE = {points: ['{0.000000, 0.000000}', '{1.000000, 1.000000}', '{0.500000, 0.350000}']};

function clampTo(row, v) {
  if (Array.isArray(row.limits)) return Math.min(row.limits[1], Math.max(row.limits[0], v));
  return v;
}

/** Two valid example patches built from keys this brush holds. Values are inside the limits. */
export function examples(rows) {
  const real = rows.filter((r) => r.row.type === 'real' && typeof r.value === 'number' && Array.isArray(r.row.limits));
  const bool = rows.find((r) => r.row.type === 'bool');
  const curve = rows.find((r) => r.row.type === 'curve_ref');
  const nudge = (r, factor, add) => Number(trim(shorten(clampTo(r.row, r.value === 0 ? add : r.value * factor)), 4));
  const first = real[0];
  const second = real.slice(1, 3);
  const out = [];
  if (first) out.push({summary: `Slightly changed ${first.row.label}`, changes: {[first.key]: nudge(first, 1.25, 0.1)}});
  const multi = {};
  for (const r of second) multi[r.key] = nudge(r, 0.8, 0.2);
  if (bool) multi[bool.key] = !bool.value;
  if (curve) multi[curve.key] = CURVE_EXAMPLE;
  if (Object.keys(multi).length) out.push({summary: 'A few settings changed together', changes: multi});
  return out;
}

export function envelopeOf({baseId, summary, changes}) {
  return {schema: PATCH_SCHEMA, base_id: baseId || null, summary, changes};
}

/**
 * The full request text.
 *   input: {schema, settings (effective, main layer), patch (keys edited so far), era, name, libraryId, wish, all}
 */
export function buildRequest({schema, settings, patch = {}, era, name, libraryId = null, wish = '', all = false}) {
  const rows = changeableRows(schema, settings, era, {all});
  const addable = addableKeys(schema, settings, era, {all});
  const wishText = String(wish || '').trim().slice(0, WISH_LIMIT) || '(describe the change you want here)';
  const baseId = libraryId || null;
  const lines = [];
  lines.push('I am editing a Procreate brush in a local brush tool. You cannot reach the tool; I will paste your reply into it. The tool checks every value and shows me a before/after list, and nothing changes until I press Apply.', '');
  lines.push('WHAT I WANT', wishText, '');
  lines.push('THE BRUSH', `Name: ${name || 'Untitled'}`, `Era: ${era || 'unknown'}`, `Brush id: ${baseId || 'none (not a library brush)'}`,
    `${rows.length} settings below can be changed${Object.keys(patch).length ? '; a * marks one I have already edited' : ''}.`, '');
  lines.push('SETTINGS YOU MAY CHANGE (key | label | kind and range | value now | meaning)');
  for (const r of rows) lines.push(tableLine(r, Object.prototype.hasOwnProperty.call(patch, r.key)));
  if (addable.length) lines.push('', `Settings this brush's era supports but this brush does not hold yet (a patch may add them): ${addable.join(', ')}.`);
  lines.push('', 'RULES THE TOOL ENFORCES');
  lines.push('- Use only the keys above. Any other key is rejected (unknown_key, or not_in_era if the era lacks it).');
  lines.push('- Numbers: real = decimal, int = whole number. true/false for on/off. Do not send strings for numbers.');
  lines.push('- A value outside the range shown is applied but flagged as untested: stay inside unless there is a reason.');
  lines.push('- A curve is {"points": ["{x, y}", ...]} with 2 to 64 points, x and y each 0 to 1, written exactly like "{0.500000, 0.350000}".');
  lines.push('- Change only what the request needs (usually 3 to 10 keys). Leave everything else out; a key you leave out is never touched.');
  lines.push('- Do not change the name.', '');
  lines.push('PATCH FORMAT (exactly this envelope)');
  lines.push(JSON.stringify(envelopeOf({baseId, summary: 'one short sentence saying what changes', changes: {'<key>': '<value>'}})), '');
  lines.push('VALID EXAMPLES (shapes only: do not copy their values)');
  for (const ex of examples(rows)) lines.push(JSON.stringify(envelopeOf({baseId, summary: ex.summary, changes: ex.changes})));
  lines.push('', 'HOW TO REPLY',
    'Two sentences at most on what you changed and why, then ONE fenced ```json block holding the envelope, and nothing after it. Keep "summary" under 300 characters.');
  return lines.join('\n');
}

/**
 * Find the patch in a chat reply: the first fenced block (or bare {...} object)
 * that parses as an object with a `changes` object. Returns {ok: true, text,
 * keys} with the JSON text to hand to the Patch box, or {ok: false, error}.
 */
export function extractPatch(reply) {
  const text = String(reply || '');
  if (!text.trim()) return {ok: false, error: 'Paste Claude’s reply first.'};
  const candidates = [];
  for (const m of text.matchAll(/```[a-zA-Z]*\s*\n?([\s\S]*?)```/g)) candidates.push(m[1].trim());
  const open = text.indexOf('{');
  if (open >= 0) {
    const balanced = balancedObject(text, open);
    if (balanced) candidates.push(balanced);
  }
  if (!candidates.length) return {ok: false, error: 'No JSON patch found. Claude’s reply should hold one fenced ```json block.'};
  let lastError = 'No JSON patch found.';
  for (const candidate of candidates) {
    try {
      const value = JSON.parse(candidate);
      if (value && typeof value === 'object' && !Array.isArray(value) && value.changes && typeof value.changes === 'object' && !Array.isArray(value.changes)) {
        return {ok: true, text: candidate, keys: Object.keys(value.changes), summary: typeof value.summary === 'string' ? value.summary : ''};
      }
      lastError = 'The JSON has no "changes" object.';
    } catch (error) {
      lastError = `The JSON does not parse (${String(error.message).slice(0, 70)}).`;
    }
  }
  return {ok: false, error: lastError};
}

/** The first balanced {...} starting at `start`, respecting strings; null if it never closes. */
function balancedObject(text, start) {
  let depth = 0; let inString = false; let escaped = false;
  for (let i = start; i < text.length; i += 1) {
    const c = text[i];
    if (inString) { if (escaped) escaped = false; else if (c === '\\') escaped = true; else if (c === '"') inString = false; continue; }
    if (c === '"') inString = true;
    else if (c === '{') depth += 1;
    else if (c === '}') { depth -= 1; if (depth === 0) return text.slice(start, i + 1); }
  }
  return null;
}

/** For the AI tab: a rough size line. */
export function sizeText(text) {
  return `${text.length.toLocaleString()} characters, about ${Math.ceil(text.length / 4).toLocaleString()} tokens`;
}

/** Pure checks: [{name, run}] given the indexed schema. */
export function promptTests(schema) {
  const tests = [];
  const t = (name, run) => tests.push({name, run});
  const ok = (c, m) => { if (!c) throw new Error(m || 'assertion failed'); };
  const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${m || 'not equal'}: got ${JSON.stringify(a).slice(0, 200)}, wanted ${JSON.stringify(b).slice(0, 200)}`); };
  const settingsFor = (era) => {
    const s = {name: 'Test brush'};
    for (const row of schema.rows) if ((row.eras || []).includes(era) && row.default !== undefined && !(row.aliases || []).length) s[row.key] = row.default;
    return s;
  };
  t('ai prompt: the request holds the wish, the F3 envelope, the rules and two valid examples, and fits the size bound', () => {
    const settings = settingsFor('M220'); settings.plotSpacing = 0.0619;
    const text = buildRequest({schema, settings, patch: {plotSpacing: 0.0619}, era: 'M220', name: 'Test brush', libraryId: 'b_0123456789ab', wish: 'make this softer and grainier, like charcoal'});
    ok(text.includes('make this softer and grainier, like charcoal'), 'wish'); ok(text.includes(`"schema":"${PATCH_SCHEMA}"`), 'envelope');
    ok(text.includes('"base_id":"b_0123456789ab"'), 'base id'); ok(text.includes('plotSpacing* | Spacing'), 'edited key is starred'); ok(text.includes('ONE fenced'), 'reply format');
    ok(text.includes('unknown_key') && text.includes('not_in_era'), 'rules');
    ok(text.length < REQUEST_LIMIT, `request is ${text.length} characters`);
    const exampleLines = text.split('\n').filter((l) => l.startsWith('{"schema"'));
    eq(exampleLines.length, 3, 'one format line and two examples');
    for (const line of exampleLines.slice(1)) { const e = JSON.parse(line); ok(Object.keys(e.changes).length >= 1 && e.base_id === 'b_0123456789ab'); }
  });
  t('ai prompt: only keys the brush holds are offered, per era, and nothing unverified, unnamed or secret appears', () => {
    const e0 = settingsFor('E0'); const rows = changeableRows(schema, e0, 'E0');
    ok(rows.length > 10, 'E0 rows');
    ok(!rows.some((r) => r.key === 'grainDepth' || r.key === 'blendMode' || r.key === 'name'), 'M-era or unnamed keys must not be offered to E0');
    const m = changeableRows(schema, settingsFor('M220'), 'M220'); ok(m.some((r) => r.key === 'grainDepth'));
    ok(m.every((r) => r.row.confidence !== 'unknown'));
    const text = buildRequest({schema, settings: settingsFor('M220'), era: 'M220', name: 'x', wish: ''});
    ok(!/X-ROSW|#t=|token/i.test(text), 'no token word');
  });
  t('ai prompt: the wish is cut to its limit and a brush with no id says so', () => {
    const text = buildRequest({schema, settings: settingsFor('M220'), era: 'M220', name: 'x', wish: 'w'.repeat(5000)});
    ok(!text.includes('w'.repeat(WISH_LIMIT + 1))); ok(text.includes('none (not a library brush)')); ok(text.includes('"base_id":null'));
  });
  t('ai prompt: a full-key request stays under the size bound', () => {
    const settings = settingsFor('M220');
    const text = buildRequest({schema, settings, era: 'M220', name: 'x', wish: 'y', all: true}); ok(text.length < REQUEST_LIMIT * 1.6, `${text.length}`);
  });
  t('ai prompt: extractPatch finds the patch in a chat reply with prose, fences and braces in strings', () => {
    const body = '{"schema":"rosw-brushes-patch/1","base_id":null,"summary":"a } b","changes":{"plotSpacing":0.2}}';
    const fenced = extractPatch(`Softer.\n\n\`\`\`json\n${body}\n\`\`\`\nDone.`); ok(fenced.ok && fenced.keys[0] === 'plotSpacing', JSON.stringify(fenced));
    const bare = extractPatch(`Here: ${body} thanks`); ok(bare.ok, JSON.stringify(bare)); eq(JSON.parse(bare.text).summary, 'a } b');
    ok(!extractPatch('no json at all').ok); ok(!extractPatch('```json\n{"a":1}\n```').ok); ok(!extractPatch('').ok); ok(!extractPatch('{"changes": [1]}').ok);
  });
  t('ai prompt: examples use this brush’s own keys and stay inside the limits', () => {
    const rows = changeableRows(schema, settingsFor('M220'), 'M220');
    for (const ex of examples(rows)) for (const [key, value] of Object.entries(ex.changes)) {
      const row = schema.byKey.get(key); ok(row, key);
      if (typeof value === 'number' && Array.isArray(row.limits)) ok(value >= row.limits[0] && value <= row.limits[1], `${key}=${value}`);
    }
  });
  return tests;
}
