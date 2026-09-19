#!/usr/bin/env python3
"""The librarian: a file-reading/condensing helper (Ollama or Gemini).

The librarian's only job in this pipeline is to go read the *exact* vault
files a drafter (Claude in the skill, or run_pipeline.py's drafting
backend) wants referenced, and hand back a condensed, logically-structured
Markdown digest -- so the drafter works from a short digest instead of
pulling full raw files into its own context. It never drafts prose itself.

Backend: "ollama" (default) or "gemini_mcp", chosen via --backend or the
LIBRARIAN_BACKEND env var, independent of PIPELINE_LLM_BACKEND -- the
librarian's model is independent of whichever backend is doing the actual
drafting. Quote verification runs the same way for both.

This intentionally lives in creative-writing/pipeline/, NOT in
creative-writing/vault/tools/ alongside vault_search.py: that tool's own
docstring states it is deliberately "stdlib only -- no network calls, no
embeddings, no Ollama dependency." Keeping the vault's own tooling
dependency-free was a deliberate choice; this is a separate,
Ollama-dependent tool in the pipeline's own orchestration layer.

Usage:
    python librarian.py digest <path1> [<path2> ...] [--query "..."] \
        [--out FILE] [--vault PATH] [--model MODEL]
"""
import argparse
import os
import re
import sys
from pathlib import Path

import llm

HERE = Path(__file__).resolve().parent
DEFAULT_MAX_CHARS_PER_FILE = 12000
LIBRARIAN_BACKENDS = {"ollama", "gemini_mcp"}
DEFAULT_BACKEND = os.environ.get("LIBRARIAN_BACKEND", "ollama")


