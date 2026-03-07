"""Data models for Markdown-to-Slide AST."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Inline:
    """Inline element within a block."""

    type: str  # "text" | "code" | "bold" | "link"
    text: str
    href: str = ""  # link only


@dataclass
class Block:
    """Block-level element within a slide."""

    type: str
    # "paragraph" | "ul" | "ol" | "checklist" | "table"
    # | "codeblock" | "callout" | "card" | "badge"
    # | "image" | "heading4"

    children: list = field(default_factory=list)
    # Inline[] for leaf blocks, Block[] for nested structures (e.g. list items)

    meta: dict = field(default_factory=dict)
    # type-specific metadata:
    #   codeblock:  {"lang": "python"}
    #   callout:    {"status": "warning"}
    #   card:       {"variant": "" | "accent"}
    #   badge:      {"text": "...", "status": "info"}
    #   table:      {"headers": [str, ...], "rows": [[str, ...], ...]}
    #   image:      {"src": "...", "alt": "...", "caption": "..."}
    #   ul/ol item: stored as child blocks with type "li"
    #   checklist:  children are "li" blocks with meta {"checked": bool}


@dataclass
class Slide:
    """A single slide."""

    type: str  # "cover" | "section" | "body"
    title: str
    subtitle: str = ""
    eyebrow: str = ""
    blocks: list[Block] = field(default_factory=list)
    source: str = ""  # footer source text
    comment: dict = field(default_factory=dict)
    # Parsed <!-- slide: ... --> attributes:
    #   {"template": "body-2col", "ratio": "6040", "compact": "true", ...}


@dataclass
class Deck:
    """The entire slide deck."""

    cover: Slide | None = None
    sections: list[tuple[Slide, list[Slide]]] = field(default_factory=list)
    # [(section_slide, [body_slide, ...]), ...]
