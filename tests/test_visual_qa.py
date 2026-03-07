import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "skills" / "scripts" / "run_visual_qa.py"
)
SPEC = importlib.util.spec_from_file_location("run_visual_qa", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class VisualQaTest(unittest.TestCase):
    def test_detect_new_version_finds_single_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            (output_dir / "v1").mkdir()
            before = MODULE.list_output_versions(output_dir)
            (output_dir / "v2").mkdir()

            self.assertEqual(MODULE.detect_new_version(output_dir, before), "v2")

    def test_detect_new_version_rejects_ambiguous_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            before = MODULE.list_output_versions(output_dir)
            (output_dir / "v1").mkdir()
            (output_dir / "v2").mkdir()

            with self.assertRaisesRegex(ValueError, "expected exactly one new version"):
                MODULE.detect_new_version(output_dir, before)

    def test_build_report_html_includes_theme_rows_and_page_links(self) -> None:
        html = MODULE.build_report_html(
            workspace=Path("/tmp/workspace"),
            project_root=Path("/tmp/workspace/project"),
            sample_input=Path("/repo/skills/assets/sample-catalog.md"),
            theme_runs=[
                MODULE.ThemeRun(theme="classic", version="v1"),
                MODULE.ThemeRun(theme="minimal", version="v2"),
            ],
            page_specs=[("01-cover", "Cover")],
            include_screenshots=True,
            notes_path=Path("/tmp/workspace/report/notes.md"),
        )

        self.assertIn("Multi-Theme Visual QA", html)
        self.assertIn("../project/output/v1/slides/slides.html", html)
        self.assertIn("../project/output/v2/slides/pages/01-cover.html", html)
        self.assertIn("../screenshots/classic--01-cover.png", html)
        self.assertIn("01-cover - Cover", html)
        self.assertIn("notes.md", html)

    def test_select_page_specs_keeps_known_labels_and_falls_back_to_stem(self) -> None:
        page_specs = MODULE.select_page_specs(["01-cover", "88-custom"])

        self.assertEqual(page_specs[0], ("01-cover", "Cover"))
        self.assertEqual(page_specs[1], ("88-custom", "88-custom"))

    def test_build_notes_markdown_includes_sections_and_theme_runs(self) -> None:
        notes = MODULE.build_notes_markdown(
            theme_runs=[
                MODULE.ThemeRun(theme="classic", version="v1"),
                MODULE.ThemeRun(theme="minimal", version="v2"),
            ],
            page_specs=[("01-cover", "Cover"), ("02-agenda", "Agenda")],
        )

        self.assertIn("# Visual QA Notes", notes)
        self.assertIn("`classic` -> `v1`", notes)
        self.assertIn("`02-agenda` - Agenda", notes)
        self.assertIn("## 1. Theme 固有の破綻", notes)
        self.assertIn("## 3. サンプル入力由来の見え方", notes)


if __name__ == "__main__":
    unittest.main()
