# Theme Authoring Guide

## この文書の位置づけ

この文書は、`markdown-to-figma-slides` の project template に新しい theme を追加するときの実務ガイドです。

- 設計方針の正本は `docs/theme-design.md`
- ここでは「どう作るか」に絞る

## 基本方針

theme は配色の差し替えだけではなく、見た目一式をまとめた design package として扱う。

- baseline は `theme.yaml` の `defaults` が持つ
- `design.config.yaml` は project 固有 override に留める
- layout / component の共通ルールは `shared/styles/slide.css` に寄せる
- theme ごとの差分は `themes/<name>/styles/` と `themes/<name>/templates/` で持つ

新しい theme を 0 から空で作るより、既存 theme を複製して調整する方が安全です。

## 最小構成

新しい theme は `themes/<name>/` 配下に次を持つ。

```text
themes/
  <name>/
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

必須:

- `theme.yaml`
- `styles/`
- `templates/`

実運用上は、上記の CSS / template 一式を揃える前提で考える。
`renderer.py` は slide template を `*.html.j2` で引き、`agenda.html.j2` は fallback しない。

## 追加手順

初手は既存 theme の複製を推奨する。

```bash
cd /path/to/my-slides
cp -R themes/classic themes/my-theme
```

次に `themes/my-theme/theme.yaml` を更新する。

```yaml
name: my-theme
label: My Theme
description: Short summary of the theme

fonts:
  google:
    - family: Outfit
      weights: [400, 500, 700]
    - family: Noto Sans JP
      weights: [400, 500, 700]

defaults:
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

  badge:
    enabled: true
    text: "Confidential"
    defaults:
      cover: true
      section: true
      agenda: true
      body: true

  page_number:
    enabled: true
    start: 1
    defaults:
      cover: false
      section: false
      agenda: true
      body: true

  accent_bar:
    defaults:
      cover: "left"
      section: "none"
      agenda: "top"
      body: "top"

  agenda:
    enabled: true

  end:
    enabled: true
    title: "Thank you"
    subtitle: ""

  tokens: {}
  slides: []
```

その後、CSS と templates を theme 用に調整する。

```bash
python3 scripts/theme.py --project-root . show my-theme
python3 scripts/theme.py --project-root . apply my-theme
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

## `theme.yaml` の扱い

### 必須項目

- `name`
- `defaults`

### 任意項目

- `label`
- `description`
- `fonts.google`

### バリデーション

loader は次をエラーにする。

- `theme.yaml` が存在しない
- `theme.yaml` が空、または dict でない
- `name` がない
- `name` と directory 名が一致しない
- `styles/` がない
- `templates/` がない

`defaults` が dict でない場合は空として扱う。

### `fonts.google`

V1 では Google Fonts のみ対応する。

- `family` は必須
- `weights` は任意
- `weights` に不正値があれば、その値だけ無視する

## defaults と `design.config.yaml` の役割分担

baseline の見た目は theme defaults で決める。

- typography の基本値
- badge / page number / accent bar の既定挙動
- agenda / end slide の既定文言
- token の既定値

`design.config.yaml` 側には project 固有 override だけを置く。
theme 追加時に baseline を `design.config.yaml` に逃がさないこと。

## CSS レイヤーの責務

依存順は次を基本とする。

```text
tokens.primitives.css
-> tokens.semantic.css
-> tokens.component.css
-> shared/styles/slide.css
-> themes/<name>/styles/slide.css
```

### `tokens.primitives.css`

theme 実装の素の値を置く。

- 色は `brand-*` / `neutral-*` を基本語彙にする
- primitive を theme 横断で完全統一することは目的にしない

### `tokens.semantic.css`

renderer / component が参照する意味レイヤーを置く。

- theme 間の差分は基本的にここで吸収する
- color はできるだけ semantic 経由にする

### `tokens.component.css`

component 単位の token を置く。

- color は semantic token から取る
- space / radius などは現状 primitive 参照を許容する

### `slide.css`

theme 固有の layout / decoration / typography override を置く。
共通化できるものは `shared/styles/slide.css` に寄せる。

運用ルール:

- `cover` / `section` / `body` の `.main` に `max-width` などの幅制限を入れるときは、要素自体も中央に置く
- 具体的には `justify-self: center` または `margin-inline: auto` を併用する
- 中身だけ `text-align: center` や `align-items: center` にしても、幅制限した `.main` の箱は左基準のまま残りうる
- theme 側の `slide.css` で幅制限だけを追加すると、見出しや section slide が少し左へ寄って見える原因になる

## Template 方針

template は theme の見た目を決める資産として扱う。

- `base.html.j2` は head と共通骨格
- slide 別 template は視覚差分の責任を持つ
- 構造差分が不要な場合でも、まずは既存 template 一式を複製して維持する

最初の 1 本を作るより、既存 theme を崩さずに 2 本目、3 本目を増やしたときに無理がないかを優先して判断する。

## 確認コマンド

theme を追加したら最低限これを確認する。

```bash
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . show my-theme
python3 scripts/theme.py --project-root . apply my-theme
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

見るポイント:

- `list` と `show` で新 theme が見えるか
- `apply` 後に `design.config.yaml.theme.name` が切り替わるか
- render が通るか
- cover / agenda / section / body / end で配色、タイポ、余白が破綻しないか
- 複数 theme 間で semantic token の責務が保てているか

## 避けること

- baseline 値を `design.config.yaml` に多く持たせる
- component token から primitive color を直接引く
- theme 追加のたびに共通 CSS を theme 側へコピーして増やす
- 1 theme だけで成立する見た目最適化に寄せる

## 関連文書

- `docs/theme-design.md`
- `skills/SKILL.md`
- `skills/references/workflow.md`
