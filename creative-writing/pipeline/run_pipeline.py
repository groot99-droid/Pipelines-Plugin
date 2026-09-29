#!/usr/bin/env python3
"""Standalone CLI for the creative-writing pipeline.

Reads stage definitions from spec.yaml (shared with the Claude Code skill),
drafts each stage via llm.py's pluggable backend (Ollama by default,
Anthropic opt-in via PIPELINE_LLM_BACKEND=anthropic), and checkpoints after
every stage by writing state + artifacts to runs/<run-id>/ and stopping.

Reference material (worked examples, vault_search.py hits, and claimed-
connection verification) is pre-condensed by librarian.py -- always
Ollama-backed regardless of the drafting backend -- before it reaches the
drafting prompt, to keep raw vault files out of that prompt's context.

Usage:
    python run_pipeline.py new --mode essay-self-help --idea "..." [--run-id slug] [--register R ...]
    python run_pipeline.py continue <run-id> [--confirm]
    python run_pipeline.py status <run-id>

`--confirm` only matters for the final (vault_integration) stage: without
it, that stage prints a dry-run preview and does NOT write to the vault or
advance the run. See spec.yaml's vault_integration stage for what it does.
"""
import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import librarian
import llm
import plot_logic
import vault_integration as vi

HERE = Path(__file__).resolve().parent
RUNS_DIR = HERE / "runs"


# --------------------------------------------------------------------
# Spec loading
# --------------------------------------------------------------------

