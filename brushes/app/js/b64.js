// b64.js - bytes, base64, hashes and just enough PNG to check an image before
// it is sent. Browser-safe and DOM-free (also importable from Node).

const CHUNK = 0x8000;

export function bytesToB64(bytes) {
  let text = '';
  for (let i = 0; i < bytes.length; i += CHUNK) text += String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK));
  return btoa(text);
}

export function b64ToBytes(b64) {
  const text = atob(b64);
  const out = new Uint8Array(text.length);
  for (let i = 0; i < text.length; i += 1) out[i] = text.charCodeAt(i);
  return out;
}

export function toHex(bytes) {
  return Array.from(bytes, (b) => b.toString(16).padStart(2, '0')).join('');
}

/** sha256 hex of bytes; null when SubtleCrypto is not available (an insecure origin). */
export async function sha256Hex(bytes) {
  if (!globalThis.crypto || !globalThis.crypto.subtle) return null;
  return toHex(new Uint8Array(await globalThis.crypto.subtle.digest('SHA-256', bytes)));
}

export const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

/** {width, height, bitDepth, colorType, interlace} from a PNG's IHDR, or null. */
export function pngInfo(bytes) {
  if (!bytes || bytes.length < 33) return null;
  for (let i = 0; i < 8; i += 1) if (bytes[i] !== PNG_SIGNATURE[i]) return null;
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  if (view.getUint32(12) !== 0x49484452) return null;            // 'IHDR'
  return {width: view.getUint32(16), height: view.getUint32(20), bitDepth: bytes[24], colorType: bytes[25], interlace: bytes[28]};
}

export function describePng(info) {
  if (!info) return 'not a PNG';
  const kinds = {0: 'grey', 2: 'RGB', 3: 'palette', 4: 'grey+alpha', 6: 'RGBA'};
  return `${info.width}×${info.height}, ${info.bitDepth}-bit ${kinds[info.colorType] || 'colour type ' + info.colorType}${info.interlace ? ', interlaced' : ''}`;
}

/** True when the server will keep a replaced texture as given (F10 settled notes). */
export function isGrey8(info) {
  return !!info && info.colorType === 0 && info.bitDepth === 8 && info.interlace === 0;
}

export function blobFromB64(b64, type = 'image/png') {
  return new Blob([b64ToBytes(b64)], {type});
}
