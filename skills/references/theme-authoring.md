# Theme Authoring Guide

This document is a practical guide for adding or adjusting a theme.

- Theme system usage rules: `theme-system.md`
- Execution workflow: `workflow.md`
- Visual verification: `visual-qa.md`
- Maintainer-facing design decisions: `../../docs/theme-design.md`

## Before You Add a Theme

- Treat a theme as a design package, not just a color swap.
- Keep the baseline design in `theme.yaml.defaults`.
- Keep `design.config.yaml` limited to project-specific overrides.
- It is safer to copy and adjust an existing theme than to build one from scratch.

## Minimal Structure

```text
themes/
  <name>/
    theme.yaml
    styles/
      tokens.primitives.css
      tokens.semantic.css
      tokens.component.css
      slide.css
    templates/
      base.html.j2
      cover.html.j2
      agenda.html.j2
      section.html.j2
      body.html.j2
      body-text.html.j2
      body-grid.html.j2
      body-grid-full.html.j2
      body-2col.html.j2
      body-3col.html.j2
      body-code.html.j2
      body-hero.html.j2
      end.html.j2
```

Required:

- `theme.yaml`
- `styles/`
- `templates/`

## Create a New Theme

First, copy an existing theme.

```bash
cd /path/to/my-slides
cp -R themes/classic themes/my-theme
```

Then update `themes/my-theme/theme.yaml`.

```yaml
name: my-theme
label: My Theme
description: Short summary of the theme

fonts:
  google:
    - family: Outfit
      weights: [400, 500, 700]
    - family: Noto Sans JP
      weights: [400, 500, 700]

defaults:
  global:
    lang: "ja"
    fonts:
      sans: "Outfit, Noto Sans JP, sans-serif"
      mono: "JetBrains Mono, monospace"
    colors:
      accent: "#D4593A"
      bg_default: "#F5F0E8"
      bg_inverse: "#1A1A1A"
      text_primary: "#1A1A1A"
      text_secondary: "#4D4D4D"

  badge:
    enabled: true
    text: "Confidential"
    defaults:
      cover: true
      section: true
      agenda: true
      body: true

  page_number:
    enabled: true
    start: 1
    defaults:
      cover: false
      section: false
      agenda: true
      body: true

  accent_bar:
    defaults:
      cover: "left"
      section: "none"
      agenda: "top"
      body: "top"

  agenda:
    enabled: true

  end:
    enabled: true
    title: "Thank you"
    subtitle: ""

  branding:
    surface_defaults:
      cover: light
      end: light
      agenda: light
      body: light
    template_surface:
      body-hero: dark

  tokens: {}
  slides: []
```

After that, adjust the CSS and templates for the new theme.

```bash
python3 scripts/theme.py --project-root . show my-theme
python3 scripts/theme.py --project-root . apply my-theme
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

## Writing `theme.yaml`

### Required Fields

- `name`
- `defaults`

### Optional Fields

- `label`
- `description`
- `fonts.google`
- branding surface defaults inside `defaults`

### Validation

The loader treats the following as errors:

- `theme.yaml` does not exist
- `theme.yaml` is empty or is not a dictionary
- `name` is missing
- `name` does not match the directory name
- `styles/` is missing
- `templates/` is missing

If `defaults` is not a dictionary, it is treated as empty.

## CSS Layer Responsibilities

The dependency order is:

```text
tokens.primitives.css
-> tokens.semantic.css
-> tokens.component.css
-> shared/styles/slide.css
-> themes/<name>/styles/slide.css
```

### `tokens.primitives.css`

- Raw values owned by the theme implementation
- Use `brand-*` / `neutral-*` as the base color vocabulary

### `tokens.semantic.css`

- Semantic layer referenced by the renderer and components
- Absorb theme-to-theme differences here

### `tokens.component.css`

- Component-level tokens
- Pull colors from semantic tokens

### `slide.css`

- Put theme-specific layout, decoration, and typography overrides here
- Move anything shareable into `shared/styles/slide.css`

## Template Responsibilities

- `base.html.j2` defines the head and shared frame
- Per-slide templates own visual differences
- `agenda.html.j2` is required because there is no fallback

## `design.config.yaml` vs. Theme Defaults

- Define the baseline look in theme defaults
- Define the baseline branding surface policy in theme defaults
- Keep only project-specific overrides in `design.config.yaml`
- Do not move baseline values into config when adding a theme

## Verification Commands

```bash
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . show my-theme
python3 scripts/theme.py --project-root . apply my-theme
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

Check the following:

- Does the new theme appear in `list` and `show`?
- Does `design.config.yaml.theme.name` change after `apply`?
- Does rendering complete successfully?
- Do cover / agenda / section / body / end slides keep sane color, type, and spacing?

## Visual QA

After creating a theme, compare it side by side with the built-in themes by following `visual-qa.md`.

## Common Mistakes

- `theme.yaml.name` does not match the directory name
- `agenda.html.j2` or `styles/` is missing
- Too many baseline values are pushed into `design.config.yaml`, so theme switching stops working cleanly
- A width limit is added without keeping `.main` centered, making headings appear left-shifted
- Component tokens reference primitive colors directly, which breaks responsibility boundaries during theme swaps

## Related References

- `theme-system.md`
- `workflow.md`
- `visual-qa.md`
