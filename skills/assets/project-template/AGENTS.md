# Markdown to Figma Slides

このプロジェクトでは、以下の順に作業する:

1. `input/raw` のMarkdownを `input/normalized` へ整形
2. `input/current.md` を唯一の生成対象としてHTMLスライドを生成
3. `output/v*` にスナップショット保存
4. デザイン調整は `design.config.yaml` または CSS Token ファイルを編集し、`sync_tokens.py` で反映
5. Figmaキャプチャ時は `output/` でローカルサーバーを起動し、`output/slides.html` を入口に使う

## ファイル構成

- `design.config.yaml` — デザイン設定（色、フォント、バッジ、テンプレート指定等）
- `styles/` — CSS Token ファイル（primitives → semantic → component の3層）
- `templates/` — Jinja2テンプレート（`base.html.j2` を全テンプレートが継承）
- `scripts/` — Python スクリプト群（parser, renderer, config, etc.）
- `input/` — Markdown入力（raw → normalized → current.md）
- `output/` — バージョン付きHTML出力

## ルール

- `input/current.md` を唯一の生成ソースとして扱う
- `output/v*` は読み取り専用スナップショット。既存バージョンを直接改変しない
- デザインの微調整は `design.config.yaml` の `tokens` セクションか CSS ファイルを直接編集。HTML再生成が必要なのは Markdown の内容が変わったときだけ
- テンプレート（`.html.j2`）を編集した場合はHTML再生成が必要
- 生成HTMLには `<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>` を必ず保持する

## カスタムスラッシュコマンド

- `/slides-generate` → `input/current.md` から生成のみ実行（captureしない）
- `/figma-capture-run` → 生成済み `output/slides.html` をFigmaへcaptureして完了まで追跡
- `/design-tune` → `design.config.yaml` の変更をCSS Tokenに反映

詳細ルールは `.claude/rules/*.md` を参照。
