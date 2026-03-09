# Theme System Reference

This document is a user-facing reference for the theme system usage rules.

- Execution workflow: `workflow.md`
- Creating a new theme: `theme-authoring.md`
- Visual QA: `visual-qa.md`
- Maintainer-facing design decisions: `../../docs/theme-design.md`

## Current Built-in Themes

- `classic`
- `minimal`
- `gradient-blue`

## Core Principles

Treat the theme system as switching design packages, not just swapping colors.

- The active theme is defined by `design.config.yaml.theme.name`
- The source of truth for render assets is `themes/<name>/`
- The baseline look is defined by theme defaults
- `design.config.yaml` should contain only project-specific overrides

## Directory Layout

```text
project-root/
  design.config.yaml
  shared/
    styles/
      slide.css
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

## Role of `design.config.yaml`

`design.config.yaml` is where project-specific overrides live. It is not where baseline design should be defined.

Minimal example:

```yaml
theme:
  name: "classic"

tokens: {}

slides: []
```

Principles:

- Keep the baseline in theme defaults
- Prefer a setup where the baseline changes naturally when the theme changes
- Add only project-specific adjustments to `design.config.yaml`

## Configuration Resolution Order

```text
engine defaults
-> theme defaults
-> design.config.yaml
-> slide override
-> markdown comment
```

## `theme.yaml` Schema

### Required Fields

- `name`
- `defaults`

### Optional Fields

- `label`
- `description`
- `fonts.google`

### Required Directories

- `themes/<name>/theme.yaml`
- `themes/<name>/styles/`
- `themes/<name>/templates/`

### `name`

- `name` must match the directory name
- A mismatch is an error

### `fonts.google`

V1 supports Google Fonts only.

```yaml
fonts:
  google:
    - family: Noto Sans JP
      weights: [400, 500, 700]
```

Rules:

- `family` is required
- `weights` is optional
- Invalid `weights` entries are ignored individually

### `defaults`

`defaults` can include:

- `global`
- `badge`
- `page_number`
- `accent_bar`
- `agenda`
- `end`
- `tokens`
- `slides`

## Theme CLI

`scripts/theme.py` provides the following commands.

- `list`
- `current`
- `show <name>`
- `apply <name>`

Example:

```bash
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . current
python3 scripts/theme.py --project-root . show minimal
python3 scripts/theme.py --project-root . apply minimal
```

## Token Layer Model

The dependency order is:

```text
primitives -> semantic -> component -> shared slide.css -> theme slide.css
```

### primitives

- Store raw theme-owned values here
- Use `brand-*` / `neutral-*` as the base color vocabulary

### semantic

- Semantic layer referenced by the renderer and components
- In most cases, theme-to-theme differences should be absorbed here

### component

- Component-level tokens
- Pull colors from semantic tokens

## Operational Rules by Change Type

- If you change Markdown, rerun `./scripts/run_pipeline.sh ...`
- If you change templates in the active theme, rerun `./scripts/run_pipeline.sh ...`
- If you change `theme.name`, rerun `./scripts/run_pipeline.sh ...`
- If you change only colors, fonts, or tokens, you can apply it with `python3 scripts/sync_tokens.py --project-root . --version vN`
- If you change CSS in the active theme or `shared/styles/slide.css`, CSS sync is enough

See `workflow.md` for the detailed commands.

## Known limitations

- In `<!-- slide: ... -->`, the keys that currently matter are mainly `template`, `confidential`, `show_source`, `compact`, `ratio`, plus `eyebrow` on body slides and `subtitle` on cover / section slides
- `show_pages`, `caption`, and `status` are not accepted as slide comment keys
- `subtitle` written in a body slide comment is not preserved
- Theme font loading assumes Google Fonts in V1

## Related References

- `workflow.md`
- `markdown-mapping.md`
- `theme-authoring.md`
- `visual-qa.md`
