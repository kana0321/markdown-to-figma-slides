# Theme System Reference

この文書は、theme system を利用するときの運用ルールをまとめた利用者向けリファレンスです。

- 実行手順は `workflow.md`
- 新しい theme の作成は `theme-authoring.md`
- visual QA は `visual-qa.md`
- repo maintainer 向けの設計判断は `../../docs/theme-design.md`

## 現在の built-in theme

- `classic`
- `minimal`
- `gradient-blue`

## 基本方針

theme system は、配色の差し替えではなく design package の切り替えとして扱います。

- active theme は `design.config.yaml.theme.name` で決まる
- 描画資産の正本は `themes/<name>/`
- baseline の見た目は theme defaults で決まる
- `design.config.yaml` には project 固有 override だけを書く

## ディレクトリ構成

```text
project-root/
  design.config.yaml
  shared/
    styles/
      slide.css
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

## `design.config.yaml` の役割

`design.config.yaml` は project 固有 override の置き場です。baseline を定義する場所ではありません。

最小構成の例:

```yaml
theme:
  name: "classic"

tokens: {}

slides: []
```

原則:

- baseline は theme defaults で持つ
- theme を切り替えたときに baseline が自然に変わる状態を優先する
- project ごとの微調整だけを `design.config.yaml` に足す

## 設定の解決順序

```text
engine defaults
-> theme defaults
-> design.config.yaml
-> slide override
-> markdown comment
```

## `theme.yaml` の schema

### 必須項目

- `name`
- `defaults`

### 任意項目

- `label`
- `description`
- `fonts.google`

### 必須ディレクトリ

- `themes/<name>/theme.yaml`
- `themes/<name>/styles/`
- `themes/<name>/templates/`

### `name`

- `name` は directory 名と一致している必要がある
- 不一致はエラー

### `fonts.google`

V1 では Google Fonts のみ対応します。

```yaml
fonts:
  google:
    - family: Noto Sans JP
      weights: [400, 500, 700]
```

ルール:

- `family` は必須
- `weights` は任意
- 不正な `weights` はその値だけ無視される

### `defaults`

`defaults` には次を含められます。

- `global`
- `badge`
- `page_number`
- `accent_bar`
- `agenda`
- `end`
- `tokens`
- `slides`

## Theme CLI

`scripts/theme.py` は次を提供します。

- `list`
- `current`
- `show <name>`
- `apply <name>`

例:

```bash
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . current
python3 scripts/theme.py --project-root . show minimal
python3 scripts/theme.py --project-root . apply minimal
```

## Token layer の考え方

依存順は次です。

```text
primitives -> semantic -> component -> shared slide.css -> theme slide.css
```

### primitives

- theme 固有の素の値を置く
- 色は `brand-*` / `neutral-*` を基本語彙にする

### semantic

- renderer / component が参照する意味レイヤー
- theme 間の差分は基本的にここで吸収する

### component

- component 単位の token
- color は semantic token から取る

## 変更内容ごとの実務ルール

- Markdown を変えたら `./scripts/run_pipeline.sh ...` で再生成する
- active theme の template を変えたら `./scripts/run_pipeline.sh ...` で再生成する
- `theme.name` を変えたら `./scripts/run_pipeline.sh ...` で再生成する
- 色・フォント・token だけを変えたら `python3 scripts/sync_tokens.py --project-root . --version vN` で反映できる
- active theme の CSS や `shared/styles/slide.css` を変えたときも CSS sync で反映できる

詳しいコマンドは `workflow.md` を参照してください。

## Known limitations

- `<!-- slide: ... -->` で実効なのは主に `template`, `confidential`, `show_source`, `compact`, `ratio` と、body slide の `eyebrow`、cover / section の `subtitle`
- `show_pages`, `caption`, `status` は slide comment key としては受理しない
- body slide で `subtitle` を comment に書いても保持されない
- theme font 読み込みは V1 では Google Fonts 前提

## 関連文書

- `workflow.md`
- `markdown-mapping.md`
- `theme-authoring.md`
- `visual-qa.md`
