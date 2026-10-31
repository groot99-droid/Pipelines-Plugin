// selftest-library.js - the phase 3c checks, run from selftest.js by one line:
//   await (await import('./selftest-library.js')).run({check, ok, eq, skip, api, schema});
//
// Real server, real library, read only: exports are built in memory and only
// their bytes are compared; nothing is saved. The Library tab and the AI tab are
// mounted on the page and driven the way a user would (clicks on their buttons).

import {el} from './dom.js';
import {ApiError, tokenForLinks} from './api.js';
import {mountLibrary} from './library.js';
import {createBasket, exportBasket, exportSource, brushSpec, runExport} from './exporter.js';
import {openLibraryBrush} from './opener.js';
import {validateBody, createPatchBox} from './patchbox.js';
import {renderAiTab} from './ai.js';
import {buildRequest, REQUEST_LIMIT, promptTests} from './ai/prompt.js';
import {NUDGES, nudgeTests, makeNudge} from './ai/nudges.js';
import {libraryStateTests} from './library/state.js';
import {kitTests, listZip, readZipEntry, KIT_ENTRY} from './kit.js';
import {buildKitFiles} from './kit-build.js';
import {schemaIndex} from './schema-load.js';
import {textureView} from './textures.js';
import {pngInfo, b64ToBytes} from './b64.js';
import {PATCH_SCHEMA} from './patch.js';

const BRUSH_PEN = 'b_e9fe9907bee5';
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function waitFor(fn, what, ms = 10000) {
  const end = Date.now() + ms;
  for (;;) {
    const value = fn();
    if (value) return value;
    if (Date.now() > end) throw new Error(`timed out waiting for ${what}`);
    await sleep(40);
  }
}

/** The pure checks of every 3c module: [{name, run}]. */
export function libraryPureTests(schema) {
  return [...libraryStateTests(), ...promptTests(schema), ...nudgeTests(schema), ...kitTests()];
}

