#!/usr/bin/env python3
"""Sync design.config.yaml token overrides into CSS token files."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

from config import load_config, load_theme

# Mapping from global.colors keys to CSS variable names (targets semantic layer)
_COLOR_MAP = {
    "accent": "semantic-color-accent-primary",
    "bg_default": "semantic-color-bg-default",
    "bg_inverse": "semantic-color-bg-inverse",
    "text_primary": "semantic-color-text-primary",
    "text_secondary": "semantic-color-text-secondary",
}

# Mapping from global.fonts keys to CSS variable names (targets semantic layer)
_FONT_MAP = {
    "sans": "semantic-font-sans",
    "mono": "semantic-font-mono",
}

# CSS files that contain token definitions
_TOKEN_FILES = [
    "tokens.primitives.css",
    "tokens.semantic.css",
    "tokens.component.css",
]


def _build_overrides(config) -> dict[str, str]:
    """Build a flat dict of CSS variable name -> value from config."""
    overrides: dict[str, str] = {}

    # Global colors
    colors = config.global_.colors
    for key, css_var in _COLOR_MAP.items():
        val = getattr(colors, key, None)
        if val:
            overrides[css_var] = val

    # Global fonts
    fonts = config.global_.fonts
    for key, css_var in _FONT_MAP.items():
        val = getattr(fonts, key, None)
        if val:
            overrides[css_var] = val

    # Explicit token overrides
    overrides.update(config.tokens)

    return overrides


def _apply_overrides(css_text: str, overrides: dict[str, str]) -> str:
    """Apply token overrides to a CSS file's text content."""
    result = css_text
    for var_name, value in overrides.items():
        # Match --var-name: <anything>;
        pattern = re.compile(
            rf"(--{re.escape(var_name)}\s*:\s*)([^;]+)(;)", re.MULTILINE
        )
        result = pattern.sub(rf"\g<1>{value}\3", result)
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="Sync token overrides from design.config.yaml.")
    p.add_argument("--project-root", default=".", help="Project root directory")
    p.add_argument("--version", default="", help="Also sync into output/vN/styles/")
    args = p.parse_args()

    root = Path(args.project_root).resolve()
    config = load_config(root / "design.config.yaml")
    theme = load_theme(root, config.theme.name)
    overrides = _build_overrides(config)

    if not overrides:
        print("no token overrides to apply")
        return 0

    styles_dir = theme.styles_dir
    targets = [styles_dir]

    if args.version:
        version_styles = root / "output" / args.version / "styles"
        if version_styles.is_dir():
            targets.append(version_styles)

    changed = 0
    for target_dir in targets:
        for filename in _TOKEN_FILES:
            filepath = target_dir / filename
            if not filepath.exists():
                continue
            original = filepath.read_text(encoding="utf-8")
            updated = _apply_overrides(original, overrides)
            if updated != original:
                filepath.write_text(updated, encoding="utf-8")
                changed += 1
                print(f"updated: {filepath}")

    # Copy slide.css to version snapshot (not a token file, but needed for CSS-only edits)
    if args.version:
        version_styles = root / "output" / args.version / "styles"
        slide_src = styles_dir / "slide.css"
        slide_dst = version_styles / "slide.css"
        if slide_src.exists() and version_styles.is_dir():
            if not slide_dst.exists() or slide_src.read_bytes() != slide_dst.read_bytes():
                shutil.copy2(slide_src, slide_dst)
                changed += 1
                print(f"copied: {slide_dst}")

    if not changed:
        print("no changes needed")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
