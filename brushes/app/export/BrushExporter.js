/**
 * BrushExporter.js - .brush and .brushset Export
 *
 * Packages brush data into valid Procreate brush files.
 * Uses fflate for ZIP compression (loaded as global via CDN).
 */

import { BrushArchive } from './BrushArchive.js';
import { PlistEncoder } from './PlistEncoder.js';

export class BrushExporter {
  /**
   * Export a single brush as .brush file
   */
  static async exportBrush(brushState, shapeCanvas, grainCanvas) {
    // 1. Encode Brush.archive binary plist
    const archive = BrushArchive.encode(brushState);

    // 2. Export Shape.png from canvas (grayscale, 512×512)
    const shapeBlob = await this.canvasToGrayscalePNG(shapeCanvas, 512);

    // 3. Export Grain.png from canvas (grayscale, 1024×1024)
    const grainBlob = await this.canvasToGrayscalePNG(grainCanvas, 1024);

    // 4. Generate Thumbnail.png (256×256 composite)
    const thumbBlob = await this.generateThumbnail(shapeCanvas, grainCanvas, 256);

    // 5. Package ZIP using fflate (global)
    const zip = {};

    zip['Brush.archive'] = [new Uint8Array(archive), { level: 6 }];
    zip['Shape.png'] = [new Uint8Array(await shapeBlob.arrayBuffer()), { level: 0 }];
    zip['Grain.png'] = [new Uint8Array(await grainBlob.arrayBuffer()), { level: 0 }];
    zip['QuickLook/Thumbnail.png'] = [new Uint8Array(await thumbBlob.arrayBuffer()), { level: 0 }];

    const zipped = fflate.zipSync(zip);

    return new Blob([zipped], { type: 'application/octet-stream' });
  }

  static async canvasToGrayscalePNG(sourceCanvas, targetSize) {
    const canvas = document.createElement('canvas');
    canvas.width = targetSize;
    canvas.height = targetSize;
    const ctx = canvas.getContext('2d');

    ctx.drawImage(sourceCanvas, 0, 0, targetSize, targetSize);

    const imageData = ctx.getImageData(0, 0, targetSize, targetSize);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
      const gray = Math.round(0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2]);
      data[i] = gray;
      data[i + 1] = gray;
      data[i + 2] = gray;
      data[i + 3] = 255;
    }

    ctx.putImageData(imageData, 0, 0);

    return new Promise((resolve) => {
      canvas.toBlob(resolve, 'image/png');
    });
  }

  /**
   * Convert a white-mark-on-black texture into black ink on a transparent
   * background -- the convention "create brush from image" tools in
   * Photoshop, Affinity, and Clip Studio Paint expect (verified: Photoshop's
   * own custom-brush docs describe painting the mark in black on white or
   * transparent, opposite of this app's own generators).
   */
  static async canvasToInkAlphaPNG(sourceCanvas, targetSize) {
    const canvas = document.createElement('canvas');
    canvas.width = targetSize;
    canvas.height = targetSize;
    const ctx = canvas.getContext('2d');

    ctx.drawImage(sourceCanvas, 0, 0, targetSize, targetSize);

    const imageData = ctx.getImageData(0, 0, targetSize, targetSize);
    const data = imageData.data;

    for (let i = 0; i < data.length; i += 4) {
      const luminance = 0.299 * data[i] + 0.587 * data[i + 1] + 0.114 * data[i + 2];
      data[i] = 0;
      data[i + 1] = 0;
      data[i + 2] = 0;
      data[i + 3] = Math.round(luminance);
    }

    ctx.putImageData(imageData, 0, 0);

    return new Promise((resolve) => {
      canvas.toBlob(resolve, 'image/png');
    });
  }

  static async generateThumbnail(shapeCanvas, grainCanvas, size = 256) {
    const canvas = document.createElement('canvas');
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#F5F0E8';
    ctx.fillRect(0, 0, size, size);

    const shapeSize = size * 0.6;
    const shapeX = (size - shapeSize) / 2;
    const shapeY = (size - shapeSize) / 2;

    ctx.drawImage(shapeCanvas, shapeX, shapeY, shapeSize, shapeSize);

    if (grainCanvas) {
      ctx.globalCompositeOperation = 'multiply';
      ctx.globalAlpha = 0.5;
      ctx.drawImage(grainCanvas, 0, 0, size, size);
      ctx.globalAlpha = 1;
      ctx.globalCompositeOperation = 'source-over';
    }

    return new Promise((resolve) => {
      canvas.toBlob(resolve, 'image/png');
    });
  }

  static downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  static async exportBrushset(name, brushes) {
    const zip = {};
    const uuids = [];

    for (const { brushState, shapeCanvas, grainCanvas } of brushes) {
      const state = brushState.get ? brushState.get() : brushState;
      const uuid = state.identifier;
      uuids.push(uuid);

      const folderPrefix = `${uuid}/`;

      const archive = BrushArchive.encode(brushState);
      const shapeBlob = await this.canvasToGrayscalePNG(shapeCanvas, 512);
      const grainBlob = await this.canvasToGrayscalePNG(grainCanvas, 1024);
      const thumbBlob = await this.generateThumbnail(shapeCanvas, grainCanvas, 256);

      zip[`${folderPrefix}Brush.archive`] = [new Uint8Array(archive), { level: 6 }];
      zip[`${folderPrefix}Shape.png`] = [new Uint8Array(await shapeBlob.arrayBuffer()), { level: 0 }];
      zip[`${folderPrefix}Grain.png`] = [new Uint8Array(await grainBlob.arrayBuffer()), { level: 0 }];
      zip[`${folderPrefix}QuickLook/Thumbnail.png`] = [new Uint8Array(await thumbBlob.arrayBuffer()), { level: 0 }];
    }

    const brushsetPlist = this.createBrushsetPlist(uuids);
    zip['brushset.plist'] = [brushsetPlist, { level: 6 }];

    const zipped = fflate.zipSync(zip);

    return new Blob([zipped], { type: 'application/octet-stream' });
  }

  static createBrushsetPlist(uuids) {
    const encoder = new PlistEncoder();
    return encoder.encode(uuids);
  }
}

export default BrushExporter;
