#!/usr/bin/env python3
"""Register the Blender MCP server with the Gemini CLI, and check the whole chain.

    python blender-gemini/install.py install   [--profile readonly|full] [--trust]
                                               [--no-safe-mode] [--scope user|project]
                                               [--settings PATH] [--dry-run]
    python blender-gemini/install.py uninstall [--scope ...] [--settings PATH] [--dry-run]
    python blender-gemini/install.py check     [--scope ...] [--settings PATH]
    python blender-gemini/install.py sync-key  [--remove] [--dry-run]

`install` merges one entry, `mcpServers.blender`, into the Gemini CLI's settings.json and
touches nothing else in it. It refuses a file it cannot parse, keeps the first version of
the file beside it as settings.json.rosw-bak, and writes through a temporary file. `check`
only reads: it never starts a server and sends nothing to Blender, and it reports whether
GEMINI_API_KEY is visible to the Gemini CLI by name and location, never by value.
`sync-key` copies GEMINI_API_KEY from ~/.rosw/keys.env (where docs/setup_keys.py saves it)
into ~/.gemini/.env, which the Gemini CLI reads; it prints names and paths, never the key.

Standard library only. The server it registers is the `mcp-for-blender` package, run
with uvx; the Blender add-on it talks to is installed separately (see README.md).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SERVER = "blender"
PACKAGE = "mcp-for-blender"
DEFAULT_HOST, DEFAULT_PORT = "localhost", 9876

# Tool names as the package registers them (blender_mcp/server.py, v2.1.9). The read-only
# profile exposes only these; none of them runs code, spends credits or leaves the machine.
READ_ONLY_TOOLS = ["get_addon_status", "get_scene_info", "look"]
# Sends feedback about a session off the machine; no profile exposes it.
NEVER_EXPOSED = ["record_trajectory_feedback"]
PROFILES = ("readonly", "full")

KEY_NAME = "GEMINI_API_KEY"
# docs/setup_keys.py treats these as "no key yet"; tests/test_install.py checks the two agree.
KEY_PLACEHOLDERS = {"your-key-here", "Add_Key"}
# What a key may look like to be written into a .env file. Anything else (spaces, quotes, #,
# $, backslashes) can be read differently by different dotenv parsers, so it is not copied.
SAFE_KEY_VALUE = re.compile(r"[A-Za-z0-9_.\-]+")
_KEY_LINE = re.compile(r"^\s*(?:export\s+)?" + KEY_NAME + r"\s*=")


class SettingsError(Exception):
    """A settings file this script will not touch."""


class KeySyncError(SettingsError):
    """A key this script will not copy. Its message never contains the key."""


def server_entry(profile="readonly", trust=False, safe_mode=True):
    """The `mcpServers.blender` entry for a profile.

    readonly: the three tools above, auto-approved (they change nothing).
    full: every tool but NEVER_EXPOSED, including execute_blender_code. Gemini asks before
    each call unless `trust` is set, which skips that prompt for the whole server.
    """
    if profile not in PROFILES:
        raise ValueError(f"profile must be one of {PROFILES}, not {profile!r}")
    env = {"BLENDER_MCP_DISABLE_TELEMETRY": "1"}
    if safe_mode:
        env["BLENDER_MCP_SAFE_MODE"] = "1"
    entry = {"command": "uvx", "args": [PACKAGE], "env": env, "timeout": 120000}
    if profile == "readonly":
        entry["includeTools"] = list(READ_ONLY_TOOLS)
        entry["trust"] = True
    else:
        entry["excludeTools"] = list(NEVER_EXPOSED)
        entry["trust"] = bool(trust)
    return entry


def settings_path(scope="user", override=None):
    if override:
        return Path(override).expanduser()
    base = Path.home() if scope == "user" else Path.cwd()
    return base / ".gemini" / "settings.json"


def load_settings(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as err:
        raise SettingsError(f"{path} is not plain JSON ({err}); remove any comments or fix it. "
                            "Nothing was changed.") from err
    if not isinstance(data, dict):
        raise SettingsError(f"{path} does not hold a JSON object. Nothing was changed.")
    if not isinstance(data.get("mcpServers", {}), dict):
        raise SettingsError(f"{path}: mcpServers is not an object. Nothing was changed.")
    return data


def _atomic_write(path, text, backup=True, private=False):
    """Write through a temporary file in the same folder, then replace.

    backup: keep the first copy of an existing file beside it as <name>.rosw-bak and never
    overwrite that copy. private: mode 600 on POSIX (no-op on Windows).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    if backup and existed:
        backup_path = path.with_name(path.name + ".rosw-bak")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)  # the first copy is the pre-install state
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        if private:
            if os.name != "nt":
                os.chmod(tmp, 0o600)
        elif existed:
            shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def write_settings(path, data):
    _atomic_write(path, json.dumps(data, indent=2) + "\n")


