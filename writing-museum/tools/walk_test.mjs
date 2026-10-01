#!/usr/bin/env node
// Browser walk-through tests for the Writing Museum viewer.
//
//   node writing-museum/tools/walk_test.mjs [--out DIR] [--grep NAME[,NAME]] [--no-shots] [--headed] [--list]
//
// The Chronicle Museum's harness (Earth_Worldbuild/_Museum/tools/walk_test.mjs), driven by the
// manifest instead of fixed room ids: it starts a static server on the tool folder, opens the
// viewer in headless Chromium (software WebGL is fine) with ?test (no animation loop) and drives
// it through window.museumDebug. Every scene has its own origin (rooms: hall door at (0, 0) on the
// south wall), so assertions are scene-local Blender metres (x east, y north, z up). Screenshots
// and report.json go to --out (default writing-museum/tools/out, git-ignored). The first test runs
// the Python lint (build_museum.py build --lint). With no scenes built yet, the room tests are
// skipped and the hall alone is checked.
//
// Playwright is loaded from the global install (/opt/node22/lib/node_modules or NODE_PATH) and
// Chromium from $CHROMIUM or /opt/pw-browsers/chromium.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { spawnSync } from 'node:child_process';

const require = createRequire(import.meta.url);
function loadPlaywright() {
  try { return require('playwright'); } catch (e) { /* fall through */ }
  for (const p of ['/opt/node22/lib/node_modules/playwright', '/usr/lib/node_modules/playwright']) {
    try { return require(p); } catch (e) { /* next */ }
  }
  throw new Error('playwright not found: npm i -g playwright (or set NODE_PATH)');
}
const { chromium } = loadPlaywright();

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');            // the tool folder: web/, data/, assets/
const args = process.argv.slice(2);
const opt = {
  out: path.join(__dirname, 'out'), grep: null, shots: true, headed: false, list: false,
  chromium: process.env.CHROMIUM || '/opt/pw-browsers/chromium', timeout: 180000,
};
for (let i = 0; i < args.length; i++) {
  const a = args[i];
  if (a === '--out') opt.out = path.resolve(args[++i]);
  else if (a === '--grep') opt.grep = args[++i];
  else if (a === '--no-shots') opt.shots = false;
  else if (a === '--headed') opt.headed = true;
  else if (a === '--list') opt.list = true;
  else if (a === '--chromium') opt.chromium = args[++i];
}
if (!fs.existsSync(opt.chromium)) opt.chromium = undefined;

const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.png': 'image/png', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.txt': 'text/plain; charset=utf-8',
  '.md': 'text/plain; charset=utf-8', '.wasm': 'application/wasm', '.gltf': 'model/gltf+json', '.glb': 'model/gltf-binary',
  '.bin': 'application/octet-stream',
};

function startServer() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      let p;
      try { p = decodeURIComponent(new URL(req.url, 'http://x').pathname); } catch (e) { res.writeHead(400); res.end(); return; }
      const file = path.normalize(path.join(ROOT, p));
      if (!file.startsWith(ROOT)) { res.writeHead(403); res.end(); return; }
      fs.stat(file, (err, st) => {
        if (err || !st.isFile()) { res.writeHead(404); res.end('not found'); return; }
        res.writeHead(200, { 'Content-Type': MIME[path.extname(file).toLowerCase()] || 'application/octet-stream', 'Content-Length': st.size, 'Cache-Control': 'no-store' });
        if (req.method === 'HEAD') { res.end(); return; }
        fs.createReadStream(file).pipe(res);
      });
    });
    server.listen(0, '127.0.0.1', () => resolve({ server, port: server.address().port }));
  });
}

// ---- page helpers (run inside the browser through page.evaluate) -----------------------
const H = {
  at: ([bx, by, bz, heading]) => {
    const D = window.museumDebug;
    const t = (heading * Math.PI) / 180;
    const yaw = Math.atan2(-Math.cos(t), Math.sin(t));
    D.controls.setPosition(bx, bz + 1.7, -by);
    D.controls.setLook(yaw, 0);
    D.controls.setKeys({});
    D.controls.setCollision(true);
    D.enter({ pointerLock: false });
    return D.step(1 / 60, 2);
  },
  walk: ([dir, seconds]) => {
    const D = window.museumDebug;
    D.controls.setKeys({ [dir]: true });
    const s = D.step(1 / 60, Math.round(seconds * 60));
    D.controls.setKeys({});
    return s;
  },
  snap: () => window.museumDebug.snapshot(),
};
const ignoreConsole = (t) => /favicon\.ico/.test(t);

class Ctx {
  constructor(browser, base) { this.browser = browser; this.base = base; this.page = null; this.errors = []; this.query = null; this.context = null; }
  async load(query = 'test', { fresh = false } = {}) {
    if (!fresh && this.page && this.query === query) return this.page;
    if (this.page) await this.page.close();
    if (!this.context) this.context = await this.browser.newContext({ viewport: { width: 1280, height: 720 } });
    this.errors = [];
    this.query = query;
    const page = await this.context.newPage();
    page.on('console', (m) => {
      if (m.type() !== 'error') return;
      const loc = m.location && m.location();
      const url = (loc && loc.url) || '';
      if (ignoreConsole(`${m.text()} ${url}`)) return;
      this.errors.push(`${m.text()}${url ? ` (${url})` : ''}`);
    });
    page.on('pageerror', (e) => this.errors.push(String(e)));
    await page.goto(`${this.base}/web/index.html?${query}`, { waitUntil: 'domcontentloaded' });
    await page.waitForFunction(() => window.museumDebug && window.museumDebug.ready, null, { timeout: opt.timeout });
    this.page = page;
    return page;
  }
  async at(bx, by, bz, heading = 0) { return this.page.evaluate(H.at, [bx, by, bz, heading]); }
  async walk(dir, seconds) { return this.page.evaluate(H.walk, [dir, seconds]); }
  async snap() { return this.page.evaluate(H.snap); }
  async ev(fn, arg) { return this.page.evaluate(fn, arg); }
  async shot(name) {
    if (!opt.shots) return null;
    await this.page.evaluate(() => { window.museumDebug.step(1 / 60, 30); window.museumDebug.renderOnce(); });
    await this.page.waitForTimeout(450);
    const file = path.join(opt.out, `${name}.png`);
    await this.page.screenshot({ path: file, timeout: 120000 });
    shots.push(file);
    return file;
  }
}

