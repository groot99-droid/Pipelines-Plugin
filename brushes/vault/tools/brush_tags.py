#!/usr/bin/env python3
"""Tag sidecars for the brush vault: plan the tagging, validate what the tagger
returned, write the sidecars, check them.

Standard library only. The brush-tagger subagent returns text and writes no
file; this script is the one writer under vault/_BrushTags/ (docs/CONTRACTS.md
F8 and F12) and writes nothing without --confirm.

    python -I brushes/vault/tools/brush_tags.py plan [--only SUBSTR] [--ids a,b] [--force] [--json]
    python -I brushes/vault/tools/brush_tags.py apply --file NOTE [--ids a,b] [--from FILE] [--confirm]
    python -I brushes/vault/tools/brush_tags.py check [--strict]
    python -I brushes/vault/tools/brush_tags.py suggestions [--json]

`plan` lists the brushes that have no current tag entry (or a stale one) and
batches them for the tagger by contact sheet: 8 brushes to a sheet and at most
2 sheets to a call (spec.yaml tags.sheet). `apply` reads the tagger's blocks
from a file or standard input, rejects any block that breaks a rule of F8 and
merges the rest into the sidecar of the note. Exit codes: 0 ok, 1 refused or
failed (a rejected block, a missing brush, a failed check), 2 usage or
environment.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import brush_search as bs  # noqa: E402

UsageError, NotFound = bs.UsageError, bs.NotFound

GENERATOR = "brush-tagger v1"
SIDECAR_SCHEMA = 1
SHEET_ROWS = 8                    # == spec.yaml tags.sheet.rows
SHEETS_PER_CALL = 2               # == spec.yaml tags.sheet.sheets_per_call
AXES, TAG_FIELDS, CAPS = bs.AXES, bs.TAG_FIELDS, bs.TAG_CAPS
EVIDENCE_ITEMS = ("sheet", "stroke", "shape", "grain")
BLOCK_KEYS = TAG_FIELDS + ("visual", "evidence", "notes", "suggestions")
ENTRY_KEYS = ("content_sha256", "name") + TAG_FIELDS + ("visual", "visual_basis", "evidence", "notes", "tagged",
                                                         "tagger")
LOG_BACKFILL = "_backfill_log.jsonl"
LOG_SUGGESTIONS = "_vocabulary_suggestions.jsonl"
TIME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

HEADER_RE = re.compile(r'^###\s+brush\s+(b_[0-9a-f]{12})\s*\(name:\s*"(.*)",\s*chunk\s+(\d+),\s*lines\s+(\d+)-(\d+),'
                       r'\s*fp:\s*([0-9a-f]{16})\)\s*$')
LOOSE_HEADER_RE = re.compile(r"^###\s+brush\b\s*(\S*)")
KEY_RE = re.compile("^(" + "|".join(BLOCK_KEYS) + r"):[ \t]*(.*)$")
STRAY_AXIS_RE = re.compile(r"^[a-z]+_tags:")
SUGGESTION_SPLIT_RE = re.compile(r",\s*(?=[a-z_]+:[a-z0-9-]+\s+--\s)")
SUGGESTION_RE = re.compile(r"^([a-z_]+):([a-z0-9][a-z0-9-]*)\s+--\s+(.*)$")


def utc_now():
    """The time a tagging is recorded, to the second."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ── the tagger block ─────────────────────────────────────────────────────────

def _split_tags(value):
    value = value.strip()
    if value.lower() in ("(none)", "none", ""):
        return []
    tags = []
    for item in value.split(","):
        item = item.strip().strip("`'\"").lower()
        if item and item not in tags:
            tags.append(item)
    return tags


def _split_suggestions(value):
    value = value.strip()
    if value.lower() in ("(none)", "none", ""):
        return []
    found = []
    for item in SUGGESTION_SPLIT_RE.split(value):
        item = item.strip()
        match = SUGGESTION_RE.match(item)
        if match:
            axis = match.group(1)
            axis = axis[:-5] if axis.endswith("_tags") else axis
            found.append({"axis": axis if axis in AXES else None, "suggestion": match.group(2) if axis in AXES
                          else f"{match.group(1)}:{match.group(2)}", "why": match.group(3).strip()})
        elif item:
            found.append({"axis": None, "suggestion": item, "why": ""})
    return found


