# Theme システム設計

## この文書の位置づけ

この文書は、`markdown-to-figma-slides` における theme system の maintainer 向け設計判断をまとめる文書です。

- 利用者向けの運用ルールは `../skills/references/theme-system.md`
- 新しい theme の作成手順は `../skills/references/theme-authoring.md`
- visual QA の実行手順は `../skills/references/visual-qa.md`
- 実装影響の判断は `docs/maintainer-change-guide.md`

この文書では「どう使うか」より「なぜそう設計しているか」と「maintainer がどこを正本とみなすか」を扱います。

## 現在の状態

theme system の V1 は実装済みです。

- project template は `themes/<name>/` 配下の assets を使って描画する
- active theme は `design.config.yaml.theme.name` で決まる
- 標準 theme は `classic`
- built-in theme として `minimal`、`gradient-blue` を追加済み
- shared のレイアウト / component CSS は `shared/styles/slide.css` に共通化済み
- 各 theme の `styles/slide.css` は theme 固有 override に寄せた
- `design.config.yaml` は最小構成にし、theme defaults が baseline になるようにした
- `scripts/theme.py` は `list`, `current`, `show`, `apply` を提供する
- `config.py` の回帰テストと multi-theme render smoke test は追加済み
- semi-automated visual QA runner は `skills/scripts/run_visual_qa.py` に追加済み

現在存在する built-in theme:

- `classic`
- `minimal`
- `gradient-blue`

現時点の整理:

- theme system の基盤実装は概ね完了
- 今後の中心は大きな再設計より、個別の theme / template / component 変更を運用で検証して粗を拾うこと

## 採用した設計判断

### 1. `themes/<name>/` を正本とする

見た目に関わる資産は theme に寄せ、レンダリングエンジンは共通化する。

theme が持つもの:

- `styles/`
- `templates/`
- `theme.yaml`
- theme defaults
- フォント読み込み定義

共通エンジンとして残すもの:

- Markdown の正規化とパース
- AST モデル
- slide / block type の contract
- semantic / component token 層
- `shared/styles/slide.css`

### 2. `design.config.yaml` は薄く保つ

`design.config.yaml` は project 固有 override の置き場であり、baseline を定義する場所ではない。

重視していること:

- baseline の見た目は theme defaults で決まる
- theme を切り替えたときに baseline が自然に変わる
- project 固有の override だけが config に残る

### 3. 解決順序を固定する

```text
engine defaults
-> theme defaults
-> design.config.yaml
-> slide override
-> markdown comment
```

maintainer は新しい入力面を増やすとき、この順序を崩さないことを優先する。

### 4. template contract は theme 横断で共有する

theme ごとの差は template / CSS で吸収するが、renderer が渡す contract 自体はできるだけ揃える。

この方針により:

- built-in theme を増やしても parser / renderer の保守面積を抑えやすい
- visual QA で同じ sample input を比較しやすい

## Token layering に関する判断

依存関係は次を基本とする。

```text
primitives -> semantic -> component -> shared slide.css -> theme slide.css
```

### primitives

- primitives は theme 実装の詳細であり、完全な theme 横断共通化は目指さない
- 色の主要語彙は `brand-*` / `neutral-*` に揃える
- 旧 `orange-*` は `brand-*` に整理済み
- 旧 `gray-*` は `neutral-*` に整理済み

### semantic

- semantic は renderer / component が参照する意味レイヤー
- theme ごとの差は、基本的にこの層で吸収する

### component

- component は原則として color を semantic から取る
- `component -> primitives color` は避ける
- `component -> primitives space/radius/line-height` は現時点では許容する

## 複数 theme 検証で得た判断

`minimal` と `gradient-blue` を追加して見えたこと:

- theme は 1 つだけでは設計の妥当性を判断しづらい
- `design.config.yaml` に baseline 値を多く持たせると theme 切り替えが効かなくなる
- contrast が強く異なる複数 theme を持つと、semantic token と shared CSS の責務分離の粗が見えやすい

## エラー方針

- theme 名が存在しない場合は即エラー
- `theme.yaml` が存在しない場合は即エラー
- `theme.yaml` が空、または dict でない場合はエラー
- `name` がない場合はエラー
- `name` と directory 名が一致しない場合はエラー
- `styles/` または `templates/` がない場合はエラー
- `defaults` が dict でない場合は空として扱う

## Known limitations

maintainer 観点で明示しておく制約:

- `show_pages`, `caption`, `status` は slide comment key としては受理しない
- body slide で `subtitle` を comment に書いても parse 時に破棄する
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

個別 theme の作り込みは visual QA とセットで判断する。

## 関連文書

- `../skills/references/theme-system.md`
- `../skills/references/theme-authoring.md`
- `../skills/references/visual-qa.md`
- `docs/maintainer-change-guide.md`
- `docs/body-grid-design.md`
