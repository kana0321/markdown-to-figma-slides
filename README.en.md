# Markdown to Figma Slides

![Markdown to Figma Slides Preview](docs/readme-preview.png)

English: this page / 日本語: [README.md](README.md)

Markdown to Figma Slides is a skill for generating HTML slide decks from Markdown and handing them off to Figma.

When you ask Claude Code, OpenAI Codex, or another coding agent to use this repo, it can handle the whole flow: project initialization, Markdown normalization, template selection, versioned HTML output, theme switching, and optional Figma capture. Each generation creates a versioned snapshot such as `v1`, `v2`, and so on, so previous outputs are not overwritten.

If you are not comfortable with Git yet, start with the [Git workflow guide](docs/git-workflow.md).

## Quick Start

The sample Markdown deck lives at `skills/assets/sample-catalog.md`. Use it first to confirm the pipeline works in your environment.

## Requirements

- Python 3.9 or newer
- A Figma MCP-enabled environment if you want Figma capture

Install the Python dependencies:

```bash
pip3 install jinja2 pyyaml pygments
```

## How to Start

You can begin by asking your coding agent in natural language:

```text
I want to turn a Markdown file into slides.
```

If you want to point to a specific source file:

```text
Generate slides from input/raw/source.md.
```

If you also want design tuning:

```text
I want to create slides from Markdown.
First generate them, then help me adjust colors and spacing.
```

If you want to go all the way through Figma import:

```text
Convert this Markdown file into Figma-ready slides and help me import them into Figma.
```

The standard flow is:

1. Initialize the project
2. Normalize the Markdown
3. Generate versioned HTML slides
4. Preview locally
5. Capture to Figma if requested

## Themes

Themes live under `themes/<name>/` and package the CSS, templates, defaults, and font loading for a visual style.

List available themes:

```bash
python3 scripts/theme.py --project-root . list
```

Show the current theme:

```bash
python3 scripts/theme.py --project-root . current
```

Apply a different theme:

```bash
python3 scripts/theme.py --project-root . apply minimal
```

After changing the theme, regenerate the HTML:

```bash
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

The initial `design.config.yaml` is intentionally minimal. Theme defaults provide the base look, and `design.config.yaml` is meant for project-specific overrides.

## Markdown Rules

### Slide Boundaries

Slide types are inferred from heading levels:

```md
# Presentation Title

## Section Title

### Slide Title

- Bullet content
```

| Heading | Slide Type | Meaning |
| --- | --- | --- |
| `#` | `cover` | Deck title slide |
| `##` | `section` | Section divider slide |
| `###` | `body` | Standard content slide |
| `####` | Column / helper heading | Used inside multi-column slides |

### Supported Markdown Elements

- Nested unordered lists up to three levels
- Ordered lists
- Task lists
- Tables
- Fenced code blocks with syntax highlighting
- Inline code, bold text, and links
- Images copied from `input/raw/images/`

Example image syntax:

```md
![Alt text](images/photo.png)
![Alt text](images/photo.png "Caption")
```

If the last paragraph of a slide begins with `Source:`, `出典:`, `参照:`, or `参考:`, it is rendered as footer attribution.

## Components

You can place special components using HTML comments inside Markdown.

### Card

```md
<!-- card -->
- Key point
<!-- /card -->
```

Accent card:

```md
<!-- card: accent -->
- Highlighted content
<!-- /card -->
```

### Badge

```md
<!-- badge: New -->
<!-- badge: Needs Review; status=warning -->
```

Available `status` values are `info`, `success`, `warning`, and `danger`.

### Callout

```md
> [!NOTE]
> Supporting information.

> [!TIP]
> Recommended approach.
```

### Arrow

```md
<!-- arrow: right -->
<!-- arrow: down; size=sm -->
<!-- arrow: left; color=accent-subtle -->
```

Supported parameters:

| Parameter | Values | Default |
| --- | --- | --- |
| `direction` | `right`, `left`, `up`, `down` | required |
| `size` | `lg`, `sm` | `lg` |
| `color` | `secondary`, `accent-subtle` | `secondary` |

### Steps

Render an ordered list as a horizontal chevron flow:

```md
<!-- steps -->
1. **Define Requirements** Clarify the problem and scope
2. **Design and Build** Implement the solution
3. **Test** Validate with unit and integration tests
4. **Release** Deploy and measure impact
<!-- /steps -->
```

Use `<!-- steps: accent=last -->` to accent the final step.

## Templates

There are 11 built-in templates. `cover`, `section`, and `agenda` are selected automatically from heading levels. For `###` slides, you can force a template with `<!-- slide: template=... -->`.

| Template | Purpose |
| --- | --- |
| `cover` | Cover slide |
| `agenda` | Section list generated from `##` headings |
| `section` | Section divider |
| `body` | General-purpose slide |
| `body-text` | Long-form text slide |
| `body-grid` | Grid layout defined with strict grid comments |
| `body-grid-full` | Grid layout without the standard body header |
| `body-2col` | Two-column layout |
| `body-3col` | Three-column layout |
| `body-code` | Code-focused slide |
| `body-hero` | Full-bleed background image with message |

