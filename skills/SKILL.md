---
name: markdown-to-figma-slides
description: Build and operate a reproducible Markdown-to-HTML slide pipeline for Figma handoff. Use when asked to normalize raw markdown with slide rules, generate versioned slide HTML files per page and all-in-one, sync CSS tokens from design config, and prepare Figma capture and polling workflow.
---

# Markdown to Figma Slides

## Overview

Convert Markdown into versioned HTML slides and capture them to Figma.
Uses a design config file, theme-based CSS/template assets, and Jinja2 templates for reproducible, tunable output.

## Quick Start

Prerequisites:

- Python 3.9+
- `jinja2`
- `pyyaml`
- `pygments` (syntax highlighting)

Install dependencies if needed:

```bash
pip3 install jinja2 pyyaml pygments
```

1. Initialize a project scaffold.

```bash
./scripts/init_project.sh /path/to/my-slides
```

2. Place your markdown in `input/raw/` and run the pipeline from the project.

```bash
cd /path/to/my-slides
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

3. Preview locally.

```bash
cd /path/to/my-slides/output && python3 -m http.server 8080
```

4. Capture to Figma (use Figma MCP).

## Architecture

### File Structure

```
project-root/
  design.config.yaml         # Project settings + active theme selection
  themes/
    classic/
      theme.yaml             # Theme metadata and defaults
      styles/                # Theme CSS tokens + layout
      templates/             # Theme Jinja2 templates
  scripts/
    generate_slides.py       # Entry point
    parser.py                # Markdown -> AST
    renderer.py              # AST -> HTML via Jinja2
    models.py                # AST data structures
    config.py                # Config loader + resolver
    normalize_md.py          # Markdown pre-processing
    create_version.py        # Version number management
    sync_tokens.py           # Config -> CSS token sync
  input/
    raw/                     # Original markdown files
    normalized/              # Pre-processed markdown
    current.md               # Active generation source
  output/
    vN/                      # Versioned snapshots
      slides/pages/*.html    # Per-page HTML
      slides/slides.html     # All-in-one (capture entry)
      source/                # Snapshot of inputs
      SLIDES.md              # Slide manifest (human readable)
      manifest.json          # Machine readable manifest
    slides.html              # Redirect to latest version
```

### Pipeline

```
Markdown -> normalize_md.py -> parser.py (AST) -> renderer.py (HTML)
                                                       |
                                design.config.yaml + active theme assets
```

### Design Tuning

Three ways to adjust design:

1. **`design.config.yaml`** - Keep project-specific overrides such as active theme, token overrides, and slide overrides
2. **`design.config.yaml.theme.name`** - Switch the whole design theme
3. **Theme CSS files** - Direct CSS variable edits inside `themes/<name>/styles/`

Run `sync_tokens.py` to apply config changes to CSS files.
HTML re-generation is only needed when markdown content changes.

By default, the scaffold's `design.config.yaml` should stay minimal.
Theme defaults define the baseline design, and `design.config.yaml` is mainly for project-specific overrides.

Theme management:

```bash
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . current
python3 scripts/theme.py --project-root . apply classic
```

### Templates (9 types)

| Template | Usage |
|---|---|
| `cover` | Title slide |
| `agenda` | Auto-generated section list |
| `section` | Section divider (dark bg) |
| `body` | General purpose |
| `body-text` | Long-form text |
| `body-2col` | Two columns (ratio: 4060/6040/equal) |
| `body-3col` | Three columns |
| `body-code` | Code-focused |
| `body-hero` | Full background image + message |

### Markdown Elements (15 types)

Headings (#-####), tables, code blocks, inline code, callouts,
unordered lists (3-level nesting), ordered lists, bold, links,
checkbox lists, cards (`<!-- card -->`), badges (`<!-- badge: text -->`),
images, arrows (`<!-- arrow: direction -->`),
steps (`<!-- steps -->...<!-- /steps -->`).

### Config Priority

```
Markdown <!-- slide: ... --> > design.config.yaml slides[] > theme defaults > engine defaults
```

## References

- Read `references/workflow.md` when you need exact commands, manual step execution, or output locations.
- Read `references/markdown-mapping.md` when the user asks how markdown maps to layouts, templates, or special comments.
- Read `references/figma-capture.md` when the user wants Figma import, capture, or polling instructions.
- Read `../docs/theme-authoring.md` when the user wants to add or customize a built-in theme in the project scaffold.

## Troubleshooting

- If `jinja2` or `yaml` imports fail, install prerequisites with `pip3 install jinja2 pyyaml pygments`.
- If `scripts/` is missing in the project, run `scripts/init_project.sh` first to create the scaffold.
- If preview fails, start a server in `output/` with `python3 -m http.server 8080` and open `http://localhost:8080/slides.html`.

## Bundled Resources

- `assets/project-template/` - Reusable project scaffold
- `scripts/init_project.sh` - Copy scaffold into a new working directory
- `scripts/run_pipeline.sh` - Full pipeline: normalize, version, generate, sync, snapshot
