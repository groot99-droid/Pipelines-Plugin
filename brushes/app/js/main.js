// main.js - boot: token, schema, status, the two top-level tabs.
//
// Module map (see README.md): api.js talks to the server; schema.js and
// state.js are pure; designer.js lays out panels.js, textures.js, patchbox.js,
// exporter.js, opener.js and engine.js around one doc; library.js is the
// Library tab. `window.__brushApp` exposes the running pieces to selftest.html.

import {el, clear} from './dom.js';
import {api, initToken, hasToken, loadStatic, tokenForLinks} from './api.js';
import {indexSchema} from './schema.js';
import {initUi, toast} from './ui.js';
import {createBasket} from './exporter.js';
import {createDesigner} from './designer.js';
import {mountLibrary} from './library.js';

const $ = (id) => document.getElementById(id);

async function boot() {
  initUi($('toasts'));
  const banners = $('banners');
  const hasTok = initToken();
  const pill = $('server-pill');

  let schema = null;
  try {
    schema = indexSchema(await loadStatic('/schema/silica_keys.json'));
  } catch (error) {
    fatal(`The schema cannot be loaded: ${error.message}`, 'Start the app with: python -I brushes/pipeline/app_server.py');
    return;
  }

  let status = null;
  if (!hasTok) {
    banners.append(notice('warn', 'No access token in this address.',
      'Open the page with the Open line the server printed (it ends in #t=...), or run: python -I brushes/pipeline/app_server.py'));
    pill.textContent = 'No token'; pill.className = 'pill pill-bad';
  } else {
    try {
      status = await api.status();
      pill.textContent = `${status.counts ? status.counts.brushes : 0} brushes · index ${status.index.state}`;
      pill.className = status.index.state === 'not_ingested' ? 'pill pill-warn' : 'pill pill-ok';
      if (!status.library_present) banners.append(notice('warn', 'The library originals are not on this machine.', 'Opening library brushes needs them (git lfs pull). Files you drop in still work.'));
      if (status.index.state === 'not_ingested') banners.append(notice('warn', 'The catalog is not built.', (status.next_steps || []).join('  then  ') || 'Run ingest.py build.'));
    } catch (error) {
      pill.textContent = error.code === 'bad_token' ? 'Wrong token' : 'Server unreachable'; pill.className = 'pill pill-bad';
      banners.append(notice('bad', `${error.code}: ${error.message}`, error.hint));
    }
  }

  const link = $('selftest-link');
  if (hasToken()) link.href = `selftest.html#t=${tokenForLinks()}`;

  const basket = createBasket();
  const designer = createDesigner({schema, status: status || {}, basket, dialog: $('dlg'), goLibrary: () => showTab('library')});
  $('designer-root').append(designer.el);

  let library = null;
  function ensureLibrary() {
    if (library) { library.refresh(); return; }
    library = mountLibrary($('library-mount'), {
      api,
      async openInDesigner(id) {
        try { const doc = await designer.openLibraryDirect(id); if (doc) showTab('designer'); } catch (error) { toast(`${error.code || 'error'}: ${error.message}${error.hint ? ' ' + error.hint : ''}`, 'error', 9000); }
      },
      addToSet(id, name) { toast(basket.addLibrary(id, name) ? `Added ${name} to the set.` : `${name} is already in the set.`, 'info'); },
      toast,
      basket,
    });
    library.refresh();
  }

  const tabs = {library: $('tab-library'), designer: $('tab-designer')};
  const views = {library: $('view-library'), designer: $('view-designer')};
  function showTab(name) {
    for (const key of Object.keys(tabs)) {
      const on = key === name;
      tabs[key].setAttribute('aria-selected', String(on)); tabs[key].tabIndex = on ? 0 : -1;
      views[key].hidden = !on;
    }
    if (name === 'library') ensureLibrary();
  }
  for (const [name, tab] of Object.entries(tabs)) {
    tab.addEventListener('click', () => showTab(name));
    tab.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { const other = name === 'library' ? 'designer' : 'library'; showTab(other); tabs[other].focus(); }
    });
  }
  showTab('designer');

  window.__brushApp = {api, schema, status, designer, basket, showTab, get library() { return library; }};
}

function notice(kind, text, hint) {
  return el('div', {class: `notice notice-${kind}`, role: kind === 'bad' ? 'alert' : 'status'}, el('strong', {text}), hint ? el('p', {class: 'small', text: hint}) : null);
}

function fatal(message, hint) {
  const host = $('banners');
  clear(host);
  host.append(notice('bad', message, hint));
  $('server-pill').textContent = 'Offline'; $('server-pill').className = 'pill pill-bad';
}

boot().catch((error) => fatal(`The app failed to start: ${error.message}`, 'See the browser console.'));
