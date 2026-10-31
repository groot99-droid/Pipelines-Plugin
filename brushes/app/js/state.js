// state.js - the brush being edited: the decoded original plus a patch of the
// keys that changed, with undo and redo. Pure: no DOM, no network.
//
// F3 "Patches": the app never sends a full settings object. It sends `changes`,
// the keys the user means to change, and the server patches the original
// archive. So the doc keeps the original settings frozen and a `patch` of
// key -> value. A widget calls set() only on user input; a brush nobody touched
// has an empty patch and exports as its source bytes (F3 "Export").
//
// History: every edit is one snapshot {main, sub, shape, grain, thumb}. A
// snapshot shares what did not change, so a long history is cheap. Edits of the
// same key within COALESCE_MS (a slider drag) replace the newest snapshot
// instead of adding one.

import {sameCurve} from './schema.js';

export const COALESCE_MS = 900;
export const HISTORY_MAX = 300;

const has = (object, key) => Object.prototype.hasOwnProperty.call(object, key);

/** Structural equality of JSON values; two curves are equal when their point sets are. */
export function deepEqual(a, b) {
  if (a === b) return true;
  if (typeof a !== typeof b || a === null || b === null || typeof a !== 'object') return false;
  if (Array.isArray(a) !== Array.isArray(b)) return false;
  if (Array.isArray(a)) return a.length === b.length && a.every((v, i) => deepEqual(v, b[i]));
  if (Array.isArray(a.points) && Array.isArray(b.points)) return sameCurve(a, b);
  const ka = Object.keys(a); const kb = Object.keys(b);
  return ka.length === kb.length && ka.every((k) => has(b, k) && deepEqual(a[k], b[k]));
}

export function clone(value) {
  return value === undefined ? undefined : JSON.parse(JSON.stringify(value));
}

const EMPTY_THUMB = Object.freeze({mode: 'keep'});

/**
 * createDoc({origin, name, era, settings, sub, meta, textures, base, libraryId, warnings})
 *   origin    {kind: 'library'|'file'|'new', id?, filename?, member?}
 *   settings  JSON forms of the decoded archive (frozen here)
 *   sub       null or {settings, meta, textures} of a dual brush's Sub01
 *   textures  the import response's textures {shape, grain, thumbnail}
 *   base      {library_id} or {members: [{path, b64}]}: what an export patches
 */
