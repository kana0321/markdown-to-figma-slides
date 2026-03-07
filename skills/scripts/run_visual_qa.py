#!/usr/bin/env python3
"""Run semi-automated multi-theme visual QA for built-in themes."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path
from typing import Iterable


DEFAULT_THEMES = [
    "classic",
    "minimal",
    "editorial-serif",
    "dark-editorial",
]

DEFAULT_PAGE_SPECS = [
    ("01-cover", "Cover"),
    ("02-agenda", "Agenda"),
    ("03-section", "Section"),
    ("05-body", "Body Text"),
    ("06-body", "Body 2col"),
    ("09-body", "Body 3col"),
    ("10-body", "Body Hero"),
    ("11-body", "Body Code"),
    ("16-body", "Table"),
    ("23-body", "Card"),
    ("29-body", "Arrow"),
    ("30-body", "Image"),
    ("73-end", "End"),
]

VERSION_RE = re.compile(r"^v\d+$")


@dataclass(frozen=True)
class ThemeRun:
    theme: str
    version: str


def _repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[2]


def list_output_versions(output_dir: Path) -> set[str]:
    if not output_dir.is_dir():
        return set()
    return {
        child.name
        for child in output_dir.iterdir()
        if child.is_dir() and VERSION_RE.fullmatch(child.name)
    }


def detect_new_version(output_dir: Path, before: set[str]) -> str:
    created = sorted(list_output_versions(output_dir) - before)
    if len(created) != 1:
        raise ValueError(f"expected exactly one new version, got: {created}")
    return created[0]


def build_report_html(
    workspace: Path,
    project_root: Path,
    sample_input: Path,
    theme_runs: list[ThemeRun],
    page_specs: list[tuple[str, str]],
    include_screenshots: bool,
    notes_path: Path,
) -> str:
    theme_rows = "\n".join(
        (
            "<tr>"
            f"<td><code>{escape(run.theme)}</code></td>"
            f"<td><code>{escape(run.version)}</code></td>"
            f"<td><a href=\"../project/output/{escape(run.version)}/slides/slides.html\">slides.html</a></td>"
            "</tr>"
        )
        for run in theme_runs
    )

    sections: list[str] = []
    for page_stem, page_label in page_specs:
        cards: list[str] = []
        for run in theme_runs:
            page_href = f"../project/output/{run.version}/slides/pages/{page_stem}.html"
            shot_href = f"../screenshots/{run.theme}--{page_stem}.png"
            image_html = (
                f'<img loading="lazy" src="{shot_href}" alt="{escape(run.theme)} {escape(page_stem)}" />'
                if include_screenshots
                else '<div class="placeholder">Screenshots skipped</div>'
            )
            cards.append(
                "\n".join(
                    [
                        '<article class="card">',
                        f"<h3>{escape(run.theme)} <span>{escape(run.version)}</span></h3>",
                        f'<p><a href="{page_href}">{escape(page_stem)}.html</a></p>',
                        image_html,
                        "</article>",
                    ]
                )
            )
        sections.append(
            "\n".join(
                [
                    "<section>",
                    f"<h2>{escape(page_stem)} - {escape(page_label)}</h2>",
                    '<div class="grid">',
                    *cards,
                    "</div>",
                    "</section>",
                ]
            )
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Multi-Theme Visual QA</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f4f1ea;
      --panel: #fffdf8;
      --ink: #1e2430;
      --muted: #5f6a7d;
      --line: #d9d1c2;
      --accent: #d4593a;
      --shadow: 0 12px 30px rgba(30, 36, 48, 0.08);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      font-family: "Iowan Old Style", "Palatino Linotype", Georgia, serif;
      background:
        radial-gradient(circle at top left, rgba(212, 89, 58, 0.1), transparent 22%),
        linear-gradient(180deg, #faf7f2 0%, var(--bg) 100%);
      color: var(--ink);
    }}

    main {{
      width: min(1400px, calc(100% - 48px));
      margin: 0 auto;
      padding: 40px 0 72px;
    }}

    h1, h2, h3 {{
      margin: 0;
      font-weight: 600;
      line-height: 1.1;
    }}

    h1 {{
      font-size: clamp(2rem, 5vw, 3.8rem);
      margin-bottom: 12px;
    }}

    h2 {{
      font-size: 1.5rem;
      margin: 40px 0 16px;
    }}

    h3 {{
      font-size: 1rem;
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 12px;
    }}

    h3 span {{
      font-size: 0.85rem;
      color: var(--muted);
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
    }}

    p, li, td, th {{
      font-size: 0.98rem;
      line-height: 1.5;
    }}

    a {{
      color: var(--accent);
    }}

    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.92em;
    }}

    .lede {{
      color: var(--muted);
      max-width: 68ch;
      margin-bottom: 24px;
    }}

    .summary {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 16px;
      margin: 24px 0 32px;
    }}

    .summary-card,
    .card {{
      background: color-mix(in srgb, var(--panel) 92%, white);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: var(--shadow);
    }}

    .summary-card {{
      padding: 18px 20px;
    }}

    .summary-card strong {{
      display: block;
      font-size: 0.82rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
      font-family: ui-sans-serif, system-ui, sans-serif;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
    }}

    th, td {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--line);
    }}

    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
    }}

    .card {{
      padding: 14px;
    }}

    .card p {{
      margin: 10px 0 12px;
      color: var(--muted);
    }}

    img,
    .placeholder {{
      width: 100%;
      display: block;
      border-radius: 12px;
      border: 1px solid var(--line);
      background: #ebe6da;
    }}

    .placeholder {{
      min-height: 240px;
      display: grid;
      place-items: center;
      color: var(--muted);
      font-family: ui-sans-serif, system-ui, sans-serif;
    }}

    .note {{
      margin-top: 32px;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <main>
    <h1>Multi-Theme Visual QA</h1>
    <p class="lede">
      Semi-automated output for the built-in slide themes. Open each linked slide HTML when a screenshot needs closer inspection.
    </p>

    <div class="summary">
      <div class="summary-card">
        <strong>Workspace</strong>
        <code>{escape(str(workspace))}</code>
      </div>
      <div class="summary-card">
        <strong>Project Root</strong>
        <code>{escape(str(project_root))}</code>
      </div>
      <div class="summary-card">
        <strong>Sample Input</strong>
        <code>{escape(str(sample_input))}</code>
      </div>
      <div class="summary-card">
        <strong>Notes</strong>
        <a href="{escape(notes_path.name)}">{escape(notes_path.name)}</a>
      </div>
    </div>

    <section class="summary-card">
      <h2>Theme Runs</h2>
      <table>
        <thead>
          <tr>
            <th>Theme</th>
            <th>Version</th>
            <th>Deck</th>
          </tr>
        </thead>
        <tbody>
          {theme_rows}
        </tbody>
      </table>
    </section>

    {"".join(sections)}

    <p class="note">
      Screenshots {"included" if include_screenshots else "were skipped"}.
      Compare these against the checklist in <code>docs/multi-theme-visual-qa.md</code>.
    </p>
  </main>
</body>
</html>
"""


