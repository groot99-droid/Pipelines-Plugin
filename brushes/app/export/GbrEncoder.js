/**
 * GbrEncoder.js - GIMP Brush (.gbr, version 2) binary encoder
 *
 * Field layout verified against GIMP's own header struct
 * (app/core/gimpbrush-header.h): seven big-endian uint32 fields --
 * header_size, version, width, height, bytes, magic_number, spacing --
 * followed by a null-terminated name and then the raw pixel data.
 *
 * Pixel convention verified independently (GIMP docs and tutorials, in
 * agreement): for a grayscale brush, BLACK is fully opaque paint and WHITE
 * is fully transparent. This app's own shape/grain canvases are the
 * opposite -- generators/ShapeGenerator.js documents "white = mark, black =
 * transparent" -- so every pixel is inverted on the way out.
 */

const GIMP_MAGIC = 0x47494d50; // 'G' 'I' 'M' 'P'

export class GbrEncoder {
  /**
   * @param {HTMLCanvasElement} sourceCanvas - white-mark-on-black texture
   * @param {{name?: string, spacingPercent?: number, size?: number}} opts
   * @returns {Uint8Array}
   */
  static encode(sourceCanvas, opts = {}) {
    const { name = 'Brush', spacingPercent = 10, size = null } = opts;
    const targetSize = size || sourceCanvas.width;

    const canvas = document.createElement('canvas');
    canvas.width = targetSize;
    canvas.height = targetSize;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(sourceCanvas, 0, 0, targetSize, targetSize);

    const { data } = ctx.getImageData(0, 0, targetSize, targetSize);
    const pixels = new Uint8Array(targetSize * targetSize);
    for (let i = 0, p = 0; i < data.length; i += 4, p++) {
      const luminance = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      pixels[p] = 255 - Math.round(luminance);
    }

    const safeName = (name || 'Brush').trim() || 'Brush';
    const nameBytes = new TextEncoder().encode(safeName);
    const headerSize = 28 + nameBytes.length + 1;
    const spacing = Math.max(1, Math.min(1000, Math.round(spacingPercent)));

    const buffer = new ArrayBuffer(headerSize + pixels.length);
    const view = new DataView(buffer);
    view.setUint32(0, headerSize, false);
    view.setUint32(4, 2, false);            // version 2
    view.setUint32(8, targetSize, false);   // width
    view.setUint32(12, targetSize, false);  // height
    view.setUint32(16, 1, false);           // bytes per pixel: grayscale
    view.setUint32(20, GIMP_MAGIC, false);
    view.setUint32(24, spacing, false);

    const bytes = new Uint8Array(buffer);
    bytes.set(nameBytes, 28);
    bytes[28 + nameBytes.length] = 0; // null terminator
    bytes.set(pixels, headerSize);

    return bytes;
  }
}

export default GbrEncoder;
