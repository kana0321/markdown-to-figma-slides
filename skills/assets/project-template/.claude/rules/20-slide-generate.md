---
paths:
  - "scripts/generate_slides.py"
  - "scripts/parser.py"
  - "scripts/renderer.py"
  - "scripts/models.py"
  - "templates/**"
  - "styles/**"
  - "output/**"
  - "input/current.md"
---

# Slide Generate Rules

## 入力と出力

- `input/current.md` を基準入力として扱う。
- パーサー（`parser.py`）で Markdown を AST（`Deck` → `Slide` → `Block` → `Inline`）に変換し、レンダラー（`renderer.py`）で Jinja2 テンプレートを使って HTML を生成する。
- 出力は必ず2種類作成する:
  - `slides/pages/*.html`（ページ別、CSS パスは `../../styles`）
  - `slides/slides.html`（all-in-one 兼キャプチャ入口、CSS パスは `../styles`）
- `SLIDES.md` と `manifest.json` を同時に更新する。
- manifest に `source_path` と `source_sha256` がない場合は失敗扱い。

## テンプレート選択

- 優先順: Markdown コメント `<!-- slide: template=... -->` > `design.config.yaml` の `slides[]` > デフォルト。
- テンプレート未指定時のデフォルト: `cover`/`section`/`agenda` はそのまま、それ以外は `body`。
- 指定テンプレートの `.html.j2` が見つからない場合は `body.html.j2` にフォールバックする。

## パース規則

- `#` (level 1): Cover スライド。ドキュメント先頭に1つ。
- `##` (level 2): Section スライド。セクション区切り。
- `###` (level 3): Body スライド。セクション内のコンテンツスライド。
- `####` (level 4): 2col/3col テンプレートではカラム分割キー、それ以外では小見出し。
- `##` のない `###` が出現した場合、暗黙のセクション（タイトル空）が自動作成される。
- `<!-- slide: ... -->` コメントがチャンク末尾（次の `###` の直前）にある場合、次のチャンクに所属させる。

## Agenda 自動生成

- `design.config.yaml` で `agenda.enabled: true` の場合、Cover の直後に Agenda スライドを自動挿入する。
- Agenda にはセクション一覧とそのページ番号が表示される。
- `agenda.title`, `agenda.eyebrow`, `agenda.show_pages` で表示をカスタマイズ可能。

## カラム分割

- `body-2col`: `#### Left` / `#### Right` で左右に分割。`ratio` で幅比率を指定（`4060`, `6040`, 空=equal）。
- `body-3col`: `#### Col1` / `#### Col2` / `#### Col3` で3列に分割。
- カラムラベルに一致しないブロックは先頭カラムに入る。
- カラム末尾の出典行もフッターとして抽出される（右 → 左 / col3 → col1 の順に探索）。

## テンプレート固有の挙動

- `body-text`: 本文の `type-body` クラスを `type-body-spacious` に自動変換し、可読性を向上させる。
- `body-hero`: 最初の画像ブロックをヒーロー画像として抽出し、残りをコンテンツとして表示。本文クラスを `type-hero` に変換する。
- `body-code`: コードブロック中心のスライド用。

## Arrow コンポーネント

- `<!-- arrow: direction -->` で方向付きシェブロン矢印を挿入する。
- パラメータ: `direction` (必須: right/left/up/down), `size` (lg/sm), `color` (secondary/accent-subtle)。
- マルチカラムの `.col` 内に配置すると、CSS でカラム間セパレータとして自動配置される。

## Steps コンポーネント

- `<!-- steps -->...<!-- /steps -->` で OL をシェブロン型の水平ステップフローに変換する。
- `**太字**` がタイトル、続くテキストが説明。説明がある場合はアクセントカラーの区切り線付き。
- パラメータ: `accent=last` で最終ステップをアクセントカラーにできる。
- card 内にも steps 内に card も配置可能（ネスト対応）。

## 出典・参照フッター

- スライド末尾の出典・参照行（`出典:` / `参照:` / `参考:` / `Source:` / `Reference:` / `Ref:` / `Citation:` 等）はパーサーが自動抽出し、フッターの `footer__source` に表示する。プレフィックスラベルは保持される。

## All-in-one HTML

- 全スライドを `<div class="deck-item">` で包み、`<div class="deck">` 内に縦並びで配置する。
- `<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>` を必ず含める。削除しない。
- スタイルは同じ CSS ファイル群をリンクする（パスは `../styles`）。
- `output/slides.html` は最新バージョンの `slides/slides.html` への JavaScript リダイレクト。