def write_summary_json(
    path: Path,
    workspace: Path,
    project_root: Path,
    sample_input: Path,
    theme_runs: list[ThemeRun],
    page_specs: list[tuple[str, str]],
    include_screenshots: bool,
    notes_path: Path,
) -> None:
    payload = {
        "workspace": str(workspace),
        "project_root": str(project_root),
        "sample_input": str(sample_input),
        "screenshots": include_screenshots,
        "notes": str(notes_path),
        "themes": [asdict(run) for run in theme_runs],
        "pages": [{"stem": stem, "label": label} for stem, label in page_specs],
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def build_notes_markdown(
    theme_runs: list[ThemeRun],
    page_specs: list[tuple[str, str]],
) -> str:
    lines = [
        "# Visual QA Notes",
        "",
        "このファイルは、今回の visual QA run に紐づく所見メモです。",
        "結果は少なくとも次の 3 区分で残します。",
        "",
        "## Theme Runs",
        "",
    ]
    for run in theme_runs:
        lines.append(f"- `{run.theme}` -> `{run.version}`")

    lines.extend(
        [
            "",
            "## Representative Pages",
            "",
        ]
    )
    for stem, label in page_specs:
        lines.append(f"- `{stem}` - {label}")

    lines.extend(
        [
            "",
            "## 1. Theme 固有の破綻",
            "",
            "- `theme:`",
            "- `page:`",
            "- `finding:`",
            "- `severity:`",
            "- `notes:`",
            "",
            "## 2. 全 theme 共通の破綻",
            "",
            "- `page:`",
            "- `finding:`",
            "- `likely_layer:` shared styles / template / renderer / config",
            "- `notes:`",
            "",
            "## 3. サンプル入力由来の見え方",
            "",
            "- `page:`",
            "- `sample_input_note:`",
            "- `why_not_a_theme_bug:`",
            "",
            "## 4. Pass / Needs Follow-up",
            "",
            "- `pass:`",
            "- `needs_follow_up:`",
            "",
            "## 5. Next Actions",
            "",
            "- ",
            "",
        ]
    )
    return "\n".join(lines)


def run_command(command: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def ensure_empty_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()):
        raise SystemExit(f"workspace must be empty: {path}")


def prepare_workspace(requested: str | None) -> Path:
    if requested:
        workspace = Path(requested).resolve()
        ensure_empty_dir(workspace)
        return workspace
    return Path(tempfile.mkdtemp(prefix="slides-visual-qa.")).resolve()


def initialize_project(repo_root: Path, workspace: Path, sample_input: Path) -> Path:
    project_root = workspace / "project"
    init_script = repo_root / "skills" / "scripts" / "init_project.sh"
    run_command([str(init_script), str(project_root)])
    target_input = project_root / "input" / "raw" / sample_input.name
    shutil.copy2(sample_input, target_input)
    print(f"copied sample input: {sample_input} -> {target_input}", flush=True)
    return project_root


def render_themes(project_root: Path, sample_input_name: str, themes: Iterable[str]) -> list[ThemeRun]:
    output_dir = project_root / "output"
    theme_runs: list[ThemeRun] = []
    for theme in themes:
        before = list_output_versions(output_dir)
        run_command(
            ["python3", "scripts/theme.py", "--project-root", ".", "apply", theme],
            cwd=project_root,
        )
        run_command(
            [
                "./scripts/run_pipeline.sh",
                "--project-root",
                ".",
                "--input",
                f"input/raw/{sample_input_name}",
            ],
            cwd=project_root,
        )
        version = detect_new_version(output_dir, before)
        theme_runs.append(ThemeRun(theme=theme, version=version))
    return theme_runs


def capture_screenshots(
    project_root: Path,
    workspace: Path,
    theme_runs: list[ThemeRun],
    page_specs: list[tuple[str, str]],
) -> None:
    if shutil.which("playwright") is None:
        raise SystemExit(
            "playwright CLI not found. Install it or rerun with --skip-screenshots."
        )

    screenshots_dir = workspace / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    for run in theme_runs:
        for page_stem, _ in page_specs:
            page_path = (
                project_root
                / "output"
                / run.version
                / "slides"
                / "pages"
                / f"{page_stem}.html"
            )
            if not page_path.exists():
                raise SystemExit(f"page not found for screenshot capture: {page_path}")
            output_path = screenshots_dir / f"{run.theme}--{page_stem}.png"
            run_command(
                [
                    "playwright",
                    "screenshot",
                    "--device=Desktop Chrome HiDPI",
                    "--full-page",
                    f"file://{page_path}",
                    str(output_path),
                ]
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run semi-automated visual QA.")
    parser.add_argument(
        "--repo-root",
        default=str(_repo_root_from_script()),
        help="Repository root. Defaults to the current repo.",
    )
    parser.add_argument(
        "--workspace",
        default="",
        help="Empty directory to use for the QA run. Defaults to a temp directory.",
    )
    parser.add_argument(
        "--sample-input",
        default="",
        help="Markdown file to use. Defaults to skills/assets/sample-catalog.md.",
    )
    parser.add_argument(
        "--themes",
        nargs="+",
        default=DEFAULT_THEMES,
        help="Theme names to render in order.",
    )
    parser.add_argument(
        "--skip-screenshots",
        action="store_true",
        help="Render slides and build the report without Playwright screenshots.",
    )
    parser.add_argument(
        "--pages",
        nargs="+",
        default=[stem for stem, _ in DEFAULT_PAGE_SPECS],
        help="Representative page stems to include in the report.",
    )
    return parser.parse_args()


def select_page_specs(page_stems: list[str]) -> list[tuple[str, str]]:
    labels = dict(DEFAULT_PAGE_SPECS)
    page_specs: list[tuple[str, str]] = []
    for stem in page_stems:
        page_specs.append((stem, labels.get(stem, stem)))
    return page_specs


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    sample_input = (
        Path(args.sample_input).resolve()
        if args.sample_input
        else repo_root / "skills" / "assets" / "sample-catalog.md"
    )
    if not sample_input.exists():
        raise SystemExit(f"sample input not found: {sample_input}")

    workspace = prepare_workspace(args.workspace or None)
    page_specs = select_page_specs(args.pages)
    project_root = initialize_project(repo_root, workspace, sample_input)
    theme_runs = render_themes(project_root, sample_input.name, args.themes)

    if not args.skip_screenshots:
        capture_screenshots(project_root, workspace, theme_runs, page_specs)

    report_dir = workspace / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    notes_path = report_dir / "notes.md"
    notes_path.write_text(
        build_notes_markdown(theme_runs=theme_runs, page_specs=page_specs),
        encoding="utf-8",
    )
    report_html = build_report_html(
        workspace=workspace,
        project_root=project_root,
        sample_input=sample_input,
        theme_runs=theme_runs,
        page_specs=page_specs,
        include_screenshots=not args.skip_screenshots,
        notes_path=notes_path,
    )
    report_path = report_dir / "index.html"
    report_path.write_text(report_html, encoding="utf-8")
    write_summary_json(
        report_dir / "summary.json",
        workspace=workspace,
        project_root=project_root,
        sample_input=sample_input,
        theme_runs=theme_runs,
        page_specs=page_specs,
        include_screenshots=not args.skip_screenshots,
        notes_path=notes_path,
    )

    print("")
    print("Visual QA run complete")
    print(f"workspace: {workspace}")
    print(f"project:   {project_root}")
    print(f"report:    {report_path}")
    print(f"summary:   {report_dir / 'summary.json'}")
    print(f"notes:     {notes_path}")
    if args.skip_screenshots:
        print("screens:   skipped")
    else:
        print(f"screens:   {workspace / 'screenshots'}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
