# Multi-Theme Visual QA

## この文書の目的

この文書は、同じ入力 Markdown を複数 theme で描画し、theme system が視覚的に破綻していないかを確認するための運用手順です。

自動テストでは次までしか見ない。

- render が成功するか
- 出力ファイルが揃うか

この手順では、その先の見た目を確認する。

- overflow / 詰まり / 余白崩れ
- light / dark での可読性
- semantic token 経由の責務が保たれているか
- shared CSS と theme override の分離が効いているか

## 使う比較入力

比較用の標準入力は `skills/assets/sample-catalog.md` とする。

理由:

- cover / agenda / section / end を含む
- `body`, `body-text`, `body-2col`, `body-3col`, `body-code`, `body-hero` を含む
- list, table, code block, callout, card, badge, image, arrow, steps を広く含む
- built-in theme の smoke test でも使っている

現時点の既知ノイズ:

- `body-2col` のサンプル文面には、説明用のインラインコードとして `` `#### Left` `` と `` `#### Right` `` が含まれる
- これは `skills/assets/sample-catalog.md` の説明文由来であり、theme 固有の破綻とは分けて扱う
- `body-3col` の `#### Col1` / `#### Col2` / `#### Col3` は現時点では routing 用見出しとして問題視しない

## 対象 theme

現時点の built-in theme:

- `classic`
- `minimal`

新しい theme を追加したときは、この 2 theme に加えて新 theme も同じ手順で比較する。

## 実行手順

### 推奨: 半自動スクリプトを使う

repo root から次を実行する。

```bash
python3 skills/scripts/run_visual_qa.py
```

このスクリプトが行うこと:

- 一時 workspace に検証用 project を作る
- `sample-catalog.md` を入力として built-in theme を順に render する
- representative pages の screenshot を取得する
- 比較用の HTML report、`summary.json`、`notes.md` を出力する

主な option:

```bash
python3 skills/scripts/run_visual_qa.py --workspace /tmp/slides-qa-run
python3 skills/scripts/run_visual_qa.py --themes classic minimal
python3 skills/scripts/run_visual_qa.py --skip-screenshots
```

注意:

- screenshot 取得には `playwright` CLI と browser install が必要
- browser 起動が制限される環境では `--skip-screenshots` で render と report 生成だけ先に回せる
- `report/notes.md` は run ごとの所見メモ雛形として使う

### 手動: project を用意して確認する

### 1. 作業用 project を用意する

```bash
./scripts/init_project.sh /tmp/slides-visual-qa
cd /tmp/slides-visual-qa
cp /path/to/repo/skills/assets/sample-catalog.md input/raw/sample-catalog.md
```

依存が未導入なら追加する。

```bash
pip3 install jinja2 pyyaml pygments
```

### 2. 各 theme を render する

```bash
python3 scripts/theme.py --project-root . apply classic
./scripts/run_pipeline.sh --project-root . --input input/raw/sample-catalog.md

python3 scripts/theme.py --project-root . apply minimal
./scripts/run_pipeline.sh --project-root . --input input/raw/sample-catalog.md
```

補足:

- `run_pipeline.sh` は実行ごとに新しい `output/vN/` を作る
- 比較時は各 `vN` がどの theme か分かるようにメモを残す

### 3. ブラウザで確認する

```bash
cd output
python3 -m http.server 8080
```

各 version の `slides/slides.html` と `slides/pages/*.html` を開いて比較する。

例:

- `http://localhost:8080/v3/slides/slides.html`
- `http://localhost:8080/v4/slides/slides.html`

## 確認順序

確認は次の順で行う。

1. deck 全体の第一印象
2. 必須確認ページの破綻
3. 補足ページの破綻
4. theme らしさが `design.config.yaml` ではなく theme assets だけで成立しているか

## Checklist

### A. deck 全体

- 各 theme で明確に見た目が切り替わっているか
- どの theme でも全ページが描画されるか
- 背景色、文字色、アクセント色のコントラストが十分か
- 主要フォントが意図通りに切り替わっているか