def load_spec() -> dict:
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(
            "The 'pyyaml' package is required to read spec.yaml. "
            "Install it with: pip install pyyaml"
        ) from exc
    with (HERE / "spec.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def vault_root_from_spec(spec: dict) -> Path:
    return (HERE / spec["vault_root"]).resolve()


def stage_by_id(spec: dict, stage_id: str) -> dict:
    for s in spec["stages"]:
        if s["id"] == stage_id:
            return s
    raise KeyError(stage_id)


EXECUTION_SYSTEM_PROMPT = (
    "You execute the instructions in the user message directly and respond with "
    "ONLY the requested output artifact. Do not restate, summarize, paraphrase, or "
    "describe the instructions themselves. Do not explain what you will do or "
    "narrate your process. Begin your response immediately with the actual content "
    "requested -- no preamble, no meta-commentary, no 'Here's what I would do' "
    "framing. Smaller/local models in particular tend to treat multi-step "
    "instructions as something to summarize back -- do not do that; carry them out "
    "and output only the result."
)


def draft(prompt: str) -> str:
    """The single call site every stage handler uses to get the drafting
    backend's output. Always sends EXECUTION_SYSTEM_PROMPT as the system
    prompt -- without it, weaker models (esp. local ones) tend to respond
    with a restatement/plan instead of actually doing the task, which is
    silently indistinguishable from a real answer unless you read it
    closely. Centralized here so every stage gets this fix uniformly."""
    return llm.generate(prompt, system=EXECUTION_SYSTEM_PROMPT)


_PLACEHOLDER_RE = re.compile(r"\{mode(?:\.(\w+))\}|\{mode\}")


def fill_template(text: str, mode_name: str, mode_cfg: dict) -> str:
    def repl(m):
        attr = m.group(1)
        if attr is None:
            return mode_name
        value = mode_cfg.get(attr, "")
        if isinstance(value, list):
            return "\n".join(f"  - {v}" for v in value)
        return str(value)
    return _PLACEHOLDER_RE.sub(repl, text)


# --------------------------------------------------------------------
# Run state
# --------------------------------------------------------------------

def slugify(text: str) -> str:
    words = re.sub(r"[^A-Za-z0-9\s]", "", text).strip().split()
    base = "-".join(w.lower() for w in words[:6]) or "untitled"
    return f"{base}-{uuid.uuid4().hex[:6]}"


def run_dir(run_id: str) -> Path:
    return RUNS_DIR / run_id


def load_state(run_id: str) -> dict:
    path = run_dir(run_id) / "state.json"
    if not path.exists():
        raise SystemExit(f"No run found at {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(run_id: str, state: dict):
    path = run_dir(run_id) / "state.json"
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def write_artifact(run_id: str, filename: str, content: str):
    (run_dir(run_id) / filename).write_text(content, encoding="utf-8")


def read_artifact(run_id: str, filename: str) -> str:
    path = run_dir(run_id) / filename
    return path.read_text(encoding="utf-8") if path.exists() else ""


# --------------------------------------------------------------------
# Stage handlers
# --------------------------------------------------------------------

def _mode_cfg(spec: dict, mode: str) -> dict:
    cfg = spec["modes"].get(mode)
    if not cfg or cfg.get("status") != "implemented":
        implemented = sorted(
            name for name, c in spec["modes"].items() if c.get("status") == "implemented"
        )
        raise SystemExit(
            f"Mode '{mode}' is not implemented in spec.yaml yet "
            f"(implemented modes: {', '.join(implemented)})."
        )
    return cfg


def handle_intake(run_id, spec, mode, idea_seed, registers=()):
    mode_cfg = _mode_cfg(spec, mode)
    stage = stage_by_id(spec, "intake")
    prompt = fill_template(stage["prompt"], mode, mode_cfg)
    if registers:
        prompt += f"\n\nRegister(s) the author chose: {', '.join(registers)}\n"
    prompt += f"\n\nRaw idea from the author:\n{idea_seed}\n"
    result = draft(prompt)
    write_artifact(run_id, "idea.md", result)
    return "idea.md written. Review it, then run `continue` to pull references."


def _extract_idea_themes(idea_text: str, vault_root: Path, limit: int = 3) -> list[str]:
    """Pull idea.md's freeform 'candidate themes' phrases (if present -- the
    intake stage asks for them, but a weaker local drafting backend doesn't
    always format them exactly as asked, so this degrades to [] rather than
    erroring) and map them onto real _ChunkTags/vocabulary.yaml context_tags
    by simple token overlap. Returns only tags that actually exist in the
    closed vocabulary -- never a raw, unmapped phrase -- so every value this
    feeds to vault_integration.search_by_tag() is guaranteed to be a real,
    queryable tag rather than one that silently matches nothing."""
    m = re.search(r"candidate themes[:\s]*(.+)", idea_text, re.IGNORECASE)
    if not m:
        return []
    raw = re.split(r"[,\n]", m.group(1))[:limit * 3]
    # Small stopword set so common conjunctions (esp. "and", which appears
    # literally inside several hyphenated vocab tags like
    # memory-and-forgetting) don't create spurious token-overlap matches.
    stopwords = {"and", "the", "of", "in", "on", "at", "to", "for", "vs",
                 "is", "as", "or", "an", "a", "not", "its", "it"}
    phrase_tokens = set()
    for r in raw:
        phrase_tokens |= {w.lower() for w in re.findall(r"[A-Za-z']+", r)
                           if len(w) > 2 and w.lower() not in stopwords}
    if not phrase_tokens:
        return []

    vocab_path = vault_root / "_ChunkTags" / "vocabulary.yaml"
    if not vocab_path.exists():
        return []
    import yaml
    with vocab_path.open("r", encoding="utf-8") as f:
        vocab = yaml.safe_load(f) or {}
    context_tags = vocab.get("context_tags", [])

    matched = []
    for tag in context_tags:
        tag_tokens = {t for t in tag.split("-") if t not in stopwords}
        overlap = tag_tokens & phrase_tokens
        # A single shared token is too loose for multi-token tags (e.g. a
        # phrase mentioning "self-knowledge" would otherwise also match
        # self-worth, self-preservation, self-deception... on "self" alone)
        # -- require every multi-token tag to match at least 2 of its own
        # tokens; single-token tags (e.g. "grief") just need that one.
        needed = min(2, len(tag_tokens))
        if len(overlap) >= needed:
            matched.append(tag)
        if len(matched) >= limit:
            break
    return matched


def handle_reference_pull(run_id, spec, mode, vault_root, registers=()):
    mode_cfg = _mode_cfg(spec, mode)
    stage = stage_by_id(spec, "reference_pull")
    idea_text = read_artifact(run_id, "idea.md")
    query = " ".join(idea_text.split()[:40])  # crude keyword query from idea.md

    # vault_search.py is a cheap index lookup, not "reading a file" -- runs
    # directly, no librarian involved.
    try:
        hits = vi.search(vault_root, query, top=5)
    except vi.VaultIntegrationError as exc:
        hits = []
        hits_note = f"(vault_search.py error, continuing without hits: {exc})"
    else:
        hits_note = ""

    # Widen the candidate pool beyond the mode's fixed worked_examples list:
    # derive a few closed-vocabulary context_tags from idea.md's candidate
    # themes and pull chunk-tagged hits for them too. This is what actually
    # fixes "always the same 3 worked examples" -- --tag search returns []
    # (not an error) for any mode/theme combination that hasn't been
    # chunk-tagged yet, so this degrades gracefully rather than failing.
    themes = _extract_idea_themes(idea_text, vault_root)
    tag_hits = []
    tag_hits_note = ""
    if themes:
        try:
            for theme in themes:
                for hit in vi.search_by_tag(vault_root, {"context": theme}, top=5):
                    if hit not in tag_hits:
                        tag_hits.append(hit)
        except vi.VaultIntegrationError as exc:
            tag_hits = []
            tag_hits_note = f"(vault_search.py --tag error, continuing without tag hits: {exc})"
    else:
        tag_hits_note = "(no candidate themes extracted from idea.md, or vocabulary.yaml not found -- skipping tag search)"

    # Compile the exact file list worth reading in full: the mode's worked
    # examples, the top few lexical search hits, and the top few tag-search
    # hits -- capped so librarian.digest_files' cost stays bounded even
    # when both hit sources are full.
    files_to_read = [f"{p}.md" for p in mode_cfg.get("worked_examples", [])]
    # A register's worked examples ride along with the mode's: a cosmic piece
    # should be grounded in Missing Campsites, not only in the mode's three.
    for name in registers:
        for p in spec["registers"][name].get("worked_examples", []):
            if f"{p}.md" not in files_to_read:
                files_to_read.append(f"{p}.md")
    for hit in hits[:5]:
        if hit["file"] not in files_to_read:
            files_to_read.append(hit["file"])
    for hit in tag_hits[:5]:
        if hit["file"] not in files_to_read:
            files_to_read.append(hit["file"])
    files_to_read = files_to_read[:12]

    digest = librarian.digest_files(
        vault_root, files_to_read, query=idea_text[:300],
        max_chars=spec.get("librarian", {}).get("max_chars_per_file", librarian.DEFAULT_MAX_CHARS_PER_FILE),
    )

    prompt = fill_template(stage["prompt"], mode, mode_cfg)
    prompt += "\n\n--- idea.md ---\n" + idea_text
    prompt += "\n\n--- vault_search.py hits (JSON, file/heading/line-range citations) ---\n" + json.dumps(hits, indent=2) + "\n" + hits_note
    prompt += "\n\n--- vault_search.py --tag hits, derived from idea.md's candidate themes (JSON) ---\n" + json.dumps(tag_hits, indent=2) + "\n" + tag_hits_note
    prompt += "\n\n--- librarian digest of worked examples + top hits ---\n" + digest

    result = draft(prompt)
    # The librarian's own quote-verification only guards its condensation
    # output -- nothing stops the drafting model from inventing a new
    # "quote" while writing references.md from that digest. Check the
    # drafted text itself against the actual source files before trusting it.
    result = librarian.verify_citations(result, vault_root, files_to_read)
    write_artifact(run_id, "references.md", result)
    return "references.md written. Review it, then run `continue` to outline."


def handle_outline(run_id, spec, mode, registers=()):
    mode_cfg = _mode_cfg(spec, mode)
    stage = stage_by_id(spec, "outline")
    registers = list(registers)
    rules = plot_logic.render_rules(spec, mode, registers)
    prompt = fill_template(stage["prompt"], mode, mode_cfg).replace("{plot_logic}", rules)
    prompt += "\n\n--- idea.md ---\n" + read_artifact(run_id, "idea.md")
    prompt += "\n\n--- references.md ---\n" + read_artifact(run_id, "references.md")
    result = draft(prompt)

    if not rules:  # this mode has no plot logic and no register asked for it
        write_artifact(run_id, "outline.md", result)
        return "outline.md written. Review it, then run `continue` to draft."

    results = plot_logic.check_text(result, spec, mode, registers)
    if not all(r["ok"] for _, r in results):
        # One automatic repair pass, in the checker's own words. The checker cannot
        # judge whether a link is TRUE, only that it is declared and anchored, so a
        # second failure is left for the author at the checkpoint.
        report = plot_logic.render_report(results, mode, registers)
        repair = (
            "The outline below failed the plot-logic checker. Rewrite the FULL outline, "
            "fixing every ERROR (and the warnings where you can) without dropping anything "
            "else that was good. Where a beat is an 'and then', either give it a real "
            "dependency on an earlier beat's Changes or cut it. Output only the corrected outline.\n\n"
            f"{rules}\n\n--- checker report ---\n{report}\n--- outline.md ---\n{result}"
        )
        fixed = draft(repair)
        fixed_results = plot_logic.check_text(fixed, spec, mode, registers)
        if sum(len(r["findings"]) for _, r in fixed_results) <= sum(len(r["findings"]) for _, r in results):
            result, results = fixed, fixed_results

    report = plot_logic.render_report(results, mode, registers)
    write_artifact(run_id, "outline.md", result)
    write_artifact(run_id, "plot_logic_report.md", report)
    passed = all(r["ok"] for _, r in results)
    return (f"outline.md written; plot logic {'PASSED' if passed else 'FAILED'} (see plot_logic_report.md).\n{report}"
            "Review both, then run `continue` to draft."
            + ("" if passed else " Fix the ledger errors first: a draft is only as causal as its outline."))


def handle_draft(run_id, spec, mode):
    mode_cfg = _mode_cfg(spec, mode)
    stage = stage_by_id(spec, "draft")
    prompt = fill_template(stage["prompt"], mode, mode_cfg)
    prompt += "\n\nVault-wide rules that always apply:\n" + "\n".join(
        f"- {r}" for r in spec.get("vault_wide_rules", []))
    prompt += "\n\n--- outline.md ---\n" + read_artifact(run_id, "outline.md")
    prompt += "\n\n--- references.md ---\n" + read_artifact(run_id, "references.md")
    result = draft(prompt)
    write_artifact(run_id, "draft.md", result)
    return "draft.md written. Review it, then run `continue` for self-revision."


_SECTION_RE = re.compile(
    r"##\s*REVISED_DRAFT\s*\n(?P<draft>.*?)\n##\s*REVISION_NOTES\s*\n(?P<notes>.*?)"
    r"(?:```json\s*(?P<json>.*?)\s*```)?\s*$",
    re.DOTALL,
)


def handle_self_revision(run_id, spec, mode, vault_root):
    mode_cfg = _mode_cfg(spec, mode)
    stage = stage_by_id(spec, "self_revision")
    prompt = fill_template(stage["prompt"], mode, mode_cfg)
    prompt += "\n\nVault-wide rules that always apply:\n" + "\n".join(
        f"- {r}" for r in spec.get("vault_wide_rules", []))
    prompt += (
        "\n\nStructure your entire response as exactly these sections, in this order, "
        "with these literal headings so it can be parsed programmatically:\n\n"
        "## REVISED_DRAFT\n<the full corrected draft text, nothing else>\n\n"
        "## REVISION_NOTES\n<the changelog: what changed and why, and anything flagged "
        "for the author to decide rather than silently resolved>\n\n"
        "Then, if the draft claims or implies any connection to an existing vault "
        'work/project, end with a fenced ```json block: '
        '{"connections_claimed": ["<short search query per claim>", ...]}. '
        'If there are no such claims, output {"connections_claimed": []}.'
    )
    prompt += "\n\n--- draft.md ---\n" + read_artifact(run_id, "draft.md")

    result = draft(prompt)

    m = _SECTION_RE.search(result)
    if m:
        revised_draft = m.group("draft").strip() + "\n"
        notes_text = m.group("notes").strip()
        json_block = m.group("json")
    else:
        # Model didn't follow the section format -- fall back to treating the
        # whole response as the draft and flag it loudly rather than silently
        # fabricating notes from unrelated text.
        revised_draft = result.strip() + "\n"
        notes_text = ("[WARNING: model response did not follow the expected "
                       "REVISED_DRAFT/REVISION_NOTES section format -- no changelog "
                       "could be extracted. Review draft_revised.md manually.]")
        json_block = None

    claims = []
    if json_block:
        try:
            claims = json.loads(json_block).get("connections_claimed", [])
        except (json.JSONDecodeError, AttributeError):
            claims = []

    librarian_max_chars = spec.get("librarian", {}).get("max_chars_per_file", librarian.DEFAULT_MAX_CHARS_PER_FILE)
    verification_lines = ["## Verification (automated, via vault_search.py + librarian)"]
    if not claims:
        verification_lines.append("No connections to existing works were claimed.")
    for claim in claims:
        try:
            hits = vi.search(vault_root, claim, top=3)
        except vi.VaultIntegrationError as exc:
            verification_lines.append(f"- \"{claim}\": search failed ({exc}) -- verify manually.")
            continue
        if not hits:
            verification_lines.append(
                f"- \"{claim}\": NO supporting hits found in the vault -- likely an invented "
                f"tie. Per CLAUDE.md, this should be cut or explicitly flagged to the author.")
            continue

        top = hits[0]
        verification_lines.append(
            f"- \"{claim}\": vault_search.py top hit is {top['file']} "
            f"(score {top['score']}, lines {top.get('start_line')}-{top.get('end_line')}). "
            f"Librarian-condensed excerpt of that file, judged against the claim:")
        try:
            excerpt = librarian.condense_file(vault_root, top["file"], query=claim, max_chars=librarian_max_chars)
        except Exception as exc:  # librarian/Ollama failure shouldn't block the whole stage
            verification_lines.append(f"  [librarian condensation failed ({exc}) -- verify {top['file']} manually.]")
        else:
            verification_lines.append("  " + excerpt.replace("\n", "\n  "))

    write_artifact(run_id, "draft_revised.md", revised_draft)
    write_artifact(run_id, "revision_notes.md", notes_text + "\n\n" + "\n".join(verification_lines) + "\n")
    return "draft_revised.md and revision_notes.md written. Review both -- check the Verification section -- then run `continue --confirm` when ready to integrate into the vault, or `continue` for a dry-run preview first."


_INTEGRATION_JSON_RE = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)


def handle_vault_integration(run_id, spec, mode, vault_root, confirm: bool, registers=()):
    mode_cfg = _mode_cfg(spec, mode)
    stage = stage_by_id(spec, "vault_integration")
    schema = spec["frontmatter_schema"]

    meta_prompt = (
        "From the materials below, produce ONLY a fenced ```json block with these keys: "
        "title, genre (list), themes (list), archetypes (list), status ('draft' or 'complete'), "
        "pov, tense, project (string, empty unless idea.md explicitly named one), "
        "index_entry_summary (one sentence, matching the style of existing _index.md entries), "
        "annotation_patterns (list of short pattern tags), "
        "annotation_body (a paragraph of genuine craft analysis of THIS piece, not templated, "
        "referencing revision_notes.md where relevant, and, if plot_logic_report.md is present, "
        "the piece's causal shape: where its buts and therefores fall, and how the protagonist's "
        "agency moves). Reuse a pattern name from an existing annotation when one truly fits, "
        "rather than coining a new one for its own sake.\n\n"
        f"frontmatter field meanings: {json.dumps(schema)}\n\n"
        "--- idea.md ---\n" + read_artifact(run_id, "idea.md") +
        "\n\n--- outline.md ---\n" + read_artifact(run_id, "outline.md") +
        "\n\n--- plot_logic_report.md ---\n" + read_artifact(run_id, "plot_logic_report.md") +
        "\n\n--- draft_revised.md ---\n" + read_artifact(run_id, "draft_revised.md") +
        "\n\n--- revision_notes.md ---\n" + read_artifact(run_id, "revision_notes.md")
    )
    meta_result = draft(meta_prompt)
    m = _INTEGRATION_JSON_RE.search(meta_result)
    if not m:
        raise SystemExit("Could not extract metadata JSON from the model response:\n" + meta_result)
    meta = json.loads(m.group(1))

    title = meta["title"]
    tags = [f"type/{mode_cfg['file_type']}", f"mode/{mode}"]
    tags += [f"theme/{t}" for t in meta.get("themes", [])]
    tags += [f"status/{meta.get('status', 'draft')}"]
    tags += [f"register/{r}" for r in registers]

    frontmatter = {
        "title": title,
        "type": mode_cfg["file_type"],
        "mode": mode,
        "genre": meta.get("genre", []),
        "status": meta.get("status", "draft"),
        "pov": meta.get("pov", ""),
        "tense": meta.get("tense", ""),
        "themes": meta.get("themes", []),
        "archetypes": meta.get("archetypes", []),
        "project": meta.get("project", ""),
        "source_volume": "",
        "source_lines": "",
        "attachments": [],
        "tags": tags,
    }
    if registers:  # recorded only when used; ordinary pieces carry no register field
        frontmatter = {**{k: v for k, v in frontmatter.items() if k != "tags"},
                       "register": list(registers), "tags": tags}
    annotation_frontmatter = {
        "title": f"Annotation — {title}",
        "type": "annotation",
        "annotates": f"[[{mode_cfg['target_folder']}/PLACEHOLDER]]",  # filled below once filename is known
        "mode": mode,
        "patterns": meta.get("annotation_patterns", []),
        "tags": ["annotation", f"mode/{mode}"] + [f"register/{r}" for r in registers],
    }

    # Draft body: strip a leading H1 if the draft already includes one, since
    # plan_integration() adds its own "# Title" line.
    draft_body = read_artifact(run_id, "draft_revised.md")
    draft_body = re.sub(r"^#\s+.+\n+", "", draft_body, count=1)

    work = vi.NewWork(
        mode=mode,
        target_folder=mode_cfg["target_folder"],
        file_type=mode_cfg["file_type"],
        title=title,
        body_markdown=draft_body,
        frontmatter=frontmatter,
        index_entry_summary=meta.get("index_entry_summary", ""),
        annotation_frontmatter=annotation_frontmatter,
        annotation_body=meta.get("annotation_body", ""),
    )
    plan = vi.plan_integration(vault_root, work)
    annotation_frontmatter["annotates"] = f"[[{mode_cfg['target_folder']}/{plan['work_path'].stem}]]"
    plan = vi.plan_integration(vault_root, work)  # recompute with corrected annotates line

    preview_lines = [f"## Vault integration plan for '{title}'", ""]
    preview_lines.append(f"- work file: {plan['work_path']}")
    preview_lines.append(f"- annotation file: {plan['annotation_path']}")
    preview_lines.append(f"- index entry in: {plan['index_path']}")
    preview_lines.append(f"  {plan['index_line']}")
    if plan["warnings"]:
        preview_lines.append("\nWarnings:")
        preview_lines += [f"- {w}" for w in plan["warnings"]]
    write_artifact(run_id, "integration_plan.md", "\n".join(preview_lines))

    log = vi.apply_integration(vault_root, plan, dry_run=not confirm)
    if confirm:
        log.append(vi.reindex(vault_root, dry_run=False))
        if mode_cfg.get("target_folder") or frontmatter.get("project"):
            log.append(vi.rebuild_canvas(vault_root, dry_run=False))
    else:
        log.append(vi.reindex(vault_root, dry_run=True))

    write_artifact(run_id, "integration_log.txt", "\n".join(log))
    status_msg = "APPLIED to the vault." if confirm else "DRY-RUN only -- nothing written. Re-run `continue --confirm` to apply."
    return f"Vault integration {status_msg}\nSee {run_dir(run_id) / 'integration_plan.md'} and integration_log.txt."


# --------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------

STAGE_ORDER = ["intake", "reference_pull", "outline", "draft", "self_revision", "vault_integration"]


def run_stage(stage_id: str, run_id: str, spec: dict, state: dict, vault_root: Path, confirm: bool) -> str:
    """Dispatch a single stage. Raises on failure -- callers decide how that
    affects run state (see _run_and_advance)."""
    mode = state["mode"]
    registers = state.get("registers", [])
    if stage_id == "intake":
        return handle_intake(run_id, spec, mode, state["idea_seed"], registers)
    if stage_id == "reference_pull":
        return handle_reference_pull(run_id, spec, mode, vault_root, registers)
    if stage_id == "outline":
        return handle_outline(run_id, spec, mode, registers)
    if stage_id == "draft":
        return handle_draft(run_id, spec, mode)
    if stage_id == "self_revision":
        return handle_self_revision(run_id, spec, mode, vault_root)
    if stage_id == "vault_integration":
        return handle_vault_integration(run_id, spec, mode, vault_root, confirm=confirm, registers=registers)
    raise SystemExit(f"Unknown stage '{stage_id}'")


def _run_and_advance(run_id: str, spec: dict, state: dict, stage_id: str, confirm: bool):
    """Run one stage and, only on success, mark it complete and persist state.
    A failed stage leaves state untouched so `continue <run-id>` retries the
    same stage rather than skipping it or corrupting progress."""
    vault_root = vault_root_from_spec(spec)
    try:
        msg = run_stage(stage_id, run_id, spec, state, vault_root, confirm)
    except (llm.LLMError, vi.VaultIntegrationError) as exc:
        print(f"Error running stage '{stage_id}': {exc}", file=sys.stderr)
        print(f"Nothing was advanced. Fix the issue above, then retry with:\n"
              f"  python run_pipeline.py continue {run_id}"
              + ("" if stage_id != "vault_integration" else " [--confirm]"),
              file=sys.stderr)
        raise SystemExit(1)

    if stage_id == "vault_integration" and not confirm:
        print(msg)
        return  # dry-run preview only -- don't mark complete/advance

    state["completed_stages"].append(stage_id)
    state["next_stage_index"] += 1
    save_state(run_id, state)
    print(msg)


def cmd_new(args):
    spec = load_spec()
    _mode_cfg(spec, args.mode)  # validates mode is implemented
    try:
        plot_logic.register_cfgs(spec, args.register)  # validates every register name
    except plot_logic.ConfigError as exc:
        raise SystemExit(str(exc))

    run_id = args.run_id or slugify(args.idea)
    d = run_dir(run_id)
    if d.exists():
        raise SystemExit(f"Run '{run_id}' already exists at {d}")
    d.mkdir(parents=True)

    state = {
        "run_id": run_id, "mode": args.mode, "idea_seed": args.idea,
        "registers": list(dict.fromkeys(args.register)),
        "created": datetime.now(timezone.utc).isoformat(),
        "completed_stages": [], "next_stage_index": 0,
    }
    save_state(run_id, state)
    print(f"Run '{run_id}' created at {d}")
    _run_and_advance(run_id, spec, state, "intake", confirm=False)


def cmd_continue(args):
    spec = load_spec()
    state = load_state(args.run_id)

    if state["next_stage_index"] >= len(STAGE_ORDER):
        print("This run has already completed all stages.")
        return

    stage_id = STAGE_ORDER[state["next_stage_index"]]
    _run_and_advance(args.run_id, spec, state, stage_id, confirm=args.confirm)


def cmd_status(args):
    state = load_state(args.run_id)
    print(json.dumps(state, indent=2))
    idx = state["next_stage_index"]
    next_stage = STAGE_ORDER[idx] if idx < len(STAGE_ORDER) else "(complete)"
    print(f"\nNext stage: {next_stage}")
    print(f"Run directory: {run_dir(args.run_id)}")


def build_arg_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_new = sub.add_parser("new", help="Start a new pipeline run (runs the intake stage).")
    p_new.add_argument("--mode", required=True)
    p_new.add_argument("--idea", required=True)
    p_new.add_argument("--run-id", default=None)
    p_new.add_argument("--register", action="append", default=[],
                       help="Overlay on the mode (liminal, psychedelic, cosmic); repeatable. "
                            "See spec.yaml registers:.")
    p_new.set_defaults(func=cmd_new)

    p_continue = sub.add_parser("continue", help="Run the next stage of an existing run.")
    p_continue.add_argument("run_id")
    p_continue.add_argument("--confirm", action="store_true",
                             help="Only meaningful for the vault_integration stage: actually write to the vault.")
    p_continue.set_defaults(func=cmd_continue)

    p_status = sub.add_parser("status", help="Show a run's current state.")
    p_status.add_argument("run_id")
    p_status.set_defaults(func=cmd_status)

    return parser


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    RUNS_DIR.mkdir(exist_ok=True)
    parser = build_arg_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
