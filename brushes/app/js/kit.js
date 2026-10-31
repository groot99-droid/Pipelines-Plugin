// kit.js - the pure parts of the extra exports: the Universal Kit's recipe
// text, the ink / mask pixel math, a zip directory reader and the plain-words
// description of every export format. No DOM, no network; importable from Node.
//
// F10 "What the code settled": a kit is a zip whose entries are limited to
// gimp/*.gbr, ink/*.png, mask/*.png, stroke-preview.png and brush-recipe.md
// (plus one optional <slug>.brush the server adds). The SERVER zips; the page
// supplies those files in the request's `files` ([{path, b64}]).

import {formatValue} from './schema.js';

/** What each format is for, in plain words (shown beside its button and in its result). */
export const FORMAT_NOTES = {
  brush: {
    title: '.brush',
    what: 'One brush as a Procreate brush file.',
    contains: 'The brush’s own archive with your changes, its shape and grain images and its thumbnail.',
    use: 'For Procreate on iPad. Not proven to open there yet: see brushes/device-tests/.',
  },
  brushset: {
    title: '.brushset',
    what: 'Several brushes in one Procreate brush set file.',
    contains: 'Each brush as above, plus the set’s name list.',
    use: 'For Procreate on iPad. Not proven to open there yet.',
  },
  gbr: {
    title: '.gbr (GIMP brush)',
    what: 'The brush’s shape as a GIMP brush tip.',
    contains: 'One grey stamp image (white is paint) and a spacing number. It does not carry the grain, pressure, taper or any other setting.',
    use: 'For GIMP, and for Krita, which can load .gbr files as brush tips. Not tested in either.',
  },
  kit: {
    title: 'Universal Kit (.zip)',
    what: 'The brush’s pictures and settings for painting apps that cannot read Procreate files.',
    contains: 'gimp/…gbr (the shape), ink/…png (black ink on transparent) and mask/…png (grey, white is paint) for the shape and the grain, stroke-preview.png (the brush’s own thumbnail), and brush-recipe.md (every setting in words).',
    use: 'For apps with a “make a brush from a picture” tool. None of it is a native brush file for those apps, and none of it has been tried in them.',
  },
  source: {
    title: 'App source (.zip)',
    what: 'The files this page is made of, as the server serves them.',
    contains: 'HTML, CSS, JavaScript and the schema files. No brush, no token.',
    use: 'For keeping a copy or reading the code.',
  },
};

export const KIT_ENTRY = /^(?:gimp\/[A-Za-z0-9._ -]{1,64}\.gbr|(?:ink|mask)\/[A-Za-z0-9._ -]{1,64}\.png|stroke-preview\.png|brush-recipe\.md)$/;

export function slugName(name) {
  const slug = String(name || '').toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 40).replace(/-+$/, '');
  return slug || 'brush';
}

export function fitSize(width, height, maxSide) {
  const scale = Math.min(1, maxSide / Math.max(width, height));
  return {width: Math.max(1, Math.round(width * scale)), height: Math.max(1, Math.round(height * scale))};
}

/** Coverage 0..255 per pixel from RGBA data: luminance (255 - luminance when inverted) times alpha, as the server does for a .gbr. */
export function coverageFromRgba(data, {inverted = false} = {}) {
  const n = data.length >> 2;
  const out = new Uint8Array(n);
  for (let i = 0; i < n; i += 1) {
    const r = data[i * 4]; const g = data[i * 4 + 1]; const b = data[i * 4 + 2]; const a = data[i * 4 + 3];
    const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    out[i] = Math.round(((inverted ? 255 - lum : lum) * a) / 255);
  }
  return out;
}

/** Opaque grey RGBA: white is paint. */
export function maskRgba(coverage) {
  const out = new Uint8ClampedArray(coverage.length * 4);
  for (let i = 0; i < coverage.length; i += 1) { out[i * 4] = coverage[i]; out[i * 4 + 1] = coverage[i]; out[i * 4 + 2] = coverage[i]; out[i * 4 + 3] = 255; }
  return out;
}

/** Black ink on transparent: alpha is the coverage. */
export function inkRgba(coverage) {
  const out = new Uint8ClampedArray(coverage.length * 4);
  for (let i = 0; i < coverage.length; i += 1) out[i * 4 + 3] = coverage[i];
  return out;
}

const SIG_END = 0x06054b50; const SIG_CENTRAL = 0x02014b50;

