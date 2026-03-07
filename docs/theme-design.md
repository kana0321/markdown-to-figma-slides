# Theme システム設計

## この文書の位置づけ

この文書は、`markdown-to-figma-slides` における theme system の現在の正本です。
過去の検討経緯ではなく、現時点の仕様、採用した判断、次の論点を整理します。

## 現在の状態

theme system の V1 は実装済みです。
theme 機能まわりの基盤整備は、現時点で概ね一段落しています。

- project template は `themes/<name>/` 配下の assets を使って描画する
- active theme は `design.config.yaml.theme.name` で決まる
- 標準 theme は `classic`
- built-in theme として `minimal`、`gradient-blue` を追加済み
- shared のレイアウト / component CSS は `shared/styles/slide.css` に共通化済み
- 各 theme の `styles/slide.css` は theme 固有 override に寄せた
- `design.config.yaml` は最小構成にし、theme defaults が baseline になるようにした
- `scripts/theme.py` は `list`, `current`, `show`, `apply` を提供する
- `config.py` の回帰テストと multi-theme render smoke test は追加済み
- theme authoring guide は `docs/theme-authoring.md` に整理済み
- multi-theme visual QA 手順は `docs/multi-theme-visual-qa.md` に整理済み
- semi-automated visual QA runner は `skills/scripts/run_visual_qa.py` に追加済み
- maintainer 向けの変更判断メモは `docs/maintainer-change-guide.md` に整理済み
- doc 更新 checklist は `docs/theme-doc-update-checklist.md` に整理済み

現在存在する theme:

- `classic`
- `minimal`
- `gradient-blue`

現時点の整理:

- theme system の基盤実装は概ね完了
- 今後の中心は新しい個別変更への対応と、実運用での確認
- 次の優先は大きな再設計より、個別の theme / template / component 変更を受けて運用で粗を拾うこと

## 目的

スライドの見た目を、数色の上書きではなく、まとまりのある design package として切り替えられるようにする。

theme が担う対象:

- 配色
- フォント
- 装飾ルール
- CSS tokens
- templates
- フォント読み込み

## 基本方針

レンダリングエンジンは共通化し、見た目に関わる資産は theme に寄せる。

共通エンジンとして残すもの:

- Markdown の正規化とパース
- AST モデル
- スライド種別
  - `cover`
  - `section`
  - `agenda`
  - `body`
  - `end`
- ブロック種別
  - `card`
  - `callout`
  - `table`
  - `codeblock`
  - `steps`
  - `arrow`
  - `image`
- template variable contract
- semantic / component token 層

theme が持つもの:

- `styles/`
- `templates/`
- `theme.yaml`
- theme defaults
- フォント読み込み定義

共通エンジン配下に持つもの:

- `shared/styles/slide.css`

## ディレクトリ構成

```text
project-root/
  design.config.yaml
  shared/
    styles/
      slide.css
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

補足:

- project template 直下の旧 `styles/` と `templates/` は廃止済み
- theme assets の正本は `themes/<name>/` のみ

## 設定の考え方

`design.config.yaml` は project 固有 override の置き場であり、baseline を定義する場所ではない。

初期 scaffold の `design.config.yaml` は次の最小構成を基本とする。

```yaml
theme:
  name: "classic"

tokens: {}

slides: []
```

原則:

- baseline の見た目は theme defaults で決まる
- `design.config.yaml` には project 固有の override だけを追加する
- theme を切り替えたときに baseline が変わることを優先する

## 設定の解決順序

```text
engine defaults
-> theme defaults
-> design.config.yaml
-> slide override
-> markdown comment
```

## theme.yaml の V1 schema

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

### `name` の扱い

- `name` は必須
- `name` は directory 名と一致している必要がある
- 不一致はエラー

### `fonts.google`

V1 では Google Fonts のみ対応する。

```yaml
fonts:
  google:
    - family: Noto Sans JP
      weights: [400, 500, 700]
```

ルール:

- `family` は必須
- `weights` は任意
- 不正な `weights` はその値だけ無視
- `fonts.google` がなければ font link は出さない

### `defaults` に含めてよい項目

- `global`
- `badge`
- `page_number`
- `accent_bar`
- `agenda`
- `end`
- `tokens`
- `slides`

## Theme CLI

`scripts/theme.py` が次を提供する。

- `list`
- `current`
- `show <name>`
- `apply <name>`

想定コマンド:

```bash
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . current
python3 scripts/theme.py --project-root . show minimal
python3 scripts/theme.py --project-root . apply minimal
```

## Token 層の方針

依存関係は次を基本とする。

```text
primitives -> semantic -> component -> shared slide.css -> theme slide.css
```

### primitives

primitives は theme 実装の詳細であり、完全な theme 横断共通化は目指さない。

ただし、色の主要語彙は次で揃える。

- `brand-*`
  - その theme の主役色
- `neutral-*`
  - 無彩色パレット

現時点の判断:

- 旧 `orange-*` は `brand-*` に整理済み
- 旧 `gray-*` は `neutral-*` に整理済み
- `beige-100` は今回は据え置き

### semantic

semantic は renderer / component が参照する意味レイヤーとする。

theme ごとの差は、基本的にこの層で吸収する。

### component

component は原則として color を semantic から取る。

現時点の整理:

- `component -> primitives color` は避ける
- 色についてはほぼ semantic 経由に整理済み
- `component -> primitives space/radius/line-height` は現時点では許容

## 複数 theme 検証で得た判断

`minimal` と `gradient-blue` を追加して分かったこと:

- theme は 1つだけでは設計の妥当性を判断しづらい
- `design.config.yaml` に baseline 値を多く持たせると theme 切り替えが効かなくなる
- したがって `design.config.yaml` は薄く保つべき
- primitive color token は `brand` / `neutral` の語彙を使う方が読みやすい
- 複数の contrast が強い theme を持つと、`design.config.yaml` を薄く保つ設計の妥当性が見えやすい

## エラー方針

- theme 名が存在しない場合は即エラー
- `theme.yaml` が存在しない場合は即エラー
- `theme.yaml` が空、または dict でない場合はエラー
- `name` がない場合はエラー
- `name` と directory 名が一致しない場合はエラー
- `styles/` または `templates/` がない場合はエラー
- `defaults` が dict でない場合は空として扱う

## Known Limitations

現時点の制約として、次は仕様として明示して扱う。

- `<!-- slide: ... -->` で実効なのは主に `template`, `confidential`, `show_source`, `compact`, `ratio` と、body slide の `eyebrow`、cover / section の `subtitle`
- `show_pages`, `caption`, `status` は slide comment key としては受理しない
- body slide で `subtitle` を comment に書いても、その値は parse 時に破棄する
- `sync_tokens.py` は output snapshot だけでなく、active theme の `themes/<name>/styles/` 配下の token CSS も更新する
- theme font 読み込みは V1 では Google Fonts 前提
- Figma capture は local HTTP server と capture script 読み込みに依存し、offline 完結ではない

## 採用しない方針

- `design.config.yaml` を baseline 設定の中心にしない
- primitive token の完全な theme 横断共通化は目指さない
- V1 では `extends` や partial theme composition は入れない

## 次の論点

現時点で次に考える候補:

1. visual QA 手順をどこまで routine 化するか
2. `space/radius` も semantic 経由に寄せるべきか
3. 追加 theme の authoring examples をどこまで持つか

## 次に着手するなら

現時点では次の順が妥当:

1. visual QA を回しながら必要なら 4 つ目以降の検証用 theme を追加

現時点では、個別 theme の作り込みは visual QA とセットで判断する。
優先すべきは theme system の安定化と documentation の整理。
