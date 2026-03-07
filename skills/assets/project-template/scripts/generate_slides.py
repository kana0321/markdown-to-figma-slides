#!/usr/bin/env python3
"""Entry point: generate HTML slides from markdown + design config."""

from __future__ import annotations

import argparse
from pathlib import Path

from config import load_config, load_theme
from parser import parse_markdown
from renderer import render_deck


def main() -> int:
    p = argparse.ArgumentParser(description="Generate HTML slides from markdown.")
    p.add_argument("--input", required=True, help="Markdown input path")
    p.add_argument("--version", required=True, help="Output version (e.g. v1)")
    p.add_argument("--project-root", default=".", help="Project root directory")
    args = p.parse_args()

    root = Path(args.project_root).resolve()
    src = Path(args.input).resolve()
    if not src.exists():
        raise SystemExit(f"input not found: {src}")

    # Load config
    config_path = root / "design.config.yaml"
    config = load_config(config_path)
    theme = load_theme(root, config.theme.name)

    # Parse markdown
    text = src.read_text(encoding="utf-8")
    deck = parse_markdown(text)

    # Render
    output_dir = root / "output"
    render_deck(
        deck,
        config,
        theme,
        theme.templates_dir,
        output_dir,
        args.version,
        src,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
