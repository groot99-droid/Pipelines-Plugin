import * as THREE from 'three';

const EYE_HEIGHT = 1.7;
const MOVE_SPEED = 4.2; // m/s
const COLLIDE_RADIUS = 0.35;
const DOWN = new THREE.Vector3(0, -1, 0);
// Floor-following searches a narrow band around the player's feet (enough to
// climb stair treads smoothly) rather than "nearest floor anywhere below" --
// this building stacks a ground floor and a mezzanine at the same XZ
// footprint in places, and a wide-open downward search would snap the player
// up onto the floor of the level above.
const STEP_UP = 0.5;
const STEP_DOWN = 1.0;

function isEditable(t) {
  return !!t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.tagName === 'SELECT' || t.isContentEditable);
}

export function createControls(camera, domElement, getCollidables) {
  const keys = { forward: false, back: false, left: false, right: false };
  const axis = { x: 0, y: 0 };  // analog move (touch joystick): x = strafe right, y = forward
  let yaw = 0;
  let pitch = 0;
  let engaged = false;       // WASD movement is active
  let pointerLocked = false; // true pointer-lock look (mouse always rotates)
  let dragLooking = false;   // fallback: rotate only while a mouse button is held
  let collision = true;      // walls block movement (the guided tour turns this off)
  let lastPointerType = 'mouse';

  const euler = new THREE.Euler(0, 0, 0, 'YXZ');
  const raycaster = new THREE.Raycaster();
  const forwardVec = new THREE.Vector3();
  const rightVec = new THREE.Vector3();
  const moveVec = new THREE.Vector3();
  const rayOrigin = new THREE.Vector3();
  const axisDir = new THREE.Vector3();

  function onKeyDown(e) {
    if (isEditable(e.target)) return;
    switch (e.code) {
      case 'KeyW': case 'ArrowUp': keys.forward = true; break;
      case 'KeyS': case 'ArrowDown': keys.back = true; break;
      case 'KeyA': case 'ArrowLeft': keys.left = true; break;
      case 'KeyD': case 'ArrowRight': keys.right = true; break;
    }
  }
  function onKeyUp(e) {
    switch (e.code) {
      case 'KeyW': case 'ArrowUp': keys.forward = false; break;
      case 'KeyS': case 'ArrowDown': keys.back = false; break;
      case 'KeyA': case 'ArrowLeft': keys.left = false; break;
      case 'KeyD': case 'ArrowRight': keys.right = false; break;
    }
  }
  // Turn by radians (positive dYaw turns right, positive dPitch looks down, like mouse deltas).
  function rotateRadians(dYaw, dPitch) {
    yaw -= dYaw;
    pitch -= dPitch;
    pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, pitch));
    euler.set(pitch, yaw, 0);
    camera.quaternion.setFromEuler(euler);
  }
  function applyLook(movementX, movementY) {
    rotateRadians(movementX * 0.0022, movementY * 0.0022);
  }
  function onMouseMove(e) {
    if (pointerLocked || dragLooking) {
      applyLook(e.movementX || 0, e.movementY || 0);
    }
  }
  function onLockChange() {
    pointerLocked = document.pointerLockElement === domElement;
    engaged = engaged || pointerLocked;
  }
  function onPointerDown(e) {
    lastPointerType = e.pointerType || 'mouse';
    if (e.button !== 0) return;
    engaged = true;
    if (!pointerLocked && lastPointerType !== 'touch') dragLooking = true;
  }
  function onPointerUp() { dragLooking = false; }

  function requestLock() {
    if (lastPointerType === 'touch') return;
    const p = domElement.requestPointerLock && domElement.requestPointerLock();
    if (p && typeof p.catch === 'function') p.catch(() => {});
  }

  domElement.addEventListener('click', () => {
    engaged = true;
    requestLock();
  });
  domElement.addEventListener('pointerdown', onPointerDown);
  document.addEventListener('pointerdown', (e) => { lastPointerType = e.pointerType || 'mouse'; }, true);
  document.addEventListener('pointerup', onPointerUp);
  document.addEventListener('pointerlockchange', onLockChange);
  document.addEventListener('keydown', onKeyDown);
  document.addEventListener('keyup', onKeyUp);
  document.addEventListener('mousemove', onMouseMove);

  function blocked(originVec, dirVec, dist, walls) {
    if (dist <= 0) return false;
    raycaster.set(originVec, dirVec);
    raycaster.far = dist;
    const hits = raycaster.intersectObjects(walls, false);
    return hits.length > 0 && hits[0].distance < dist;
  }

  function tryMove(delta) {
    const len = moveVec.length();
    if (len === 0) return;
    if (len > 1) moveVec.divideScalar(len);
    moveVec.multiplyScalar(MOVE_SPEED * delta);
    if (!collision) {
      camera.position.x += moveVec.x;
      camera.position.z += moveVec.z;
      return;
    }
    const { walls } = getCollidables();

    // Move on each horizontal axis independently so sliding along a wall works.
    // Collision rays run 1.2 m above the player's feet (not at absolute y=1.2), so walls
    // on upper floors collide and ground-floor walls below them don't.
    const rayY = camera.position.y - EYE_HEIGHT + 1.2;
    if (Math.abs(moveVec.x) > 0) {
      rayOrigin.set(camera.position.x, rayY, camera.position.z);
      axisDir.set(Math.sign(moveVec.x), 0, 0);
      if (!blocked(rayOrigin, axisDir, Math.abs(moveVec.x) + COLLIDE_RADIUS, walls)) {
        camera.position.x += moveVec.x;
      }
    }
    if (Math.abs(moveVec.z) > 0) {
      rayOrigin.set(camera.position.x, rayY, camera.position.z);
      axisDir.set(0, 0, Math.sign(moveVec.z));
      if (!blocked(rayOrigin, axisDir, Math.abs(moveVec.z) + COLLIDE_RADIUS, walls)) {
        camera.position.z += moveVec.z;
      }
    }
  }

  function followFloor() {
    const { floors } = getCollidables();
    if (!floors || floors.length === 0) return;
    const feetY = camera.position.y - EYE_HEIGHT;
    rayOrigin.set(camera.position.x, feetY + STEP_UP, camera.position.z);
    raycaster.set(rayOrigin, DOWN);
    raycaster.far = STEP_UP + STEP_DOWN;
    const hits = raycaster.intersectObjects(floors, false);
    if (hits.length > 0) {
      camera.position.y = hits[0].point.y + EYE_HEIGHT;
    }
  }

  // Height of the floor under (x, z), searched from nearY+up down to nearY-down. null when none.
  function groundY(x, z, nearY, { up = 1.0, down = 4.0 } = {}) {
    const { floors } = getCollidables();
    if (!floors || floors.length === 0) return null;
    rayOrigin.set(x, nearY + up, z);
    raycaster.set(rayOrigin, DOWN);
    raycaster.far = up + down;
    const hits = raycaster.intersectObjects(floors, false);
    return hits.length ? hits[0].point.y : null;
  }

  function update(delta) {
    camera.getWorldDirection(forwardVec);
    forwardVec.y = 0;
    forwardVec.normalize();
    rightVec.crossVectors(forwardVec, camera.up).normalize();

    moveVec.set(0, 0, 0);
    if (keys.forward) moveVec.add(forwardVec);
    if (keys.back) moveVec.sub(forwardVec);
    if (keys.right) moveVec.add(rightVec);
    if (keys.left) moveVec.sub(rightVec);
    if (axis.x || axis.y) {
      moveVec.addScaledVector(forwardVec, axis.y);
      moveVec.addScaledVector(rightVec, axis.x);
    }

    tryMove(delta);
    followFloor();
  }

  // ---- look state -------------------------------------------------------------------
  function syncLook() {
    // Re-read yaw/pitch from the camera after something else (framing, lookAt, tour) rotated it,
    // so the next mouse movement continues from the current view instead of snapping back.
    euler.setFromQuaternion(camera.quaternion, 'YXZ');
    yaw = euler.y;
    pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, euler.x));
    euler.set(pitch, yaw, 0);
    camera.quaternion.setFromEuler(euler);
  }
  function setLook(y, p = 0) {
    yaw = y;
    pitch = Math.max(-Math.PI / 2 + 0.05, Math.min(Math.PI / 2 - 0.05, p));
    euler.set(pitch, yaw, 0);
    camera.quaternion.setFromEuler(euler);
  }
  function getLook() { return { yaw, pitch }; }
  function lookAt(target) {
    camera.lookAt(target);
    syncLook();
  }
  function rotateBy(dx, dy) { applyLook(dx, dy); }

  // ---- movement state / test hooks -------------------------------------------------
  function setKeys(next = {}) {
    keys.forward = !!next.forward;
    keys.back = !!next.back;
    keys.left = !!next.left;
    keys.right = !!next.right;
  }
  function setMoveAxis(x, y) {
    const len = Math.hypot(x, y);
    const s = len > 1 ? 1 / len : 1;
    axis.x = x * s;
    axis.y = y * s;
  }
  function setCollision(on) { collision = !!on; }
  function getCollision() { return collision; }
  function isLocked() { return engaged; }
  function isPointerLocked() { return pointerLocked; }
  function setPosition(x, y, z) { camera.position.set(x, y, z); }

  // Place the player: snap to the floor under the point when there is one, then look.
  function teleport(pos, { yaw: y, pitch: p, lookAt: target } = {}) {
    camera.position.copy(pos);
    const g = groundY(pos.x, pos.z, pos.y - EYE_HEIGHT, { up: 1.0, down: 3.0 });
    if (g !== null) camera.position.y = g + EYE_HEIGHT;
    if (target) lookAt(target);
    else if (y !== undefined) setLook(y, p || 0);
  }

  function engage({ pointerLock = true } = {}) {
    engaged = true;
    if (pointerLock) requestLock();
  }
  function release() {
    if (pointerLocked && document.exitPointerLock) document.exitPointerLock();
  }

  function state() {
    return { position: camera.position.toArray(), yaw, pitch, engaged, pointerLocked, collision };
  }

  function dispose() {
    document.removeEventListener('pointerlockchange', onLockChange);
    document.removeEventListener('keydown', onKeyDown);
    document.removeEventListener('keyup', onKeyUp);
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('pointerup', onPointerUp);
    domElement.removeEventListener('pointerdown', onPointerDown);
  }

  return {
    update, isLocked, isPointerLocked, setPosition, engage, release, dispose, EYE_HEIGHT,
    syncLook, setLook, getLook, lookAt, rotateBy, rotateRadians,
    setKeys, setMoveAxis, setCollision, getCollision, groundY, teleport, state,
  };
}
