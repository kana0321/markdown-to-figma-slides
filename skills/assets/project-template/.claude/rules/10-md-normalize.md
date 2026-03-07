---
paths:
  - "scripts/normalize_md.py"
  - "input/**"
---

# Markdown Normalize Rules

- `input/raw` の Markdown を `scripts/normalize_md.py` で正規化し `input/normalized` に出力する。
- 正規化後のファイルを `input/current.md` にコピーする。
- 正規化処理:
  1. 改行を `\n` に統一（`\r\n`, `\r` を変換）
  2. `---` 単独行（水平線）を削除
  3. 3行以上の連続空行を2行に圧縮
  4. `<!-- slide: ... -->` のキーを正規化（小文字化、アルファベット順ソート）
  5. コールアウトタイプを大文字に正規化
  6. 行末スペース削除（ただし末尾ダブルスペースは `<br>` 用に保持する）
- 未知のキーや不正な値は警告を stderr に出して安全な値にフォールバックする。
- 有効なスライドコメントキー: `template`, `confidential`, `show_source`, `show_pages`, `caption`, `status`, `eyebrow`, `subtitle`, `ratio`, `compact`
- ブール値として扱うキー: `confidential`, `show_source`, `show_pages`, `caption`, `compact`（`true`/`1`/`yes` → `true`、それ以外 → `false`）
- `status` の有効値: `success`, `warning`, `danger`, `info`（不正値は `info` にフォールバック）
- コールアウトの有効タイプ: `NOTE`, `TIP`, `WARNING`, `CAUTION`（不正値は `NOTE` にフォールバック）
- スライド末尾に出典・参照行を記述するとフッターに表示される。対応プレフィックス（大文字小文字不問）:
  - 日本語: `出典:` / `参照:` / `参考:`
  - 英語: `Source:` / `Sources:` / `Reference:` / `References:` / `Ref:` / `Refs:` / `Citation:`
  - プレフィックスのラベルはフッターにそのまま残る（例: `参照: Gartner ...`）
