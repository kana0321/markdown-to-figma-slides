---
paths:
  - "**"
---

# Global Rules

- `design.config.yaml` と CSS Token ファイルをデザインの信頼できるソースとして扱う。
- 同一入力・同一設定・同一テンプレートで同一出力を再現する。
- 空要素は出力しない（空のタグを生成しない）。
- Markdown 由来文字列は HTML エスケープする（`html.escape(text, quote=True)`）。
- `output/v*` はスナップショットとして扱い、既存バージョンを直接改変しない。
- デザイン調整時は HTML を再生成せず、`design.config.yaml` + `sync_tokens.py` で CSS のみ更新する。
- ファイル入出力のエンコーディングは常に UTF-8 を使う。
- 生成 HTML のファイル名は `{連番:02d}-{テンプレート種別}.html`（例: `01-cover.html`, `03-body.html`）。
- スクリプト実行時のカレントディレクトリはプロジェクトルートを前提とする。`--project-root` オプションがある場合はそれを優先する。
