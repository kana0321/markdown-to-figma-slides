# Markdown to Figma Slides

Markdown を HTML スライドに変換し、Figma に取り込むためのプロジェクト。

## 前提条件

- Python 3.9+
- `pip3 install jinja2 pyyaml pygments`

## 基本フロー

1. `input/raw/` に Markdown を置く
2. `./scripts/run_pipeline.sh --project-root . --input input/raw/<file>.md` で生成する
3. 必要なら `python3 scripts/theme.py --project-root . apply <theme>` で theme を切り替える
4. 生成後に `output/slides.html` を preview または Figma capture する

`design.config.yaml` は基本的に最小構成のまま保ち、theme defaults に対する project 固有 override だけを追加する。

初期状態では、同梱の `input/raw/images/logo-horizontal-light.png` /
`logo-horizontal-dark.png` が cover / end 上部と body / agenda footer に表示される。
差し替えたい場合は `design.config.yaml` の `branding.cover_logo` /
`branding.footer_logo` の `light_src` と `dark_src` を更新する。
非表示にしたい側だけ `*_logo_enabled: false` を指定する。

運用の目安:

- built-in theme defaults が branding surface の基準を持つ
- `classic` / `minimal` の cover / end はまず `light`
- `gradient-blue` の cover / end はまず `dark`
- `agenda` / 通常 body はまず `light`
- project ごとの事情があるときだけ `surface_defaults` / `template_surface` を override する

## 変更内容に応じた再実行

| 変更した対象 | 必要なアクション |
| --- | --- |
| Markdown の内容 | `/slides-generate` で再生成 |
| 有効 theme の template (`themes/<name>/templates/*.html.j2`) | `/slides-generate` で再生成 |
| `design.config.yaml` の `theme.name` | `/slides-generate` で再生成 |
| `design.config.yaml` の色・フォント・トークン | `/design-tune` で CSS のみ反映 |
| `design.config.yaml` の `branding.*` | `/slides-generate` で再生成 |
| `design.config.yaml` の `slides[]` template 指定 | `/slides-generate` で再生成 |
| 有効 theme の CSS / `shared/styles/slide.css` | `/design-tune` で出力先にも反映 |

## カスタムスラッシュコマンド

### `/slides-generate`

`input/current.md` から HTML スライドを生成する。Figma capture は行わない。

### `/design-tune`

`design.config.yaml` と CSS 変更を出力先に反映する。HTML の再生成は行わない。

### `/figma-capture-run`

生成済みの `output/slides.html` を Figma にキャプチャし、完了まで追跡する。

## 補足

- active theme は `design.config.yaml.theme.name` で決まる
- 詳細ルールは `.claude/rules/*.md` を参照
