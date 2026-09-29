#!/usr/bin/env python3
"""Validate that ui-design's declared contract matches its code, skills and data.

spec.yaml declares what catalog/scripts/core.py implements (domains, stacks,
formats, defaults). This is the check that stops that declaration from being
decorative. It also checks that:

  - every ui-design skill and agent is registered correctly (frontmatter keys,
    name equals its folder or file name, no agent grants a write or delegation
    tool; spec.yaml agent_tool_exceptions may grant Bash, and only Bash, to a
    named agent whose body states that it never persists and never writes);
  - the skills and agents are portable: every path they cite starts from
    ${CLAUDE_PLUGIN_ROOT} and exists, no frontmatter carries a path or a
    variable (only the body is substituted), and nothing names the Pipelines
    repo, its root, or a .claude/ folder, none of which exist once installed;
  - every file spec.yaml and the skills reference exists;
  - the live counts each carrier repeats (SKILL.md, README.md) are current;
  - every documented search.py command uses only real flags, domains and
    stacks, and a --persist example always passes --output-dir;
  - catalog/ still imports only the standard library;
  - the plugin's own .gitignore guards the persist and staging directories, and
    its .gitattributes still pins every file to LF (the relevance gate
    fingerprints raw bytes);
  - the plugin manifest, marketplace entry, changelog version and release files
    (LICENSE, NOTICE, README.md, CHANGELOG.md) agree and exist;
  - three locked semantic examples and two exit codes still behave as promised.

Everything is relative to the plugin root, the directory that holds
.claude-plugin/plugin.json: plugins/ui-design/ in the Pipelines monorepo, the
repository root in the published plugin.

Usage:
    python maintenance/validate-contract.py     # from the plugin root, or give the path

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

TOOL_ROOT = Path(__file__).resolve().parents[1]      # the plugin root
SPEC = TOOL_ROOT / "spec.yaml"
CATALOG_SCRIPTS = TOOL_ROOT / "catalog" / "scripts"
DATA = TOOL_ROOT / "catalog" / "data"
SEARCH_PY = CATALOG_SCRIPTS / "search.py"
SKILLS_DIR = TOOL_ROOT / "skills"
AGENTS_DIR = TOOL_ROOT / "agents"
GITIGNORE = TOOL_ROOT / ".gitignore"
GITATTRIBUTES = TOOL_ROOT / ".gitattributes"
PLUGIN_JSON = TOOL_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = TOOL_ROOT / ".claude-plugin" / "marketplace.json"
CHANGELOG = TOOL_ROOT / "CHANGELOG.md"
RELEASE_FILES = ("LICENSE", "NOTICE", "README.md", "CHANGELOG.md")

# How a skill or agent body names the plugin's install directory. Claude Code
# substitutes it in the Markdown body only, never in frontmatter.
PLUGIN_ROOT_VAR = "${CLAUDE_PLUGIN_ROOT}"

OWNED_PREFIX = "ui-design-"          # every skill and agent this tool owns
GUIDE_SKILL = "ui-design-catalog"    # the one whose commands and counts are linted

SKILL_KEYS = {"name", "description"}
AGENT_KEYS = {"name", "description", "tools"}
# Agents only read and report; the caller decides what gets written or promoted.
AGENT_FORBIDDEN_TOOLS = ("Write", "Edit", "Agent", "Bash", "NotebookEdit")
# spec.yaml agent_tool_exceptions may lift the ban for these tools only, for a
# named agent that exists. Write, Edit, Agent and NotebookEdit stay forbidden
# for every agent, declared or not.
EXCEPTABLE_TOOLS = ("Bash",)
# A tool list cannot confine Bash, so an agent granted it must say, in its own
# body, what it may run and that it never writes. Checked case-insensitively.
BASH_AGENT_REQUIREMENTS = (
    "never pass `--persist`",
    "never write any file",
    "catalog/scripts/search.py",
)

# Gitignored scratch directories (see the repo .gitignore). A path under one is
# a legitimate reference even though it does not exist in a fresh clone.
STAGING_DIRS = {"candidates", "captures"}
# A tripwire, not a cache: validate_data.py fails while it exists. Ignoring it
# would hide a partial refresh.
TRIPWIRE_FILE = ".google-font-refresh.incomplete.json"

GUIDE_REQUIREMENTS = (
    "## Query Contract", "one dominant intent", "Retry once",
    "Do not persist unverified output", "explicit accessibility outcome terms",
    "Confirm the output directory with the user",
)
PYTHON_COMMAND = re.compile(r"python(3?)\s")      # group 1 is the version suffix, if any
SEARCH_COMMAND = re.compile(r"search\.py")
QUOTED_QUERY = re.compile(r'search\.py"?\s+"[^"]+"')
DOMAIN_FLAG = re.compile(r"--domain\s+(\S+)")
STACK_FLAG = re.compile(r"--stack\s+(\S+)")
PATH_REFERENCE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./*<>-]*[A-Za-z0-9_>/])")
# What a portable skill, agent or reader-facing doc must never say: each names
# something that exists only in the Pipelines monorepo, not in an installed plugin.
NON_PORTABLE = (
    (re.compile(r"(?<![\w-])ui-design/"), "a ui-design/ path (the plugin root is ${CLAUDE_PLUGIN_ROOT})"),
    (re.compile(r"\.claude/(?:skills|agents)/"), "a .claude/skills or .claude/agents path"),
    (re.compile(r"Pipelines"), "the Pipelines repo"),
    (re.compile(r"\bROSW\b"), "the ROSW repo"),
    (re.compile(r"repo[- ]root|this repo\b", re.IGNORECASE), "the repo root"),
)
SPEC_KEYS = (
    "catalog_root", "entry_point", "stdlib_only", "domains", "stacks", "dials",
    "formats", "default_max_results", "dtcg_extension_key", "exit_codes",
    "persistence", "counts_contract", "consumers", "agent_tool_exceptions",
)


class EnvironmentProblem(Exception):
    """The contract cannot be checked at all -- reported as exit 2."""


def rel(path):
    return Path(path).resolve().relative_to(TOOL_ROOT).as_posix()


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
        if not path or not (TOOL_ROOT / path).exists():
            errors.append(f"spec.yaml: referenced path does not exist: {path!r}")


def check_path_references(path, errors):
    """Every plugin path a skill or the agent cites must exist."""
    for match in sorted(set(PATH_REFERENCE.findall(path.read_text(encoding="utf-8")))):
        if any(ch in match for ch in "<>*"):
            continue                                   # placeholder or glob
        if STAGING_DIRS & set(Path(match).parts):
            continue                                   # gitignored staging
        if not (TOOL_ROOT / match).exists():
            errors.append(f"{rel(path)}: references {PLUGIN_ROOT_VAR}/{match}, which does not exist.")


def portability_errors(label, text):
    """Pure, so the rule can be tested: what in this text would break once installed."""
    problems = []
    for pattern, what in NON_PORTABLE:
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            problems.append(f"{label}:{line}: names {what}, which does not exist in an installed plugin.")
    return problems


def check_portable(path, errors):
    errors.extend(portability_errors(rel(path), path.read_text(encoding="utf-8")))


def check_frontmatter_portable(path, frontmatter, errors):
    """Only the Markdown body is substituted, so a variable in frontmatter is shown raw."""
    for key, value in frontmatter.items():
        if "${" in str(value):
            errors.append(f"{rel(path)}: frontmatter '{key}' contains a ${{...}} variable, which "
                          f"Claude Code does not expand outside the Markdown body.")


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
        check_portable(path, errors)
        check_frontmatter_portable(path, frontmatter, errors)
    return skills


def agent_tool_errors(name, granted, body, exceptions):
    """Problems with one agent's tool list; pure, so the rule can be tested.

    exceptions is spec.yaml agent_tool_exceptions: {agent name: [tool, ...]}.
    """
    allowed = set((exceptions or {}).get(name) or []) & set(EXCEPTABLE_TOOLS)
    errors = []
    forbidden = [t for t in AGENT_FORBIDDEN_TOOLS if t in granted and t not in allowed]
    if forbidden:
        errors.append(f"tools list grants {forbidden} -- this agent must stay read-only and "
                      f"non-delegating; the caller decides what is written or promoted.")
    if "Bash" in allowed and "Bash" in granted:
        lowered = body.lower()
        missing = [phrase for phrase in BASH_AGENT_REQUIREMENTS if phrase not in lowered]
        if missing:
            errors.append(f"is granted Bash by spec.yaml agent_tool_exceptions, so its body must "
                          f"state its boundary; missing {missing}.")
    return errors


def exception_declaration_errors(exceptions, agent_names):
    """Problems with the agent_tool_exceptions block itself."""
    errors = []
    if exceptions is None:
        return errors
    if not isinstance(exceptions, dict):
        return ["spec.yaml agent_tool_exceptions: must be a mapping of agent name -> tool list."]
    for name, tools in exceptions.items():
        if name not in agent_names:
            errors.append(f"spec.yaml agent_tool_exceptions: {name!r} is not an existing "
                          f"{OWNED_PREFIX}* agent.")
        if not isinstance(tools, list) or not tools:
            errors.append(f"spec.yaml agent_tool_exceptions: {name!r} must list the tools it may hold.")
            continue
        for tool in tools:
            if tool not in EXCEPTABLE_TOOLS:
                errors.append(f"spec.yaml agent_tool_exceptions: {name!r} may not be granted {tool!r}; "
                              f"only {list(EXCEPTABLE_TOOLS)} can be excepted.")
    return errors


def check_agents(yaml, spec, errors):
    agents = sorted(AGENTS_DIR.glob(f"{OWNED_PREFIX}*.md"))
    exceptions = spec.get("agent_tool_exceptions")
    errors.extend(exception_declaration_errors(exceptions, {p.stem for p in agents}))
    if not isinstance(exceptions, dict):
        exceptions = {}
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
        for message in agent_tool_errors(path.stem, granted, path.read_text(encoding="utf-8"), exceptions):
            errors.append(f"{rel(path)}: {message}")
        check_path_references(path, errors)
        check_portable(path, errors)
        check_frontmatter_portable(path, frontmatter, errors)
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
        path = TOOL_ROOT / carrier
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
        expected = f"{PLUGIN_ROOT_VAR}/{entry_point}"
        if script != expected:
            errors.append(f"{label}: command must run {expected}, not {script}: {command}")
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
    root = TOOL_ROOT / spec["stdlib_only"]["root"]
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
    if not GITIGNORE.is_file():
        errors.append("the plugin has no .gitignore; it is published on its own, so the "
                      "monorepo root one does not travel with it.")
        return
    lines = {line.strip() for line in GITIGNORE.read_text(encoding="utf-8").splitlines()}
    dir_name = (spec.get("persistence") or {}).get("dir_name", "design-system")
    for pattern in (f"{dir_name}/", "candidates/", "captures/"):
        if pattern not in lines:
            errors.append(f".gitignore: missing the bare pattern {pattern!r}.")
    if TRIPWIRE_FILE in lines:
        errors.append(f".gitignore: must not ignore {TRIPWIRE_FILE}; validate_data.py treats "
                      f"its presence as a failure signal for a partial refresh.")


def check_gitattributes(errors):
    """The relevance gate hashes raw bytes; a CRLF checkout would change every hash."""
    if not GITATTRIBUTES.is_file():
        errors.append("the plugin has no .gitattributes; without it the LF pin the relevance "
                      "gate depends on does not travel with the published plugin.")
        return
    rules = [line.split() for line in GITATTRIBUTES.read_text(encoding="utf-8").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    if not any(rule[0] == "*" and "eol=lf" in rule[1:] for rule in rules):
        errors.append(".gitattributes: needs a `* ... eol=lf` rule so every file is checked out "
                      "with LF; the relevance gate fingerprints raw bytes.")


def check_release_files(errors):
    """The manifest, marketplace entry, changelog and release files must agree."""
    for name in RELEASE_FILES:
        if not (TOOL_ROOT / name).is_file():
            errors.append(f"{name}: missing; the plugin is published on its own and needs it.")
    try:
        plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f".claude-plugin/plugin.json: unreadable ({exc}).")
        return
    name, version = plugin.get("name"), plugin.get("version")
    if name != "ui-design":
        errors.append(f".claude-plugin/plugin.json: name is {name!r}; skills are namespaced by it, "
                      f"so it must stay 'ui-design'.")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append(f".claude-plugin/plugin.json: version {version!r} is not MAJOR.MINOR.PATCH.")
    try:
        market = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f".claude-plugin/marketplace.json: unreadable ({exc}).")
        market = {}
    entries = market.get("plugins") or []
    if [entry.get("name") for entry in entries] != [name]:
        errors.append(f".claude-plugin/marketplace.json: plugins must list exactly {name!r}, "
                      f"named as plugin.json names it.")
    for entry in entries:
        if entry.get("source") != "./":
            errors.append(f".claude-plugin/marketplace.json: source is {entry.get('source')!r}; "
                          f"the plugin root is the repository root, so it must be './'.")
    if CHANGELOG.is_file() and isinstance(version, str):
        heading = re.search(r"^## \[?(\d+\.\d+\.\d+)\]?", CHANGELOG.read_text(encoding="utf-8"), re.MULTILINE)
        if not heading or heading.group(1) != version:
            errors.append(f"CHANGELOG.md: newest entry is {heading.group(1) if heading else 'missing'}, "
                          f"plugin.json says {version}.")


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
    agents = check_agents(yaml, spec, errors)
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

    docs = [TOOL_ROOT / "ROUTER.md", *sorted((TOOL_ROOT / "references").glob("*.md"))]
    for path in docs:
        if path.is_file():
            check_portable(path, errors)

    modules = check_stdlib_only(spec, errors)
    check_gitignore(spec, errors)
    check_gitattributes(errors)
    check_release_files(errors)
    check_locked_examples(spec, errors)

    summary = (f"{len(core.CSV_CONFIG)} domains, {len(core.AVAILABLE_STACKS)} stacks, "
               f"{len(skills)} skills, {len(agents)} agents, {commands} documented commands, "
               f"{claims} count claims per carrier, {modules} stdlib-only modules, "
               f"{len(docs)} portable docs, 3 locked examples, 2 exit codes")
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
