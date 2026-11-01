"""Pluggable LLM backend for the creative-writing pipeline.

Three backends:
  - "ollama" ("local"): local inference via the Ollama HTTP API.
    stdlib-only (urllib/json), no pip dependency. Default backend -- no
    API key or billing required to get started.
  - "anthropic": the Anthropic API. Requires the `anthropic` package and
    ANTHROPIC_API_KEY. Opt in with PIPELINE_LLM_BACKEND=anthropic (or by
    passing backend="anthropic" to generate()).
  - "gemini_mcp" ("mcp"): Google Gemini, via the same google-genai API the
    "Gemini MCP" plugin's `ask_gemini` tool calls. Requires the
    `google-genai` package and GEMINI_API_KEY. Opt in with
    PIPELINE_LLM_BACKEND=gemini_mcp (or backend="gemini_mcp"). Named for
    the MCP plugin it mirrors, not because this module speaks the MCP
    wire protocol -- a headless script has no live MCP client to broker
    stdio for it, so this calls the Gemini API directly with the same
    model/key the plugin's server.py uses. See _generate_gemini_mcp.

("native", i.e. running inside a live Claude Code session via the
creative-writing-pipeline skill, is not a backend here -- it's a separate
execution path that uses Claude's own reasoning directly and never calls
this module. See the creative-writing-pipeline skill under .claude/skills/.)

librarian.py picks its own backend independently of PIPELINE_LLM_BACKEND
(default "ollama", override via LIBRARIAN_BACKEND) -- the librarian's
model is independent of whichever backend is doing the actual drafting.

Settings (environment variables, or ~/.rosw/keys.env):
  PIPELINE_LLM_BACKEND   ollama (default) | anthropic | gemini_mcp
  ANTHROPIC_MODEL        default claude-sonnet-5-5
  OLLAMA_MODEL, OLLAMA_HOST, GEMINI_MODEL
  PIPELINE_MAX_TOKENS    output cap per call (default 8000). A reply cut off at
                         the cap raises LLMError rather than returning a
                         truncated draft.
  PIPELINE_LLM_RETRIES   extra attempts after a transient failure (default 3)
  PIPELINE_LLM_BACKOFF   seconds before the first retry, doubling each time
                         (default 2)
The anthropic and ollama backends retry rate limits, overloads, 5xx replies and
dropped connections; the gemini_mcp backend does not retry.
"""
import json
import os
import time
import urllib.error
import urllib.request



# Values that mean "no key yet". Never loaded into the environment.
PLACEHOLDERS = {"your-key-here", "Add_Key"}

LEGACY_ENV = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def user_keys_file() -> str:
    """The per-user key file, outside the repo: ~/.rosw/keys.env.

    docs/setup_keys.py writes it. ROSW_KEYS_FILE overrides the location.
    """
    return os.environ.get("ROSW_KEYS_FILE") or os.path.join(
        os.path.expanduser("~"), ".rosw", "keys.env")


def _load_env_file(path: str) -> None:
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip('"').strip("'")
        if value and value not in PLACEHOLDERS:
            os.environ[key.strip()] = value


def _load_dotenv() -> None:
    """Load KEY=VALUE lines into os.environ from the key files.

    First creative-writing/pipeline/.env (a legacy location, still read if
    present), then the user key file (see user_keys_file), which wins.
    Values in either file override the shell's, so the pipeline's dedicated
    key wins over any GEMINI_API_KEY set elsewhere. Placeholder values
    ("your-key-here", "Add_Key") are ignored.
    """
    _load_env_file(LEGACY_ENV)
    _load_env_file(user_keys_file())


_load_dotenv()

BACKEND = os.environ.get("PIPELINE_LLM_BACKEND", "ollama")

DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-5-5"
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL") or DEFAULT_ANTHROPIC_MODEL
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise RuntimeError(f"{name} must be a whole number, got {raw!r}.") from None
    if value < 0:
        raise RuntimeError(f"{name} must not be negative, got {value}.")
    return value


MAX_TOKENS = _int_env("PIPELINE_MAX_TOKENS", 8000)
MAX_RETRIES = _int_env("PIPELINE_LLM_RETRIES", 3)
BACKOFF_SECONDS = _int_env("PIPELINE_LLM_BACKOFF", 2)

OLLAMA_TIMEOUT = 600


class LLMError(RuntimeError):
    pass


class _Transient(Exception):
    """A failure worth retrying; carries the LLMError to raise if retries run out."""

    def __init__(self, error: LLMError):
        super().__init__(str(error))
        self.error = error


def _with_retries(call):
    """Run call(); on _Transient, wait (doubling) and retry up to MAX_RETRIES times."""
    delay = BACKOFF_SECONDS
    for attempt in range(MAX_RETRIES + 1):
        try:
            return call()
        except _Transient as exc:
            if attempt == MAX_RETRIES:
                raise exc.error from exc.error.__cause__
            time.sleep(delay)
            delay *= 2


