# Markdown to Figma Slides

Markdown を書くだけで、Figma に取り込める HTML スライドを生成するスキルです。

Claude Code（または OpenAI Codex 等の AI エージェント）に依頼すると、Markdown の正規化からテンプレート適用、バージョン管理、Figma キャプチャまでを一貫して進めてくれます。生成のたびにバージョン付きスナップショット（`v1`, `v2`, ...）が作られるので、過去のスライドを失う心配がありません。

## まずは試してみる

`skills/assets/sample-catalog.md` にサンプルの Markdown ファイルが入っています。まずはこれを使ってスライド生成を試してみてください。

## 前提条件

- Python 3.9 以上
- Figma MCP が利用できる環境（Figma キャプチャを行う場合のみ）

依存パッケージをインストールしてください。

```bash
pip3 install jinja2 pyyaml pygments
```

## はじめかた

Claude Code に次のように依頼するだけで始められます。

```text
Markdownファイルをスライドにしたいです。
```

入力ファイルを指定する場合:

```text
input/raw/source.md をもとにスライドを生成してください。
```

デザイン調整も含めて頼む場合:

```text
Markdownからスライドを作りたいです。
まず生成して、そのあとで配色や余白を調整したいです。
```

Figma への取り込みまで進めたい場合:

```text
MarkdownファイルをFigma用のスライドに変換して、Figmaに取り込むところまで進めてください。
```

依頼を受けると、以下の流れで自動的に作業が進みます。

1. プロジェクトの初期化
2. Markdown の正規化
3. HTML スライドの生成（バージョン付き）
4. ローカルプレビュー
5. Figma キャプチャ（依頼した場合）

## Markdown の書き方

### スライドの区切り

見出しレベルでスライドの種別が決まります。

```md
# プレゼンテーションタイトル

## セクション名

### スライドタイトル

- 箇条書きの内容
```

| 見出し | スライド種別 | 説明 |
| --- | --- | --- |
| `#` | 表紙（cover） | デッキのタイトルスライド |
| `##` | セクション区切り（section） | ダーク背景のセクション扉 |
| `###` | 本文スライド（body） | 通常のコンテンツスライド |
| `####` | カラム見出し / 補助見出し | 2カラム・3カラム内の分割に使用 |

### 使える Markdown 要素

#### 箇条書き（3 段階ネスト対応）

```md
- 親の項目
  - 子の項目
    - 孫の項目
```

#### 番号付きリスト

```md
1. 最初のステップ
2. 次のステップ
3. 最後のステップ
```

#### チェックボックス

```md
- [x] 完了した項目
- [ ] 未完了の項目
```

#### テーブル

```md
| 指標 | 値 |
| --- | --- |
| 成長率 | 15% |
| 利益率 | 12% |
```

#### コードブロック（シンタックスハイライト対応）

言語を指定すると、自動的にシンタックスハイライトが適用されます（Pygments の monokai テーマ）。インラインスタイルで出力されるため、Figma キャプチャでもそのまま色が保持されます。

````md
```python
def hello():
    print("Hello, world!")
```
````

#### インラインコード・太字・リンク

```md
`inline code` と **太字** と [リンク](https://example.com)
```

#### 画像

```md
![代替テキスト](images/photo.png)
![代替テキスト](images/photo.png "キャプション付き")
```

画像ファイルは `input/raw/images/` に配置します。生成時に出力先へ自動コピーされます。

#### 出典

スライドの最後の段落が `Source:` / `出典:` / `参照:` / `参考:` で始まる場合、自動的にフッター出典として表示されます。

```md
### 市場シェア

- A社: 35%
- B社: 28%

出典: 業界レポート 2025年版
```

## コンポーネント

Markdown 内に HTML コメントを書くことで、特殊なコンポーネントを配置できます。

### Card（カード）

コンテンツをカードで囲みます。

```md
<!-- card -->
- 重要なポイント
<!-- /card -->
```

`<!-- /card -->` を省略すると、直後の 1 ブロックだけがカードになります。

アクセントカラーのカード:

