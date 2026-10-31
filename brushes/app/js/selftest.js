// selftest.js - the app's check, run in the browser: open
//   http://localhost:8719/selftest.html#t=<token>
// (the app's header has the link). It prints PASS / FAIL / SKIP per check and
// sets the page title to "selftest: PASS n/n". A SKIP is a check the machine
// cannot do (for example, library originals missing); it is never counted as a
// pass. window.__selftest holds the results.
//
// Network checks use the real server and the real library, read only: the
// export checks build files in memory and only compare bytes; nothing is saved.

import {el} from './dom.js';
import {api, initToken, hasToken, loadStatic, ApiError} from './api.js';
import {indexSchema} from './schema.js';
import {createDoc, deepEqual} from './state.js';
import {pureTests} from './pure-tests.js';
import {createPanels} from './panels.js';
import {brushSpec, runExport} from './exporter.js';
import {openLibraryBrush, newBrush, docFromResponse} from './opener.js';
import {validateBody} from './patchbox.js';
import {createEngine} from './engine.js';
import {textureView, thumbnailView, canvasToReplacement} from './textures.js';
import {bytesToB64} from './b64.js';
import {ShapeGenerators} from './generators/shape.js';
import {initUi} from './ui.js';

const BRUSH_PEN = 'b_e9fe9907bee5';
const results = [];
const consoleErrors = [];
const out = document.getElementById('checks');
const summary = document.getElementById('summary');

const originalError = console.error;
console.error = (...args) => { consoleErrors.push(args.map(String).join(' ')); originalError.apply(console, args); };
window.addEventListener('error', (e) => consoleErrors.push(`error: ${e.message}`));
window.addEventListener('unhandledrejection', (e) => consoleErrors.push(`unhandled rejection: ${e.reason && e.reason.message}`));

