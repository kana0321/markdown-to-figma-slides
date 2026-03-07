# Maintainer Change Guide

## この文書の目的

この文書は、`markdown-to-figma-slides` に変更を入れるときに、どの種類の変更がどの層へ波及するかを素早く判断するための maintainer 向けメモです。

細かい設計方針の正本は次を参照する。

- `docs/theme-design.md`
- `docs/theme-authoring.md`
- `docs/multi-theme-visual-qa.md`
- `docs/theme-doc-update-checklist.md`

## まず先に切り分けること

変更を始める前に、次のどちらかを先に決める。

1. 既存の slide / component に見た目要素を足したいのか
2. Markdown から新しい component を正式に扱いたいのか

この 2 つは見た目が似ていても、変更範囲がかなり違う。

## パターン A: template / theme 装飾変更

例:

- `cover` に会社ロゴを入れる
- `section` の装飾ラインを変える
- `end` に補助コピーを足す
- 既存 card の accent variant を少し調整する

これは基本的に「既存 contract の中で見た目を変える」変更。
新しい Markdown 構文や AST を増やさないなら、比較的軽い。

### 主に触る場所

#### 1. 入力の置き場所を決める

まず、その変更がどこで決まるべきかを決める。

- theme 固定なら `theme.yaml`
- project ごとに変えたいなら `design.config.yaml`
- slide ごとに変えたいなら既存 slide override で足りるか確認する

#### 2. config loader が必要か確認する

project override を増やすなら、`skills/assets/project-template/scripts/config.py` を更新する。

見るポイント:

- dataclass 追加が必要か
- theme defaults と project override の merge 順に合うか
- slide override と衝突しないか

#### 3. template を変更する

既存 slide type に要素を足すなら、まず template を見る。

主な対象:

- `themes/<name>/templates/cover.html.j2`
- `themes/<name>/templates/section.html.j2`
- `themes/<name>/templates/end.html.j2`
- 必要なら `themes/<name>/templates/base.html.j2`

判断:

- 共通構造の話なら `base.html.j2`
- slide type 固有ならその slide template

#### 4. CSS の責務を決める

装飾が全 theme 共通なら `shared/styles/slide.css` を優先する。
theme ごとの差分なら各 theme の `styles/slide.css` に置く。

原則:

- 共通化できるものは shared に寄せる
- theme 固有の見た目は theme 側に留める

#### 5. asset 配置を決める

ロゴや装飾画像を使うなら、どこに置くかを決める。

- theme asset として固定したいなら `themes/<name>/` 側
- project ごとに差し替えたいなら project input 側

#### 6. sample / docs / QA を見る

ユーザーが触る仕様に影響するなら、次も更新候補になる。

- `skills/assets/sample-catalog.md`
- `skills/references/markdown-mapping.md`
- `docs/multi-theme-visual-qa.md`

### 変更規模の目安

- 小: template と CSS だけ
- 小〜中: `config.py` に入力追加が入る
- 中: 全 theme template に同種の変更が必要

## パターン B: 新 component の正式追加

例:

- 新しい callout variant を正式 component にする
- timeline / metric strip / quote block を追加する
- 新しい HTML comment 記法を増やす

これは「見た目追加」ではなく「renderer が理解する構造追加」。
変更範囲は明確に広い。

### 主に触る場所

#### 1. Markdown 記法を決める

まず input syntax を決める。

参照先:

- `skills/references/markdown-mapping.md`

決めること:

- 既存 comment 記法に寄せるか
- block 構造として追加するか
- slide override で十分か

#### 2. parser を更新する

新しい記法を読むには、`skills/assets/project-template/scripts/parser.py` を更新する。

見るポイント:

- 既存 block 判定との競合
- ネスト時の扱い
- 不正入力時の fallback

#### 3. AST model を更新する

`skills/assets/project-template/scripts/models.py` に新 block 表現が必要か確認する。

判断:

- 既存 block の variant で表現できるなら増やさない
- renderer 分岐に新しい意味が必要なら追加する

#### 4. renderer を更新する

`skills/assets/project-template/scripts/renderer.py` で HTML 出力を足す。

見るポイント:

- 既存 component と同じ template / partial に載せられるか
- inline / block の責務が崩れないか
- deck 内の他 block と並んだときに自然か

#### 5. CSS / token を更新する

新 component が theme 横断で成立するには、shared と token の責務整理が必要。

主な対象:

- `shared/styles/slide.css`
- `themes/<name>/styles/tokens.semantic.css`
- `themes/<name>/styles/tokens.component.css`
- 必要なら `themes/<name>/styles/slide.css`

原則:

- color は semantic token から取る
- theme ごとの差分は必要最小限だけ theme 側へ寄せる

#### 6. sample を追加する

新 component を入れたら、`skills/assets/sample-catalog.md` に必ずサンプルを足す。

理由:

- render smoke の入力になる
- visual QA の比較対象になる
- 使い方の実例になる

#### 7. docs を更新する

必要に応じて次を更新する。

- `skills/references/markdown-mapping.md`
- `skills/SKILL.md`
- `skills/references/workflow.md`
- `docs/multi-theme-visual-qa.md`

#### 8. tests と visual QA を回す

最低限見るもの:

- parser / config / renderer まわりの unit test
- built-in theme の render smoke
- `python3 skills/scripts/run_visual_qa.py`

### 変更規模の目安

- 中: renderer + CSS + sample 追加
- 中〜大: parser + model + renderer + sample + docs + tests
- 大: template contract にも影響する

## 判断に迷ったときの目安

次に当てはまるなら、まずパターン A を疑う。

- 既存 slide type の見た目を良くしたいだけ
- Markdown 記法を増やしたくない
- theme ごとの差分として閉じたい

次に当てはまるなら、パターン B を疑う。

- ユーザーが Markdown で新しい構造を書けるようにしたい
- sample-catalog に新しい項目を増やす必要がある
- parser / renderer の認識対象が増える

## 実務上のおすすめ順序

迷ったら、次の順で考える。

1. 既存 slide / component の variant で吸収できないか
2. template と CSS の変更だけで済まないか
3. それでも無理なら新 component を正式追加する

新 component の正式追加は便利だが、そのぶん parser / renderer / QA / docs / tests の保守面積が増える。
先に軽い表現拡張で足りるかを見る方が安全。
