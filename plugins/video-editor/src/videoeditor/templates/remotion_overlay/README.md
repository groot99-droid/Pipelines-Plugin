# remotion_overlay (slot template)

Written for videoeditor; contains no Remotion source. It depends on the `remotion` npm packages, which have
their own licence: free for individuals, for-profit organisations of up to 3 people, and non-profits; larger
companies need a company licence (https://www.remotion.pro/license).

`ve overlay --engine remotion` copies this folder into `<edit>/animations/slot_N/`, writes `overlay.json`
(see `src/types.ts`), runs `npm install` once and renders `render.mp4` (or `render.webm` with alpha when
`--transparent`). Node 20.19+/22.13+ and a headless Chrome (Remotion downloads one, or set
`REMOTION_BROWSER_EXECUTABLE`) are required.
