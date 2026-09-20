#!/usr/bin/env python3
"""Validate that ui-design's declared contract matches its code, skills and data.

ui-design/spec.yaml declares what catalog/scripts/core.py implements (domains,
stacks, formats, defaults). This is the check that stops that declaration from
being decorative. It also checks that:

  - both skills and the agent are registered correctly (frontmatter keys, name
    equals its folder or file name, the agent grants no write or delegation tool);
  - every file spec.yaml and the skills reference exists;
  - the live counts each carrier repeats (SKILL.md, README.md) are current;
  - every documented search.py command uses only real flags, domains and
    stacks, and a --persist example always passes --output-dir;
  - catalog/ still imports only the standard library;
  - the repo .gitignore still guards the persist and staging directories;
  - three locked semantic examples and two exit codes still behave as promised.

Usage:
    python ui-design/maintenance/validate-contract.py

Exit codes:
    0 -- the contract holds
    1 -- one or more checks failed (each is listed on stderr)
    2 -- environment problem (pyyaml missing, spec.yaml unreadable, Python < 3.10)
"""
import argparse
import ast
import csv
import json
import os
import re
import shlex
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

TOOL_ROOT = Path(__file__).resolve().parents[1]      # ui-design/
REPO_ROOT = TOOL_ROOT.parent                         # Pipelines/
SPEC = TOOL_ROOT / "spec.yaml"
CATALOG_SCRIPTS = TOOL_ROOT / "catalog" / "scripts"
DATA = TOOL_ROOT / "catalog" / "data"
SEARCH_PY = CATALOG_SCRIPTS / "search.py"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
AGENTS_DIR = REPO_ROOT / ".claude" / "agents"
GITIGNORE = REPO_ROOT / ".gitignore"

OWNED_PREFIX = "ui-design-"          # every skill and agent this tool owns
GUIDE_SKILL = "ui-design-catalog"    # the one whose commands and counts are linted

SKILL_KEYS = {"name", "description"}
AGENT_KEYS = {"name", "description", "tools"}
# The reviewer only reads and reports; the caller decides what gets promoted.
AGENT_FORBIDDEN_TOOLS = ("Write", "Edit", "Agent", "Bash", "NotebookEdit")

# Gitignored scratch directories (see the repo .gitignore). A path under one is
# a legitimate reference even though it does not exist in a fresh clone.
STAGING_DIRS = {"candidates", "captures"}
# A tripwire, not a cache: validate_data.py fails while it exists. Ignoring it
# would hide a partial refresh.
TRIPWIRE_FILE = ".google-font-refresh.incomplete.json"

GUIDE_REQUIREMENTS = (
    "## Query Contract", "one dominant intent", "Retry once",
    "Do not persist unverified output", "explicit accessibility outcome terms",
)
PYTHON_COMMAND = re.compile(r"python(3?)\s")      # group 1 is the version suffix, if any
SEARCH_COMMAND = re.compile(r"search\.py")
QUOTED_QUERY = re.compile(r'search\.py\s+"[^"]+"')
DOMAIN_FLAG = re.compile(r"--domain\s+(\S+)")
STACK_FLAG = re.compile(r"--stack\s+(\S+)")
PATH_REFERENCE = re.compile(r"(?:ui-design|\.claude)/[A-Za-z0-9_./*<>-]*[A-Za-z0-9_>/]")
SPEC_KEYS = (
    "catalog_root", "entry_point", "stdlib_only", "domains", "stacks", "dials",
    "formats", "default_max_results", "dtcg_extension_key", "exit_codes",
    "persistence", "counts_contract", "consumers",
)


class EnvironmentProblem(Exception):
    """The contract cannot be checked at all -- reported as exit 2."""


def rel(path):
    return Path(path).resolve().relative_to(REPO_ROOT).as_posix()


def load_yaml():
    try:
        import yaml
    except ImportError as exc:
        raise EnvironmentProblem(
            "The 'pyyaml' package is required to validate spec.yaml and the "
            "skill frontmatter. Install it with: pip install pyyaml") from exc
    return yaml