def generate(prompt: str, *, system: str | None = None, model: str | None = None,
             backend: str | None = None) -> str:
    """Send a single prompt (with optional system prompt) and return the text response."""
    backend = backend or BACKEND
    if backend == "ollama":
        return _generate_ollama(prompt, system=system, model=model or OLLAMA_MODEL)
    if backend == "anthropic":
        return _generate_anthropic(prompt, system=system, model=model or ANTHROPIC_MODEL)
    if backend == "gemini_mcp":
        return _generate_gemini_mcp(prompt, system=system, model=model)
    raise LLMError(f"Unknown backend '{backend}' -- expected 'ollama', 'anthropic', or 'gemini_mcp'.")


def _generate_anthropic(prompt: str, *, system: str | None, model: str) -> str:
    try:
        import anthropic
    except ImportError as exc:
        raise LLMError(
            "The 'anthropic' package is required for the anthropic backend. "
            "Install it with: pip install anthropic"
        ) from exc

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise LLMError("ANTHROPIC_API_KEY is not set in the environment.")

    client = anthropic.Anthropic(api_key=api_key, max_retries=0)
    kwargs = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    transient = (anthropic.APIConnectionError, anthropic.RateLimitError,
                 anthropic.InternalServerError)

    def call():
        try:
            return client.messages.create(**kwargs)
        except transient as exc:
            raise _Transient(LLMError(f"Anthropic request failed for model '{model}': {exc}")) from exc
        except anthropic.APIStatusError as exc:
            if exc.status_code in (408, 409, 429, 529) or exc.status_code >= 500:
                raise _Transient(LLMError(f"Anthropic request failed for model '{model}': {exc}")) from exc
            raise LLMError(f"Anthropic request failed for model '{model}': {exc}") from exc

    response = _with_retries(call)
    if getattr(response, "stop_reason", None) == "max_tokens":
        raise LLMError(
            f"Anthropic stopped at the {MAX_TOKENS}-token output cap, so the reply is "
            f"truncated. Raise PIPELINE_MAX_TOKENS and retry."
        )
    parts = [block.text for block in response.content if getattr(block, "type", None) == "text"]
    if not parts:
        raise LLMError("Model response contained no text content.")
    return "\n".join(parts)


def _generate_ollama(prompt: str, *, system: str | None, model: str) -> str:
    url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": MAX_TOKENS},
    }
    if system:
        payload["system"] = system

    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    def call():
        try:
            with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            error = LLMError(
                f"Ollama returned HTTP {exc.code} for model '{model}': {detail}\n"
                f"If the model isn't pulled yet, run: ollama pull {model}"
            )
            error.__cause__ = exc
            if exc.code >= 500 or exc.code in (408, 429):
                raise _Transient(error) from exc
            raise error from exc
        except urllib.error.URLError as exc:
            error = LLMError(
                f"Could not reach Ollama at {OLLAMA_HOST} ({exc.reason}). "
                f"Start it with `ollama serve` (or confirm it's already running as a "
                f"background service), then retry."
            )
            error.__cause__ = exc
            raise _Transient(error) from exc
        except (ConnectionResetError, TimeoutError, OSError) as exc:
            error = LLMError(
                f"Ollama's connection failed mid-request ({exc}) -- it may have "
                f"crashed, restarted or timed out. Confirm `ollama serve` is still "
                f"running, then retry with `continue <run-id>`."
            )
            error.__cause__ = exc
            raise _Transient(error) from exc
        except json.JSONDecodeError as exc:
            error = LLMError(f"Ollama sent a reply that is not JSON: {exc}")
            error.__cause__ = exc
            raise _Transient(error) from exc

    body = _with_retries(call)

    text = body.get("response", "")
    if not text:
        raise LLMError(f"Ollama returned no text content. Full response: {body}")
    if body.get("done_reason") == "length":
        raise LLMError(
            f"Ollama stopped at the {MAX_TOKENS}-token output cap, so the reply is "
            f"truncated. Raise PIPELINE_MAX_TOKENS and retry."
        )
    return text


def _generate_gemini_mcp(prompt: str, *, system: str | None, model: str | None) -> str:
    """Gemini via google-genai, mirroring the Gemini MCP plugin's ask_gemini.

    Same key (GEMINI_API_KEY) and default model as the plugin's server.py.
    Does not apply the plugin's per-session call cap; keep the key on the
    free tier (no billing account) if you need a hard $0 guarantee.
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise LLMError(
            "The 'google-genai' package is required for the gemini_mcp backend. "
            "Install it with: pip install google-genai"
        ) from exc

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise LLMError("GEMINI_API_KEY is not set in the environment.")

    config = types.GenerateContentConfig(system_instruction=system) if system else None
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model or GEMINI_MODEL, contents=prompt, config=config,
        )
    except Exception as exc:
        raise LLMError(f"Gemini request failed for model '{model or GEMINI_MODEL}': {exc}") from exc

    text = response.text
    if not text:
        raise LLMError(f"Gemini returned no text content. Full response: {response}")
    return text
