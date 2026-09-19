#!/usr/bin/env python3
"""Validate and package the creative-writing pipeline into one build artifact.

Validates that the Claude Code skill is actually correctly registered
(valid SKILL.md frontmatter, every file it and spec.yaml depend on
actually exists) and, only if that passes, zips the whole pipeline --
spec, scripts, docs, and a copy of the skill -- into one portable archive
at the Pipelines repo root. Refuses to produce a zip if validation
fails: a broken
pipeline shouldn't ship as if it were a working one.

Usage:
    python build_package.py [--out PATH]
"""
import argparse
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent               # creative-writing/pipeline/
CW_DIR = HERE                                        # the pipeline's own scripts
VAULT_ROOT = HERE.parent / "vault"                   # creative-writing/vault/
REPO_ROOT = HERE.parent.parent                       # Pipelines/
# The skill and its agents live at the REPO root, not in the vault: one home,
# discovered whenever Pipelines is the working directory, and already in the
# shape a plugin wants.
SKILL_DIR = REPO_ROOT / ".claude" / "skills" / "creative-writing-pipeline"
SKILL_MD = SKILL_DIR / "SKILL.md"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"

# Subagents the skill delegates to (native drafting + native reference
# condensation) -- these live under .claude/agents/, a sibling of
# .claude/skills/, not inside the skill folder itself. Packaging must
# carry them too, or dropping just skill/ into another vault silently
# loses both.
AGENT_FILES = [
    "creative-writing-drafter.md",
    "creative-writing-librarian-native.md",
]

PIPELINE_SCRIPT_FILES = [
    "spec.yaml", "run_pipeline.py", "llm.py", "librarian.py",
    "vault_integration.py", "requirements.txt",
]
VAULT_DEPENDENCY_FILES = [
    VAULT_ROOT / "tools" / "vault_search.py",
    VAULT_ROOT / "tools" / "build_canvas.py",
    VAULT_ROOT / "CLAUDE.md",
]

DEFAULT_OUT = REPO_ROOT / "creative-writing-pipeline.zip"


class ValidationError(RuntimeError):
    pass


def validate() -> dict:
    """Check the skill is properly registered and every dependency exists.
    Raises ValidationError with a clear, specific message on any failure.
    Returns the parsed SKILL.md frontmatter on success (used for the
    manifest)."""
    errors = []

    if not SKILL_MD.exists():
        raise ValidationError(f"SKILL.md not found at {SKILL_MD} -- cannot package a skill that doesn't exist.")

    try:
        import yaml
    except ImportError as exc:
        raise ValidationError("The 'pyyaml' package is required to validate SKILL.md. Install it with: pip install pyyaml") from exc

    text = SKILL_MD.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise ValidationError(f"{SKILL_MD} has no YAML frontmatter block (must start with '---').")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValidationError(f"{SKILL_MD}'s frontmatter block is never closed with a second '---'.")
    frontmatter = yaml.safe_load(text[3:end])
    if not isinstance(frontmatter, dict):
        raise ValidationError(f"{SKILL_MD}'s frontmatter did not parse as a mapping.")

    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not name or not str(name).strip():
        errors.append(f"{SKILL_MD}: frontmatter 'name' is missing or empty.")
    elif name != SKILL_DIR.name:
        errors.append(f"{SKILL_MD}: frontmatter name '{name}' does not match its folder name '{SKILL_DIR.name}'.")
    if not description or not str(description).strip():
        errors.append(f"{SKILL_MD}: frontmatter 'description' is missing or empty.")

    for filename in PIPELINE_SCRIPT_FILES:
        path = CW_DIR / filename
        if not path.exists():
            errors.append(f"Missing pipeline file: {path}")

    readme = REPO_ROOT / "README.md"
    if not readme.exists():
        errors.append(f"Missing: {readme}")

    for filename in AGENT_FILES:
        path = AGENTS_DIR / filename
        if not path.exists():
            errors.append(f"Missing agent file the skill delegates to: {path}")
            continue
        atext = path.read_text(encoding="utf-8")
        if not atext.startswith("---"):
            errors.append(f"{path} has no YAML frontmatter block (must start with '---').")
            continue
        aend = atext.find("\n---", 3)
        if aend == -1:
            errors.append(f"{path}'s frontmatter block is never closed with a second '---'.")
            continue
        afm = yaml.safe_load(atext[3:aend])
        if not isinstance(afm, dict):
            errors.append(f"{path}'s frontmatter did not parse as a mapping.")
            continue
        if not afm.get("name") or not str(afm["name"]).strip():
            errors.append(f"{path}: frontmatter 'name' is missing or empty.")
        if not afm.get("description") or not str(afm["description"]).strip():
            errors.append(f"{path}: frontmatter 'description' is missing or empty.")
        tools = str(afm.get("tools", ""))
        forbidden = [t for t in ("Write", "Edit", "Agent") if t in [s.strip() for s in tools.split(",")]]
        if forbidden:
            errors.append(
                f"{path}: tools list grants {forbidden} -- these subagents must stay "
                f"read-only/non-delegating (no vault writes, no spawning further agents)."
            )

    for path in VAULT_DEPENDENCY_FILES:
        if not path.exists():
            errors.append(f"Missing vault dependency the pipeline relies on: {path}")

    if errors:
        raise ValidationError("Validation failed:\n" + "\n".join(f"  - {e}" for e in errors))

    return frontmatter


