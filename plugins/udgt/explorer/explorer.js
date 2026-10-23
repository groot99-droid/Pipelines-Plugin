/* UDGT explorer: reads ../teardown.json, ../answers.json and chapters.json, nothing else.
   Views come from the profile (teardown.explorer.views); the hash is #<view>/<node id>. */
(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const state = { data: null, chapters: [], answers: [], byId: new Map(), out: new Map(), inn: new Map(), view: null, sel: null };

  async function getJSON(url, fallback) {
    try {
      const r = await fetch(url, { cache: 'no-store' });
      if (!r.ok) return fallback;
      return await r.json();
    } catch (e) {
      return fallback;
    }
  }

  async function boot() {
    const data = await getJSON('../teardown.json', null);
    if (!data) {
      $('x-reader').innerHTML = '<h2>No teardown yet</h2><p>Run <code>udgt.py scan</code> and <code>udgt.py build</code>, then serve the teardown folder over HTTP (for example <code>python -m http.server</code>) and open <code>explorer/index.html</code>.</p>';
      return;
    }
    state.data = data;
    state.chapters = (await getJSON('chapters.json', { chapters: [] })).chapters;
    state.answers = (await getJSON('../answers.json', { answers: [] })).answers;
    for (const n of data.nodes) state.byId.set(n.id, n);
    for (const e of data.edges) {
      push(state.out, e.from, e);
      push(state.inn, e.to, e);
    }
    const ex = data.explorer || {};
    document.title = ex.title || data.name + ' — Teardown';
    $('x-title').textContent = ex.title || data.name;
    $('x-tagline').textContent = ex.tagline || '';
    state.views = (ex.views && ex.views.length) ? ex.views : [{ id: 'all', label: 'All', about: '' }];
    renderTabs();
    $('x-q').addEventListener('input', renderList);
    $('x-kind').addEventListener('change', renderList);
    $('x-area').addEventListener('change', renderList);
    window.addEventListener('hashchange', route);
    route();
  }

  function push(map, key, val) {
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(val);
  }

  function renderTabs() {
    $('x-views').innerHTML = state.views.map((v) =>
      `<button class="x-view x-glass" data-view="${esc(v.id)}" type="button">${esc(v.label)}</button>`).join('');
    $('x-views').querySelectorAll('button').forEach((b) => b.addEventListener('click', () => go(b.dataset.view)));
  }

  function go(view, id) {
    location.hash = '#' + view + (id ? '/' + encodeURIComponent(id) : '');
  }

  function route() {
    const raw = location.hash.slice(1);
    const cut = raw.indexOf('/');
    const vid = cut < 0 ? raw : raw.slice(0, cut);
    const id = cut < 0 ? null : decodeURIComponent(raw.slice(cut + 1));
    const view = state.views.find((v) => v.id === vid) || state.views[0];
    const changed = view !== state.view;
    state.view = view;
    state.sel = id;
    $('x-views').querySelectorAll('button').forEach((b) => b.setAttribute('aria-current', b.dataset.view === view.id ? 'page' : 'false'));
    $('x-about').textContent = view.about || '';
    if (changed) setupFilters();
    const wide = view.special === 'title' || view.special === 'history';
    $('x-main').classList.toggle('x-wide', wide && !id);
    document.body.classList.toggle('x-on-title', view.special === 'title' && !id);
    renderList();
    renderReader();
  }

  function inView(n, view) {
    if (view.kinds && !view.kinds.includes(n.kind)) return false;
    if (view.areas && n.kind === 'section' && !view.areas.includes(n.area)) return false;
    if (view.areas && view.kinds && view.kinds.length === 1 && !view.areas.includes(n.area)) return false;
    return true;
  }

  function pool() {
    const v = state.view;
    if (v.special === 'chapters') return state.chapters.map((c, i) => ({ id: 'chapter:' + i, kind: 'chapter', area: 'teardown', title: c.title }));
    if (v.special === 'title' || v.special === 'history') return [];
    return state.data.nodes.filter((n) => inView(n, v));
  }

  function setupFilters() {
    const nodes = pool();
    const kinds = [...new Set(nodes.map((n) => n.kind))].sort();
    const areas = [...new Set(nodes.map((n) => n.area))].sort();
    $('x-kind').innerHTML = '<option value="">every kind</option>' + kinds.map((k) => `<option>${esc(k)}</option>`).join('');
    $('x-area').innerHTML = '<option value="">every area</option>' + areas.map((a) => `<option>${esc(a)}</option>`).join('');
    $('x-q').value = '';
    $('x-filters').hidden = !nodes.length;
  }

  function matches(n, words) {
    if (!words.length) return true;
    const hay = (n.id + ' ' + n.title + ' ' + (n.text || '')).toLowerCase();
    return words.every((w) => hay.includes(w));
  }

  function renderList() {
    const words = $('x-q').value.toLowerCase().split(/\s+/).filter(Boolean);
    const kind = $('x-kind').value;
    const area = $('x-area').value;
    const rows = pool().filter((n) => (!kind || n.kind === kind) && (!area || n.area === area) && matches(n, words));
    const shown = rows.slice(0, 400);
    $('x-count').textContent = rows.length + (rows.length === 1 ? ' entry' : ' entries') + (rows.length > shown.length ? ', first 400 shown' : '');
    $('x-list').innerHTML = shown.map((n) =>
      `<li><button type="button" data-id="${esc(n.id)}" aria-current="${n.id === state.sel}">${esc(n.title)}<span class="x-id">${esc(n.kind)} · ${esc(n.id)}</span></button></li>`).join('');
    $('x-list').querySelectorAll('button').forEach((b) => b.addEventListener('click', () => go(state.view.id, b.dataset.id)));
  }

  function renderReader() {
    const r = $('x-reader');
    const v = state.view;
    if (state.sel && state.sel.startsWith('chapter:')) {
      const c = state.chapters[Number(state.sel.slice(8))];
      r.innerHTML = c ? md(c.markdown) : '<p>No such chapter.</p>';
      wireLinks(r);
      return;
    }
    if (state.sel) {
      r.innerHTML = nodeHTML(state.byId.get(state.sel), state.sel);
      wireLinks(r);
      r.focus({ preventScroll: true });
      return;
    }
    if (v.special === 'title') r.innerHTML = titleHTML();
    else if (v.special === 'history') r.innerHTML = historyHTML();
    else if (v.special === 'chapters') r.innerHTML = chaptersHTML();
    else if (v.cards) r.innerHTML = cardsHTML(v);
    else r.innerHTML = overviewHTML(v);
    wireLinks(r);
  }

  function wireLinks(root) {
    root.querySelectorAll('[data-go]').forEach((a) => a.addEventListener('click', (ev) => {
      ev.stopPropagation();
      ev.preventDefault();
      const id = a.dataset.go;
      go(viewFor(id), id);
    }));
  }

  function viewFor(id) {
    if (id.startsWith('chapter:')) return state.views.find((v) => v.special === 'chapters')?.id || state.view.id;
    const n = state.byId.get(id);
    if (!n) return state.view.id;
    if (inView(n, state.view) && !state.view.special) return state.view.id;
    const hit = state.views.find((v) => !v.special && inView(n, v));
    return hit ? hit.id : state.view.id;
  }

  function link(id, label) {
    const n = state.byId.get(id);
    return n ? `<a href="#" data-go="${esc(id)}">${esc(label || n.title)}</a>` : `<span class="x-mono">${esc(label || id)}</span>`;
  }

  function sourceLink(n) {
    if (!n.source) return '';
    const where = `${n.source.path}:${n.source.line}`;
    const url = (state.data.game && state.data.game.browse) ? state.data.game.browse + n.source.path + '#L' + n.source.line : null;
    return `<p class="x-mono">${url ? `<a href="${esc(url)}" rel="noopener">${esc(where)}</a>` : esc(where)}</p>`;
  }

  function looksLikeColour(v) {
    return typeof v === 'string' && /^(#[0-9a-f]{3,8}|rgb|var\(|hsl)/i.test(v.trim()) && !/\d+(px|ms|s|em|rem)\b/.test(v);
  }

  function metaHTML(meta) {
    if (!meta) return '';
    const rows = Object.entries(meta).filter(([k]) => !k.startsWith('_') && k !== 'items' && k !== 'sentences' && k !== 'days');
    if (!rows.length) return '';
    return '<table class="x-meta"><tbody>' + rows.map(([k, val]) => {
      let cell;
      if (val && typeof val === 'object') cell = `<code>${esc(JSON.stringify(val))}</code>`;
      else if (k === 'value' && looksLikeColour(val)) cell = `<span class="x-swatch" style="background:${esc(val)}"></span><code>${esc(val)}</code>`;
      else cell = esc(val);
      return `<tr><th>${esc(k)}</th><td>${cell}</td></tr>`;
    }).join('') + '</tbody></table>';
  }

  function nodeHTML(n, id) {
    if (!n) return `<h2>Not found</h2><p class="x-mono">${esc(id)}</p>`;
    const meta = n.meta || {};
    const chips = [`<span class="x-chip x-accent">${esc(n.kind)}</span>`, `<span class="x-chip">${esc(n.area)}</span>`];
    if (meta.status) chips.push(`<span class="x-chip">${esc(meta.status)}</span>`);
    if (meta.date) chips.push(`<span class="x-chip">${esc(meta.date)}</span>`);
    if (meta.owner) chips.push('<span class="x-chip">owner</span>');
    (meta.eras || []).forEach((e) => chips.push(`<span class="x-chip">${esc(e)}</span>`));
    if (meta.open) chips.push('<span class="x-chip x-warn">open</span>');
    let html = `<p>${chips.join('')}</p><h2>${esc(n.title)}</h2><p class="x-id x-mono">${esc(n.id)}</p>${sourceLink(n)}`;
    if (n.text) html += `<blockquote>${esc(n.text)}</blockquote>`;
    if (meta.items) html += '<h3>In order</h3><ol class="x-ring">' + meta.items.map((i) => `<li title="line ${esc(i.line)}${i.note ? ': ' + esc(i.note) : ''}">${esc(i.name)}</li>`).join('') + '</ol>';
    if (meta.sentences) html += '<h3>What it says</h3><ul>' + meta.sentences.map((s) => `<li>${esc(s)}</li>`).join('') + '</ul>';
    if (n.kind === 'answer') html += `<h3>Question</h3><p>${esc(meta.question)}</p><h3>The owner's answer</h3><blockquote>${esc(meta.answer)}</blockquote>`;
    html += metaHTML(n.kind === 'answer' ? { stage: meta.stage, date: meta.date } : meta);
    const out = state.out.get(n.id) || [];
    const inn = state.inn.get(n.id) || [];
    if (out.length) html += `<h3>Links to (${out.length})</h3><ul class="x-links">` + out.slice(0, 120).map((e) => `<li>${esc(e.kind)}: ${link(e.to)}</li>`).join('') + '</ul>';
    if (inn.length) html += `<h3>Cited by (${inn.length})</h3><ul class="x-links">` + inn.slice(0, 200).map((e) => `<li>${esc(e.kind)}: ${link(e.from)}</li>`).join('') + '</ul>';
    if (n.kind === 'decision') {
      const did = n.id.slice(4);
      const cs = state.data.commits.filter((c) => c.ids.includes(did));
      if (cs.length) html += `<h3>Commits naming it (${cs.length})</h3><ul class="x-timeline">` + cs.map((c) => `<li><time>${esc(c.d)}</time><code>${esc(c.h)}</code> ${esc(c.s)}</li>`).join('') + '</ul>';
    }
    const cites = state.chapters.map((c, i) => [c, i]).filter(([c]) => c.markdown.includes('[[' + n.id + ']]') || c.markdown.includes('[[' + n.id + '|'));
    if (cites.length) html += '<h3>Discussed in</h3><ul>' + cites.map(([c, i]) => `<li><a href="#" data-go="chapter:${i}">${esc(c.title)}</a></li>`).join('') + '</ul>';
    return html;
  }

  function count(kind) {
    return state.data.counts[kind] || 0;
  }

  /* The title view is the game's own main menu: the logo, a column of glass buttons (one per view),
     a row of small buttons, the version line; the teardown's state sits in a glass panel beside it. */
  function titleHTML() {
    const d = state.data;
    const ex = d.explorer || {};
    const h = state.byId.get('history:summary')?.meta || {};
    const logo = (ex.logo && ex.logo.length) ? ex.logo : [d.name];
    const small = ex.menu_small || [];
    const menu = state.views.filter((v) => v.special !== 'title' && !small.includes(v.id));
    const smallViews = state.views.filter((v) => small.includes(v.id));
    const buttons = menu.map((v, i) =>
      `<a class="x-menubtn x-glass${i === 0 ? ' x-menubtn--primary' : ''}" href="#${esc(v.id)}"><span class="x-menubtn__glyph" aria-hidden="true">${i === 0 ? '▶' : '›'}</span>${esc(v.label)}</a>`).join('');
    const smalls = smallViews.map((v) => `<a class="x-menubtn x-menubtn--small x-glass" href="#${esc(v.id)}">${esc(v.label)}</a>`).join('');
    const stats = [
      ['decision', 'decisions'], ['section', 'doc sections'], ['record', 'data records'], ['message', 'wire messages'],
      ['scene', 'scenes'], ['token', 'design tokens'], ['copy', 'UI strings'], ['plan', 'stated plans'],
    ].map(([k, label]) => `<li class="x-stat"><b>${count(k)}</b><span>${label}</span></li>`);
    stats.push(`<li class="x-stat"><b>${esc(h.commits || 0)}</b><span>commits, ${esc(h.first || '?')} to ${esc(h.last || '?')}</span></li>`);
    const answered = new Map();
    state.answers.forEach((a) => answered.set(a.stage, (answered.get(a.stage) || 0) + 1));
    const stages = d.stages.map((s) => {
      const ch = state.chapters.findIndex((c) => c.file.startsWith(String(s.id).padStart(2, '0') + '-'));
      return `<li>${ch >= 0 ? `<a href="#" data-go="chapter:${ch}">${esc(s.title)}</a>` : esc(s.title)} <span class="x-chip">${answered.get(s.id) || 0} answers</span>${ch >= 0 ? '<span class="x-chip x-accent">chapter</span>' : ''}</li>`;
    }).join('');
    const broken = d.broken.length ? `<p><span class="x-chip x-warn">${d.broken.length}</span> citations in the game's documents point at sections that do not exist (yet).</p>` : '';
    return `<div class="x-menu">
      <div class="x-menu__left">
        <h2 class="x-logo">${logo.map((line, i) => `<span class="${i === logo.length - 1 && logo.length > 1 ? 'x-logo__accent' : ''}">${esc(line)}</span>`).join('')}</h2>
        <p class="x-logo__sub">${esc(ex.subtitle || 'Teardown')}</p>
        <nav class="x-menu__list" aria-label="Teardown menu">${buttons}</nav>
        <div class="x-menu__small">${smalls}</div>
        <p class="x-version">scan ${esc(d.scanned)} · ${esc((d.game.head || '').slice(0, 7))}${d.game.shallow ? ' · shallow clone' : ''}</p>
      </div>
      <aside class="x-menu__panel x-glass" aria-label="Where the teardown stands">
        <h3>${esc(ex.tagline || '')}</h3>
        <ul class="x-stats">${stats.join('')}</ul>${broken}
        <h3>Stage by stage</h3><ol class="x-stages">${stages}</ol>
      </aside>
    </div>`;
  }

  function historyHTML() {
    const d = state.data;
    const days = state.byId.get('history:summary')?.meta?.days || {};
    const vals = Object.values(days);
    const max = Math.max(1, ...vals);
    const bars = Object.entries(days).map(([day, n]) => `<span title="${esc(day)}: ${n} commits" style="height:${Math.round(100 * n / max)}%"></span>`).join('');
    const prs = d.nodes.filter((n) => n.kind === 'pr').sort((a, b) => (a.meta.date < b.meta.date ? 1 : -1));
    const decisions = d.nodes.filter((n) => n.kind === 'decision' && n.meta.date).sort((a, b) => (a.meta.date < b.meta.date ? 1 : -1));
    return `<h2>How it was made</h2><p>${vals.reduce((a, b) => a + b, 0)} commits over ${vals.length} days. Each bar is one day.</p>
      <div class="x-bars" role="img" aria-label="Commits per day">${bars}</div>
      <h3>Decisions by date (${decisions.length})</h3><ul class="x-timeline">${decisions.map((n) => `<li><time>${esc(n.meta.date)}</time>${link(n.id)}</li>`).join('')}</ul>
      <h3>Pull requests (${prs.length})</h3><ul class="x-timeline">${prs.map((n) => `<li><time>${esc(n.meta.date)}</time>${link(n.id)}${n.meta.round ? ` <span class="x-chip">round ${esc(n.meta.round)}</span>` : ''}</li>`).join('')}</ul>
      <h3>Every commit</h3><ul class="x-timeline">${d.commits.map((c) => `<li><time>${esc(c.d)}</time><code>${esc(c.h)}</code> ${esc(c.s)}${c.ids.map((i) => ' ' + link('dec:' + i, i)).join('')}</li>`).join('')}</ul>`;
  }

  function chaptersHTML() {
    if (!state.chapters.length) return '<h2>No chapters yet</h2><p>Chapters are written stage by stage, after each brief with the owner.</p>';
    return '<h2>Case file</h2><ol>' + state.chapters.map((c, i) => `<li><a href="#" data-go="chapter:${i}">${esc(c.title)}</a></li>`).join('') + '</ol>';
  }

  /* Records dealt as the game's cards. The profile's explorer.cards names a template per collection
     ("role": the role card's stripe, title, goal, lists, text and Beware line; "tip": a small card)
     and the record fields that fill each slot; a list of fields takes the first one present. */
  function field(meta, spec) {
    const names = Array.isArray(spec) ? spec : [spec];
    for (const name of names) {
      const v = meta[name];
      if (v != null && v !== '' && !(typeof v === 'string' && /^[[{]\d+[\]}]$/.test(v))) return v;
    }
    return null;
  }

  function cardHTML(n, cards) {
    const m = n.meta || {};
    const kind = (cards.collections || {})[m._collection] || 'tip';
    const t = (cards.templates || {})[kind] || {};
    const fac = (cards.factions || {})[m[cards.faction_field || 'faction']] || '';
    const title = field(m, t.title || 'name') || n.title;
    const lists = (t.list || []).map((f) => m[f]).filter(Array.isArray).flat();
    const text = t.text ? field(m, t.text) : null;
    let html = `<article class="x-rolecard x-rolecard--${esc(kind)}${fac ? ' x-rolecard--' + esc(fac) : ''}" data-go="${esc(n.id)}">`;
    if (t.stripe) html += `<p class="x-rolecard__stripe">${esc(field(m, t.stripe) || fac || kind)}</p>`;
    html += `<h3 class="x-rolecard__title"><a href="#" data-go="${esc(n.id)}">${esc(title)}</a></h3>`;
    if (t.sub) {
      const sub = field(m, t.sub);
      if (sub) html += `<p class="x-rolecard__sub">walks as ${esc(sub)}${m.cover ? ' · wears a cover' : ''}</p>`;
    }
    if (t.goal && m[t.goal]) html += `<p class="x-rolecard__goal">${esc(m[t.goal])}</p>`;
    if (lists.length) html += '<ul class="x-rolecard__list">' + lists.map((x) => `<li>${esc(x)}</li>`).join('') + '</ul>';
    if (text) html += `<p class="x-rolecard__text">${esc(String(text))}</p>`;
    if (t.beware && m[t.beware]) html += `<p class="x-rolecard__beware"><strong>Beware:</strong> ${esc(m[t.beware])}</p>`;
    return html + '</article>';
  }

  function cardsHTML(v) {
    const words = $('x-q').value.toLowerCase().split(/\s+/).filter(Boolean);
    const cards = state.data.explorer?.cards || {};
    const recs = state.data.nodes.filter((n) => n.kind === v.cards && matches(n, words));
    const groups = new Map();
    recs.forEach((n) => push(groups, n.meta?._collection || '', n));
    const order = [...groups.keys()].sort((a, b) => ((cards.collections || {})[b] ? 1 : 0) - ((cards.collections || {})[a] ? 1 : 0));
    let html = `<h2>${esc(v.label)}</h2><p>${esc(v.about || '')}</p>`;
    for (const coll of order) {
      const list = groups.get(coll);
      const c = state.byId.get(coll);
      const kind = (cards.collections || {})[coll] || 'tip';
      html += `<h3>${c ? link(coll, c.title) : esc(coll)} · ${list.length}</h3><div class="x-deal x-deal--${esc(kind)}">` +
        list.slice(0, 60).map((n) => cardHTML(n, cards)).join('') + '</div>';
    }
    return html;
  }

  function overviewHTML(v) {
    const nodes = pool();
    const byKind = new Map();
    nodes.forEach((n) => push(byKind, n.kind, n));
    let html = `<h2>${esc(v.label)}</h2><p>${esc(v.about || '')}</p><ul class="x-stats">` +
      [...byKind].map(([k, l]) => `<li class="x-stat x-glass"><b>${l.length}</b><span>${esc(k)}</span></li>`).join('') + '</ul>';
    const anchors = nodes.filter((n) => n.kind === 'anchor');
    anchors.forEach((a) => {
      html += `<h3>${link(a.id)}</h3><ol class="x-ring">` + a.meta.items.map((i) => `<li>${esc(i.name)}</li>`).join('') + '</ol>';
    });
    const colours = nodes.filter((n) => n.kind === 'colour' || (n.kind === 'token' && looksLikeColour(n.meta?.value) && !n.title.endsWith('-rgb')));
    if (colours.length) html += '<h3>Colours</h3><p>' + colours.slice(0, 80).map((n) => `<a href="#" data-go="${esc(n.id)}" title="${esc(n.title)}"><span class="x-swatch" style="background:${esc(n.kind === 'token' ? 'var(' + n.title + ')' : n.meta.value)}"></span></a>`).join('') + '</p>';
    return html + '<p>Pick an entry on the left, or search.</p>';
  }

  /* A small Markdown renderer for chapters: headings, lists, quotes, tables, code, bold, italics,
     links, and [[node-id]] / [[node-id|label]] links into the teardown. */
  function inline(s) {
    let t = esc(s);
    t = t.replace(/\[\[([a-z]+:[^\]|]+)(?:\|([^\]]*))?\]\]/g, (_, id, label) => link(id, label));
    t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
    t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>');
    t = t.replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" rel="noopener">$1</a>');
    return t;
  }

  function md(text) {
    const lines = text.replace(/\r/g, '').split('\n');
    const out = [];
    let list = null;
    let para = [];
    const flushPara = () => { if (para.length) { out.push('<p>' + inline(para.join(' ')) + '</p>'); para = []; } };
    const flushList = () => { if (list) { out.push(`</${list}>`); list = null; } };
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      let m;
      if (/^```/.test(line)) {
        flushPara(); flushList();
        const code = [];
        for (i++; i < lines.length && !/^```/.test(lines[i]); i++) code.push(lines[i]);
        out.push('<pre><code>' + esc(code.join('\n')) + '</code></pre>');
      } else if ((m = /^(#{1,4})\s+(.*)$/.exec(line))) {
        flushPara(); flushList();
        const lv = Math.min(m[1].length + 1, 4);
        out.push(`<h${lv}>${inline(m[2])}</h${lv}>`);
      } else if (/^\|/.test(line) && i + 1 < lines.length && /^\|?\s*:?-{2,}/.test(lines[i + 1])) {
        flushPara(); flushList();
        const cells = (l) => l.replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
        let html = '<table class="x-md"><thead><tr>' + cells(line).map((c) => `<th>${inline(c)}</th>`).join('') + '</tr></thead><tbody>';
        for (i += 2; i < lines.length && /^\|/.test(lines[i]); i++) html += '<tr>' + cells(lines[i]).map((c) => `<td>${inline(c)}</td>`).join('') + '</tr>';
        i--;
        out.push(html + '</tbody></table>');
      } else if ((m = /^>\s?(.*)$/.exec(line))) {
        flushPara(); flushList();
        const q = [m[1]];
        while (i + 1 < lines.length && /^>/.test(lines[i + 1])) q.push(lines[++i].replace(/^>\s?/, ''));
        out.push('<blockquote>' + md(q.join('\n')) + '</blockquote>');
      } else if ((m = /^\s*([-*]|\d+\.)\s+(.*)$/.exec(line))) {
        flushPara();
        const kind = /\d/.test(m[1]) ? 'ol' : 'ul';
        if (list !== kind) { flushList(); out.push(`<${kind}>`); list = kind; }
        out.push('<li>' + inline(m[2]) + '</li>');
      } else if (!line.trim()) {
        flushPara(); flushList();
      } else {
        flushList();
        para.push(line.trim());
      }
    }
    flushPara(); flushList();
    return out.join('\n');
  }

  boot();
})();
