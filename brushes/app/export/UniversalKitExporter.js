/**
 * UniversalKitExporter.js - Multi-app brush export
 *
 * Procreate has a real binary format we can write exactly (BrushArchive.js).
 * GIMP's .gbr is documented well enough to write exactly too (GbrEncoder.js).
 * Photoshop's .abr and Affinity's .afbrushes are not: Adobe has never
 * published the modern (v6+) format, and it wraps a serialized
 * ActionDescriptor blob that is only known through partial, disputed
 * reverse-engineering. Affinity's format is entirely undocumented. Guessing
 * at either risks a file that LOOKS exported but silently fails to open --
 * worse than not offering it.
 *
 * Every mainstream brush engine, though, can build a brush tip from a plain
 * image ("Define Brush Preset" in Photoshop, "create brush from image" in
 * Affinity and Clip Studio Paint, brush-tip import in Krita). That path is
 * guesswork-free, so this kit leans on it: real PNGs, a real .gbr, and a
 * recipe explaining exactly how to bring them into each app.
 */

import { GbrEncoder } from './GbrEncoder.js';
import { BrushExporter } from './BrushExporter.js';
import { BRUSH_PROPERTY_RANGES, BLENDING_MODES } from '../editor/BrushState.js';

export class UniversalKitExporter {
  static async export(brushState, shapeCanvas, grainCanvas, previewCanvas) {
    const state = brushState.get ? brushState.get() : brushState;
    const spacingPercent = Math.round((state.brushSpacing || 0) * 100);
    const zip = {};

    zip['gimp/shape.gbr'] = [
      GbrEncoder.encode(shapeCanvas, { name: state.name, spacingPercent }),
      { level: 6 },
    ];

    const [shapeInk, grainInk, shapeMask, grainMask] = await Promise.all([
      BrushExporter.canvasToInkAlphaPNG(shapeCanvas, 512),
      BrushExporter.canvasToInkAlphaPNG(grainCanvas, 1024),
      BrushExporter.canvasToGrayscalePNG(shapeCanvas, 512),
      BrushExporter.canvasToGrayscalePNG(grainCanvas, 1024),
    ]);

    zip['ink/shape-ink.png'] = [new Uint8Array(await shapeInk.arrayBuffer()), { level: 0 }];
    zip['ink/grain-ink.png'] = [new Uint8Array(await grainInk.arrayBuffer()), { level: 0 }];
    zip['mask/shape-mask.png'] = [new Uint8Array(await shapeMask.arrayBuffer()), { level: 0 }];
    zip['mask/grain-mask.png'] = [new Uint8Array(await grainMask.arrayBuffer()), { level: 0 }];

    if (previewCanvas) {
      const previewBlob = await new Promise((resolve) => previewCanvas.toBlob(resolve, 'image/png'));
      if (previewBlob) {
        zip['stroke-preview.png'] = [new Uint8Array(await previewBlob.arrayBuffer()), { level: 0 }];
      }
    }

    zip['brush-recipe.md'] = [
      new TextEncoder().encode(this.buildRecipe(state, spacingPercent)),
      { level: 6 },
    ];

    const zipped = fflate.zipSync(zip);
    return new Blob([zipped], { type: 'application/zip' });
  }

  static buildRecipe(state, spacingPercent) {
    const blendName = (BLENDING_MODES.find((b) => b.id === state.brushBlendingMode) || {}).name || 'Normal';
    const lines = [];

    lines.push(`# ${state.name || 'Untitled Brush'}`);
    if (state.authorName) lines.push('', `_by ${state.authorName}_`);
    if (state.notes) lines.push('', state.notes);

    lines.push(
      '', '## What is in this kit', '',
      '- `gimp/shape.gbr` -- a real GIMP brush file. Krita can also import it directly as a brush tip.',
      '- `ink/shape-ink.png`, `ink/grain-ink.png` -- black ink on a transparent background, the shape ' +
        'apps like Photoshop, Affinity, and Clip Studio Paint expect from a "create brush from image" tool.',
      '- `mask/shape-mask.png`, `mask/grain-mask.png` -- the raw grayscale textures this brush was ' +
        'built from (white = mark, black = transparent), for reference or hand re-editing.',
      '- `stroke-preview.png` -- how the brush actually paints at light/medium/heavy pressure, if this ' +
        'kit was exported with a live preview.',
    );

    lines.push(
      '', '## Bringing it into other apps', '',
      '**Photoshop, Affinity Photo/Designer, Clip Studio Paint** -- open `ink/shape-ink.png`, select ' +
        'all, and use that app\'s brush-from-image tool (Photoshop: Edit -> Define Brush Preset). Set ' +
        `spacing to ${spacingPercent}% to match this brush. These apps' native brush formats (.abr, ` +
        '.afbrushes, .sut) are undocumented or proprietary, so this PNG path is the reliable one -- a ' +
        'hand-built binary file risks silently failing to open.',
      '',
      '**Krita** -- Settings -> Manage Resources... -> Import Resources -> Brush tips, and pick either ' +
        '`gimp/shape.gbr` or `ink/shape-ink.png`.',
      '',
      '**GIMP** -- drop `gimp/shape.gbr` into your brushes folder (Edit -> Preferences -> Folders -> Brushes).',
      '',
      '**Anything else (Rebelle, ArtRage, Paint Tool SAI, and similar)** -- most brush engines accept a ' +
        'black-on-transparent PNG as a custom tip; use `ink/shape-ink.png` and check that app\'s manual ' +
        'for "custom brush from image".',
    );

    lines.push('', '## Parameters', '', '| Property | Value |', '|---|---|');
    for (const [key, range] of Object.entries(BRUSH_PROPERTY_RANGES)) {
      const value = state[key];
      if (value === undefined || value === null) continue;
      lines.push(`| ${key} | ${range.display(value)} |`);
    }
    lines.push(`| Blending Mode | ${blendName} |`);

    lines.push('', '_Exported from the Studio Headless OS brush designer._');
    return lines.join('\n');
  }
}

export default UniversalKitExporter;
