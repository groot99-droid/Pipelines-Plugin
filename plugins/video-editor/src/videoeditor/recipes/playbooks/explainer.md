# Playbook: explainer (overlay add-on)

Built in: `ve overlay "Title" --engine pil` (no setup) and `ve overlay ... --engine remotion` (our own template in
`templates/remotion_overlay`; titles and caption pages from `--captions-from edl.json`; `--transparent` gives a WebM
with alpha, which render.py decodes with libvpx so the alpha survives). Remotion needs Node and is NOT open source:
free for individuals, for-profit orgs up to 3 people and non-profits, otherwise a company licence
(https://www.remotion.pro/license). Check eligibility before using it commercially. For deeper Remotion work,
the user can install Remotion's official agent skills themselves: `npx skills add remotion-dev/skills`.

Pick the engine per slot: PIL (simple cards/counters),
Remotion (React), Manim (formal diagrams, equations, graph morphs; see skills/manim-video/SKILL.md).

Get palette, font and visual language from the user; propose and confirm if they have none.
Duration: sync-to-narration cards 3s floor, 5-7s typical, 8-14s complex; hold the last frame >= 1s; over
voiceover total >= narration + 1s. Start the overlay `reveal_duration` early so the landing frame hits the
spoken payoff word. Never reveal two independent things at once. Use cubic easing, never linear.

Fonts fail silently: assert the font loaded (browser engines) or pass an explicit font path (PIL).
Several animations: spawn one sub-agent per slot in parallel, each with a self-contained brief and a unique
output path. Overlays sit under captions (captions are applied last).