def rosw_keys_file():
    """Where docs/setup_keys.py saves keys: ROSW_KEYS_FILE, else ~/.rosw/keys.env."""
    override = os.environ.get("ROSW_KEYS_FILE")
    return Path(override) if override else Path.home() / ".rosw" / "keys.env"


def gemini_env_file():
    """The .env the Gemini CLI reads for every project: ~/.gemini/.env."""
    return Path.home() / ".gemini" / ".env"


def read_key(path):
    """GEMINI_API_KEY from a dotenv-style file, or None. The last non-empty, non-placeholder
    assignment wins, as in docs/setup_keys.py. The value goes to the caller and nowhere else."""
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return None
    found = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, _, value = line.partition("=")
        name = name.strip()
        if name.startswith("export "):
            name = name[len("export "):].strip()
        value = value.strip().strip('"').strip("'")
        if name == KEY_NAME and value and value not in KEY_PLACEHOLDERS:
            found = value
    return found


def _rewrite_key_lines(lines, new_line):
    """lines with every GEMINI_API_KEY assignment replaced by new_line (kept at the position of
    the first one, or appended), or dropped if new_line is None. Other lines are untouched."""
    out, placed = [], False
    for line in lines:
        if _KEY_LINE.match(line):
            if new_line is not None and not placed:
                out.append(new_line)
                placed = True
            continue
        out.append(line)
    if new_line is not None and not placed:
        out.append(new_line)
    return out


def sync_key(source, target, dry_run=False, remove=False):
    """Copy GEMINI_API_KEY from `source` into the dotenv file `target`, or with remove=True
    take it out of `target`. Returns added/updated/unchanged, or removed/absent. Nothing it
    returns, prints or raises holds the key. No backup is made of `target`: it would be a
    second copy of the old key."""
    try:
        lines = target.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        lines = []
    present = any(_KEY_LINE.match(line) for line in lines)
    if remove:
        if not present:
            return "absent"
        if not dry_run:
            _atomic_write(target, "\n".join(_rewrite_key_lines(lines, None)) + "\n", backup=False, private=True)
        return "removed"
    value = read_key(source)
    if value is None:
        raise KeySyncError(f"{KEY_NAME} is not set in {source}. Add it with: python docs/setup_keys.py")
    if not SAFE_KEY_VALUE.fullmatch(value):
        raise KeySyncError(f"the {KEY_NAME} in {source} has characters this script will not write into a "
                           f".env file; put it in {target} by hand")
    if read_key(target) == value:
        return "unchanged"
    status = "updated" if present else "added"
    if not dry_run:
        text = "\n".join(_rewrite_key_lines(lines, f"{KEY_NAME}={value}")) + "\n"
        _atomic_write(target, text, backup=False, private=True)
    return status


def install(path, entry, dry_run=False):
    """Merge the entry. Returns (status, previous) with status added/updated/unchanged."""
    data = load_settings(path)
    servers = data.setdefault("mcpServers", {})
    previous = servers.get(SERVER)
    if previous == entry:
        return "unchanged", previous
    servers[SERVER] = entry
    if not dry_run:
        write_settings(path, data)
    return ("updated" if previous is not None else "added"), previous


def uninstall(path, dry_run=False):
    data = load_settings(path)
    servers = data.get("mcpServers", {})
    if SERVER not in servers:
        return "absent"
    del servers[SERVER]
    if not dry_run:
        write_settings(path, data)
    return "removed"


def blender_endpoint(entry=None):
    """Host and port the server will dial: its own env first, then ours, then the defaults."""
    env = (entry or {}).get("env", {})
    host = env.get("BLENDER_HOST") or os.environ.get("BLENDER_HOST") or DEFAULT_HOST
    raw = env.get("BLENDER_PORT") or os.environ.get("BLENDER_PORT") or str(DEFAULT_PORT)
    try:
        return host, int(raw)
    except ValueError:
        return host, DEFAULT_PORT


