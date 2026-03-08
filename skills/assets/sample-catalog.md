# Component Catalog

<!-- slide: subtitle=All templates & components at a glance -->


## テンプレート

<!-- slide: subtitle=スライドレイアウトテンプレート -->
<!-- -->

### ボディ（デフォルト）

標準のボディテンプレートは、アイブロウ付きのタイトルヘッダーに続いてコンテンツブロックを表示します。この最も基本的なレイアウトです。

- アイブロウは親セクションのタイトルを自動継承
- コンテンツは標準の余白で縦に並ぶ
- このカタログに掲載されている全コンポーネントに対応

### ボディテキスト

<!-- slide: template=body-text -->

ボディテキストテンプレートは、可読性を重視したゆったりとした行間を使用します。箇条書きやデータよりも、文章が中心のスライドに最適です。

段落は `type-body-spacious` スタイルで描画され、テキストに余裕を持たせます。リストやテーブルをあまり使わず、テキスト主体のスライドに適しています。

### 2カラムレイアウト（50:50）

<!-- slide: template=body-2col -->

#### Left

デフォルトの2カラムはコンテンツを均等に分割します。

- すべてのブロックコンポーネントに対応
- 各カラムは独立してフロー

#### Right

`#### Left` と `#### Right` の見出しでカラム間にコンテンツを振り分けます。

- リスト、テーブル、カードなど全対応
- 矢印でカラム間を繋げることも可能

### 2カラムレイアウト（60:40）

<!-- slide: template=body-2col; ratio=6040 -->

#### Left

`ratio=6040` オプションで左カラムにより多くのスペースを割り当てます。メインコンテンツを強調しつつ、補足情報を並べたい場合に有効です。

- メインの説明はこちらに配置
- より広いスペースで詳細に記述

#### Right

狭い右カラムの用途：

- 要約ポイント
- 主要指標
- 補足メモ

### 2カラムレイアウト（40:60）

<!-- slide: template=body-2col; ratio=4060 -->

#### Left

- 概要
- 背景
- ナビゲーション

#### Right

`ratio=4060` オプションは強調を逆にします。右カラムがより広くなり、左はコンパクトなサイドバーとして機能します。

狭いラベルやカテゴリカラムから詳細コンテンツに導くレイアウトに最適です。

### 3カラムレイアウト

<!-- slide: template=body-3col -->

#### Col1

**企画**

プロジェクトの目標とスコープを定義します。

- 要件定義
- スケジュール
- リソース

#### Col2

**開発**

機能を開発し、デザインを反復改善します。

- プロトタイピング
- 実装
- テスト

#### Col3

**リリース**

デプロイ、監視、フィードバック収集を行います。

- 公開
- モニタリング
- 改善サイクル

### ボディグリッド（2x2）

<!-- slide: template=body-grid -->

<!-- grid: columns=2; rows=2; gap=sm -->

<!-- cell: col=1; row=1 -->
主要論点をコンパクトに並べる基本 2x2 グリッドです。

- 各セルは既存 body block をそのまま使えます
- `gap=sm` は高密度な情報整理向けです
<!-- /cell -->

<!-- cell: col=2; row=1 -->
> [!TIP]
> セル自体は装飾を持たないので、強調したい場合は card や callout を中で使います。
<!-- /cell -->

<!-- cell: col=1; row=2 -->
| 指標 | 値 |
|---|---|
| MRR | 12.4M |
| NRR | 118% |
<!-- /cell -->

<!-- cell: col=2; row=2 -->
1. **整理** 情報の種類を分ける
2. **配置** セル単位で視線を制御する
3. **強調** 必要な要素だけ装飾する
<!-- /cell -->

<!-- /grid -->

### ボディグリッド（spanあり）

<!-- slide: template=body-grid -->

<!-- grid: columns=3; rows=2; col_gap=lg; row_gap=md -->

<!-- cell: col=1; row=1; col_span=2 -->
大きい主役領域をつくるには `col_span` / `row_span` を使います。

<!-- card: accent -->
メインメッセージを横長のセルにまとめると、2col より自由に強弱を付けられます。
<!-- /card -->
<!-- /cell -->

