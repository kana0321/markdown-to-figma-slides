import sys
import textwrap
import unittest
from pathlib import Path


PROJECT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = PROJECT_TEMPLATE_ROOT / "scripts"

if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from parser import MarkdownParseError, parse_markdown


class ParserTest(unittest.TestCase):
    def parse(self, text: str):
        return parse_markdown(textwrap.dedent(text).lstrip())

    def test_trailing_slide_comment_belongs_to_next_body_slide(self) -> None:
        deck = self.parse(
            """
            # Deck

            ## Section

            ### First Body
            First paragraph.

            <!-- slide: template=body-code; compact=true -->

            ### Second Body
            Second paragraph.
            """
        )

        _, body_slides = deck.sections[0]
        first_body, second_body = body_slides

        self.assertEqual(first_body.comment, {})
        self.assertEqual(second_body.comment["template"], "body-code")
        self.assertEqual(second_body.comment["compact"], "true")

    def test_body_slide_uses_eyebrow_comment_and_drops_subtitle_comment(self) -> None:
        deck = self.parse(
            """
            # Deck

            ## Section Title

            ### Body Title
            <!-- slide: eyebrow=Custom Eyebrow; subtitle=Body Subtitle -->
            Body paragraph.
            """
        )

        _, body_slides = deck.sections[0]
        body = body_slides[0]

        self.assertEqual(body.eyebrow, "Custom Eyebrow")
        self.assertEqual(body.subtitle, "")
        self.assertNotIn("subtitle", body.comment)

    def test_body_slide_defaults_eyebrow_to_section_title(self) -> None:
        deck = self.parse(
            """
            # Deck

            ## Section Title

            ### Body Title
            Body paragraph.
            """
        )

        _, body_slides = deck.sections[0]
        body = body_slides[0]

        self.assertEqual(body.eyebrow, "Section Title")

    def test_body_grid_parses_to_grid_ast(self) -> None:
        deck = self.parse(
            """
            # Deck

            ## Section

            ### Grid Slide
            <!-- slide: template=body-grid -->
            <!-- grid: columns=3; rows=2 -->
            <!-- cell: col=1; row=1; col_span=2 -->
            Main message
            <!-- /cell -->
            <!-- cell: col=3; row=1; row_span=2 -->
            Side note
            <!-- /cell -->
            <!-- cell: col=1; row=2 -->
            Bottom left
            <!-- /cell -->
            <!-- cell: col=2; row=2 -->
            Bottom middle
            <!-- /cell -->
            <!-- /grid -->
            """
        )

        _, body_slides = deck.sections[0]
        body = body_slides[0]
        grid = body.blocks[0]

        self.assertEqual(grid.type, "grid")
        self.assertEqual(grid.meta["columns"], ["1fr", "1fr", "1fr"])
        self.assertEqual(grid.meta["rows"], ["1fr", "1fr"])
        self.assertEqual(grid.meta["col_gap"], "md")
        self.assertEqual(grid.meta["row_gap"], "md")
        self.assertEqual(grid.meta["source_kind"], "body-grid")
        self.assertEqual(len(grid.children), 4)
        self.assertEqual(grid.children[0].meta["col_span"], 2)
        self.assertEqual(grid.children[1].meta["row_span"], 2)

    def test_body_grid_resolves_axis_specific_gaps(self) -> None:
        deck = self.parse(
            """
            # Deck

            ## Section

            ### Grid Slide
            <!-- slide: template=body-grid -->
            <!-- grid: columns=3; rows=2; gap=md; col_gap=lg -->
            <!-- cell: col=1; row=1 -->
            A
            <!-- /cell -->
            <!-- cell: col=2; row=1 -->
            B
            <!-- /cell -->
            <!-- /grid -->
            """
        )

        _, body_slides = deck.sections[0]
        grid = body_slides[0].blocks[0]

        self.assertEqual(grid.meta["col_gap"], "lg")
        self.assertEqual(grid.meta["row_gap"], "md")

    def test_body_grid_full_parses_with_same_strict_grid_grammar(self) -> None:
        deck = self.parse(
            """
            # Deck

            ## Section

            ### Grid Slide
            <!-- slide: template=body-grid-full -->
            <!-- grid: columns=2; rows=1 -->
            <!-- cell: col=1; row=1 -->
            A
            <!-- /cell -->
            <!-- cell: col=2; row=1 -->
            B
            <!-- /cell -->
            <!-- /grid -->
            """
        )

        _, body_slides = deck.sections[0]
        grid = body_slides[0].blocks[0]

        self.assertEqual(grid.type, "grid")
        self.assertEqual(grid.meta["source_kind"], "body-grid-full")
        self.assertEqual(grid.meta["columns"], ["1fr", "1fr"])
        self.assertEqual(grid.meta["rows"], ["1fr"])

    def test_legacy_body_2col_normalizes_to_grid_ast(self) -> None:
        deck = self.parse(
            """
            # Deck

            ## Section

            ### Two Col
            <!-- slide: template=body-2col; ratio=6040 -->
            #### Left
            Left side
            #### Right
            Right side
            """
        )

        _, body_slides = deck.sections[0]
        grid = body_slides[0].blocks[0]

        self.assertEqual(grid.type, "grid")
        self.assertEqual(grid.meta["source_kind"], "body-2col")
        self.assertEqual(grid.meta["columns"], ["3fr", "2fr"])
        self.assertEqual(grid.meta["col_gap"], "lg")
        self.assertEqual(grid.meta["row_gap"], "lg")
        self.assertEqual(len(grid.children), 2)
        self.assertEqual(grid.children[0].children[0].type, "paragraph")
        self.assertEqual(grid.children[1].children[0].type, "paragraph")

    def test_legacy_body_3col_keeps_empty_column_as_empty_cell(self) -> None:
        deck = self.parse(
            """
            # Deck

            ## Section

            ### Three Col
            <!-- slide: template=body-3col -->
            #### Col1
            First
            #### Col3
            Third
            """
        )

        _, body_slides = deck.sections[0]
        grid = body_slides[0].blocks[0]

        self.assertEqual(grid.meta["source_kind"], "body-3col")
        self.assertEqual(len(grid.children), 3)
        self.assertTrue(grid.children[0].children)
        self.assertFalse(grid.children[1].children)
        self.assertTrue(grid.children[2].children)

    def test_body_grid_extracts_footer_source_from_last_cell(self) -> None:
        deck = self.parse(
            """
            # Deck

            ## Section

            ### Grid Source
            <!-- slide: template=body-grid -->
            <!-- grid: columns=2; rows=1 -->
            <!-- cell: col=1; row=1 -->
            Primary content
            <!-- /cell -->
            <!-- cell: col=2; row=1 -->
            Supporting content

            Source: Internal handbook
            <!-- /cell -->
            <!-- /grid -->
            """
        )

        _, body_slides = deck.sections[0]
        body = body_slides[0]

        self.assertEqual(body.source, "Source: Internal handbook")
        self.assertEqual(len(body.blocks[0].children[1].children), 1)

    def test_body_grid_rejects_unknown_attribute(self) -> None:
        with self.assertRaisesRegex(MarkdownParseError, "unknown grid attribute 'gutter'"):
            self.parse(
                """
                # Deck

                ## Section

                ### Grid Slide
                <!-- slide: template=body-grid -->
                <!-- grid: columns=2; rows=2; gutter=md -->
                <!-- cell: col=1; row=1 -->
                A
                <!-- /cell -->
                <!-- /grid -->
                """
            )

    def test_body_grid_rejects_duplicate_cell_attribute(self) -> None:
        with self.assertRaisesRegex(MarkdownParseError, "duplicate cell attribute 'col'"):
            self.parse(
                """
                # Deck

                ## Section

                ### Grid Slide
                <!-- slide: template=body-grid -->
                <!-- grid: columns=2; rows=1 -->
                <!-- cell: col=1; col=2; row=1 -->
                A
                <!-- /cell -->
                <!-- /grid -->
                """
            )

    def test_body_grid_rejects_content_outside_grid(self) -> None:
        with self.assertRaisesRegex(MarkdownParseError, "does not allow content outside"):
            self.parse(
                """
                # Deck

                ## Section

                ### Grid Slide
                <!-- slide: template=body-grid -->
                Intro text
                <!-- grid: columns=2; rows=1 -->
                <!-- cell: col=1; row=1 -->
                A
                <!-- /cell -->
                <!-- /grid -->
                """
            )

    def test_body_grid_rejects_content_inside_grid_but_outside_cell(self) -> None:
        with self.assertRaisesRegex(MarkdownParseError, "does not allow content outside"):
            self.parse(
                """
                # Deck

                ## Section

                ### Grid Slide
                <!-- slide: template=body-grid -->
                <!-- grid: columns=2; rows=1 -->
                Orphan text
                <!-- cell: col=1; row=1 -->
                A
                <!-- /cell -->
                <!-- /grid -->
                """
            )

    def test_body_grid_rejects_overlap(self) -> None:
        with self.assertRaisesRegex(MarkdownParseError, "grid cells overlap at row=1 col=2"):
            self.parse(
                """
                # Deck

                ## Section

                ### Grid Slide
                <!-- slide: template=body-grid -->
                <!-- grid: columns=3; rows=1 -->
                <!-- cell: col=1; row=1; col_span=2 -->
                A
                <!-- /cell -->
                <!-- cell: col=2; row=1 -->
                B
                <!-- /cell -->
                <!-- /grid -->
                """
            )

    def test_body_grid_rejects_out_of_bounds_cell(self) -> None:
        with self.assertRaisesRegex(MarkdownParseError, "exceeds declared grid size 2x2"):
            self.parse(
                """
                # Deck

                ## Section

                ### Grid Slide
                <!-- slide: template=body-grid -->
                <!-- grid: columns=2; rows=2 -->
                <!-- cell: col=2; row=2; col_span=2 -->
                A
                <!-- /cell -->
                <!-- /grid -->
                """
            )

    def test_body_grid_requires_at_least_one_cell(self) -> None:
        with self.assertRaisesRegex(MarkdownParseError, "requires at least one"):
            self.parse(
                """
                # Deck

                ## Section

                ### Grid Slide
                <!-- slide: template=body-grid -->
                <!-- grid: columns=2; rows=2 -->
                <!-- /grid -->
                """
            )

    def test_body_grid_rejects_unclosed_cell(self) -> None:
        with self.assertRaisesRegex(MarkdownParseError, "found before <!-- /cell -->"):
            self.parse(
                """
                # Deck

                ## Section

                ### Grid Slide
                <!-- slide: template=body-grid -->
                <!-- grid: columns=2; rows=1 -->
                <!-- cell: col=1; row=1 -->
                A
                <!-- /grid -->
                """
            )


if __name__ == "__main__":
    unittest.main()
