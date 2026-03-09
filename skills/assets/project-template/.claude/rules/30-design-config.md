---
paths:
  - "design.config.yaml"
  - "scripts/config.py"
  - "scripts/sync_tokens.py"
  - "themes/**/styles/**"
  - "shared/styles/**"
---

# Design Config Rules

## 設定の唯一のソース

- `design.config.yaml` はデザイン設定の唯一のソース。

## global セクション

- `global.colors` の値は `sync_tokens.py` で **semantic 層** のトークンに直接書き込まれる。マッピング:
  - `accent` → `--semantic-color-accent-primary`
  - `bg_default` → `--semantic-color-bg-default`
  - `bg_inverse` → `--semantic-color-bg-inverse`
  - `text_primary` → `--semantic-color-text-primary`
  - `text_secondary` → `--semantic-color-text-secondary`
- `global.fonts` のマッピング:
  - `sans` → `--semantic-font-sans`
  - `mono` → `--semantic-font-mono`
- `global.lang`: HTML の `lang` 属性に使用（デフォルト: `ja`）。

## tokens セクション

- `tokens` セクションの値は CSS 変数名（`--` を除いた名前）で直接指定する。
- `tokens` と `global.colors`/`global.fonts` が同じ変数を指す場合、`tokens` が優先する。

## badge / page_number / accent_bar セクション

- `badge.enabled`: バッジ全体の有効/無効。`badge.text`: 表示テキスト（デフォルト: `Confidential`）。
- `badge.defaults`: スライドタイプごとのデフォルト（`cover`, `section`, `agenda`, `body`, `end`）。`end` のデフォルトは `false`。
- `page_number.enabled`: ページ番号全体の有効/無効。`page_number.start`: 開始番号（デフォルト: 1）。
- `page_number.defaults`: デフォルトで `cover: false`, `section: false`, `end: false`。
- `accent_bar.defaults`: スライドタイプごとの位置指定。選択肢: `top`, `left`, `none`。
  - デフォルト: `cover: left`, `section: none`, `agenda: top`, `body: top`, `end: left`。

## agenda セクション

- `agenda.enabled`: Agenda スライドの自動挿入（デフォルト: `true`）。
- `agenda.title`: Agenda 本文のタイトル（デフォルト: `Agenda`）。
- `agenda.eyebrow`: Agenda のアイブロウテキスト（デフォルト: `Agenda`）。
- `agenda.show_pages`: セクション横のページ番号表示（デフォルト: `false`）。

## end セクション

- `end.enabled`: End スライドの自動挿入（デフォルト: `true`）。
- `end.title`: End スライドのタイトル（デフォルト: `Thank you`）。
- `end.subtitle`: End スライドのサブタイトル（デフォルト: 空）。

## branding セクション

- `branding.cover_logo_enabled`: Cover 上部ロゴの表示 ON/OFF。デフォルトは `true`。
- `branding.cover_logo_src`: Cover / End 上部に表示するロゴ画像パス。`images/logo-horizontal.svg` のような project 内相対パスを使う。
- `branding.cover_logo_alt`: Cover ロゴ画像の alt テキスト。
- `branding.footer_logo_enabled`: Body フッターロゴの表示 ON/OFF。デフォルトは `true`。
- `branding.footer_logo_src`: Body / Agenda スライドのフッター右側に表示するロゴ画像パス。`images/logo-icon.svg` のような project 内相対パスを使う。
- `branding.footer_logo_alt`: Footer ロゴ画像の alt テキスト。
- `branding.*` の変更は CSS sync ではなく HTML 再生成が必要。

## slides[] オーバーライド

- `slides[]` の `match` はタイプ名（`cover`, `section`, `body` 等）またはタイトル（`### タイトル`, `## タイトル`）で指定する。
- 複数マッチ時の優先順: タイトル指定 > タイプ指定。
- 指定可能なフィールド: `template`, `badge`, `page_number`, `accent_bar`, `show_source`, `compact`, `ratio`, `subtitle`, `tokens`。

## Markdown コメントによる上書き

- `<!-- slide: ... -->` で指定できるキーと config 解決時の対応:
  - `template` → テンプレート選択
  - `confidential` → `badge_enabled`（`true`/`false`）
  - `show_source` → 出典フッター表示
  - `compact` → コンパクト表示
  - `ratio` → 2col の幅比率
- 設定優先順: Markdown コメント > `slides[]` タイトルマッチ > `slides[]` タイプマッチ > デフォルト。

## CSS トークン3層ルール

トークンは primitives → semantic → component の3層構造。

- **primitives**: 生の値（色コード、px、em 等）。他のトークンを参照しない。
- **semantic**: primitives を参照し、意味のある名前を与える（`bg-default`, `text-primary`, `accent-primary` 等）。
- **component**: semantic を参照し、コンポーネント固有の値を定義する。コンポーネント固有のスペーシング等で適切な semantic がない場合は primitives を直接参照してもよい。

参照ルール:
- `slide.css` は **component** と **semantic**（typography の color 指定）のみ参照する。**primitives を直接参照しない**。
- `tokens.component.css` は原則 **semantic** を参照する。共有概念のないコンポーネント固有値（badge padding 等）は primitives を直接参照してもよい。
- `tokens.semantic.css` は **primitives** のみ参照する。

デザイン調整時に触る層:
- 色・フォントの変更 → `design.config.yaml` の `global` セクション + `sync_tokens.py`（semantic 層を上書き）
- 個別トークンの変更 → `design.config.yaml` の `tokens` セクション + `sync_tokens.py`
- CSS 直接編集 → 対象の層のファイルを直接編集（`sync_tokens.py` は上書きのみで手動編集を壊さない）

## sync_tokens.py

- `sync_tokens.py` で `design.config.yaml` の変更を CSS ファイルに反映する。
- `global.colors` / `global.fonts` は **semantic 層** (`tokens.semantic.css`) を対象に上書きする。
- `tokens` セクションの値は3ファイル全て (`tokens.primitives.css`, `tokens.semantic.css`, `tokens.component.css`) を走査し、一致する変数名を上書きする。
- CSS ファイルを直接編集した場合もそのまま動作する（`sync_tokens.py` は上書きのみ行い、手動編集を壊さない）。
- `--version` オプションで `output/vN/styles/` にも同時反映できる。`slide.css` も差分があればコピーする。
