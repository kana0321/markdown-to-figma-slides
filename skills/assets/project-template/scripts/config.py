"""Load and resolve design.config.yaml with theme defaults."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

DEFAULT_THEME_NAME = "gradient-blue"


# ---------------------------------------------------------------------------
# Config data structures
# ---------------------------------------------------------------------------


@dataclass
class ThemeConfig:
    name: str = DEFAULT_THEME_NAME


@dataclass
class FontsConfig:
    sans: str = "Outfit, Noto Sans JP, system-ui, -apple-system, Segoe UI, Roboto, Helvetica Neue, Arial, Hiragino Sans, Noto Sans CJK JP, Yu Gothic, sans-serif"
    mono: str = "JetBrains Mono, ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, Courier New, monospace"


@dataclass
class ColorsConfig:
    accent: str = "#D4593A"
    bg_default: str = "#F5F0E8"
    bg_inverse: str = "#1A1A1A"
    text_primary: str = "#1A1A1A"
    text_secondary: str = "#4D4D4D"


@dataclass
class GlobalConfig:
    lang: str = "ja"
    fonts: FontsConfig = field(default_factory=FontsConfig)
    colors: ColorsConfig = field(default_factory=ColorsConfig)


@dataclass
class TypeDefaults:
    cover: bool = True
    section: bool = True
    agenda: bool = True
    body: bool = True
    end: bool = True


@dataclass
class BadgeConfig:
    enabled: bool = True
    text: str = "Confidential"
    defaults: TypeDefaults = field(
        default_factory=lambda: TypeDefaults(end=False)
    )


@dataclass
class PageNumberConfig:
    enabled: bool = True
    start: int = 1
    defaults: TypeDefaults = field(
        default_factory=lambda: TypeDefaults(cover=False, section=False, end=False)
    )


@dataclass
class AccentBarDefaults:
    cover: str = "left"
    section: str = "none"
    agenda: str = "top"
    body: str = "top"
    end: str = "left"


@dataclass
class AccentBarConfig:
    defaults: AccentBarDefaults = field(default_factory=AccentBarDefaults)


@dataclass
class EndConfig:
    enabled: bool = True
    title: str = "Thank you"
    subtitle: str = ""


@dataclass
class AgendaConfig:
    enabled: bool = True
    title: str = "Agenda"
    eyebrow: str = "Agenda"
    show_pages: bool = False


@dataclass
class BrandingLogoConfig:
    light_src: str = ""
    dark_src: str = ""
    alt: str = "Company logo"


@dataclass
class BrandingSurfaceDefaults:
    cover: str = "light"
    end: str = "light"
    agenda: str = "light"
    body: str = "light"


@dataclass
class BrandingConfig:
    cover_logo_enabled: bool = True
    footer_logo_enabled: bool = True
    cover_logo: BrandingLogoConfig = field(default_factory=BrandingLogoConfig)
    footer_logo: BrandingLogoConfig = field(default_factory=BrandingLogoConfig)
    surface_defaults: BrandingSurfaceDefaults = field(
        default_factory=BrandingSurfaceDefaults
    )
    template_surface: dict[str, str] = field(default_factory=dict)


@dataclass
class SlideOverride:
    match: str = ""
    template: str = ""
    badge: bool | None = None
    page_number: bool | None = None
    accent_bar: str = ""
    show_source: bool | None = None
    compact: bool | None = None
    ratio: str = ""
    subtitle: str = ""
    tokens: dict[str, str] = field(default_factory=dict)


@dataclass
class DesignConfig:
    theme: ThemeConfig = field(default_factory=ThemeConfig)
    global_: GlobalConfig = field(default_factory=GlobalConfig)
    badge: BadgeConfig = field(default_factory=BadgeConfig)
    page_number: PageNumberConfig = field(default_factory=PageNumberConfig)
    accent_bar: AccentBarConfig = field(default_factory=AccentBarConfig)
    agenda: AgendaConfig = field(default_factory=AgendaConfig)
    end: EndConfig = field(default_factory=EndConfig)
    branding: BrandingConfig = field(default_factory=BrandingConfig)
    tokens: dict[str, str] = field(default_factory=dict)
    slides: list[SlideOverride] = field(default_factory=list)


@dataclass
class GoogleFont:
    family: str
    weights: list[int] = field(default_factory=list)


@dataclass
class ThemeDefinition:
    name: str
    root: Path
    label: str = ""
    description: str = ""
    google_fonts: list[GoogleFont] = field(default_factory=list)
    defaults: dict = field(default_factory=dict)

    @property
    def templates_dir(self) -> Path:
        return self.root / "templates"

    @property
    def styles_dir(self) -> Path:
        return self.root / "styles"

    @property
    def theme_yaml_path(self) -> Path:
        return self.root / "theme.yaml"

    def font_links(self) -> list[str]:
        if not self.google_fonts:
            return []

        families: list[str] = []
        for font in self.google_fonts:
            family = font.family.replace(" ", "+")
            if font.weights:
                weights = ";".join(str(weight) for weight in sorted(set(font.weights)))
                families.append(f"family={family}:wght@{weights}")
            else:
                families.append(f"family={family}")

        query = "&".join(families)
        return [
            "https://fonts.googleapis.com",
            "https://fonts.gstatic.com",
            f"https://fonts.googleapis.com/css2?{query}&display=swap",
        ]


# ---------------------------------------------------------------------------
# Theme loading
# ---------------------------------------------------------------------------


def _load_yaml_dict(path: Path) -> dict:
    """Load a YAML file and return a dict."""
    if not path.exists():
        return {}

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def read_project_theme_name(config_path: Path) -> str:
    """Read the selected theme name from design.config.yaml."""
    raw = _load_yaml_dict(config_path)
    theme_raw = raw.get("theme", {})
    if isinstance(theme_raw, dict) and theme_raw.get("name"):
        return str(theme_raw["name"])
    return DEFAULT_THEME_NAME


def load_theme(project_root: Path, theme_name: str) -> ThemeDefinition:
    """Load a theme definition from themes/<name>/theme.yaml."""
    theme_root = project_root / "themes" / theme_name
    theme_yaml_path = theme_root / "theme.yaml"

    if not theme_yaml_path.exists():
        raise FileNotFoundError(
            f"theme not found: {theme_name} ({theme_yaml_path})"
        )

    raw = _load_yaml_dict(theme_yaml_path)
    if not raw:
        raise ValueError(f"invalid theme.yaml: {theme_yaml_path}")

    declared_name = str(raw.get("name", "")).strip()
    if not declared_name:
        raise ValueError(f"theme name is required: {theme_yaml_path}")
    if declared_name != theme_name:
        raise ValueError(
            f"theme name mismatch: directory={theme_name} theme.yaml={declared_name}"
        )

    fonts_raw = raw.get("fonts", {})
    google_raw = fonts_raw.get("google", []) if isinstance(fonts_raw, dict) else []

    google_fonts: list[GoogleFont] = []
    for entry in google_raw:
        if not isinstance(entry, dict):
            continue
        family = str(entry.get("family", "")).strip()
        if not family:
            continue
        weights_raw = entry.get("weights", [])
        weights: list[int] = []
        if isinstance(weights_raw, list):
            for weight in weights_raw:
                try:
                    weights.append(int(weight))
                except (TypeError, ValueError):
                    continue
        google_fonts.append(GoogleFont(family=family, weights=weights))

    defaults = raw.get("defaults", {})
    if not isinstance(defaults, dict):
        defaults = {}

    if not (theme_root / "styles").is_dir():
        raise FileNotFoundError(f"theme styles directory not found: {theme_root / 'styles'}")
    if not (theme_root / "templates").is_dir():
        raise FileNotFoundError(
            f"theme templates directory not found: {theme_root / 'templates'}"
        )

    return ThemeDefinition(
        name=theme_name,
        root=theme_root,
        label=str(raw.get("label", theme_name)),
        description=str(raw.get("description", "")),
        google_fonts=google_fonts,
        defaults=defaults,
    )


def list_themes(project_root: Path) -> list[ThemeDefinition]:
    """List available themes under themes/*."""
    themes_dir = project_root / "themes"
    if not themes_dir.exists():
        return []

    themes: list[ThemeDefinition] = []
    for theme_dir in sorted(p for p in themes_dir.iterdir() if p.is_dir()):
        theme_yaml_path = theme_dir / "theme.yaml"
        if not theme_yaml_path.exists():
            continue
        themes.append(load_theme(project_root, theme_dir.name))
    return themes


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def _merge_dataclass(target, source_dict: dict):
    """Recursively merge a dict into a dataclass instance."""
    if not isinstance(source_dict, dict):
        return
    for key, val in source_dict.items():
        attr_name = key.rstrip("_")
        if not hasattr(target, attr_name):
            attr_name = key + "_"
            if not hasattr(target, attr_name):
                continue
        current = getattr(target, attr_name)
        if isinstance(val, dict) and hasattr(current, "__dataclass_fields__"):
            _merge_dataclass(current, val)
        elif isinstance(val, dict) and isinstance(current, dict):
            current.update(val)
        else:
            setattr(target, attr_name, val)


def _parse_slide_overrides(entries: list[dict]) -> list[SlideOverride]:
    """Parse slide override dicts into dataclasses."""
    parsed: list[SlideOverride] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        override = SlideOverride()
        override.match = entry.get("match", "")
        override.template = entry.get("template", "")
        override.ratio = entry.get("ratio", "")
        override.subtitle = entry.get("subtitle", "")
        if "badge" in entry:
            override.badge = bool(entry["badge"])
        if "page_number" in entry:
            override.page_number = bool(entry["page_number"])
        if "accent_bar" in entry:
            override.accent_bar = str(entry["accent_bar"])
        if "show_source" in entry:
            override.show_source = bool(entry["show_source"])
        if "compact" in entry:
            override.compact = bool(entry["compact"])
        if "tokens" in entry and isinstance(entry["tokens"], dict):
            override.tokens = {str(k): str(v) for k, v in entry["tokens"].items()}
        parsed.append(override)
    return parsed


def _apply_config_dict(config: DesignConfig, raw: dict) -> None:
    """Apply a raw config dict onto DesignConfig."""
    if not isinstance(raw, dict):
        return

    if "theme" in raw and isinstance(raw["theme"], dict):
        _merge_dataclass(config.theme, raw["theme"])
    if "global" in raw:
        _merge_dataclass(config.global_, raw["global"])
    if "badge" in raw:
        _merge_dataclass(config.badge, raw["badge"])
    if "page_number" in raw:
        _merge_dataclass(config.page_number, raw["page_number"])
    if "accent_bar" in raw:
        _merge_dataclass(config.accent_bar, raw["accent_bar"])
    if "agenda" in raw:
        _merge_dataclass(config.agenda, raw["agenda"])
    if "end" in raw:
        _merge_dataclass(config.end, raw["end"])
    if "branding" in raw:
        _merge_dataclass(config.branding, raw["branding"])
    if "tokens" in raw and isinstance(raw["tokens"], dict):
        config.tokens.update({str(k): str(v) for k, v in raw["tokens"].items()})
    if "slides" in raw and isinstance(raw["slides"], list):
        config.slides.extend(_parse_slide_overrides(raw["slides"]))


def load_config(path: Path) -> DesignConfig:
    """Load design.config.yaml and merge engine defaults, theme defaults, and project overrides."""
    project_root = path.parent
    raw = _load_yaml_dict(path)
    theme_name = read_project_theme_name(path)
    theme = load_theme(project_root, theme_name)

    config = DesignConfig()
    config.theme.name = theme.name

    _apply_config_dict(config, theme.defaults)
    _apply_config_dict(config, raw)
    config.theme.name = theme.name

    return config


# ---------------------------------------------------------------------------
# Resolution: find matching override for a slide
# ---------------------------------------------------------------------------


@dataclass
class ResolvedSlideConfig:
    """Fully resolved configuration for a single slide."""

    template: str = "body"
    badge_enabled: bool = True
    badge_text: str = "Confidential"
    page_number_enabled: bool = True
    accent_bar: str = "top"
    show_source: bool = False
    compact: bool = False
    ratio: str = ""
    tokens: dict[str, str] = field(default_factory=dict)


def resolve_slide(
    slide_type: str,
    slide_title: str,
    slide_comment: dict,
    config: DesignConfig,
) -> ResolvedSlideConfig:
    """Resolve the final configuration for a slide."""
    resolved = ResolvedSlideConfig()

    type_badge_default = getattr(config.badge.defaults, slide_type, True)
    resolved.badge_enabled = config.badge.enabled and type_badge_default
    resolved.badge_text = config.badge.text

    type_page_default = getattr(config.page_number.defaults, slide_type, True)
    resolved.page_number_enabled = config.page_number.enabled and type_page_default

    resolved.accent_bar = getattr(config.accent_bar.defaults, slide_type, "top")
    resolved.template = (
        slide_type if slide_type in ("cover", "section", "agenda", "end") else "body"
    )
    resolved.tokens = dict(config.tokens)

    for override in config.slides:
        if override.match == slide_type:
            _apply_override(resolved, override)

    for override in config.slides:
        match_val = override.match
        if match_val.startswith("### ") and match_val[4:] == slide_title:
            _apply_override(resolved, override)
        elif match_val.startswith("## ") and match_val[3:] == slide_title:
            _apply_override(resolved, override)

    if "template" in slide_comment:
        resolved.template = slide_comment["template"]
    if "confidential" in slide_comment:
        resolved.badge_enabled = slide_comment["confidential"].lower() == "true"
    if "show_source" in slide_comment:
        resolved.show_source = slide_comment["show_source"].lower() == "true"
    if "compact" in slide_comment:
        resolved.compact = slide_comment["compact"].lower() == "true"
    if "ratio" in slide_comment:
        resolved.ratio = slide_comment["ratio"]

    return resolved


def _apply_override(resolved: ResolvedSlideConfig, override: SlideOverride):
    """Apply a SlideOverride onto a ResolvedSlideConfig."""
    if override.template:
        resolved.template = override.template
    if override.badge is not None:
        resolved.badge_enabled = override.badge
    if override.page_number is not None:
        resolved.page_number_enabled = override.page_number
    if override.accent_bar:
        resolved.accent_bar = override.accent_bar
    if override.show_source is not None:
        resolved.show_source = override.show_source
    if override.compact is not None:
        resolved.compact = override.compact
    if override.ratio:
        resolved.ratio = override.ratio
    if override.tokens:
        resolved.tokens.update(override.tokens)
