#!/usr/bin/env python3
"""Normalize raw markdown for slide generation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_VALID_SLIDE_KEYS = {
    "template", "confidential", "show_source",
    "eyebrow", "subtitle", "ratio", "compact",
}
_VALID_CALLOUT_TYPES = {"NOTE", "TIP", "WARNING", "CAUTION"}


def normalize(text: str) -> str:
    """Apply all normalization steps to markdown text."""
    # 1. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    lines = text.split("\n")
    result: list[str] = []

    for line in lines:
        # 2. Remove horizontal rules (--- on its own line)
        if re.match(r"^-{3,}\s*$", line):
            continue

        # 4. Normalize slide comments
        line = _normalize_slide_comment(line)

        # 5. Normalize callout types
        line = _normalize_callout(line)

        # 6. Strip trailing whitespace (preserve trailing double-space for <br>)
        if line.rstrip("\n").endswith("  "):
            line = line.rstrip("\n\r ") + "  "
        else:
            line = line.rstrip()

        result.append(line)

    # 3. Collapse 3+ consecutive blank lines to 2
    text = "\n".join(result)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text


def _normalize_slide_comment(line: str) -> str:
    """Normalize <!-- slide: ... --> comments."""
    m = re.match(r"^(\s*)<!--\s*slide:\s*(.*?)\s*-->(.*)$", line)
    if not m:
        return line

    prefix = m.group(1)
    body = m.group(2)
    suffix = m.group(3)

    pairs: list[tuple[str, str]] = []
    for part in body.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            continue
        key, val = part.split("=", 1)
        key = key.strip().lower()
        val = val.strip()

        if key not in _VALID_SLIDE_KEYS:
            print(f"warning: unknown slide key '{key}', ignoring", file=sys.stderr)
            continue

        # Normalize boolean values
        if key in ("confidential", "show_source", "compact"):
            val = "true" if val.lower() in ("true", "1", "yes") else "false"

        pairs.append((key, val))

    # Sort by key for stable output
    pairs.sort(key=lambda x: x[0])
    normalized = "; ".join(f"{k}={v}" for k, v in pairs)
    return f"{prefix}<!-- slide: {normalized} -->{suffix}"


def _normalize_callout(line: str) -> str:
    """Normalize callout type to uppercase and validate."""
    m = re.match(r"^(>\s*\[!)(\w+)(\].*)$", line)
    if not m:
        return line

    callout_type = m.group(2).upper()
    if callout_type not in _VALID_CALLOUT_TYPES:
        print(f"warning: unknown callout type '{callout_type}', falling back to 'NOTE'", file=sys.stderr)
        callout_type = "NOTE"

    return f"{m.group(1)}{callout_type}{m.group(3)}"


def main() -> int:
    p = argparse.ArgumentParser(description="Normalize markdown for slide generation.")
    p.add_argument("--input", required=True, help="Raw markdown input path")
    p.add_argument("--output", required=True, help="Normalized markdown output path")
    args = p.parse_args()

    src = Path(args.input)
    dst = Path(args.output)

    if not src.exists():
        raise SystemExit(f"input not found: {src}")

    text = src.read_text(encoding="utf-8")
    normalized = normalize(text)

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(normalized, encoding="utf-8")
    print(f"normalized: {src} -> {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