Template example:

```md
<!-- slide: template=body-text -->

### Detailed Explanation

Long-form body content goes here.
```

### Two Columns

Use `#### Left` and `#### Right`:

```md
<!-- slide: template=body-2col; ratio=6040 -->

### Comparison

#### Left

- Pros

#### Right

- Cons
```

Supported ratios are `4060`, `6040`, or equal-width when omitted.

### Three Columns

Use `#### Col1`, `#### Col2`, and `#### Col3`.

### Body Grid

`body-grid` uses `<!-- grid: ... -->` and `<!-- cell: ... -->` comments:

```md
<!-- slide: template=body-grid -->
<!-- grid: columns=2; rows=2; gap=md -->

<!-- cell: col=1; row=1 -->
Primary message
<!-- /cell -->

<!-- cell: col=2; row=1 -->
Supporting detail
<!-- /cell -->

<!-- cell: col=1; row=2; col_span=2 -->
Bottom summary
<!-- /cell -->

<!-- /grid -->
```

### Body Hero

The first image on the slide is used as the full background:

```md
<!-- slide: template=body-hero -->

### Message

![](images/hero-bg.jpg)

Large message text goes here.
```

## Slide Display Settings

Use slide comments to control display settings:

```md
<!-- slide: compact=true; confidential=true; show_pages=false -->
```

| Setting | Example | Purpose |
| --- | --- | --- |
| `template` | `template=body-2col` | Select a template |
| `ratio` | `ratio=6040` | Set two-column ratio |
| `compact` | `compact=true` | Reduce spacing |
| `confidential` | `confidential=true` | Show the Confidential badge |
| `subtitle` | `subtitle=FY2026 Q1` | Add a subtitle to cover or section slides |
| `show_pages` | `show_pages=false` | Toggle page numbers |
| `eyebrow` | `eyebrow=Overview` | Override the eyebrow label |

## Design Tuning

Visual tuning is controlled with `design.config.yaml`. Color and font changes can be applied without regenerating HTML.

### Colors and Fonts

```yaml
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
```

### Useful Config Areas

- `badge` controls the Confidential badge defaults
- `page_number` controls pagination defaults
- `accent_bar` controls accent bar placement
- `agenda` controls agenda slide generation
- `tokens` lets you override CSS variables directly
- `slides[]` lets you override template and display settings for specific slides

Config precedence from low to high:

1. Defaults in `design.config.yaml`
2. `slides[]` overrides
3. `<!-- slide: ... -->` comments inside Markdown

## Project Layout

The initialized project structure looks like this:

```text
my-slides/
  design.config.yaml
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
  scripts/
  input/
    raw/
      images/
    normalized/
    current.md
  output/
    v1/
      slides/
        pages/*.html
        slides.html
      source/
      SLIDES.md
      manifest.json
    slides.html
```

## Slash Commands

Initialized projects include Claude Code slash commands:

| Command | Purpose |
| --- | --- |
| `/slides-generate` | Generate HTML slides from `input/current.md` |
| `/design-tune` | Apply `design.config.yaml` updates to CSS without regeneration |
| `/figma-capture-run` | Capture the generated slides to Figma and wait for completion |

## Figma Capture

If Figma MCP is available, you can import generated slides into Figma by asking:

```text
Import these slides into Figma.
```

Or run `/figma-capture-run`, which automatically:

1. Starts a local server in `output/`
2. Starts the Figma capture via MCP
3. Polls until completion

## Manual Commands

Most users should let the coding agent run the workflow, but you can also run it manually.

```bash
# Initialize a project
cd /path/to/claude-skills/markdown-to-figma-slides/skills
./scripts/init_project.sh /path/to/my-slides

# Run the full pipeline
cd /path/to/my-slides
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md

# Local preview
cd output
python3 -m http.server 8080
```

Then open `http://localhost:8080/slides.html`.

Step-by-step execution:

```bash
# 1. Normalize
python3 scripts/normalize_md.py --input input/raw/source.md --output input/normalized/source.md
cp input/normalized/source.md input/current.md

# 2. Create a new version number
VERSION=$(python3 scripts/create_version.py --project-root .)

# 3. Sync tokens
python3 scripts/sync_tokens.py --project-root .

# 4. Generate slides
python3 scripts/generate_slides.py --input input/current.md --version $VERSION --project-root .

# 5. Sync versioned tokens into the output
python3 scripts/sync_tokens.py --project-root . --version $VERSION
```

## Troubleshooting

### `jinja2` or `yaml` not found

```bash
pip3 install jinja2 pyyaml pygments
```

### `scripts/` does not exist

Run project initialization first:

```bash
cd /path/to/claude-skills/markdown-to-figma-slides/skills
./scripts/init_project.sh /path/to/my-slides
```

### Slides do not open correctly in the browser

Start an HTTP server inside `output/`:

```bash
cd /path/to/my-slides/output
python3 -m http.server 8080
```

### Older versions disappeared

Outputs are versioned as `v1`, `v2`, and so on. Existing versions are not overwritten.