<!-- cell: col=3; row=1; row_span=2 -->
#### 補助情報

- 右側に縦長の補助列
- FAQ
- 制約条件
- 参考リンク
<!-- /cell -->

<!-- cell: col=1; row=2 -->
<!-- badge: rollout -->
段階導入
<!-- /cell -->

<!-- cell: col=2; row=2 -->
段階的にロールアウトし、反応を見ながら機能を広げます。
<!-- /cell -->

<!-- /grid -->

### ボディグリッド（余白を方向別に調整）

<!-- slide: template=body-grid -->

<!-- grid: columns=3; rows=2; col_gap=lg; row_gap=sm -->

<!-- cell: col=1; row=1; row_span=2 -->
<!-- card: accent -->
**左右の区切りを強める**

- `col_gap=lg`
- カラム間の余白を大きく取る
- 左右のまとまりを見分けやすくする
<!-- /card -->
<!-- /cell -->

<!-- cell: col=2; row=1; col_span=2 -->
横方向はゆったり、縦方向は詰め気味にしたい時の例です。

| 設定 | 値 |
|---|---|
| `col_gap` | `lg` |
| `row_gap` | `sm` |
<!-- /cell -->

<!-- cell: col=2; row=2 -->
上下の距離は小さいままなので、関連する情報をひとまとまりで読ませやすくなります。
<!-- /cell -->

<!-- cell: col=3; row=2 -->
> [!TIP]
> 左右はしっかり分けたいが、上下はつながって見せたい時に向いています。
<!-- /cell -->

<!-- /grid -->

### ヒーロー

<!-- slide: template=body-hero -->

![都市風景](https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1920&q=80 "Photo by Pedro Lastra on Unsplash")

オーバーレイテキスト付きの大型ビジュアル

### コードブロックテンプレート

<!-- slide: template=body-code -->

```python
from dataclasses import dataclass

@dataclass
class Slide:
    type: str
    title: str = ""
    blocks: list = None

    def render(self) -> str:
        """スライドをHTML文字列にレンダリング"""
        template = load_template(self.type)
        return template.render(slide=self)
```


## コンポーネント

<!-- slide: subtitle=スライドの構成要素 -->
<!-- -->

### 箇条書きリスト（ul）

- レベル1の項目はプライマリマーカースタイルを使用
- ネストは最大3階層まで対応
  - レベル2の項目は1段インデント
  - 親リストのスタイルを継承
    - レベル3は最大の深さ
    - これ以上のネストはこのレベルに制限
- レベル1に戻る

### 番号付きリスト（ol）

1. **定義** プロジェクトのスコープと目標を定める
2. **設計** アーキテクチャとUXを設計する
3. **開発** イテレーティブなスプリントで開発する
4. **テスト** 全環境で徹底的にテストする
5. **デプロイ** モニタリング付きで本番環境にリリース

### チェックリスト

- [x] プロジェクトキックオフミーティング完了
- [x] 要件定義書の承認
- [x] デザインモックアップのレビュー
- [ ] 開発スプリント1
- [ ] QAテストフェーズ
- [ ] ステークホルダー承認

### データテーブル

| カテゴリ | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| 売上 | 1.2億円 | 1.5億円 | 1.8億円 | 2.1億円 |
| ユーザー数 | 12,000 | 15,400 | 19,200 | 24,800 |
| NPS | 72 | 75 | 78 | 82 |
| 解約率 | 3.2% | 2.8% | 2.4% | 2.1% |

### コードブロック

```javascript
// フェンスコードブロックは言語ラベル付きで表示
async function fetchSlides(deckId) {
  const res = await fetch(`/api/decks/${deckId}/slides`);
  const data = await res.json();
  return data.slides.map(s => ({
    id: s.id,
    title: s.title,
    template: s.template ?? "body",
  }));
}
```

### インライン書式

