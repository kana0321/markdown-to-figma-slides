`input/current.md` からスライドHTMLを生成する。Figma captureは行わない。

手順:

1. `input/current.md` が存在するか確認する。なければユーザーに聞く。
2. `scripts/create_version.py` で次のバージョン番号を取得する。
3. `scripts/sync_tokens.py` で `design.config.yaml` のトークン上書きをCSSに反映する。
4. `scripts/generate_slides.py --input input/current.md --version <VERSION> --project-root .` を実行する。
5. `scripts/sync_tokens.py --version <VERSION>` で出力バージョンにもトークンを反映する。
6. `input/raw/images/` が存在すれば、画像を `output/<VERSION>/slides/images/` と `output/<VERSION>/slides/pages/images/` の両方にコピーする。
7. ソースファイルをスナップショットとして `output/<VERSION>/source/` にコピーする:
   - `input/current.md` → `source/input.normalized.md`
   - `design.config.yaml` → `source/design.config.yaml`
8. 生成結果の `output/<VERSION>/SLIDES.md` を読んでスライド一覧を表示する。
9. プレビュー方法を案内する: `cd output && python3 -m http.server 8080`
