#!/usr/bin/env python3
"""Determine the next version number from existing output directories."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def next_version(output_dir: Path) -> str:
    """Return the next version string (e.g. 'v3') based on existing vN directories."""
    existing = []
    if output_dir.is_dir():
        for d in output_dir.iterdir():
            if d.is_dir():
                m = re.match(r"^v(\d+)$", d.name)
                if m:
                    existing.append(int(m.group(1)))
    return f"v{max(existing) + 1}" if existing else "v1"


def main() -> int:
    p = argparse.ArgumentParser(description="Print next version number.")
    p.add_argument("--project-root", default=".", help="Project root directory")
    args = p.parse_args()

    root = Path(args.project_root).resolve()
    output_dir = root / "output"
    version = next_version(output_dir)
    print(version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
