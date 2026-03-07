import sys
import textwrap
import unittest
from pathlib import Path


PROJECT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = PROJECT_TEMPLATE_ROOT / "scripts"

if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from parser import parse_markdown


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


if __name__ == "__main__":
    unittest.main()
