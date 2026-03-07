"""Load and resolve design.config.yaml with defaults."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Config data structures
# ---------------------------------------------------------------------------


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


@dataclass
class BadgeConfig:
    enabled: bool = True
    text: str = "Confidential"
    defaults: TypeDefaults = field(default_factory=TypeDefaults)


@dataclass
class PageNumberConfig:
    enabled: bool = True
    start: int = 1
    defaults: TypeDefaults = field(
        default_factory=lambda: TypeDefaults(cover=False, section=False)
    )


@dataclass
class AccentBarDefaults:
    cover: str = "left"
    section: str = "none"
    agenda: str = "top"
    body: str = "top"


@dataclass
class AccentBarConfig:
    defaults: AccentBarDefaults = field(default_factory=AccentBarDefaults)


@dataclass
class AgendaConfig:
    enabled: bool = True
    title: str = "Agenda"
    eyebrow: str = "Agenda"
    show_pages: bool = False


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
    global_: GlobalConfig = field(default_factory=GlobalConfig)
    badge: BadgeConfig = field(default_factory=BadgeConfig)
    page_number: PageNumberConfig = field(default_factory=PageNumberConfig)
    accent_bar: AccentBarConfig = field(default_factory=AccentBarConfig)
    agenda: AgendaConfig = field(default_factory=AgendaConfig)
    tokens: dict[str, str] = field(default_factory=dict)
    slides: list[SlideOverride] = field(default_factory=list)


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
            # Try with underscore suffix (e.g. global -> global_)
            attr_name = key + "_"
            if not hasattr(target, attr_name):
                continue
        current = getattr(target, attr_name)
        if isinstance(val, dict) and hasattr(current, "__dataclass_fields__"):
            _merge_dataclass(current, val)
        else:
            setattr(target, attr_name, val)


def load_config(path: Path) -> DesignConfig:
    """Load design.config.yaml and return a DesignConfig with defaults filled in."""
    config = DesignConfig()

    if not path.exists():
        return config

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return config

    # Global
    if "global" in raw:
        _merge_dataclass(config.global_, raw["global"])

    # Badge
    if "badge" in raw:
        _merge_dataclass(config.badge, raw["badge"])

    # Page number
    if "page_number" in raw:
        _merge_dataclass(config.page_number, raw["page_number"])

    # Accent bar
    if "accent_bar" in raw:
        _merge_dataclass(config.accent_bar, raw["accent_bar"])

    # Agenda
    if "agenda" in raw:
        _merge_dataclass(config.agenda, raw["agenda"])

    # Tokens
    if "tokens" in raw and isinstance(raw["tokens"], dict):
        config.tokens = {str(k): str(v) for k, v in raw["tokens"].items()}

    # Slides
    if "slides" in raw and isinstance(raw["slides"], list):
        for entry in raw["slides"]:
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
            config.slides.append(override)

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
    """Resolve the final configuration for a slide by merging defaults, config overrides, and markdown comments."""
    resolved = ResolvedSlideConfig()

    # --- Layer 1: Defaults from config ---
    # Badge
    type_badge_default = getattr(config.badge.defaults, slide_type, True)
    resolved.badge_enabled = config.badge.enabled and type_badge_default
    resolved.badge_text = config.badge.text

    # Page number
    type_page_default = getattr(config.page_number.defaults, slide_type, True)
    resolved.page_number_enabled = config.page_number.enabled and type_page_default

    # Accent bar
    resolved.accent_bar = getattr(config.accent_bar.defaults, slide_type, "top")

    # Template default
    resolved.template = slide_type if slide_type in ("cover", "section", "agenda") else "body"

    # Global tokens
    resolved.tokens = dict(config.tokens)

    # --- Layer 2: Config slide overrides ---
    # First pass: type-level matches
    for override in config.slides:
        if override.match == slide_type:
            _apply_override(resolved, override)

    # Second pass: title-level matches (more specific, higher priority)
    for override in config.slides:
        match_val = override.match
        if match_val.startswith("### ") and match_val[4:] == slide_title:
            _apply_override(resolved, override)
        elif match_val.startswith("## ") and match_val[3:] == slide_title:
            _apply_override(resolved, override)

    # --- Layer 3: Markdown comment (highest priority) ---
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