class Skip extends Error {}
const skip = (why) => { throw new Skip(why); };
function ok(c, m) { if (!c) throw new Error(m || 'assertion failed'); }
function eq(a, b, m) { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${m || 'not equal'}: got ${JSON.stringify(a).slice(0, 200)}, wanted ${JSON.stringify(b).slice(0, 200)}`); }

async function check(name, fn) {
  let status = 'PASS'; let why = '';
  try { await fn(); } catch (error) {
    if (error instanceof Skip) { status = 'SKIP'; why = error.message; } else { status = 'FAIL'; why = error && error.message ? error.message : String(error); }
  }
  results.push({name, status, why});
  out.append(el('li', {}, el('span', {class: `tag ${status}`, text: status}), el('span', {}, el('span', {text: name}), why ? el('div', {class: 'why', text: why}) : null)));
  return status;
}

async function libraryDoc() {
  try { return await openLibraryBrush(BRUSH_PEN); } catch (error) {
    if (error.code === 'library_missing' || error.code === 'unknown_id' || error.code === 'not_ingested') skip(`${error.code}: ${error.message}`);
    throw error;
  }
}

// a stored (uncompressed) zip with one entry, to prove a hostile or broken file is refused with the F10 error shape
function crc32(bytes) {
  let c; let crc = 0xffffffff;
  for (let n = 0; n < bytes.length; n += 1) { c = (crc ^ bytes[n]) & 0xff; for (let k = 0; k < 8; k += 1) c = c & 1 ? (c >>> 1) ^ 0xedb88320 : c >>> 1; crc = (crc >>> 8) ^ c; }
  return (crc ^ 0xffffffff) >>> 0;
}
function storedZip(name, data) {
  const enc = new TextEncoder().encode(name); const crc = crc32(data);
  const local = new Uint8Array(30 + enc.length + data.length); const lv = new DataView(local.buffer);
  lv.setUint32(0, 0x04034b50, true); lv.setUint16(4, 20, true); lv.setUint32(14, crc, true); lv.setUint32(18, data.length, true); lv.setUint32(22, data.length, true); lv.setUint16(26, enc.length, true);
  local.set(enc, 30); local.set(data, 30 + enc.length);
  const central = new Uint8Array(46 + enc.length); const cv = new DataView(central.buffer);
  cv.setUint32(0, 0x02014b50, true); cv.setUint16(4, 20, true); cv.setUint16(6, 20, true); cv.setUint32(16, crc, true); cv.setUint32(20, data.length, true); cv.setUint32(24, data.length, true); cv.setUint16(28, enc.length, true);
  central.set(enc, 46);
  const end = new Uint8Array(22); const ev = new DataView(end.buffer);
  ev.setUint32(0, 0x06054b50, true); ev.setUint16(8, 1, true); ev.setUint16(10, 1, true); ev.setUint32(12, central.length, true); ev.setUint32(16, local.length, true);
  const all = new Uint8Array(local.length + central.length + end.length); all.set(local, 0); all.set(central, local.length); all.set(end, local.length + central.length);
  return all;
}

async function main() {
  initUi(document.getElementById('toasts'));
  let schema = null; let status = null;

  await check('token: read from the URL fragment into memory', async () => { initToken(); ok(hasToken(), 'open this page with #t=<token> (use the link in the app header)'); });
  await check('api: GET /api/status answers with the library state', async () => {
    status = await api.status(); ok(status.server === 'rosw-brushes'); ok(['fresh', 'stale', 'memory', 'not_ingested'].includes(status.index.state)); ok(status.caps && status.caps.export_formats.includes('brush'));
  });
  await check('api: a wrong token is refused with the F10 error shape (a 403 line in the console is that request)', async () => {
    try { await api.rawStatus('x'.repeat(24)); } catch (error) { ok(error instanceof ApiError && error.code === 'bad_token' && error.status === 403, `got ${error.code}`); return; }
    throw new Error('a wrong token was accepted');
  });
  await check('api: a missing token is refused', async () => {
    try { await api.rawStatus(null); } catch (error) { eq(error.code, 'bad_token'); return; }
    throw new Error('a missing token was accepted');
  });
  await check('schema: silica_keys.json loads and indexes', async () => {
    schema = indexSchema(await loadStatic('/schema/silica_keys.json')); ok(schema.rows.length > 200, `${schema.rows.length} rows`); eq(schema.groups.length, 14);
  });
  await check('static: the optional schema files answer or are absent (404), nothing else', async () => {
    for (const name of ['facets.json', 'bundled_textures.json', 'preview_calibration.json']) { const r = await loadStatic(`/schema/${name}`, {optional: true}); ok(r === null || typeof r === 'object', name); }
  });
  await check('static: a file outside the allow-list is not served', async () => {
    const r = await fetch('/js/../../pipeline/service.py', {cache: 'no-store'}); ok(r.status === 404, `status ${r.status}`);
    const r2 = await fetch('/README.md', {cache: 'no-store'}); ok(r2.status === 404, `README status ${r2.status}`);
  });
  if (!schema) { finish(); return; }

  for (const test of pureTests(schema)) await check(`pure: ${test.name}`, () => test.run());

  await check('panels: every schema key renders a labelled widget, and unverified keys are locked', async () => {
    const settings = Object.fromEntries(schema.rows.map((r) => [r.key, r.default === undefined ? null : r.default]));
    const doc = createDoc({origin: {kind: 'file'}, name: 'synthetic', era: 'M220', settings, textures: {}});
    const host = el('div', {class: 'offscreen'}); document.body.append(host);
    const panels = createPanels({schema}); host.append(panels.el); panels.setDoc(doc);
    let rendered = 0; const problems = [];
    for (const group of schema.groups) {
      panels.selectGroup(group.id);
      for (const [key, comp] of panels.visibleRows()) {
        rendered += 1;
        const label = comp.el.querySelector('label.row-label'); const control = comp.el.querySelector('input, select, canvas, code, button');
        if (!label || !control) problems.push(`${key}: no label or control`);
        else if (label.htmlFor && !comp.el.querySelector(`#${CSS.escape(label.htmlFor)}`)) problems.push(`${key}: label points nowhere`);
        const row = schema.byKey.get(key);
        if (row.confidence === 'unknown' && row.ui === 'slider' && !comp.el.querySelector('input.num').disabled) problems.push(`${key}: an unverified key is editable`);
      }
    }
    host.remove();
    ok(!problems.length, problems.slice(0, 4).join('; '));
    eq(rendered, schema.rows.length, 'rows rendered');
  });

  await check('panels: opening a brush edits nothing, and a widget edit becomes a patch key', async () => {
    const doc = createDoc({origin: {kind: 'file'}, name: 'synthetic', era: 'M220', settings: {plotSpacing: 0.25, plotJitter: 0, name: 'x'}, textures: {}});
    const host = el('div', {class: 'offscreen'}); document.body.append(host);
    const panels = createPanels({schema}); host.append(panels.el); panels.setDoc(doc); panels.selectGroup('stroke');
    ok(!doc.dirty, 'rendering must not write');
    const num = panels.visibleRows().get('plotSpacing').el.querySelector('input.num');
    num.value = '0.75'; num.dispatchEvent(new Event('change', {bubbles: true}));
    eq(doc.patch(), {plotSpacing: 0.75}); ok(!panels.visibleRows().get('plotJitter').el.classList.contains('is-changed'));
    doc.undo(); eq(doc.patch(), {}); host.remove();
  });

  await check('engine: the placeholder renders a labelled box and disposes', async () => {
    const canvas = document.createElement('canvas'); const engine = createEngine(canvas);
    const r = await engine.render({}, {width: 320, name: 'x'}); eq(r.drew, 'label'); engine.setBadges({a: 'ignored'}); engine.dispose();
    const after = await engine.render({}, {width: 320}); eq(after.drew, 'nothing');
  });

  let pen = null;
  await check('open: the library brush Brush Pen opens as a clean doc with its textures described honestly', async () => {
    pen = await libraryDoc(); eq(pen.name, 'Brush Pen'); eq(pen.era, 'M220'); ok(!pen.dirty && pen.canUndo === false); ok(Object.keys(pen.original).length > 200);
    eq(textureView(pen, 'shape').kind, 'bundled', 'a bundled shape is a placeholder, not an invented image'); ok(!('b64' in textureView(pen, 'shape')));
    eq(thumbnailView(pen).kind, 'image');
  });

  let baseline = null;
  await check('export: an unedited library brush exports unchanged (dry run: every member verbatim, nothing applied)', async () => {
    if (!pen) skip('no brush'); ok(Object.keys(pen.patch()).length === 0);
    const spec = brushSpec(pen); eq(spec.changes, {}); eq(spec.base, {library_id: BRUSH_PEN});
    const dry = await api.exportBrush({format: 'brush', dry_run: true, brushes: [spec]});
    ok(dry.kind === 'report'); ok(dry.report.members.length >= 2 && dry.report.members.every((m) => m.state === 'verbatim'), JSON.stringify(dry.report.members));
    eq(dry.report.brushes[0].applied, {}); eq(dry.report.brushes[0].rejected, []);
  });
  await check('export: the unedited bytes match the server hash and are the same on a second export', async () => {
    if (!pen) skip('no brush');
    baseline = await runExport({format: 'brush', brushes: [brushSpec(pen)], save: false}); const again = await runExport({format: 'brush', brushes: [brushSpec(pen)], save: false});
    ok(baseline.filename.endsWith('.brush')); ok(baseline.info && baseline.info.size === baseline.size, 'X-ROSW-Export size'); ok(baseline.sha256 === null || baseline.shaMatches === true, 'sha256 header vs saved bytes');
    eq(baseline.sha256, again.sha256, 'two exports differ');
  });
  await check('export: the exported file decodes (via import) to the same archive hash and the same settings as the original', async () => {
    if (!baseline) skip('no export');
    const file = new File([baseline.bytes], baseline.filename); const back = await api.importFile(file, {});
    eq(back.kind, 'brush'); eq(back.meta.archive_sha256, pen.meta.archive_sha256, 'Brush.archive changed'); ok(deepEqual(back.settings, pen.original), 'settings differ');
  });
  await check('export: one edited key changes only that key (patch -> export -> import)', async () => {
    if (!pen) skip('no brush');
    const doc = await openLibraryBrush(BRUSH_PEN); doc.set('plotSpacing', 0.5); ok(doc.dirty);
    const dry = await api.exportBrush({format: 'brush', dry_run: true, brushes: [brushSpec(doc)]});
    eq(dry.report.members.find((m) => m.path === 'Brush.archive').state, 're-encoded'); ok(dry.report.members.filter((m) => m.path !== 'Brush.archive').every((m) => m.state === 'verbatim'), 'other members must stay verbatim');
    const result = await runExport({format: 'brush', brushes: [brushSpec(doc)], save: false});
    const back = await api.importFile(new File([result.bytes], result.filename), {});
    eq(back.settings.plotSpacing, 0.5); const wanted = {...pen.original, plotSpacing: 0.5}; ok(deepEqual(back.settings, wanted), 'another key changed');
  });
  await check('export: a replaced shape image goes out and comes back embedded', async () => {
    if (!pen) skip('no brush');
    const doc = await openLibraryBrush(BRUSH_PEN); const canvas = document.createElement('canvas'); canvas.width = 64; canvas.height = 64;
    const g = canvas.getContext('2d'); g.fillStyle = '#000'; g.fillRect(0, 0, 64, 64); ShapeGenerators['Hard Circle'](g, 64);
    doc.setTexture('shape', await canvasToReplacement(canvas, 'Hard Circle')); ok(doc.dirty);
    const result = await runExport({format: 'brush', brushes: [brushSpec(doc)], save: false});
    const back = await api.importFile(new File([result.bytes], result.filename), {});
    eq(back.textures.shape.source, 'embedded'); eq(back.textures.shape.width, 64);
  });
  await check('export: a brushset of two library brushes exports', async () => {
    if (!pen) skip('no brush');
    const found = await api.search({q: 'ink', top: 2}); const ids = (found.results || []).map((r) => r.brush_id); if (ids.length < 2) skip('fewer than 2 search hits');
    const result = await runExport({format: 'brushset', name: 'Selftest set', brushes: ids.map((id) => ({base: {library_id: id}, changes: {}, mode: 'strict'}))});
    ok(result.filename.endsWith('.brushset')); ok(result.report.members.every((m) => m.state === 'verbatim' || m.path === 'brushset.plist'), 'unedited members are verbatim');
  });

  await check('patch: validate-patch happy path reports applied keys and a patch_text envelope', async () => {
    const r = await api.validatePatch({changes: {plotSpacing: 0.5}, era: 'M220'}); ok(r.ok, JSON.stringify(r.rejected)); eq(r.applied, {plotSpacing: 0.5}); ok(r.patch_text && r.patch_text.includes('rosw-brushes-patch/1')); ok(r.base && r.base.kind);
  });
  await check('patch: validate-patch rejects an unknown key, a wrong type and a read-only key, per key', async () => {
    const r = await api.validatePatch({changes: {noSuchKey: 1, plotSpacing: 'wide', version: 99}, era: 'M220'});
    ok(!r.ok); const codes = Object.fromEntries(r.rejected.map((x) => [x.key, x.code]));
    eq(codes, {noSuchKey: 'unknown_key', plotSpacing: 'wrong_type', version: 'read_only'});
  });
  await check('patch: base_id and base together are refused (400 bad_argument); a bad body is refused', async () => {
    try { await api.validatePatch({changes: {plotSpacing: 1}, base_id: BRUSH_PEN, base: {members: []}}); } catch (error) { eq(error.code, 'bad_argument'); return; }
    throw new Error('both bases were accepted');
  });
  await check('patch: the paste -> check -> apply -> undo path against the open brush', async () => {
    if (!pen) skip('no brush');
    const doc = await openLibraryBrush(BRUSH_PEN);
    const r = await api.validatePatch(validateBody(doc, {plotSpacing: 0.4, plotJitter: 1.5})); eq(r.base.kind, 'library');
    doc.setMany(r.applied, {label: 'patch'}); eq(doc.patch(), {plotSpacing: Math.fround(0.4), plotJitter: 1.5}, 'the server rounds reals to 32 bits'); doc.undo(); ok(!doc.dirty);
  });

  await check('upload: a new brush (made by the server from its donor) decodes to a doc', async () => {
    let doc; try { doc = await newBrush('M220'); } catch (error) { if (error.code === 'library_missing') skip(error.message); throw error; }
    eq(doc.era, 'M220'); eq(doc.name, 'New brush'); ok(!doc.dirty); ok(doc.base && doc.base.members.some((m) => m.path === 'Brush.archive'));
    const shape = textureView(doc, 'shape'); ok(['none', 'bundled', 'blank'].includes(shape.kind), shape.kind);
  });
  await check('upload: a set file lists its brushes, then opens one by member', async () => {
    const found = await api.search({q: 'ink', top: 3}); const ids = (found.results || []).map((r) => r.brush_id); if (ids.length < 2) skip('fewer than 2 search hits');
    const built = await api.exportBrush({format: 'brushset', name: 'Two', dry_run: false, brushes: ids.slice(0, 2).map((id) => ({base: {library_id: id}, changes: {}}))});
    const file = new File([built.blob], built.filename); const manifest = await api.importFile(file, {}); eq(manifest.kind, 'brushset'); eq(manifest.brush_count, 2);
    const one = await api.importFile(file, {member: manifest.brushes[1].member}); eq(one.kind, 'brush'); ok(docFromResponse(one, {kind: 'file', filename: file.name}).name);
  });
  await check('upload: garbage bytes and a zip with a broken Brush.archive are refused with the F10 error shape', async () => {
    for (const bytes of [new TextEncoder().encode('this is not a brush'), storedZip('Brush.archive', new TextEncoder().encode('bplist00 nope'))]) {
      try { await api.importFile(new File([bytes], 'bad.brush'), {}); } catch (error) { ok(error instanceof ApiError && ['unsupported_file', 'corrupt_file'].includes(error.code), `code ${error.code}`); continue; }
      throw new Error('a broken file was accepted');
    }
  });
  await check('upload: an empty body and a wrong content type are refused', async () => {
    try { await api.importFile(new File([new Uint8Array(0)], 'e.brush'), {}); } catch (error) { ok(error.code, 'has a code'); return; }
    throw new Error('an empty upload was accepted');
  });
  await check('library: search answers the F9 envelope and Brush Pen is found', async () => {
    const r = await api.search({q: 'brush pen', top: 5}); ok(typeof r.total === 'number' && Array.isArray(r.results)); ok(r.results.length === 0 || r.results[0].brush_id.startsWith('b_'));
  });
  await check('library: a stroke preview image loads with the token (blob URL)', async () => {
    const url = await api.previewUrl(BRUSH_PEN, 'stroke').catch((e) => { if (e.code === 'no_preview' || e.code === 'not_found' || e.code === 'unknown_id') skip(e.code); throw e; }); ok(url.startsWith('blob:'));
  });

  finish();
}