export async function run({check, ok, eq, skip, api, schema}) {
  for (const test of libraryPureTests(schema)) await check(`pure: ${test.name}`, () => test.run());

  const hosts = [];
  const newHost = () => { const host = el('div', {class: 'selftest-host'}); document.body.append(host); hosts.push(host); return host; };
  const opened = [];
  const makeCtx = (basket, over = {}) => ({api, openInDesigner: (id) => opened.push(id), addToSet: (id, name) => basket.addLibrary(id, name), toast: () => {}, basket, ...over});
  const libDoc = async (id) => {
    try { return await openLibraryBrush(id); } catch (error) {
      if (['library_missing', 'unknown_id', 'not_ingested'].includes(error.code)) skip(`${error.code}: ${error.message}`);
      throw error;
    }
  };

  // the tab remembers the last words and layout; the self-test puts them back as it found them
  const pref = (key) => { try { return localStorage.getItem(`rosw.brushes.${key}`); } catch (_) { return null; } };
  const restore = (key, value) => { try { if (value === null) localStorage.removeItem(`rosw.brushes.${key}`); else localStorage.setItem(`rosw.brushes.${key}`, value); } catch (_) { /* no storage */ } };
  const kept = {q: pref('lib.q'), view: pref('lib.view')};

  // ── the Library tab ──
  const basket = createBasket();
  const host = newHost();
  const lib = mountLibrary(host, makeCtx(basket));
  let firstId = null; let firstSet = null; let wholeTotal = 0;

  await check('library: a search for “watercolour wash” renders cards with stroke thumbnails from the real API', async () => {
    await lib.search('watercolour wash');
    const st = lib.state();
    ok(st.total > 0, `total ${st.total}`); ok(st.cards > 0 && st.cards <= 24, `${st.cards} cards`); eq(st.ranking, 'cosine'); wholeTotal = st.total;
    const card = host.querySelector('li.brush-card'); firstId = card.dataset.id; firstSet = card.dataset.set;
    ok(/^b_[0-9a-f]{12}$/.test(firstId), firstId);
    ok(host.querySelector('.lib-count').textContent.includes('brushes'), host.querySelector('.lib-count').textContent);
    host.scrollIntoView({block: 'start'});
    await waitFor(() => host.querySelector('img.card-img[src^="blob:"]'), 'a stroke thumbnail to load');
    ok(host.querySelectorAll('button.card-name').length === st.cards, 'every card has a name button');
  });

  await check('library: the facet chips come from the API, a tag note says how few brushes are tagged, and a chip narrows the results', async () => {
    await waitFor(() => lib.facetPanel.chips().length > 10, 'the facet chips');
    const tagNote = [...host.querySelectorAll('.facet-more p')].map((p) => p.textContent).find((t) => /tagged/.test(t));
    ok(tagNote && /\d+ of \d+ brushes (are )?tagged/.test(tagNote), `tag note: ${tagNote}`);
    const candidates = ['e:kind:stamp', 'e:wet_mix:true', 'e:taper:both', 'e:has_grain:true', 'e:kind:stroke'];
    let narrowed = null;
    for (const cid of candidates) {
      const chip = lib.facetPanel.chips().find((b) => b.dataset.cid === cid && b.getAttribute('aria-disabled') !== 'true');
      if (!chip) continue;
      chip.click(); await lib.settled(); await sleep(60);
      const st = lib.state();
      if (st.total < wholeTotal) { narrowed = {cid, total: st.total}; break; }
      lib.facetPanel.chips().find((b) => b.dataset.cid === cid).click(); await lib.settled();
    }
    ok(narrowed, 'no candidate chip narrowed the results');
    const [, facet, value] = narrowed.cid.split(':');
    const direct = await api.search({q: 'watercolour wash', where: [`${facet}=${value}`], top: 1});
    eq(narrowed.total, direct.total, 'the tab and a direct API call disagree');
    ok(lib.facetPanel.chips().find((b) => b.dataset.cid === narrowed.cid).getAttribute('aria-pressed') === 'true', 'the chip shows it is on');
    ok(host.querySelector('.active-chips button'), 'an active-filter chip is listed');
    host.querySelector('.active-chips button').click(); await lib.settled();
    eq(lib.state().total, wholeTotal, 'removing the chip restores the results');
  });

  await check('library: a number range narrows the results, and a nonsense word gives the empty state with a way out', async () => {
    const from = await waitFor(() => host.querySelector('input[aria-label="Spacing (number), from"]'), 'the spacing range field');
    from.value = '0.5'; from.dispatchEvent(new Event('change', {bubbles: true})); await sleep(50); await lib.settled(); await sleep(60);
    const direct = await api.search({q: 'watercolour wash', where: ['spacing=0.5..'], top: 1});
    eq(lib.state().total, direct.total, 'range total'); ok(lib.state().total < wholeTotal, 'the range did not narrow');
    await lib.clearFilters(); eq(lib.state().total, wholeTotal);
    await lib.search('xqzvvkk'); eq(lib.state().total, 0); ok(host.querySelector('.lib-note .notice'), 'empty-state note');
    await lib.search('watercolour wash');
  });

  await check('library: Similar works in the detail drawer, and “other sets only” leaves out the brush’s own set', async () => {
    if (!firstId) skip('no search result');
    lib.drawer.open(firstId);
    await waitFor(() => host.querySelector('dialog.drawer[open] .drawer-body'), 'the drawer body');
    const dialog = host.querySelector('dialog.drawer');
    ok(dialog.querySelector('.drawer-title').textContent.length > 0);
    ok(dialog.textContent.includes('Where it lives') && dialog.textContent.includes('Tags and description') && dialog.textContent.includes('Vault note'), 'drawer sections');
    ok(/Not tagged yet/.test(dialog.textContent) || dialog.querySelector('.drawer-sec dl'), 'honest tag state');
    [...dialog.querySelectorAll('button')].find((b) => b.textContent === 'Find similar brushes').click();
    await waitFor(() => dialog.querySelector('.similar-box li.brush-card'), 'similar brushes');
    const plain = [...dialog.querySelectorAll('.similar-box li.brush-card')].map((li) => li.dataset);
    ok(plain.length > 0 && plain.every((d) => d.id !== firstId), 'the brush itself is not its own neighbour');
    ok(dialog.querySelector('.similar-box .card-note'), 'a difference line');
    const toggle = dialog.querySelector('#sim-other'); toggle.checked = true; toggle.dispatchEvent(new Event('change', {bubbles: true}));
    await sleep(100);
    await waitFor(() => dialog.querySelector('.similar-box li.brush-card') && !/Looking for/.test(dialog.querySelector('.similar-box').textContent), 'similar brushes from other sets');
    const other = [...dialog.querySelectorAll('.similar-box li.brush-card')].map((li) => li.dataset);
    ok(other.length > 0, 'some neighbours in other sets'); ok(other.every((d) => d.id !== firstId && d.set !== firstSet), `a neighbour from ${firstSet} remained`);
    dialog.close();
  });

  await check('library: the Sets browser lists the sets, and a set page lists its brushes in order', async () => {
    lib.setMode('sets');
    const rows = await waitFor(() => host.querySelectorAll('.set-rows .set-row').length && host.querySelectorAll('.set-rows .set-row'), 'the set list');
    ok(rows.length > 10, `${rows.length} sets`);
    rows[0].click();
    await waitFor(() => host.querySelector('.set-page li.brush-card'), 'a set page');
    ok(host.querySelectorAll('.set-page li.brush-card').length >= 1);
    ok([...host.querySelectorAll('.set-page button')].some((b) => /Add all \d+ to the set/.test(b.textContent)));
    lib.setMode('search');
  });

  await check('library: Add to set fills the basket (count in the header) and the basket exports a .brushset that reads back', async () => {
    basket.clear();
    const buttons = [...host.querySelectorAll('.lib-results li.brush-card .card-actions button')].filter((b) => b.textContent === 'Add to set');
    ok(buttons.length >= 2, 'two cards to add'); buttons[0].click(); buttons[1].click();
    eq(basket.items.length, 2); ok(lib.basketView.button.textContent === 'Set basket: 2', lib.basketView.button.textContent);
    const result = await exportBasket({basket, name: 'Selftest basket', save: false});
    ok(result.filename.endsWith('.brushset'), result.filename); ok(result.info && result.info.size === result.size); ok(result.sha256 === null || result.shaMatches === true);
    const back = await api.importFile(new File([result.bytes], result.filename), {});
    eq(back.kind, 'brushset'); eq(back.brush_count, 2);
    basket.clear(); eq(lib.basketView.button.textContent, 'Set basket: 0');
  });

  await check('library: Open in Designer calls the app, and only the words and the layout are remembered (never a token)', async () => {
    host.querySelector('li.brush-card .card-actions .btn-primary').click(); eq(opened.length, 1);
    eq(localStorage.getItem('rosw.brushes.lib.q'), 'watercolour wash');
    const token = tokenForLinks(); const keys = []; for (let i = 0; i < localStorage.length; i += 1) keys.push(localStorage.key(i));
    for (const key of keys) ok(!String(localStorage.getItem(key)).includes(token), `${key} holds the token`);
  });

  await check('library: a failing search shows the error with a retry, and a slow server is announced', async () => {
    const slowApi = {...api, search: async (p) => { await sleep(1100); return api.search(p); }};
    const h2 = newHost(); const l2 = mountLibrary(h2, makeCtx(createBasket(), {api: slowApi}));
    const pending = l2.search('ink'); await sleep(900);
    ok(/Still searching/.test(h2.querySelector('.lib-count').textContent), h2.querySelector('.lib-count').textContent); await pending;
    ok(l2.state().total > 0); l2.dispose();
    const failing = {...api, search: async () => { throw new ApiError('internal', 'The search exploded.', {status: 500, hint: 'Try again.'}); }};
    const h3 = newHost(); const l3 = mountLibrary(h3, makeCtx(createBasket(), {api: failing}));
    await l3.search('ink');
    const alert = h3.querySelector('.lib-note [role="alert"]'); ok(alert && /exploded/.test(alert.textContent) && /Try again/.test(alert.textContent), 'error note');
    ok(h3.querySelector('.lib-note button')); l3.dispose();
  });

  // ── the AI tab ──
  let pen = null;
  await check('ai: the request for Brush Pen holds the F3 envelope, the rules and a table of its own keys, fits the bound, and holds no token', async () => {
    pen = await libDoc(BRUSH_PEN);
    const text = buildRequest({schema, settings: pen.effective('main'), patch: pen.patch('main'), era: pen.era, name: pen.name, libraryId: pen.libraryId, wish: 'make this softer and grainier, like charcoal'});
    ok(text.includes(`"schema":"${PATCH_SCHEMA}"`) && text.includes(`"base_id":"${BRUSH_PEN}"`), 'envelope');
    ok(text.includes('make this softer and grainier, like charcoal') && text.includes('plotSpacing |') && text.includes('grainDepth |'), 'wish and table');
    ok(text.length < REQUEST_LIMIT, `${text.length} characters`);
    const token = tokenForLinks(); ok(!text.includes(token) && !/X-ROSW|#t=/.test(text), 'the request must not hold the token');
  });

  await check('ai: the tab shows Ollama is unavailable, builds the request from the live doc, and picks the patch out of a reply', async () => {
    if (!pen) skip('no brush');
    const h = newHost(); const box = createPatchBox({schema, getDoc: () => pen}); box.setDoc(pen); h.append(box.el);
    const tab = renderAiTab(h, {doc: pen, schema, layer: 'main', focusPatchBox: () => {}});
    ok(h.textContent.includes('Ollama is not available from this page') && h.textContent.includes('future server proxy'), 'Ollama note');
    h.querySelector('#ai-wish').value = 'darker please'; h.querySelector('#ai-wish').dispatchEvent(new Event('input', {bubbles: true}));
    ok(tab.requestText().includes('darker please'), 'the wish reaches the request');
    const reply = h.querySelector('#ai-reply');
    reply.value = `Softer it is.\n\n\`\`\`json\n{"schema":"${PATCH_SCHEMA}","base_id":"${BRUSH_PEN}","summary":"softer","changes":{"maxOpacity":0.7,"plotSpacing":0.2}}\n\`\`\``;
    reply.dispatchEvent(new Event('input', {bubbles: true}));
    const send = [...h.querySelectorAll('button')].find((b) => b.textContent === 'Check in the Patch box'); ok(!send.disabled, 'the send button is on');
    ok(/changes 2 settings/.test(h.textContent), 'found-patch line');
    send.click(); await waitFor(() => box.area.value.includes('maxOpacity'), 'the patch in the Patch box');
    await box.check(); await waitFor(() => /2 to apply/.test(box.el.textContent), 'the server check');
    reply.value = 'no patch here'; reply.dispatchEvent(new Event('input', {bubbles: true})); ok([...h.querySelectorAll('button')].find((b) => b.textContent === 'Check in the Patch box').disabled);
  });

  await check('ai: a suggestion is checked by the server, shown as a diff, applies as one undo step, and undo restores the brush', async () => {
    if (!pen) skip('no brush');
    const doc = await libDoc(BRUSH_PEN);
    const h = newHost(); renderAiTab(h, {doc, schema, layer: 'main', focusPatchBox: () => {}});
    h.querySelector('[data-nudge="softer"]').click();
    const apply = await waitFor(() => [...h.querySelectorAll('.ai-nudge-report button')].find((b) => /^Apply \d+ change/.test(b.textContent)), 'the Apply button');
    ok(h.querySelector('.ai-nudge-report table.diff'), 'a diff table'); ok(!doc.dirty, 'nothing changes before Apply');
    apply.click(); ok(doc.dirty && doc.dirtyCount >= 1); const steps = doc.historyLength; eq(steps, 2, 'one undo step');
    doc.undo(); ok(!doc.dirty, 'undo restores');
  });

  const nudgeBrushes = [['M220', BRUSH_PEN]];
  for (const era of ['E4', 'E2', 'E0']) {
    try { const found = await api.search({where: [`era=${era}`], top: 1}); if (found.results && found.results[0]) nudgeBrushes.push([era, found.results[0].brush_id]); } catch (_) { /* skipped below */ }
  }
  await check('ai: every suggestion preset gives a patch the server does not reject, on brushes of four eras', async () => {
    let made = 0; const seen = [];
    for (const [era, id] of nudgeBrushes) {
      let doc; try { doc = await openLibraryBrush(id); } catch (error) { if (id === BRUSH_PEN) skip(error.message); continue; }
      seen.push(`${doc.era}`);
      for (const nudge of NUDGES) {
        const r = makeNudge(nudge.id, {schema, settings: doc.effective('main'), era: doc.era, strength: 1});
        if (!Object.keys(r.changes).length) continue;
        const result = await api.validatePatch(validateBody(doc, r.changes));
        eq(result.rejected, [], `${nudge.id} on ${era} brush ${id} was rejected`); eq(Object.keys(result.applied).sort(), Object.keys(r.changes).sort(), `${nudge.id} on ${doc.era}: applied keys`);
        made += 1;
      }
    }
    ok(made >= 20, `only ${made} presets produced a patch (eras ${seen.join(', ')})`);
  });

  // ── .gbr, kit, source ──
  let shaped = null;
  const shapedDoc = async () => {
    if (shaped) return shaped;
    const found = await api.search({where: ['shape_source=embedded', 'grain_source=embedded'], top: 8});
    for (const r of found.results || []) {
      const doc = await libDoc(r.brush_id);
      if (textureView(doc, 'shape').kind === 'image' && textureView(doc, 'grain').kind === 'image') { shaped = doc; return doc; }
    }
    return null;
  };

  await check('export: a .gbr of an embedded shape is a GIMP version 2 brush with the shape’s size, the spacing asked for, and the server’s hash', async () => {
    const doc = await shapedDoc(); if (!doc) skip('no brush with an embedded shape and grain');
    const result = await runExport({format: 'gbr', brushes: [brushSpec(doc)], extra: {spacing: 12}, save: false});
    const b = result.bytes; const v = new DataView(b.buffer, b.byteOffset, b.byteLength);
    ok(result.filename.endsWith('.gbr'), result.filename); eq(String.fromCharCode(...b.slice(20, 24)), 'GIMP'); eq(v.getUint32(4), 2, 'version'); eq(v.getUint32(16), 1, 'bytes per pixel');
    eq(v.getUint32(24), 12, 'spacing');
    const shape = pngInfo(b64ToBytes(textureView(doc, 'shape').b64)); eq([v.getUint32(8), v.getUint32(12)], [shape.width, shape.height], 'size');
    ok(b.length > 28 + v.getUint32(8) * v.getUint32(12) - 1, 'body is there'); ok(result.shaMatches !== false && result.info.size === result.size, 'hash');
  });

  await check('export: a .gbr of a bundled shape is refused with a reason (no picture is made up)', async () => {
    if (!pen) skip('no brush');
    try { await api.exportBrush({format: 'gbr', dry_run: false, brushes: [brushSpec(pen)], spacing: 10}); } catch (error) {
      eq(error.code, 'bad_argument'); ok(/image inside the drawing app/.test(error.message), error.message); return;
    }
    throw new Error('a bundled shape was written as a .gbr');
  });

  await check('export: the Universal Kit holds only the allowed entries, the ink / mask pictures, the thumbnail and a recipe, and its hash matches', async () => {
    const doc = await shapedDoc(); if (!doc) skip('no brush with an embedded shape and grain');
    const gbr = await runExport({format: 'gbr', brushes: [brushSpec(doc)], extra: {spacing: 10}, save: false});
    const kit = await buildKitFiles(doc, {schema: await schemaIndex(), gbrBytes: gbr.bytes, gbrSpacing: 10});
    ok(kit.paths.includes('ink/shape-ink.png') && kit.paths.includes('mask/shape-mask.png') && kit.paths.includes('brush-recipe.md'), kit.paths.join(', '));
    const result = await runExport({format: 'kit', name: doc.name, brushes: [brushSpec(doc)], extra: {files: kit.files}, save: false});
    ok(result.filename.endsWith('.zip') && /-kit\.zip$/.test(result.info.filename), `${result.filename} / ${result.info && result.info.filename}`); ok(result.sha256 === null || result.shaMatches === true, 'hash');
    const entries = listZip(result.bytes); const names = entries.map((e) => e.name);
    ok(names.every((n) => KIT_ENTRY.test(n) || n.endsWith('.brush')), names.join(', '));
    ok(names.some((n) => n.startsWith('gimp/') && n.endsWith('.gbr')) && names.some((n) => n.endsWith('.brush')) && names.includes('stroke-preview.png'), names.join(', '));
    eq(result.report.members.map((m) => m.path).sort(), names.slice().sort(), 'the dry-run list and the zip agree');
    if (typeof DecompressionStream === 'function') {
      const ink = await readZipEntry(result.bytes, entries.find((e) => e.name === 'ink/shape-ink.png'));
      eq(Array.from(ink.slice(0, 4)), [0x89, 0x50, 0x4e, 0x47]); const info = pngInfo(ink); eq(info.colorType, 6, 'ink is RGBA');
      const recipe = new TextDecoder().decode(await readZipEntry(result.bytes, entries.find((e) => e.name === 'brush-recipe.md')));
      ok(recipe.includes(`# ${doc.name}`) && recipe.includes('Nothing here has been tried') && recipe.includes('plotSpacing'), 'recipe text');
    }
  });

  await check('export: the app source zip downloads, lists the app files and holds no token', async () => {
    const result = await exportSource({save: false});
    ok(result.filename.endsWith('.zip') && result.size > 1000, result.filename);
    const names = listZip(result.bytes).map((e) => e.name);
    ok(names.includes('index.html') && names.includes('js/library.js') && names.includes('js/ai.js') && names.includes('library.css'), names.slice(0, 8).join(', '));
    ok(!new TextDecoder().decode(result.bytes).includes(tokenForLinks()), 'the token is in the zip');
  });

  lib.dispose();
  for (const h of hosts) h.remove();
  restore('lib.q', kept.q); restore('lib.view', kept.view);
}
