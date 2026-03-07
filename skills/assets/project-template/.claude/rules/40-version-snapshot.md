---
paths:
  - "scripts/create_version.py"
  - "output/**"
---

# Version Snapshot Rules

- バージョンは `v1`, `v2`, ... と連番。`create_version.py` が `output/` 内の既存ディレクトリから自動決定する。
- 各バージョンのスナップショットには以下を含む:
  - `slides/pages/*.html` — ページ別 HTML
  - `slides/slides.html` — all-in-one HTML（キャプチャ入口）
  - `source/input.raw.md` — 元の Markdown
  - `source/input.normalized.md` — 正規化済み Markdown
  - `source/design.config.yaml` — 使用した設定ファイル
  - `styles/` — 使用した CSS トークンファイルのコピー
  - `SLIDES.md` — スライド一覧（人間向け）
  - `manifest.json` — メタデータ（version, source_path, source_sha256, generated_at, pages, capture_entry）
- 既存バージョンは読み取り専用。修正が必要な場合は新バージョンを生成する。
- `output/latest.txt` に最新バージョン名を記録する。
- `output/slides.html` は最新バージョンへの JavaScript リダイレクト。
