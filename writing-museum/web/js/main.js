import * as THREE from 'three';
import { threeToBlender } from './coords.js';
import { createControls } from './controls.js';
import { createInteractions } from './interactions.js';
import { createWaypointTrail } from './waypoints.js';
import { readRenderOptions, configureRenderer, setupEnvironment, createPipeline } from './render.js';
import { createLightRig } from './lights.js';
import { createDebug } from './debug.js';
import { createHud } from './hud.js';
import { createNavigate } from './navigate.js';
import { createTour } from './tour.js';
import { createUI } from './ui.js';
import { createTouchControls } from './touch.js';
import { createGamepadControls } from './gamepad.js';
import { createPersist } from './persist.js';
import { createMaterialLibrary } from './matlib.js';
import { createModels } from './models.js';
import { createTitleCard } from './titlecard.js';
import { createScenes } from './scenes.js';

const MANIFEST_URL = '../data/museum-manifest.json';
const RENDER_OPTS = readRenderOptions(window.location.search); // ?classic ?exposure= ?debug ?view= ?test ?room= ?work= ?wing=0 ...

const loadingEl = document.getElementById('loading');
const blockerEl = document.getElementById('blocker');
const roomLabelEl = document.getElementById('room-label');

export function buildManifestIndex(manifest) {
  const wings = manifest.wings && manifest.wings.length
    ? manifest.wings
    : [{ id: 'art-talk', name: 'Art-Talk Wing', image_base: 'Art-Talk-main/', rooms: manifest.rooms.map((r) => r.id) }];
  const wingsById = new Map(wings.map((w) => [w.id, w]));
  const byMeshName = new Map();
  const byWorkId = new Map();
  const flatWorks = [];
  for (const artist of manifest.artists) {
    for (const work of artist.works) {
      const meshName = `ART-${artist.slug}__${work.id}`;
      const entry = { artist, work, room: artist.room, wing: artist.wing || wings[0].id, meshName, index: flatWorks.length };
      byMeshName.set(meshName, entry);
      byWorkId.set(work.id, entry);
      flatWorks.push(entry);
    }
  }

  function suggestNext(entry) {
    const idx = flatWorks.indexOf(entry);
    if (idx === -1) return [];
    const suggestions = [];
    const next = flatWorks[(idx + 1) % flatWorks.length];
    suggestions.push(next);
    if (next.room === entry.room) {
      let j = idx + 1;
      while (j < flatWorks.length && flatWorks[j].room === entry.room) j++;
      if (j < flatWorks.length) suggestions.push(flatWorks[j]);
      else if (flatWorks.length) suggestions.push(flatWorks[0]);
    }
    return suggestions;
  }

  return { wings, wingsById, byMeshName, byWorkId, flatWorks, suggestNext };
}

// ?wing=0: leave the People wing out (its rooms, doors, artists and menu entries).
function dropWing(manifest, wingId) {
  const wing = (manifest.wings || []).find((w) => w.id === wingId);
  if (!wing) return manifest;
  const gone = new Set(wing.rooms || []);
  manifest.wings = manifest.wings.filter((w) => w.id !== wingId);
  manifest.artists = manifest.artists.filter((a) => (a.wing || 'art-talk') !== wingId);
  manifest.rooms = manifest.rooms.filter((r) => !gone.has(r.id));
  for (const r of manifest.rooms) {
    r.connects_to = (r.connects_to || []).filter((id) => !gone.has(id));
    for (const id of Object.keys(r.doors || {})) if (gone.has(id)) delete r.doors[id];
  }
  return manifest;
}