const tests = [];
const shots = [];
function test(name, fn) { tests.push({ name, fn }); }
function assert(cond, msg) { if (!cond) throw new Error(msg); }
const near = (v, target, tol) => Math.abs(v - target) <= tol;
const between = (v, lo, hi) => v >= lo && v <= hi;
const fmt = (b) => `(${b.map((v) => v.toFixed(2)).join(', ')})`;

// ---- the manifest on disk decides what is tested -------------------------------------------
const MANIFEST_PATH = path.join(ROOT, 'data', 'museum-manifest.json');
const LAYOUT_PATH = path.join(ROOT, 'data', 'museum-layout.json');
const manifestOnDisk = fs.existsSync(MANIFEST_PATH) ? JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8')) : { rooms: [], artists: [], wings: [] };
const layoutOnDisk = fs.existsSync(LAYOUT_PATH) ? JSON.parse(fs.readFileSync(LAYOUT_PATH, 'utf-8')) : { order: [], scenes: {} };
const ROOM_IDS = layoutOnDisk.order || [];
const worksInRoom = (manifest, room) => manifest.artists.filter((a) => a.room === room).reduce((n, a) => n + a.works.length, 0);
const firstPanel = (room) => { const a = manifestOnDisk.artists.find((x) => x.room === room); return a ? a.works[0] : null; };
const N_ROOMS = ROOM_IDS.length;
const N_WORKS = manifestOnDisk.artists.length;
const N_PANELS = manifestOnDisk.artists.reduce((n, a) => n + a.works.length, 0);

// ---- shared browser helpers ---------------------------------------------------------------
const B = {
  faceDoor: (name) => {
    const D = window.museumDebug, T = D.THREE;
    const d = D.lists.doors.find((m) => m.name === name);
    if (!d) return { probe: null, prompt: `no ${name}` };
    const c = d.userData.center, f = d.userData.facing;
    D.controls.setCollision(true);
    D.controls.teleport(new T.Vector3(c.x + f.x * 2.0, 1.7, c.z + f.z * 2.0), { lookAt: new T.Vector3(c.x, 1.5, c.z) });
    D.enter({ pointerLock: false });
    D.step(1 / 60, 3);
    return { probe: D.probeArt(), prompt: document.getElementById('look-prompt').textContent };
  },
  settle: async () => {
    const D = window.museumDebug;
    await new Promise((r) => setTimeout(r, 30));
    while (D.scenes.isSwitching()) await new Promise((r) => setTimeout(r, 30));
    await D.scenes.world().whenLoaded();
    D.step(1 / 60, 5);
    return D.snapshot();
  },
  counts: () => {
    const D = window.museumDebug;
    return { scene: D.scenes.currentId(), art: D.lists.art.length, walls: D.lists.walls.length, floors: D.lists.floors.length,
      doors: D.lists.doors.length, pickables: D.lists.pickables.length, rooms: D.rooms.size, room: D.getCurrentRoomId(),
      geoRoom: D.snapshot().geoRoom, pipeline: D.pipeline.mode };
  },
};

// ---- 0. python lint --------------------------------------------------------------------------
test('lint_prestep', async () => {
  const py = process.env.PYTHON || 'python3';
  const a = spawnSync(py, [path.join(ROOT, 'build', 'build_museum.py'), 'build', '--lint'], { encoding: 'utf-8' });
  assert(a.status === 0, `build_museum.py build --lint failed:\n${(a.stdout || '').slice(-1500)}\n${(a.stderr || '').slice(-800)}`);
  assert(fs.existsSync(MANIFEST_PATH) && fs.existsSync(LAYOUT_PATH), 'data/museum-manifest.json and data/museum-layout.json must be built (build_museum.py build)');
  for (const a2 of manifestOnDisk.artists) for (const w of a2.works) {
    assert(typeof w.text === 'string' && w.text.length > 0 && w.dims && w.dims.h_m > 0, `${w.id}: a passage needs text and dims`);
    assert(w.credit && w.credit.source_path && Array.isArray(w.credit.lines), `${w.id}: a passage cites its vault path and lines`);
  }
  return { lint: a.stdout.trim().split('\n').slice(-1)[0], rooms: N_ROOMS, works: N_WORKS, panels: N_PANELS };
});

// ---- 1. the hall -----------------------------------------------------------------------------
test('load', async (c) => {
  await c.load('test');
  const n = await c.ev(B.counts);
  assert(n.scene === 'hub' && n.room === 'hub', `expected to start in the hall, got ${JSON.stringify(n)}`);
  assert(n.doors === N_ROOMS, `expected ${N_ROOMS} doors, got ${n.doors}`);
  assert(n.art === 0, `the hall hangs no works, got ${n.art}`);
  assert(n.walls >= 6 && n.floors >= 2, `hall geometry: ${JSON.stringify(n)}`);
  const sub = await c.ev(() => document.getElementById('blocker-subtitle').textContent);
  if (N_WORKS) assert(sub.includes(`${N_WORKS} works, ${N_PANELS} passages`), `subtitle: ${sub}`);
  const layout = await c.ev(() => Object.keys(window.museumDebug.layout.scenes).length);
  assert(layout === N_ROOMS + 1, `layout scenes: ${layout}`);
  const sky = await c.ev(() => { const b = window.museumDebug.scene.background; return b && b.isTexture ? [b.image.width, b.image.height] : null; });
  assert(sky && sky[0] === 2 * sky[1], `assets/sky.jpg should be the equirectangular background, got ${JSON.stringify(sky)}`);
  assert(c.errors.length === 0, `console errors: ${c.errors.join(' | ')}`);
  await c.ev(async () => { await window.museumDebug.scenes.world().whenLoaded(); window.museumDebug.renderOnce(); });
  await c.shot('view_hub_spawn');
  return n;
});