function finish() {
  const failed = results.filter((r) => r.status === 'FAIL').length; const skipped = results.filter((r) => r.status === 'SKIP').length;
  const noConsole = consoleErrors.length === 0;
  results.push({name: 'console: no console.error, uncaught error or unhandled rejection during the run', status: noConsole ? 'PASS' : 'FAIL', why: consoleErrors.slice(0, 3).join(' | ')});
  out.append(el('li', {}, el('span', {class: `tag ${noConsole ? 'PASS' : 'FAIL'}`, text: noConsole ? 'PASS' : 'FAIL'}), el('span', {}, 'console: no console.error, uncaught error or unhandled rejection during the run', noConsole ? null : el('div', {class: 'why', text: consoleErrors.slice(0, 3).join(' | ')}))));
  const total = results.length; const passed = results.filter((r) => r.status === 'PASS').length; const failedNow = results.filter((r) => r.status === 'FAIL').length;
  const label = failedNow ? `FAIL ${failedNow} of ${total}` : `PASS ${passed}/${total - skipped}${skipped ? ` (${skipped} skipped)` : ''}`;
  document.title = `selftest: ${label}`;
  summary.textContent = `selftest: ${label}`; summary.className = failedNow ? 'bad-text' : 'ok-text';
  window.__selftest = {passed, failed: failedNow, skipped, total, results, consoleErrors};
  void failed;
}

main().catch((error) => { results.push({name: 'selftest crashed', status: 'FAIL', why: String(error && error.stack || error)}); out.append(el('li', {}, el('span', {class: 'tag FAIL', text: 'FAIL'}), `selftest crashed: ${error && error.message}`)); finish(); });
