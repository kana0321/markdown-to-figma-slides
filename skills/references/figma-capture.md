# Figma Capture Reference

## Prerequisites

- Local HTTP server running in `output/` directory
- Figma MCP server connected

Note:

- Claude Code can proceed through the capture flow when Figma MCP is available
- Codex cannot currently execute the Figma capture step, so treat this reference as Claude Code-specific for the final handoff

## Capture Flow

1. Start local server:

```bash
cd /path/to/project/output
python3 -m http.server 8080
```

2. Entry URL: `http://localhost:8080/slides.html`
   (redirects to latest version's all-in-one HTML)

3. All generated HTML includes the capture script:
   `<script src="https://mcp.figma.com/mcp/html-to-design/capture.js" async></script>`

4. Use `generate_figma_design` MCP tool to initiate capture.

5. Poll with `generate_figma_design(captureId=...)` until status is `completed`.