test('hub_walk_and_walls', async (c) => {
  await c.load('test');
  const L = layoutOnDisk.scenes.hub.size[0];
  let s = await c.at(0, 2.2, 0, 0);
  s = await c.walk('forward', Math.min(8, L / 4.2 * 0.6));
  assert(s.blender[0] > 10 && s.geoRoom === 'hub', `walked east along the hall: ${fmt(s.blender)} in ${s.geoRoom}`);
  await c.at(L / 2, 0, 0, 90);
  s = await c.walk('forward', 3);
  assert(s.blender[1] < 3.95, `the north wall should block at y=4: ${fmt(s.blender)}`);
  await c.at(L / 2, 0, 0, 270);
  s = await c.walk('forward', 3);
  assert(s.blender[1] > -3.95, `the south wall should block at y=-4: ${fmt(s.blender)}`);
  await c.at(-2, 2.5, 0, 180);
  s = await c.walk('forward', 4);
  assert(s.blender[0] > -13.9 && s.blender[0] < -9, `the rotunda drum should stop the walk: ${fmt(s.blender)}`);
  assert(s.geoRoom === 'hub', `still in the hall geo room: ${s.geoRoom}`);
  return s.blender;
});

// ---- 2. every door -----------------------------------------------------------------------------
for (const room of ROOM_IDS) {
  test(`door_${room}`, async (c) => {
    await c.load('test');
    const manifest = await c.ev(() => window.museumDebug.manifest);
    if (await c.ev(() => window.museumDebug.scenes.currentId()) !== 'hub') {
      await c.ev(async () => { await window.museumDebug.enterRoom('hub', { fade: false }); });
      await c.ev(B.settle);
    }
    const f = await c.ev(B.faceDoor, `DOOR-${room}`);
    assert(f.probe === `DOOR-${room}`, `looking at the door should probe it, got ${f.probe}`);
    assert(/^Enter /.test(f.prompt), `door prompt: ${f.prompt}`);
    await c.page.mouse.click(640, 360);
    const s = await c.ev(B.settle);
    const n = await c.ev(B.counts);
    assert(n.scene === room && n.room === room, `after the click expected ${room}, got ${JSON.stringify(n)}`);
    const expected = worksInRoom(manifest, room);
    assert(n.art === expected, `${room}: ${n.art} panels hung, manifest has ${expected}`);
    const check = await c.ev((rid) => {
      const D = window.museumDebug;
      const unknown = D.lists.art.filter((m) => !D.manifestIndex.byMeshName.has(m.name)).length;
      const wrongRoom = D.lists.art.filter((m) => m.userData.room !== rid).length;
      const untextured = D.lists.art.filter((m) => !(m.material.map && m.material.map.isCanvasTexture)).length;
      const title = document.getElementById('title-card');
      const style = D.layout.scenes[rid].style;
      const floor = D.scene.getObjectByName(`GEO-${rid}_floor`);
      return { unknown, wrongRoom, untextured, titleShown: title && title.classList.contains('visible'), titleText: title ? title.textContent.trim().slice(0, 40) : '',
        floorSlot: floor && floor.material.userData.slot, wantFloor: style.floor, wallTint: D.lists.walls.find((m) => /wallN/.test(m.name)) ? '#' + D.lists.walls.find((m) => /wallN/.test(m.name)).material.color.getHexString() : null, wantWall: style.wall };
    }, room);
    assert(check.unknown === 0 && check.wrongRoom === 0, `art meshes: ${JSON.stringify(check)}`);
    assert(check.untextured === 0, `${check.untextured} panels without a drawn text texture`);
    assert(check.titleShown, `title card should show on entry: ${JSON.stringify(check)}`);
    assert(check.floorSlot === check.wantFloor, `floor material follows the scene style: ${JSON.stringify(check)}`);
    assert(check.wallTint && check.wallTint.toLowerCase() === check.wantWall.toLowerCase(), `wall tint follows the scene style: ${JSON.stringify(check)}`);
    assert(near(s.blender[0], 0, 0.3) && between(s.blender[1], 1.5, 4.0), `arrived just inside the hall door: ${fmt(s.blender)}`);
    const w = await c.walk('forward', 4);
    assert(w.geoRoom === room && w.blender[1] > 4, `walking into the room: ${fmt(w.blender)} in ${w.geoRoom}`);
    await c.ev(async (rid) => { await window.museumDebug.setView(`${rid}_door`); }, room);
    await c.shot(`view_${room}`);
    const g = await c.ev(B.faceDoor, 'DOOR-hub');
    assert(g.probe === 'DOOR-hub' && /Hall/.test(g.prompt), `hall door: ${JSON.stringify(g)}`);
    await c.page.keyboard.press('KeyE');
    await c.ev(B.settle);
    const back = await c.ev(B.counts);
    assert(back.scene === 'hub' && back.art === 0 && back.doors === N_ROOMS, `back in the hall: ${JSON.stringify(back)}`);
    const pos = await c.snap();
    const hubDoor = manifest.rooms.find((r) => r.id === 'hub').doors[room];
    assert(near(pos.blender[0], hubDoor[0], 0.5) && Math.abs(pos.blender[1]) < 3.9, `spawned inside the hall by the ${room} door: ${fmt(pos.blender)} vs ${fmt(hubDoor)}`);
    assert(c.errors.length === 0, `console errors: ${c.errors.join(' | ')}`);
    return { panels: n.art, spawn: s.blender.map((v) => +v.toFixed(2)) };
  });
}

