# Workflow Reference

This document is the source of truth for project initialization, slide generation, rerun decisions, and manual commands.

- Markdown syntax: `markdown-mapping.md`
- Figma import flow: `figma-capture.md`
- Theme system rules: `theme-system.md`

## 1. Initialize

Create a project from bundled scaffold:

```bash
./scripts/init_project.sh /path/to/my-slides
```

Install dependencies if needed:

```bash
pip3 install jinja2 pyyaml pygments
```

Optionally copy the bundled sample deck:

```bash
cp /path/to/repo/skills/assets/sample-catalog.md /path/to/my-slides/input/raw/sample-catalog.md
```

The bundled scaffold starts with sample branding logos configured for both the
cover / end header and the body / agenda footer. The referenced assets live under
`input/raw/images/`.
Use separate `light_src` / `dark_src` assets for each placement, and let the renderer
select between them based on slide type and template surface rules.
Set `cover_logo_enabled: false` and/or `footer_logo_enabled: false` when you want to hide them,
or replace the `light_src` / `dark_src` paths when you want project-specific logos.

Example:

```yaml
branding:
  cover_logo:
    light_src: "images/logo-horizontal-light.png"
    dark_src: "images/logo-horizontal-dark.png"
    alt: "Company logo"
  footer_logo:
    light_src: "images/logo-horizontal-light.png"
    dark_src: "images/logo-horizontal-dark.png"
    alt: "Company logo"
```

Practical rule of thumb:

- built-in theme defaults already choose the recommended surface policy
- `classic` / `minimal`: cover / end default to `light`
- `gradient-blue`: cover / end default to `dark`
- `agenda` / normal `body`: default to `light`
- `body-hero`: defaults to `dark`

Add `branding.surface_defaults` or `branding.template_surface` only when your project
needs to override the active theme's defaults.

Confirm available themes if needed:

```bash
cd /path/to/my-slides
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . current
```

The scaffold starts with a small `design.config.yaml` plus sample branding-logo paths.
Theme defaults still provide the baseline look, and you should only add project-specific overrides.

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

## 3. Rerun Decision

| Changed Item | Required Action |
| --- | --- |
| Markdown content | Rerun `./scripts/run_pipeline.sh ...` |
| Active theme templates (`themes/<name>/templates/*.html.j2`) | Rerun `./scripts/run_pipeline.sh ...` |
| `design.config.yaml` `theme.name` | Rerun `./scripts/run_pipeline.sh ...` |
| Colors, fonts, or tokens in `design.config.yaml` | Run `python3 scripts/sync_tokens.py --project-root . --version vN` |
| `design.config.yaml` `branding.*` (logo paths, alt text, or surface overrides) | Rerun `./scripts/run_pipeline.sh ...` |
| `slides[]` template selection in `design.config.yaml` | Rerun `./scripts/run_pipeline.sh ...` |
| Active theme CSS or `shared/styles/slide.css` | Run `python3 scripts/sync_tokens.py --project-root . --version vN` |

Notes:

- `sync_tokens.py --project-root .` updates the active theme token CSS
- `sync_tokens.py --project-root . --version vN` also updates CSS in the versioned output
- Changing `theme.name` or templates requires HTML regeneration

## 4. Manual Commands

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

## 5. Theme Operations

Switch the active theme:

```bash
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . current
python3 scripts/theme.py --project-root . apply classic
```

Keep `design.config.yaml` thin. The baseline design should come from theme defaults, not from project-level baseline overrides.

For theme-system rules, token layering, and config resolution order, use `theme-system.md`.

## 6. Create or Customize a Theme

When you need a new built-in theme, copy an existing one first:

```bash
cd /path/to/my-slides
cp -R themes/classic themes/my-theme
```

Then inspect and apply it:

```bash
python3 scripts/theme.py --project-root . show my-theme
python3 scripts/theme.py --project-root . apply my-theme
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

Use `theme-authoring.md` for the full authoring rules and `visual-qa.md` for visual verification.

## 7. Preview

```bash
cd output
python3 -m http.server 8080
```

Open `http://localhost:8080/slides.html`.

## 8. Related References

- `markdown-mapping.md` for syntax, templates, comments, and `body-grid`
- `figma-capture.md` for capture flow
- `../docs/body-grid-design.md` for maintainer-facing `body-grid` rationale
- `../docs/maintainer-change-guide.md` for implementation impact by change type