async function main() {
  const manifest = await fetch(MANIFEST_URL).then((r) => r.json());
  if (!RENDER_OPTS.wing) dropWing(manifest, 'people');
  const manifestIndex = buildManifestIndex(manifest);
  const roomsById = new Map(manifest.rooms.map((r) => [r.id, r]));

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0806);

  const camera = new THREE.PerspectiveCamera(70, window.innerWidth / window.innerHeight, 0.05, 500);
  camera.position.set(0, 1.7, 3);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  document.body.appendChild(renderer.domElement);
  // v2 look: AgX + soft shadows + PMREM environment + composer (MSAA HalfFloat, bloom, OutputPass).
  // ?classic keeps the v1 look (plain renderer.render, hemisphere light only).
  configureRenderer(renderer, RENDER_OPTS);
  const pipeline = createPipeline(renderer, scene, camera, RENDER_OPTS);
  const envInfo = await setupEnvironment(renderer, scene, RENDER_OPTS);

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // DPR changes (monitor switch, zoom)
    renderer.setSize(window.innerWidth, window.innerHeight);
    pipeline.setSize(window.innerWidth, window.innerHeight);
  });

  const hemi = new THREE.HemisphereLight(0x9a9488, 0x2a231a, 0.6);
  if (RENDER_OPTS.classic) scene.add(hemi); // otherwise lights.js owns the fill light

  // The shared mesh lists: refilled in place by the scene manager on every switch.
  const lists = { walls: [], floors: [], art: [], doors: [], pickables: [] };
  const wallMeshes = lists.walls, floorMeshes = lists.floors, artMeshes = lists.art;

  const matlib = createMaterialLibrary(renderer);
  const models = createModels(renderer);
  const lights = RENDER_OPTS.classic ? null : createLightRig(scene, renderer, { lightGain: RENDER_OPTS.lightGain });
  const titlecard = createTitleCard();

  const controls = createControls(camera, renderer.domElement, () => ({ walls: lists.walls, floors: lists.floors }));

  let scenes = null; // created below (needs hud/interactions); referenced through closures
  const currentScene = () => (scenes ? scenes.currentId() : null);
  const waypointTrail = createWaypointTrail(scene, manifest, camera, { currentScene });

  function getCurrentRoomId() {
    // The geo room under the camera when it is a manifest room, else the scene itself (every
    // scene is a manifest room: the hub or one gallery).
    const r = scenes ? scenes.roomAt(camera.position) : null;
    if (r && roomsById.has(r.manifestId)) return r.manifestId;
    return currentScene() || manifest.rooms[0].id;
  }

  const interactions = createInteractions(camera, manifestIndex, waypointTrail, controls.isLocked, getCurrentRoomId, {
    domElement: renderer.domElement,
    walls: () => lists.walls,
    groundY: controls.groundY,
  });

  function enter({ pointerLock = true } = {}) {
    blockerEl.classList.add('hidden');
    controls.engage({ pointerLock });
  }
  blockerEl.addEventListener('click', (e) => {
    if (e.target.closest('button, a')) return;
    enter();
  });
  const exploreBtn = document.getElementById('btn-explore');
  if (exploreBtn) exploreBtn.addEventListener('click', () => enter());

  const hud = createHud({
    camera, rooms: new Map(), roomsById, manifest, artMeshes: lists.art, controls, lights,
    onDoor: (id) => scenes && scenes.enter(id, { via: currentScene() }),
  });
  const persist = createPersist({ camera, controls, enabled: !RENDER_OPTS.test, scenes: null });
  scenes = createScenes({
    scene, renderer, camera, controls, manifest, manifestIndex, roomsById, lights, hud, interactions, waypointTrail,
    matlib, models, titlecard, persist, opts: RENDER_OPTS, lists,
  });
  persist.setScenes && persist.setScenes(scenes);
  interactions.onDoor((leaf) => scenes.enter(leaf.userData.target, { via: currentScene() }));

  const debug = createDebug({
    renderer, scene, camera, pipeline, lights, controls, manifest,
    roomAt: (p) => scenes.roomAt(p),
    scenes,
    opts: RENDER_OPTS,
    info: { model: 'layout', ...envInfo },
  });

  const navigate = createNavigate({
    manifest, manifestIndex, camera, controls, interactions, waypointTrail, getCurrentRoomId,
    teleportToRoom: (id) => scenes.teleportToRoom(id), lights, fade: hud.fade, scenes,
  });
  const tour = createTour({ manifestIndex, roomsById, camera, controls, interactions, getCurrentRoomId, scenes, waypointTrail, roomAt: (p) => scenes.roomAt(p), opts: { dwell: RENDER_OPTS.tourDwell } });
  const ui = createUI({ manifest, manifestIndex, controls, interactions, hud, navigate, tour, persist, enter });
  const touch = createTouchControls({ domElement: renderer.domElement, controls, interactions });
  const gamepad = createGamepadControls({ controls, interactions, hud, navigate, tour, ui, enter, blockerEl });

  // ---- simulation / rendering -------------------------------------------------------------
  let lastRoomId = null;
  let roomLabelTimer = 0;

  function simulate(delta) {
    gamepad.update(delta); // before the move step so this frame's stick drives this frame's walk
    if (tour.active()) tour.update(delta);
    else if (controls.isLocked()) controls.update(delta);
    camera.updateMatrixWorld(); // raycasts below (look prompt, picks, tests) see this frame's pose, not the last rendered one
    waypointTrail.update(delta);
    interactions.update(delta);
    hud.update(delta);
    persist.tick(delta);
    ui.update(delta);
    scenes.update(delta);

    const currentRoomId = getCurrentRoomId();
    if (currentRoomId !== lastRoomId) {
      lastRoomId = currentRoomId;
      const room = roomsById.get(currentRoomId);
      roomLabelEl.textContent = room ? room.name : '';
      roomLabelEl.classList.add('visible');
      roomLabelTimer = 2.5;
    }
    if (roomLabelTimer > 0) {
      roomLabelTimer -= delta;
      if (roomLabelTimer <= 0) roomLabelEl.classList.remove('visible');
    }
    if (lights) lights.update(camera, delta);
  }

  function frame(delta) {
    simulate(delta);
    pipeline.render(delta);
    debug.update(delta);
  }

  function renderOnce() {
    if (lights) lights.update(camera, 0, true);
    pipeline.render(0);
    hud.draw();
    debug.update(0);
  }
  debug.setRenderOnce(renderOnce);

  function snapshot() {
    const p = camera.position;
    const look = controls.getLook();
    const geo = scenes.roomAt(camera.position);
    return {
      pos: [p.x, p.y, p.z], blender: threeToBlender(p), yaw: look.yaw, pitch: look.pitch,
      room: getCurrentRoomId(), geoRoom: geo ? geo.id : null, scene: currentScene(),
    };
  }
  function step(dt = 1 / 60, n = 1) {
    for (let i = 0; i < n; i++) simulate(dt);
    return snapshot();
  }
  function probeArt() {
    const hit = interactions.pick();
    return hit ? hit.name : null;
  }

  let autoLoop = !RENDER_OPTS.test;
  const clock = new THREE.Clock();
  function animate() {
    if (!autoLoop) return;
    requestAnimationFrame(animate);
    frame(Math.min(clock.getDelta(), 0.1));
  }
  function setAutoLoop(on) {
    const was = autoLoop;
    autoLoop = !!on;
    if (autoLoop && !was) { clock.getDelta(); animate(); }
  }

  window.museumDebug = {
    THREE, camera, scene, wallMeshes, floorMeshes, artMeshes, lists, manifest, manifestIndex, roomsById,
    get rooms() { return scenes.geoRooms(); }, roomAt: (p) => scenes.roomAt(p),
    controls, renderer, pipeline, lights, renderOnce, renderOptions: RENDER_OPTS,
    interactions, waypointTrail, hud, navigate, tour, persist, ui, touch, gamepad, scenes, models, matlib, titlecard,
    enterRoom: (id, opts) => scenes.enter(id, opts), get layout() { return scenes.layout; },
    simulate, frame, step, snapshot, probeArt, setAutoLoop, getCurrentRoomId, enter,
    setView: (name) => debug.setView(name).then((ok) => { renderOnce(); return ok; }),
    measure: debug.measure, probe: debug.probe, tune: debug.tune,
    ready: false,
  };

  // ---- start: pick the first scene, then honour the deep links --------------------------
  await scenes.layoutReady;
  const workEntry = RENDER_OPTS.work ? manifestIndex.byWorkId.get(RENDER_OPTS.work) : null;
  const saved = RENDER_OPTS.resume ? persist.read() : null;
  let startScene = 'hub';
  if (RENDER_OPTS.room && scenes.sceneRecord(RENDER_OPTS.room)) startScene = RENDER_OPTS.room;
  else if (workEntry && scenes.sceneRecord(workEntry.room)) startScene = workEntry.room;
  else if (saved && saved.scene && scenes.sceneRecord(saved.scene)) startScene = saved.scene;
  await scenes.enter(startScene, { fade: false });
  await interactions.rewritesReady; // the placard overlay is small and local; ready means fully loaded
  loadingEl.classList.add('hidden');
  if (workEntry) { await navigate.goToWork(RENDER_OPTS.work); enter({ pointerLock: false }); }
  else if (RENDER_OPTS.room && startScene === RENDER_OPTS.room) enter({ pointerLock: false });
  else if (saved) { await persist.restore(saved); enter({ pointerLock: false }); }
  window.museumDebug.ready = true;
  if (autoLoop) animate();
  else renderOnce();
  if (RENDER_OPTS.view) window.museumDebug.setView(RENDER_OPTS.view);
}

main().catch((err) => {
  console.error(err);
  loadingEl.textContent = 'Failed to load the museum: ' + err.message;
});