// ---- 3. passages, placards, sizes ------------------------------------------------------------
if (N_ROOMS) {
  test('placard_shows_the_passage', async (c) => {
    await c.load('test');
    const p = firstPanel(ROOM_IDS[0]);
    const r = await c.ev(async (id) => {
      const D = window.museumDebug;
      const ok = await D.navigate.goToWork(id);
      await D.scenes.world().whenLoaded();
      D.step(1 / 60, 3);
      const text = (s) => document.getElementById(s).textContent;
      const out = { ok, meta: text('placard-meta'), title: text('placard-title'), desc: text('placard-description'), credit: text('placard-credit'),
        imageHidden: document.getElementById('placard-image-wrap').hidden, scene: D.scenes.currentId() };
      D.interactions.closePlacard();
      D.enter({ pointerLock: false });
      D.step(1 / 60, 4);
      out.probe = D.probeArt();
      out.prompt = text('look-prompt');
      D.interactions.openAtCrosshair();
      out.open = D.interactions.isOpen();
      return out;
    }, p.id);
    assert(r.ok && r.scene === ROOM_IDS[0], `goToWork: ${JSON.stringify(r)}`);
    assert(r.title === p.title, `title: ${r.title} vs ${p.title}`);
    const flat = (t) => t.replace(/[\s*]+/g, '');   // the placard renders *italics* as <em>
    assert(flat(r.desc).startsWith(flat(p.text).slice(0, 60)), `the placard shows the passage: ${r.desc.slice(0, 80)}`);
    assert(r.credit.includes(p.credit.source_path) && r.credit.includes(`lines ${p.credit.lines[0]}`), `citation on the placard: ${r.credit}`);
    assert(r.imageHidden, 'a passage has no image on its placard');
    assert(/panel \d/.test(r.meta), `panel size on the placard: ${r.meta}`);
    assert(r.probe && r.probe.endsWith(`__${p.id}`) && /click \/ E to read/.test(r.prompt), `look prompt: ${JSON.stringify(r)}`);
    assert(r.open, 'clicking the panel under the crosshair opens the placard');
    await c.shot('feature_placard');
    return r;
  });

  test('hang_sizes_match_dims', async (c) => {
    await c.load('test');
    const bad = [];
    for (const room of ROOM_IDS.slice(0, 3)) {
      const r = await c.ev(async (rid) => {
        const D = window.museumDebug;
        await D.enterRoom(rid, { fade: false });
        await D.scenes.world().whenLoaded();
        const hangs = D.layout.scenes[rid].hangs;
        const out = [];
        const box = new D.THREE.Box3(), size = new D.THREE.Vector3();
        for (const m of D.lists.art) {
          const e = D.manifestIndex.byMeshName.get(m.name);
          const h = hangs[e.work.id];
          box.setFromObject(m); box.getSize(size);
          const w = Math.max(size.x, size.z), hh = size.y;
          const expW = e.work.dims.disp_w * h.scale, expH = e.work.dims.disp_h * h.scale;
          if (Math.abs(w - expW) > 0.02 || Math.abs(hh - expH) > 0.02) out.push(`${e.work.id}: ${w.toFixed(2)}×${hh.toFixed(2)} vs ${expW.toFixed(2)}×${expH.toFixed(2)}`);
        }
        return out;
      }, room);
      bad.push(...r);
    }
    assert(bad.length === 0, `hung sizes differ from the panel dims: ${bad.slice(0, 5).join('; ')}`);
    return 'ok';
  });

  test('no_art_overlap', async (c) => {
    await c.load('test');
    const r = await c.ev(() => {
      const D = window.museumDebug;
      const bad = [];
      for (const [rid, sc] of Object.entries(D.layout.scenes)) {
        const byWall = {};
        for (const h of Object.values(sc.hangs || {})) (byWall[h.wall] = byWall[h.wall] || []).push(h);
        for (const lst of Object.values(byWall)) {
          for (let i = 0; i < lst.length; i++) for (let j = i + 1; j < lst.length; j++) {
            const a = lst[i], b = lst[j];
            const fa = a.frame.width + 0.01, fb = b.frame.width + 0.01;
            const ox = Math.abs(a.along - b.along) < (a.w + b.w) / 2 + fa + fb + 0.24;
            const oz = Math.abs(a.pos[2] - b.pos[2]) < (a.h + b.h) / 2 + fa + fb + 0.2;
            if (ox && oz) bad.push(`${rid}: ${a.id} / ${b.id}`);
          }
        }
      }
      return bad;
    });
    assert(r.length === 0, `overlapping hangs: ${r.slice(0, 5).join('; ')}`);
    return 'ok';
  });

  test('look_prompt_keys_map_help', async (c) => {
    await c.load('test');
    const p = firstPanel(ROOM_IDS[0]);
    await c.ev(async (id) => { const D = window.museumDebug; D.enter({ pointerLock: false }); await D.navigate.goToWork(id); D.interactions.closePlacard(); D.step(1 / 60, 3); }, p.id);
    const hot = await c.ev(() => ({ hot: document.getElementById('crosshair').classList.contains('hot'), prompt: document.getElementById('look-prompt').textContent }));
    assert(hot.hot && hot.prompt.includes(p.title), `prompt: ${JSON.stringify(hot)}`);
    await c.page.keyboard.press('KeyE');
    assert(await c.ev(() => window.museumDebug.interactions.isOpen()), 'E opens the placard');
    await c.page.keyboard.press('Escape');
    assert(!(await c.ev(() => window.museumDebug.interactions.isOpen())), 'Esc closes the placard');
    await c.page.keyboard.press('KeyM');
    assert(await c.ev(() => window.museumDebug.hud.isMapOpen()), 'M opens the map');
    await c.shot('feature_map_room');
    await c.page.keyboard.press('KeyM');
    assert(!(await c.ev(() => window.museumDebug.hud.isMapOpen())), 'M closes the map');
    await c.page.keyboard.press('KeyH');
    assert(await c.ev(() => window.museumDebug.ui.isHelpOpen()), 'H opens help');
    await c.page.keyboard.press('Escape');
    return hot;
  });

  test('minimap_door_click', async (c) => {
    await c.load('test');
    const room = ROOM_IDS[0];
    await c.ev(async () => { await window.museumDebug.enterRoom('hub', { fade: false }); });
    await c.ev(B.settle);
    // enter first: the entry overlay sits above the map and would take the click (ten doors put the first one under its buttons)
    await c.ev(() => { const D = window.museumDebug; D.enter({ pointerLock: false }); D.step(1 / 60, 40); D.hud.openMap(); });
    const under = await c.ev(() => { const el = document.elementFromPoint(640, 360); return el ? `${el.tagName}#${el.id || (el.parentElement && el.parentElement.id)}` : null; });
    assert(/map-large/.test(under), `the large map should be on top at the screen centre, got ${under}`);
    await c.shot('feature_map_hub');
    const pt = await c.ev((rid) => {
      const D = window.museumDebug;
      const canvas = document.querySelector('#map-large canvas');
      const rect = canvas.getBoundingClientRect();
      // the centre of the door's hit area, not its first scanned edge point: the mouse lands on whole pixels
      const pts = [];
      for (let y = 0; y < rect.height; y += 3) for (let x = 0; x < rect.width; x += 3) {
        const h = D.hud.hitAtScreen(rect.left + x, rect.top + y);
        if (h && h.kind === 'door' && h.id === rid) pts.push([rect.left + x, rect.top + y]);
      }
      if (!pts.length) return null;
      return { x: Math.round(pts.reduce((a, p) => a + p[0], 0) / pts.length), y: Math.round(pts.reduce((a, p) => a + p[1], 0) / pts.length) };
    }, room);
    assert(pt, `the large map should have a clickable ${room} door`);
    await c.page.mouse.click(pt.x, pt.y);
    const s = await c.ev(async () => {
      const D = window.museumDebug;
      for (let i = 0; i < 100 && D.scenes.currentId() === 'hub'; i++) await new Promise((r) => setTimeout(r, 30));
      while (D.scenes.isSwitching()) await new Promise((r) => setTimeout(r, 30));
      await D.scenes.world().whenLoaded();
      D.step(1 / 60, 5);
      return { ...D.snapshot(), mapOpen: D.hud.isMapOpen() };
    });
    assert(s.scene === room, `clicking the door on the map enters the room: ${s.scene}`);
    assert(!s.mapOpen, 'the map closes after the click');
    return s.scene;
  });

  test('navigate_filter_goto', async (c) => {
    await c.load('test');
    const a = manifestOnDisk.artists[0];
    const word = a.name.split(/\s+/).find((w) => w.length > 3) || a.name;
    const r = await c.ev(async ({ word, id }) => {
      const D = window.museumDebug;
      D.navigate.open();
      const n = D.navigate.filter(word);
      const shown = [...document.querySelectorAll('#nav-panel .nav-artist')].filter((e) => !e.hidden).map((e) => e.textContent.trim().slice(0, 30));
      D.navigate.close();
      const ok = await D.navigate.goToWork(id);
      return { n, shown, ok, scene: D.scenes.currentId(), open: D.interactions.isOpen(), title: document.getElementById('placard-title').textContent };
    }, { word, id: a.works[a.works.length - 1].id });
    assert(r.n >= 1 && r.shown.some((t) => t.toLowerCase().includes(word.toLowerCase())), `filter: ${JSON.stringify(r)}`);
    assert(r.ok && r.scene === a.room && r.open, `go to: ${JSON.stringify(r)}`);
    return r;
  });
}

