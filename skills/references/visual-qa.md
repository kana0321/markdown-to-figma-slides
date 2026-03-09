# Multi-Theme Visual QA

This document describes the operating procedure for checking visuals after adding a theme or making theme-related changes.

- Execution workflow: `workflow.md`
- Theme creation: `theme-authoring.md`
- Semi-automated runner: `../scripts/run_visual_qa.py`
- Maintainer-facing change guidance: `../../docs/maintainer-change-guide.md`

## What This Procedure Checks

Automated tests only check the following:

- Whether rendering succeeds
- Whether the output files are generated as expected

This procedure goes beyond that and checks the visual result itself.

- Overflow, crowding, and broken spacing
- Readability in both light and dark contexts
- Whether semantic-token responsibilities are preserved
- Whether shared CSS and theme overrides stay cleanly separated

## Standard Input

Use `skills/assets/sample-catalog.md` as the standard comparison input.

Why:

- It includes cover / agenda / section / end slides
- It includes `body`, `body-text`, `body-2col`, `body-3col`, `body-grid`, `body-grid-full`, `body-code`, and `body-hero`
- It covers a broad set of content types: list, table, code block, callout, card, badge, image, arrow, and steps

## Target Themes

Current built-in themes:

- `classic`
- `minimal`
- `gradient-blue`

When you add a new theme, compare it with the same procedure alongside these three built-in themes.

## Recommended: Use the Semi-Automated Runner

Run the following from the repo root.

```bash
python3 skills/scripts/run_visual_qa.py
```

What this script does:

- Creates a temporary workspace with a verification project
- Renders the built-in themes in sequence using `sample-catalog.md` as input
- Captures screenshots of representative pages
- Generates an HTML comparison report, `summary.json`, and `notes.md`

Main options:

```bash
python3 skills/scripts/run_visual_qa.py --workspace /tmp/slides-qa-run
python3 skills/scripts/run_visual_qa.py --themes classic minimal gradient-blue
python3 skills/scripts/run_visual_qa.py --skip-screenshots
```

Notes:

- Capturing screenshots requires the `playwright` CLI and installed browsers
- In environments where browsers cannot be launched, use `--skip-screenshots` to run rendering and report generation first
- `report/notes.md` is a useful per-run notes template

## Manual Verification Steps

### 1. Prepare a Working Project

```bash
./skills/scripts/init_project.sh /tmp/my-slides-qa
cp skills/assets/sample-catalog.md /tmp/my-slides-qa/input/raw/sample-catalog.md
```

### 2. Render Each Theme

```bash
cd /tmp/my-slides-qa
python3 scripts/theme.py --project-root . apply classic
./scripts/run_pipeline.sh --project-root . --input input/raw/sample-catalog.md
python3 scripts/theme.py --project-root . apply minimal
./scripts/run_pipeline.sh --project-root . --input input/raw/sample-catalog.md
```

### 3. Preview the Output

```bash
cd /tmp/my-slides-qa/output
python3 -m http.server 8080
```

Open `http://localhost:8080/slides.html`.

## Verification Checklist

- Cover / section / agenda / end slides remain intact across themes
- `body-text`, `body-2col`, `body-3col`, `body-grid`, `body-grid-full`, `body-code`, and `body-hero` still work correctly
- Headings and `.main` centering are not broken
- Code blocks and tables remain readable
- Card / callout / badge / arrow / steps / image contrast remains acceptable
- Shared CSS changes do not depend on a single theme

## Known Noise

- The `body-2col` sample text contains `` `#### Left` `` and `` `#### Right` `` as explanatory inline code
- That comes from the explanatory text in `skills/assets/sample-catalog.md` and should not be treated as a theme-specific defect
- `#### Col1` / `#### Col2` / `#### Col3` in `body-3col` are routing headings and are not an issue by themselves
- If `body-grid` / `body-grid-full` looks broken, suspect a parser or renderer regression before blaming theme differences

## Verification Scope by Change Type

- Added a theme: compare all templates against the built-in themes
- Changed token layers or shared CSS: verify all existing built-in themes
- Changed only one theme's template or `slide.css`: focus on that theme, but also check for spillover into shared behavior

## How to Record Results

- Record findings in `report/notes.md`
- Keep `summary.json` and screenshots as comparison material for each run

## Related References

- `theme-system.md`
- `theme-authoring.md`
- `workflow.md`
