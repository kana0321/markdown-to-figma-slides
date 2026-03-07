#!/usr/bin/env bash
set -euo pipefail

# Run the full slide generation pipeline.
# Usage: ./run_pipeline.sh --project-root /path/to/project --input /path/to/source.md

PROJECT_ROOT="."
INPUT=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-root) PROJECT_ROOT="$2"; shift 2 ;;
    --input) INPUT="$2"; shift 2 ;;
    *) echo "unknown option: $1"; exit 1 ;;
  esac
done

if [ -z "$INPUT" ]; then
  echo "error: --input is required"
  exit 1
fi

PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd)"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

echo "=== Step 1: Normalize markdown ==="
BASENAME="$(basename "$INPUT" .md)"
NORMALIZED="$PROJECT_ROOT/input/normalized/${BASENAME}.md"
python3 "$SCRIPTS_DIR/normalize_md.py" --input "$INPUT" --output "$NORMALIZED"
cp "$NORMALIZED" "$PROJECT_ROOT/input/current.md"

echo "=== Step 2: Determine version ==="
VERSION=$(python3 "$SCRIPTS_DIR/create_version.py" --project-root "$PROJECT_ROOT")
echo "version: $VERSION"

echo "=== Step 3: Sync tokens ==="
python3 "$SCRIPTS_DIR/sync_tokens.py" --project-root "$PROJECT_ROOT"

echo "=== Step 4: Generate slides ==="
python3 "$SCRIPTS_DIR/generate_slides.py" --input "$PROJECT_ROOT/input/current.md" --version "$VERSION" --project-root "$PROJECT_ROOT"

echo "=== Step 5: Sync tokens into version ==="
python3 "$SCRIPTS_DIR/sync_tokens.py" --project-root "$PROJECT_ROOT" --version "$VERSION"

echo "=== Step 6: Copy images ==="
INPUT_DIR="$(cd "$(dirname "$INPUT")" && pwd)"
if [ -d "$INPUT_DIR/images" ] && [ "$(ls -A "$INPUT_DIR/images" 2>/dev/null)" ]; then
  cp -R "$INPUT_DIR/images" "$PROJECT_ROOT/output/$VERSION/slides/images"
  cp -R "$INPUT_DIR/images" "$PROJECT_ROOT/output/$VERSION/slides/pages/images"
  echo "copied: $INPUT_DIR/images -> slides/images + slides/pages/images"
else
  echo "no images found, skipping"
fi

echo "=== Step 7: Snapshot source files ==="
mkdir -p "$PROJECT_ROOT/output/$VERSION/source"
cp "$INPUT" "$PROJECT_ROOT/output/$VERSION/source/input.raw.md"
cp "$NORMALIZED" "$PROJECT_ROOT/output/$VERSION/source/input.normalized.md"
cp "$PROJECT_ROOT/design.config.yaml" "$PROJECT_ROOT/output/$VERSION/source/design.config.yaml"

echo "=== Done ==="
echo "Output: $PROJECT_ROOT/output/$VERSION/"
echo "Preview: cd $PROJECT_ROOT/output && python3 -m http.server 8080"
