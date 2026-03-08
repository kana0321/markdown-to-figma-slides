# Markdown Mapping Reference

この文書は、Markdown の書き方とユーザー向けの制約をまとめたリファレンスです。
内部設計や実装判断は `../docs/body-grid-design.md` と `../docs/theme-design.md` を参照してください。

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

方向付きシェブロン矢印。コンテンツブロック間やカラム内に配置できる。

```md
<!-- arrow: right -->
<!-- arrow: down; size=sm -->
<!-- arrow: left; size=lg; color=accent-subtle -->
```

| パラメータ | 値 | デフォルト |
|---|---|---|
| direction (必須) | `right`, `left`, `up`, `down` | - |
| size | `lg`, `sm` | `lg` |
| color | `secondary`, `accent-subtle` | `secondary` |

マルチカラムテンプレートの `.col` 内に `right` / `left` を配置すると、CSS でカラム間のセパレータとして自動配置される。

## Steps

水平ステップフロー。OL（番号付きリスト）をシェブロン型ブロックとして描画する。

```md
<!-- steps -->
1. **タイトル** 説明テキスト
2. **タイトル** 説明テキスト
3. **タイトル**
<!-- /steps -->
```

- `**太字**` がタイトル、その後のテキストが説明になる。説明がある場合はアクセントカラーの区切り線で区切られる。
- 最初のシェブロンは左端フラット、2番目以降は左にノッチ付き。

| パラメータ | 値 | デフォルト |
|---|---|---|
| accent | `last` (最終ステップをアクセントカラーに) | なし |

```md
<!-- steps: accent=last -->
1. **企画**
2. **設計**
3. **リリース**
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
