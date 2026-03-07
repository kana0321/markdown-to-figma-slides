#!/usr/bin/env bash
set -euo pipefail

# Initialize a new slide project from the bundled template.
# Usage: ./init_project.sh /path/to/new-project

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="${SKILL_DIR}/assets/project-template"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <project-dir>"
  exit 1
fi

TARGET="$1"

if [ -d "$TARGET" ]; then
  echo "error: directory already exists: $TARGET"
  exit 1
fi

echo "creating project: $TARGET"
cp -R "$TEMPLATE_DIR" "$TARGET"

# Ensure directories exist
mkdir -p "$TARGET/output"
mkdir -p "$TARGET/input/raw/images"
mkdir -p "$TARGET/input/normalized"

# Ensure run_pipeline.sh is executable
chmod +x "$TARGET/scripts/run_pipeline.sh"

echo "done. Next steps:"
echo "  1. Place your markdown in $TARGET/input/raw/"
echo "  2. Place images in $TARGET/input/raw/images/"
echo "  3. Run: cd $TARGET && ./scripts/run_pipeline.sh --project-root . --input input/raw/your-file.md"
