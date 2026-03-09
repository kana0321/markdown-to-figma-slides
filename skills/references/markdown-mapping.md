# Markdown Mapping Reference

This document is a reference for Markdown authoring rules and user-facing constraints.
For internal design and implementation decisions, see `../docs/body-grid-design.md` and `../docs/theme-design.md`.

## Heading Mapping

- `#` at document start: Cover slide (`.type-display`)
- `##`: Section slide (`.type-section`)
- `###`: Body slide title (`.type-title`)
- `####`: Layout split key in 2col/3col templates, otherwise subtitle (`.type-subtitle`)

## Body Elements

| Markdown | HTML Output | CSS Class |
|---|---|---|
| paragraph | `<div>` | `.type-body` |
| `- ` list | `<ul>` | `.ul` (3-level nesting) |
| `1. ` list | `<div>` | `.ol > .ol-item` |
| `- [x]` / `- [ ]` | `<ul>` | `.checklist > .checklist-item` |
| fenced code | `<div>` | `.codeblock` |
| inline code | `<span>` | `.inline-code` |
| `**bold**` | `<strong>` | - |
| `[text](url)` | `<a>` | `.link` |
| `> [!TYPE]` | `<div>` | `.callout[data-status]` |
| pipe table | `<table>` | `.data-table` |
| `![alt](src "cap")` | `<figure>` / `<div>` | `.image-block` |
| `<!-- card -->` | `<div>` wrapping next block | `.card` |
| `<!-- card: accent -->` | `<div>` wrapping next block | `.card.card--accent` |
| `<!-- badge: text -->` | `<div>` | `.block-badge` |
| `<!-- arrow: direction -->` | `<div>` | `.arrow` |
| `<!-- steps -->...<!-- /steps -->` | `<div>` | `.steps > .steps-item` |

## Arrow

A directional chevron arrow. It can be placed between content blocks or inside columns.

```md
<!-- arrow: right -->
<!-- arrow: down; size=sm -->
<!-- arrow: left; size=lg; color=accent-subtle -->
```

| Parameter | Values | Default |
|---|---|---|
| direction (required) | `right`, `left`, `up`, `down` | - |
| size | `lg`, `sm` | `lg` |
| color | `secondary`, `accent-subtle` | `secondary` |

When `right` or `left` is placed inside `.col` in a multi-column template, CSS automatically positions it as a separator between columns.

## Steps

A horizontal step flow. Ordered lists are rendered as chevron-style blocks.

```md
<!-- steps -->
1. **Title** Description text
2. **Title** Description text
3. **Title**
<!-- /steps -->
```

- `**bold**` becomes the title, and any following text becomes the description. When a description is present, it is separated by an accent-colored divider.
- The first chevron has a flat left edge. Every chevron after that has a left-side notch.

| Parameter | Values | Default |
|---|---|---|
| accent | `last` (highlight the final step with the accent color) | none |

```md
<!-- steps: accent=last -->
1. **Plan**
2. **Design**
3. **Release**
<!-- /steps -->
```

## Callout Status Mapping

| Markdown | `data-status` |
|---|---|
| `[!NOTE]` | `info` |
| `[!TIP]` | `success` |
| `[!WARNING]` | `warning` |
| `[!CAUTION]` | `danger` |

## Template Selection

Explicit comment format:

```md
<!-- slide: template=body-2col; ratio=6040; compact=true -->
```

Accepted keys during parsing / normalization:
`template`, `confidential`, `show_source`, `eyebrow`, `subtitle`, `ratio`, `compact`

Keys that currently affect output:

- `template`
- `confidential`
- `show_source`
- `compact`
- `ratio`
- `eyebrow` on body slides
- `subtitle` on cover / section slides

Rejected as unknown slide comment keys:

- `show_pages`
- `caption`
- `status`

Body slide note:

- `subtitle` on a body slide comment is dropped during parsing and is not preserved in the slide comment payload

## `####` Layout Rules

- Only interpreted as layout keys in 2col/3col templates
- 2-column: `#### Left`, `#### Right`
- 3-column: `#### Col1`, `#### Col2`, `#### Col3`
- Unknown labels treated as normal subtitle headings

## `body-grid` / `body-grid-full` Layout Rules

`body-grid` and `body-grid-full` share the same strict block grammar.

```md
### Example
<!-- slide: template=body-grid -->

<!-- grid: columns=3; rows=2; col_gap=lg; row_gap=sm -->
<!-- cell: col=1; row=1; col_span=2 -->
Main content
<!-- /cell -->
<!-- cell: col=3; row=1; row_span=2 -->
Side content
<!-- /cell -->
<!-- /grid -->
```

`grid` attributes:

| Attribute | Required | Values |
|---|---|---|
| `columns` | yes | integer `1..6` |
| `rows` | yes | integer `1..6` |
| `gap` | no | `sm`, `md`, `lg` (fallback for both directions) |
| `col_gap` | no | `sm`, `md`, `lg` |
| `row_gap` | no | `sm`, `md`, `lg` |

`cell` attributes:

| Attribute | Required | Values |
|---|---|---|
| `col` | yes | positive integer |
| `row` | yes | positive integer |
| `col_span` | no | positive integer, default `1` |
| `row_span` | no | positive integer, default `1` |

Rules:

- `template=body-grid` requires exactly one root `grid` block
- `template=body-grid-full` uses the same grid grammar, but renders without the standard body header
- `gap` applies to both axes unless `col_gap` and/or `row_gap` override one side
- `grid` may contain only `cell` blocks
- content outside `grid` or directly inside `grid` is rejected
- `unknown` attributes, duplicate attributes, invalid values, overlap, and out-of-bounds placement all raise parse errors
- nested `grid` / `cell` blocks are not supported

Maintainer note:

- internal layout-engine decisions and the implementation contract for `body-grid` live in `../docs/body-grid-design.md`
