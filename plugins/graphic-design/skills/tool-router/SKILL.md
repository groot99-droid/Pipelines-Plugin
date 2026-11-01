---
name: tool-router
description: Decide which app, provider or command line does a graphic-design job - raster generation, background removal, vectorizing, upscaling, batch resize, SVG optimising, font subsetting, Adobe, Affinity, Figma, Canva, Inkscape, GIMP, Krita, Penpot, Scribus, Blender, Lottie - and say what each needs and whether it is verified. Use when a design task needs a tool beyond writing SVG or HTML, or when the owner asks what can do a job.
allowed-tools: Read Grep Glob Bash(python *search.py *)
---
# Tool router

`search` below means `python "${CLAUDE_PLUGIN_ROOT}/catalog/scripts/search.py"`. The table is
`${CLAUDE_PLUGIN_ROOT}/catalog/data/tools.csv`: job, route, provider, how, what it needs, and a status.

```
search "remove background" --domain tool
search "print layout pdf" --domain tool -n 5
```

## Rules

1. **Prefer the route that needs nothing.** Writing SVG or HTML and rendering it (route `Claude-native`) comes first when it
   can do the job. Raster pictures, background removal and upscaling go to a provider or a local tool.
2. **Check what is actually connected.** A row marked "Ready where connected" is only ready if that connector's tools are
   in this session. If they are not, say so and offer the local route.
3. **Status matters.** "Unverified" rows (community MCP servers for Photoshop, Illustrator, GIMP, Krita, Penpot) are
   proposals. Do not install, configure or call one unasked. Describe what it needs and let the owner decide, the way
   Blender add-on tools stay off until the owner enables them.
4. **Paid and slow work asks first.** Provider generation, upscaling on a GPU and anything that spends credits needs the
   owner's go-ahead, with the cost named if known. Inside a studio run, the studio's own gates apply instead.
5. **Local installs are the owner's.** Say which command line a job needs (for example `svgo`, `inkscape`, `magick`) and
   check that it exists before assuming it is there. Never install software unasked.
6. **Read-only on brand.** This plugin never writes a brand gate or token file. A studio run consumes the plugin read-only.

## Reporting

Give the route you picked, why it beat the next one, what it needs, and what you could not check. If two routes tie,
give both in one line each and ask.