if (N_ROOMS >= 2) {
  test('placard_prev_next_crosses_rooms', async (c) => {
    await c.load('test');
    const r = await c.ev(async ([a, b]) => {
      const D = window.museumDebug;
      const inA = D.manifestIndex.flatWorks.filter((e) => e.room === a);
      const last = inA[inA.length - 1];
      await D.navigate.goToWork(last.work.id);
      document.getElementById('placard-next').click();
      await new Promise((res) => setTimeout(res, 50));
      while (D.scenes.isSwitching()) await new Promise((res) => setTimeout(res, 30));
      await D.scenes.world().whenLoaded();
      const after = D.interactions.current();
      return { from: last.work.id, to: after ? after.work.id : null, scene: D.scenes.currentId(), room: after ? after.room : null };
    }, ROOM_IDS.slice(0, 2));
    assert(r.scene === ROOM_IDS[1] && r.room === ROOM_IDS[1] && r.to, `next passage from the last of ${ROOM_IDS[0]} enters ${ROOM_IDS[1]}: ${JSON.stringify(r)}`);
    return r;
  });

  test('guide_trail_to_another_room', async (c) => {
    await c.load('test');
    const r = await c.ev(async ([a, b]) => {
      const D = window.museumDebug;
      await D.enterRoom(a, { fade: false });
      await D.scenes.world().whenLoaded();
      D.waypointTrail.showPathTo(a, b, D.camera.position);
      const mesh = D.scene.getObjectByName('trail');
      const pos = mesh.geometry.attributes.position;
      let ex = 0, ez = 0;
      for (let i = pos.count - 8; i < pos.count; i++) { ex += pos.getX(i) / 8; ez += pos.getZ(i) / 8; }
      const door = D.lists.doors.find((m) => m.name === 'DOOR-hub' || m.name === `DOOR-${b}`).userData.center;
      const segs = D.waypointTrail.segmentsTo(a, b, D.camera.position);
      const before = { has: D.waypointTrail.hasTrail(), endDist: Math.hypot(ex - door.x, ez - door.z), segs: segs.map((s) => [s.scene, s.exitDoor]) };
      await D.enterRoom(segs.length > 1 ? segs[1].scene : b, { via: a });
      await D.scenes.world().whenLoaded();
      const midHas = D.waypointTrail.hasTrail();
      if (D.scenes.currentId() !== b) await D.enterRoom(b, { via: D.scenes.currentId() });
      return { before, midHas, arrivedHas: D.waypointTrail.hasTrail(), target: D.waypointTrail.target() };
    }, ROOM_IDS.slice(0, 2));
    assert(r.before.has && r.before.segs.length >= 2, `route segments: ${JSON.stringify(r.before)}`);
    assert(!r.arrivedHas && !r.target, `the trail clears on arrival: ${JSON.stringify(r)}`);
    return r;
  });

  test('tour_crosses_door', async (c) => {
    await c.load('test');
    const r = await c.ev(async ([a, b]) => {
      const D = window.museumDebug;
      await D.enterRoom(a, { fade: false });
      await D.scenes.world().whenLoaded();
      const works = D.manifestIndex.flatWorks.filter((w) => w.room === a).slice(-2).concat(D.manifestIndex.flatWorks.filter((w) => w.room === b).slice(0, 1));
      D.tour.start({ works, dwell: 0.3 });
      let guard = 0, crossed = false, outside = 0, placards = 0;
      while (D.tour.active() && guard++ < 4000) {
        D.step(1 / 60, 10);
        if (D.scenes.isSwitching() || D.tour.state().phase === 'switching') { await new Promise((res) => setTimeout(res, 30)); continue; }
        if (!D.roomAt(D.camera.position)) outside++;
        if (D.scenes.currentId() === b) crossed = true;
        if (D.tour.state().phase === 'dwell' && D.interactions.isOpen()) placards++;
      }
      return { crossed, outside, placards, final: D.scenes.currentId(), collision: D.controls.getCollision() };
    }, ROOM_IDS.slice(0, 2));
    assert(r.crossed && r.final === ROOM_IDS[1], `the tour walked through the door: ${JSON.stringify(r)}`);
    assert(r.outside === 0, `${r.outside} tour samples were outside a room`);
    assert(r.placards > 0 && r.collision, `placards opened and collision restored: ${JSON.stringify(r)}`);
    return r;
  });
}