このスライドでは **太字テキスト** による強調、`インラインコード` による技術用語の表記、[ハイパーリンク](https://example.com) による参照を示します。

組み合わせも可能です。**[太字リンク](https://example.com)** はCTA的な参照に使えます。`useState()` や `design.config.yaml` のようなインラインコードはモノスペースフォントで表示されます。

### コールアウト（NOTE）

> [!NOTE]
> 補足情報を提供するためのコールアウトです。本文の理解を助けるが、必須ではない情報に使います。

### コールアウト（TIP）

> [!TIP]
> ベストプラクティスや推奨されるアプローチを示すコールアウトです。実践的なアドバイスに最適です。

### コールアウト（WARNING）

> [!WARNING]
> 無視すると問題が発生する可能性のある事項を示すコールアウトです。注意が必要です。

### コールアウト（CAUTION）

> [!CAUTION]
> 危険または破壊的な操作を警告するコールアウトです。最も強い警告レベルです。

### カード

<!-- card -->
カードはコンテンツブロックをボーダー付きのコンテナで囲みます。関連情報を視覚的にグループ化し、注目を集めます。

- `<!-- card -->` で開始
- `<!-- /card -->` で終了
- 内部にあらゆるブロック要素を配置可能
<!-- /card -->

### カード（アクセントバリアント）

<!-- card: accent -->
アクセントバリアントは、テーマのアクセントカラーを背景とボーダーに適用し、標準カードよりも目立たせます。

- `<!-- card: accent -->` で開始
- 重要なポイントやハイライトに最適
<!-- /card -->

### カード（アイブロウ付き）

<!-- card: accent; eyebrow=重要ポイント -->
カードは `<!-- card: accent; eyebrow=ラベル -->` でアイブロウラベルを設定できます。アクセントカラーでカード上部に表示されます。
<!-- /card -->

### バッジ

<!-- badge: 新規 -->

<!-- badge: 安定版; status=success -->

<!-- badge: ベータ; status=warning -->

<!-- badge: 非推奨; status=danger -->

バッジはインラインのステータスラベルです。`status` を `info`（デフォルト）、`success`、`warning`、`danger` に設定してカラーを変更できます。

### ステップ

<!-- steps -->
1. **企画** スコープと要件を定義
2. **設計** モックアップとアーキテクチャを作成
3. **開発** イテレーティブなスプリントで実装
4. **テスト** 品質とパフォーマンスを検証
5. **リリース** 本番環境にデプロイ
<!-- /steps -->

### ステップ（accent=last）

<!-- steps: accent=last -->
1. **調査** ユーザーインサイトを収集
2. **発想** ソリューションを探索
3. **検証** ユーザーでテスト
4. **公開** ローンチ
<!-- /steps -->

### 矢印

<!-- slide: template=body-2col -->

#### Left

**方向**

<!-- arrow: right -->

<!-- arrow: down -->

<!-- arrow: left -->

<!-- arrow: up -->

#### Right

**サイズとカラーオプション**

<!-- arrow: right; size=lg -->

<!-- arrow: right; size=sm -->

<!-- arrow: right; size=lg; color=accent-subtle -->

<!-- arrow: right; size=sm; color=accent-subtle -->

### 画像

![サンプル画像](https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80 "雲海と山岳風景")

### 画像（キャプションなし）

![キャプションなしのシンプルな画像](https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80)


## メタ機能

<!-- slide: subtitle=スライドレベルの設定オプション -->
<!-- -->

### 社外秘バッジ

<!-- slide: confidential=true -->

`confidential=true` をスライドコメントに設定すると、右上にバッジが表示されます。バッジのテキストとスタイルは `design.config.yaml` で設定します。

- スライドごとの上書き: `<!-- slide: confidential=true -->`
- デフォルト動作は `badge.defaults` で設定
- バッジテキストはカスタマイズ可能（例: "Confidential"、"社外秘"）

### コンパクトモード

<!-- slide: compact=true -->

コンパクトモードはフォントサイズと余白を縮小し、より多くのコンテンツを収めます。情報密度の高いスライドに有効です。

| 項目 | 通常 | コンパクト |
|---|---|---|
| 本文 | type-body | type-caption サイズ |
| リードテキスト | type-body-lead | type-body サイズ |
| サブタイトル | type-subtitle | type-body サイズ |
| コード | type-code | type-note サイズ |
| 余白 | gap-lg | gap-md |

- リストやアジェンダ項目の余白も縮小
- リファレンスや詳細比較スライドに最適

### カスタムアイブロウ

<!-- slide: eyebrow=カスタムラベル -->

`eyebrow` パラメータはセクションタイトルの自動継承を上書きします。スライド固有のカテゴリ分けに使用します。

- デフォルト: 親 `##` セクションのタイトルを継承
- 上書き: `<!-- slide: eyebrow=任意のテキスト -->`
- アクセントカラーでスライドタイトルの上に表示

### サブタイトル（セクション用）

サブタイトルは `##` セクションスライドと `#` カバースライドで使用できます。上部の「メタ機能」セクションヘッダーで実例を確認できます。

- カバー: `<!-- slide: subtitle=サブタイトル -->`
- セクション: `<!-- slide: subtitle=サブタイトル -->`
- セカンダリテキストカラーでメインタイトルの下に表示

### 出典・参照フッター

このスライドは出典の自動抽出機能を示します。スライド末尾の段落が所定のプレフィックスで始まる場合、フッターに移動されます。

出典: 総務省「情報通信白書」令和7年版


## Templates

<!-- slide: subtitle=Slide layout templates -->
<!-- -->

### Body (Default)

The standard body template renders a title with eyebrow header, followed by content blocks. This slide demonstrates the default layout with paragraph text.

- Eyebrow is auto-inherited from the parent section title
- Content flows vertically with standard spacing
- Supports all components listed in this catalog

### Body Text

<!-- slide: template=body-text -->

Body Text template uses spacious line-height for readability. Ideal for slides where the main content is running prose rather than bullet points or data.

Paragraphs are rendered with `type-body-spacious` styling, giving text more breathing room. Use this template when your slide is primarily textual explanation without heavy use of lists or tables.

### 2-Column Layout (50:50)

<!-- slide: template=body-2col -->

#### Left

Default 2-column splits content evenly.

- Supports all block components
- Each column flows independently

#### Right

Use `#### Left` and `#### Right` headings to divide content between columns.

- Lists, tables, cards all work
- Arrows can bridge columns

### 2-Column Layout (60:40)

<!-- slide: template=body-2col; ratio=6040 -->

#### Left

The `ratio=6040` option gives the left column more space. Useful when primary content needs emphasis while supporting info sits alongside.

- Main explanation goes here
- More room for detailed content

#### Right

The narrower right column works well for:

- Summary points
- Key metrics
- Side notes

### 2-Column Layout (40:60)

<!-- slide: template=body-2col; ratio=4060 -->

#### Left

- Overview
- Context
- Navigation

#### Right

The `ratio=4060` option reverses the emphasis. The right column gets more space, while the left serves as a compact sidebar.

Useful for layouts where a narrow label or category column leads into detailed content.

### 3-Column Layout

<!-- slide: template=body-3col -->

#### Col1

**Plan**

Define goals and scope for the project.

- Requirements
- Timeline
- Resources

#### Col2

**Build**

Develop features and iterate on design.

- Prototyping
- Development
- Testing

#### Col3

**Ship**

Deploy, monitor, and gather feedback.

- Release
- Monitoring
- Iteration

### Body Grid (2x2)

<!-- slide: template=body-grid -->

<!-- grid: columns=2; rows=2; gap=sm -->

<!-- cell: col=1; row=1 -->
This is the basic 2x2 grid for compact information grouping.

- Each cell accepts the same body blocks as a normal slide
- `gap=sm` works well for dense content
<!-- /cell -->

<!-- cell: col=2; row=1 -->
> [!TIP]
> Cells stay unstyled on purpose, so emphasis should come from cards or callouts placed inside them.
<!-- /cell -->

<!-- cell: col=1; row=2 -->
| Metric | Value |
|---|---|
| MRR | 12.4M |
| NRR | 118% |
<!-- /cell -->

<!-- cell: col=2; row=2 -->
1. **Group** content by meaning
2. **Place** blocks to guide the eye
3. **Emphasize** only what matters
<!-- /cell -->

<!-- /grid -->

### Body Grid (With Span)

<!-- slide: template=body-grid -->

<!-- grid: columns=3; rows=2; col_gap=lg; row_gap=md -->

<!-- cell: col=1; row=1; col_span=2 -->
Use `col_span` and `row_span` when one message should dominate the slide.

<!-- card: accent -->
This gives you a large hero cell without falling back to a fixed 2-column structure.
<!-- /card -->
<!-- /cell -->

<!-- cell: col=3; row=1; row_span=2 -->
#### Supporting Notes

- Tall side rail
- FAQ
- Constraints
- Links
<!-- /cell -->

<!-- cell: col=1; row=2 -->
<!-- badge: rollout -->
Phased rollout
<!-- /cell -->

<!-- cell: col=2; row=2 -->
Ship in stages and expand once the signal is clear.
<!-- /cell -->

<!-- /grid -->

### Body Grid (Directional Spacing)

<!-- slide: template=body-grid -->

<!-- grid: columns=3; rows=2; col_gap=lg; row_gap=sm -->

<!-- cell: col=1; row=1; row_span=2 -->
<!-- card: accent -->
**Make the left-right split more pronounced**

- `col_gap=lg`
- Wider spacing between columns
- Clearer separation between horizontal groups
<!-- /card -->
<!-- /cell -->

<!-- cell: col=2; row=1; col_span=2 -->
Use this when you want more air between columns but still want related rows to read as one cluster.

| Setting | Value |
|---|---|
| `col_gap` | `lg` |
| `row_gap` | `sm` |
<!-- /cell -->

<!-- cell: col=2; row=2 -->
The tighter row spacing keeps the upper and lower cells visually connected.
<!-- /cell -->

<!-- cell: col=3; row=2 -->
> [!TIP]
> Useful when horizontal grouping matters more than vertical separation.
<!-- /cell -->

<!-- /grid -->

### Hero

<!-- slide: template=body-hero -->

![Cityscape](https://images.unsplash.com/photo-1477959858617-67f85cf4f1df?w=1920&q=80 "Photo by Pedro Lastra on Unsplash")

Large visual with overlay text

### Code Block Template

<!-- slide: template=body-code -->

```python
from dataclasses import dataclass

@dataclass
class Slide:
    type: str
    title: str = ""
    blocks: list = None

    def render(self) -> str:
        """Render slide to HTML string."""
        template = load_template(self.type)
        return template.render(slide=self)
```


## Components

<!-- slide: subtitle=Building blocks for slide content -->
<!-- -->

### Bullet List (ul)

- Level 1 items use the primary marker style
- Nesting is supported up to 3 levels deep
  - Level 2 items are indented once
  - They inherit the parent list's styling
    - Level 3 items reach maximum depth
    - Further nesting is clamped to this level
- Back to level 1

### Ordered List (ol)

1. **Define** the project scope and objectives
2. **Design** the architecture and user experience
3. **Develop** features in iterative sprints
4. **Test** thoroughly across all environments
5. **Deploy** to production with monitoring

### Checklist

- [x] Project kickoff meeting completed
- [x] Requirements document approved
- [x] Design mockups reviewed
- [ ] Development sprint 1
- [ ] QA testing phase
- [ ] Stakeholder sign-off

### Data Table

| Category | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|
| Revenue | $1.2M | $1.5M | $1.8M | $2.1M |
| Users | 12,000 | 15,400 | 19,200 | 24,800 |
| NPS | 72 | 75 | 78 | 82 |
| Churn | 3.2% | 2.8% | 2.4% | 2.1% |

### Code Block

```javascript
// Fenced code blocks display with language label
async function fetchSlides(deckId) {
  const res = await fetch(`/api/decks/${deckId}/slides`);
  const data = await res.json();
  return data.slides.map(s => ({
    id: s.id,
    title: s.title,
    template: s.template ?? "body",
  }));
}
```

### Inline Formatting

This slide demonstrates **bold text** for emphasis, `inline code` for technical terms, and [hyperlinks](https://example.com) for references.

You can also combine them: **[bold links](https://example.com)** work for call-to-action style references. Inline code like `useState()` or `design.config.yaml` renders in a monospace font.

### Callout (NOTE)

> [!NOTE]
> Notes provide supplementary information. Use them for context that helps but isn't critical to the main message.

### Callout (TIP)

> [!TIP]
> Tips highlight best practices and recommended approaches. Great for actionable advice.

### Callout (WARNING)

> [!WARNING]
> Warnings flag potential issues that could cause problems if ignored. Users should pay attention.

### Callout (CAUTION)

> [!CAUTION]
> Caution signals dangerous or destructive actions. This is the strongest level of alert.

### Card

<!-- card -->
Cards wrap content blocks in a bordered container. They visually group related information and draw attention.

- Use `<!-- card -->` to open
- Use `<!-- /card -->` to close
- Any block elements work inside
<!-- /card -->

### Card (Accent Variant)

<!-- card: accent -->
The accent variant applies the theme's accent color to the background and border, making the card stand out from standard cards.

- Use `<!-- card: accent -->` to open
- Ideal for key takeaways or highlights
<!-- /card -->

### Card with Eyebrow

<!-- card: accent; eyebrow=KEY INSIGHT -->
Cards support an eyebrow label via `<!-- card: accent; eyebrow=LABEL -->`. The eyebrow appears above the card content in accent color.
<!-- /card -->

### Badge

<!-- badge: NEW -->

<!-- badge: STABLE; status=success -->

<!-- badge: BETA; status=warning -->

<!-- badge: DEPRECATED; status=danger -->

Badges are inline status labels. Set `status` to `info` (default), `success`, `warning`, or `danger` to change the color.

### Steps

<!-- steps -->
1. **Plan** Define scope and requirements
2. **Design** Create mockups and architecture
3. **Build** Develop in iterative sprints
4. **Test** Validate quality and performance
5. **Ship** Deploy to production
<!-- /steps -->

### Steps (accent=last)

<!-- steps: accent=last -->
1. **Research** Gather user insights
2. **Ideate** Explore solutions
3. **Validate** Test with users
4. **Launch** Go live
<!-- /steps -->

### Arrow

<!-- slide: template=body-2col -->

#### Left

**Directions**

<!-- arrow: right -->

<!-- arrow: down -->

<!-- arrow: left -->

<!-- arrow: up -->

#### Right

**Size & Color Options**

<!-- arrow: right; size=lg -->

<!-- arrow: right; size=sm -->

<!-- arrow: right; size=lg; color=accent-subtle -->

<!-- arrow: right; size=sm; color=accent-subtle -->

### Image

![Sample Image](https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80 "Mountain landscape with dramatic clouds")

### Image (No Caption)

![Minimal image without caption text](https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=800&q=80)


## Meta Features

<!-- slide: subtitle=Slide-level configuration options -->
<!-- -->

### Confidential Badge

<!-- slide: confidential=true -->

Setting `confidential=true` in the slide comment displays a badge in the top-right corner. The badge text and style are configured in `design.config.yaml`.

- Per-slide override with `<!-- slide: confidential=true -->`
- Default behavior set in `badge.defaults` config
- Badge text customizable (e.g. "Confidential", "Internal Only")

### Compact Mode

<!-- slide: compact=true -->

Compact mode reduces font sizes and spacing to fit more content. Useful for dense information slides.

| Feature | Normal | Compact |
|---|---|---|
| Body text | type-body | type-caption size |
| Lead text | type-body-lead | type-body size |
| Subtitle | type-subtitle | type-body size |
| Code | type-code | type-note size |
| Gaps | gap-lg | gap-md |

- Lists and agenda items also tighten spacing
- Best for reference slides or detailed comparisons

### Custom Eyebrow

<!-- slide: eyebrow=CUSTOM LABEL -->

The `eyebrow` parameter overrides the auto-inherited section title. Use it for slide-specific categorization.

- Default: inherits from parent `##` section title
- Override: `<!-- slide: eyebrow=YOUR TEXT -->`
- Rendered in accent color above the slide title

### Subtitle (on Section)

Subtitles are supported on `##` section slides and `#` cover slides. See the "Meta Features" section header above for a live example.

- Cover: `<!-- slide: subtitle=Your subtitle -->`
- Section: `<!-- slide: subtitle=Your subtitle -->`
- Rendered in secondary text color below the main title

### Source / Citation Footer

This slide demonstrates the automatic source extraction feature. When the last paragraph of a slide starts with a recognized prefix, it is moved to the footer.

Source: Gartner, "Market Guide for Slide Automation," 2025