```md
<!-- card: accent -->
- 強調したい内容
<!-- /card -->
```

アイブロウ（小見出し）付き:

```md
<!-- card ; eyebrow=ポイント -->
- まとめたい内容
<!-- /card -->
```

### Badge（バッジ）

テキストラベルを表示します。

```md
<!-- badge: 新機能 -->
<!-- badge: 要注意; status=warning -->
```

`status` は `info`（デフォルト）/ `success` / `warning` / `danger` から選べます。

### Callout（コールアウト）

注意書きブロックを表示します。

```md
> [!NOTE]
> 補足情報です。

> [!TIP]
> おすすめの方法です。

> [!WARNING]
> 注意してください。

> [!CAUTION]
> 重大なリスクがあります。
```

### Arrow（矢印）

コンテンツ間にシェブロン矢印を配置します。

```md
<!-- arrow: right -->
<!-- arrow: down; size=sm -->
<!-- arrow: left; color=accent-subtle -->
```

| パラメータ | 値 | デフォルト |
| --- | --- | --- |
| direction（必須） | `right`, `left`, `up`, `down` | — |
| size | `lg`, `sm` | `lg` |
| color | `secondary`, `accent-subtle` | `secondary` |

2カラム・3カラムのカラム内に配置すると、カラム間のセパレータになります。

### Steps（ステップフロー）

番号付きリストをシェブロン型の水平フローとして描画します。

```md
<!-- steps -->
1. **要件定義** ビジネス課題をヒアリングし仕様を策定
2. **設計・開発** アーキテクチャ設計とコーディング
3. **テスト** ユニットテスト・結合テスト・UAT
4. **リリース** 本番デプロイと効果測定
<!-- /steps -->
```

`**太字**` がタイトル、その後のテキストが説明になります。

最後のステップをアクセントカラーにしたい場合:

```md
<!-- steps: accent=last -->
1. **企画**
2. **設計**
3. **実装**
4. **リリース**
<!-- /steps -->
```

## テンプレート

9 種類のテンプレートが用意されています。`cover` / `section` / `agenda` は見出しレベルから自動選択されます。`###` のスライドには `<!-- slide: template=... -->` で明示指定できます。

| テンプレート | 用途 |
| --- | --- |
| `cover` | 表紙スライド（`#` で自動選択） |
| `agenda` | セクション一覧（`##` から自動生成） |
| `section` | セクション区切り / ダーク背景（`##` で自動選択） |
| `body` | 汎用スライド（デフォルト） |
| `body-text` | 長文テキスト向け（余白広め） |
| `body-2col` | 2 カラムレイアウト |
| `body-3col` | 3 カラムレイアウト |
| `body-code` | コード表示向け |
| `body-hero` | フル背景画像 + メッセージ |

### テンプレートの指定例

```md
<!-- slide: template=body-text -->

### 長めの説明ページ

ここに本文を書きます。
```

### 2 カラム

`#### Left` と `#### Right` でカラムを分割します。

```md
<!-- slide: template=body-2col; ratio=6040 -->

### 比較表

#### Left

- メリット A
- メリット B

#### Right

- デメリット A
- デメリット B
```

`ratio` の値: `4060`（左 40：右 60）/ `6040`（左 60：右 40）/ 未指定で均等。

### 3 カラム

`#### Col1` / `#### Col2` / `#### Col3` でカラムを分割します。

```md
<!-- slide: template=body-3col -->

### 三つの柱

#### Col1

- 品質

#### Col2

- コスト

#### Col3

- 納期
```

### Hero（フル背景画像）

スライド内の最初の画像が背景として使われます。

```md
<!-- slide: template=body-hero -->

### メッセージ

![](images/hero-bg.jpg)

大きなメッセージをここに書きます。
```

## スライドの表示設定

スライドごとの表示設定は `<!-- slide: key=value -->` コメントで指定します。複数の設定はセミコロンで区切ります。

```md
<!-- slide: compact=true; confidential=true; show_pages=false -->
```

