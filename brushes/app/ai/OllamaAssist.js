/**
 * OllamaAssist.js - local-model brush parameter editing
 *
 * Talks straight to Ollama's REST API on this machine (same pattern as
 * hub/ollama.js and OBSIDIAN.md's "Vault -> Ollama" connection B; nothing
 * leaves the laptop). Shares its endpoint/tier settings with hub/ via the
 * same localStorage keys -- both tools are served from one origin, so the
 * connection is configured once.
 *
 * The model is asked to return a strict JSON patch, never given write access
 * itself: every property it names is validated and clamped against
 * BRUSH_PROPERTY_RANGES before anything is applied, and unknown properties
 * are reported back rather than silently dropped or silently applied.
 */

import { BRUSH_PROPERTY_RANGES, BLENDING_MODES } from '../editor/BrushState.js';

const DEFAULT_ENDPOINT = 'http://localhost:11434';

const TIERS = {
  sm: { model: 'llama3.1:8b', num_ctx: 8192, num_predict: 400 },
  md: { model: 'mistral-nemo:12b', num_ctx: 4096, num_predict: 400 },
};

const BOOLEAN_PROPS = [
  'brushShapeRandomized', 'brushAzimuth', 'brushFlipX', 'brushFlipY',
  'brushGrainMoving', 'brushGrainZoom', 'brushTaperLinked',
  'brushWetEdge', 'brushWetBurn',
];

// Short on purpose: this table is re-sent on every request, and CPU
// generation time on the target hardware scales with prompt length.
const PROPERTY_HINTS = {
  brushSpacing: 'gap between stamps, dotted if high',
  brushSpacingJitter: 'random spacing variation',
  brushStreamline: 'stroke smoothing, laggier if high',
  brushStreamlinePressure: 'pressure effect on smoothing',
  brushStabilization: 'wobble reduction',
  brushMotionFiltering: 'motion smoothing',
  brushJitterX: 'horizontal scatter',
  brushJitterY: 'vertical scatter',
  brushFallOff: 'edge opacity fade',
  brushShapeScatter: 'stamp rotation scatter',
  brushShapeRotation: 'base stamp rotation, radians',
  brushShapeCount: 'copies stamped per step',
  brushShapeCountJitter: 'random count variation',
  brushGrainScale: 'grain texture size',
  brushGrainRotation: 'grain rotation, radians',
  brushGrainDepth: 'grain strength / roughness',
  brushGrainDepthMin: 'min grain depth, light pressure',
  brushGrainDepthJitter: 'random grain depth variation',
  brushGrainOffsetJitter: 'random grain offset per stamp',
  brushSizeMaximum: 'stamp size, full pressure',
  brushSizeMinimum: 'stamp size, zero pressure',
  brushOpacityMaximum: 'opacity, full pressure',
  brushOpacityMinimum: 'opacity, zero pressure',
  brushBleedAmount: 'wet bleed into paper',
  brushTaperSizeStart: 'taper thinness at start',
  brushTaperSizeEnd: 'taper thinness at end',
  brushTaperTip: 'taper tip sharpness',
  brushTaperOpacity: 'taper opacity fade',
  brushWetDilution: 'paint thins with water',
  brushWetCharge: 'paint loaded per stroke',
  brushWetPull: 'existing color dragged/smeared',
  brushWetAttack: 'wet mix strength at stroke start',
  brushWetBleed: 'wet spread distance',
};