def parse_tagger_blocks(text):
    """Read the tagger's reply into blocks.

    Returns (blocks, stray). A block is {"id", "name", "chunk", "lines": (a, b),
    "fp", "fields": {key: text}, "errors": [reason]}; a block with errors is
    malformed and `apply` rejects it. `stray` lists non-blank lines outside any
    block (a preamble or a code fence is dropped, other text is reported). A
    line inside a block that is not a `key:` line continues the line before it.
    """
    blocks, stray = [], []
    current, last_key = None, None
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw.strip()
        if not line or re.match(r"^`{3,}[a-z]*$", line) or re.match(r"^~{3,}[a-z]*$", line):
            continue
        header = HEADER_RE.match(line)
        if header:
            current = {"id": header.group(1), "name": header.group(2), "chunk": int(header.group(3)),
                       "lines": (int(header.group(4)), int(header.group(5))), "fp": header.group(6),
                       "fields": {}, "errors": []}
            blocks.append(current)
            last_key = None
            continue
        if line.startswith("###") and LOOSE_HEADER_RE.match(line):
            loose = LOOSE_HEADER_RE.match(line)
            current = {"id": loose.group(1) if bs.BRUSH_ID_RE.match(loose.group(1)) else None, "name": None,
                       "chunk": None, "lines": None, "fp": None, "fields": {},
                       "errors": ["malformed block header (expected: ### brush <id> (name: \"...\", chunk <n>, "
                                  "lines <a>-<b>, fp: <16 hex>))"]}
            blocks.append(current)
            last_key = None
            continue
        if current is None:
            stray.append(line)
            continue
        key = KEY_RE.match(line)
        if key:
            name = key.group(1)
            if name in current["fields"]:
                current["errors"].append(f"`{name}` appears twice")
            current["fields"][name] = key.group(2).strip()
            last_key = name
        elif STRAY_AXIS_RE.match(line):
            current["errors"].append(f"unknown line `{line.split(':', 1)[0]}` (the axes are "
                                     f"{', '.join(TAG_FIELDS)})")
        elif last_key is not None:
            current["fields"][last_key] = (current["fields"][last_key] + " " + line).strip()
        else:
            stray.append(line)
    for block in blocks:
        if block["errors"] and block["fp"] is None:
            continue
        for key in BLOCK_KEYS:
            if key not in block["fields"]:
                block["errors"].append(f"missing line `{key}:`")
    return blocks, stray


def _parse_evidence(value):
    """(previews list, error). `none` is the empty list."""
    text = value.strip().lower()
    items = [i for i in re.split(r"[,\s]+", text) if i]
    if not items:
        return None, "evidence is empty (write sheet, stroke, shape, grain, or none)"
    if items == ["none"]:
        return [], None
    bad = [i for i in items if i not in EVIDENCE_ITEMS]
    if bad:
        return None, f"evidence `{bad[0]}` is none of sheet, stroke, shape, grain, none"
    return [i for n, i in enumerate(items) if i not in items[:n]], None


# ── sidecar helpers ──────────────────────────────────────────────────────────

def _vocab(vault):
    full = bs.load_vocabulary_full(vault)
    return full, bs._vocab_tags(full), bs.vocabulary_fingerprint(full)


def _brush_sections(vault, note):
    """{brush id: section} of the brush sections of a note on disk."""
    note, path = bs._note_path(vault, note)
    if not path.is_file():
        raise UsageError(f"there is no note {note} in the vault (run notes.py write --confirm first)")
    parsed = bs.parse_note(bs.read_text(path))
    return note, {s["brush_id"]: s for s in parsed["sections"] if s["brush_id"]}, parsed


def resolve_note(vault, catalog, value):
    """A note path as given, or a set slug that the catalog gives a note."""
    value = str(value).strip().replace("\\", "/")
    if value.endswith(".md"):
        return value
    cat = bs.load_catalog_json(catalog)
    for row in cat.get("sets", []):
        if row.get("set_slug") == value and row.get("note"):
            return row["note"]
    raise UsageError(f"`{value}` is neither a note path (…/name.md) nor the slug of a set that has a note")