| 設定 | 例 | 用途 |
| --- | --- | --- |
| `template` | `template=body-2col` | テンプレートを指定する |
| `ratio` | `ratio=6040` | 2カラムの比率を指定する |
| `compact` | `compact=true` | 余白を詰めて表示する |
| `confidential` | `confidential=true` | Confidential チップを表示する |
| `subtitle` | `subtitle=FY2026 Q1` | 表紙・セクションにサブタイトルを付ける |
| `show_pages` | `show_pages=false` | ページ番号の表示を切り替える |
| `eyebrow` | `eyebrow=概要` | アイブロウ（小見出し）を変更する |

### サブタイトルの配置

表紙:

```md
# 事業戦略レビュー

<!-- slide: subtitle=FY2026 Q1 Review -->
```

セクション扉（前のスライド末尾に配置すると、次のセクションに自動適用されます）:

```md
<!-- slide: subtitle=市場・競合・自社の状況整理 -->

## 市場環境
```

## デザイン調整

見た目は `design.config.yaml` で調整します。色・フォントの変更は HTML を再生成せずに反映できます。

### 配色とフォント

```yaml
global:
  lang: "ja"
  fonts:
    sans: "Outfit, Noto Sans JP, sans-serif"
    mono: "JetBrains Mono, monospace"
  colors:
    accent: "#D4593A"        # アクセントカラー
    bg_default: "#F5F0E8"    # 背景色
    bg_inverse: "#1A1A1A"    # セクション背景色
    text_primary: "#1A1A1A"  # 本文色
    text_secondary: "#4D4D4D" # 補助テキスト色
```

### Confidential チップ

```yaml
badge:
  enabled: true
  text: "Confidential"
  defaults:           # スライド種別ごとの表示/非表示
    cover: true
    section: true
    agenda: true
    body: true
```

### ページ番号

```yaml
page_number:
  enabled: true
  start: 1
  defaults:
    cover: false       # 表紙は非表示
    section: false     # セクションは非表示
    agenda: true
    body: true
```

### アクセントバー

```yaml
accent_bar:
  defaults:
    cover: "left"      # left / top / none
    section: "none"
    agenda: "top"
    body: "top"
```

### Agenda

```yaml
agenda:
  enabled: true       # false で無効化
  title: "Agenda"
  eyebrow: "Agenda"
  show_pages: true    # 各セクションのページ番号を表示
```

### CSS トークンの直接上書き

CSS 変数名をキーとして、任意のトークンを上書きできます。

```yaml
tokens:
  semantic-color-accent-primary: "#2563EB"
  component-slide-padding: "48px"
```

スタイルは 3 層のトークンで管理されています。

| ファイル | 役割 |
| --- | --- |
| `tokens.primitives.css` | ベーストークン（色の生値、フォントサイズ等） |
| `tokens.semantic.css` | セマンティックエイリアス（`accent-primary` → 具体的な色） |
| `tokens.component.css` | コンポーネントレベル（スライド余白、カード半径等） |
| `slide.css` | レイアウトとコンポーネントのスタイル |

`global.colors` / `global.fonts` の変更はセマンティック層に反映されます。`tokens` セクションでは任意の層の変数を直接上書きできます。

### スライド単位のオーバーライド

特定のスライドに対して、テンプレートや表示設定を上書きできます。

```yaml
slides:
  - match: "### 財務ハイライト"    # タイトルで指定
    template: "body-2col"
    ratio: "6040"
    compact: true
  - match: "body"                  # スライド種別で指定
    badge: true
  - match: "## 市場環境"           # セクションタイトルで指定
    subtitle: "市場分析セクション"
```

設定の優先順位（下ほど高い）:

1. `design.config.yaml` のデフォルト値
2. `slides[]` オーバーライド（種別マッチ → タイトルマッチの順）
3. Markdown 内の `<!-- slide: ... -->` コメント

### 変更内容と反映方法