/** The entries of a zip from its central directory: [{name, size, packed, method, offset}]. Throws on anything that is not a plain zip. */
export function listZip(bytes) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  let end = -1;
  for (let i = bytes.length - 22; i >= Math.max(0, bytes.length - 22 - 65535); i -= 1) { if (view.getUint32(i, true) === SIG_END) { end = i; break; } }
  if (end < 0) throw new Error('not a zip: no end-of-directory record');
  const count = view.getUint16(end + 10, true);
  let at = view.getUint32(end + 16, true);
  const entries = [];
  for (let n = 0; n < count; n += 1) {
    if (at + 46 > bytes.length || view.getUint32(at, true) !== SIG_CENTRAL) throw new Error('bad zip directory');
    const nameLength = view.getUint16(at + 28, true); const extra = view.getUint16(at + 30, true); const comment = view.getUint16(at + 32, true);
    entries.push({name: new TextDecoder().decode(bytes.subarray(at + 46, at + 46 + nameLength)), size: view.getUint32(at + 24, true),
      packed: view.getUint32(at + 20, true), method: view.getUint16(at + 10, true), offset: view.getUint32(at + 42, true)});
    at += 46 + nameLength + extra + comment;
  }
  return entries;
}

const cell = (text) => String(text).replace(/\|/g, '\\|').replace(/[\r\n]+/g, ' ');

/**
 * The text of brush-recipe.md. `schema` is the indexed silica_keys.json,
 * `settings` the brush's effective settings (what the export would hold).
 */
export function recipeMarkdown({name, era, libraryId, schema, settings, paths, notes = [], gbrSpacing = null}) {
  const lines = [];
  lines.push(`# ${name || 'Untitled brush'}`, '');
  lines.push(`This kit was made from ${libraryId ? `the library brush ${libraryId}` : 'a brush opened in the ROSW brushes app'}${era ? ` (era ${era})` : ''}. `
    + 'It is the brush’s pictures and its settings written out in words.', '');
  lines.push('Nothing here has been tried in GIMP, Krita, Photoshop, Affinity, Clip Studio Paint or any other app, and none of it is a native brush file for them. '
    + 'Check each file in your own app.', '');
  lines.push('## What is in this kit', '');
  const explain = {
    gbr: 'a GIMP brush tip made from the shape (grey, white is paint)',
    ink: 'black ink on a transparent background, for apps that make a brush from a picture',
    mask: 'the same picture as plain grey, white is paint, black is nothing',
    'stroke-preview.png': 'the thumbnail stored in the brush (a stroke drawn by Procreate when the brush was made)',
    'brush-recipe.md': 'this file',
  };
  for (const path of paths) {
    const kind = path.startsWith('gimp/') ? 'gbr' : path.startsWith('ink/') ? 'ink' : path.startsWith('mask/') ? 'mask' : path;
    lines.push(`- \`${path}\`: ${explain[kind] || (path.endsWith('.brush') ? 'the Procreate brush itself' : 'a file')}`);
  }
  if (!paths.some((p) => p.startsWith('gimp/'))) lines.push('- (no .gbr: this brush’s shape is not an image that could be written)');
  for (const note of notes) lines.push(`- Note: ${note}`);
  lines.push('', '## Bringing it into other apps', '');
  lines.push('- Photoshop, Affinity, Clip Studio Paint and similar: open the ink picture and use the app’s “brush from image” tool (in Photoshop, Edit > Define Brush Preset).');
  lines.push('- Krita: Settings > Manage Resources > Import Resources, then choose the .gbr or the ink picture.');
  lines.push('- GIMP: put the .gbr in a brushes folder listed in Edit > Preferences > Folders > Brushes.');
  if (gbrSpacing) lines.push(`- The .gbr was written with spacing ${gbrSpacing}% of the brush width (a number you chose, not one read from the brush).`);
  lines.push('', '## Settings', '', 'Values as Procreate stores them, with this app’s label. A label with confidence “inferred” is a guess from the key name.', '');
  if (schema) {
    for (const group of schema.groups) {
      if (group.id === 'ai' || group.id === 'about') continue;
      const rows = (schema.rowsByGroup.get(group.id) || []).filter((row) => row.confidence !== 'unknown' && row.ui !== 'hidden'
        && Object.prototype.hasOwnProperty.call(settings, row.key));
      if (!rows.length) continue;
      lines.push(`### ${group.label}`, '', '| Setting | Value | Key |', '|---|---|---|');
      for (const row of rows) lines.push(`| ${cell(row.label)} | ${cell(formatValue(row, settings[row.key]))} | \`${row.key}\` |`);
      lines.push('');
    }
  } else {
    lines.push('(The schema could not be loaded, so the settings are not listed.)', '');
  }
  lines.push('_Written by the ROSW brushes app._', '');
  return lines.join('\n');
}

