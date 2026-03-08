# Body Grid Design

この文書は maintainer 向けの設計メモです。
利用者向けの書き方と入力制約は `../skills/references/markdown-mapping.md` を参照してください。

## Goals / non-goals

### Goals

- `body-grid` を Markdown-to-Figma Slides の正式な layout grammar として追加する
- 同じ grammar を使う headerless variant `body-grid-full` を追加する
- Markdown から可変 grid layout を明示的に記述できるようにする
- `body-2col` / `body-3col` / `body-grid` / `body-grid-full` を内部では同じ grid layout engine に統一する
- parser / renderer / docs / sample / tests を含めて保守可能な contract にする
- strict validation により、曖昧な入力を静かに吸収せず早期に失敗させる

### Non-goals

- auto placement
- `area` 名による grid-template-areas 的指定
- nested grid
- 複数 grid per slide
- CSS 生値入力
- cell 自体の装飾 variant
- line number 付き parser error
- header なしの grid 専用テンプレート

### Design intent

`body-grid` は component ではなく layout system として扱う。
セルは単なる配置箱であり、見た目は中に置く既存 block が担う。

この方針により次を分離する。

- layout の責務
- block/component の責務
- theme の責務

## Final grammar / AST / renderer rules

利用者向けの記法一覧や属性表は `../skills/references/markdown-mapping.md` を基準にし、この文書では設計判断と内部契約を主に扱います。

### User-facing grammar

`body-grid` は `<!-- slide: template=body-grid -->` で opt-in する。
`body-grid-full` は `<!-- slide: template=body-grid-full -->` で opt-in する。

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

<!-- cell: col=1; row=2 -->
Bottom left
<!-- /cell -->

<!-- cell: col=2; row=2 -->
Bottom middle
<!-- /cell -->

<!-- /grid -->
```

### Input contract

利用者向けの属性一覧は `../skills/references/markdown-mapping.md` を参照。
ここでは parser / renderer の設計前提として必要な制約だけを残す。

### `grid` rules

- root `grid` block は 1 slide にちょうど 1 つ
- `grid` 開始タグと終了タグは必須
- 許可属性は `columns`, `rows`, `gap`, `col_gap`, `row_gap`
- `columns` は必須、`1..6` の整数
- `rows` は必須、`1..6` の整数
- `gap` は任意、`sm|md|lg`
- `col_gap` は任意、`sm|md|lg`
- `row_gap` は任意、`sm|md|lg`
- gap 解決順は次の通り
  - `col_gap` があれば横方向に使う
  - `row_gap` があれば縦方向に使う
  - 未指定側には `gap` を使う
  - `gap` も未指定なら `md`

### `cell` rules

- `cell` は `grid` の直下でのみ許可
- `cell` 開始タグと終了タグは必須
- 許可属性は `col`, `row`, `col_span`, `row_span`
- `col`, `row` は必須の正整数
- `col_span`, `row_span` は任意の正整数
- `col_span`, `row_span` のデフォルトは `1`
- `col`, `row` は 1-based

### `gap` mapping

- `sm = 16px`
- `md = 32px`
- `lg = 80px`

この値は既存 body block gap とは意味を分ける。
`body-grid` 用に専用 token を持つ。

例:

- `gap=md` -> row / column ともに `md`
- `gap=md; col_gap=lg` -> column は `lg`, row は `md`
- `col_gap=lg; row_gap=sm` -> column は `lg`, row は `sm`

### Strict validation

次はすべて parser error とする。

- unknown key
- duplicate key
- 不正な型
- 範囲外の `columns` / `rows`
- 不正な `gap`
- `grid` の外に本文がある
- `grid` の直下に `cell` 以外がある
- `cell` が `grid` の外にある
- nested `grid`
- nested `cell`
- `grid` / `cell` の閉じ忘れ
- 閉じ順の逆転
- overlap
- grid 範囲外にはみ出す cell
- `grid` 内に cell が 1 つもない

エラー文は英語で出し、slide title を含める。
V1 では line number は持たない。
複数エラー収集は行わず、最初の 1 件で停止する。

### Allowed content in cells

`cell` の中で許可する block は、既存 body slide と完全一致とする。

- paragraph
- list
- checklist
- table
- codeblock
- callout
- card
- badge
- image
- arrow
- steps
- その他既存 body が扱う block

`cell` 自体は以下を持たない。

- padding
- background
- border

### Internal AST

`Block` を拡張利用し、`type="grid"` と `type="grid_cell"` を扱う。

```python
Block(
  type="grid",
  meta={
    "columns": ["1fr", "1fr", "1fr"],
    "rows": ["1fr", "1fr"],
    "col_gap": "lg",
    "row_gap": "sm",
    "source_kind": "body-grid",
    "declared_columns": 3,
    "declared_rows": 2,
  },
  children=[
    Block(
      type="grid_cell",
      meta={
        "col": 1,
        "row": 1,
        "col_span": 2,
        "row_span": 1,
        "cell_index": 0,
      },
      children=[...],
    ),
  ],
)
```

### AST normalization

user-facing input は整数ベースでも、内部では track 配列に正規化する。

- `columns=3` -> `["1fr", "1fr", "1fr"]`
- `rows=2` -> `["1fr", "1fr"]`

この shape により、将来の可変 track 幅へ拡張しやすくする。

### Legacy `body-2col` / `body-3col`

外部記法は維持する。

- `body-2col`
  - `#### Left`, `#### Right`
  - `ratio` は `equal`, `6040`, `4060` 相当
