"""Put the plugin's src/ on sys.path so the tests run with plain `python -m unittest discover` (no pip install)."""
import sys
from pathlib import Path

SRC = str(Path(__file__).resolve().parents[1] / "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