def port_open(host, port, timeout=1.0):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def describe(entry):
    if entry.get("includeTools") is not None:
        scope = "read-only (" + ", ".join(entry["includeTools"]) + ")"
    else:
        scope = "full access, including execute_blender_code"
    approval = "auto-approved" if entry.get("trust") else "Gemini asks before each call"
    safe = "safe mode on" if entry.get("env", {}).get("BLENDER_MCP_SAFE_MODE") == "1" else "safe mode OFF"
    return f"{scope}; {approval}; {safe}"


def key_row(env, keys_file, gemini_env):
    """(status, detail) for whether the Gemini CLI can see GEMINI_API_KEY. Says where it was
    found, never what it is."""
    if env.get(KEY_NAME):
        return "ok", f"{KEY_NAME} is set in this shell's environment"
    if read_key(gemini_env):
        return "ok", f"{KEY_NAME} is set in {gemini_env}"
    if read_key(keys_file):
        return "fail", (f"{KEY_NAME} is only in {keys_file}, which the Gemini CLI does not read; "
                        "run: python blender-gemini/install.py sync-key")
    return "fail", f"{KEY_NAME} is not set; add it with: python docs/setup_keys.py, then run: " \
                   "python blender-gemini/install.py sync-key"


def run_checks(path, which=shutil.which, probe=port_open, platform=sys.platform, repo_root=REPO_ROOT,
               env=None, keys_file=None, gemini_env=None):
    """A list of (status, label, detail), status being ok, warn or fail. Reads only."""
    env = os.environ if env is None else env
    rows = []

    def add(status, label, detail):
        rows.append((status, label, detail))

    entry = None
    try:
        servers = load_settings(path).get("mcpServers", {})
        entry = servers.get(SERVER)
        if entry is None:
            add("fail", "gemini config", f"no mcpServers.{SERVER} in {path}; run: python blender-gemini/install.py install")
        elif entry.get("command") != "uvx" or entry.get("args") != [PACKAGE]:
            add("fail", "gemini config", f"mcpServers.{SERVER} in {path} is not the {PACKAGE} server")
        else:
            add("ok", "gemini config", f"{path}: {describe(entry)}")
    except SettingsError as err:
        add("fail", "gemini config", str(err))

    for tool, why in (("uvx", "runs the Blender server"),
                      ("gemini", "the Gemini CLI itself"),
                      ("npx", "runs the gemini MCP server Claude calls")):
        found = which(tool)
        add("ok" if found else "fail", tool, found or f"not on PATH ({why})")

    status, detail = key_row(env, keys_file or rosw_keys_file(), gemini_env or gemini_env_file())
    add(status, "gemini key", detail)

    mcp_json = repo_root / ".mcp.json"
    try:
        gemini = json.loads(mcp_json.read_text(encoding="utf-8")).get("mcpServers", {}).get("gemini")
    except (OSError, ValueError):
        gemini = None
    if not gemini:
        add("fail", "claude config", f"no mcpServers.gemini in {mcp_json}")
    elif gemini.get("env", {}).get("GEMINI_MCP_BACKEND") != "gemini":
        add("fail", "claude config", "mcpServers.gemini does not set GEMINI_MCP_BACKEND=gemini, "
            "so it would call the Antigravity CLI (agy), which does not read the Gemini CLI settings")
    elif platform == "win32" and gemini.get("command") == "npx":
        add("warn", "claude config", "bare `npx` often fails to start on native Windows; see README.md, 'Windows'")
    else:
        add("ok", "claude config", f"{mcp_json}: mcpServers.gemini, backend gemini")

    host, port = blender_endpoint(entry)
    if probe(host, port):
        add("ok", "blender", f"something is listening on {host}:{port}")
    else:
        add("fail", "blender", f"nothing on {host}:{port}; in Blender press N, open the 'MCP for Blender' "
            "tab and click Start MCP Server")
    return rows


def _path_from(args):
    return settings_path(args.scope, args.settings)