### B. 必須確認ページ

まず次のページは毎回見る。

- `cover`
- `agenda`
- `section`
- `body-text`
- `body-2col`
- `body-3col`
- `body-hero`
- `body-code`
- `table`
- `card`
- `arrow`
- `image`
- `end`

重点観点:

- `cover` でタイトル、subtitle、badge、accent bar の関係が自然か
- `agenda` で section 一覧がはみ出さないか
- `section` で大見出しが潰れないか
- `body` でタイトルと本文の余白バランスが保たれているか
- `body-text` で長文の可読性が落ちていないか
- `body-2col` と `body-3col` でカラム幅と段落折返しが破綻しないか
- `body-code` でコード文字サイズ、行高、背景コントラストが自然か
- `body-hero` で画像 overlay と文字可読性が保たれているか
- `end` で closing slide の密度が不自然でないか

今回の実施で、特に差が出やすいと分かった重点確認:

- `body-hero` は theme 差分よりも画像の強さに引っ張られやすいので、overlay と文字可読性を優先して見る
- `classic` と `minimal` は `cover`, `agenda`, `body-text`, `body-code`, `table`, `card`, `end` の順で見ると差分を把握しやすい
- `body-2col` はカラム崩れと、サンプル文面由来のノイズを分けて判断する

### C. 補足確認 component

- ul / ol / checklist の marker とインデントが安定しているか
- table のセル余白、罫線、文字色が theme に対して自然か
- code block と inline code の判別がつくか
- callout の区別がつくか
- card の標準 variant と accent variant が両立しているか
- badge の status 差分が読めるか
- arrow と steps が theme 差分の中でも崩れないか
- image が不自然にトリミングされたり、周囲余白を壊したりしないか

### D. theme system 観点

- shared CSS を変えずに theme 差分だけで成立しているか
- semantic token の差し替えで大半の component color が制御できているか
- `design.config.yaml` に baseline を逃がしたくなる箇所が出ていないか
- 特定 theme だけで成り立つ例外実装が増えていないか

## 結果の記録ルール

結果は最低限、次の 3 区分で残す。

半自動 runner を使う場合は、workspace の `report/notes.md` に追記する。

### 1. theme 固有の破綻

例:

- `minimal` の agenda で section list が詰まり気味
- `classic` の cover で badge 位置が不自然

### 2. 全 theme 共通の破綻

例:

- `shared/styles/slide.css` 変更後に全 theme で card padding が崩れた
- renderer 変更後に全 theme で page number 位置がずれた

### 3. サンプル入力由来の見え方

例:

- `body-2col` の `` `#### Left` `` / `` `#### Right` `` は説明文なので、視覚ノイズでも theme の不具合とは別扱い
- ヒーロー画像の印象差は画像自体の強さもあるため、theme の良し悪しと切り分けて記録する

## 失敗時の切り分け

見た目が壊れたら、まず責務の層を切り分ける。

1. `themes/<name>/styles/slide.css` の問題か
2. token layer の問題か
3. `shared/styles/slide.css` の問題か
4. `themes/<name>/templates/*.html.j2` の問題か
5. renderer / config contract の問題か

目安:

- 複数 theme で同じ崩れ方をするなら shared 側を疑う
- 1 theme だけで崩れるなら theme asset 側を疑う
- theme ごとの差分だけで崩れるなら semantic / component token を疑う

## 実施タイミング

次のタイミングで最低 1 回は実施する。

- 新しい built-in theme を追加したとき
- `shared/styles/slide.css` を大きく変更したとき
- token layer の責務を変更したとき
- template contract や renderer の構造を変えたとき

docs-only の変更では通常不要。

## 関連

- `docs/theme-design.md`
- `docs/theme-authoring.md`
- `skills/scripts/run_visual_qa.py`
- `skills/assets/project-template/tests/test_render_smoke.py`