- `body-3col`
  - `#### Col1`, `#### Col2`, `#### Col3`

ただし parser で同じ grid AST に正規化する。

`body-2col`:

- default -> `["1fr", "1fr"]`
- `ratio=6040` -> `["3fr", "2fr"]`
- `ratio=4060` -> `["2fr", "3fr"]`
- `rows = ["1fr"]`
- `col_gap = "lg"`
- `row_gap = "lg"`

`body-3col`:

- `columns = ["1fr", "1fr", "1fr"]`
- `rows = ["1fr"]`
- `col_gap = "lg"`
- `row_gap = "lg"`

空カラムは空セルとして保持する。
つまり legacy 2col は常に 2 セル、legacy 3col は常に 3 セル構成とする。

### Renderer rules

renderer は grid AST を正本として扱う。

- `body-grid` / `body-grid-full` は CSS Grid で描画
- `grid` は `grid-template-columns` / `grid-template-rows` / `gap` を持つ
- `grid_cell` は `grid-column` / `grid-row` で配置する
- `body-2col` / `body-3col` も同じ grid renderer を通す
- 旧 template は content 受けの薄い wrapper にする

HTML イメージ:

```html
<div
  class="layout-grid"
  style="
    --grid-columns: 1fr 1fr 1fr;
    --grid-rows: 1fr 1fr;
    --grid-col-gap: var(--component-grid-gap-lg);
    --grid-row-gap: var(--component-grid-gap-sm);
  "
>
  <div
    class="grid-cell"
    style="grid-column: 1 / span 2; grid-row: 1 / span 1;"
  >
    ...
  </div>
</div>
```

legacy `body-2col` / `body-3col` は `layout-grid--legacy-cols` の modifier を持ち、既存の column-arrow 振る舞いを維持する。

### Header rule

`body-grid` の header は既存 body と同じ構造を使う。
`body-grid-full` は header を描画せず、main を shell の先頭領域として使う。

- eyebrow
- title

## Deferred items and rationale

### Deferred

- `area` 指定
- auto placement
- CSS の自由入力
- nested grid
- 複数 grid per slide
- cell variant
- line number 付き parse error

### Rationale

#### Why strict grammar

grid は layout language なので、曖昧な推測を入れると壊れたレイアウトに気づきにくい。
そのため、fallback ではなく parse error を優先した。

#### Why `col_span` / `row_span`

一般ユーザーには多少抽象的でも、CSS Grid と概念が揃っていて実装・保守でぶれにくい。
将来の説明や theme 側の理解とも整合する。

#### Why normalize legacy 2col / 3col now

`body-grid` だけを別 engine にすると、layout 系の保守面積が増える。
今回のタイミングで内部統一しておくことで、renderer / QA / 今後の layout 追加がやりやすくなる。

#### Why cells are unstyled

cell まで装飾責務を持つと、layout と component の責務が混ざる。
見た目は既存 block に委ねることで、theme 変更時の影響範囲を抑えやすい。

#### Why `lg=80`

grid gap は body の block gap と意味が違う。
2col 相当の大きな分割でも十分な余白を出したいため、`lg` は 48 ではなく 80 にした。

#### Why split row/column gap

grid では横方向の分割を大きく取りたい一方、縦方向は詰めたいケースが普通にある。
そのため、`gap` 1 本だけではなく `col_gap` / `row_gap` を持てるようにした。
一方で、単純なケースの書きやすさのため `gap` は互換 shorthand として残す。

### Follow-up candidates

- `body-grid` の visual QA screenshot 追加をさらに増やす
- `body-grid` 専用の renderer unit test を追加で厚くする
- `area` 指定が本当に必要になった時点で V2 grammar を検討する
- header なし / 軽量 header の grid-family template を別途設計する
