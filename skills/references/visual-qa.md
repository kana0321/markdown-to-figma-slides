# Multi-Theme Visual QA

この文書は、theme 追加や theme 関連変更のあとに見た目を確認するための運用手順です。

- 実行手順は `workflow.md`
- theme 作成は `theme-authoring.md`
- 半自動 runner は `../scripts/run_visual_qa.py`
- repo maintainer 向けの判断は `../../docs/maintainer-change-guide.md`

## 何を確認する手順か

自動テストでは次までしか見ません。

- render が成功するか
- 出力ファイルが揃うか

この手順では、その先の見た目を確認します。

- overflow / 詰まり / 余白崩れ
- light / dark での可読性
- semantic token 経由の責務が保たれているか
- shared CSS と theme override の分離が効いているか

## 標準入力

比較用の標準入力は `skills/assets/sample-catalog.md` です。

理由:

- cover / agenda / section / end を含む
- `body`, `body-text`, `body-2col`, `body-3col`, `body-grid`, `body-grid-full`, `body-code`, `body-hero` を含む
- list, table, code block, callout, card, badge, image, arrow, steps を広く含む

## 対象 theme

現時点の built-in theme:

- `classic`
- `minimal`
- `gradient-blue`

新しい theme を追加したら、この 3 theme に加えて新 theme も同じ手順で比較します。

## 推奨: 半自動 runner を使う

repo root から次を実行します。

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
python3 skills/scripts/run_visual_qa.py --themes classic minimal gradient-blue
python3 skills/scripts/run_visual_qa.py --skip-screenshots
```

注意:

- screenshot 取得には `playwright` CLI と browser install が必要
- browser 起動が制限される環境では `--skip-screenshots` で render と report 生成だけ先に回せる
- `report/notes.md` は run ごとの所見メモ雛形として使える

## 手動確認手順

### 1. 作業用 project を用意する

```bash
./skills/scripts/init_project.sh /tmp/my-slides-qa
cp skills/assets/sample-catalog.md /tmp/my-slides-qa/input/raw/sample-catalog.md
```

### 2. theme ごとに render する

```bash
cd /tmp/my-slides-qa
python3 scripts/theme.py --project-root . apply classic
./scripts/run_pipeline.sh --project-root . --input input/raw/sample-catalog.md
python3 scripts/theme.py --project-root . apply minimal
./scripts/run_pipeline.sh --project-root . --input input/raw/sample-catalog.md
```

### 3. preview する

```bash
cd /tmp/my-slides-qa/output
python3 -m http.server 8080
```

`http://localhost:8080/slides.html` を開きます。

## 確認観点チェックリスト

- cover / section / agenda / end が theme ごとに破綻していないか
- `body-text`, `body-2col`, `body-3col`, `body-grid`, `body-grid-full`, `body-code`, `body-hero` が成立しているか
- 見出しや `.main` の中央配置が崩れていないか
- codeblock と table の可読性が落ちていないか
- card / callout / badge / arrow / steps / image の contrast が保たれているか
- shared CSS の変更が特定 theme だけに依存していないか

## 既知ノイズ

- `body-2col` のサンプル文面には、説明用のインラインコードとして `` `#### Left` `` と `` `#### Right` `` が含まれる
- これは `skills/assets/sample-catalog.md` の説明文由来であり、theme 固有の破綻とは分けて扱う
- `body-3col` の `#### Col1` / `#### Col2` / `#### Col3` は routing 用見出しとして問題視しない
- `body-grid` / `body-grid-full` で崩れが見えた場合は、theme 差分より先に parser / renderer 回帰を疑う

## 変更タイプ別の確認範囲

- theme を追加した: 全テンプレートを built-in theme と比較する
- token layer や shared CSS を変えた: 既存 built-in theme 全部で確認する
- 特定 theme の template / slide.css だけを変えた: 変更 theme を中心に確認し、shared への波及がないかも見る

## 記録の残し方

- `report/notes.md` に所見を残す
- `summary.json` と screenshot を run ごとの比較材料として残す

## 関連文書

- `theme-system.md`
- `theme-authoring.md`
- `workflow.md`
