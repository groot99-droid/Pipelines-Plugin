"""Helpers for stage 6 (vault integration): shells out to the vault's own
tools/vault_search.py for search + reindexing (no reimplementation of its
TF-IDF logic), and writes/patches frontmatter, the folder _index.md, and the
companion annotation file per CLAUDE.md's existing Maintenance procedure.

Every write helper here supports dry_run=True (the default) so a scripted
run can preview exactly what would change before touching the real vault.
"""
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


class VaultIntegrationError(RuntimeError):
    pass


# --------------------------------------------------------------------
# vault_search.py subprocess helpers
# --------------------------------------------------------------------

def _tools_dir(vault_root: Path) -> Path:
    return vault_root / "tools"


def search(vault_root: Path, query: str, top: int = 5) -> list[dict]:
    """Run `vault_search.py search --json` and return the parsed results."""
    import json

    script = _tools_dir(vault_root) / "vault_search.py"
    if not script.exists():
        raise VaultIntegrationError(f"vault_search.py not found at {script}")
    result = subprocess.run(
        [sys.executable, str(script), "search", query, "--top", str(top), "--json"],
        cwd=vault_root, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        raise VaultIntegrationError(f"vault_search.py search failed:\n{result.stderr}")
    return json.loads(result.stdout or "[]")


def search_by_tag(vault_root: Path, tag_filters: dict, top: int = 8) -> list[dict]:
    """Run `vault_search.py search --tag field=value ...` (no lexical query)
    and return the parsed results. `tag_filters` maps short field names
    (plot/context/mood/motif) to a single value each -- e.g.
    {"context": "isolation"} -- mirroring the CLI's own --tag FIELD=VALUE
    syntax. Returns [] (not an error) if a mode's works haven't been
    chunk-tagged yet -- --tag search degrades gracefully to no hits rather
    than failing the stage."""
    import json

    script = _tools_dir(vault_root) / "vault_search.py"
    if not script.exists():
        raise VaultIntegrationError(f"vault_search.py not found at {script}")
    args = [sys.executable, str(script), "search", "--top", str(top), "--json"]
    for field, value in tag_filters.items():
        args += ["--tag", f"{field}={value}"]
    result = subprocess.run(
        args, cwd=vault_root, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        raise VaultIntegrationError(f"vault_search.py search --tag failed:\n{result.stderr}")
    return json.loads(result.stdout or "[]")


def reindex(vault_root: Path, dry_run: bool = True) -> str:
    if dry_run:
        return "[dry-run] would run: python tools/vault_search.py index"
    script = _tools_dir(vault_root) / "vault_search.py"
    result = subprocess.run(
        [sys.executable, str(script), "index"],
        cwd=vault_root, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        raise VaultIntegrationError(f"vault_search.py index failed:\n{result.stderr}")
    return result.stdout


def rebuild_canvas(vault_root: Path, dry_run: bool = True) -> str:
    script = _tools_dir(vault_root) / "build_canvas.py"
    if not script.exists():
        return "[skip] tools/build_canvas.py not found"
    if dry_run:
        return "[dry-run] would run: python tools/build_canvas.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=vault_root, capture_output=True, text=True, encoding="utf-8",
    )
    if result.returncode != 0:
        raise VaultIntegrationError(f"build_canvas.py failed:\n{result.stderr}")
    return result.stdout


# --------------------------------------------------------------------
# Filename / frontmatter rendering
# --------------------------------------------------------------------

_NUMBERED_FILE_RE = re.compile(r"^(\d{2})_")


def next_numbered_filename(folder: Path, title: str) -> str:
    """Match the vault's existing `NN_Title_With_Underscores.md` convention."""
    max_n = 0
    if folder.exists():
        for p in folder.glob("*.md"):
            m = _NUMBERED_FILE_RE.match(p.name)
            if m:
                max_n = max(max_n, int(m.group(1)))
    n = max_n + 1
    slug = re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")
    return f"{n:02d}_{slug}.md"


def _yaml_scalar(value) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(_yaml_list_item(v) for v in value) + "]"
    s = str(value)
    if s == "" or any(c in s for c in ':#"\'') or s != s.strip():
        return f"\"{s}\""
    return s


def _yaml_list_item(v) -> str:
    s = str(v)
    return f'"{s}"' if any(c in s for c in ",[]\"") else s


def render_frontmatter(fields: dict) -> str:
    """Render an ordered dict of frontmatter fields as a `---`-delimited block,
    matching the vault's existing style (see 11_Essays/02_The_Architecture_of_Being.md).

    A field whose value is an empty *string* is omitted entirely, matching the
    vault's own convention of dropping unset scalar fields (e.g. existing
    works with no `project` tie simply have no `project:` line) rather than
    writing them out blank. Empty *lists* (e.g. `archetypes: []`) are kept,
    since that's how the vault represents "field applies, nothing to list."
    """
    lines = ["---"]
    for key, value in fields.items():
        if value == "":
            continue
        lines.append(f"{key}: {_yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


@dataclass
class NewWork:
    mode: str
    target_folder: str          # e.g. "11_Essays"
    file_type: str               # e.g. "essay"
    title: str
    body_markdown: str           # the finished draft body, below the "# Title" line
    frontmatter: dict            # full frontmatter_schema-shaped dict
    index_entry_summary: str     # one-line summary for the folder's _index.md
    annotation_frontmatter: dict
    annotation_body: str
    filename: str = ""           # filled in by plan_integration if empty
    warnings: list = field(default_factory=list)


def plan_integration(vault_root: Path, work: NewWork) -> dict:
    """Compute every file that stage 6 would write/modify, without writing
    anything. Returns a dict describing the planned changes -- used for both
    the dry-run preview and (with dry_run=False) as the basis for the actual
    write in apply_integration().
    """
    folder = vault_root / work.target_folder
    ann_folder = vault_root / "_Annotations" / work.target_folder
    filename = work.filename or next_numbered_filename(folder, work.title)

    work_path = folder / filename
    ann_path = ann_folder / filename
    index_path = folder / "_index.md"

    work_content = (
        render_frontmatter(work.frontmatter)
        + "\n# " + work.title + "\n\n"
        + work.body_markdown.strip() + "\n"
    )
    annotation_content = (
        render_frontmatter(work.annotation_frontmatter)
        + "\nWikilink back to [[" + f"{work.target_folder}/{filename[:-3]}|{work.title}" + "]].\n\n"
        + work.annotation_body.strip() + "\n"
    )
    index_line = (
        f"- [[{work.target_folder}/{filename[:-3]}|{work.title}]] — "
        f"{work.index_entry_summary} → annotation: "
        f"[[_Annotations/{work.target_folder}/{filename[:-3]}|notes]]"
    )

    warnings = list(work.warnings)
    if work_path.exists():
        warnings.append(f"{work_path} already exists -- would overwrite.")
    if not index_path.exists():
        warnings.append(f"{index_path} does not exist -- would need to be created.")

    return {
        "work_path": work_path,
        "work_content": work_content,
        "annotation_path": ann_path,
        "annotation_content": annotation_content,
        "index_path": index_path,
        "index_line": index_line,
        "warnings": warnings,
    }


def apply_integration(vault_root: Path, plan: dict, dry_run: bool = True) -> list[str]:
    """Write the files described by plan_integration(). Returns a log of
    actions taken (or, if dry_run, actions that would be taken)."""
    log = []

    def write(path: Path, content: str):
        if dry_run:
            log.append(f"[dry-run] would write {path} ({len(content)} chars)")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        log.append(f"wrote {path}")

    def append_line(path: Path, line: str):
        if dry_run:
            log.append(f"[dry-run] would append to {path}: {line}")
            return
        if not path.exists():
            raise VaultIntegrationError(f"{path} does not exist -- refusing to create a new _index.md silently.")
        with path.open("a", encoding="utf-8") as f:
            f.write(("\n" if not path.read_text(encoding="utf-8").endswith("\n") else "") + line + "\n")
        log.append(f"appended to {path}: {line}")

    write(plan["work_path"], plan["work_content"])
    write(plan["annotation_path"], plan["annotation_content"])
    append_line(plan["index_path"], plan["index_line"])

    return log
