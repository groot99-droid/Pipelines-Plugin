"""videoeditor: questionnaire-driven video editing recipes on top of ffmpeg + local Whisper."""

__version__ = "0.1.0"


def _tolerate_legacy_consoles() -> None:
    """Progress lines use arrows and dashes. A Windows console on a legacy code page (cp1252) cannot encode them,
    and a print() would raise mid-render. Keep the console's encoding, but replace what it cannot show."""
    import sys

    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(errors="replace")
            except (OSError, ValueError):
                pass


_tolerate_legacy_consoles()
