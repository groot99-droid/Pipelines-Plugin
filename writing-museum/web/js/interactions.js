import * as THREE from 'three';
import { viewingSpot } from './artgeom.js';

// Writing Museum: a work is a passage (`text`, no image); the placard shows the passage itself, the
// work it comes from and the vault path and lines it was copied from. There is no rewrite layer
// (the text on the wall is the author's own, verbatim). Image works keep the Chronicle Museum path.
const IMAGE_ROOT = '../';                     // the server is rooted at the tool folder
const DEFAULT_IMAGE_BASE = '';

function escapeHtml(t) {
  return String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}
// Placard text is plain prose with *italic*, blank-line paragraph breaks and (verse) line breaks.
function placardHtml(t) {
  return escapeHtml(t).split(/\n\s*\n/).map((p) => p.replace(/\*([^*\n]+)\*/g, '<em>$1</em>').replace(/\n/g, '<br>')).join('<br><br>');
}

const PICK_DISTANCE = 6;

export function createInteractions(camera, manifestIndex, waypointTrail, isLockedFn, getCurrentRoomId,
  { domElement = null, walls = () => [], groundY = null } = {}) {
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2(0, 0);
  let artMeshes = [];
  let pickables = [];       // DOOR- leaves and SCULPT- proxies
  let targets = [];
  let current = null;       // the entry whose placard is open ({kind:'sculpture'} for a sculpture)
  let hovered = null;       // the object under the crosshair (entry, door leaf or sculpture proxy)
  let teleporter = null;    // fn(entry) provided by navigate.js
  let doorHandler = null;   // fn(leaf) provided by main.js (scenes.enter)
  let frame = 0;

  function setArtMeshes(meshes) { artMeshes = meshes; targets = [...artMeshes, ...pickables]; }
  function setPickables(list) { pickables = list; targets = [...artMeshes, ...pickables]; }
  function setTeleporter(fn) { teleporter = fn; }
  function onDoor(fn) { doorHandler = fn; }

  // The clickable object under a screen point (art plane, door leaf or sculpture proxy), or null.
  function pick(x = 0, y = 0) {
    ndc.set(x, y);
    raycaster.setFromCamera(ndc, camera);
    raycaster.far = PICK_DISTANCE;
    const hits = raycaster.intersectObjects(targets, false);
    return hits.length ? hits[0].object : null;
  }
  const pickArt = pick;
  const kindOf = (obj) => (!obj ? null : obj.name.startsWith('DOOR-') ? 'door' : obj.name.startsWith('SCULPT-') ? 'sculpture' : 'art');

  function imageUrl(entry, rel) {
    if (!rel) return null;
    const wing = manifestIndex.wingsById && manifestIndex.wingsById.get(entry.wing);
    const base = wing && wing.image_base ? wing.image_base : DEFAULT_IMAGE_BASE;
    return IMAGE_ROOT + base + rel;
  }

  const placard = document.getElementById('placard');
  const closeBtn = document.getElementById('placard-close');
  const titleEl = document.getElementById('placard-title');
  const metaEl = document.getElementById('placard-meta');
  const artistEl = document.getElementById('placard-artist');
  const descEl = document.getElementById('placard-description');
  const creditEl = document.getElementById('placard-credit');
  const voiceEl = document.getElementById('placard-voice');
  const imgEl = document.getElementById('placard-image');
  const suggestedList = document.getElementById('suggested-list');
  const prevBtn = document.getElementById('placard-prev');
  const nextBtn = document.getElementById('placard-next');
  const promptEl = document.getElementById('look-prompt');
  const crosshair = document.getElementById('crosshair');
  const rewritesReady = Promise.resolve({});   // no rewrite layer here; main.js awaits this before the start screen

  function artistLine(artist) {
    const bits = [artist.lifespan ? `${artist.name} (${artist.lifespan})` : artist.name];
    if (artist.era && artist.era.title) bits.push(artist.era.title);
    if (artist.wing === 'people' && artist.region) bits.push(artist.region);
    if (artist.vault_path) bits.push(`${(artist.discipline || [])[0] || 'work'} · ${artist.mode || ''}`.replace(/ · $/, ''));
    return bits.join(' · ');
  }

  function creditHtml(c) {
    if (!c) return '';
    if (c.source_path) {
      const lines = Array.isArray(c.lines) ? ` · lines ${c.lines[0]}–${c.lines[1]}` : '';
      return `Verbatim from <code>${escapeHtml(c.source_path)}</code>${lines} · ${escapeHtml(c.license || 'the author\'s own text')}`;
    }
    const link = c.source
      ? `<a href="${escapeHtml(c.source)}" target="_blank" rel="noopener">Wikimedia Commons</a>`
      : 'Wikimedia Commons';
    const license = c.license
      ? (c.license_url ? `<a href="${escapeHtml(c.license_url)}" target="_blank" rel="noopener">${escapeHtml(c.license)}</a>` : escapeHtml(c.license))
      : '';
    const bits = [`Image: ${link}`, escapeHtml(c.author || 'Unknown')];
    if (license) bits.push(license);
    if (c.ai) bits.push(`AI illustration${c.model ? ` (${escapeHtml(c.model)})` : ''}`);
    return bits.join(' · ');
  }

  function renderSuggestions(entry) {
    suggestedList.innerHTML = '';
    const suggestions = manifestIndex.suggestNext(entry);
    for (const s of suggestions) {
      const div = document.createElement('div');
      div.className = 'suggested-item';
      const url = imageUrl(s, s.work.thumb || s.work.image);
      const img = document.createElement(url ? 'img' : 'span');
      if (url) { img.src = url; img.alt = s.work.title || ''; } else { img.className = 'suggested-panel'; img.textContent = (s.work.text || '').slice(0, 60); }
      const label = document.createElement('span');
      label.textContent = s.work.title && s.work.title !== s.artist.name ? `${s.work.title} — ${s.artist.name}` : s.artist.name;
      const actions = document.createElement('div');
      actions.className = 'suggested-actions';
      const guide = document.createElement('button');
      guide.type = 'button';
      guide.textContent = 'Guide me';
      guide.title = 'Draw the trail to this work';
      guide.addEventListener('click', (e) => {
        e.stopPropagation();
        waypointTrail.showPathTo(getCurrentRoomId(), s.room, camera.position);
      });
      const tp = document.createElement('button');
      tp.type = 'button';
      tp.textContent = 'Teleport';
      tp.title = 'Jump to this work';
      tp.addEventListener('click', (e) => {
        e.stopPropagation();
        if (teleporter) teleporter(s);
      });
      actions.appendChild(guide);
      actions.appendChild(tp);
      div.appendChild(img);
      div.appendChild(label);
      div.appendChild(actions);
      div.addEventListener('click', () => {
        waypointTrail.showPathTo(getCurrentRoomId(), s.room, camera.position);
      });
      suggestedList.appendChild(div);
    }
  }

  function sizeLine(dims) {
    if (!dims || !dims.h_m) return '';
    const cm = (v) => (v >= 10 ? `${(v * 100).toFixed(0)} cm` : `${(v * 100).toFixed(1)} cm`);
    const m = (v) => `${v.toFixed(2)} m`;
    const big = dims.h_m >= 3 || dims.w_m >= 3;
    const real = `${big ? m(dims.h_m) : cm(dims.h_m)} × ${big ? m(dims.w_m) : cm(dims.w_m)}`;
    const shown = dims.scale && dims.scale < 0.999 ? ` · shown at 1:${Math.round(1 / dims.scale)}` : ' · shown at actual size';
    if (dims.source === 'panel') return `panel ${real}`;
    const src = dims.source && dims.source.startsWith('default') ? ' (typical size)' : '';
    return `${real}${src}${shown}`;
  }

  function openPlacard(meshName) {
    const entry = manifestIndex.byMeshName.get(meshName);
    if (!entry) return null;
    const { artist, work } = entry;
    titleEl.textContent = work.title || 'Untitled';
    const metaBits = [work.year, work.medium, work.location].filter(Boolean);
    if (artist.themes && artist.themes.length) metaBits.push(artist.themes.map((t) => t.title || t.slug || t).join(', '));
    const sz = sizeLine(work.dims);
    if (sz) metaBits.push(sz);
    metaEl.textContent = metaBits.join(' · ');
    if (imgEl.parentElement) imgEl.parentElement.hidden = false;
    suggestedList.parentElement.hidden = false;
    if (prevBtn) prevBtn.parentElement.hidden = false;
    artistEl.textContent = artistLine(artist);
    descEl.innerHTML = placardHtml(work.description || work.text || '');
    descEl.classList.toggle('passage', typeof work.text === 'string');
    voiceEl.textContent = '';
    voiceEl.hidden = true;
    creditEl.innerHTML = creditHtml(work.credit);
    const url = imageUrl(entry, work.image);
    if (url) { imgEl.src = url; imgEl.alt = work.title || ''; }
    else { imgEl.removeAttribute('src'); imgEl.alt = ''; }
    if (imgEl.parentElement) imgEl.parentElement.hidden = !url;

    renderSuggestions(entry);
    const n = manifestIndex.flatWorks.length;
    if (prevBtn) prevBtn.disabled = !(teleporter && n > 1);
    if (nextBtn) nextBtn.disabled = !(teleporter && n > 1);

    current = entry;
    placard.classList.remove('hidden');
    placard.classList.add('visible');
    return entry;
  }

  // A sculpture's placard: title, maker, museum, licence and source link (assets/models.json).
  function openSculpture(proxy) {
    const c = (proxy && proxy.userData && proxy.userData.credits) || null;
    if (!c) return null;
    titleEl.textContent = c.title || proxy.userData.model;
    metaEl.textContent = [c.date, c.kind === 'relief' ? 'relief' : 'sculpture', c.museum].filter(Boolean).join(' · ');
    artistEl.textContent = c.artist || '';
    descEl.innerHTML = placardHtml(`A 3D scan of the original, shown at ${c.target_h ? `${c.target_h.toFixed(2)} m tall` : 'its real size'}.`);
    voiceEl.hidden = true;
    const link = c.url ? `<a href="${escapeHtml(c.url)}" target="_blank" rel="noopener">${escapeHtml(c.museum || c.source || 'source')}</a>` : escapeHtml(c.museum || '');
    creditEl.innerHTML = `Model: ${link} · ${escapeHtml(c.license || '')}`;
    if (c.preview) { imgEl.src = `../assets/models/${proxy.userData.model}/${c.preview}`; imgEl.alt = c.title || ''; if (imgEl.parentElement) imgEl.parentElement.hidden = false; }
    else if (imgEl.parentElement) imgEl.parentElement.hidden = true;
    suggestedList.innerHTML = '';
    suggestedList.parentElement.hidden = true;
    if (prevBtn) prevBtn.parentElement.hidden = true;
    current = { kind: 'sculpture', id: proxy.userData.model, meshName: proxy.name };
    placard.classList.remove('hidden');
    placard.classList.add('visible');
    return current;
  }

  function closePlacard({ keepTrail = false } = {}) {
    current = null;
    placard.classList.remove('visible');
    placard.classList.add('hidden');
    if (!keepTrail) waypointTrail.clear();
  }
  function isOpen() { return current !== null; }

  function stepWork(dir) {
    if (!current || !teleporter || current.kind === 'sculpture') return;
    const list = manifestIndex.flatWorks;
    const idx = list.indexOf(current);
    if (idx === -1) return;
    teleporter(list[(idx + dir + list.length) % list.length]);
  }

  closeBtn.addEventListener('click', closePlacard);
  if (prevBtn) prevBtn.addEventListener('click', () => stepWork(-1));
  if (nextBtn) nextBtn.addEventListener('click', () => stepWork(1));

  function activate(hit) {
    const kind = kindOf(hit);
    if (kind === 'door') { if (doorHandler) doorHandler(hit); return { kind: 'door', target: hit.userData.target }; }
    if (kind === 'sculpture') return openSculpture(hit);
    if (kind === 'art') return openPlacard(hit.name);
    return null;
  }
  function prevWork() { stepWork(-1); }
  function nextWork() { stepWork(1); }
  function openAtCrosshair() { return activate(pick()); }
  function openAtScreen(x, y) { return activate(pick(x, y)); }

  function onClick(e) {
    if (domElement && e.target !== domElement) return; // clicks on panels/buttons are theirs
    if (!isLockedFn()) return;
    openAtCrosshair();
  }
  document.addEventListener('click', onClick);

  // Look-at prompt under the crosshair (every 3rd frame).
  function promptFor(hit) {
    const kind = kindOf(hit);
    if (kind === 'door') {
      const u = hit.userData;
      return u.target === 'hub' ? 'Back to the Grand Hall · click / E' : `Enter ${u.name || u.target}${u.years ? ` · ${u.years}` : ''} · click / E`;
    }
    if (kind === 'sculpture') {
      const c = hit.userData.credits || {};
      return `${c.title || hit.userData.model}${c.artist ? ` — ${c.artist}` : ''} · click / E to read`;
    }
    const entry = manifestIndex.byMeshName.get(hit.name);
    if (!entry) return '';
    const t = entry.work.title || '';
    const a = entry.artist.name || '';
    return `${t && t !== a ? `${t} — ${a}` : a} · click / E to read`;
  }

  function update() {
    frame++;
    if (frame % 3) return;
    const hit = isLockedFn() ? pick() : null;
    if (hit === hovered) return;
    hovered = hit;
    if (!promptEl) return;
    if (hit) {
      promptEl.textContent = promptFor(hit);
      promptEl.hidden = false;
      if (crosshair) crosshair.classList.add('hot');
    } else {
      promptEl.hidden = true;
      if (crosshair) crosshair.classList.remove('hot');
    }
  }

  // Where to stand to look at an entry's work (used by navigate.js / tour.js).
  function spotFor(entry, distance = null) {
    const mesh = artMeshes.find((m) => m.name === entry.meshName);
    if (!mesh) return null;
    const d = distance || Math.max(2.0, Math.min(5.0, 1.1 * Math.max(mesh.userData.w || 1, mesh.userData.h || 1) + 1.2));
    return viewingSpot(mesh, { walls: walls(), groundY, distance: d });
  }

  return {
    setArtMeshes, setPickables, setTeleporter, onDoor, openPlacard, openSculpture, closePlacard, isOpen, openAtCrosshair, openAtScreen, prevWork, nextWork,
    current: () => current, hovered: () => hovered, update, imageUrl, spotFor, pick, pickArt, rewritesReady,
  };
}
