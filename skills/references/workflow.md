# Workflow Reference

## 1. Initialize

Create a project from bundled scaffold:

```bash
./scripts/init_project.sh /path/to/my-slides
```

Install dependencies if needed:

```bash
pip3 install jinja2 pyyaml pygments
```

Confirm available themes if needed:

```bash
cd /path/to/my-slides
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . current
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
python3 scripts/theme.py --project-root . apply classic
```

Edit `design.config.yaml`, theme CSS token files, theme `slide.css`, or `shared/styles/slide.css` directly, then:

```bash
python3 scripts/sync_tokens.py --project-root . --version vN
```

Current behavior:

- `sync_tokens.py --project-root .` updates the active theme's token CSS files in `themes/<active-theme>/styles/`
- `sync_tokens.py --project-root . --version vN` also syncs token CSS into `output/vN/styles/`
- with `--version`, it also copies theme `slide.css` and `shared/styles/slide.css` into the version output if changed

Template note:

- `body-grid-full` is a headerless variant of `body-grid`
- it uses the same strict `<!-- grid: ... -->` / `<!-- cell: ... -->` grammar
- shared spacing tweaks for `body-grid-full` should stay in `shared/styles/slide.css` and theme-specific values should stay in theme component tokens

Known limitations:

- `show_pages`, `caption`, and `status` are not supported as `<!-- slide: ... -->` keys
- `subtitle` in a body slide comment is dropped during parsing
- Figma capture requires a local HTTP server and external capture script access
- detailed limitations are tracked in `docs/theme-design.md`

## 4.5 Create or Customize a Theme

When you need a new built-in theme, copy an existing one first:

```bash
cd /path/to/my-slides
cp -R themes/classic themes/my-theme
```

Then update `themes/my-theme/theme.yaml` so `name` matches the directory name, adjust CSS and templates, and inspect it with:

```bash
python3 scripts/theme.py --project-root . show my-theme
python3 scripts/theme.py --project-root . apply my-theme
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

Use `docs/theme-authoring.md` in the repo root for the full authoring rules and file responsibilities.

When a theme or shared styling change needs visual verification across themes, use `docs/multi-theme-visual-qa.md` in the repo root.

## 5. Preview

```bash
cd output && python3 -m http.server 8080
# Open http://localhost:8080/slides.html
```
