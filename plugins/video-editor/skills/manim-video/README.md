# Manim Video Skill

Production pipeline for mathematical and technical animations using [Manim Community Edition](https://www.manim.community/).

## What it does

Creates 3Blue1Brown-style animated videos from text prompts. The agent handles the full pipeline: creative planning, Python code generation, rendering, scene stitching, and iterative refinement.

## Use cases

- **Concept explainers** — "Explain how neural networks learn"
- **Equation derivations** — "Animate the proof of the Pythagorean theorem"
- **Algorithm visualizations** — "Show how quicksort works step by step"
- **Data stories** — "Animate our before/after performance metrics"
- **Architecture diagrams** — "Show our microservice architecture building up"

## Prerequisites

Python 3.10+, Manim CE (`pip install manim`), LaTeX, ffmpeg.

Check what is installed (the same on Windows, macOS and Linux):

```
python -c "import manim; print(manim.__version__)"
ffmpeg -version
```

Install what is missing with `pip install manim`; LaTeX comes from MiKTeX (Windows), MacTeX (macOS) or TeX Live
(Linux). `scripts/setup.sh` in this folder is a bash convenience for macOS and Linux (on Windows run it under
Git Bash or WSL, or use the commands above):

```bash
bash scripts/setup.sh
```
