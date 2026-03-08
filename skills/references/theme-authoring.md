# Theme Authoring Guide

この文書は、新しい theme を追加または調整するときの実務ガイドです。

- theme system の運用ルールは `theme-system.md`
- 実行手順は `workflow.md`
- 見た目確認は `visual-qa.md`
- repo maintainer 向けの設計判断は `../../docs/theme-design.md`

## 追加前に理解しておくこと

- theme は配色差し替えではなく design package として扱う
- baseline は `theme.yaml` の `defaults` が持つ
- `design.config.yaml` は project 固有 override に留める
- 新しい theme を 0 から作るより、既存 theme を複製して調整する方が安全

## 最小構成

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
      body-grid.html.j2
      body-grid-full.html.j2
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

## 新しい theme の作成手順

まず既存 theme を複製します。

```bash
cd /path/to/my-slides
cp -R themes/classic themes/my-theme
```

次に `themes/my-theme/theme.yaml` を更新します。

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

その後、CSS と templates を theme 用に調整します。

```bash
python3 scripts/theme.py --project-root . show my-theme
python3 scripts/theme.py --project-root . apply my-theme
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

## `theme.yaml` の書き方

### 必須項目

- `name`
- `defaults`

### 任意項目

- `label`
- `description`
- `fonts.google`

### バリデーション

loader は次をエラーにします。

- `theme.yaml` が存在しない
- `theme.yaml` が空、または dict でない
- `name` がない
- `name` と directory 名が一致しない
- `styles/` がない
- `templates/` がない

`defaults` が dict でない場合は空として扱われます。

## CSS レイヤーの責務

依存順は次です。

```text
tokens.primitives.css
-> tokens.semantic.css
-> tokens.component.css
-> shared/styles/slide.css
-> themes/<name>/styles/slide.css
```

### `tokens.primitives.css`

- theme 実装の素の値
- 色は `brand-*` / `neutral-*` を基本語彙にする

### `tokens.semantic.css`

- renderer / component が参照する意味レイヤー
- theme 間の差分をここで吸収する

### `tokens.component.css`

- component 単位の token
- color は semantic token から取る

### `slide.css`

- theme 固有の layout / decoration / typography override を置く
- 共通化できるものは `shared/styles/slide.css` に寄せる

## Template の責務

- `base.html.j2` は head と共通骨格
- slide 別 template は視覚差分の責任を持つ
- `agenda.html.j2` は fallback しないので必須

## `design.config.yaml` と theme defaults の分担

- baseline の見た目は theme defaults で決める
- `design.config.yaml` は project 固有 override だけを置く
- theme を追加するときに baseline 値を config に逃がさない

## 確認コマンド

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

## visual QA の進め方

theme を作ったら `visual-qa.md` の手順で built-in theme と並べて確認します。

## よくある失敗

- `theme.yaml.name` と directory 名が一致していない
- `agenda.html.j2` や `styles/` が欠けている
- baseline 値を `design.config.yaml` に持たせすぎて theme 切り替えが効かなくなる
- 幅制限だけを追加して `.main` の中央配置を忘れ、見出しが左に寄って見える
- component token が primitive color を直接参照して、theme 差し替えで責務が崩れる

## 関連文書

- `theme-system.md`
- `workflow.md`
- `visual-qa.md`