/** Pure checks: [{name, run}]. */
export function kitTests() {
  const tests = [];
  const t = (name, run) => tests.push({name, run});
  const ok = (c, m) => { if (!c) throw new Error(m || 'assertion failed'); };
  const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error(`${m || 'not equal'}: got ${JSON.stringify(a)}, wanted ${JSON.stringify(b)}`); };
  t('kit: slugs are file-safe and every kit path the app writes passes the server’s entry rule', () => {
    eq(slugName('Brush Pen!  ÄÖ'), 'brush-pen-ao'); eq(slugName('   '), 'brush'); ok(slugName('x'.repeat(200)).length <= 40);
    for (const p of ['gimp/brush-pen.gbr', 'ink/shape-ink.png', 'mask/grain-mask.png', 'stroke-preview.png', 'brush-recipe.md']) ok(KIT_ENTRY.test(p), p);
    for (const p of ['../x.png', 'gimp/a/b.gbr', 'ink/x.jpg', 'readme.txt', 'Brush.archive']) ok(!KIT_ENTRY.test(p), p);
  });
  t('kit: ink is black with the coverage as alpha, mask is the coverage as grey, and inverted flips white and black', () => {
    const px = new Uint8ClampedArray([255, 255, 255, 255, 0, 0, 0, 255, 255, 255, 255, 0, 128, 128, 128, 255]);
    eq(Array.from(coverageFromRgba(px)), [255, 0, 0, 128]); eq(Array.from(coverageFromRgba(px, {inverted: true})), [0, 255, 0, 127]);
    const cov = coverageFromRgba(px);
    eq(Array.from(maskRgba(cov).slice(0, 4)), [255, 255, 255, 255]); eq(Array.from(inkRgba(cov).slice(0, 8)), [0, 0, 0, 255, 0, 0, 0, 0]);
  });
  t('kit: fitSize keeps the aspect ratio and never enlarges', () => {
    eq(fitSize(2048, 1024, 1024), {width: 1024, height: 512}); eq(fitSize(64, 32, 1024), {width: 64, height: 32});
  });
  t('kit: the recipe names the files, the caveat and the settings with labels, and escapes table cells', () => {
    const schema = {groups: [{id: 'stroke', label: 'Stroke path'}], rowsByGroup: new Map([['stroke', [
      {key: 'plotSpacing', label: 'Spacing | gap', confidence: 'inferred', ui: 'slider', display: 'raw'},
      {key: 'mystery', label: 'Mystery', confidence: 'unknown', ui: 'number', display: 'raw'}]]])};
    const text = recipeMarkdown({name: 'Test', era: 'M220', libraryId: 'b_0123456789ab', schema, settings: {plotSpacing: 0.25, mystery: 1},
      paths: ['gimp/test.gbr', 'ink/shape-ink.png', 'mask/shape-mask.png', 'brush-recipe.md'], gbrSpacing: 12});
    ok(text.includes('# Test') && text.includes('b_0123456789ab') && text.includes('Nothing here has been tried'), 'header and caveat');
    ok(text.includes('| Spacing \\| gap | 0.25 | `plotSpacing` |'), 'row'); ok(!text.includes('Mystery'), 'unknown-meaning keys are left out'); ok(text.includes('spacing 12%'));
    ok(!/Studio Headless/.test(text), 'no branding line');
  });
  t('kit: the zip reader lists a stored zip and refuses a non-zip', () => {
    const name = new TextEncoder().encode('a.txt'); const data = new TextEncoder().encode('hi');
    const local = new Uint8Array(30 + name.length + data.length); const lv = new DataView(local.buffer);
    lv.setUint32(0, 0x04034b50, true); lv.setUint32(18, 2, true); lv.setUint32(22, 2, true); lv.setUint16(26, name.length, true); local.set(name, 30); local.set(data, 30 + name.length);
    const central = new Uint8Array(46 + name.length); const cv = new DataView(central.buffer);
    cv.setUint32(0, 0x02014b50, true); cv.setUint32(20, 2, true); cv.setUint32(24, 2, true); cv.setUint16(28, name.length, true); central.set(name, 46);
    const end = new Uint8Array(22); const ev = new DataView(end.buffer);
    ev.setUint32(0, SIG_END, true); ev.setUint16(8, 1, true); ev.setUint16(10, 1, true); ev.setUint32(12, central.length, true); ev.setUint32(16, local.length, true);
    const zip = new Uint8Array(local.length + central.length + end.length); zip.set(local); zip.set(central, local.length); zip.set(end, local.length + central.length);
    eq(listZip(zip), [{name: 'a.txt', size: 2, packed: 2, method: 0, offset: 0}]);
    let threw = false; try { listZip(new Uint8Array(40)); } catch (_) { threw = true; } ok(threw);
  });
  t('kit: every format has plain words for what it is, holds and is for, and none claims Procreate opens it', () => {
    for (const [id, n] of Object.entries(FORMAT_NOTES)) { ok(n.what && n.contains && n.use && n.title, id); ok(!/opens in Procreate|works in Procreate/i.test(`${n.what}${n.use}`), id); }
  });
  return tests;
}

/** The bytes of one entry (stored or deflated); needs DecompressionStream for a deflated one. */
export async function readZipEntry(bytes, entry) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const start = entry.offset + 30 + view.getUint16(entry.offset + 26, true) + view.getUint16(entry.offset + 28, true);
  const packed = bytes.subarray(start, start + entry.packed);
  if (entry.method === 0) return packed.slice();
  if (entry.method !== 8 || typeof DecompressionStream !== 'function') throw new Error('this entry cannot be unpacked here');
  const stream = new Blob([packed]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
  return new Uint8Array(await new Response(stream).arrayBuffer());
}
