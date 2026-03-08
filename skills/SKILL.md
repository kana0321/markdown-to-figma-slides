---
name: markdown-to-figma-slides
description: Build and operate a reproducible Markdown-to-HTML slide pipeline for Figma handoff. Use when asked to initialize the slide scaffold, generate versioned HTML slides, tune theme/config-driven styling, or prepare Figma capture.
---

# Markdown to Figma Slides

## Overview

Convert Markdown into versioned HTML slides and, when requested, prepare them for Figma capture.

This skill owns the scaffold initialization flow, the generation pipeline, theme switching, config-driven design tuning, and the capture handoff.

## Use This Skill When

- the user wants to turn Markdown into slides
- the user wants to initialize or operate the bundled slide project scaffold
- the user wants to switch themes or tune `design.config.yaml`
- the user wants to prepare or run Figma capture

## Default Workflow

1. Initialize a project from `assets/project-template/` if the working project does not exist yet.
2. Run `scripts/run_pipeline.sh` to normalize Markdown, create a new version, render HTML, and snapshot sources.
3. Preview from `output/slides.html`.
4. If the user only changed config tokens or CSS, use the lighter design-tuning path instead of full regeneration.
5. If the user requests Figma handoff, follow the capture reference.

Exact commands and rerun rules live in `references/workflow.md`.

## Working Rules

- Keep `design.config.yaml` minimal. Baseline design should come from theme defaults.
- Treat `themes/<name>/` as the source of truth for theme assets.
- Use `references/markdown-mapping.md` for syntax, template, and slide comment questions.
- Use `references/theme-system.md` for theme-system rules and operating constraints.
- Use `../docs/theme-design.md` only when maintainer-facing design decisions matter.
- Use `../docs/maintainer-change-guide.md` before extending parser, renderer, or component contracts.

## References

- Read `references/workflow.md` for initialization, generation, rerun decisions, output locations, and manual commands.
- Read `references/markdown-mapping.md` for Markdown grammar, templates, comments, and `body-grid` rules.
- Read `references/figma-capture.md` for Figma import, capture, and polling instructions.
- Read `references/theme-system.md` for the current user-facing theme-system rules.
- Read `references/theme-authoring.md` when adding or customizing a built-in theme in the project scaffold.
- Read `references/visual-qa.md` when verifying theme-related changes across built-in themes.
- Read `../docs/body-grid-design.md` when the user needs maintainer-facing design rationale for `body-grid`.
- Read `../docs/maintainer-change-guide.md` when a change may affect parser, renderer, CSS layers, or docs.

## Troubleshooting

- If `jinja2` or `yaml` imports fail, install prerequisites with `pip3 install jinja2 pyyaml pygments`.
- If `scripts/` is missing in the project, run `scripts/init_project.sh` first to create the scaffold.
- If preview fails, start a server in `output/` with `python3 -m http.server 8080` and open `http://localhost:8080/slides.html`.

## Bundled Resources

- `assets/project-template/` - Reusable project scaffold
- `scripts/init_project.sh` - Copy scaffold into a new working directory
- `scripts/run_pipeline.sh` - Full pipeline wrapper used by the scaffold
