import shutil
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


PROJECT_TEMPLATE_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = PROJECT_TEMPLATE_ROOT / "scripts"

if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from config import load_config, load_theme, resolve_slide


class ConfigTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.project_root = Path(self._tmpdir.name)
        shutil.copytree(PROJECT_TEMPLATE_ROOT / "themes", self.project_root / "themes")
        self.write_config(
            """
            theme:
              name: "classic"

            tokens: {}

            slides: []
            """
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def write_config(self, text: str) -> None:
        self._write_text(self.project_root / "design.config.yaml", text)

    def create_theme(
        self,
        name: str,
        theme_yaml: str,
        *,
        styles: bool = True,
        templates: bool = True,
    ) -> Path:
        theme_root = self.project_root / "themes" / name
        theme_root.mkdir(parents=True, exist_ok=True)
        self._write_text(theme_root / "theme.yaml", theme_yaml)
        if styles:
            (theme_root / "styles").mkdir(exist_ok=True)
        if templates:
            (theme_root / "templates").mkdir(exist_ok=True)
        return theme_root

    def _write_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")

    def test_load_theme_rejects_name_mismatch(self) -> None:
        self.create_theme(
            "broken",
            """
            name: not-broken
            defaults: {}
            """,
        )

        with self.assertRaisesRegex(ValueError, "theme name mismatch"):
            load_theme(self.project_root, "broken")

    def test_load_theme_requires_theme_asset_directories(self) -> None:
        self.create_theme(
            "missing-styles",
            """
            name: missing-styles
            defaults: {}
            """,
            styles=False,
        )
        self.create_theme(
            "missing-templates",
            """
            name: missing-templates
            defaults: {}
            """,
            templates=False,
        )

        with self.assertRaisesRegex(FileNotFoundError, "styles"):
            load_theme(self.project_root, "missing-styles")
        with self.assertRaisesRegex(FileNotFoundError, "templates"):
            load_theme(self.project_root, "missing-templates")

    def test_load_theme_treats_non_dict_defaults_as_empty(self) -> None:
        self.create_theme(
            "list-defaults",
            """
            name: list-defaults
            defaults:
              - not
              - a
              - dict
            """,
        )

        theme = load_theme(self.project_root, "list-defaults")

        self.assertEqual(theme.defaults, {})

    def test_font_links_ignore_invalid_weights(self) -> None:
        self.create_theme(
            "fonty",
            """
            name: fonty
            fonts:
              google:
                - family: Test Sans
                  weights: [700, bad, 400, 700, null]
            defaults: {}
            """,
        )

        theme = load_theme(self.project_root, "fonty")
        links = theme.font_links()

        self.assertEqual(len(links), 3)
        self.assertIn("family=Test+Sans:wght@400;700", links[2])
        self.assertNotIn("bad", links[2])
        self.assertNotIn("None", links[2])

    def test_load_config_merges_theme_defaults_then_project_overrides(self) -> None:
        self.create_theme(
            "custom",
            """
            name: custom
            defaults:
              global:
                lang: "en"
                fonts:
                  sans: "Theme Sans"
              badge:
                enabled: true
                text: "Theme Badge"
              tokens:
                surface-bg: "theme-surface"
                accent: "theme-accent"
              slides:
                - match: body
                  template: body-text
            """,
        )
        self.write_config(
            """
            theme:
              name: "custom"
            global:
              lang: "fr"
            branding:
              cover_logo:
                light_src: "images/project-cover-light.svg"
              footer_logo:
                dark_src: "images/project-footer-dark.svg"
              template_surface:
                body-grid-full: dark
            badge:
              text: "Project Badge"
            tokens:
              accent: "project-accent"
            slides:
              - match: body
                accent_bar: "left"
            """
        )

        config = load_config(self.project_root / "design.config.yaml")

        self.assertEqual(config.theme.name, "custom")
        self.assertEqual(config.global_.lang, "fr")
        self.assertEqual(config.global_.fonts.sans, "Theme Sans")
        self.assertTrue(config.branding.cover_logo_enabled)
        self.assertEqual(
            config.branding.cover_logo.light_src,
            "images/project-cover-light.svg",
        )
        self.assertEqual(
            config.branding.footer_logo.dark_src,
            "images/project-footer-dark.svg",
        )
        self.assertEqual(config.branding.surface_defaults.cover, "dark")
        self.assertEqual(config.branding.surface_defaults.body, "light")
        self.assertEqual(config.branding.template_surface["body-hero"], "dark")
        self.assertEqual(config.branding.template_surface["body-grid-full"], "dark")
        self.assertTrue(config.badge.enabled)
        self.assertEqual(config.badge.text, "Project Badge")
        self.assertEqual(config.tokens["surface-bg"], "theme-surface")
        self.assertEqual(config.tokens["accent"], "project-accent")
        self.assertEqual(len(config.slides), 2)
        self.assertEqual(config.slides[0].template, "body-text")
        self.assertEqual(config.slides[1].accent_bar, "left")

    def test_resolve_slide_applies_type_title_and_markdown_precedence(self) -> None:
        self.create_theme(
            "custom",
            """
            name: custom
            defaults:
              badge:
                enabled: true
                text: "Theme Badge"
                defaults:
                  body: true
              page_number:
                enabled: true
                defaults:
                  body: true
              accent_bar:
                defaults:
                  body: "right"
              tokens:
                surface-bg: "theme-surface"
                tone: "theme-tone"
            """,
        )
        self.write_config(
            """
            theme:
              name: "custom"
            tokens:
              surface-bg: "project-surface"
            slides:
              - match: body
                template: body-text
                page_number: false
                accent_bar: "top"
                tokens:
                  surface-bg: "type-surface"
                  type-only: "yes"
              - match: "## Specific"
                template: body-hero
                page_number: true
                accent_bar: "left"
                tokens:
                  surface-bg: "title-surface"
                  title-only: "yes"
            """
        )

        config = load_config(self.project_root / "design.config.yaml")
        resolved = resolve_slide(
            "body",
            "Specific",
            {
                "template": "body-code",
                "confidential": "false",
                "show_source": "true",
                "compact": "true",
                "ratio": "16:9",
            },
            config,
        )

        self.assertEqual(resolved.template, "body-code")
        self.assertFalse(resolved.badge_enabled)
        self.assertTrue(resolved.page_number_enabled)
        self.assertEqual(resolved.accent_bar, "left")
        self.assertTrue(resolved.show_source)
        self.assertTrue(resolved.compact)
        self.assertEqual(resolved.ratio, "16:9")
        self.assertEqual(resolved.tokens["surface-bg"], "title-surface")
        self.assertEqual(resolved.tokens["tone"], "theme-tone")
        self.assertEqual(resolved.tokens["type-only"], "yes")
        self.assertEqual(resolved.tokens["title-only"], "yes")

    def test_resolve_slide_ignores_unknown_comment_keys(self) -> None:
        config = load_config(self.project_root / "design.config.yaml")

        resolved = resolve_slide(
            "body",
            "Body Title",
            {
                "template": "body-2col",
                "show_pages": "true",
                "caption": "true",
                "status": "warning",
                "unknown": "value",
            },
            config,
        )

        self.assertEqual(resolved.template, "body-2col")
        self.assertFalse(resolved.show_source)
        self.assertFalse(resolved.compact)
        self.assertEqual(resolved.ratio, "")


if __name__ == "__main__":
    unittest.main()
