#!/usr/bin/env python3
"""Plot-logic checker: the causal spine of the pipeline's outline stage.

The rule is "but / therefore, never and-then": between any two plot beats there
is either a BUT (this beat defeats what the last one left behind) or a
THEREFORE (this beat happens because of it). "And then" means the second beat
did not need the first.

An outline carries a "Causal ledger": one Markdown table, one row per beat.

    | # | Link | Because       | Beat                 | Response | Changes            |
    |---|------|---------------|----------------------|----------|--------------------|
    | 1 | open | -             | Lamp dims early.     | denies   | He logs, not looks |
    | 2 | B    | 1 "logs"      | A page he didn't ... | denies   | Entry, no memory   |

`Because` is `<id> "<phrase>"`: the earlier beat this one depends on, and a
phrase copied from that beat's `Changes`. The checker verifies the phrase is
really there, the way librarian.py verifies quotes. It also checks the chain's
shape (runs of B with no T, runs of T with no B, beats that change nothing) and,
when a register is active, that the register's state track moves the way the
register says. What it cannot do is judge whether a link is TRUE; that stays
with the author at the checkpoint. What it can do is make an unearned link
impossible to hide.

Both consumers of spec.yaml (run_pipeline.py and the Claude Code skill) read the
same `plot_logic:` and `registers:` blocks through this module.

Usage:
    python plot_logic.py check OUTLINE.md [--mode MODE] [--register R ...] [--json]
    python plot_logic.py rules --mode MODE [--register R ...]
    python plot_logic.py template [--register R ...]

Exit codes:
    0 -- every ledger checked has no errors (warnings may remain)
    1 -- at least one ledger has an error, or a file has no ledger
    2 -- bad usage or config (unknown mode/register, unreadable file)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent

LINK_ALIASES = {
    "open": "open", "origin": "open", "start": "open", "o": "open",
    "t": "T", "therefore": "T", "so": "T",
    "b": "B", "but": "B", "however": "B",
    "a": "A", "and then": "A", "and-then": "A", "andthen": "A",
}
NO_VALUE = {"", "-", "–", "—", "n/a", "na", "none", "nothing", "nil"}


# --------------------------------------------------------------------
# Spec access
# --------------------------------------------------------------------

def load_spec() -> dict:
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - same message run_pipeline gives
        raise SystemExit(
            "The 'pyyaml' package is required to read spec.yaml. "
            "Install it with: pip install pyyaml"
        ) from exc
    with (HERE / "spec.yaml").open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class ConfigError(ValueError):
    pass


def mode_policy(spec: dict, mode: str | None) -> dict:
    """The plot_logic block of a mode, merged over the defaults. A mode of None
    (a ledger checked with no mode named) gets the defaults and no ending rule."""
    base = dict(spec["plot_logic"]["defaults"])
    if mode is None:
        return {**base, "enabled": True, "ending": None}
    cfg = spec["modes"].get(mode)
    if cfg is None:
        raise ConfigError(f"unknown mode '{mode}' (known: {', '.join(spec['modes'])})")
    pl = cfg.get("plot_logic") or {}
    return {**base, "enabled": pl.get("enabled", False), "ending": pl.get("ending"),
            "note": pl.get("note", "")} | {k: v for k, v in pl.items() if k in base}


def register_cfgs(spec: dict, names: list[str]) -> list[tuple[str, dict]]:
    out = []
    for n in names:
        if n not in spec["registers"]:
            raise ConfigError(f"unknown register '{n}' (known: {', '.join(spec['registers'])})")
        out.append((n, spec["registers"][n]))
    return out


# --------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------

@dataclass
class Row:
    n: int
    link: str                      # open | T | B | A | "" (unparsable)
    because: list[int]
    handle: str
    beat: str
    changes: str
    response: str = ""
    tracks: dict = field(default_factory=dict)   # column name (lower) -> value (lower)
    line: int = 0


@dataclass
class Ledger:
    title: str
    rows: list[Row]
    ending: str = ""
    mode: str | None = None
    registers: list[str] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    expect: str = ""               # "pass" | "fail": what a demonstration ledger in a vault note should do
    line: int = 0


@dataclass
class Finding:
    level: str                     # error | warn | info
    code: str
    row: int | None
    message: str

    def as_dict(self) -> dict:
        return {"level": self.level, "code": self.code, "row": self.row, "message": self.message}


# --------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_ENDING_RE = re.compile(r"^\W*(?:ending)\W*[:=]\s*[*_`]*\s*([A-Za-z][A-Za-z-]*)", re.I)
_MODE_RE = re.compile(r"^\W*mode\W*[:=]\s*[*_`]*\s*([A-Za-z][A-Za-z-]*)", re.I)
_REGISTER_RE = re.compile(r"^\W*registers?\W*[:=]\s*(.+)$", re.I)
_EXPECT_RE = re.compile(r"^\W*expect\W*[:=]\s*[*_`]*\s*(pass|fail)", re.I)


def _clean(cell: str) -> str:
    return cell.replace("\\|", "|").strip()


def _split_row(line: str) -> list[str]:
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [_clean(c) for c in re.split(r"(?<!\\)\|", body)]


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in cells if c != "")


def _strip_marks(s: str) -> str:
    return re.sub(r"[*_`]", "", s).strip()


def _norm(text: str) -> str:
    """Lowercase, straighten quotes, drop punctuation, collapse whitespace. The
    handle match is deliberately forgiving about typography and strict about words."""
    t = text.lower().replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    t = re.sub(r"[^a-z0-9'\s-]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def parse_because(cell: str) -> tuple[list[int], str]:
    """`3 "weather front"`, `4+5 the strait`, `2: gull`, `-` -> ([ids], handle)."""
    c = _strip_marks(cell)
    if _norm(c) in NO_VALUE:
        return [], ""
    m = re.match(r"^\s*(\d+(?:\s*[+,&/]\s*\d+)*)\s*[:—–\-]?\s*(.*)$", c)
    if not m:
        return [], c.strip().strip("\"'“”")
    ids = [int(x) for x in re.findall(r"\d+", m.group(1))]
    handle = m.group(2).strip().strip("\"'“”").strip()
    return ids, handle


def parse_ledgers(text: str, heading: str = "Causal ledger") -> list[Ledger]:
    lines = text.splitlines()
    starts = []
    for i, ln in enumerate(lines):
        m = _HEADING_RE.match(ln)
        if m and m.group(2).lower().startswith(heading.lower()):
            starts.append((i, len(m.group(1)), m.group(2)))
    ledgers: list[Ledger] = []
    for i, level, title in starts:
        end = len(lines)
        for j in range(i + 1, len(lines)):
            m = _HEADING_RE.match(lines[j])
            if m and len(m.group(1)) <= level:
                end = j
                break
        ledgers.append(_parse_section(lines, i, end, title))
    return ledgers


def _parse_section(lines: list[str], start: int, end: int, title: str) -> Ledger:
    ledger = Ledger(title=title, rows=[], line=start + 1)
    table_lines: list[tuple[int, str]] = []
    prose: list[str] = []
    table_done = False
    for i in range(start + 1, end):
        ln = lines[i]
        if ln.strip().startswith("|") and not table_done:
            table_lines.append((i, ln))
            continue
        if table_lines:
            table_done = True          # only the first contiguous table is the ledger
        prose.append(ln)
    for ln in prose:
        s = ln.strip()
        if m := _ENDING_RE.match(s):
            ledger.ending = m.group(1).lower()
        elif m := _MODE_RE.match(s):
            ledger.mode = m.group(1).lower()
        elif m := _EXPECT_RE.match(s):
            ledger.expect = m.group(1).lower()
        elif m := _REGISTER_RE.match(s):
            ledger.registers = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z-]*", _strip_marks(m.group(1)))
                                if t.lower() not in {"and", "none"}]
    if not table_lines:
        return ledger

    header_cells = _split_row(table_lines[0][1])
    ledger.columns = [_strip_marks(c).lower() for c in header_cells]
    idx = {name: k for k, name in enumerate(ledger.columns)}
    for lineno, raw in table_lines[1:]:
        cells = _split_row(raw)
        if _is_separator(cells):
            continue
        cells += [""] * (len(ledger.columns) - len(cells))

        def get(name: str) -> str:
            k = idx.get(name)
            return cells[k] if k is not None and k < len(cells) else ""

        n_txt = _strip_marks(get("#"))
        try:
            n = int(re.match(r"\d+", n_txt).group(0))   # type: ignore[union-attr]
        except (AttributeError, ValueError):
            n = -1
        link = LINK_ALIASES.get(_norm(_strip_marks(get("link"))), "")
        ids, handle = parse_because(get("because"))
        tracks = {name: _norm(_strip_marks(cells[k])) for name, k in idx.items()
                  if name not in {"#", "link", "because", "beat", "changes", "response"} and k < len(cells)}
        ledger.rows.append(Row(
            n=n, link=link, because=ids, handle=handle, beat=get("beat"),
            changes=get("changes"), response=_norm(_strip_marks(get("response"))),
            tracks=tracks, line=lineno + 1))
    return ledger


# --------------------------------------------------------------------
# Checking
# --------------------------------------------------------------------

def _has_value(s: str) -> bool:
    return _norm(_strip_marks(s)) not in NO_VALUE


def check_ledger(ledger: Ledger, spec: dict, mode: str | None = None,
                 registers: list[str] | None = None) -> dict:
    """Returns {"ok", "findings", "stats"}. `mode`/`registers` given here are
    merged with the ones the ledger declares for itself."""
    mode = mode or ledger.mode
    regs = list(dict.fromkeys((registers or []) + ledger.registers))
    findings: list[Finding] = []

    def add(level, code, row, msg):
        findings.append(Finding(level, code, row, msg))

    policy = mode_policy(spec, mode)
    reg_cfgs = register_cfgs(spec, regs)
    pl = spec["plot_logic"]
    rows = ledger.rows

    # A register is an explicit opt-in to structure, so it switches the ledger on even
    # for a mode (an essay, a poem) that would not ask for one.
    if not policy.get("enabled", True) and not reg_cfgs:
        return {"ok": True, "findings": [Finding("info", "not-applicable", None,
                f"plot logic is switched off for mode '{mode}'.")], "stats": {}}

    # ---- structure ---------------------------------------------------
    missing = [c for c in pl["columns"]["required"] if c.lower() not in ledger.columns]
    if not rows and not ledger.columns:
        add("error", "no-ledger", None, "no causal ledger table found under the 'Causal ledger' heading.")
        return _result(findings, rows)
    if missing:
        add("error", "columns", None, f"ledger is missing required column(s): {', '.join(missing)}.")
        return _result(findings, rows)
    if not rows:
        add("error", "no-rows", None, "the ledger table has a header but no rows.")
        return _result(findings, rows)

    by_n = {r.n: r for r in rows}
    for k, r in enumerate(rows, start=1):
        if r.n != k:
            add("error", "row-number", r.n, f"rows must be numbered 1..N in order; row {k} is numbered {r.n}.")
            break

    max_and_then = policy.get("max_and_then", 0)
    a_seen = 0
    callbacks = 0
    for r in rows:
        where = r.n
        if r.link == "":
            add("error", "link-invalid", where,
                "Link must be one of open, T (therefore), B (but), A (and then).")
            continue
        if where == 1 and r.link != "open":
            add("error", "first-not-open", where, "row 1 starts a thread, so its Link must be 'open'.")
        if r.link == "open":
            if r.because:
                add("error", "open-because", where, "an 'open' row depends on nothing; leave Because empty (-).")
            continue

        # T / B / A
        if r.link == "A":
            a_seen += 1
            over = a_seen > max_and_then
            add("error" if over else "warn", "and-then", where,
                f"and-then (budget {max_and_then}): the swap test says this beat did not need the one before it. "
                "What in the previous beat's Changes does it push on? Make it a T or a B, or cut it.")
            if r.because:
                add("warn", "and-then-because", where, "an A row names a Because; if it depends on it, it is a T or a B.")
            continue

        if not r.because:
            add("error", "because-missing", where,
                f"a {r.link} row must say which earlier beat it depends on: Because = <id> \"<phrase from that beat's Changes>\".")
            continue
        bad = [b for b in r.because if b >= where or b not in by_n]
        if bad:
            add("error", "because-invalid", where, f"Because names beat(s) {bad}, which are not earlier beats.")
            continue
        if any(b < where - 1 for b in r.because):
            callbacks += 1
        if not r.handle:
            add("warn", "handle-missing", where,
                "no phrase after the id, so nothing shows what this beat pushes on. Quote a phrase from the cited beat's Changes.")
            continue
        h = _norm(r.handle)
        if not h:
            add("warn", "handle-missing", where, "the Because phrase has no words in it; quote a phrase from the cited beat's Changes.")
            continue
        in_changes = any(h in _norm(by_n[b].changes) for b in r.because)
        in_beat = any(h in _norm(by_n[b].beat) for b in r.because)
        if not in_changes and not in_beat:
            cited = " and ".join(f"#{b}" for b in r.because)
            add("error", "handle-not-found", where,
                f"the phrase \"{r.handle}\" is not in {cited}. Copy a phrase that appears in the cited beat's Changes; "
                "if you cannot find one, the link is not anchored.")
        elif not in_changes:
            add("warn", "handle-weak", where,
                f"\"{r.handle}\" is in the cited beat's Beat but not its Changes. A beat should push on what the earlier "
                "beat CHANGED, not on what merely happened in it.")

    # ---- shape --------------------------------------------------------
    links = [r.link for r in rows]
    if len(rows) >= 4:
        if "B" not in links:
            add("warn", "no-but", None, "no B anywhere: nothing ever goes against the protagonist, so nothing is at risk.")
        if "T" not in links:
            add("warn", "no-therefore", None, "no T anywhere: no consequence follows from anything the protagonist does.")
    run_b = run_t = 0
    for r in rows:
        run_b = run_b + 1 if r.link == "B" else 0
        run_t = run_t + 1 if r.link == "T" else 0
        if run_b == policy["max_pile_on"]:
            add("warn", "pile-on", r.n,
                f"{run_b} B beats in a row with no T between: complications with no response are a catalogue in disguise. "
                "Let the protagonist do something (even shelving it) that the next beat must break.")
        if run_t == policy["max_smooth_run"]:
            add("warn", "smooth-run", r.n,
                f"{run_t} T beats in a row with no B: every step works. Where does something push back?")
    seen_changes: dict[str, int] = {}
    for r in rows:
        if not _has_value(r.changes):
            add("warn", "no-change", r.n, "Changes is empty: a beat that leaves nothing different is a treadmill step.")
            continue
        key = _norm(r.changes)
        if key in seen_changes:
            add("warn", "repeat-change", r.n, f"Changes repeats beat {seen_changes[key]}'s: the story did not move.")
        else:
            seen_changes[key] = r.n
    if len(rows) >= 5 and callbacks == 0:
        add("info", "no-callback", None,
            "every link cites the beat directly before it. Outlines that pay off an early beat late (foreshadow, then payoff) usually read as designed.")

    # ---- response column -----------------------------------------------
    if "response" in ledger.columns:
        valid = set(pl["responses"])
        for r in rows:
            if r.response and r.response not in NO_VALUE and r.response not in valid:
                add("error", "response-invalid", r.n,
                    f"Response '{r.response}' is not one of: {', '.join(valid)}.")

    # ---- ending ---------------------------------------------------------
    ending_rule = policy.get("ending")
    if not ledger.ending:
        add("error", "ending-missing", None,
            f"declare how it ends under the table: 'Ending: <{' | '.join(pl['endings'])}>'.")
    elif ledger.ending not in pl["endings"]:
        add("error", "ending-unknown", None, f"Ending '{ledger.ending}' is not one of: {', '.join(pl['endings'])}.")
    else:
        if ending_rule and ledger.ending not in ending_rule["allowed"]:
            add(ending_rule.get("severity", "warn"), "ending-mode", None,
                f"Ending '{ledger.ending}' is not allowed in {mode} (allowed: {', '.join(ending_rule['allowed'])}).")
        if reg_cfgs and not any(ledger.ending in c.get("endings", []) for _, c in reg_cfgs):
            names = " / ".join(n for n, _ in reg_cfgs)
            union = sorted({e for _, c in reg_cfgs for e in c.get("endings", [])})
            add("warn", "ending-register", None,
                f"Ending '{ledger.ending}' is not one the {names} register normally earns ({', '.join(union)}).")

    # ---- registers --------------------------------------------------------
    for name, cfg in reg_cfgs:
        _check_register(name, cfg, ledger, rows, add)

    return _result(findings, rows)


def _check_register(name: str, cfg: dict, ledger: Ledger, rows: list[Row], add) -> None:
    track = cfg.get("track")
    if track:
        col = track["column"].lower()
        levels = track["levels"]
        rank = {lv: i for i, lv in enumerate(levels)}
        if col not in ledger.columns:
            add("error", "track-column", None,
                f"the {name} register needs a '{track['column']}' column with values from: {', '.join(levels)}.")
        else:
            vals = []
            for r in rows:
                v = r.tracks.get(col, "")
                if v not in rank:
                    add("error", "track-value", r.n, f"{track['column']} '{v}' is not one of: {', '.join(levels)}.")
                    vals.append(None)
                else:
                    vals.append(rank[v])
            good = [(r, rank[r.tracks[col]]) for r in rows if r.tracks.get(col) in rank]
            if good:
                first = good[0][0].tracks[col]
                if track.get("start") and first not in track["start"]:
                    add("warn", "track-start", good[0][0].n,
                        f"{track['column']} starts at '{first}'; the {name} register starts at {' or '.join(track['start'])}.")
                for (r0, a), (r1, b) in zip(good, good[1:]):
                    if track.get("monotone") and b < a:
                        add("error", "track-monotone", r1.n,
                            f"{track['column']} falls from '{levels[a]}' to '{levels[b]}': in the {name} register this can only rise. "
                            "What was known cannot be un-known; if the protagonist denies it, that goes in Response, not here.")
                    mj = track.get("max_jump")
                    if mj is not None and b - a > mj:
                        skipped = ", ".join(levels[a + 1:b])
                        add("warn", "track-jump", r1.n,
                            f"{track['column']} jumps '{levels[a]}' to '{levels[b]}', skipping {skipped}. The skipped rung is usually where the dread lived.")
                for lv in track.get("must_include", []):
                    if not any(rank[r.tracks[col]] == rank[lv] for r, _ in good):
                        add("error", "track-must-include", None,
                            f"the {name} register needs at least one row with {track['column']} = '{lv}'.")
                floor = track.get("end_at_least")
                if floor and good[-1][1] < rank[floor]:
                    add("error", "track-end", good[-1][0].n,
                        f"the story ends with {track['column']} = '{levels[good[-1][1]]}'; the {name} register needs at least '{floor}'.")

    turn = cfg.get("turn")
    exp = cfg.get("expect_response")
    if (turn or exp) and "response" not in ledger.columns:
        add("warn", "response-column", None, f"the {name} register checks the protagonist's moves; add a Response column.")
        return
    if turn and track:
        col = track["column"].lower()
        levels = track["levels"]
        rank = {lv: i for i, lv in enumerate(levels)}
        floor = rank[turn["after_level"]]
        peak_at = next((i for i, r in enumerate(rows) if rank.get(r.tracks.get(col, ""), -1) >= floor), None)
        if peak_at is not None and not any(r.response in turn["response_in"] for r in rows[peak_at:]):
            add(turn.get("severity", "warn"), "turn", rows[peak_at].n, turn["message"])
    if exp:
        for resp, rule in exp.items():
            if not any(r.response == resp for r in rows):
                add(rule.get("severity", "warn"), f"no-{resp}", None, rule["message"])


def _result(findings: list[Finding], rows: list[Row]) -> dict:
    order = {"error": 0, "warn": 1, "info": 2}
    findings = sorted(findings, key=lambda f: (order[f.level], f.row if f.row is not None else -1))
    counts = {k: sum(1 for r in rows if r.link == k) for k in ("open", "T", "B", "A")}
    return {"ok": not any(f.level == "error" for f in findings), "findings": findings,
            "stats": {"rows": len(rows), "links": counts}}


def check_text(text: str, spec: dict, mode: str | None = None,
               registers: list[str] | None = None) -> list[tuple[Ledger, dict]]:
    ledgers = parse_ledgers(text, spec["plot_logic"]["ledger_heading"])
    if not ledgers:
        return [(Ledger(title="(none)", rows=[]),
                 {"ok": False, "stats": {}, "findings": [Finding(
                     "error", "no-ledger", None,
                     f"no '## {spec['plot_logic']['ledger_heading']}' section found. The outline must end with one.")]})]
    return [(lg, check_ledger(lg, spec, mode, registers)) for lg in ledgers]


# --------------------------------------------------------------------
# Rendering: rules for prompts, skeleton for humans, report for stdout
# --------------------------------------------------------------------

def render_rules(spec: dict, mode: str, registers: list[str] | None = None) -> str:
    """The block injected into the outline prompt. Empty when the mode has plot
    logic switched off, so the same prompt text serves every mode."""
    policy = mode_policy(spec, mode)
    regs = register_cfgs(spec, registers or [])
    if not policy.get("enabled") and not regs:
        return ""
    pl = spec["plot_logic"]
    cols = ["#", "Link", "Because", "Beat", "Response"]
    cols += [c["track"]["column"] for _, c in regs if c.get("track")]
    cols += ["Changes"]
    out = [
        f"PLOT LOGIC. End the outline with a section headed \"## {pl['ledger_heading']}\": ONE Markdown table, one row per plot beat, "
        f"with exactly these columns in this order: | {' | '.join(cols)} |",
        "Between any two beats there is a BUT or a THEREFORE, never an AND THEN. Link values:",
    ]
    for k in ("open", "T", "B", "A"):
        ln = pl["links"][k]
        out.append(f"  {k} ({ln['word']}): {ln['meaning']}" + (f" Test: {ln['test']}" if ln.get("test") else ""))
    out += [
        f"Because = <id of the earlier beat> \"<a phrase copied word-for-word from THAT beat's Changes>\". Several parents: 4+5 \"the strait\". "
        f"The checker verifies the phrase is really there. Use '-' for an open row. Budget: {policy['max_and_then']} A row(s).",
        "Changes = what is now irreversibly different after the beat (the ratchet). Never empty, never repeated.",
        "Response = what the protagonist does about it, one of: " + ", ".join(pl["responses"]) + ".",
    ]
    for name, c in regs:
        t = c.get("track")
        if t:
            out.append(f"{t['column']} ({name}): one of {' < '.join(t['levels'])}"
                       + ("; may only rise" if t.get("monotone") else "")
                       + f"; starts at {' or '.join(t.get('start', []))}"
                       + (f"; must reach at least '{t['end_at_least']}'" if t.get("end_at_least") else "")
                       + (f"; must include '{', '.join(t['must_include'])}'" if t.get("must_include") else "") + ".")
    allowed = (policy.get("ending") or {}).get("allowed") or list(pl["endings"])
    out.append(f"Under the table write 'Ending: <one of {', '.join(allowed)}>'"
               + (" (this mode's rule; anything else is rejected)." if (policy.get("ending") or {}).get("severity") == "error" else "."))
    if policy.get("note"):
        out.append("Mode note: " + " ".join(str(policy["note"]).split()))
    for name, c in regs:
        out.append(f"Register {name}: " + " ".join(c["summary"].split()) + "\n" + _indent(c["guidance"]))
    return "\n".join(out)


def _indent(text: str, pad: str = "  ") -> str:
    return "\n".join(pad + ln if ln.strip() else ln for ln in text.strip().splitlines())


def render_template(spec: dict, registers: list[str] | None = None) -> str:
    pl = spec["plot_logic"]
    regs = register_cfgs(spec, registers or [])
    cols = ["#", "Link", "Because", "Beat", "Response"] + [c["track"]["column"] for _, c in regs if c.get("track")] + ["Changes"]
    rows = [f"## {pl['ledger_heading']}", "",
            "| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    first = ["1", "open", "-", "", ""] + [""] * (len(cols) - 6) + [""]
    rows.append("| " + " | ".join(first) + " |")
    second = ["2", "B", '1 "phrase from #1\'s Changes"', "", ""] + [""] * (len(cols) - 6) + [""]
    rows.append("| " + " | ".join(second) + " |")
    rows += ["", "Ending: "]
    if registers:
        rows.insert(1, f"Register: {', '.join(registers)}")
    return "\n".join(rows) + "\n"


def render_report(results: list[tuple[Ledger, dict]], mode: str | None, registers: list[str]) -> str:
    out = []
    for ledger, res in results:
        errs = [f for f in res["findings"] if f.level == "error"]
        warns = [f for f in res["findings"] if f.level == "warn"]
        st = res["stats"]
        head = f"plot-logic: {'PASS' if res['ok'] else 'FAIL'}  ({len(errs)} error(s), {len(warns)} warning(s))"
        ctx = [f"mode={ledger.mode or mode or '-'}"]
        regs = list(dict.fromkeys(registers + ledger.registers))
        ctx.append(f"registers={','.join(regs) or '-'}")
        out.append(f"{head}  [{ledger.title}]  " + " ".join(ctx))
        if st:
            ln = st["links"]
            out.append(f"  rows={st['rows']}  open={ln['open']} therefore={ln['T']} but={ln['B']} and-then={ln['A']}")
        for f in res["findings"]:
            tag = {"error": "ERROR", "warn": "warn ", "info": "info "}[f.level]
            loc = f"row {f.row}" if f.row is not None else "ledger"
            out.append(f"  {tag} {loc:<7} {f.code}: {f.message}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


# --------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------

def _cmd_check(args) -> int:
    spec = load_spec()
    try:
        text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
        results = check_text(text, spec, args.mode, args.register)
    except (OSError, ConfigError) as exc:
        print(f"plot_logic: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps([{"title": lg.title, "ok": r["ok"], "stats": r["stats"],
                           "findings": [f.as_dict() for f in r["findings"]]} for lg, r in results], indent=2))
    else:
        print(render_report(results, args.mode, args.register), end="")
    return 0 if all(r["ok"] for _, r in results) else 1


def _cmd_rules(args) -> int:
    try:
        print(render_rules(load_spec(), args.mode, args.register))
    except ConfigError as exc:
        print(f"plot_logic: {exc}", file=sys.stderr)
        return 2
    return 0


def _cmd_template(args) -> int:
    try:
        print(render_template(load_spec(), args.register), end="")
    except ConfigError as exc:
        print(f"plot_logic: {exc}", file=sys.stderr)
        return 2
    return 0


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    c = sub.add_parser("check", help="Check every causal ledger in a file ('-' reads stdin).")
    c.add_argument("file")
    c.add_argument("--mode", default=None)
    c.add_argument("--register", action="append", default=[], help="repeatable")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=_cmd_check)

    r = sub.add_parser("rules", help="Print the rules block that goes into the outline prompt.")
    r.add_argument("--mode", required=True)
    r.add_argument("--register", action="append", default=[])
    r.set_defaults(func=_cmd_rules)

    t = sub.add_parser("template", help="Print an empty ledger skeleton.")
    t.add_argument("--register", action="append", default=[])
    t.set_defaults(func=_cmd_template)
    return p


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    args = build_arg_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
