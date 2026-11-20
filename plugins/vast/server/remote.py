"""ssh and scp to a rented instance, through the system's own OpenSSH (no third-party library).

Every command runs as `root@<ssh_host> -p <ssh_port>` with:
  * the private key named by VAST_SSH_KEY (default ~/.ssh/id_ed25519); only its .pub is ever sent
    to Vast;
  * BatchMode=yes, so ssh never prompts, and stdin from the null device, so ssh never reads the
    server's own input;
  * StrictHostKeyChecking=accept-new with a known_hosts file of the server's own, under the state
    folder, so a host key that changes after the first connection is refused.

Recipe arguments are checked against their declared type and inserted shell-quoted. Local files
move only inside VAST_WORK_DIR; remote files only inside the job folder.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
from pathlib import Path, PurePosixPath

from vast_api import VastError, expand, home

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TAIL_LINES = 60
REMOTE_PATH = re.compile(r"^[A-Za-z0-9_][A-Za-z0-9_.\-/#]*$")


def load_recipes(path=None):
    return json.loads(Path(path or PLUGIN_ROOT / "recipes.json").read_text(encoding="utf-8"))


def ssh_key_path(environ):
    return expand(environ.get("VAST_SSH_KEY") or home(environ) / ".ssh" / "id_ed25519", environ)


def public_key(environ):
    path = ssh_key_path(environ)
    pub = Path(str(path) + ".pub")
    try:
        text = pub.read_text(encoding="utf-8").strip()
    except OSError:
        raise VastError("no_ssh_key", f"no public key at {pub}",
                        "make one with `ssh-keygen -t ed25519`, or point VAST_SSH_KEY at your private key") from None
    if not text.startswith(("ssh-ed25519 ", "ssh-rsa ", "ecdsa-sha2-")):
        raise VastError("bad_ssh_key", f"{pub} does not look like an OpenSSH public key")
    return text


def work_dir(environ):
    return expand(environ.get("VAST_WORK_DIR") or "vast-work", environ).resolve()


def local_path(environ, relative, must_exist=False):
    """A path inside VAST_WORK_DIR, or a refusal."""
    root = work_dir(environ)
    candidate = (root / relative).resolve()
    if candidate != root and root not in candidate.parents:
        raise VastError("outside_work_dir", f"{relative} is outside VAST_WORK_DIR ({root})",
                        "copy the file into VAST_WORK_DIR first, or set VAST_WORK_DIR")
    if must_exist and not candidate.exists():
        raise VastError("missing", f"{candidate} does not exist")
    return candidate


def remote_path(job_dir, relative):
    """/workspace/job/<relative>, or a refusal for anything that could climb out."""
    if not isinstance(relative, str) or not REMOTE_PATH.match(relative) or ".." in PurePosixPath(relative).parts:
        raise VastError("bad_path", f"{relative!r} is not a plain path inside {job_dir}",
                        "use letters, digits, _ . - / and # only, no `..`, and no leading /")
    return f"{job_dir.rstrip('/')}/{relative}"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


# ── recipe rendering ─────────────────────────────────────────────────────────

def _check_param(name, spec, value, job_dir):
    kind = spec["type"]
    if kind == "path":
        return shlex.quote(remote_path(job_dir, value))
    if kind == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            raise VastError("bad_argument", f"{name} must be an integer")
        if value < spec.get("minimum", value) or value > spec.get("maximum", value):
            raise VastError("bad_argument", f"{name} is out of range")
        return str(value)
    if kind == "enum":
        if value not in spec["values"]:
            raise VastError("bad_argument", f"{name} must be one of {', '.join(spec['values'])}")
        return shlex.quote(value)
    if kind == "string":
        if not isinstance(value, str) or len(value) > spec.get("maxLength", 400):
            raise VastError("bad_argument", f"{name} must be a string of at most {spec.get('maxLength', 400)} characters")
        if "pattern" in spec and not re.fullmatch(spec["pattern"], value):
            raise VastError("bad_argument", f"{name} must match {spec['pattern']}")
        return shlex.quote(value)
    if kind == "array":
        if not isinstance(value, list) or len(value) > spec.get("maxItems", 40):
            raise VastError("bad_argument", f"{name} must be a list of at most {spec.get('maxItems', 40)} items")
        item = spec.get("items", {"type": "string"})
        return " ".join(_check_param(f"{name}[{i}]", item, v, job_dir) for i, v in enumerate(value))
    raise VastError("bad_recipe", f"recipe parameter {name} has an unknown type {kind}")


def render(recipe_name, arguments, recipes):
    recipe = recipes["recipes"].get(recipe_name)
    if recipe is None:
        raise VastError("unknown_recipe", f"no recipe named {recipe_name}",
                        "list_recipes shows the recipes and their parameters")
    params = recipe.get("params", {})
    unknown = sorted(set(arguments) - set(params))
    if unknown:
        raise VastError("bad_argument", f"{recipe_name} takes no {', '.join(unknown)}",
                        f"it takes: {', '.join(params) or 'nothing'}")
    values = {}
    for name, spec in params.items():
        if name in arguments:
            value = arguments[name]
        elif "default" in spec:
            value = spec["default"]
        else:
            raise VastError("bad_argument", f"{recipe_name} needs {name}")
        values[name] = _check_param(name, spec, value, recipes["job_dir"])
    # One pass over the template, so a value that happens to contain `{name}` is never substituted again.
    command = re.sub(r"\{([a-z_]+)\}", lambda m: values.get(m.group(1), m.group(0)), recipe["template"])
    return command, bool(recipe.get("background"))


# ── ssh ──────────────────────────────────────────────────────────────────────

class Remote:
    def __init__(self, environ, state_folder, runner=subprocess.run, popen=subprocess.Popen):
        self.environ = environ
        self.state_folder = Path(state_folder)
        self.runner = runner
        self.popen = popen

    def _binary(self, name):
        found = shutil.which(name, path=self.environ.get("PATH"))
        if not found:
            raise VastError("no_" + name, f"`{name}` was not found on PATH",
                            "install OpenSSH (Windows 10+ and macOS include it)")
        return found

    def _options(self, port_flag):
        self.state_folder.mkdir(parents=True, exist_ok=True)
        key = ssh_key_path(self.environ)
        if not key.exists():
            raise VastError("no_ssh_key", f"no private key at {key}",
                            "make one with `ssh-keygen -t ed25519`, or set VAST_SSH_KEY")
        return ["-i", str(key), "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=accept-new",
                "-o", "UserKnownHostsFile=" + str(self.state_folder / "known_hosts"),
                "-o", "ConnectTimeout=20", "-o", "ServerAliveInterval=30", port_flag]

    @staticmethod
    def target(instance):
        host, port = instance.get("ssh_host"), instance.get("ssh_port")
        if not host or not port:
            raise VastError("no_ssh_yet", "the instance has no ssh address yet",
                            "wait_ready polls until it does")
        if not re.fullmatch(r"[A-Za-z0-9.\-]+", str(host)):
            raise VastError("bad_host", "the instance's ssh host is not a plain host name")
        return str(host), int(port)

    def run(self, instance, command, timeout=600):
        host, port = self.target(instance)
        argv = [self._binary("ssh"), *self._options("-p"), str(port), f"root@{host}", command]
        try:
            done = self.runner(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise VastError("timeout", f"the command ran longer than {timeout}s",
                            "run long work as a background recipe and read it with job_status") from None
        return done.returncode, done.stdout, done.stderr

    def copy(self, instance, source, destination, upload, timeout=3600):
        host, port = self.target(instance)
        remote = f"root@{host}:{shlex.quote(destination if upload else source)}"
        pair = [str(source), remote] if upload else [remote, str(destination)]
        argv = [self._binary("scp"), *self._options("-P"), str(port), "-r", *pair]
        try:
            done = self.runner(argv, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            raise VastError("timeout", f"the copy ran longer than {timeout}s") from None
        if done.returncode != 0:
            raise VastError("copy_failed", "scp failed: " + tail(done.stderr, 5))

    def open_tunnel(self, instance, local_port, remote_port):
        host, port = self.target(instance)
        argv = [self._binary("ssh"), *self._options("-p"), str(port), "-N",
                "-o", "ExitOnForwardFailure=yes",
                "-L", f"127.0.0.1:{int(local_port)}:127.0.0.1:{int(remote_port)}", f"root@{host}"]
        process = self.popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
        return process.pid


def tail(text, lines=TAIL_LINES):
    return "\n".join((text or "").splitlines()[-lines:])


def close_pid(pid):
    """Stop a tunnel process. False when it was already gone."""
    try:
        os.kill(int(pid), signal.SIGTERM)
        return True
    except (ProcessLookupError, PermissionError, OSError, ValueError):
        return False
