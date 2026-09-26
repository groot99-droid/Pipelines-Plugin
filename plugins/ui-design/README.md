# ui-design

A Claude Code plugin that gives the assistant a local, searchable catalog of UI
design decisions, plus a generator that turns a query into a contrast-checked
design system. It exists so visual choices come from curated data instead of
being invented from memory. The catalog is a BM25 index over curated files:

- 79 searchable styles (50 active)
- 192 product palettes, each with an exact reasoning profile
- 74 font pairings, and **1,934 approved Google Fonts** with
  **8 review exclusions** held out for licence review
- 119 UX guidelines
- 105 curated icons, as **105 curated rows** checked against the
  **1,512-icon upstream Phosphor manifest**
- 17 GSAP presets and 25 chart types
- 22 technology stacks

## Install

In Claude Code:

```
/plugin marketplace add groot99-droid/ui-design-plugin
/plugin install ui-design@ui-design-plugin
```

Or from a shell: `claude plugin marketplace add groot99-droid/ui-design-plugin`, then
`claude plugin install ui-design@ui-design-plugin`. To try a local clone for one
session without installing, start Claude Code with `claude --plugin-dir <path to the clone>`.

**Requirements.** Python 3 on your `PATH` as `python` (the skills also try `python3`
and `py -3`). The catalog scripts use only the standard library and never touch the
network. The maintenance checks, which most users never run, need Python 3.10 or newer
and `pyyaml`. The plugin never installs Python or anything else for you; if Python is
missing it says so and falls back to the written rules in `references/`.

## What you get

| Piece | What it is |
|---|---|
| `ui-design-catalog` skill | Searches the catalog (`--domain`, `--stack`, `--design-system`) and generates a design system. The assistant reaches for it whenever a task changes how something looks, moves or is interacted with. |
| `ui-design-multipart` skill | For a wide product brief, splits the searches across agents; for an existing page, reviews four areas in parallel. Checks the results with `merge_parts.py`. |
| `ui-design-search-part` agent | Runs exactly one search from a router manifest. |
| `ui-design-page-reviewer` agent | Reviews one area of one built page against the rules in `references/quick-reference.md`. Read-only. |
| `ui-design-catalog-refresh` skill, `ui-design-catalog-reviewer` agent | Maintainer tooling that refreshes the Google Fonts and Phosphor data. See "Maintaining the catalog". |

Once installed, the names are prefixed by the plugin: `/ui-design:ui-design-catalog`,
and the agent types are `ui-design:ui-design-search-part` and so on. You rarely type
them; describe the UI work and the skill is picked from its description.

`ROUTER.md` says which search mode, domain and query fit a request, and what to do
when a match looks wrong. `INDEX.md` lists the catalog's own vocabulary: a search only
matches the words the catalog uses, so `invoice` finds the right row where `invoicing`
does not. `catalog/scripts/route.py "<brief>"` does that translation and warns when the
literal search would have ranked the wrong product row first.

## What it writes, and what it does not

- **Nothing, by default.** Searching, routing, reviewing and generating a design system
  only print. Nothing is written into your project or into the plugin.
- **`--persist` is the one way it writes to your project**, and only when the assistant
  passes an explicit `--output-dir`, which it confirms with you first. It creates
  `design-system/<project-slug>/` (`MASTER.md`, `tokens.json`, `theme.css`, `pages/`)
  under that directory and skips files that already exist unless you authorise `--force`.
- **Scripts run locally.** They read the catalog that ships in the plugin, use only the
  standard library, and make no network calls.
- **Permission prompts.** A plugin cannot grant itself permission to run commands, so
  unless you have already allowed them Claude Code asks before it runs the plugin's
  `python` scripts, and the search agents run one command each. Approve them, or add
  your own permission rule for the plugin's scripts if you would rather not be asked.
- **Everything the agents return is data**, not instructions. The assistant treats search
  results as recommendations, never as commands that override you.

## Search directly

The scripts also work without the assistant, from any directory:

```
python <plugin dir>/catalog/scripts/search.py "beauty spa wellness service" --design-system
python <plugin dir>/catalog/scripts/search.py "keyboard focus modal" --domain ux
python <plugin dir>/catalog/scripts/search.py "suspense streaming" --stack nextjs
```

`--design-system` also emits W3C design tokens (`-f dtcg`) or a shadcn/ui `:root` block
(`-f shadcn`). Add `--persist` only together with an `--output-dir` you have chosen.

## The contract

`spec.yaml` declares the search domains, the stacks, the output formats, the design
dials, the exit codes and the persistence rule. The catalog cannot read it (it is
standard-library-only and YAML needs `pyyaml`), so `maintenance/validate-contract.py`
keeps the two from drifting apart. It also checks the skills, the agents, the
documented commands, the counts above, and that nothing in a skill or agent depends on
where the plugin happens to be checked out.

## Maintaining the catalog

`maintenance/` holds everything that needs a dependency, the network or a secret: the
validators, the relevance gate, the refresh scripts and `verify.py`. It alone holds the
one dependency (`pyyaml`), the network calls, and the one secret
(`GOOGLE_FONTS_API_KEY`, see `maintenance/.env.example`). One command runs all ten gates
and stops at the first failure, printing the exact command to re-run it:

```
pip install -r maintenance/requirements.txt
python maintenance/verify.py
```

The Google Fonts and Phosphor catalogs are derived from upstream. The
`ui-design-catalog-refresh` skill fetches them, stages candidates under
`maintenance/candidates/` (gitignored), diffs them against the live rows and has the
read-only `ui-design-catalog-reviewer` agent check each one. It then stops: promoting a
candidate is an editorial decision with a licensing dimension (see `SOURCE-RESEARCH.md`)
and needs the maintainer's explicit approval.

**Run the refresh skill from a clone, not an installed copy.** Claude Code keeps each
installed version in its own cache directory and discards what was written there on the
next update, so the skill refuses to run from one. Clone this repository and start
Claude Code with `--plugin-dir` pointing at it.

## Data and licences

The catalog is derived from
[ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) by Next
Level Builder, released under the MIT licence carried in `LICENSE`. `NOTICE` lists the
upstream sources the data draws on. The origin of individual rows is recorded in
`catalog/data/data-provenance.json`.

The Google Fonts catalog holds metadata for 1,934 families, each with the licence its
`METADATA.pb` records (OFL, Apache-2.0 or Ubuntu Font Licence); it does not contain font
files. Eight families are **not** in the catalog: they are held out for licence review
because the official `google/fonts` snapshot has no metadata entry for them, and are
listed under `excludedFamilies` in `catalog/data/google-font-licenses.json`.