export function createDoc(init) {
  const original = {main: freezeDeep(clone(init.settings || {})), sub: init.sub ? freezeDeep(clone(init.sub.settings || {})) : null};
  const listeners = new Set();
  let snapshots = [snapshot()];
  let index = 0;
  let lastCoalesce = {key: null, time: 0};
  let active = 'main';

  function snapshot(parts = {}) {
    return Object.freeze({
      main: parts.main || Object.freeze({}), sub: parts.sub || Object.freeze({}),
      shape: parts.shape === undefined ? null : parts.shape,
      grain: parts.grain === undefined ? null : parts.grain,
      thumb: parts.thumb || EMPTY_THUMB,
      label: parts.label || '',
    });
  }
  const current = () => snapshots[index];

  function commit(next, keys, {coalesceKey = null, now = Date.now()} = {}) {
    const coalesce = coalesceKey !== null && lastCoalesce.key === coalesceKey && now - lastCoalesce.time < COALESCE_MS && index > 0
      && index === snapshots.length - 1;
    if (coalesce) snapshots[index] = next;
    else {
      snapshots = snapshots.slice(0, index + 1);
      snapshots.push(next);
      if (snapshots.length > HISTORY_MAX) snapshots.shift();
      index = snapshots.length - 1;
    }
    lastCoalesce = {key: coalesceKey, time: now};
    emit({type: 'change', keys});
  }

  function emit(event) {
    for (const fn of [...listeners]) fn(event);
  }

  const layerOf = (layer) => (layer === 'sub' ? 'sub' : 'main');
  const baseOf = (layer) => (layer === 'sub' ? original.sub || {} : original.main);

  const doc = {
    origin: init.origin || {kind: 'file'},
    name: init.name || '',
    era: init.era || null,
    meta: init.meta || {},
    subMeta: init.sub ? init.sub.meta || {} : null,
    textures: init.textures || {},
    base: init.base || null,
    libraryId: init.libraryId || null,
    warnings: init.warnings || [],
    original: original.main,
    originalSub: original.sub,
    hasSub: !!init.sub,

    get active() { return active; },
    setActive(layer) { active = layerOf(layer); emit({type: 'layer', keys: []}); },

    /** The value now: the patched one, else the original. */
    value(key, layer = active) {
      const patch = current()[layerOf(layer)];
      return has(patch, key) ? patch[key] : baseOf(layer)[key];
    },
    has(key, layer = active) { return has(baseOf(layer), key) || has(current()[layerOf(layer)], key); },
    originalValue(key, layer = active) { return baseOf(layer)[key]; },
    isChanged(key, layer = active) { return has(current()[layerOf(layer)], key); },
    /** The settings as they would be after the patch: for the engine and the diff. */
    effective(layer = active) { return {...baseOf(layer), ...current()[layerOf(layer)]}; },
    /** A copy of the patch: key -> value, only what changed. */
    patch(layer = 'main') { return {...current()[layerOf(layer)]}; },
    changedKeys(layer = active) { return Object.keys(current()[layerOf(layer)]); },

    set(key, value, opts = {}) { return doc.setMany({[key]: value}, {...opts, coalesceKey: opts.coalesce ? `${opts.layer || active}:${key}` : null}); },

    /** Several keys as one undo step. Returns the keys that changed. */
    setMany(changes, {label = '', layer = active, coalesceKey = null} = {}) {
      const l = layerOf(layer);
      const patch = {...current()[l]};
      const touched = [];
      for (const [key, value] of Object.entries(changes)) {
        const before = has(patch, key) ? patch[key] : baseOf(l)[key];
        if (deepEqual(before, value)) continue;
        if (has(baseOf(l), key) && deepEqual(baseOf(l)[key], value)) delete patch[key];
        else patch[key] = freezeDeep(clone(value));
        touched.push(key);
      }
      if (!touched.length) return [];
      commit(snapshot({...current(), [l]: Object.freeze(patch), label: label || touched.join(', ')}), touched.map((k) => k), {coalesceKey});
      return touched;
    },

    /** Put one key back to the original value. */
    reset(key, layer = active) {
      const l = layerOf(layer);
      if (!has(current()[l], key)) return false;
      const patch = {...current()[l]};
      delete patch[key];
      commit(snapshot({...current(), [l]: Object.freeze(patch), label: `reset ${key}`}), [key]);
      return true;
    },

    /** Drop every edit, texture and thumbnail change: back to the opened brush. One undo step. */
    resetAll() {
      if (!doc.dirty) return false;
      const keys = [...Object.keys(current().main), ...Object.keys(current().sub)];
      commit(snapshot({label: 'reset all'}), keys);
      return true;
    },

    textureChange(role) { return current()[role]; },
    /** role: 'shape' | 'grain'. replacement: {png_b64, width, height, how, label} or null (keep the original). */
    setTexture(role, replacement) {
      commit(snapshot({...current(), [role]: replacement ? Object.freeze({...replacement}) : null, label: `${role} image`}), [`texture:${role}`]);
    },
    thumbnail() { return current().thumb; },
    /** spec: {mode: 'keep'} | {mode: 'omit'} | {mode: 'replace', png_b64, ...} */
    setThumbnail(spec) {
      commit(snapshot({...current(), thumb: Object.freeze({...spec}), label: 'thumbnail'}), ['texture:thumbnail']);
    },

    /** Stop merging the next edit into the last one (a drag ended). */
    endCoalesce() { lastCoalesce = {key: null, time: 0}; },

    get canUndo() { return index > 0; },
    get canRedo() { return index < snapshots.length - 1; },
    undo() { if (index > 0) return move(-1); return false; },
    redo() { if (index < snapshots.length - 1) return move(1); return false; },
    get undoLabel() { return index > 0 ? current().label : ''; },
    get redoLabel() { return index < snapshots.length - 1 ? snapshots[index + 1].label : ''; },
    get historyLength() { return snapshots.length; },

    get dirty() {
      const s = current();
      return Object.keys(s.main).length > 0 || Object.keys(s.sub).length > 0 || s.shape !== null || s.grain !== null || s.thumb.mode !== 'keep';
    },
    get dirtyCount() {
      const s = current();
      return Object.keys(s.main).length + Object.keys(s.sub).length + (s.shape ? 1 : 0) + (s.grain ? 1 : 0) + (s.thumb.mode !== 'keep' ? 1 : 0);
    },

    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
  };

  function move(step) {
    const before = current();
    index += step;
    const after = current();
    lastCoalesce = {key: null, time: 0};
    const keys = new Set([...Object.keys(before.main), ...Object.keys(after.main), ...Object.keys(before.sub), ...Object.keys(after.sub)]);
    if (before.shape !== after.shape) keys.add('texture:shape');
    if (before.grain !== after.grain) keys.add('texture:grain');
    if (before.thumb !== after.thumb) keys.add('texture:thumbnail');
    emit({type: step < 0 ? 'undo' : 'redo', keys: [...keys]});
    return true;
  }

  return doc;
}

export function freezeDeep(value) {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    Object.freeze(value);
    for (const inner of Object.values(value)) freezeDeep(inner);
  }
  return value;
}