def _cmd_install(args):
    entry = server_entry(args.profile, trust=args.trust, safe_mode=not args.no_safe_mode)
    path = _path_from(args)
    status, previous = install(path, entry, dry_run=args.dry_run)
    prefix = "(dry run, nothing written) " if args.dry_run else ""
    print(f"{prefix}{status}: mcpServers.{SERVER} in {path}")
    print(f"  {describe(entry)}")
    if status == "updated":
        print("  replaced a different entry; the first copy of the file is kept as "
              f"{path.name}.rosw-bak. It was: {json.dumps(previous)}")
    if args.dry_run:
        print(json.dumps({"mcpServers": {SERVER: entry}}, indent=2))
    if args.profile == "full" and not args.dry_run and status != "unchanged":
        print("  full profile: execute_blender_code can run Python in your open Blender. Save your .blend first.")
    return 0


def _cmd_uninstall(args):
    path = _path_from(args)
    status = uninstall(path, dry_run=args.dry_run)
    prefix = "(dry run, nothing written) " if args.dry_run else ""
    print(f"{prefix}{status}: mcpServers.{SERVER} in {path}")
    return 0


def _cmd_sync_key(args):
    source = Path(args.keys_file).expanduser() if args.keys_file else rosw_keys_file()
    target = Path(args.env_file).expanduser() if args.env_file else gemini_env_file()
    status = sync_key(source, target, dry_run=args.dry_run, remove=args.remove)
    prefix = "(dry run, nothing written) " if args.dry_run else ""
    where = f"in {target}" if args.remove else f"in {target} (from {source})"
    print(f"{prefix}{status}: {KEY_NAME} {where}")  # names and paths only, never the value
    if status in ("added", "updated") and not args.dry_run:
        print("  that file is now a second copy of the key; mode 600 on Linux and macOS. "
              "Undo with: python blender-gemini/install.py sync-key --remove")
    return 0


def _cmd_check(args):
    rows = run_checks(_path_from(args))
    for status, label, detail in rows:
        print(f"[{status:>4}] {label:<14} {detail}")
    failed = [label for status, label, _ in rows if status == "fail"]
    print("ready" if not failed else "not ready: " + ", ".join(failed))
    return 1 if failed else 0


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--scope", choices=("user", "project"), default="user",
                       help="user: ~/.gemini/settings.json (default); project: ./.gemini/settings.json")
        p.add_argument("--settings", help="a settings.json path, instead of --scope")

    p_install = sub.add_parser("install", help="add mcpServers.blender to the Gemini CLI settings")
    common(p_install)
    p_install.add_argument("--profile", choices=PROFILES, default="readonly",
                           help="readonly (default): inspect the scene only; full: every tool, incl. execute_blender_code")
    p_install.add_argument("--trust", action="store_true",
                           help="full profile only: skip Gemini's per-call approval for the server")
    p_install.add_argument("--no-safe-mode", action="store_true",
                           help="do not set BLENDER_MCP_SAFE_MODE=1 (safe mode blocks file, process and network access in scripts)")
    p_install.add_argument("--dry-run", action="store_true", help="show the entry; write nothing")
    p_install.set_defaults(func=_cmd_install)

    p_remove = sub.add_parser("uninstall", help="remove mcpServers.blender, leaving the rest")
    common(p_remove)
    p_remove.add_argument("--dry-run", action="store_true")
    p_remove.set_defaults(func=_cmd_uninstall)

    p_check = sub.add_parser("check", help="read-only preflight of the whole chain")
    common(p_check)
    p_check.set_defaults(func=_cmd_check)

    p_key = sub.add_parser("sync-key", help=f"copy {KEY_NAME} from ~/.rosw/keys.env to ~/.gemini/.env "
                                           "(the Gemini CLI does not read keys.env); never prints the key")
    p_key.add_argument("--keys-file", help="the file to copy from (default: ROSW_KEYS_FILE or ~/.rosw/keys.env)")
    p_key.add_argument("--env-file", help="the file to copy into (default: ~/.gemini/.env)")
    p_key.add_argument("--remove", action="store_true", help=f"remove {KEY_NAME} from the Gemini .env instead")
    p_key.add_argument("--dry-run", action="store_true", help="say what would happen; write nothing")
    p_key.set_defaults(func=_cmd_sync_key)
    return parser


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    args = build_parser().parse_args(argv)
    if getattr(args, "trust", False) and args.profile != "full":
        print("--trust only applies to --profile full (the read-only profile is already auto-approved).",
              file=sys.stderr)
        return 2
    try:
        return args.func(args)
    except SettingsError as err:
        print(f"refused: {err}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
