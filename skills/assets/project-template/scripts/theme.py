#!/usr/bin/env python3
"""Manage project themes."""

from __future__ import annotations

import argparse
import sys
import re
from pathlib import Path

from config import list_themes, load_theme, read_project_theme_name

_THEME_BLOCK_RE = re.compile(r"^theme:\n(?:^[ \t].*\n?)*", re.MULTILINE)


def _config_path(project_root: Path) -> Path:
    return project_root / "design.config.yaml"


def _format_theme_summary(theme) -> str:
    """Format one-line theme summary."""
    label = f" ({theme.label})" if theme.label and theme.label != theme.name else ""
    description = f" - {theme.description}" if theme.description else ""
    return f"{theme.name}{label}{description}"


def _available_theme_names(project_root: Path) -> list[str]:
    """Return available theme names."""
    return [theme.name for theme in list_themes(project_root)]


def _load_theme_or_exit(project_root: Path, theme_name: str):
    """Load a theme or exit with a helpful error."""
    try:
        return load_theme(project_root, theme_name)
    except FileNotFoundError:
        available = _available_theme_names(project_root)
        if available:
            choices = ", ".join(available)
            raise SystemExit(
                f"theme not found: {theme_name}\navailable themes: {choices}"
            )
        raise SystemExit(f"theme not found: {theme_name}\nno themes are available")
    except ValueError as exc:
        raise SystemExit(str(exc))


def _apply_theme(config_path: Path, theme_name: str) -> None:
    """Update or insert the theme block in design.config.yaml."""
    theme_block = f'theme:\n  name: "{theme_name}"\n\n'

    if config_path.exists():
        original = config_path.read_text(encoding="utf-8")
        if _THEME_BLOCK_RE.search(original):
            updated = _THEME_BLOCK_RE.sub(theme_block, original, count=1)
        else:
            updated = theme_block + original
    else:
        updated = theme_block

    config_path.write_text(updated, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage slide themes.")
    parser.add_argument("--project-root", default=".", help="Project root directory")

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List available themes")
    subparsers.add_parser("current", help="Show current theme")
    show_parser = subparsers.add_parser("show", help="Show one theme")
    show_parser.add_argument("theme_name", help="Theme name to inspect")

    apply_parser = subparsers.add_parser("apply", help="Apply a theme")
    apply_parser.add_argument("theme_name", help="Theme name to apply")

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    if args.command == "list":
        themes = list_themes(project_root)
        if not themes:
            print("no themes available")
            return 0
        for theme in themes:
            print(_format_theme_summary(theme))
        return 0

    if args.command == "current":
        current_name = read_project_theme_name(_config_path(project_root))
        theme = _load_theme_or_exit(project_root, current_name)
        print(_format_theme_summary(theme))
        return 0

    if args.command == "show":
        theme = _load_theme_or_exit(project_root, args.theme_name)
        print(f"name: {theme.name}")
        print(f"label: {theme.label or theme.name}")
        print(f"description: {theme.description}")
        print(f"root: {theme.root}")
        print(f"templates: {theme.templates_dir}")
        print(f"styles: {theme.styles_dir}")
        if theme.google_fonts:
            families = ", ".join(font.family for font in theme.google_fonts)
            print(f"google_fonts: {families}")
        else:
            print("google_fonts: none")
        return 0

    if args.command == "apply":
        theme = _load_theme_or_exit(project_root, args.theme_name)
        config_path = _config_path(project_root)
        _apply_theme(config_path, theme.name)
        print(f"applied theme: {theme.name}")
        print(f"config: {config_path}")
        return 0

    print("unknown command", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