def _read_sidecar(vault, note):
    path = bs.sidecar_path(vault, note)
    if not path.is_file():
        return None
    try:
        data = json.loads(bs.read_text(path))
    except ValueError as err:
        raise UsageError(f"{path.name} is not valid JSON ({err}); fix or remove it by hand before applying") from None
    if not isinstance(data, dict):
        raise UsageError(f"{path.name} does not hold a JSON object")
    return data


def _append_jsonl(path, rows):
    if not rows:
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _read_jsonl(path):
    rows, errors = [], []
    path = Path(path)
    if not path.is_file():
        return rows, errors
    for number, line in enumerate(bs.read_text(path).split("\n"), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError("not an object")
            rows.append(row)
        except ValueError:
            errors.append(f"{path.name} line {number} is not a JSON object")
    return rows, errors


# ── apply ────────────────────────────────────────────────────────────────────

def validate_block(block, *, chunk, record, allowed_ids, tags_by_key, seen):
    """(entry, reasons, refused tags) for one parsed block. `entry` is None when
    the block is rejected; `reasons` says why, in the order the rules of F8
    list them."""
    reasons, refused = [], []
    if block["errors"]:
        return None, list(block["errors"]), refused
    brush_id = block["id"]
    if chunk is None:
        return None, ["the id is not a brush section of this note"], refused
    if allowed_ids is not None and brush_id not in allowed_ids:
        return None, ["the id is not in --ids"], refused
    if brush_id in seen:
        return None, ["a second block for the same id"], refused
    if record is None:
        return None, ["the id has no catalog record"], refused
    sha = record.get("content_sha256") or ""
    if block["fp"] != sha[:16]:
        reasons.append(f"fp {block['fp']} is not the brush's current fingerprint {sha[:16]} (the brush changed, "
                       "or the block is for another brush)")
    fields = block["fields"]
    tags = {}
    for key in TAG_FIELDS:
        values = _split_tags(fields[key])
        tags[key] = values
        outside = [v for v in values if v not in tags_by_key[key]]
        if outside:
            refused.extend((key[:-5], v) for v in outside)
            reasons.append(f"{key}: not in the vocabulary: {', '.join(outside)}")
        cap = CAPS[key[:-5]]
        if len(values) > cap:
            reasons.append(f"{key}: {len(values)} tags is over the cap of {cap}")
    previews, evidence_error = _parse_evidence(fields["evidence"])
    if evidence_error:
        reasons.append(evidence_error)
    visual = fields["visual"].strip()
    if visual.lower() == "(none)":
        visual = ""
    if not visual and previews:
        reasons.append("visual is empty while evidence is not none")
    if reasons:
        return None, reasons, refused
    preview = record.get("preview") or {}
    notes = fields["notes"].strip()
    entry = {"content_sha256": sha, "name": record.get("name"), **tags, "visual": visual,
             "visual_basis": bs.VISUAL_BASIS,
             "evidence": {"previews": previews, "stroke_source": preview.get("stroke_source")},
             "notes": "" if notes.lower() == "(none)" else notes}
    return entry, [], refused


def apply_blocks(vault, catalog, note, text, *, ids=None, confirm=False, now=None):
    """Validate the tagger's reply for one note and, with confirm=True, merge
    the accepted entries into the note's sidecar and append the two logs.

    Returns a report: {"file", "accepted": [id], "retagged": [id], "rejected":
    [{"id", "reason"}], "missing": [id], "suggestions": [...], "stray": [...],
    "written": bool, "dry_run": bool, "ok": bool}. Nothing is written when
    confirm is false, and nothing when no block is accepted."""
    vault, catalog = Path(vault), Path(catalog)
    note, sections, _ = _brush_sections(vault, note)
    full, tags_by_key, vocab_fp = _vocab(vault)
    if isinstance(ids, str):
        ids = [i.strip() for i in ids.split(",") if i.strip()]
    allowed = set(ids) if ids else None
    blocks, stray = parse_tagger_blocks(text)
    existing = _read_sidecar(vault, note)
    old_entries = (existing or {}).get("brushes") or {}
    accepted, rejected, suggestions, entries, seen = [], [], [], {}, set()
    stamp = now or utc_now()
    for block in blocks:
        brush_id = block["id"]
        record = None
        if brush_id and bs.BRUSH_ID_RE.match(brush_id) and (catalog / "brushes" / f"{brush_id}.json").is_file():
            record = bs.load_record(catalog, brush_id)
        entry, reasons, refused = validate_block(
            block, chunk=sections.get(brush_id), record=record, allowed_ids=allowed, tags_by_key=tags_by_key,
            seen=seen)
        if brush_id:
            seen.add(brush_id)
        name = (record or {}).get("name") or block.get("name")
        for axis, tag in refused:
            suggestions.append({"timestamp": stamp, "file": note, "brush_id": brush_id, "name": name,
                                "axis": axis, "suggestion": tag,
                                "why": "refused: the tagger used this tag but it is not in the vocabulary"})
        if entry is None:
            rejected.append({"id": brush_id, "reason": "; ".join(reasons)})
        else:
            entry["tagged"], entry["tagger"] = stamp, GENERATOR
            entries[brush_id] = entry
            accepted.append(brush_id)
        if brush_id and (entry is not None or sections.get(brush_id) is not None):
            for item in _split_suggestions(block["fields"].get("suggestions", "(none)")):
                suggestions.append({"timestamp": stamp, "file": note, "brush_id": brush_id, "name": name,
                                    "axis": item["axis"], "suggestion": item["suggestion"], "why": item["why"]})
    returned = {b["id"] for b in blocks if b["id"]}
    missing = sorted(i for i in (allowed or ()) if i not in returned)
    retagged = [i for i in accepted if i in old_entries]
    report = {"file": note, "accepted": accepted, "retagged": retagged, "rejected": rejected, "missing": missing,
              "suggestions": suggestions, "stray": stray, "blocks": len(blocks), "written": False,
              "dry_run": not confirm, "ok": bool(blocks) and not rejected and not missing}
    if not confirm:
        return report
    stamp_log = {"timestamp": stamp, "file": note, "generator": GENERATOR, "vocabulary_fingerprint": vocab_fp}
    log_rows = []
    new = [i for i in accepted if i not in old_entries]
    if new:
        log_rows.append({**stamp_log, "action": "tagged", "brush_ids": new, "count": len(new)})
    if retagged:
        log_rows.append({**stamp_log, "action": "retagged", "brush_ids": retagged, "count": len(retagged)})
    if rejected or missing:
        log_rows.append({**stamp_log, "action": "rejected", "brush_ids": [r["id"] for r in rejected if r["id"]],
                         "count": len(rejected), "rejected": rejected, "missing": missing})
    if entries:
        merged = dict(old_entries)
        merged.update(entries)
        sidecar = {"schema": SIDECAR_SCHEMA, "file": note, "generator": GENERATOR,
                   "vocabulary_fingerprint": vocab_fp, "updated": stamp, "brushes": merged}
        bs.write_text_atomic(bs.sidecar_path(vault, note), bs.json_text(sidecar))
        report["written"] = True
    base = vault / "_BrushTags"
    _append_jsonl(base / LOG_BACKFILL, log_rows)
    _append_jsonl(base / LOG_SUGGESTIONS, suggestions)
    return report


# ── plan ─────────────────────────────────────────────────────────────────────

def _sheet_cells(vault, slug):
    """{brush id: sheet file name} from _Previews/_sheets/<slug>/sheets.json, or
    None when it is absent or in a shape this reader does not know."""
    path = Path(vault) / "_Previews" / "_sheets" / slug / "sheets.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(bs.read_text(path))
        sheets = data.get("sheets") if isinstance(data, dict) else data
        mapping = {}
        for number, sheet in enumerate(sheets, start=1):
            name = sheet.get("file") or sheet.get("name") or f"sheet-{number:02d}.png"
            if not str(name).endswith(".png"):
                name = f"{name}.png"
            for cell in sheet.get("cells", []):
                mapping[cell["id"]] = str(name)
        return mapping or None
    except (OSError, ValueError, AttributeError, KeyError, TypeError):
        return None


def build_plan(vault, catalog, *, only=None, ids=None, force=False, limit=None):
    """What is left to tag, batched by contact sheet.

    Per brush whose home note is on disk: `tag` (no entry anywhere), `retag`
    (an entry whose content_sha256 differs), `force` (force asked) or
    `skip_valid`. The brushes to do are grouped by sheet (8 to a sheet, in note
    order, or as sheets.json says) and the sheets into calls of at most 2."""
    vault, catalog = Path(vault), Path(catalog)
    cat = bs.load_catalog_json(catalog)
    if isinstance(ids, str):
        ids = [i.strip() for i in ids.split(",") if i.strip()]
    wanted = set(ids) if ids else None
    records, hashes = {}, {}
    for brush_id in bs.record_ids(catalog):
        records[brush_id] = bs.load_record(catalog, brush_id)
        hashes[brush_id] = records[brush_id].get("content_sha256")
    chosen, _, _ = bs.resolve_entries(bs.read_sidecars(vault), hashes)
    plan = {"calls": [], "blocked": [], "counts": Counter(), "missing_sheets": []}
    for row in sorted((r for r in cat.get("sets", []) if r.get("note")), key=lambda r: r["note"]):
        note, slug = row["note"], row["set_slug"]
        if only and only.lower() not in note.lower():
            continue
        path = vault / note
        home = sorted((i for i, r in records.items() if (r.get("home") or {}).get("set_slug") == slug),
                      key=lambda i: ((records[i].get("home") or {}).get("position") or 0, i))
        if not path.is_file():
            pending = [i for i in home if not wanted or i in wanted]
            if pending:
                plan["blocked"].append({"file": note, "set": slug, "ids": pending,
                                        "reason": "the note is not on disk (run notes.py write --confirm)"})
                plan["counts"]["blocked"] += len(pending)
            continue
        parsed = bs.parse_note(bs.read_text(path))
        order = [s for s in parsed["sections"] if s["brush_id"] and s["brush_id"] in records]
        cells = _sheet_cells(vault, slug)
        sheets = {}
        for position, section in enumerate(order):
            brush_id = section["brush_id"]
            sheet = (cells or {}).get(brush_id) or f"sheet-{position // SHEET_ROWS + 1:02d}.png"
            sheets.setdefault(sheet, []).append(section)
        pending_by_sheet = {}
        for section in order:
            brush_id = section["brush_id"]
            if wanted and brush_id not in wanted:
                continue
            pick = chosen.get(brush_id)
            if force:
                decision = "force"
            elif pick is None:
                decision = "tag"
            elif pick["state"] == "stale":
                decision = "retag"
            else:
                decision = "skip_valid"
            plan["counts"][decision] += 1
            if decision == "skip_valid":
                continue
            sheet = next(name for name, items in sheets.items() if section in items)
            pending_by_sheet.setdefault(sheet, []).append((section, decision))
        if not pending_by_sheet:
            continue
        has_sheets = (vault / "_Previews" / "_sheets" / slug / "sheets.json").is_file()
        if not has_sheets:
            plan["missing_sheets"].append(slug)
        names = sorted(pending_by_sheet)
        for k in range(0, len(names), SHEETS_PER_CALL):
            group = names[k:k + SHEETS_PER_CALL]
            items = [pair for name in group for pair in pending_by_sheet[name]]
            plan["calls"].append({
                "call": f"{slug}#{k // SHEETS_PER_CALL + 1}", "file": note, "set": slug, "sheets": group,
                "sheets_present": has_sheets,
                "ids": [s["brush_id"] for s, _ in items],
                "names": [records[s["brush_id"]].get("name") for s, _ in items],
                "decisions": {s["brush_id"]: d for s, d in items},
                "chunks": [{"id": s["brush_id"], "chunk": s["chunk_index"], "lines": f"{s['start_line']}-{s['end_line']}",
                            "fp": (records[s["brush_id"]].get("content_sha256") or "")[:16]} for s, _ in items]})
    if limit is not None:
        plan["calls"] = plan["calls"][:limit]
    plan["counts"] = dict(sorted(plan["counts"].items()))
    plan["sheet"] = {"rows": SHEET_ROWS, "sheets_per_call": SHEETS_PER_CALL}
    plan["pending"] = sum(len(c["ids"]) for c in plan["calls"])
    return plan


# ── check ────────────────────────────────────────────────────────────────────

def check_sidecars(vault, catalog):
    """(errors, warnings, summary) over every sidecar and both logs."""
    vault, catalog = Path(vault), Path(catalog)
    errors, warnings = [], []
    try:
        full, tags_by_key, vocab_fp = _vocab(vault)
    except UsageError as err:
        return [str(err)], [], {"sidecars": 0, "entries": 0}
    sidecars = bs.read_sidecars(vault)
    hashes = {}
    have_catalog = (catalog / "catalog.json").is_file()
    if have_catalog:
        for brush_id in bs.record_ids(catalog):
            hashes[brush_id] = bs.load_record(catalog, brush_id).get("content_sha256")
    else:
        warnings.append("no catalog: stale and orphan entries were not checked")
    entries = 0
    for sc in sidecars:
        where = sc["path"]
        if sc["error"]:
            errors.append(f"{where}: not valid JSON ({sc['error']})")
            continue
        data = sc["data"]
        for key in ("schema", "file", "generator", "vocabulary_fingerprint", "updated", "brushes"):
            if key not in data:
                errors.append(f"{where}: missing key `{key}`")
        if data.get("schema") != SIDECAR_SCHEMA:
            errors.append(f"{where}: schema is {data.get('schema')!r}, not {SIDECAR_SCHEMA}")
        if data.get("file") != sc["note"]:
            errors.append(f"{where}: `file` is {data.get('file')!r}, not its own note path {sc['note']!r}")
        if "updated" in data and not (isinstance(data["updated"], str) and TIME_RE.match(data["updated"])):
            errors.append(f"{where}: `updated` is not a UTC time like 2026-01-01T00:00:00Z")
        if data.get("vocabulary_fingerprint") not in (None, vocab_fp) and "vocabulary_fingerprint" in data:
            warnings.append(f"{where}: written under another vocabulary (re-tag with --force to refresh)")
        brushes = data.get("brushes")
        if not isinstance(brushes, dict):
            errors.append(f"{where}: `brushes` is not an object")
            continue
        for brush_id in sorted(brushes):
            entry = brushes[brush_id]
            entries += 1
            label = f"{where} {brush_id}"
            if not bs.BRUSH_ID_RE.match(brush_id):
                errors.append(f"{label}: the key is not a brush id")
            if not isinstance(entry, dict):
                errors.append(f"{label}: the entry is not an object")
                continue
            for key in ENTRY_KEYS:
                if key not in entry:
                    errors.append(f"{label}: missing key `{key}`")
            if not (isinstance(entry.get("content_sha256"), str) and bs.SHA_RE.match(entry["content_sha256"])):
                errors.append(f"{label}: content_sha256 is not 64 hex characters")
            for key in TAG_FIELDS:
                values = entry.get(key)
                if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
                    errors.append(f"{label}: {key} is not a list of tags")
                    continue
                for value in values:
                    if value not in tags_by_key[key]:
                        errors.append(f"{label}: {key} holds `{value}`, which is not in the vocabulary")
                if len(values) > CAPS[key[:-5]]:
                    errors.append(f"{label}: {key} has {len(values)} tags; the cap is {CAPS[key[:-5]]}")
                if len(set(values)) != len(values):
                    errors.append(f"{label}: {key} repeats a tag")
            if entry.get("visual_basis") != bs.VISUAL_BASIS:
                errors.append(f"{label}: visual_basis is {entry.get('visual_basis')!r}, not {bs.VISUAL_BASIS!r}")
            if not isinstance(entry.get("visual"), str):
                errors.append(f"{label}: visual is not text")
            evidence = entry.get("evidence")
            if not (isinstance(evidence, dict) and isinstance(evidence.get("previews"), list)
                    and all(p in EVIDENCE_ITEMS for p in evidence["previews"])):
                errors.append(f"{label}: evidence.previews must be a list of {', '.join(EVIDENCE_ITEMS)}")
            elif isinstance(entry.get("visual"), str) and not entry["visual"] and evidence["previews"]:
                errors.append(f"{label}: visual is empty while evidence is not none")
            if "tagged" in entry and not (isinstance(entry["tagged"], str) and TIME_RE.match(entry["tagged"])):
                errors.append(f"{label}: `tagged` is not a UTC time like 2026-01-01T00:00:00Z")
    if have_catalog:
        chosen, orphans, divergent = bs.resolve_entries(sidecars, hashes)
        for brush_id in sorted(i for i, c in chosen.items() if c["state"] == "stale"):
            warnings.append(f"{chosen[brush_id]['path']} {brush_id}: stale (the brush changed since it was tagged)")
        for path, brush_id in orphans:
            warnings.append(f"{path} {brush_id}: names no brush in the catalog (orphan)")
        for brush_id in divergent:
            warnings.append(f"{brush_id}: two sidecars hold different current tags for it")
    for log in (LOG_BACKFILL, LOG_SUGGESTIONS):
        _, problems = _read_jsonl(vault / "_BrushTags" / log)
        errors.extend(problems)
    return errors, warnings, {"sidecars": len(sidecars), "entries": entries}


# ── suggestions ──────────────────────────────────────────────────────────────

def summarise_suggestions(vault):
    rows, _ = _read_jsonl(Path(vault) / "_BrushTags" / LOG_SUGGESTIONS)
    groups = {}
    for row in rows:
        key = f"{row.get('axis') or '?'}:{row.get('suggestion')}"
        group = groups.setdefault(key, {"suggestion": key, "count": 0, "brushes": [], "why": []})
        group["count"] += 1
        label = f"{row.get('brush_id')} {row.get('name')!r}"
        if label not in group["brushes"] and len(group["brushes"]) < 5:
            group["brushes"].append(label)
        if row.get("why") and row["why"] not in group["why"] and len(group["why"]) < 3:
            group["why"].append(row["why"])
    return sorted(groups.values(), key=lambda g: (-g["count"], g["suggestion"]))


# ── command line ─────────────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(prog="brush_tags.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    verbs = parser.add_subparsers(dest="verb", required=True)

    def common(p):
        p.add_argument("--vault", default=None, help="vault folder (default: ROSW_BRUSHES_VAULT, "
                                                    "ROSW_BRUSHES_ROOT/vault, or this tool's own vault)")
        p.add_argument("--catalog", default=None, help="catalog folder (default: ROSW_BRUSHES_CATALOG, "
                                                      "ROSW_BRUSHES_ROOT/catalog, or the catalog/ beside the vault)")
        p.add_argument("--json", action="store_true")

    p = verbs.add_parser("plan", help="list what is left to tag, batched by contact sheet")
    common(p)
    p.add_argument("--only", default=None, metavar="SUBSTR", help="only notes whose path contains this")
    p.add_argument("--ids", default=None, help="comma-separated brush ids")
    p.add_argument("--force", action="store_true", help="plan brushes that already have a current entry")
    p.add_argument("--limit", type=int, default=None, help="at most this many tagger calls")
    p.add_argument("--allow-no-sheets", action="store_true", dest="allow_no_sheets",
                   help="do not fail when a set's contact sheets are not built")

    p = verbs.add_parser("apply", help="validate the tagger's blocks and write the sidecar")
    common(p)
    p.add_argument("--file", required=True, metavar="NOTE", help="vault-relative note path, or a set slug")
    p.add_argument("--ids", default=None, help="comma-separated brush ids of this call; others are rejected")
    p.add_argument("--from", default=None, dest="source", metavar="FILE", help="the tagger's reply (default: standard input)")
    p.add_argument("--confirm", action="store_true", help="write the sidecar and the logs")

    p = verbs.add_parser("check", help="check every sidecar against the vocabulary and the catalog")
    common(p)
    p.add_argument("--strict", action="store_true", help="a warning is an error")

    p = verbs.add_parser("suggestions", help="the vocabulary suggestions logged so far, counted")
    common(p)
    return parser


def _roots(args):
    vault, catalog, _ = bs.resolve_roots(args.vault, args.catalog)
    return vault, catalog


def _cmd_plan(args, out, err):
    vault, catalog = _roots(args)
    plan = build_plan(vault, catalog, only=args.only, ids=args.ids, force=args.force, limit=args.limit)
    blocked = bool(plan["missing_sheets"]) and not args.allow_no_sheets
    if args.json:
        bs._emit_json(plan, out)
        return 1 if blocked else 0
    counts = plan["counts"]
    out.write("plan: " + (", ".join(f"{k}={v}" for k, v in counts.items()) or "nothing to do") + "\n")
    for call in plan["calls"]:
        out.write(f"\n{call['call']}  {call['file']}  sheets: {', '.join(call['sheets'])}"
                  f"{'' if call['sheets_present'] else '  (sheets not built)'}\n")
        for chunk, name in zip(call["chunks"], call["names"]):
            out.write(f"  {chunk['id']}  chunk {chunk['chunk']}  lines {chunk['lines']}  fp {chunk['fp']}  {name!r}"
                      f"  [{call['decisions'][chunk['id']]}]\n")
    for item in plan["blocked"]:
        out.write(f"\nblocked: {item['file']}: {len(item['ids'])} brushes, {item['reason']}\n")
    if plan["missing_sheets"]:
        out.write("\ncontact sheets are not built for: " + ", ".join(plan["missing_sheets"])
                  + "\nbuild them first: python -I brushes/pipeline/previews.py render --sheets-only --confirm\n")
    if blocked:
        err.write("error: sheets missing; do not tag blind (--allow-no-sheets to list anyway)\n")
    return 1 if blocked else 0


def _cmd_apply(args, out, err):
    vault, catalog = _roots(args)
    note = resolve_note(vault, catalog, args.file)
    if args.source:
        try:
            text = bs.read_text(args.source)
        except OSError as problem:
            raise UsageError(f"cannot read {args.source}: {problem}") from None
    else:
        text = sys.stdin.read()
    report = apply_blocks(vault, catalog, note, text, ids=args.ids, confirm=args.confirm)
    if args.json:
        bs._emit_json(report, out)
    else:
        out.write(f"{report['file']}: {report['blocks']} blocks, {len(report['accepted'])} accepted "
                  f"({len(report['retagged'])} re-tagged), {len(report['rejected'])} rejected, "
                  f"{len(report['missing'])} missing, {len(report['suggestions'])} suggestions\n")
        for item in report["rejected"]:
            out.write(f"  REJECTED {item['id']}: {item['reason']}\n")
        for brush_id in report["missing"]:
            out.write(f"  MISSING  {brush_id}: no block came back\n")
        for line in report["stray"][:5]:
            out.write(f"  stray text ignored: {line[:80]}\n")
        if report["dry_run"]:
            out.write("DRY RUN   nothing is written without --confirm.\n")
        elif report["written"]:
            out.write(f"wrote _BrushTags/{note}.tags.json and appended the logs\n")
    if not report["blocks"]:
        err.write("error: no tagger blocks found in the input\n")
    return 0 if report["ok"] else 1


def _cmd_check(args, out, err):
    vault, catalog = _roots(args)
    errors, warnings, summary = check_sidecars(vault, catalog)
    failed = bool(errors) or (args.strict and bool(warnings))
    if args.json:
        bs._emit_json({"errors": errors, "warnings": warnings, **summary, "ok": not failed}, out)
        return 1 if failed else 0
    for line in errors:
        out.write(f"ERROR   {line}\n")
    for line in warnings:
        out.write(f"WARNING {line}\n")
    out.write(f"checked {summary['sidecars']} sidecars, {summary['entries']} entries: "
              f"{len(errors)} errors, {len(warnings)} warnings"
              f"{' (warnings count as errors under --strict)' if args.strict and warnings else ''}\n")
    return 1 if failed else 0


def _cmd_suggestions(args, out, err):
    vault, _ = _roots(args)
    groups = summarise_suggestions(vault)
    if args.json:
        bs._emit_json(groups, out)
        return 0
    if not groups:
        out.write("No suggestions logged.\n")
    for group in groups:
        out.write(f"{group['count']:>3}  {group['suggestion']}\n")
        for why in group["why"]:
            out.write(f"       why: {why}\n")
        out.write("       e.g. " + "; ".join(group["brushes"]) + "\n")
    return 0


COMMANDS = {"plan": _cmd_plan, "apply": _cmd_apply, "check": _cmd_check, "suggestions": _cmd_suggestions}


def main(argv=None):
    bs._console()
    args = build_parser().parse_args(argv)
    try:
        return COMMANDS[args.verb](args, sys.stdout, sys.stderr)
    except (UsageError, NotFound) as problem:
        print(f"error: {problem}", file=sys.stderr)
        return problem.exit_code
    except BrokenPipeError:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