export const OllamaAssist = {
  DEFAULT_ENDPOINT,
  TIERS,

  getEndpoint() {
    return localStorage.getItem('hub:endpoint') || DEFAULT_ENDPOINT;
  },
  setEndpoint(v) {
    localStorage.setItem('hub:endpoint', v);
  },
  getTierKey() {
    return localStorage.getItem('hub:tier') || 'sm';
  },
  setTierKey(v) {
    localStorage.setItem('hub:tier', v);
  },
  getTier() {
    return TIERS[this.getTierKey()] || TIERS.sm;
  },

  async fetchTags(endpoint) {
    const r = await fetch(`${endpoint}/api/tags`, { signal: AbortSignal.timeout(6000) });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    return (data.models || []).map((m) => m.name);
  },

  familyMatches(tag, served) {
    const fam = tag.split(':')[0];
    return served.some((n) => n.split(':')[0] === fam);
  },

  async generate(endpoint, { model, prompt, options }) {
    const r = await fetch(`${endpoint}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model, prompt, stream: false, keep_alive: '5m', options }),
    });
    if (!r.ok) throw new Error(`generate HTTP ${r.status}`);
    const data = await r.json();
    return data.response || '';
  },

  async evict(endpoint, model) {
    try {
      await fetch(`${endpoint}/api/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model, keep_alive: 0 }),
      });
    } catch (_) {
      /* best effort */
    }
  },

  buildPropertyTable(state) {
    const lines = [];
    for (const [key, range] of Object.entries(BRUSH_PROPERTY_RANGES)) {
      const hint = PROPERTY_HINTS[key] || '';
      lines.push(`${key} = ${state[key]} (number, range ${range.min}-${range.max})${hint ? ' -- ' + hint : ''}`);
    }
    for (const key of BOOLEAN_PROPS) {
      lines.push(`${key} = ${!!state[key]} (boolean, true or false)`);
    }
    const blendNames = BLENDING_MODES.map((m) => `${m.id}=${m.name}`).join(', ');
    lines.push(`brushBlendingMode = ${state.brushBlendingMode} (integer 0-15: ${blendNames})`);
    return lines.join('\n');
  },

  buildPrompt(instruction, state) {
    return (
      'You are adjusting parameters of a digital painting brush. Output ONLY a JSON object -- ' +
      'no markdown code fences, no prose outside the JSON -- shaped exactly like:\n' +
      '{"changes": {"propertyName": value, ...}, "summary": "one short plain-language sentence"}\n\n' +
      'Only include properties that should actually change. Use ONLY property names from this list, ' +
      'and respect each one\'s type and range:\n' +
      `${this.buildPropertyTable(state)}\n\n` +
      `Request: ${instruction}\n\nJSON:`
    );
  },

  /**
   * Extract the first balanced {...} object from free-form model output,
   * tolerant of prose or <think> traces around it. Returns null (never
   * throws) so callers can show the raw response on failure.
   */
  extractJSON(text) {
    const stripped = String(text || '').replace(/<think>[\s\S]*?<\/think>/g, '');
    const start = stripped.indexOf('{');
    if (start === -1) return null;

    let depth = 0;
    let inString = false;
    let escape = false;

    for (let i = start; i < stripped.length; i++) {
      const ch = stripped[i];
      if (escape) { escape = false; continue; }
      if (ch === '\\') { escape = true; continue; }
      if (ch === '"') { inString = !inString; continue; }
      if (inString) continue;
      if (ch === '{') depth++;
      else if (ch === '}') {
        depth--;
        if (depth === 0) {
          try {
            return JSON.parse(stripped.slice(start, i + 1));
          } catch (_) {
            return null;
          }
        }
      }
    }
    return null;
  },

  /**
   * Validate and clamp a proposed patch against the known property schema.
   * Never trusts the model's types or ranges directly.
   */
  validatePatch(changes) {
    const applied = {};
    const rejected = [];

    if (!changes || typeof changes !== 'object') return { applied, rejected };

    for (const [key, rawValue] of Object.entries(changes)) {
      if (BOOLEAN_PROPS.includes(key)) {
        applied[key] = rawValue === true || rawValue === 'true' || rawValue === 1;
      } else if (key === 'brushBlendingMode') {
        const n = Math.round(Number(rawValue));
        if (Number.isFinite(n)) applied[key] = Math.max(0, Math.min(15, n));
        else rejected.push({ key, reason: 'not a number' });
      } else if (BRUSH_PROPERTY_RANGES[key]) {
        const n = Number(rawValue);
        if (Number.isFinite(n)) {
          const range = BRUSH_PROPERTY_RANGES[key];
          applied[key] = Math.max(range.min, Math.min(range.max, n));
        } else {
          rejected.push({ key, reason: 'not a number' });
        }
      } else {
        rejected.push({ key, reason: 'unknown property' });
      }
    }

    return { applied, rejected };
  },
};

export default OllamaAssist;
