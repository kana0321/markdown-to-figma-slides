import io
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path


PROJECT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = PROJECT_TEMPLATE_ROOT / "scripts"

if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from normalize_md import normalize


class NormalizeMarkdownTest(unittest.TestCase):
    def test_normalize_slide_comment_drops_removed_keys(self) -> None:
        stderr = io.StringIO()

        with redirect_stderr(stderr):
            normalized = normalize(
                "<!-- slide: template=body-2col; show_pages=true; caption=yes; status=warning; compact=yes -->"
            )

        self.assertEqual(
            normalized,
            "<!-- slide: compact=true; template=body-2col -->",
        )
        err = stderr.getvalue()
        self.assertIn("unknown slide key 'show_pages'", err)
        self.assertIn("unknown slide key 'caption'", err)
        self.assertIn("unknown slide key 'status'", err)


if __name__ == "__main__":
    unittest.main()