def _default_vault_root() -> Path:
    """Resolve the vault root from spec.yaml's vault_root field, the same
    source of truth run_pipeline.py uses -- avoids hardcoding the vault's
    path/name a second time here."""
    try:
        import yaml
    except ImportError:
        return (HERE / ".." / "vault").resolve()
    with (HERE / "spec.yaml").open("r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return (HERE / spec["vault_root"]).resolve()

LIBRARIAN_PROMPT_TEMPLATE = """\
You are a librarian doing a condensation pass over ONE file from a
creative-writing vault, for another writer who will use your notes to
reference this work without reading it in full themselves.

Focus (if any): {query}

Source file: {path}

--- full text ---
{text}
--- end text ---

Produce a condensed Markdown summary of THIS file only:
- 3 to 6 bullet points capturing what's actually in this file relevant to
  the focus above (or a general summary of its content if no focus was
  given).
- A "Verbatim quotes" list of 1 to 4 short quotes copied EXACTLY,
  character-for-character, from the text above, in quotation marks. Never
  paraphrase inside a quote. Never invent a quote that is not present in
  the source text above -- if nothing is worth quoting, write "(none)".
- Do not add commentary, opinions, or information not present in the
  source text.

Output only the bullets and the Verbatim quotes list, no preamble or
closing remarks.
"""


def _read_source_text(vault_root: Path, rel_path: str, max_chars: int) -> tuple[str, bool]:
    path = vault_root / rel_path
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist.")
    text = path.read_text(encoding="utf-8")
    if len(text) > max_chars:
        return text[:max_chars], True
    return text, False


_QUOTE_LINE_RE = re.compile(r'^\s*[-*]\s*"(.+)"\s*$')
_PUNCT_NORMALIZE = str.maketrans({
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-",
})


def _normalize_for_match(s: str) -> str:
    return " ".join(s.translate(_PUNCT_NORMALIZE).split())


def _verify_quotes(condensed: str, source_text: str) -> str:
    """Check every '- "quote"' line under the model's Verbatim-quotes list
    actually occurs in source_text (tolerant of curly-vs-straight quote/
    apostrophe/dash normalization, since models routinely "clean up" that
    punctuation when reproducing text without actually fabricating content).
    Any quote that still doesn't verify gets flagged inline -- CLAUDE.md's
    "never fabricate a citation" rule applies to this layer too, and a
    silent trust-the-model pass would violate it just as much as inventing
    one outright.
    """
    normalized_source = _normalize_for_match(source_text)
    out_lines = []
    for line in condensed.splitlines():
        m = _QUOTE_LINE_RE.match(line)
        if m and _normalize_for_match(m.group(1)) not in normalized_source:
            out_lines.append(line.rstrip() + "  [UNVERIFIED -- not found in source text, do not cite as exact]")
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


_INLINE_QUOTE_RE = re.compile(r'"([^"\n]{8,300})"')


def verify_citations(text: str, vault_root: Path, candidate_files: list[str]) -> str:
    """General-purpose citation check for FREE-FORM drafted text (e.g. a
    drafting model's references.md), not just the librarian's own
    structured '- "quote"' bullets.

    _verify_quotes() only guards the librarian's own condensation output.
    Nothing stops a downstream drafting model from later inventing an
    entirely new "quote" (with a fabricated line range) while writing its
    own summary from that digest -- observed in practice: a drafting pass
    over a real librarian digest still fabricated a quote attributed to a
    real file that was never in the source text at all. This scans any
    double-quoted span of plausible-quote length in the given text and
    flags any that don't actually occur (normalized) in the combined text
    of candidate_files -- the same fail-loudly-not-silently discipline as
    _verify_quotes, applied one layer downstream where prompt instructions
    alone were not enough to prevent fabrication.
    """
    combined_source = ""
    for rel in candidate_files:
        path = vault_root / rel
        if path.exists():
            combined_source += path.read_text(encoding="utf-8") + "\n"
    normalized_source = _normalize_for_match(combined_source)

    def repl(m):
        quote = m.group(1)
        if _normalize_for_match(quote) in normalized_source:
            return m.group(0)
        return m.group(0) + " [UNVERIFIED CITATION -- not found verbatim in the source files checked; treat as unconfirmed/possibly fabricated]"

    return _INLINE_QUOTE_RE.sub(repl, text)


def condense_file(vault_root: Path, rel_path: str, query: str | None = None,
                   model: str | None = None, max_chars: int = DEFAULT_MAX_CHARS_PER_FILE,
                   backend: str | None = None) -> str:
    """Read one vault file and return a condensed Markdown block for it.

    The '### <path>' heading is added by this code, not the model -- keeps
    citation traceability deterministic rather than trusting the model to
    format it correctly. Every claimed verbatim quote is independently
    checked against the source text before being returned (see
    _verify_quotes) -- the model's own claim that a quote is exact is not
    taken on faith.
    """
    text, truncated = _read_source_text(vault_root, rel_path, max_chars)
    full_text_for_verification = text
    if truncated:
        text += f"\n\n[... truncated at {max_chars} characters ...]"

    prompt = LIBRARIAN_PROMPT_TEMPLATE.format(
        query=query or "(no specific focus given -- general summary)",
        path=rel_path, text=text,
    )
    backend = backend or DEFAULT_BACKEND
    if backend not in LIBRARIAN_BACKENDS:
        raise llm.LLMError(f"Unknown librarian backend '{backend}' -- expected one of {sorted(LIBRARIAN_BACKENDS)}.")
    default_model = llm.GEMINI_MODEL if backend == "gemini_mcp" else llm.OLLAMA_MODEL
    condensed = llm.generate(prompt, backend=backend, model=model or default_model)
    condensed = _verify_quotes(condensed.strip(), full_text_for_verification)
    return f"### {rel_path}\n\n{condensed}\n"


def digest_files(vault_root: Path, rel_paths: list[str], query: str | None = None,
                  model: str | None = None, max_chars: int = DEFAULT_MAX_CHARS_PER_FILE,
                  backend: str | None = None) -> str:
    """Condense a list of vault files into one combined Markdown digest."""
    blocks = []
    for rel_path in rel_paths:
        try:
            blocks.append(condense_file(vault_root, rel_path, query=query, model=model,
                                        max_chars=max_chars, backend=backend))
        except FileNotFoundError as exc:
            blocks.append(f"### {rel_path}\n\n[skipped: {exc}]\n")
    return "\n".join(blocks)


def cmd_digest(args):
    vault_root = Path(args.vault).resolve() if args.vault else _default_vault_root()
    digest = digest_files(vault_root, args.paths, query=args.query, model=args.model, backend=args.backend)
    if args.out:
        Path(args.out).write_text(digest, encoding="utf-8")
        print(f"Wrote digest to {args.out}")
    else:
        print(digest)


def build_arg_parser():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p_digest = sub.add_parser("digest", help="Condense one or more vault files into a Markdown digest.")
    p_digest.add_argument("paths", nargs="+", help="Vault-relative file paths, e.g. 11_Essays/02_The_Architecture_of_Being.md")
    p_digest.add_argument("--query", default=None, help="Optional focus to guide the condensation.")
    p_digest.add_argument("--out", default=None, help="Write the digest to this file instead of stdout.")
    p_digest.add_argument("--vault", default=None, help="Vault root (default: ../vault relative to this file).")
    p_digest.add_argument("--backend", default=None, choices=sorted(LIBRARIAN_BACKENDS),
                          help="Condensation backend (default: LIBRARIAN_BACKEND env var, else ollama). "
                               "gemini_mcp needs GEMINI_API_KEY and `pip install google-genai`.")
    p_digest.add_argument("--model", default=None, help="Override the model (default: OLLAMA_MODEL or GEMINI_MODEL, per backend).")
    p_digest.set_defaults(func=cmd_digest)

    return parser


def main():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except llm.LLMError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
