---
paths:
  - "output/**"
---

# Figma Capture Rules

## 前提条件

- `output/` ディレクトリで `python3 -m http.server 8080` が起動していること。
- Figma MCP サーバーが接続されていること。

## キャプチャの流れ

1. ローカルサーバーを起動する:
   ```bash
   cd output && python3 -m http.server 8080
   ```
2. キャプチャは常に `http://localhost:8080/slides.html` を入口とする。このURLは最新バージョンの `slides/slides.html` にリダイレクトされる。
3. 生成 HTML には `<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>` が必須。削除しない。
4. Figma MCP の `generate_figma_design` ツールでキャプチャを開始する。
5. `captureId` を取得したら、同じ `generate_figma_design(captureId=...)` で完了までポーリングする。
6. ステータスが `completed` になったら、結果の Figma URL をユーザーに伝える。

## エラー時の対処

- ポーリングで `failed` が返った場合は、エラー内容をユーザーに報告し、再キャプチャを提案する。
- ローカルサーバーが起動していない場合、キャプチャ前に起動を案内する。
- `output/slides.html` や `output/latest.txt` が存在しない場合、先にスライド生成（`/slides-generate`）を案内する。
