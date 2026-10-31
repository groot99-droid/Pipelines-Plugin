// input.js - draw a stroke on the preview with a mouse, a finger or an Apple
// Pencil. DOM (pointer events). The samples are in the preview's own unit U
// (1060 across); the engine turns them into a path (path.js drawnPath).
//
// A pen gives pressure, and tilt when the hardware reports it; a mouse or a
// finger gives none, and the engine uses the pressure level of the controls.
// touch-action: none on the canvas (styles.css) keeps the page from scrolling
// under a drag.

import {VIEW_W} from './path.js';

/**
 * attachInput(canvas, {getLayout, onStart(), onSamples(raw, pointerType), onEnd(raw)}) -> detach()
 * getLayout() returns {bandU, totalU}: the stroke band is the top bandU of totalU.
 */
export function attachInput(canvas, {getLayout, onStart, onSamples, onEnd}) {
  let raw = null; let pointerId = null; let pointerType = 'mouse'; let queued = 0;

  const toSample = (event, rect, layout) => {
    const x = (event.clientX - rect.left) / rect.width * VIEW_W;
    const y = (event.clientY - rect.top) / rect.height * layout.totalU;
    const pen = event.pointerType === 'pen';
    const tx = event.tiltX || 0; const ty = event.tiltY || 0;
    const tilt = pen ? Math.min(1, Math.hypot(tx, ty) / 90) : 0;
    const az = typeof event.azimuthAngle === 'number' && tilt > 0 ? event.azimuthAngle : Math.atan2(ty, tx);
    return {x, y, t: event.timeStamp, p: pen ? Math.max(0.02, event.pressure || 0.02) : 0.6, tilt, az};
  };

  const push = (event) => {
    const layout = getLayout(); const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const list = typeof event.getCoalescedEvents === 'function' ? event.getCoalescedEvents() : [];
    for (const e of list.length ? list : [event]) raw.push(toSample(e, rect, layout));
  };

  const flush = () => { queued = 0; if (raw) onSamples(raw, pointerType); };
  const schedule = () => { if (!queued) queued = requestAnimationFrame(flush); };

  const down = (event) => {
    if (event.button !== undefined && event.button > 0) return;
    const layout = getLayout(); const rect = canvas.getBoundingClientRect();
    const y = (event.clientY - rect.top) / rect.height * layout.totalU;
    if (y > layout.bandU) return;                                    // below the band: Procreate's own thumbnail, not drawable
    event.preventDefault();
    pointerId = event.pointerId; pointerType = event.pointerType || 'mouse';
    try { canvas.setPointerCapture(pointerId); } catch (_) { /* not capturable: the drag still works over the canvas */ }
    raw = []; onStart(); push(event); schedule();
  };
  const move = (event) => { if (raw && event.pointerId === pointerId) { push(event); schedule(); } };
  const up = (event) => {
    if (!raw || event.pointerId !== pointerId) return;
    push(event);
    const finished = raw; raw = null; pointerId = null;
    if (queued) { cancelAnimationFrame(queued); queued = 0; }
    onSamples(finished, pointerType); onEnd(finished, pointerType);
  };

  canvas.addEventListener('pointerdown', down);
  canvas.addEventListener('pointermove', move);
  canvas.addEventListener('pointerup', up);
  canvas.addEventListener('pointercancel', up);
  return () => {
    canvas.removeEventListener('pointerdown', down); canvas.removeEventListener('pointermove', move);
    canvas.removeEventListener('pointerup', up); canvas.removeEventListener('pointercancel', up);
    if (queued) cancelAnimationFrame(queued);
  };
}
