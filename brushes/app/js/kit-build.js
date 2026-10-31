// kit-build.js - the browser half of the Universal Kit: it turns the brush's
// shape and grain images into the ink / mask PNGs, gathers the stroke preview
// (the thumbnail stored in the brush) and the recipe, and returns the
// `files` array of the kit export request ([{path, b64}]). The server checks
// each name, zips them and (when asked) adds the .brush; see kit.js.

import {bytesToB64, b64ToBytes, pngInfo} from './b64.js';
import {textureView, thumbnailView} from './textures.js';
import {slugName, fitSize, coverageFromRgba, maskRgba, inkRgba, recipeMarkdown, KIT_ENTRY} from './kit.js';

const MAX_SIDE = 1024;

/** Decode PNG bytes into {width, height, data} (RGBA), scaled down to maxSide. */
export async function decodeToRgba(bytes, maxSide = MAX_SIDE) {
  const bitmap = await createImageBitmap(new Blob([bytes], {type: 'image/png'}));
  const size = fitSize(bitmap.width, bitmap.height, maxSide);
  const canvas = document.createElement('canvas');
  canvas.width = size.width; canvas.height = size.height;
  const g = canvas.getContext('2d', {willReadFrequently: true});
  g.drawImage(bitmap, 0, 0, size.width, size.height);
  if (bitmap.close) bitmap.close();
  return {width: size.width, height: size.height, data: g.getImageData(0, 0, size.width, size.height).data};
}

export async function rgbaToPng(width, height, rgba) {
  const canvas = document.createElement('canvas');
  canvas.width = width; canvas.height = height;
  const g = canvas.getContext('2d');
  g.putImageData(new ImageData(rgba, width, height), 0, 0);
  const blob = await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));
  if (!blob) throw new Error('The browser could not encode a PNG.');
  return new Uint8Array(await blob.arrayBuffer());
}

/**
 * Build the kit files for a doc.
 *   opts.schema      the indexed schema (labels for the recipe), or null
 *   opts.gbrBytes    the .gbr the server made for this brush, or null
 *   opts.gbrSpacing  the spacing that .gbr was written with
 * Resolves to {files: [{path, b64}], paths, notes} where notes say what was left out and why.
 */
export async function buildKitFiles(doc, {schema = null, gbrBytes = null, gbrSpacing = null} = {}) {
  const slug = slugName(doc.value('name', 'main') || doc.name);
  const files = []; const notes = [];
  const add = (path, bytes) => {
    if (!KIT_ENTRY.test(path)) throw new Error(`${path} is not a kit entry.`);
    files.push({path, b64: bytesToB64(bytes)});
  };
  if (gbrBytes) add(`gimp/${slug}.gbr`, gbrBytes);
  for (const [role, invertKey] of [['shape', 'shapeInverted'], ['grain', 'textureInverted']]) {
    const view = textureView(doc, role);
    if (view.kind !== 'image') {
      notes.push(view.kind === 'bundled' ? `The ${role} is an image that ships inside Procreate (${view.ref}); there is no picture of it to write.`
        : `The brush has no ${role} image.`);
      continue;
    }
    const bytes = b64ToBytes(view.b64);
    if (!pngInfo(bytes)) { notes.push(`The ${role} image is not a PNG that could be read.`); continue; }
    const image = await decodeToRgba(bytes);
    const coverage = coverageFromRgba(image.data, {inverted: doc.value(invertKey, 'main') === true});
    add(`ink/${role}-ink.png`, await rgbaToPng(image.width, image.height, inkRgba(coverage)));
    add(`mask/${role}-mask.png`, await rgbaToPng(image.width, image.height, maskRgba(coverage)));
  }
  const thumb = thumbnailView(doc);
  if (thumb.kind === 'image') add('stroke-preview.png', b64ToBytes(thumb.b64));
  else notes.push('There is no thumbnail to use as a stroke preview.');
  if (!gbrBytes) notes.push('No .gbr: the shape could not be written as one.');
  const paths = [...files.map((f) => f.path), 'brush-recipe.md'];
  const recipe = recipeMarkdown({name: doc.value('name', 'main') || doc.name, era: doc.era, libraryId: doc.libraryId, schema,
    settings: doc.effective('main'), paths, notes, gbrSpacing: gbrBytes ? gbrSpacing : null});
  add('brush-recipe.md', new TextEncoder().encode(recipe));
  return {files, paths, notes, slug};
}
