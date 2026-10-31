// api.js - the client of pipeline/app_server.py (F10 "HTTP").
//
// Token: the server prints `Open http://localhost:<port>/#t=<token>`; the token
// reaches the page only in the URL fragment. It is read once into this module's
// memory and sent as `X-ROSW-Token` on every /api/* call. It is never stored.
// The fragment is left in the address bar so that a reload still works; a
// fragment is never sent to a server.
//
// Errors: the server answers {"error": {code, message, hint, data}}. Every
// failure here becomes an ApiError with those fields (code `network` when the
// server cannot be reached, `parse` when a reply is not what F10 says).

let token = null;

export class ApiError extends Error {
  constructor(code, message, {status = 0, hint = null, data = null} = {}) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.status = status;
    this.hint = hint;
    this.data = data;
  }
}

/** Read `#t=<token>` from a location-like object into memory. Returns true when there is one. */
export function initToken(loc = globalThis.location) {
  const hash = (loc && loc.hash) || '';
  const found = /(?:^#|&)t=([A-Za-z0-9_-]{8,128})(?:&|$)/.exec(hash);
  token = found ? found[1] : null;
  return token !== null;
}

export function hasToken() { return token !== null; }
export function tokenForLinks() { return token; }        // selftest link only: same origin, in a fragment

async function send(method, path, {body = null, headers = {}, tokenOverride} = {}) {
  const used = tokenOverride === undefined ? token : tokenOverride;
  const init = {method, headers: {...headers}, cache: 'no-store', credentials: 'omit', referrerPolicy: 'no-referrer'};
  if (used !== null) init.headers['X-ROSW-Token'] = used;
  if (body !== null) init.body = body;
  let response;
  try {
    response = await fetch(path, init);
  } catch (error) {
    throw new ApiError('network', 'The app server cannot be reached.', {
      hint: 'Start it with: python -I brushes/pipeline/app_server.py  and open the Open line it prints.'});
  }
  if (!response.ok) throw await errorFrom(response);
  return response;
}

async function errorFrom(response) {
  let payload = null;
  try { payload = await response.json(); } catch (_) { payload = null; }
  const e = payload && payload.error;
  if (e && typeof e.code === 'string') {
    return new ApiError(e.code, e.message || e.code, {status: response.status, hint: e.hint || null, data: e.data || null});
  }
  return new ApiError('parse', `The server answered ${response.status} without the error shape of F10.`, {status: response.status});
}

async function jsonOf(response) {
  try { return await response.json(); } catch (_) { throw new ApiError('parse', 'The server reply was not JSON.'); }
}

function query(params) {
  const pairs = [];
  for (const [name, value] of Object.entries(params || {})) {
    if (value === undefined || value === null || value === '') continue;
    for (const one of Array.isArray(value) ? value : [value]) pairs.push(`${encodeURIComponent(name)}=${encodeURIComponent(one)}`);
  }
  return pairs.length ? `?${pairs.join('&')}` : '';
}

const previewCache = new Map();               // path -> Promise<blob URL>, least recently used first
const PREVIEW_CACHE_MAX = 160;

export const api = {
  status: async () => jsonOf(await send('GET', '/api/status')),
  search: async (params) => jsonOf(await send('GET', `/api/search${query(params)}`)),
  facets: async (params) => jsonOf(await send('GET', `/api/facets${query(params)}`)),
  vocabulary: async () => jsonOf(await send('GET', '/api/vocabulary')),
  sets: async (library) => jsonOf(await send('GET', `/api/sets${query({library})}`)),
  set: async (slug) => jsonOf(await send('GET', `/api/sets/${encodeURIComponent(slug)}`)),
  brush: async (id, include) => jsonOf(await send('GET', `/api/brush/${encodeURIComponent(id)}${query({include})}`)),
  similar: async (id, top) => jsonOf(await send('GET', `/api/brush/${encodeURIComponent(id)}/similar${query({top})}`)),
  similarSettings: async (body) => jsonOf(await send('POST', '/api/similar', {
    body: JSON.stringify(body), headers: {'Content-Type': 'application/json'}})),

  /** GET /api/brush/<id>/open: the import "brush" response from the library original. */
  openBrush: async (id, textures = 'full') => jsonOf(await send('GET', `/api/brush/${encodeURIComponent(id)}/open${query({textures})}`)),

  /** POST /api/import with the raw file; `member` picks one brush of a set. */
  importFile: async (file, {member, textures = 'full'} = {}) => jsonOf(await send('POST', `/api/import${query({member, textures})}`, {
    body: file, headers: {'Content-Type': 'application/octet-stream', 'X-ROSW-Filename': encodeURIComponent(file.name || '')}})),

  validatePatch: async (body) => jsonOf(await send('POST', '/api/validate-patch', {
    body: JSON.stringify(body), headers: {'Content-Type': 'application/json'}})),

  /**
   * POST /api/export. A dry run answers JSON ({kind: 'report', report}); a real
   * export answers bytes ({kind: 'file', blob, filename, info}) with the
   * filename of Content-Disposition and the X-ROSW-Export header decoded.
   */
  exportBrush: async (request) => {
    const response = await send('POST', '/api/export', {
      body: JSON.stringify(request), headers: {'Content-Type': 'application/json'}});
    const type = response.headers.get('Content-Type') || '';
    if (type.startsWith('application/json')) return {kind: 'report', report: await jsonOf(response)};
    const blob = await response.blob();
    return {kind: 'file', blob, filename: filenameOf(response.headers.get('Content-Disposition')),
      info: infoOf(response.headers.get('X-ROSW-Export'))};
  },

  quit: async () => jsonOf(await send('POST', '/api/quit', {body: '{}', headers: {'Content-Type': 'application/json'}})),

  /** A preview PNG as a blob: URL (an <img> cannot send the token header). Cached. */
  previewUrl(id, kind = 'stroke') {
    const path = `/api/preview/${encodeURIComponent(id)}/${kind}.png`;
    let hit = previewCache.get(path);
    if (hit) { previewCache.delete(path); previewCache.set(path, hit); return hit; }
    hit = send('GET', path).then((r) => r.blob()).then((blob) => URL.createObjectURL(blob));
    previewCache.set(path, hit);
    hit.catch(() => previewCache.delete(path));
    while (previewCache.size > PREVIEW_CACHE_MAX) {
      const [oldPath, old] = previewCache.entries().next().value;
      previewCache.delete(oldPath);
      old.then((url) => URL.revokeObjectURL(url), () => {});
    }
    return hit;
  },

  /** A call with an explicit token (the selftest uses it to prove a wrong token is refused). */
  rawStatus: async (tokenOverride) => jsonOf(await send('GET', '/api/status', {tokenOverride})),
};

/** The static files need no token. A missing optional file gives null. */
export async function loadStatic(path, {optional = false} = {}) {
  let response;
  try {
    response = await fetch(path, {cache: 'no-store', credentials: 'omit'});
  } catch (_) {
    throw new ApiError('network', `${path} cannot be loaded: the server is not reachable.`);
  }
  if (!response.ok) {
    if (optional) return null;
    throw await errorFrom(response);
  }
  return jsonOf(response);
}

export function filenameOf(disposition) {
  if (!disposition) return 'brush-export';
  const star = /filename\*\s*=\s*UTF-8''([^;]+)/i.exec(disposition);
  if (star) { try { return decodeURIComponent(star[1].trim()); } catch (_) { /* use the ascii name */ } }
  const plain = /filename\s*=\s*"([^"]*)"/i.exec(disposition);
  return plain ? plain[1] : 'brush-export';
}

export function infoOf(header) {
  if (!header) return null;
  try { return JSON.parse(decodeURIComponent(header)); } catch (_) { return null; }
}