// ---- 4. deep links, persistence, touch, gamepad ------------------------------------------------
if (N_ROOMS) {
  test('deep_link_room', async (c) => {
    const room = ROOM_IDS[N_ROOMS - 1];
    await c.load(`test&room=${room}`, { fresh: true });
    const n = await c.ev(B.counts);
    const blocker = await c.ev(() => document.getElementById('blocker').classList.contains('hidden'));
    assert(n.scene === room && n.art === worksInRoom(manifestOnDisk, room) && blocker, `?room=: ${JSON.stringify(n)}`);
    return n;
  });

  test('deep_link_work', async (c) => {
    const p = firstPanel(ROOM_IDS[0]);
    await c.load(`test&work=${p.id}`, { fresh: true });
    const r = await c.ev(() => ({ scene: window.museumDebug.scenes.currentId(), open: window.museumDebug.interactions.isOpen(), title: document.getElementById('placard-title').textContent, probe: window.museumDebug.probeArt() }));
    assert(r.scene === ROOM_IDS[0] && r.open && r.title === p.title, `?work=: ${JSON.stringify(r)}`);
    assert(r.probe && r.probe.endsWith(`__${p.id}`), `standing in front of the panel: ${r.probe}`);
    await c.shot('feature_deep_link_work');
    return r;
  });

  test('persist_resume', async (c) => {
    await c.load('test', { fresh: true });
    const room = ROOM_IDS[0];
    const saved = await c.ev(async (rid) => {
      const D = window.museumDebug;
      await D.enterRoom(rid, { fade: false });
      D.controls.teleport(new D.THREE.Vector3(1, 1.7, -4), { yaw: 0.7, pitch: 0 });
      D.step(1 / 60, 2);
      return { ok: D.persist.save(), read: D.persist.read() };
    }, room);
    assert(saved.ok && saved.read.scene === room, `saved: ${JSON.stringify(saved)}`);
    await c.load('test&resume=1', { fresh: true });
    const s = await c.snap();
    assert(s.scene === room && near(s.pos[0], 1, 0.05) && near(s.pos[2], -4, 0.05) && near(s.yaw, 0.7, 0.01), `resumed where we stood: ${JSON.stringify(s)}`);
    return s;
  });

  test('touch_tap_reads', async (c) => {
    await c.load('test');
    const p = firstPanel(ROOM_IDS[0]);
    const r = await c.ev(async (id) => {
      const D = window.museumDebug;
      await D.navigate.goToWork(id);
      D.interactions.closePlacard();
      D.step(1 / 60, 2);
      const res = D.interactions.openAtScreen(0, 0);
      return { res: res ? res.work ? res.work.id : res : null, open: D.interactions.isOpen() };
    }, p.id);
    assert(r.open && r.res === p.id, `tap at the screen centre reads the panel: ${JSON.stringify(r)}`);
    return r;
  });

  test('gamepad_walk_look_buttons', async (c) => {
    await c.load('test');
    const p = firstPanel(ROOM_IDS[0]);
    const r = await c.ev(async (id) => {
      const D = window.museumDebug;
      D.enter({ pointerLock: false });
      await D.navigate.goToWork(id);
      D.interactions.closePlacard();
      D.step(1 / 60, 2);
      const pad = { mapping: 'standard', connected: true, axes: [0, 0, 0, 0], buttons: Array.from({ length: 16 }, () => ({ pressed: false, value: 0 })) };
      D.gamepad.setSource(() => pad);
      const press = (i) => { pad.buttons[i].pressed = true; D.step(1 / 60, 1); pad.buttons[i].pressed = false; D.step(1 / 60, 1); };
      const out = {};
      const s0 = D.snapshot();
      pad.axes = [0, -1, 0, 0];
      const s1 = D.step(1 / 60, 30);
      out.walked = Math.hypot(s1.pos[0] - s0.pos[0], s1.pos[2] - s0.pos[2]);
      pad.axes = [0, 0, 0, 0];
      const s2 = D.step(1 / 60, 10);
      pad.axes = [0, 0, 1, 0];
      const s3 = D.step(1 / 60, 30);
      out.turned = s2.yaw - s3.yaw;
      pad.axes = [0, 0, 0, 0];
      out.connected = D.gamepad.connected();
      await D.navigate.goToWork(id);
      D.interactions.closePlacard();
      D.step(1 / 60, 3);
      press(0); out.aOpens = D.interactions.isOpen();
      press(1); out.bCloses = !D.interactions.isOpen();
      press(2); out.xMap = D.hud.isMapOpen();
      press(1); out.bClosesMap = !D.hud.isMapOpen();
      D.gamepad.setSource(null);
      return out;
    }, p.id);
    assert(r.walked > 0.5 && r.walked < 2.5, `left stick walks: ${r.walked.toFixed(2)} m`);
    assert(r.turned > 0, `right stick turns right: ${r.turned.toFixed(3)}`);
    for (const k of ['connected', 'aOpens', 'bCloses', 'xMap', 'bClosesMap']) assert(r[k], `${k}: ${JSON.stringify(r)}`);
    return r;
  });
}