| 変更した対象 | 必要なアクション |
| --- | --- |
| Markdown の内容 | スライド再生成 |
| テンプレート（`.html.j2`） | スライド再生成 |
| `design.config.yaml` の色・フォント・トークン | CSS のみ反映（再生成不要） |
| `design.config.yaml` の `slides[]` テンプレート指定 | スライド再生成 |
| CSS ファイル直接編集 | CSS のみ反映（再生成不要） |

## プロジェクト構成

初期化後のディレクトリ構成です。

```text
my-slides/
  design.config.yaml          # デザイン設定
  styles/
    tokens.primitives.css      # ベーストークン
    tokens.semantic.css        # セマンティックトークン
    tokens.component.css       # コンポーネントトークン
    slide.css                  # レイアウト CSS
  templates/                   # Jinja2 テンプレート
    base.html.j2
    cover.html.j2
    agenda.html.j2
    section.html.j2
    body.html.j2
    body-text.html.j2
    body-2col.html.j2
    body-3col.html.j2
    body-code.html.j2
    body-hero.html.j2
  scripts/                     # Python スクリプト
  input/
    raw/                       # 元の Markdown を配置
      images/                  # 画像ファイルを配置
    normalized/                # 正規化後の Markdown
    current.md                 # 生成対象（正規化済み）
  output/
    v1/                        # バージョン付きスナップショット
      slides/
        pages/*.html           # ページ単位の HTML
        slides.html            # 全スライドをまとめた HTML
      source/                  # 入力と設定のスナップショット
      SLIDES.md                # スライド一覧
      manifest.json            # メタデータ
    slides.html                # 最新版へのリダイレクト
```

## スラッシュコマンド

初期化後のプロジェクトでは、Claude Code のスラッシュコマンドが使えます。

| コマンド | 用途 |
| --- | --- |
| `/slides-generate` | `input/current.md` から HTML スライドを生成する |
| `/design-tune` | `design.config.yaml` の変更を CSS に反映する（再生成不要） |
| `/figma-capture-run` | 生成済みスライドを Figma にキャプチャし、完了まで追跡する |

## Figma キャプチャ

Figma MCP が利用できる環境で、生成済みスライドを Figma に取り込めます。

```text
スライドをFigmaに取り込んでください。
```

または `/figma-capture-run` を実行すると、以下が自動的に行われます。

1. `output/` でローカルサーバーを起動
2. Figma MCP でキャプチャを開始
3. 完了までポーリング

## 手動でのコマンド実行

通常は Claude Code に依頼すれば自動で実行されますが、手動で実行することもできます。

```bash
# プロジェクト初期化
cd /path/to/claude-skills/markdown-to-figma-slides/skills
./scripts/init_project.sh /path/to/my-slides

# パイプライン一括実行
cd /path/to/my-slides
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md

# ローカルプレビュー
cd output && python3 -m http.server 8080
# http://localhost:8080/slides.html を開く
```

個別ステップでの実行:

```bash
# 1. 正規化
python3 scripts/normalize_md.py --input input/raw/source.md --output input/normalized/source.md
cp input/normalized/source.md input/current.md

# 2. バージョン番号の取得
VERSION=$(python3 scripts/create_version.py --project-root .)

# 3. トークン同期
python3 scripts/sync_tokens.py --project-root .

# 4. スライド生成
python3 scripts/generate_slides.py --input input/current.md --version $VERSION --project-root .

# 5. 出力へのトークン同期
python3 scripts/sync_tokens.py --project-root . --version $VERSION
```

## トラブルシューティング

### `jinja2` または `yaml` が見つからない

```bash
pip3 install jinja2 pyyaml pygments
```

### `scripts/` が存在しない

プロジェクト初期化を実行してください。

```bash
cd /path/to/claude-skills/markdown-to-figma-slides/skills
./scripts/init_project.sh /path/to/my-slides
```

### スライドがブラウザで表示されない

`output/` ディレクトリで HTTP サーバーを起動してください。

```bash
cd /path/to/my-slides/output
python3 -m http.server 8080
```

### 以前のバージョンが消えた

出力は `v1`, `v2` のようにバージョン管理されており、既存バージョンは上書きされません。
