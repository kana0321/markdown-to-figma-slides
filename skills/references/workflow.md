# Workflow Reference

## 1. Initialize

Create a project from bundled scaffold:

```bash
./scripts/init_project.sh /path/to/my-slides
```

Install dependencies if needed:

```bash
pip3 install jinja2 pyyaml
```

Confirm available themes if needed:

```bash
cd /path/to/my-slides
python3 scripts/theme.py list
python3 scripts/theme.py current --project-root .
```

The scaffold starts with a minimal `design.config.yaml`.
Theme defaults provide the baseline look, and you only add project-specific overrides as needed.

## 2. Run Pipeline

Run all generation steps:

```bash
cd /path/to/my-slides
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

Outputs:
- `output/vN/slides/pages/*.html`
- `output/vN/slides/slides.html`
- `output/vN/SLIDES.md`
- `output/vN/manifest.json`
- `output/vN/source/` (input snapshots + config snapshot)
- `output/slides.html` (latest redirect entry)

## 3. Manual Commands

Step-by-step control:

```bash
# Normalize
python3 scripts/normalize_md.py --input input/raw/xxx.md --output input/normalized/xxx.md
cp input/normalized/xxx.md input/current.md

# Version
VERSION=$(python3 scripts/create_version.py --project-root .)

# Sync tokens from config
python3 scripts/sync_tokens.py --project-root .

# Generate
python3 scripts/generate_slides.py --input input/current.md --version $VERSION --project-root .

# Sync tokens into version output
python3 scripts/sync_tokens.py --project-root . --version $VERSION
```

## 4. Design Tuning (no HTML regeneration)

Switch the active theme:

```bash
python3 scripts/theme.py apply classic --project-root .
```

Edit `design.config.yaml`, theme CSS token files, or `slide.css` directly, then:

```bash
python3 scripts/sync_tokens.py --project-root . --version vN
```

This syncs token overrides and also copies `slide.css` to the version output if changed.

## 5. Preview

```bash
cd output && python3 -m http.server 8080
# Open http://localhost:8080/slides.html
```
