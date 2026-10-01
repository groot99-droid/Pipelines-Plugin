// The Library: read every work of the vault, passage by passage, and look through the rooms.
// Reads data/library.json (written by build_museum.py build) and nothing else. Writes nothing
// but the last work read, in localStorage, so the page opens where it was left.
//
//   explore.html                      the works, opened on the last work read (or the first)
//   explore.html?work=<slug>          one work
//   explore.html?view=scenes          the rooms, in hall order
//   explore.html?view=scenes&scene=<id>   one room, found and marked
(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
  const words = (s) => s.replace(/-/g, ' ');
  const VERSE_TYPES = ['poem', 'prose-poem', 'song'];
  const TAG_FAMILIES = [['plot_tags', 'plot'], ['context_tags', 'context'], ['mood_tags', 'mood'], ['motif_tags', 'motif']];

  let lib = { folders: [], works: [], scenes: [] };
  let bySlug = new Map();
  let sceneById = new Map();
  let view = 'works';
  let current = null;          // slug of the work in the reader
  let shown = [];              // the slugs the shelf shows, in order (for ← →)
  let markedScene = null;

  // ---- data -------------------------------------------------------------------------------
  async function load() {
    const res = await fetch('../data/library.json', { cache: 'no-store' });
    if (!res.ok) throw new Error(`library.json: HTTP ${res.status}`);
    lib = await res.json();
    bySlug = new Map(lib.works.map((w) => [w.slug, w]));
    sceneById = new Map(lib.scenes.map((s) => [s.id, s]));
    for (const w of lib.works) {
      w._hay = [w.title, w.blurb, w.path, ...(w.themes || []), ...(w.genre || []), ...(w.archetypes || []),
        ...w.passages.map((p) => p.text)].join('\n').toLowerCase();
    }
  }

  // ---- url + memory -----------------------------------------------------------------------
  function readUrl() {
    const q = new URLSearchParams(location.search);
    return { view: q.get('view') === 'scenes' ? 'scenes' : 'works', work: q.get('work'), scene: q.get('scene') };
  }
  function writeUrl(replace = false) {
    const q = new URLSearchParams();
    if (view === 'scenes') {
      q.set('view', 'scenes');
      if (markedScene) q.set('scene', markedScene);
    } else if (current) {
      q.set('work', current);
    }
    const url = `${location.pathname}${q.toString() ? '?' + q : ''}`;
    if (replace) history.replaceState(null, '', url); else history.pushState(null, '', url);
  }
  function remember(slug) { try { localStorage.setItem('library:work', slug); } catch (e) { /* private mode */ } }
  function remembered() { try { return localStorage.getItem('library:work'); } catch (e) { return null; } }

  // ---- views ------------------------------------------------------------------------------
  function showView(name, { push = true } = {}) {
    view = name;
    $('view-works').hidden = name !== 'works';
    $('view-scenes').hidden = name !== 'scenes';
    for (const b of document.querySelectorAll('.view-tab')) b.setAttribute('aria-pressed', b.dataset.view === name ? 'true' : 'false');
    if (name === 'scenes') renderScenes();
    if (push) writeUrl();
  }

  // ---- the shelf --------------------------------------------------------------------------
  function fillSelect(select, values, label) {
    const keep = select.value;
    while (select.options.length > 1) select.remove(1);
    for (const [value, text] of values) {
      const o = document.createElement('option');
      o.value = value; o.textContent = text || label(value);
      select.append(o);
    }
    select.value = values.some(([v]) => v === keep) ? keep : '';
  }

  function filtered() {
    const q = $('q').value.trim().toLowerCase();
    const mode = $('mode').value;
    const folder = $('folder').value;
    const withRoom = $('withRoom').checked;
    return lib.works.filter((w) => (!q || w._hay.includes(q)) && (!mode || (w.mode || 'unclassified') === mode)
      && (!folder || w.folder === folder) && (!withRoom || w.scene));
  }

  function highlight(text, q) {
    if (!q) return esc(text);
    const i = text.toLowerCase().indexOf(q);
    if (i < 0) return esc(text);
    return esc(text.slice(0, i)) + '<mark>' + esc(text.slice(i, i + q.length)) + '</mark>' + esc(text.slice(i + q.length));
  }

  function renderShelf() {
    const q = $('q').value.trim().toLowerCase();
    const list = filtered();
    shown = list.map((w) => w.slug);
    const groups = new Map(lib.folders.map((f) => [f.folder, []]));
    for (const w of list) (groups.get(w.folder) || groups.set(w.folder, []).get(w.folder)).push(w);
    const html = [];
    for (const f of lib.folders) {
      const ws = groups.get(f.folder) || [];
      if (!ws.length) continue;
      html.push(`<h2>${esc(f.name)} <span>${ws.length}</span></h2>`);
      if (f.about && !q) html.push(`<p class="about">${esc(f.about)}</p>`);
      for (const w of ws) {
        const meta = [w.type ? words(w.type) : null, w.mode ? words(w.mode) : 'unclassified', `${w.words} words`].filter(Boolean).join(' · ');
        html.push(`<button type="button" class="spine${w.slug === current ? ' on' : ''}" data-slug="${esc(w.slug)}">
          <span class="t">${highlight(w.title, q)}</span>
          <span class="m">${esc(meta)}${w.scene ? ' · <span class="room">room</span>' : ''}</span></button>`);
      }
    }
    $('shelf').innerHTML = html.join('') || '<p class="empty">No work matches.</p>';
    $('shelfCount').textContent = list.length === lib.works.length ? `${lib.works.length} works` : `${list.length} of ${lib.works.length} works`;
  }

  // ---- the reader -------------------------------------------------------------------------
  function paragraphs(text) {
    return text.split(/\n{2,}/).map((p) => `<p>${esc(p)}</p>`).join('');
  }

  function chips(items, cls) {
    return (items || []).map((t) => `<li class="chip ${cls}">${esc(words(t))}</li>`).join('');
  }

  function openWork(slug, { push = true, scroll = true } = {}) {
    const w = bySlug.get(slug);
    if (!w) return;
    current = slug;
    remember(slug);
    const folder = lib.folders.find((f) => f.folder === w.folder);
    const verse = VERSE_TYPES.includes(w.type);
    const scene = w.scene ? sceneById.get(w.scene) : null;
    const n = w.passages.length;
    const meta = [w.mode ? `${words(w.mode)} mode` : 'unclassified mode', w.status, w.pov ? words(w.pov) : null, w.tense ? `${w.tense} tense` : null,
      `${w.words} words`, `${n} passage${n === 1 ? '' : 's'}`].filter(Boolean).join(' · ');
    const source = w.source_volume ? `${esc(w.source_volume)}${w.source_lines ? `, lines ${esc(w.source_lines)}` : ''}` : '';
    const idx = shown.indexOf(slug);
    const prev = idx > 0 ? bySlug.get(shown[idx - 1]) : null;
    const next = idx >= 0 && idx < shown.length - 1 ? bySlug.get(shown[idx + 1]) : null;

    const passages = w.passages.map((p) => {
      const title = p.heading && p.heading.trim().toLowerCase() !== w.title.trim().toLowerCase() ? p.heading : `Passage ${p.n} of ${n}`;
      const tags = TAG_FAMILIES.flatMap(([fam, k]) => (p.tags[fam] || []).map((t) => `<span class="chip ${k}">${esc(words(t))}</span>`));
      const foot = p.tagged && tags.length ? `<footer><span class="chip k">tags</span>${tags.join('')}</footer>` : '';
      return `<article class="passage${verse ? ' verse' : ''}" id="p${p.n}">
        <header><h2>${esc(title)}</h2><span class="cite">lines ${p.lines[0]}–${p.lines[1]}</span></header>
        <div class="text">${paragraphs(p.text)}</div>${foot}</article>`;
    }).join('');

    $('reader').innerHTML = `
      <p class="eyebrow">${esc(folder ? folder.name : w.folder)}${w.type ? ` · ${esc(words(w.type))}` : ''}</p>
      <h1>${esc(w.title)}</h1>
      <p class="meta">${esc(meta)}</p>
      ${w.blurb ? `<p class="blurb">${esc(w.blurb)}</p>` : ''}
      <ul class="chips">${chips(w.themes, 'theme')}${chips(w.genre, 'genre')}${chips(w.archetypes, 'arch')}</ul>
      <p class="source"><code>${esc(w.path)}</code>${source ? ` · ${source}` : ''}</p>
      <div class="actions">
        ${scene ? `<a class="primary" href="index.html?room=${encodeURIComponent(scene.id)}">Walk its room →</a>
                   <button type="button" data-scene="${esc(scene.id)}">Look at the scene</button>`
                : `<span class="noroom">No room yet. A <code>scene-3d</code> run would make one; <code>build_museum.py propose ${esc(w.path)}</code> previews what the mapping suggests.</span>`}
      </div>
      <div class="passages">${passages}</div>
      <nav class="pager" aria-label="Previous and next work">
        <button type="button" data-go="${prev ? esc(prev.slug) : ''}" ${prev ? '' : 'disabled'}><span class="d">← previous</span>${prev ? esc(prev.title) : 'start of the shelf'}</button>
        <button type="button" data-go="${next ? esc(next.slug) : ''}" ${next ? '' : 'disabled'}><span class="d">next →</span>${next ? esc(next.title) : 'end of the shelf'}</button>
      </nav>`;
    for (const b of document.querySelectorAll('.spine')) b.classList.toggle('on', b.dataset.slug === slug);
    const on = document.querySelector('.spine.on');
    if (on && scroll) on.scrollIntoView({ block: 'nearest' });
    if (scroll) window.scrollTo({ top: 0 });
    if (push) writeUrl();
  }

  function step(delta) {
    if (view !== 'works' || !current) return;
    const idx = shown.indexOf(current);
    const to = shown[idx + delta];
    if (to) openWork(to);
  }

  // ---- the scenes -------------------------------------------------------------------------
  function hallSvg() {
    const scenes = lib.scenes;
    const W = 1000, H = 220, L = 60, R = 60, top = 55, bottom = 165;
    const n = Math.max(1, Math.max(...scenes.map((s) => s.order), 0));
    const slots = Math.ceil(n / 2) || 1;
    const pitch = (W - L - R - 80) / Math.max(1, slots);
    const x = (order) => L + 40 + (Math.ceil(order / 2) - 0.5) * pitch;
    const parts = [`<rect class="floor" x="${L}" y="${top}" width="${W - L - R}" height="${bottom - top}" />`,
      `<circle class="rotunda" cx="${L}" cy="${(top + bottom) / 2}" r="40" />`,
      `<text class="label" x="${L - 30}" y="${(top + bottom) / 2 + 5}">entrance</text>`,
      `<text class="label" x="${W / 2}" y="${(top + bottom) / 2 + 5}" text-anchor="middle">the hall</text>`,
      `<text class="label" x="${W - R + 6}" y="${top - 30}" text-anchor="end">north side</text>`,
      `<text class="label" x="${W - R + 6}" y="${bottom + 44}" text-anchor="end">south side</text>`];
    for (const s of scenes) {
      const cx = x(s.order);
      const south = s.hub_side === 'S';
      const y = south ? bottom - 8 : top - 8;
      const ly = south ? bottom + 28 : top - 18;
      parts.push(`<g class="door-hit${s.id === markedScene ? ' on' : ''}" data-scene="${esc(s.id)}" tabindex="0" role="button" aria-label="${esc(s.name)}, door ${s.order}">
        <rect x="${cx - 22}" y="${south ? bottom - 30 : top - 10}" width="44" height="54" fill="transparent" />
        <rect class="door ${south ? 'S' : 'N'}" x="${cx - 14}" y="${y}" width="28" height="16" rx="2" />
        <text class="num" x="${cx}" y="${y + 12.5}">${s.order}</text>
        <text class="name" x="${cx}" y="${ly}">${esc(shortName(s.name))}</text></g>`);
    }
    return parts.join('');
  }

  function shortName(name) {
    const base = name.split(/\s[-–—]\s/)[0];
    return base.length > 22 ? base.slice(0, 21).trimEnd() + '…' : base;
  }

  function bright(hex) {
    const m = /^#([0-9a-f]{6})$/i.exec(hex || '');
    if (!m) return false;
    const v = parseInt(m[1], 16);
    const lum = 0.2126 * (v >> 16 & 255) + 0.7152 * (v >> 8 & 255) + 0.0722 * (v & 255);
    return lum > 150;
  }

  function sceneCard(s) {
    const w = bySlug.get(s.slug) || lib.works.find((x) => x.path === s.work);
    const st = s.style || {};
    const light = st.light || {};
    const size = s.size && s.size.length === 2 ? `${s.size[0]} × ${s.size[1]} m` : '—';
    const minis = Array.from({ length: Math.min(4, s.passages) }, (_, i) => `<div class="mini${i % 3 === 2 ? ' wide' : ''}"></div>`).join('');
    const sources = Object.entries(s.sources || {}).map(([k, v]) => `<li><code>${esc(k)}</code> — ${esc(v)}</li>`).join('');
    return `<article class="scene${s.id === markedScene ? ' on' : ''}" id="scene-${esc(s.id)}" data-scene="${esc(s.id)}">
      <div class="swatch${bright(st.wall) ? ' bright' : ''}" style="background:${esc(st.wall || '#8a7a66')}">
        <span class="door-mark">${esc(words(st.theme || 'default'))} door</span>
        <span class="lamp" title="light ${esc(light.color || '')} at ${esc(light.intensity ?? '')}" style="background:${esc(light.color || '#ffd9a8')};box-shadow:0 0 ${Math.round((light.intensity || 180) / 12)}px ${esc(light.color || '#ffd9a8')}"></span>
        ${minis}
      </div>
      <div class="body">
        <h2><span class="n">door ${s.order} · ${s.hub_side === 'S' ? 'south' : 'north'}</span>${esc(s.name || (w && w.title) || s.id)}</h2>
        <p class="what">${esc((s.intro && s.intro.summary) || '')}</p>
        <dl>
          <dt>wall</dt><dd><span class="dot" style="background:${esc(st.wall || '')}"></span>${esc(st.wall || 'default')}</dd>
          <dt>light</dt><dd><span class="dot" style="background:${esc(light.color || '')}"></span>${esc(light.color || 'default')}${light.intensity != null ? ` at ${esc(light.intensity)}` : ''}</dd>
          <dt>floor</dt><dd>${esc(words(st.floor || 'default'))}</dd>
          <dt>trim</dt><dd>${esc(words(st.trim || 'default'))}</dd>
          <dt>frames</dt><dd>${esc(words(st.frame || 'default'))}${st.frame_small ? `, small ${esc(words(st.frame_small))}` : ''}</dd>
          <dt>room</dt><dd>${esc(size)} · ${s.passages} passage${s.passages === 1 ? '' : 's'}${s.panels !== 'all' ? ` (chunks ${esc((s.panels || []).join(', '))})` : ''}</dd>
        </dl>
        ${sources ? `<details><summary>where each value came from</summary><ul>${sources}</ul></details>` : ''}
        <p class="note">note: <code>${esc(s.note)}</code></p>
        <div class="actions">
          <a class="primary" href="index.html?room=${encodeURIComponent(s.id)}">Walk this room →</a>
          ${w ? `<button type="button" data-read="${esc(w.slug)}">Read the work</button>` : ''}
        </div>
      </div></article>`;
  }

  function renderScenes() {
    const n = lib.scenes.length;
    const south = lib.scenes.filter((s) => s.hub_side === 'S').length;
    $('scenesLede').textContent = n
      ? `${n} room${n === 1 ? '' : 's'} off the hall, in the order the scenes were made: ${south} on the south side, ${n - south} on the north. ${lib.works.length - n} of the ${lib.works.length} works have no room yet.`
      : 'The hall stands alone for now.';
    $('hall').innerHTML = hallSvg();
    $('sceneGrid').innerHTML = lib.scenes.map(sceneCard).join('');
    $('scenesEmpty').hidden = n > 0;
    $('hall').hidden = n === 0;
  }

  function markScene(id, { push = true, scroll = true } = {}) {
    markedScene = id;
    for (const el of document.querySelectorAll('.scene, .door-hit')) el.classList.toggle('on', el.dataset.scene === id);
    const card = $(`scene-${id}`);
    if (card && scroll) card.scrollIntoView({ block: 'start', behavior: 'smooth' });
    if (push) writeUrl(true);
  }

  // ---- boot -------------------------------------------------------------------------------
  function applyUrl({ push = false } = {}) {
    const u = readUrl();
    if (u.view === 'scenes') {
      showView('scenes', { push });
      if (u.scene && sceneById.has(u.scene)) markScene(u.scene, { push: false, scroll: true });
    } else {
      showView('works', { push });
      const slug = (u.work && bySlug.has(u.work) && u.work) || (bySlug.has(remembered()) && remembered()) || (lib.works[0] && lib.works[0].slug);
      if (slug) openWork(slug, { push, scroll: false });
    }
  }

  async function boot() {
    try {
      await load();
    } catch (e) {
      $('summary').textContent = `${e.message}. Build it: python writing-museum/build/build_museum.py build`;
      return;
    }
    const nPassages = lib.works.reduce((n, w) => n + w.passages.length, 0);
    $('summary').textContent = `${lib.works.length} works in ${lib.folders.length} folders, ${nPassages} passages, ${lib.scenes.length} rooms · built ${lib.built}`;
    const modes = [...new Set(lib.works.map((w) => w.mode || 'unclassified'))].sort();
    fillSelect($('mode'), modes.map((m) => [m, words(m)]));
    fillSelect($('folder'), lib.folders.map((f) => [f.folder, f.name]));
    renderShelf();

    for (const b of document.querySelectorAll('.view-tab')) b.addEventListener('click', () => showView(b.dataset.view));
    for (const id of ['mode', 'folder', 'withRoom']) $(id).addEventListener('change', renderShelf);
    let timer = null;
    $('q').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(renderShelf, 120); });
    $('shelf').addEventListener('click', (e) => { const b = e.target.closest('.spine'); if (b) openWork(b.dataset.slug); });
    $('reader').addEventListener('click', (e) => {
      const go = e.target.closest('[data-go]');
      if (go && go.dataset.go) return openWork(go.dataset.go);
      const look = e.target.closest('[data-scene]');
      if (look) { showView('scenes'); markScene(look.dataset.scene); }
    });
    $('view-scenes').addEventListener('click', (e) => {
      const read = e.target.closest('[data-read]');
      if (read) { showView('works'); return openWork(read.dataset.read); }
      const door = e.target.closest('.door-hit');
      if (door) markScene(door.dataset.scene);
    });
    $('hall').addEventListener('keydown', (e) => {
      const door = e.target.closest('.door-hit');
      if (door && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); markScene(door.dataset.scene); }
    });
    document.addEventListener('keydown', (e) => {
      const t = e.target;
      const typing = t && (t.tagName === 'SELECT' || t.tagName === 'TEXTAREA' || (t.tagName === 'INPUT' && t.type !== 'checkbox'));
      if (typing) {
        if (e.key === 'Escape') t.blur();
        return;
      }
      if (e.key === 'ArrowLeft') step(-1);
      else if (e.key === 'ArrowRight') step(1);
      else if (e.key === '/') { e.preventDefault(); showView('works'); $('q').focus(); }
    });
    window.addEventListener('popstate', () => applyUrl({ push: false }));
    applyUrl({ push: false });
    writeUrl(true);
  }

  window.libraryDebug = { get lib() { return lib; }, openWork, showView, markScene, filtered: () => filtered().map((w) => w.slug) };
  document.addEventListener('DOMContentLoaded', boot);
})();
