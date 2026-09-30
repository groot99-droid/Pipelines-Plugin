// Remembers where the visitor stood (localStorage) so "Resume last visit" and ?resume=1
// can put them back. Storage access is wrapped: private windows and file:// pages may throw.
import * as THREE from 'three';

const KEY = 'writing-museum.pos.v1';

export function createPersist({ camera, controls, enabled = true, scenes: scenesIn = null }) {
  let scenes = scenesIn;
  let acc = 0;
  let last = null;
  function setScenes(s) { scenes = s; }

  function read() {
    try {
      const j = localStorage.getItem(KEY);
      const s = j ? JSON.parse(j) : null;
      return s && Array.isArray(s.p) && s.p.length === 3 ? s : null;
    } catch (e) { return null; }
  }
  function save() {
    try {
      const { yaw, pitch } = controls.getLook();
      const p = camera.position;
      last = [p.x, p.y, p.z];
      const sceneId = scenes ? scenes.currentId() : null;
      if (scenes && !sceneId) return false;
      localStorage.setItem(KEY, JSON.stringify({ p: last, yaw, pitch, scene: sceneId, t: Date.now() }));
      return true;
    } catch (e) { return false; }
  }
  function clear() {
    try { localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
  }
  function hasSave() { return read() !== null; }
  async function restore(record = null) {
    const s = record || read();
    if (!s) return false;
    if (scenes) {
      const id = s.scene && scenes.sceneRecord && scenes.sceneRecord(s.scene) ? s.scene : 'hub';
      if (scenes.currentId() !== id) await scenes.enter(id, { fade: true });
      else if (scenes.currentId() === null) await scenes.enter('hub', { fade: false });
      if (id !== s.scene) return true; // unknown scene: the hub's spawn will do
    }
    controls.teleport(new THREE.Vector3(s.p[0], s.p[1], s.p[2]), { yaw: s.yaw || 0, pitch: s.pitch || 0 });
    return true;
  }
  function tick(dt) {
    if (!enabled) return;
    acc += dt;
    if (acc < 3) return;
    acc = 0;
    const p = camera.position;
    if (!last || Math.hypot(p.x - last[0], p.y - last[1], p.z - last[2]) > 0.5) save();
  }
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'hidden') save(); });

  return { save, restore, hasSave, tick, read, clear, setScenes, KEY };
}
