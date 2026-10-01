// Scene manager: one scene (the hub or a gallery room) is resident at a time. The THREE.Scene,
// renderer, composer and the 8-light pool persist; a world root Group is swapped in and out.
// On every switch the shared mesh lists (walls/floors/art/doors/pickables), the geo rooms,
// the light anchors, the HUD and the interactions are rebuilt from the new root.
import * as THREE from 'three';
import { blenderToThree, yawFromHeadingDeg } from './coords.js';
import { buildScene } from './procroom.js';
import { collectRooms, makeRoomAt } from './lights.js';
import { patchMaterials } from './materials.js';
import { applyFraming } from './debug.js';

export const LAYOUT_URL = '../data/museum-layout.json';

export function classifyRoot(root, lists) {
  const { walls, floors, art, doors, pickables } = lists;
  walls.length = 0; floors.length = 0; art.length = 0; doors.length = 0; pickables.length = 0;
  root.traverse((obj) => {
    if (!obj.isMesh) return;
    const name = obj.name || '';
    if (name.startsWith('SCULPT-')) { pickables.push(obj); return; }
    if (!obj.visible && !name.includes('wall')) return;
    if (name.startsWith('ART-')) art.push(obj);
    else if (name.startsWith('DOOR-')) { doors.push(obj); pickables.push(obj); walls.push(obj); }
    else if (name.includes('wall') || name.includes('outer')) walls.push(obj);
    else if (name.includes('floor') || name.includes('landing') || name.includes('step')) floors.push(obj);
  });
  return lists;
}

export function createScenes({ scene, renderer, camera, controls, manifest, manifestIndex, roomsById, lights, hud, interactions,
  waypointTrail, matlib, models, titlecard, persist = null, opts = {}, lists }) {
  let layout = null;
  let current = null;        // { id, world, geoRooms, roomAt }
  let switching = null;      // promise while a switch is in flight
  const listeners = [];
  const layoutReady = fetch(LAYOUT_URL).then((r) => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); }).then((j) => { layout = j; return j; });

  function sceneRecord(id) {
    if (!layout) return null;
    return layout.scenes[id] || null;
  }
  function currentId() { return current ? current.id : null; }
  function world() { return current ? current.world : null; }
  function geoRooms() { return current ? current.geoRooms : new Map(); }
  function roomAt(pos, eye) { return current ? current.roomAt(pos, eye) : null; }
  function onSwitch(fn) { listeners.push(fn); }

  function doorSpawn(worldRec, via) {
    // arriving from `via`: stand just inside the door that leads back there
    const d = (worldRec.doors || []).find((x) => x.target === via) || null;
    return d ? d.spawn : worldRec.spawn;
  }

  async function enter(id, { via = null, fade = true, spawn = null } = {}) {
    await layoutReady;
    if (switching) await switching;
    if (!sceneRecord(id)) { console.warn('[museum] unknown scene', id); return null; }
    if (current && current.id === id && !spawn) return current.world;
    const run = (async () => {
      if (fade && hud) hud.fade();
      const rec = sceneRecord(id);
      const old = current;
      const w = buildScene(rec, { matlib, manifestIndex, renderer, models, roomsById });
      if (old) {
        scene.remove(old.world.root);
        old.world.dispose();
        if (waypointTrail) waypointTrail.clear({ keepTarget: true });
        if (interactions) interactions.closePlacard({ keepTrail: true });
      }
      scene.add(w.root);
      w.root.updateMatrixWorld(true);
      patchMaterials(w.root, renderer, { envIntensity: opts.envIntensity });
      classifyRoot(w.root, lists);
      const rooms = collectRooms(w.root);
      const at = makeRoomAt(rooms);
      current = { id, world: w, geoRooms: rooms, roomAt: at };
      if (lights) lights.setWorld({ root: w.root, rooms });
      if (hud) hud.setScene({ rooms, doors: w.doors, artMeshes: lists.art, sceneId: id, rec });
      if (interactions) { interactions.setArtMeshes(lists.art); interactions.setPickables(lists.pickables); }
      const sp = spawn || doorSpawn(rec, via) || rec.spawn;
      const pos = blenderToThree(sp);
      pos.y += controls.EYE_HEIGHT;
      controls.teleport(pos, { yaw: yawFromHeadingDeg(sp[3] || 0), pitch: 0 });
      camera.updateMatrixWorld();
      if (lights) lights.update(camera, 0, true);
      renderer.shadowMap.needsUpdate = true;
      if (titlecard && rec.intro) titlecard.show(rec.intro);
      if (waypointTrail) waypointTrail.refresh();
      for (const fn of listeners) { try { fn(id, w, old ? old.id : null); } catch (e) { console.warn(e); } }
      if (persist) persist.save();
      w.loadTextures();
      // models (sculptures, their proxies and colliders, chandeliers) arrive asynchronously: re-classify then
      w.whenLoaded().then(() => {
        if (!current || current.world !== w) return;
        classifyRoot(w.root, lists);
        if (interactions) { interactions.setArtMeshes(lists.art); interactions.setPickables(lists.pickables); }
        renderer.shadowMap.needsUpdate = true;
      }).catch(() => {});
      return w;
    })();
    switching = run.finally(() => { switching = null; });
    return switching;
  }

  // In-scene teleport to a room's spawn, switching scenes first when needed.
  async function teleportToRoom(id) {
    if (!roomsById.has(id) && !sceneRecord(id)) return false;
    if (currentId() !== id) {
      const w = await enter(id, { via: null });
      return !!w;
    }
    return hud ? hud.teleportToRoom(id) : false;
  }

  function applyView(name) {
    if (!layout) return false;
    for (const [sid, rec] of Object.entries(layout.scenes)) {
      const v = rec.views && rec.views[name];
      if (!v) continue;
      const go = async () => {
        if (currentId() !== sid) await enter(sid, { fade: false });
        applyFraming(camera, v);
        controls.syncLook();
        if (lights) lights.update(camera, 0, true);
      };
      return go();
    }
    return false;
  }
  function views() {
    const out = [];
    if (!layout) return out;
    for (const rec of Object.values(layout.scenes)) for (const k of Object.keys(rec.views || {})) out.push(k);
    return out;
  }

  function update(dt) {
    if (titlecard) titlecard.update(dt);
  }

  function state() {
    const w = world();
    return { scene: currentId(), switching: !!switching, art: lists.art.length, walls: lists.walls.length, doors: lists.doors.length,
      textures: w ? w.textureStats : null, models: models ? models.state() : null };
  }

  return { enter, currentId, current: () => current, world, geoRooms, roomAt, teleportToRoom, applyView, views, update, state, onSwitch,
    layoutReady, get layout() { return layout; }, isSwitching: () => !!switching, sceneRecord, lists };
}
