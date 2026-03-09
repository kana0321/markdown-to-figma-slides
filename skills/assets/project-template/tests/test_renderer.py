import sys
import unittest
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


PROJECT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = PROJECT_TEMPLATE_ROOT / "scripts"

if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from config import load_config, load_theme
from models import Block, Inline, Slide
from renderer import _render_slide, blocks_to_html


class RendererTest(unittest.TestCase):
    def test_render_slide_renders_cover_logo_from_branding_config(self) -> None:
        env = Environment(
            loader=FileSystemLoader(
                [
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates"),
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates" / "custom"),
                ]
            ),
            autoescape=False,
        )
        config = load_config(PROJECT_TEMPLATE_ROOT / "design.config.yaml")
        config.branding.cover_logo_enabled = True
        config.branding.cover_logo_src = "images/logo-horizontal.svg"
        config.branding.cover_logo_alt = "Acme"
        theme = load_theme(PROJECT_TEMPLATE_ROOT, "classic")
        slide = Slide(type="cover", title="Cover Title")

        html, _ = _render_slide(env, slide, "cover", config, theme, 1, "../../styles")

        self.assertIn('class="cover-branding"', html)
        self.assertIn('src="images/logo-horizontal.svg"', html)
        self.assertIn('alt="Acme"', html)

    def test_render_slide_does_not_render_cover_logo_when_disabled(self) -> None:
        env = Environment(
            loader=FileSystemLoader(
                [
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates"),
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates" / "custom"),
                ]
            ),
            autoescape=False,
        )
        config = load_config(PROJECT_TEMPLATE_ROOT / "design.config.yaml")
        config.branding.cover_logo_enabled = False
        config.branding.cover_logo_src = "images/logo-horizontal.svg"
        theme = load_theme(PROJECT_TEMPLATE_ROOT, "classic")
        slide = Slide(type="cover", title="Cover Title")

        html, _ = _render_slide(env, slide, "cover", config, theme, 1, "../../styles")

        self.assertNotIn('class="cover-branding"', html)

    def test_render_slide_renders_body_footer_logo_from_branding_config(self) -> None:
        env = Environment(
            loader=FileSystemLoader(
                [
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates"),
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates" / "custom"),
                ]
            ),
            autoescape=False,
        )
        config = load_config(PROJECT_TEMPLATE_ROOT / "design.config.yaml")
        config.branding.footer_logo_enabled = True
        config.branding.footer_logo_src = "images/logo-icon.svg"
        config.branding.footer_logo_alt = "Acme icon"
        theme = load_theme(PROJECT_TEMPLATE_ROOT, "classic")
        slide = Slide(
            type="body",
            title="Body Title",
            blocks=[Block(type="paragraph", children=[Inline(type="text", text="Hello")])],
        )

        html, _ = _render_slide(env, slide, "body", config, theme, 3, "../../styles")

        self.assertIn('class="footer__right"', html)
        self.assertIn('class="footer__logo"', html)
        self.assertIn('src="images/logo-icon.svg"', html)
        self.assertIn('alt="Acme icon"', html)
        self.assertIn('class="footer__page type-caption">3</div>', html)

    def test_render_slide_renders_agenda_footer_logo_from_branding_config(self) -> None:
        env = Environment(
            loader=FileSystemLoader(
                [
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates"),
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates" / "custom"),
                ]
            ),
            autoescape=False,
        )
        config = load_config(PROJECT_TEMPLATE_ROOT / "design.config.yaml")
        config.branding.footer_logo_enabled = True
        config.branding.footer_logo_src = "images/logo-icon.svg"
        config.branding.footer_logo_alt = "Agenda logo"
        theme = load_theme(PROJECT_TEMPLATE_ROOT, "classic")
        slide = Slide(type="agenda", title="Agenda")

        html, _ = _render_slide(env, slide, "agenda", config, theme, 2, "../../styles")

        self.assertIn('class="footer__logo"', html)
        self.assertIn('alt="Agenda logo"', html)
        self.assertIn('class="footer__page type-caption">2</div>', html)

    def test_render_slide_renders_end_cover_logo_from_branding_config(self) -> None:
        env = Environment(
            loader=FileSystemLoader(
                [
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates"),
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates" / "custom"),
                ]
            ),
            autoescape=False,
        )
        config = load_config(PROJECT_TEMPLATE_ROOT / "design.config.yaml")
        config.branding.cover_logo_enabled = True
        config.branding.cover_logo_src = "images/logo-horizontal.svg"
        config.branding.cover_logo_alt = "End logo"
        theme = load_theme(PROJECT_TEMPLATE_ROOT, "classic")
        slide = Slide(type="end", title="Thank you")

        html, _ = _render_slide(env, slide, "end", config, theme, 99, "../../styles")

        self.assertIn('class="cover-branding"', html)
        self.assertIn('alt="End logo"', html)

    def test_render_slide_does_not_render_footer_logo_when_disabled(self) -> None:
        env = Environment(
            loader=FileSystemLoader(
                [
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates"),
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates" / "custom"),
                ]
            ),
            autoescape=False,
        )
        config = load_config(PROJECT_TEMPLATE_ROOT / "design.config.yaml")
        config.branding.footer_logo_enabled = False
        config.branding.footer_logo_src = "images/logo-icon.svg"
        theme = load_theme(PROJECT_TEMPLATE_ROOT, "classic")
        slide = Slide(
            type="body",
            title="Body Title",
            blocks=[Block(type="paragraph", children=[Inline(type="text", text="Hello")])],
        )

        html, _ = _render_slide(env, slide, "body", config, theme, 3, "../../styles")

        self.assertNotIn('class="footer__logo"', html)

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

    def test_render_slide_uses_headerless_shell_for_body_grid_full(self) -> None:
        env = Environment(
            loader=FileSystemLoader(
                [
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates"),
                    str(PROJECT_TEMPLATE_ROOT / "themes" / "classic" / "templates" / "custom"),
                ]
            ),
            autoescape=False,
        )
        config = load_config(PROJECT_TEMPLATE_ROOT / "design.config.yaml")
        theme = load_theme(PROJECT_TEMPLATE_ROOT, "classic")
        slide = Slide(
            type="body",
            title="Grid Full",
            comment={"template": "body-grid-full"},
            blocks=[
                Block(
                    type="grid",
                    meta={
                        "columns": ["1fr", "1fr"],
                        "rows": ["1fr"],
                        "col_gap": "md",
                        "row_gap": "md",
                        "source_kind": "body-grid-full",
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
            ],
        )

        html, _ = _render_slide(env, slide, "body", config, theme, 1, "../../styles")

        self.assertIn('class="slide slide--body slide--body-grid-full"', html)
        self.assertIn('class="main main--grid-full al-col gap-lg ', html)
        self.assertNotIn('<div class="header">', html)
        self.assertIn('data-grid-source-kind="body-grid-full"', html)


if __name__ == "__main__":
    unittest.main()