// ---- 5. look, fixtures, budgets --------------------------------------------------------------
test('textures_pbr_world_uv', async (c) => {
  await c.load('test');
  const r = await c.ev(async () => {
    const D = window.museumDebug;
    await D.enterRoom('hub', { fade: false });
    const floor = D.scene.getObjectByName('GEO-hub_floor');
    const m = floor.material;
    const uv = floor.geometry.attributes.uv;
    let lo = Infinity, hi = -Infinity;
    for (let i = 0; i < uv.count; i++) { lo = Math.min(lo, uv.getX(i)); hi = Math.max(hi, uv.getX(i)); }
    return { map: !!m.map, normal: !!m.normalMap, rough: !!m.roughnessMap, pbr: !!m.userData.pbr, span: hi - lo, slot: m.userData.slot };
  });
  assert(r.map && r.normal && r.rough && r.pbr, `hall floor material: ${JSON.stringify(r)}`);
  assert(r.span > 5, `world-space tiling along the hall: uv span ${r.span}`);
  return r;
});

if (N_ROOMS) {
  test('fixtures_drive_the_light_pool', async (c) => {
    await c.load('test');
    const r = await c.ev(async (rid) => {
      const D = window.museumDebug;
      await D.enterRoom(rid, { fade: false });
      await D.scenes.world().whenLoaded();
      D.step(1 / 60, 20);
      D.lights.update(D.camera, 0, true);
      return D.lights.state();
    }, ROOM_IDS[0]);
    assert(r.mode === 'fx' && r.sun.mode === 'laylight' && r.chandelier && /chandelier/.test(r.chandelier), `light pool: ${JSON.stringify(r)}`);
    assert(r.pool.filter(Boolean).length >= 2, `pool lights parked on fixtures: ${JSON.stringify(r.pool)}`);
    return r;
  });
}

test('doors_themed_with_plaques', async (c) => {
  await c.load('test');
  const r = await c.ev(async () => {
    const D = window.museumDebug;
    await D.enterRoom('hub', { fade: false });
    const out = [];
    for (const d of D.lists.doors) {
      const plaque = D.scene.getObjectByName(`GEO-hub_plaque_${d.userData.target}`);
      out.push({ door: d.name, theme: d.userData.theme, plaque: !!(plaque && plaque.material.map && plaque.material.map.isCanvasTexture), leaf: d.material.name });
    }
    return out;
  });
  const missing = r.filter((x) => !x.plaque || !x.theme);
  assert(missing.length === 0, `doors without a theme/plaque: ${JSON.stringify(missing)}`);
  for (const room of ROOM_IDS) {
    const want = layoutOnDisk.scenes[room].style.theme;
    const got = r.find((x) => x.door === `DOOR-${room}`);
    assert(got && got.theme === want, `${room}: door theme ${got && got.theme} vs the scene's ${want}`);
  }
  return [...new Set(r.map((x) => x.theme))];
});

test('room_budget', async (c) => {
  await c.load('test');
  const r = await c.ev(async (ids) => {
    const D = window.museumDebug;
    const out = {};
    for (const id of ids) {
      await D.enterRoom(id, { fade: false });
      await D.scenes.world().whenLoaded();
      await D.setView(id === 'hub' ? 'hub_west' : `${id}_door`);
      D.renderOnce();
      out[id] = { calls: D.renderer.info.render.calls, tris: D.renderer.info.render.triangles, geometries: D.renderer.info.memory.geometries, textures: D.renderer.info.memory.textures };
    }
    return out;
  }, ['hub', ...ROOM_IDS]);
  for (const [id, v] of Object.entries(r)) assert(v.calls <= 450 && v.tris <= 2_000_000, `${id} over budget: ${JSON.stringify(v)}`);
  return r;
});

