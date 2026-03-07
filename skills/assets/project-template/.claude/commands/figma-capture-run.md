生成済みの `output/slides.html` をFigmaにキャプチャして完了まで追跡する。

手順:

1. `output/slides.html` と `output/latest.txt` が存在するか確認する。
2. ローカルサーバーが `output/` ディレクトリで起動しているか確認する。
   起動していなければ `cd output && python3 -m http.server 8080` をバックグラウンドで実行する。
3. Figma MCP の `generate_figma_design` ツールでキャプチャを開始する。
   - URL: `http://localhost:8080/slides.html`
4. `captureId` を取得したら、完了するまでポーリングする。
5. 完了したら結果のURLをユーザーに伝える。
