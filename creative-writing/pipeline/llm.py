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
this module. See Pipelines/README.md for the full local/native/mcp model.)

librarian.py picks its own backend independently of PIPELINE_LLM_BACKEND
(default "ollama", override via LIBRARIAN_BACKEND) -- the librarian's
model is independent of whichever backend is doing the actual drafting.
"""
import json
import os
import urllib.error
import urllib.request



def _load_dotenv() -> None:
    """Load KEY=VALUE lines from creative-writing/pipeline/.env into os.environ.

    Values in the file override the shell's, so the pipeline's dedicated
    key wins over any GEMINI_API_KEY set elsewhere. Placeholder values
    ("your-key-here") are ignored.
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
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
        if value and value != "your-key-here":
            os.environ[key.strip()] = value


_load_dotenv()

BACKEND = os.environ.get("PIPELINE_LLM_BACKEND", "ollama")

ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.6-flash")
MAX_TOKENS = int(os.environ.get("PIPELINE_MAX_TOKENS", "8000"))


class LLMError(RuntimeError):
    pass


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

    client = anthropic.Anthropic(api_key=api_key)
    kwargs = {
        "model": model,
        "max_tokens": MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
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
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LLMError(
            f"Ollama returned HTTP {exc.code} for model '{model}': {detail}\n"
            f"If the model isn't pulled yet, run: ollama pull {model}"
        ) from exc
    except urllib.error.URLError as exc:
        raise LLMError(
            f"Could not reach Ollama at {OLLAMA_HOST} ({exc.reason}). "
            f"Start it with `ollama serve` (or confirm it's already running as a "
            f"background service), then retry."
        ) from exc
    except (ConnectionResetError, OSError) as exc:
        raise LLMError(
            f"Ollama's connection was reset mid-request ({exc}) -- it may have "
            f"crashed or restarted. Confirm `ollama serve` is still running, then "
            f"retry with `continue <run-id>`."
        ) from exc

    text = body.get("response", "")
    if not text:
        raise LLMError(f"Ollama returned no text content. Full response: {body}")
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
