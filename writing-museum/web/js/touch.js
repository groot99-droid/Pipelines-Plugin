// Touch controls: left half of the screen is a virtual joystick (walk), right half drags
// to look, a short tap on the right half reads the work under the finger.
export function createTouchControls({ domElement, controls, interactions }) {
  const enabled = (navigator.maxTouchPoints || 0) > 0 || 'ontouchstart' in window;
  if (!enabled) return { enabled: false };
  document.body.classList.add('touch');

  const joy = document.createElement('div');
  joy.id = 'joystick';
  joy.innerHTML = '<div class="knob"></div>';
  document.body.appendChild(joy);
  const knob = joy.querySelector('.knob');

  const RADIUS = 50;   // px of thumb travel for full speed
  const LOOK_GAIN = 2.2;
  let movePointer = null, lookPointer = null;
  let moveStart = null, lookLast = null, tapStart = null;

  function setKnob(dx, dy) {
    knob.style.transform = `translate(${dx}px, ${dy}px)`;
  }

  function onDown(e) {
    if (e.pointerType !== 'touch') return;
    controls.engage({ pointerLock: false });
    if (e.clientX < window.innerWidth / 2 && movePointer === null) {
      movePointer = e.pointerId;
      moveStart = { x: e.clientX, y: e.clientY };
    } else if (lookPointer === null) {
      lookPointer = e.pointerId;
      lookLast = { x: e.clientX, y: e.clientY };
      tapStart = { x: e.clientX, y: e.clientY, t: performance.now() };
    } else return;
    try { domElement.setPointerCapture(e.pointerId); } catch (err) { /* ignore */ }
    e.preventDefault();
  }
  function onMove(e) {
    if (e.pointerId === movePointer) {
      let dx = (e.clientX - moveStart.x) / RADIUS;
      let dy = -(e.clientY - moveStart.y) / RADIUS;
      const len = Math.hypot(dx, dy);
      if (len > 1) { dx /= len; dy /= len; }
      controls.setMoveAxis(dx, dy);
      setKnob(dx * RADIUS * 0.8, -dy * RADIUS * 0.8);
    } else if (e.pointerId === lookPointer) {
      controls.rotateBy((e.clientX - lookLast.x) * LOOK_GAIN, (e.clientY - lookLast.y) * LOOK_GAIN);
      lookLast = { x: e.clientX, y: e.clientY };
    }
  }
  function onUp(e) {
    if (e.pointerId === movePointer) {
      movePointer = null;
      controls.setMoveAxis(0, 0);
      setKnob(0, 0);
    } else if (e.pointerId === lookPointer) {
      lookPointer = null;
      const moved = Math.hypot(e.clientX - tapStart.x, e.clientY - tapStart.y);
      if (performance.now() - tapStart.t < 250 && moved < 8) {
        const x = (e.clientX / window.innerWidth) * 2 - 1;
        const y = -(e.clientY / window.innerHeight) * 2 + 1;
        interactions.openAtScreen(x, y);
      }
    }
  }
  domElement.addEventListener('pointerdown', onDown);
  domElement.addEventListener('pointermove', onMove);
  domElement.addEventListener('pointerup', onUp);
  domElement.addEventListener('pointercancel', onUp);

  return { enabled: true };
}