def _spec_version() -> str:
    try:
        import yaml
        with (CW_DIR / "spec.yaml").open("r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        return str(spec.get("version", "unknown"))
    except Exception:
        return "unknown"


def build(out_path: Path, frontmatter: dict) -> int:
    """Write the zip. Returns the number of files written."""
    count = 0
    build_time = datetime.now(timezone.utc).isoformat()

    manifest_lines = [
        "Creative-writing pipeline -- build artifact",
        f"Built: {build_time}",
        f"spec.yaml version: {_spec_version()}",
        f"Skill: {frontmatter.get('name')} -- {frontmatter.get('description')}",
        "",
        "Contents:",
        "  spec.yaml, run_pipeline.py, llm.py, librarian.py, vault_integration.py,",
        "  requirements.txt, README.md",
        "  skill/creative-writing-pipeline/SKILL.md",
        "  agents/creative-writing-drafter.md",
        "  agents/creative-writing-librarian-native.md",
        "",
        "Install:",
        "  1. Drop skill/creative-writing-pipeline/ under <repo-root>/.claude/skills/",
        "     -- the working directory Claude Code opens on, so it is discovered",
        "     there. Note the skill's paths assume the vault sits at",
        "     creative-writing/vault/ relative to that root; adjust them if your",
        "     layout differs.",
        "  2. Drop both files under agents/ into <repo-root>/.claude/agents/ --",
        "     the skill delegates its heavy generation and reference-condensation",
        "     work to these subagents and won't work correctly without them.",
        "  3. Put the rest of these files wherever the pipeline scripts should live,",
        "     and update spec.yaml's vault_root to point at your vault (it is",
        "     resolved relative to spec.yaml's own directory).",
        "  4. pip install -r requirements.txt (pyyaml always; anthropic only if you",
        "     plan to use PIPELINE_LLM_BACKEND=anthropic). Ollama is only needed for",
        "     the standalone script's default drafting backend and librarian.py --",
        "     the skill's native subagents need neither.",
    ]

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for filename in PIPELINE_SCRIPT_FILES:
            zf.write(CW_DIR / filename, filename)
            count += 1
        zf.write(REPO_ROOT / "README.md", "README.md")
        count += 1
        zf.write(SKILL_MD, "skill/creative-writing-pipeline/SKILL.md")
        count += 1
        for filename in AGENT_FILES:
            zf.write(AGENTS_DIR / filename, f"agents/{filename}")
            count += 1
        zf.writestr("MANIFEST.txt", "\n".join(manifest_lines) + "\n")
        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", default=None, help=f"Output zip path (default: {DEFAULT_OUT})")
    args = parser.parse_args()
    out_path = Path(args.out).resolve() if args.out else DEFAULT_OUT

    try:
        frontmatter = validate()
    except ValidationError as exc:
        print(f"BUILD REFUSED -- {exc}", file=sys.stderr)
        sys.exit(1)

    count = build(out_path, frontmatter)
    size_kb = out_path.stat().st_size / 1024
    print(f"Validated OK: skill '{frontmatter.get('name')}' registered, all dependencies present.")
    print(f"Wrote {out_path} ({count} files, {size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
