import sys
import unittest
from pathlib import Path


PROJECT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = PROJECT_TEMPLATE_ROOT / "scripts"

if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from models import Block, Inline
from renderer import blocks_to_html


class RendererTest(unittest.TestCase):
    def test_blocks_to_html_renders_grid_with_css_grid_styles(self) -> None:
        grid = Block(
            type="grid",
            meta={
                "columns": ["3fr", "2fr"],
                "rows": ["1fr"],
                "col_gap": "lg",
                "row_gap": "lg",
                "source_kind": "body-2col",
                "declared_columns": 2,
                "declared_rows": 1,
            },
            children=[
                Block(
                    type="grid_cell",
                    meta={"col": 1, "row": 1, "col_span": 1, "row_span": 1, "cell_index": 0},
                    children=[Block(type="paragraph", children=[Inline(type="text", text="Left")])],
                ),
                Block(
                    type="grid_cell",
                    meta={"col": 2, "row": 1, "col_span": 1, "row_span": 1, "cell_index": 1},
                    children=[Block(type="paragraph", children=[Inline(type="text", text="Right")])],
                ),
            ],
        )

        html = blocks_to_html([grid])

        self.assertIn('class="layout-grid layout-grid--legacy-cols"', html)
        self.assertIn("--grid-columns: 3fr 2fr;", html)
        self.assertIn("--grid-rows: 1fr;", html)
        self.assertIn("--grid-col-gap: var(--component-grid-gap-lg);", html)
        self.assertIn("--grid-row-gap: var(--component-grid-gap-lg);", html)
        self.assertIn("grid-column: 1 / span 1; grid-row: 1 / span 1;", html)
        self.assertIn("grid-column: 2 / span 1; grid-row: 1 / span 1;", html)


if __name__ == "__main__":
    unittest.main()
