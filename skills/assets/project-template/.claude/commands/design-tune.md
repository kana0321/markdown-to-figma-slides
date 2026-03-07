`design.config.yaml` の変更をCSS Tokenに反映する。HTMLの再生成は行わない。

手順:

1. `design.config.yaml` の内容を読み、ユーザーが何を変えたか確認する。
2. `output/latest.txt` から最新バージョンを取得する。
3. `scripts/sync_tokens.py --project-root . --version <LATEST_VERSION>` を実行する。
4. 変更されたCSSファイルがあれば報告する。
5. ブラウザのリロードで反映されることを案内する。
