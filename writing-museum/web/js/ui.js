// Key router, help overlay, blocker buttons, HUD buttons and the manifest-driven subtitle.
function isEditable(t) {
  return !!t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable);
}

// "973–1968" from year strings (numbers between 500 and 2100), or null. The Art-Talk
// timeline spans the artists' lives, so the subtitle uses lifespans (works as a fallback).
export function yearRange(items, field = 'year') {
  let lo = Infinity, hi = -Infinity;
  for (const w of items) {
    const m = String(w[field] || '').match(/\d{3,4}/g);
    if (!m) continue;
    for (const t of m) {
      const y = parseInt(t, 10);
      if (y < 500 || y > 2100) continue;
      lo = Math.min(lo, y);
      hi = Math.max(hi, y);
    }
  }
  return lo === Infinity ? null : `${lo}–${hi}`;
}

export function subtitleFor(manifest, manifestIndex) {
  const parts = [];
  for (const wing of manifestIndex.wings) {
    const artists = manifest.artists.filter((a) => (a.wing || manifestIndex.wings[0].id) === wing.id);
    const works = artists.flatMap((a) => a.works);
    if (!artists.length) continue;
    const nouns = wing.nouns || ['artists', 'works'];
    const range = wing.years || yearRange(artists, 'lifespan') || yearRange(works, 'year');
    parts.push(`${wing.name} — ${artists.length} ${nouns[0]}, ${works.length} ${nouns[1]}${range ? `, ${range}` : ''}`);
  }
  return parts;
}

