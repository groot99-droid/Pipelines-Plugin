// "Go to" panel (Tab): wing -> room -> artist -> works, with a live filter. Clicking a
// work or an artist's arrow teleports to the viewing spot in front of the work and opens
// its placard; "guide" draws the waypoint trail instead.
import { yawToward } from './coords.js';

function esc(t) {
  return String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

export function createNavigate({ manifest, manifestIndex, camera, controls, interactions, waypointTrail, getCurrentRoomId, teleportToRoom = null, lights = null, fade = null, scenes = null }) {
  const roomsById = new Map(manifest.rooms.map((r) => [r.id, r]));

  const panel = document.createElement('div');
  panel.id = 'nav-panel';
  panel.innerHTML = `
    <button type="button" class="nav-close" aria-label="Close">&times;</button>
    <div class="nav-head"><h2>Go to</h2><input type="search" id="nav-filter" placeholder="Filter artists and works&hellip;" autocomplete="off"></div>
    <div class="nav-list"></div>`;
  document.body.appendChild(panel);
  const input = panel.querySelector('#nav-filter');
  const list = panel.querySelector('.nav-list');
  let isOpen = false;

  // ---- tree ------------------------------------------------------------------------------
  const rows = []; // {el, kind, text, parent, children}
  function build() {
    list.innerHTML = '';
    rows.length = 0;
    const artistsByRoom = new Map();
    for (const a of manifest.artists) {
      if (!artistsByRoom.has(a.room)) artistsByRoom.set(a.room, []);
      artistsByRoom.get(a.room).push(a);
    }
    for (const wing of manifestIndex.wings) {
      const wingEl = document.createElement('div');
      wingEl.className = 'nav-wing';
      wingEl.textContent = wing.name || wing.id;
      list.appendChild(wingEl);
      const wingRow = { el: wingEl, kind: 'wing', children: [] };
      rows.push(wingRow);
      for (const roomId of wing.rooms || []) {
        const artists = (artistsByRoom.get(roomId) || []).slice().sort((a, b) => (a.order || 0) - (b.order || 0));
        if (!artists.length) continue;
        const room = roomsById.get(roomId);
        const roomEl = document.createElement('div');
        roomEl.className = 'nav-room';
        roomEl.textContent = room ? room.name : roomId;
        roomEl.title = 'Teleport to this room';
        roomEl.addEventListener('click', () => { if (teleportToRoom) { close(); teleportToRoom(roomId); } });
        list.appendChild(roomEl);
        const roomRow = { el: roomEl, kind: 'room', children: [], parent: wingRow };
        rows.push(roomRow);
        wingRow.children.push(roomRow);
        for (const a of artists) {
          const entries = a.works.map((w) => manifestIndex.byMeshName.get(`ART-${a.slug}__${w.id}`)).filter(Boolean);
          const aEl = document.createElement('div');
          aEl.className = 'nav-artist';
          aEl.innerHTML = `<span>${esc(a.name)} <small>${esc(a.lifespan || '')}</small></span><button type="button" title="Go to ${esc(a.name)}">&rarr;</button>`;
          const worksEl = document.createElement('div');
          worksEl.className = 'nav-works';
          worksEl.hidden = true;
          const artistRow = { el: aEl, kind: 'artist', text: `${a.name} ${a.short_name || ''}`.toLowerCase(), children: [], parent: roomRow, worksEl, entries };
          rows.push(artistRow);
          roomRow.children.push(artistRow);
          aEl.querySelector('button').addEventListener('click', (e) => { e.stopPropagation(); if (entries[0]) goToEntry(entries[0]); });
          aEl.addEventListener('click', () => { worksEl.hidden = !worksEl.hidden; });
          for (const entry of entries) {
            const wEl = document.createElement('div');
            wEl.className = 'nav-work';
            wEl.textContent = entry.work.title || entry.work.id;
            wEl.addEventListener('click', (e) => { e.stopPropagation(); goToEntry(entry); });
            worksEl.appendChild(wEl);
            const workRow = { el: wEl, kind: 'work', text: `${entry.work.title || ''} ${entry.work.id}`.toLowerCase(), parent: artistRow, entry };
            rows.push(workRow);
            artistRow.children.push(workRow);
          }
          list.appendChild(aEl);
          list.appendChild(worksEl);
        }
      }
    }
    const empty = document.createElement('div');
    empty.className = 'nav-empty';
    empty.hidden = true;
    empty.textContent = 'Nothing matches.';
    list.appendChild(empty);
    rows.emptyEl = empty;
  }

  function filter(text) {
    const q = String(text || '').trim().toLowerCase();
    let visibleCount = 0;
    for (const r of rows) {
      if (r.kind === 'artist') {
        const artistHit = !q || r.text.includes(q);
        let anyWork = false;
        for (const w of r.children) {
          const hit = !!q && w.text.includes(q);
          w.el.hidden = !!q && !hit && !artistHit; // with a query, an artist match keeps all their works listed
          anyWork = anyWork || hit;
        }
        const show = artistHit || anyWork;
        r.el.hidden = !show;
        r.worksEl.hidden = !q || !anyWork; // works unfold only for matches; an artist row toggles them by click
        if (show) visibleCount++;
      }
    }
    for (const r of rows) {
      if (r.kind === 'room') r.el.hidden = !r.children.some((a) => !a.el.hidden);
    }
    for (const r of rows) {
      if (r.kind === 'wing') r.el.hidden = !r.children.some((room) => !room.el.hidden);
    }
    if (rows.emptyEl) rows.emptyEl.hidden = visibleCount > 0;
    return visibleCount;
  }

  // Stand in front of the work (and open its placard), entering its room's scene first.
  async function goToEntry(entry, { open = true, distance = null } = {}) {
    if (scenes && scenes.currentId() !== entry.room) {
      const w = await scenes.enter(entry.room, { via: null, fade: true });
      if (!w) return false;
    }
    const spot = interactions.spotFor(entry, distance);
    if (!spot) return false;
    if (fade) fade();
    controls.teleport(spot.position, { lookAt: spot.lookAt });
    if (lights) lights.update(camera, 0, true);
    close();
    if (open) interactions.openPlacard(entry.meshName);
    else interactions.closePlacard();
    return true;
  }
  function goToWork(workId, opts) {
    const entry = manifestIndex.byWorkId.get(workId);
    return entry ? goToEntry(entry, opts) : Promise.resolve(false);
  }
  function guideTo(entry) {
    waypointTrail.showPathTo(getCurrentRoomId(), entry.room, camera.position);
  }

  function open() {
    isOpen = true;
    panel.classList.add('open');
    if (document.pointerLockElement && document.exitPointerLock) document.exitPointerLock(); // the panel is clicked with a free cursor
    // focus once the slide-in has started; never grab it if the panel was closed meanwhile
    // (a focused hidden input would swallow every hotkey)
    setTimeout(() => { if (isOpen) input.focus({ preventScroll: true }); }, 50);
  }
  function close() {
    isOpen = false;
    panel.classList.remove('open');
    if (document.activeElement === input) input.blur();
  }
  function toggle() { if (isOpen) close(); else open(); }

  input.addEventListener('input', () => filter(input.value));
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') { e.preventDefault(); close(); }
    if (isOpen) e.stopPropagation(); // typing in the filter never triggers viewer hotkeys
    else input.blur();
  });
  panel.querySelector('.nav-close').addEventListener('click', close);
  panel.addEventListener('click', (e) => e.stopPropagation());

  build();
  interactions.setTeleporter((entry) => goToEntry(entry));

  return { open, close, toggle, isOpen: () => isOpen, filter, goToEntry, goToWork, guideTo, rebuild: build, panel, yawToward };
}
