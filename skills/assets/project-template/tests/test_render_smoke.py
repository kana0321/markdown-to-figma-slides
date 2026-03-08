import shutil
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


PROJECT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PROJECT_TEMPLATE_ROOT.parents[2]
SAMPLE_CATALOG_PATH = REPO_ROOT / "skills" / "assets" / "sample-catalog.md"


class RenderSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.project_root = Path(self._tmpdir.name) / "project"
        shutil.copytree(PROJECT_TEMPLATE_ROOT, self.project_root)
        shutil.copy2(SAMPLE_CATALOG_PATH, self.project_root / "input" / "current.md")

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def write_theme_config(self, theme_name: str) -> None:
        (self.project_root / "design.config.yaml").write_text(
            textwrap.dedent(
                f"""
                theme:
                  name: "{theme_name}"

                tokens: {{}}

                slides: []
                """
            ).lstrip(),
            encoding="utf-8",
        )

    def run_generate(self, theme_name: str, version: str) -> subprocess.CompletedProcess[str]:
        self.write_theme_config(theme_name)
        return subprocess.run(
            [
                "python3",
                str(self.project_root / "scripts" / "generate_slides.py"),
                "--project-root",
                str(self.project_root),
                "--input",
                str(self.project_root / "input" / "current.md"),
                "--version",
                version,
            ],
            capture_output=True,
            text=True,
            check=True,
        )

    def assert_render_output(self, version: str) -> None:
        version_root = self.project_root / "output" / version
        self.assertTrue((version_root / "SLIDES.md").exists())
        self.assertTrue((version_root / "manifest.json").exists())
        self.assertTrue((version_root / "slides" / "slides.html").exists())
        self.assertTrue((version_root / "styles" / "slide.css").exists())
        self.assertTrue((version_root / "styles" / "shared" / "slide.css").exists())
        self.assertTrue((version_root / "styles" / "tokens.primitives.css").exists())
        self.assertTrue((version_root / "styles" / "tokens.semantic.css").exists())
        self.assertTrue((version_root / "styles" / "tokens.component.css").exists())
        self.assertTrue(any((version_root / "slides" / "pages").glob("*.html")))

    def test_generate_slides_succeeds_for_built_in_themes(self) -> None:
        for theme_name, version in (
            ("classic", "vclassic"),
            ("minimal", "vminimal"),
            ("gradient-blue", "vgradientblue"),
        ):
            result = self.run_generate(theme_name, version)

            self.assertIn("generated:", result.stdout)
            self.assertIn("(75 slides)", result.stdout)
            self.assert_render_output(version)

        self.assertTrue((self.project_root / "output" / "slides.html").exists())
        self.assertTrue((self.project_root / "output" / "latest.txt").exists())


if __name__ == "__main__":
    unittest.main()
