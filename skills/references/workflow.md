# Workflow Reference

この文書は、project 初期化、スライド生成、再実行判断、手動コマンドの正本です。

- Markdown 記法は `markdown-mapping.md`
- Figma 取り込みは `figma-capture.md`
- theme system の運用ルールは `theme-system.md`

## 1. Initialize

Create a project from bundled scaffold:

```bash
./scripts/init_project.sh /path/to/my-slides
```

Install dependencies if needed:

```bash
pip3 install jinja2 pyyaml pygments
```

Optionally copy the bundled sample deck:

```bash
cp /path/to/repo/skills/assets/sample-catalog.md /path/to/my-slides/input/raw/sample-catalog.md
```

Confirm available themes if needed:

```bash
cd /path/to/my-slides
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . current
```

The scaffold starts with a minimal `design.config.yaml`.
Theme defaults provide the baseline look, and you should only add project-specific overrides.

## 2. Run Pipeline

Run all generation steps:

```bash
cd /path/to/my-slides
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

Outputs:

- `output/vN/slides/pages/*.html`
- `output/vN/slides/slides.html`
- `output/vN/SLIDES.md`
- `output/vN/manifest.json`
- `output/vN/source/` (input snapshots + config snapshot)
- `output/slides.html` (latest redirect entry)

## 3. Rerun Decision

| 変更した対象 | 必要なアクション |
| --- | --- |
| Markdown の内容 | `./scripts/run_pipeline.sh ...` で再生成 |
| 有効 theme の template (`themes/<name>/templates/*.html.j2`) | `./scripts/run_pipeline.sh ...` で再生成 |
| `design.config.yaml` の `theme.name` | `./scripts/run_pipeline.sh ...` で再生成 |
| `design.config.yaml` の色・フォント・トークン | `python3 scripts/sync_tokens.py --project-root . --version vN` |
| `design.config.yaml` の `slides[]` template 指定 | `./scripts/run_pipeline.sh ...` で再生成 |
| 有効 theme の CSS / `shared/styles/slide.css` | `python3 scripts/sync_tokens.py --project-root . --version vN` |

補足:

- `sync_tokens.py --project-root .` は active theme の token CSS を更新する
- `sync_tokens.py --project-root . --version vN` は version 出力側の CSS も更新する
- `theme.name` の変更や template 変更は HTML を再生成する

## 4. Manual Commands

Step-by-step control:

```bash
# Normalize
python3 scripts/normalize_md.py --input input/raw/xxx.md --output input/normalized/xxx.md
cp input/normalized/xxx.md input/current.md

# Version
VERSION=$(python3 scripts/create_version.py --project-root .)

# Sync tokens from config
python3 scripts/sync_tokens.py --project-root .

# Generate
python3 scripts/generate_slides.py --input input/current.md --version $VERSION --project-root .

# Sync tokens into version output
python3 scripts/sync_tokens.py --project-root . --version $VERSION
```

## 5. Theme Operations

Switch the active theme:

```bash
python3 scripts/theme.py --project-root . list
python3 scripts/theme.py --project-root . current
python3 scripts/theme.py --project-root . apply classic
```

Keep `design.config.yaml` thin. The baseline design should come from theme defaults, not from project-level baseline overrides.

For theme-system rules, token layering, and config resolution order, use `theme-system.md`.

## 6. Create or Customize a Theme

When you need a new built-in theme, copy an existing one first:

```bash
cd /path/to/my-slides
cp -R themes/classic themes/my-theme
```

Then inspect and apply it:

```bash
python3 scripts/theme.py --project-root . show my-theme
python3 scripts/theme.py --project-root . apply my-theme
./scripts/run_pipeline.sh --project-root . --input input/raw/source.md
```

Use `theme-authoring.md` for the full authoring rules and `visual-qa.md` for visual verification.

## 7. Preview

```bash
cd output
python3 -m http.server 8080
```

Open `http://localhost:8080/slides.html`.

## 8. Related References

- `markdown-mapping.md` for syntax, templates, comments, and `body-grid`
- `figma-capture.md` for capture flow
- `../docs/body-grid-design.md` for maintainer-facing `body-grid` rationale
- `../docs/maintainer-change-guide.md` for implementation impact by change type