def load_spec(yaml):
    try:
        with SPEC.open("r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
    except OSError as exc:
        raise EnvironmentProblem(f"Cannot read {SPEC}: {exc}") from exc
    if not isinstance(spec, dict):
        raise EnvironmentProblem(f"{SPEC} did not parse as a mapping.")
    return spec


def load_catalog_modules():
    sys.path.insert(0, str(CATALOG_SCRIPTS))
    import core
    import tokens
    return core, tokens


@lru_cache(maxsize=None)
def row_count(name):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


@lru_cache(maxsize=1)
def style_counts():
    with (DATA / "styles.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return {
        "searchable": sum(row.get("Status") != "deprecated" for row in rows),
        "active": sum(row.get("Status") == "active" for row in rows),
    }


def count_claims(stack_total):
    """The live counts every carrier must repeat, derived from catalog/data/."""
    styles = style_counts()
    return (
        f"{styles['searchable']} searchable styles ({styles['active']} active)",
        f"{row_count('colors.csv')} product palettes",
        f"{row_count('typography.csv')} font pairings",
        f"{row_count('ux-guidelines.csv')} UX guidelines",
        f"{row_count('icons.csv')} curated icons",
        f"{row_count('motion.csv')} GSAP presets",
        f"{row_count('charts.csv')} chart types",
        f"{stack_total} technology stacks",
    )


def search_cli():
    """Flags and --format choices declared by search.py's argparse calls.

    Read from the source rather than --help: help output is wrapped to the
    terminal width and would make the flag set depend on it. search.py builds
    its parser under __main__, so it cannot be imported to ask.
    """
    tree = ast.parse(SEARCH_PY.read_text(encoding="utf-8"), filename=str(SEARCH_PY))
    flags = {"-h", "--help"}
    formats = None
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"):
            continue
        names = [arg.value for arg in node.args
                 if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
                 and arg.value.startswith("-")]
        flags.update(names)
        if "--format" in names:
            for keyword in node.keywords:
                if keyword.arg == "choices" and isinstance(keyword.value, (ast.List, ast.Tuple)):
                    formats = [el.value for el in keyword.value.elts if isinstance(el, ast.Constant)]
    return flags, formats


def run_search(*args):
    return subprocess.run(
        [sys.executable, str(SEARCH_PY), *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        env={**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )


def run_json(errors, label, *args):
    done = run_search(*args, "--json")
    if done.returncode != 0:
        errors.append(f"{label}: search.py exited {done.returncode}: {done.stderr.strip()[:200]}")
        return None
    try:
        return json.loads(done.stdout)
    except ValueError as exc:
        errors.append(f"{label}: search.py --json did not emit JSON ({exc})")
        return None


def parse_frontmatter(yaml, path, errors):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append(f"{rel(path)}: no YAML frontmatter block (must start with '---').")
        return None
    end = text.find("\n---", 3)
    if end == -1:
        errors.append(f"{rel(path)}: frontmatter block is never closed with a second '---'.")
        return None
    frontmatter = yaml.safe_load(text[3:end])
    if not isinstance(frontmatter, dict):
        errors.append(f"{rel(path)}: frontmatter did not parse as a mapping.")
        return None
    return frontmatter


def check_keys(path, frontmatter, expected, errors):
    if set(frontmatter) != expected:
        errors.append(f"{rel(path)}: frontmatter keys are {sorted(frontmatter)}, "
                      f"expected exactly {sorted(expected)}.")
    for key in ("name", "description"):
        value = frontmatter.get(key)
        if not value or not str(value).strip():
            errors.append(f"{rel(path)}: frontmatter '{key}' is missing or empty.")


def check_spec(spec, core, tokens, flags, formats, errors):
    for key in SPEC_KEYS:
        if key not in spec:
            errors.append(f"spec.yaml: missing key '{key}'.")

    def same(key, declared, actual, what):
        declared = list(declared or [])
        if len(declared) != len(set(declared)):
            errors.append(f"spec.yaml {key}: contains duplicates.")
        extra, missing = sorted(set(declared) - set(actual)), sorted(set(actual) - set(declared))
        if extra:
            errors.append(f"spec.yaml {key}: declares {extra}, which {what} does not have.")
        if missing:
            errors.append(f"spec.yaml {key}: does not declare {missing}, which {what} has.")

    same("domains", spec.get("domains"), core.CSV_CONFIG.keys(), "core.CSV_CONFIG")
    same("stacks", spec.get("stacks"), core.AVAILABLE_STACKS, "core.AVAILABLE_STACKS")
    same("stacks", spec.get("stacks"), {p.stem for p in (DATA / "stacks").glob("*.csv")},
         "catalog/data/stacks/")
    if formats is None:
        errors.append("search.py: could not read the --format choices from its argparse calls.")
    else:
        same("formats", spec.get("formats"), formats, "search.py --format")
    if spec.get("default_max_results") != core.MAX_RESULTS:
        errors.append(f"spec.yaml default_max_results: {spec.get('default_max_results')!r} "
                      f"!= core.MAX_RESULTS {core.MAX_RESULTS!r}.")
    if spec.get("dtcg_extension_key") != tokens.EXTENSION_KEY:
        errors.append(f"spec.yaml dtcg_extension_key: {spec.get('dtcg_extension_key')!r} "
                      f"!= tokens.EXTENSION_KEY {tokens.EXTENSION_KEY!r}.")
    for dial in spec.get("dials") or []:
        if f"--{dial}" not in flags:
            errors.append(f"spec.yaml dials: search.py has no --{dial} flag.")
    for code in ("ok", "contrast_gate", "usage"):
        if not isinstance((spec.get("exit_codes") or {}).get(code), int):
            errors.append(f"spec.yaml exit_codes: '{code}' must be an integer.")


def check_files_exist(spec, errors):
    stdlib = spec.get("stdlib_only") or {}
    paths = [spec.get("catalog_root"), spec.get("entry_point"), stdlib.get("root"),
             stdlib.get("exception"), *(spec.get("consumers") or []),
             *((spec.get("counts_contract") or {}).get("carriers") or [])]
    for path in paths:
        if not path or not (REPO_ROOT / path).exists():
            errors.append(f"spec.yaml: referenced path does not exist: {path!r}")


def check_path_references(path, errors):
    """Every repo path a skill or the agent cites must exist."""
    for match in sorted(set(PATH_REFERENCE.findall(path.read_text(encoding="utf-8")))):
        if any(ch in match for ch in "<>*"):
            continue                                   # placeholder or glob
        if STAGING_DIRS & set(Path(match).parts):
            continue                                   # gitignored staging
        if not (REPO_ROOT / match).exists():
            errors.append(f"{rel(path)}: references {match}, which does not exist.")


def check_skills(yaml, stack_total, errors):
    skills = sorted(SKILLS_DIR.glob(f"{OWNED_PREFIX}*/SKILL.md"))
    for path in skills:
        frontmatter = parse_frontmatter(yaml, path, errors)
        if frontmatter is None:
            continue
        check_keys(path, frontmatter, SKILL_KEYS, errors)
        if frontmatter.get("name") != path.parent.name:
            errors.append(f"{rel(path)}: frontmatter name {frontmatter.get('name')!r} "
                          f"does not match its folder name {path.parent.name!r}.")
        # The guide's description names the stack count; it is the one number
        # in any description, so it is checked rather than left to rot.
        if path.parent.name == GUIDE_SKILL and f"{stack_total} stacks" not in str(
                frontmatter.get("description", "")):
            errors.append(f"{rel(path)}: description does not state the live stack count "
                          f"({stack_total} stacks).")
        check_path_references(path, errors)
    return skills


def check_agents(yaml, errors):
    agents = sorted(AGENTS_DIR.glob(f"{OWNED_PREFIX}*.md"))
    for path in agents:
        frontmatter = parse_frontmatter(yaml, path, errors)
        if frontmatter is None:
            continue
        check_keys(path, frontmatter, AGENT_KEYS, errors)
        if frontmatter.get("name") != path.stem:
            errors.append(f"{rel(path)}: frontmatter name {frontmatter.get('name')!r} "
                          f"does not match its file name {path.stem!r}.")
        tools = frontmatter.get("tools", "")
        granted = [str(t).strip() for t in (tools if isinstance(tools, list) else str(tools).split(","))]
        forbidden = [t for t in AGENT_FORBIDDEN_TOOLS if t in granted]
        if forbidden:
            errors.append(f"{rel(path)}: tools list grants {forbidden} -- this agent must stay "
                          f"read-only and non-delegating; the caller decides what is promoted.")
        check_path_references(path, errors)
    return agents


def check_counts(spec, stack_total, errors):
    product_counts = {
        "products": row_count("products.csv"),
        "palettes": row_count("colors.csv"),
        "reasoning profiles": row_count("ui-reasoning.csv"),
    }
    if len(set(product_counts.values())) != 1:
        errors.append(f"product/palette/reasoning counts differ: {product_counts}")
    claims = count_claims(stack_total)
    for carrier in (spec.get("counts_contract") or {}).get("carriers") or []:
        path = REPO_ROOT / carrier
        if not path.is_file():
            continue                                   # check_files_exist reports it
        text = path.read_text(encoding="utf-8")
        for claim in claims:
            if claim not in text:
                errors.append(f"{carrier}: missing live count claim {claim!r}")
    return len(claims)


def validate_commands(label, text, domains, stacks, flags, entry_point, errors):
    commands = []
    for line in text.splitlines():
        command = line.strip()
        if PYTHON_COMMAND.match(command) and SEARCH_COMMAND.search(command):
            commands.append(command)
    if not commands:
        errors.append(f"{label}: no documented search commands found")
    for command in commands:
        if PYTHON_COMMAND.match(command).group(1):
            errors.append(f"{label}: the house command is `python`, not a versioned one: {command}")
        if not QUOTED_QUERY.search(command):
            errors.append(f"{label}: query must immediately follow search.py: {command}")
        try:
            tokens = shlex.split(command.replace("[", "").replace("]", ""))
        except ValueError as exc:
            errors.append(f"{label}: invalid shell command ({exc}): {command}")
            continue
        script = next((t for t in tokens if t.endswith("search.py")), None)
        if script != entry_point:
            errors.append(f"{label}: command must run {entry_point}, not {script}: {command}")
        unknown_flags = sorted({t for t in tokens if t.startswith("-") and t not in flags})
        if unknown_flags:
            errors.append(f"{label}: unknown flags {unknown_flags}: {command}")
        domain = DOMAIN_FLAG.search(command)
        if domain and domain.group(1) not in set(domains) | {"<domain>"}:
            errors.append(f"{label}: unknown domain {domain.group(1)!r}")
        stack = STACK_FLAG.search(command)
        if stack and stack.group(1) not in set(stacks) | {"<stack>"}:
            errors.append(f"{label}: unknown stack {stack.group(1)!r}")
        if "--persist" in command and "--output-dir" not in command:
            errors.append(f"{label}: persisted command lacks --output-dir")
    return len(commands)


def check_stdlib_only(spec, errors):
    stdlib = getattr(sys, "stdlib_module_names", None)
    if stdlib is None:
        raise EnvironmentProblem("Python 3.10 or newer is required (sys.stdlib_module_names).")
    root = REPO_ROOT / spec["stdlib_only"]["root"]
    files = sorted(root.rglob("*.py"))
    local = {path.stem for path in files}              # flat sibling modules, no packages
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name.split(".")[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                modules = [node.module.split(".")[0]]
            else:
                continue
            for module in modules:
                if module not in stdlib and module not in local:
                    errors.append(f"{rel(path)}:{node.lineno}: imports {module!r}, which is not "
                                  f"standard library. catalog/ is stdlib-only; move the code "
                                  f"to maintenance/.")
    return len(files)


def check_gitignore(spec, errors):
    lines = {line.strip() for line in GITIGNORE.read_text(encoding="utf-8").splitlines()}
    dir_name = (spec.get("persistence") or {}).get("dir_name", "design-system")
    for pattern in (f"{dir_name}/", "candidates/", "captures/"):
        if pattern not in lines:
            errors.append(f".gitignore: missing the bare pattern {pattern!r}.")
    if TRIPWIRE_FILE in lines:
        errors.append(f".gitignore: must not ignore {TRIPWIRE_FILE}; validate_data.py treats "
                      f"its presence as a failure signal for a partial refresh.")


def check_locked_examples(spec, errors):
    design = run_json(errors, "design-system example", "beauty spa wellness service", "--design-system")
    if design is not None and design["design_system"]["category"] != "Beauty/Spa/Wellness Service":
        errors.append("design-system example resolved wrong product category")
    ux = run_json(errors, "focused UX example", "keyboard focus modal", "--domain", "ux")
    if ux is not None and (ux.get("domain") != "ux" or not ux.get("results")):
        errors.append("focused UX example did not return an explicit UX match")
    stack = run_json(errors, "React Native stack example", "virtualized list", "--stack", "react-native")
    if stack is not None and (stack.get("stack") != "react-native" or not stack.get("results")):
        errors.append("React Native stack example did not return a stack match")

    codes = spec.get("exit_codes") or {}
    empty = run_search("zzzqqq nonexistent", "--domain", "ux", "--json")
    if empty.returncode != codes.get("ok"):
        errors.append(f"an empty result set exited {empty.returncode}, spec.yaml exit_codes.ok "
                      f"is {codes.get('ok')!r}")
    bad = run_search("x", "--domain", "nosuchdomain")
    if bad.returncode != codes.get("usage"):
        errors.append(f"an unknown domain exited {bad.returncode}, spec.yaml exit_codes.usage "
                      f"is {codes.get('usage')!r}")


def validate():
    """Return (errors, summary). Raises EnvironmentProblem when nothing can be checked."""
    errors = []
    yaml = load_yaml()
    spec = load_spec(yaml)
    core, tokens = load_catalog_modules()
    flags, formats = search_cli()

    check_spec(spec, core, tokens, flags, formats, errors)
    check_files_exist(spec, errors)
    skills = check_skills(yaml, len(core.AVAILABLE_STACKS), errors)
    agents = check_agents(yaml, errors)
    claims = check_counts(spec, len(core.AVAILABLE_STACKS), errors)

    guide = SKILLS_DIR / GUIDE_SKILL / "SKILL.md"
    commands = 0
    if guide.is_file():
        text = guide.read_text(encoding="utf-8")
        for phrase in GUIDE_REQUIREMENTS:
            if phrase not in text:
                errors.append(f"{rel(guide)}: missing {phrase!r}")
        commands = validate_commands(rel(guide), text, core.CSV_CONFIG, core.AVAILABLE_STACKS,
                                     flags, spec.get("entry_point"), errors)
    else:
        errors.append(f"{rel(guide)}: the guide skill does not exist.")

    modules = check_stdlib_only(spec, errors)
    check_gitignore(spec, errors)
    check_locked_examples(spec, errors)

    summary = (f"{len(core.CSV_CONFIG)} domains, {len(core.AVAILABLE_STACKS)} stacks, "
               f"{len(skills)} skills, {len(agents)} agent, {commands} documented commands, "
               f"{claims} count claims per carrier, {modules} stdlib-only modules, "
               f"3 locked examples, 2 exit codes")
    return errors, summary


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    argparse.ArgumentParser(description=__doc__,
                            formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    try:
        errors, summary = validate()
    except EnvironmentProblem as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(2)
    if errors:
        print("Contract validation failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        sys.exit(1)
    print(f"Contract validation passed: {summary}.")


if __name__ == "__main__":
    main()
