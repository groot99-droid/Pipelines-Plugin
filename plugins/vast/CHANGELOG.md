# Changelog

## 0.1.1 (2026-11-19)

Fixes from the first live run (two one-hour rentals of an RTX 3090; `UNVERIFIED.md` has the results).

- `quote` and `rent` found no offer: Vast matches nothing on an `id` filter. The offer is now looked up
  by `ask_contract_id`.
- `instances` answered HTTP 410: the v0 list is retired. That one call now goes to `/api/v1/instances/`.
- The `blender` environment never installed: download.blender.org answers 403 to wget and curl. It now
  installs Blender 5.2.1 LTS from a mirror (two mirrors, then blender.org), checked against a sha256
  pinned in `recipes.json`. A failed install leaves `.blender-failed` and `logs/blender-install.log`,
  and the `ready` recipe shows them.
- A background start (`run_shell` with `background`, or a background recipe) hung for 60 s and returned
  no `job_id`, though the job ran. The job now gets its own session with stdin, stdout and stderr away
  from ssh, ssh itself reads from the null device, and a start that still times out returns the `job_id`
  with `start_confirmed: false`. Not yet tried on a live host.
- `quote` shows `disk_dph_estimate`, `dph_with_disk_estimate` and `worst_case_cost_with_disk_usd`: the
  listed price does not include the disk asked for. The band and the ledger still use the listed price.
- `verified` on an offer is read from Vast's `verification` field (it was always null).
- `search_offers` takes `min_cuda`; each environment states its `cuda`, and `quote` warns when a host
  lists less.

## 0.1.0 (2026-11-19)

- First version: the `vast` MCP server (stdlib) with offer search, quotes priced against biweekly
  per-price-band hour budgets (`limits.json`), confirm-gated renting with an on-box stop watchdog, ssh/scp
  transfer inside fixed folders, typed recipes (`recipes.json`: Blender 4.2.3 LTS, ComfyUI v0.3.10),
  background jobs, ssh tunnels, stop/destroy/reap, and a spend meter on every result.
- The `vast-gpu` skill and the `/vast-status` command.
- Not yet run against a live account (`UNVERIFIED.md`).