export function createUI({ manifest, manifestIndex, controls, interactions, hud, navigate, tour, persist = null, enter }) {
  const blocker = document.getElementById('blocker');
  const subtitleEl = document.getElementById('blocker-subtitle');
  const btnExplore = document.getElementById('btn-explore');
  const btnTour = document.getElementById('btn-tour');
  const btnResume = document.getElementById('btn-resume');

  // ---- subtitle ---------------------------------------------------------------------------
  function setSubtitle() {
    if (!subtitleEl) return;
    const parts = subtitleFor(manifest, manifestIndex);
    subtitleEl.innerHTML = parts.map((p) => `<span>${p.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span>`).join('<br>');
  }
  setSubtitle();

  // ---- help overlay -----------------------------------------------------------------------
  const help = document.createElement('div');
  help.id = 'help';
  help.innerHTML = `
    <div class="help-box">
      <h2>How to visit</h2>
      <table>
        <tr><td><kbd>W</kbd> <kbd>A</kbd> <kbd>S</kbd> <kbd>D</kbd> / arrows</td><td>walk</td></tr>
        <tr><td>mouse</td><td>look around (click the view to capture the mouse; drag if your browser blocks it)</td></tr>
        <tr><td>click / <kbd>E</kbd></td><td>read the passage under the crosshair · go through the door you are looking at</td></tr>
        <tr><td><kbd>M</kbd></td><td>floor plan: click a door to go through it, a room to go there</td></tr>
        <tr><td><kbd>Tab</kbd></td><td>go to a work or a passage (filter, teleport, guide trail)</td></tr>
        <tr><td><kbd>Space</kbd> <kbd>N</kbd> <kbd>P</kbd></td><td>guided tour: pause, next, previous</td></tr>
        <tr><td><kbd>Esc</kbd></td><td>close panels, end the tour, release the mouse</td></tr>
        <tr><td><kbd>?</kbd> / <kbd>H</kbd></td><td>this help</td></tr>
        <tr><td>touch</td><td>left half: joystick to walk · right half: drag to look · tap a passage to read</td></tr>
        <tr><td>controller</td><td>left stick / D-pad walk · right stick look · <kbd>A</kbd> read, go through the door · <kbd>B</kbd> back · <kbd>X</kbd> map · <kbd>Y</kbd> go to · <kbd>LB</kbd> <kbd>RB</kbd> previous / next · Menu help · View tour</td></tr>
      </table>
      <button type="button" class="help-close">Close</button>
    </div>`;
  document.body.appendChild(help);
  let helpOpen = false;
  function showHelp() { helpOpen = true; help.classList.add('open'); }
  function hideHelp() { helpOpen = false; help.classList.remove('open'); }
  function toggleHelp() { if (helpOpen) hideHelp(); else showHelp(); }
  help.querySelector('.help-close').addEventListener('click', hideHelp);
  help.addEventListener('click', (e) => { if (e.target === help) hideHelp(); });

  // ---- HUD buttons (touch users have no keys) ----------------------------------------------
  const hudButtons = document.createElement('div');
  hudButtons.id = 'hud-buttons';
  const mk = (label, title, fn) => {
    const b = document.createElement('button');
    b.type = 'button';
    b.textContent = label;
    b.title = title;
    b.addEventListener('click', (e) => { e.stopPropagation(); fn(); });
    hudButtons.appendChild(b);
    return b;
  };
  mk('Map', 'Floor plan (M)', () => hud.toggleMap());
  mk('Go to', 'Works and passages (Tab)', () => navigate.toggle());
  const tourBtn = mk('Tour', 'Guided tour', () => toggleTour());
  mk('?', 'Help (?)', toggleHelp);
  document.body.appendChild(hudButtons);

  // ---- blocker buttons --------------------------------------------------------------------
  const tourWing = document.getElementById('tour-wing');
  if (tourWing) {
    tourWing.innerHTML = '';
    const all = document.createElement('option');
    all.value = '';
    all.textContent = 'whole museum';
    tourWing.appendChild(all);
    if (manifestIndex.wings.length > 1) {
      for (const w of manifestIndex.wings) {
        const o = document.createElement('option');
        o.value = w.id;
        o.textContent = w.name || w.id;
        tourWing.appendChild(o);
      }
    } else tourWing.hidden = true;
    tourWing.addEventListener('click', (e) => e.stopPropagation());
  }
  function tourWorks() {
    const id = tourWing ? tourWing.value : '';
    return id ? manifestIndex.flatWorks.filter((e) => e.wing === id) : manifestIndex.flatWorks;
  }
  if (btnTour) btnTour.addEventListener('click', (e) => { e.stopPropagation(); tour.start({ works: tourWorks() }); });
  if (btnResume) {
    btnResume.hidden = !(persist && persist.hasSave());
    btnResume.addEventListener('click', async (e) => {
      e.stopPropagation();
      if (persist) await persist.restore();
      enter();
    });
  }

  // ---- key router -------------------------------------------------------------------------
  // The Esc cascade: close the topmost thing (help, map, Go to, placard, then the tour). Also the
  // controller's B button. Returns true when something was closed.
  function back() {
    if (helpOpen) hideHelp();
    else if (hud.isMapOpen()) hud.closeMap();
    else if (navigate.isOpen()) navigate.close();
    else if (interactions.isOpen()) interactions.closePlacard();
    else if (tour.active()) tour.stop();
    else return false;
    return true;
  }
  function toggleTour() { if (tour.active()) tour.stop(); else tour.start({ works: tourWorks() }); }
  function onKey(e) {
    if (isEditable(e.target)) return;
    if (e.key === '?') { toggleHelp(); return; }
    switch (e.code) {
      case 'KeyE':
        if (interactions.isOpen()) interactions.closePlacard();
        else if (interactions.openAtCrosshair()) e.preventDefault();
        break;
      case 'Escape': back(); break;
      case 'KeyM': hud.toggleMap(); break;
      case 'Tab': e.preventDefault(); navigate.toggle(); break;
      case 'KeyH': toggleHelp(); break;
      case 'Space': if (tour.active()) { e.preventDefault(); tour.togglePause(); } break;
      case 'KeyN': if (tour.active()) tour.next(); break;
      case 'KeyP': if (tour.active()) tour.prev(); break;
    }
  }
  document.addEventListener('keydown', onKey);

  function update() {
    const active = tour.active();
    if (tourBtn) tourBtn.textContent = active ? 'End tour' : 'Tour';
  }

  return { setSubtitle, showHelp, hideHelp, toggleHelp, isHelpOpen: () => helpOpen, back, toggleTour, update, blocker, btnExplore, btnTour, btnResume };
}
