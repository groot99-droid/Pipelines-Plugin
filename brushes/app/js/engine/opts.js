// opts.js - the `opts` of engine.render() for an open doc. DOM-adjacent (it uses
// the textures panel's view of the doc); shared by designer.js and the self-test
// so both feed the engine the same way.

import {textureView, thumbnailView} from '../textures.js';

/**
 * previewOpts(doc, urlFor, extra) -> opts
 *   urlFor(slot, b64) returns a blob: URL for an image (or null for no image); `slot` is
 *   'thumb' | 'shape' | 'grain'. The caller owns the URLs (it should reuse one for the same image).
 */
export function previewOpts(doc, urlFor, extra = {}) {
  const thumb = thumbnailView(doc);
  const shape = textureView(doc, 'shape'); const grain = textureView(doc, 'grain');
  const held = doc.textures || {};
  const info = (view, entry) => ({...(entry || {}), source: view.kind === 'image' ? 'embedded' : view.kind, ref: view.ref || (entry || {}).ref});
  return {
    era: doc.era, name: doc.name, hasSub: !!doc.hasSub,
    thumbnailUrl: urlFor('thumb', thumb.kind === 'image' ? thumb.b64 : null),
    shapeUrl: urlFor('shape', shape.kind === 'image' ? shape.b64 : null),
    grainUrl: urlFor('grain', grain.kind === 'image' ? grain.b64 : null),
    shapeInfo: info(shape, held.shape), grainInfo: info(grain, held.grain),
    ...extra,
  };
}
