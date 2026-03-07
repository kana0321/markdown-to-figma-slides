import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


PROJECT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_TEMPLATE_ROOT / "scripts" / "theme.py"


class ThemeCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.project_root = Path(self._tmpdir.name)
        shutil.copytree(PROJECT_TEMPLATE_ROOT / "themes", self.project_root / "themes")
        shutil.copy2(
            PROJECT_TEMPLATE_ROOT / "design.config.yaml",
            self.project_root / "design.config.yaml",
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def run_theme(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(SCRIPT_PATH), *args],
            capture_output=True,
            text=True,
            check=True,
        )

    def test_current_accepts_project_root_after_subcommand(self) -> None:
        before = self.run_theme("--project-root", str(self.project_root), "current")
        after = self.run_theme("current", "--project-root", str(self.project_root))

        self.assertEqual(after.stdout, before.stdout)
        self.assertTrue(after.stdout.strip())

    def test_apply_accepts_project_root_after_subcommand(self) -> None:
        result = self.run_theme("apply", "gradient-blue", "--project-root", str(self.project_root))

        self.assertIn("applied theme: gradient-blue", result.stdout)
        config_text = (self.project_root / "design.config.yaml").read_text(encoding="utf-8")
        self.assertIn('name: "gradient-blue"', config_text)


if __name__ == "__main__":
    unittest.main()
