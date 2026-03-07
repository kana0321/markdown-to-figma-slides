# Markdown to Figma Slides

Markdown を HTML スライドに変換し、Figma に取り込むためのプロジェクト。

## 前提条件

- Python 3.9+
- `pip3 install jinja2 pyyaml`

## 作業フロー

1. `input/raw/` に Markdown を配置
2. 必要なら `design.config.yaml` の `theme.name` か `python3 scripts/theme.py apply <theme>` でテーマを切り替え
3. 正規化して `input/current.md` を作成
4. HTML スライドを生成し `output/vN/` にスナップショット保存
5. 必要に応じてデザイン調整
6. Figma キャプチャ

## 変更内容に応じた再実行の判断

| 変更した対象 | 必要なアクション |
|---|---|
| Markdown の内容 | `/slides-generate` で再生成 |
| 有効テーマのテンプレート（`themes/<name>/templates/*.html.j2`） | `/slides-generate` で再生成 |
| `design.config.yaml` の `theme.name` | `/slides-generate` で再生成 |
| `design.config.yaml` の色・フォント・トークン | `/design-tune` で CSS のみ反映（HTML 再生成不要） |
| `design.config.yaml` の `slides[]` テンプレート指定 | `/slides-generate` で再生成 |
| 有効テーマの CSS ファイル直接編集 | `/design-tune` で出力先にも反映（`slide.css` 含む） |

## カスタムスラッシュコマンド

### `/slides-generate`

`input/current.md` から HTML スライドを生成する。Figma キャプチャは行わない。
Markdown の内容変更やテンプレート変更後に使う。

### `/design-tune`

`design.config.yaml` のトークン変更を CSS に反映する。`slide.css` の変更も出力先にコピーする。HTML の再生成は行わない。
配色・フォント・余白・レイアウトなどの見た目調整に使う。

### `/figma-capture-run`

生成済みの `output/slides.html` を Figma にキャプチャし、完了まで追跡する。
スライド生成とデザイン調整が終わった後の最終ステップ。

## ファイル構成

- `design.config.yaml` — デザイン設定の唯一のソース
- `themes/<name>/styles/` — テーマごとの CSS トークン（primitives → semantic → component）+ レイアウト
- `themes/<name>/templates/` — テーマごとの Jinja2 テンプレート
- `scripts/` — Python スクリプト群
- `input/` — Markdown 入力（`raw/` → `normalized/` → `current.md`）
- `output/` — バージョン付き HTML 出力（`output/slides.html` が最新版への入口）

詳細ルールは `.claude/rules/*.md` を参照。
