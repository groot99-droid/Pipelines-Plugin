// patch.js - the patch envelope of F3 and the diff the patch box shows.
// Pure: no DOM, no network. Importable from Node.
//
//   {"schema": "rosw-brushes-patch/1", "base_id": <brush_id>|null,
//    "summary": str, "changes": {key: value}}
//
// Claude proposes a patch (validated with validate_settings_patch) and the user
// pastes it here; there is no patch inbox on the server (F10 "The app").

import {formatValue} from './schema.js';

export const PATCH_SCHEMA = 'rosw-brushes-patch/1';
export const MAX_PATCH_TEXT = 900 * 1024;        // the server takes 1 MiB of JSON; stay under it

const BRUSH_ID = /^b_[0-9a-f]{12}$/;

/**
 * Parse pasted text. Accepts the envelope, or a bare {"changes": {...}}.
 * Returns {ok: true, envelope} or {ok: false, error}.
 */
export function parseEnvelope(text) {
  if (typeof text !== 'string' || !text.trim()) return {ok: false, error: 'Paste a patch first.'};
  if (text.length > MAX_PATCH_TEXT) return {ok: false, error: 'The patch is larger than 900 KiB.'};
  let value;
  try {
    value = JSON.parse(stripFence(text));
  } catch (error) {
    return {ok: false, error: `This is not valid JSON (${String(error.message).slice(0, 80)}).`};
  }
  if (!value || typeof value !== 'object' || Array.isArray(value)) return {ok: false, error: 'A patch is a JSON object.'};
  if (value.schema !== undefined && value.schema !== PATCH_SCHEMA) {
    return {ok: false, error: `The schema is "${String(value.schema).slice(0, 40)}"; this app reads "${PATCH_SCHEMA}".`};
  }
  const changes = value.changes;
  if (!changes || typeof changes !== 'object' || Array.isArray(changes)) return {ok: false, error: 'The patch has no "changes" object.'};
  if (!Object.keys(changes).length) return {ok: false, error: 'The patch changes nothing.'};
  if (Object.keys(changes).length > 400) return {ok: false, error: 'The patch changes more than 400 keys.'};
  const baseId = value.base_id === undefined || value.base_id === null ? null : value.base_id;
  if (baseId !== null && (typeof baseId !== 'string' || !BRUSH_ID.test(baseId))) return {ok: false, error: '"base_id" is not a brush id.'};
  const summary = typeof value.summary === 'string' ? value.summary.slice(0, 300) : '';
  return {ok: true, envelope: {schema: PATCH_SCHEMA, base_id: baseId, summary, changes}};
}

/** A chat client may wrap JSON in a code fence; take what is inside. */
export function stripFence(text) {
  const m = /^\s*```[a-z]*\s*\n([\s\S]*?)\n?```\s*$/i.exec(text);
  return m ? m[1] : text;
}

/** The shortest decimal that is the same 32-bit float (0.30000001192092896 -> 0.3); other JSON is kept. */
export function shorten(value) {
  if (typeof value === 'number') {
    if (!Number.isFinite(value) || Number.isInteger(value)) return value;
    const wanted = Math.fround(value);
    for (let p = 1; p <= 9; p += 1) { const short = Number(value.toPrecision(p)); if (Math.fround(short) === wanted) return short; }
    return value;
  }
  if (Array.isArray(value)) return value.map(shorten);
  if (value && typeof value === 'object') return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, shorten(v)]));
  return value;
}

/** A legacy curve comes back from the server with `resolution`; it is not a setting, so it is not kept in the patch. */
export function dropResolution(changes) {
  const out = {};
  for (const [key, value] of Object.entries(changes)) {
    out[key] = value && typeof value === 'object' && Array.isArray(value.points) ? {points: value.points} : value;
  }
  return out;
}

/** The compact envelope text for a patch: what "Copy patch" puts on the clipboard. */
export function envelopeText({baseId = null, changes, summary}) {
  const keys = Object.keys(changes);
  const shown = keys.slice(0, 6).join(', ') + (keys.length > 6 ? ' ...' : '');
  return JSON.stringify({schema: PATCH_SCHEMA, base_id: baseId, summary: summary || `${keys.length} setting(s): ${shown}`, changes: shorten(changes)});
}

/**
 * Rows for the diff: one per key in `applied`, with the label, the value in the
 * opened brush, the value now, and the value the patch would give.
 */
export function diffRows(index, doc, applied) {
  const rows = [];
  for (const [key, after] of Object.entries(applied)) {
    const row = index.byKey.get(key) || null;
    const original = doc.originalValue(key, 'main');
    const now = doc.value(key, 'main');
    rows.push({
      key, label: row ? row.label : key, original: formatValue(row, original), now: formatValue(row, now),
      after: formatValue(row, after), isNew: doc.originalValue(key, 'main') === undefined,
    });
  }
  return rows;
}

/** Reasons the server gives, in plain words. */
export const REJECT_TEXT = {
  unknown_key: 'No such setting in this app’s schema.',
  wrong_type: 'The value is the wrong kind for this setting.',
  not_in_enum: 'Not one of the values this setting is known to hold.',
  non_finite: 'The value is not a finite number.',
  read_only: 'This setting cannot be changed.',
  not_in_era: 'This brush’s era does not have this setting.',
  curve_invalid: 'The curve is not valid (2 to 64 points, each 0 to 1).',
  out_of_range: 'The value is outside the allowed range.',
};

export const WARNING_TEXT = {
  outside_observed: 'Outside the range seen in the library. Applied, but not tested.',
  stale_thumbnail: 'The thumbnail still shows the brush as it was before the change.',
};
