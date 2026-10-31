// browser-checks.js - the stroke engine's checks that need the browser and the
// real library (selftest.js calls runEngineChecks in place of the old placeholder
// check). Read only: they open library brushes and draw to a detached canvas.
//
//   - two renders of the same settings give the same pixel hash
//   - a changed setting changes the pixels, an ignored one does not
//   - inverting an embedded shape changes the picture
//   - a brush of every era (E0..E4, the M series) draws without an exception
//   - compare / tall layouts size the canvas
//   - the timing of a render is logged (never asserted)

import {createEngine, ENGINE_NAME, supportDifferences} from '../engine.js';
import {previewOpts} from './opts.js';
import {textureView} from '../textures.js';
import {blobFromB64} from '../b64.js';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function urlMaker() {
  const urls = new Map();
  return {
    urlFor(slot, b64) {
      if (!b64) return null;
      const key = `${slot}:${b64.length}:${b64.slice(0, 40)}:${b64.slice(-40)}`;
      if (!urls.has(key)) urls.set(key, URL.createObjectURL(blobFromB64(b64)));
      return urls.get(key);
    },
    release() { for (const u of urls.values()) URL.revokeObjectURL(u); urls.clear(); },
  };
}

export async function runEngineChecks({check, ok, eq, skip, api, schema, libraryDoc, openLibraryBrush}) {
  const maker = urlMaker();
  const opts = (doc, extra) => previewOpts(doc, maker.urlFor, {width: 360, final: true, ...(extra || {})});
  const fresh = () => { const canvas = document.createElement('canvas'); return {canvas, engine: createEngine(canvas, {persist: false})}; };
  const timing = {};

  await check('engine: the stroke engine draws Brush Pen; the same settings give the same pixel hash; the bundled shape is a labelled stand-in', async () => {
    const doc = await libraryDoc(); const {engine, canvas} = fresh(); const params = doc.effective('main');
    const a = await engine.render(params, opts(doc)); eq(a.drew, 'stroke'); ok(a.stamps > 100, `stamps ${a.stamps}`);
    const b = await engine.refresh({force: true, settle: true}); eq(b.hash, a.hash, 'second render');
    const c = await engine.render({...params}, opts(doc, {width: 360})); eq(c.hash, a.hash, 'identical params');
    ok(a.standIn.shape && a.notes.some((n) => /stand-in|this is not it/.test(n)), 'a bundled shape must be reported as a stand-in');
    ok(canvas.width >= 160 && canvas.height > 40, `canvas ${canvas.width}x${canvas.height}`);
    const marks = []; for (let i = 0; i < 6; i += 1) { engine.setView({seed: 1 + (i % 2)}); const r = await engine.render(params, opts(doc)); marks.push(r.ms); }
    marks.sort((x, y) => x - y); timing.median = marks[marks.length >> 1]; timing.stamps = a.stamps; timing.ms = a.ms; timing.rasterMs = a.rasterMs;
    engine.dispose(); eq((await engine.render(params, opts(doc))).drew, 'nothing');
  });

  await check(`engine: timing of a 360 px Brush Pen render is logged, not asserted (${JSON.stringify({firstMs: Math.round(timing.ms || 0), medianMs: Math.round(timing.median || 0), stamps: timing.stamps})})`, async () => { /* informational */ });

  await check('engine: a changed setting changes the pixels; an ignored one (and an unrelated one) does not', async () => {
    const doc = await libraryDoc(); const {engine} = fresh(); const params = doc.effective('main');
    const base = await engine.render(params, opts(doc));
    const spaced = await engine.render({...params, plotSpacing: 0.6}, opts(doc)); ok(spaced.hash !== base.hash, 'plotSpacing is honoured, so it must change the picture');
    const thick = await engine.render({...params, maxSize: 0.8}, opts(doc)); ok(thick.hash !== base.hash, 'maxSize must change the picture');
    const same = await engine.render({...params, plotSmoothing: 0.9, dynamicsMix: 0.8, wetEdgesAmount: 1, blendMode: 5, name: 'another name'}, opts(doc));
    eq(same.hash, base.hash, 'ignored settings must not change the picture');
    engine.dispose();
  });

  await check('engine: inverting an embedded shape image flips the picture, and the real image is not called a stand-in', async () => {
    let doc; try { doc = await openLibraryBrush('b_72dacfda3c12'); } catch (error) { if (/library_missing|unknown_id|not_ingested/.test(error.code || '')) skip(error.code); throw error; }
    if (textureView(doc, 'shape').kind !== 'image') skip('this brush has no embedded shape here');
    const {engine} = fresh(); const params = doc.effective('main');
    const a = await engine.render(params, opts(doc)); ok(!a.standIn.shape, 'an embedded shape is the real image');
    const b = await engine.render({...params, shapeInverted: !params.shapeInverted}, opts(doc)); ok(a.hash !== b.hash, 'invert must change the picture');
    engine.dispose();
  });

  await check('engine: a brush of every era draws without an exception (E0..E4 and the M series, one each from the library)', async () => {
    const eras = (schema.raw.eras || []).map((e) => e.id); const drew = [];
    for (const era of eras) {
      let found; try { found = await api.search({where: [`era=${era}`], top: 1}); } catch (error) { skip(`search: ${error.code || error.message}`); }
      const hit = (found.results || [])[0]; if (!hit) continue;
      const doc = await openLibraryBrush(hit.brush_id); const {engine} = fresh();
      for (const extra of [{}, {compare: true}]) {
        if (extra.compare) engine.setView({compare: true, tall: true}); else engine.setView({compare: false, tall: false, stroke: 'auto'});
        const r = await engine.render(doc.effective('main'), opts(doc));
        ok(r.drew === 'stroke' && r.stamps >= 1 && typeof r.hash === 'string', `${era} ${hit.brush_id}: ${r.drew}`);
      }
      for (const stroke of ['line', 'scribble', 'tap']) { engine.setView({stroke, compare: false, tall: false}); const r = await engine.render(doc.effective('main'), opts(doc)); ok(r.drew === 'stroke', `${era} ${stroke}`); }
      engine.dispose(); drew.push(era);
    }
    ok(drew.length >= 5, `only ${drew.length} eras were in the library`);
  });

  await check('engine: the compare and tall layouts size the canvas; compare adds the stored thumbnail band', async () => {
    const doc = await libraryDoc(); const {engine, canvas} = fresh(); const params = doc.effective('main');
    await engine.setView({compare: false, tall: false}); await engine.render(params, opts(doc)); const plain = canvas.height;
    await engine.setView({compare: true}); await engine.render(params, opts(doc)); ok(canvas.height > plain * 1.9, `compare ${canvas.height} vs ${plain}`);
    await engine.setView({compare: false, tall: true}); await engine.render(params, opts(doc)); ok(canvas.height > plain * 1.5, `tall ${canvas.height} vs ${plain}`);
    engine.dispose();
  });

  await check('engine: a burst of edits (a slider drag) ends with a full-quality render', async () => {
    const doc = await libraryDoc(); const {engine} = fresh(); const params = doc.effective('main');
    const final = await engine.render(params, opts(doc)); const seen = [];
    engine.onresult = (r) => seen.push(r.drew);
    for (let i = 0; i < 5; i += 1) { await engine.render({...params, plotSpacing: 0.02 * (i + 1)}, {...opts(doc), final: false}); await sleep(30); }
    await sleep(700); engine.onresult = null;
    ok(seen.length >= 5 && seen[seen.length - 1] === 'stroke', `results ${seen.join(',')}`);
    ok(final.drew === 'stroke');
    engine.dispose();
  });

  await check('engine: the engine and the schema’s preview column differences are listed (information; the panels show the engine’s answer)', async () => {
    ok(typeof ENGINE_NAME === 'string'); ok(Array.isArray(supportDifferences(schema)));
  });

  maker.release();
}
