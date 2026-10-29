#!/usr/bin/env python3
"""Run the videoeditor CLI from a plugin checkout or an installed plugin cache, without pip-installing it.

    python <plugin-root>/bin/ve.py doctor
    python <plugin-root>/bin/ve.py ask my_video.mp4
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from videoeditor.cli import main  # noqa: E402

if __name__ == "__main__":
    main()