if (N_ROOMS) {
  test('memory_returns_after_switches', async (c) => {
    await c.load('test');
    const r = await c.ev(async (rid) => {
      const D = window.museumDebug;
      const go = async (id) => { await D.enterRoom(id, { fade: false }); await D.scenes.world().whenLoaded(); D.renderOnce(); return { ...D.renderer.info.memory }; };
      const base = await go('hub');
      const seq = [];
      for (let i = 0; i < 3; i++) { await go(rid); seq.push(await go('hub')); }
      return { base, seq };
    }, ROOM_IDS[0]);
    const last = r.seq[r.seq.length - 1];
    assert(last.textures <= r.base.textures + 8 && last.geometries <= r.base.geometries + 8, `GPU memory should return to the hall baseline: ${JSON.stringify(r)}`);
    return r;
  });
}

test('framing_views', async (c) => {
  await c.load('test');
  // every room's three fixed views (door, corner, west), as the layout declares them, so all three reach the contact sheet
  const views = ['hub_west', 'hub_rotunda', 'hub_bays', 'hub_east', ...ROOM_IDS.flatMap((r) => [`${r}_door`, `${r}_corner`, `${r}_west`])];
  for (const v of views) {
    const ok = await c.ev(async (name) => { const D = window.museumDebug; const r = await D.setView(name); await D.scenes.world().whenLoaded(); D.renderOnce(); return r; }, v);
    assert(ok, `unknown view ${v}`);
    await c.shot(`view_${v}`);
  }
  return 'ok';
});

test('classic_mode_loads', async (c) => {
  await c.load('test&classic', { fresh: true });
  const n = await c.ev(B.counts);
  assert(n.pipeline === 'classic' && n.scene === 'hub' && n.doors === N_ROOMS, `classic mode: ${JSON.stringify(n)}`);
  if (N_ROOMS) {
    await c.ev(async (rid) => { await window.museumDebug.enterRoom(rid, { fade: false }); await window.museumDebug.scenes.world().whenLoaded(); window.museumDebug.renderOnce(); }, ROOM_IDS[0]);
    await c.shot('view_classic_room');
  }
  return n;
});

test('no_console_errors', async (c) => {
  await c.load('test');
  assert(c.errors.length === 0, `console errors on the last page: ${c.errors.join(' | ')}`);
  return 'ok';
});

// ---- runner --------------------------------------------------------------------------------
async function main() {
  if (opt.list) { for (const t of tests) console.log(t.name); return 0; }
  fs.mkdirSync(opt.out, { recursive: true });
  const { server, port } = await startServer();
  const base = `http://127.0.0.1:${port}`;
  const browser = await chromium.launch({
    executablePath: opt.chromium,
    headless: !opt.headed,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--no-sandbox'],
  });
  const ctx = new Ctx(browser, base);
  const report = { started: new Date().toISOString(), base, rooms: ROOM_IDS, results: [] };
  const greps = opt.grep ? opt.grep.split(',').map((g) => g.trim()).filter(Boolean) : [];
  const selected = tests.filter((t) => !greps.length || greps.some((g) => t.name.includes(g)));
  let failed = 0;
  for (const t of selected) {
    const t0 = Date.now();
    try {
      const value = await t.fn(ctx);
      report.results.push({ name: t.name, ok: true, ms: Date.now() - t0, value });
      console.log(`  ok    ${t.name}  (${((Date.now() - t0) / 1000).toFixed(1)} s)`);
    } catch (e) {
      failed++;
      report.results.push({ name: t.name, ok: false, ms: Date.now() - t0, error: String(e && e.message || e) });
      console.log(`  FAIL  ${t.name}  (${((Date.now() - t0) / 1000).toFixed(1)} s)\n        ${String(e && e.message || e).replace(/\n/g, '\n        ')}`);
      if (opt.shots && ctx.page) { try { await ctx.shot(`fail_${t.name}`); } catch (e2) { /* ignore */ } }
    }
  }
  if (opt.shots && shots.length) {
    const rel = (f) => path.basename(f);
    const html = `<!doctype html><meta charset="utf-8"><body style="margin:0;background:#111;font:12px sans-serif;color:#ddd">
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px;padding:6px;width:1280px">
${shots.map((f) => `<figure style="margin:0"><img src="${rel(f)}" style="width:100%;display:block"><figcaption style="padding:2px 4px">${rel(f)}</figcaption></figure>`).join('\n')}
</div></body>`;
    fs.writeFileSync(path.join(opt.out, 'sheet.html'), html);
    const page = await browser.newPage({ viewport: { width: 1292, height: 800 } });
    await page.goto(`file://${path.join(opt.out, 'sheet.html')}`);
    await page.screenshot({ path: path.join(opt.out, 'contact_sheet.png'), fullPage: true });
    await page.close();
  }
  report.finished = new Date().toISOString();
  report.failed = failed;
  report.consoleErrors = ctx.errors;
  fs.writeFileSync(path.join(opt.out, 'report.json'), JSON.stringify(report, null, 2));
  await browser.close();
  server.close();
  console.log(`\n${selected.length - failed}/${selected.length} passed${failed ? `, ${failed} FAILED` : ''}. Report: ${path.join(opt.out, 'report.json')}`);
  return failed ? 1 : 0;
}

main().then((code) => process.exit(code)).catch((e) => { console.error(e); process.exit(2); });
