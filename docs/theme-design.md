# Theme システム設計

## 目的

`theme` 機能を追加し、スライドのデザインを「数色の上書き」ではなく、まとまりのあるデザインパッケージとして切り替えられるようにする。

テーマが担う対象は次の通り。

- 配色
- フォント
- 装飾ルール
- CSS トークン値
- テンプレート
- フォント読み込み

## 基本方針

レンダリングエンジンは共通化し、見た目に関わる資産をテーマ側へ寄せる。

共通エンジンとして残すもの:

- Markdown の正規化とパース
- AST モデル
- スライド種別: `cover`, `section`, `agenda`, `body`, `end`
- ブロック種別: `card`, `callout`, `table`, `codeblock`, `steps`, `arrow`, `image`
- テンプレート変数の契約
- renderer が前提にする semantic/component token 名

テーマが持つもの:

- `styles/` 一式
- `templates/` 一式
- テーマ既定値
- フォント読み込み定義
- テーマのメタ情報

`primitives` を過度に共通化しない。primitive token の具体値はテーマ実装の詳細として扱う。

## ディレクトリ構成

```text
project-root/
  design.config.yaml
  themes/
    classic/
      theme.yaml
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
        body-2col.html.j2
        body-3col.html.j2
        body-code.html.j2
        body-hero.html.j2
        end.html.j2
```

## プロジェクト設定

`design.config.yaml` には最小限のテーマ指定だけを追加する。

```yaml
theme:
  name: classic
```

既存のプロジェクト単位の上書き設定は引き続き持つ。

- `global`
- `badge`
- `page_number`
- `accent_bar`
- `agenda`
- `end`
- `tokens`
- `slides`

## theme.yaml の仕様

各テーマは `theme.yaml` を持つ。

```yaml
name: classic
label: Classic
description: Warm editorial theme with accent bars and rounded cards

fonts:
  google:
    - family: Outfit
      weights: [400, 500, 600, 700]
    - family: Noto Sans JP
      weights: [400, 500, 600, 700]
    - family: JetBrains Mono
      weights: [400, 500, 600]

defaults:
  global:
    lang: ja
    fonts:
      sans: "Outfit, Noto Sans JP, sans-serif"
      mono: "JetBrains Mono, monospace"
  badge:
    enabled: true
    text: Confidential
  page_number:
    enabled: true
    start: 1
  accent_bar:
    defaults:
      cover: left
      section: none
      agenda: top
      body: top
      end: left
  agenda:
    enabled: true
  end:
    enabled: true
    title: Thank you
    subtitle: ""
  tokens: {}
  slides: []
```

### V1 schema

必須項目:

- `name`
- `defaults`

任意項目:

- `label`
- `description`
- `fonts.google`

必須ディレクトリ:

- `themes/<name>/theme.yaml`
- `themes/<name>/styles/`
- `themes/<name>/templates/`

### `name` の扱い

- `name` は必須
- `name` はディレクトリ名と一致している必要がある
- 不一致の場合はエラーにする

例:

- `themes/classic/theme.yaml` の `name` は `classic`

### `fonts.google`

V1 では Google Fonts のみ対応する。

```yaml
fonts:
  google:
    - family: Outfit
      weights: [400, 500, 600, 700]
```

ルール:

- `family` は必須
- `weights` は任意
- 不正な `weights` 値はその値だけ無視する
- `fonts.google` がなければフォントリンクは出力しない

### `defaults` に含めてよい項目

- `global`
- `badge`
- `page_number`
- `accent_bar`
- `agenda`
- `end`
- `tokens`
- `slides`

### V1 で非対応の項目

- `extends`
- `inherits`
- フォントプロバイダの複数対応
- theme ごとの custom script
- partial theme composition
- renderer が読む theme 独自 key

### エラー方針

- theme 名が存在しない場合は即エラー
- `theme.yaml` が存在しない場合は即エラー
- `theme.yaml` が空、または dict でない場合はエラー
- `name` がない場合はエラー
- `name` とディレクトリ名が一致しない場合はエラー
- `styles/` または `templates/` がない場合はエラー
- `defaults` が dict でない場合は空として扱う

## 設定の解決順序

設定は次の順序で解決する。

```text
engine defaults
-> theme defaults
-> design.config.yaml
-> slide override
-> markdown comment
```

これにより、テーマが全体のベースラインを定義しつつ、プロジェクトごとの調整も維持できる。

## テーマの読み込みルール

- 有効なテーマは `design.config.yaml.theme.name` から決定する
- テンプレートは `themes/<theme>/templates` から読む
- スタイルは `themes/<theme>/styles` を `output/vN/styles` にコピーする
- all-in-one の `slides.html` も有効テーマのスタイルを使う
- テーマが存在しない場合は、明確なエラーで失敗させる

## フォント読み込み

現在のフォント読み込みは `templates/base.html.j2` と renderer が生成する `slides.html` にハードコードされている。

これはテーマ対応のレンダリングに移す必要がある。

要件:

- テーマは `theme.yaml` でフォント読み込みメタデータを宣言する
- renderer はそのメタデータから適切な Google Fonts の `<link>` を生成する
- CSS の `font-family` 変数は、引き続き config/theme 解決結果から与える

## テーマ管理

管理機能は軽量に保つ。大きなレジストリは不要。

必要な操作:

- 利用可能なテーマの一覧を出す
- 現在のテーマを表示する
- テーマを適用する

想定 CLI:

```bash
python3 scripts/theme.py list
python3 scripts/theme.py current --project-root .
python3 scripts/theme.py apply classic --project-root .
```

振る舞い:

- `list`: `themes/*/theme.yaml` を走査する
- `current`: `design.config.yaml.theme.name` を読む
- `apply <name>`: `design.config.yaml.theme.name` を更新する

## 移行手順

1. config 読み込みに theme サポートを追加する
2. theme メタデータのローダーと軽量 CLI を追加する
3. generator/renderer を、有効テーマの templates/styles を使う形に変更する
4. 共通テンプレートと all-in-one HTML からハードコードされたフォントリンクを除去する
5. 現在の見た目一式を `themes/classic` に移す
6. スキル文書と workflow 文書を更新する

## V1 でやらないこと

- テーマ継承 (`extends`) は入れない
- テーマの部分合成は入れない
- 複数テーマディレクトリの実行時マージはしない
- radically different なテーマ間で primitive token 名まで完全共通化しようとしない

V1 は明快さと実装の堅さを優先する。
