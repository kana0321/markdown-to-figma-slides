"""Render Deck AST to HTML files using Jinja2 templates."""

from __future__ import annotations

import hashlib
import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

try:
    from pygments import highlight as _pygments_highlight
    from pygments.formatters import HtmlFormatter as _HtmlFormatter
    from pygments.lexers import get_lexer_by_name as _get_lexer, guess_lexer as _guess_lexer
    _HAS_PYGMENTS = True
except ImportError:
    _HAS_PYGMENTS = False

from config import DesignConfig, ResolvedSlideConfig, resolve_slide
from models import Block, Deck, Inline, Slide

CAPTURE_SCRIPT = "https://mcp.figma.com/mcp/html-to-design/capture.js"


# ---------------------------------------------------------------------------
# Syntax highlighting
# ---------------------------------------------------------------------------

_PYGMENTS_FORMATTER = _HtmlFormatter(nowrap=True, noclasses=True, style="gruvbox-light") if _HAS_PYGMENTS else None


def _highlight_code(code: str, lang: str) -> str:
    """Syntax-highlight code using Pygments (inline styles). Falls back to escaped text."""
    if not _HAS_PYGMENTS:
        return html.escape(code, quote=True)
    try:
        if lang:
            lexer = _get_lexer(lang, stripall=True)
        else:
            lexer = _guess_lexer(code)
    except Exception:
        return html.escape(code, quote=True)
    return _pygments_highlight(code, lexer, _PYGMENTS_FORMATTER)


# ---------------------------------------------------------------------------
# Inline rendering
# ---------------------------------------------------------------------------


def inline_to_html(inlines: list[Inline]) -> str:
    """Render a list of Inline elements to an HTML string."""
    parts: list[str] = []
    for node in inlines:
        if node.type == "text":
            parts.append(html.escape(node.text, quote=True).replace("\n", "<br>"))
        elif node.type == "code":
            parts.append(
                f'<span class="inline-code">{html.escape(node.text, quote=True)}</span>'
            )
        elif node.type == "bold":
            parts.append(f"<strong>{html.escape(node.text, quote=True)}</strong>")
        elif node.type == "bold-link":
            href = html.escape(node.href, quote=True)
            text = html.escape(node.text, quote=True)
            parts.append(f'<strong><a class="link" href="{href}">{text}</a></strong>')
        elif node.type == "link":
            href = html.escape(node.href, quote=True)
            text = html.escape(node.text, quote=True)
            parts.append(f'<a class="link" href="{href}">{text}</a>')
    return "".join(parts)


# ---------------------------------------------------------------------------
# Block rendering
# ---------------------------------------------------------------------------


_UL_MARKERS = ["•", "◦", "–"]


def _render_list_items_nested(items: list[Block], list_tag: str = "ul") -> str:
    """Render list items with nesting support (up to 3 levels)."""
    if not items:
        return ""

    result: list[str] = []

    for item in items:
        depth = item.meta.get("depth", 0)
        inner = inline_to_html(item.children)
        indent_cls = f" ul-item--d{depth}" if depth > 0 else ""

        if item.meta.get("checked") is not None:
            checked_cls = " checklist-item--checked" if item.meta["checked"] else ""
            if item.meta["checked"]:
                box_html = '<div class="checklist-box checklist-box--checked"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13l4 4L19 7"/></svg></div>'
            else:
                box_html = '<div class="checklist-box"></div>'
            result.append(
                f'<div class="ul-item{indent_cls} checklist-item{checked_cls}">'
                f'{box_html}'
                f'<div class="ul-item__text type-body">{inner}</div>'
                f"</div>"
            )
        else:
            marker = _UL_MARKERS[min(depth, len(_UL_MARKERS) - 1)]
            result.append(
                f'<div class="ul-item{indent_cls}">'
                f'<div class="ul-item__marker type-body">{marker}</div>'
                f'<div class="ul-item__text type-body">{inner}</div>'
                f"</div>"
            )

    return "\n".join(result)



# ---------------------------------------------------------------------------
# Callout icons (inline SVG, no trademark / license issues)
# ---------------------------------------------------------------------------
_CALLOUT_ICONS = {
    "info": (
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/>'
        '<path d="M10 9v5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '<circle cx="10" cy="6.5" r="0.75" fill="currentColor"/>'
        '</svg>'
    ),
    "success": (
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/>'
        '<path d="M6.5 10.5l2.5 2.5 5-5.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        '</svg>'
    ),
    "warning": (
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<path d="M10 2L1 18h18L10 2z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'
        '<path d="M10 8v4.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '<circle cx="10" cy="15" r="0.75" fill="currentColor"/>'
        '</svg>'
    ),
    "danger": (
        '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">'
        '<circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="2"/>'
        '<path d="M7 7l6 6M13 7l-6 6" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
        '</svg>'
    ),
}


def _render_arrow_svg(direction: str, size: str, color: str) -> str:
    """Render an arrow as inline SVG (Figma-safe, no clip-path).

    Simple pointer shape: flat back edge, pointed tip.
    """
    # Dimensions from component tokens
    if size == "sm":
        w, h = 28, 48
    else:
        w, h = 48, 80

    # For vertical arrows, swap w/h
    if direction in ("up", "down"):
        w, h = h, w

    # Simple pointer shape (flat back, pointed tip)
    path_map = {
        "right": f"M0,0 L{w},{h/2:.0f} L0,{h} Z",
        "left":  f"M{w},0 L0,{h/2:.0f} L{w},{h} Z",
        "down":  f"M0,0 L{w/2:.0f},{h} L{w},0 Z",
        "up":    f"M0,{h} L{w/2:.0f},0 L{w},{h} Z",
    }
    path = path_map.get(direction, path_map["right"])
    color_cls = f"arrow--{color}"

    return (
        f'<svg class="arrow arrow--{direction} arrow--{size} {color_cls}"'
        f' width="{w}" height="{h}" viewBox="0 0 {w} {h}"'
        f' xmlns="http://www.w3.org/2000/svg">'
        f'<path d="{path}" fill="var(--component-arrow-color)"/>'
        f'</svg>'
    )


def _split_step_title_desc(inlines: list[Inline]) -> tuple[str, str]:
    """Split step li inlines into (title_html, description_html).

    If the first inline is bold, it becomes the title and the rest is description.
    Otherwise, everything is the title.
    """
    if not inlines:
        return "", ""
    if inlines[0].type == "bold":
        title = html.escape(inlines[0].text, quote=True)
        desc = inline_to_html(inlines[1:]).strip()
        if desc.startswith(" "):
            desc = desc.lstrip()
        return title, desc
    return inline_to_html(inlines), ""


def _render_steps(block: Block) -> str:
    """Render a steps block to HTML with inline SVG chevron backgrounds.

    Uses SVG instead of CSS clip-path for Figma compatibility.
    """
    meta = block.meta
    accent = meta.get("accent", "")  # "last" to accent the final item

    # Collect step items from children (look for ol blocks, or direct li items)
    items: list[Block] = []
    for child in block.children:
        if child.type == "ol":
            items.extend(child.children)
        elif child.type == "li":
            items.append(child)

    if not items:
        return ""

    parts: list[str] = []

    for idx, item in enumerate(items):
        title_html, desc_html = _split_step_title_desc(item.children)
        is_first = idx == 0
        is_last = idx == len(items) - 1
        accent_cls = " steps-item--accent" if (accent == "last" and is_last) else ""

        inner = f'<div class="steps-item__title type-body">{title_html}</div>'
        if desc_html:
            inner += f'<div class="steps-item__desc type-caption">{desc_html}</div>'

        # SVG chevron background — notch=20px mapped to viewBox percentage
        # Using a 200x100 viewBox with notch=10 units (20px / ~200px width)
        if is_first:
            # Flat left edge, pointed right
            svg_path = "M0,0 L190,0 L200,50 L190,100 L0,100 Z"
        else:
            # Notched left edge, pointed right
            svg_path = "M0,0 L190,0 L200,50 L190,100 L0,100 L10,50 Z"

        fill_var = "var(--component-steps-accent-bg)" if (accent == "last" and is_last) else "var(--component-steps-item-bg)"

        svg_bg = (
            f'<svg class="steps-item__bg" viewBox="0 0 200 100"'
            f' preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">'
            f'<path d="{svg_path}" fill="{fill_var}"/>'
            f'</svg>'
        )

        parts.append(
            f'<div class="steps-item{accent_cls}">'
            f'{svg_bg}'
            f'<div class="steps-item__content">{inner}</div>'
            f'</div>'
        )

    return f'<div class="steps">{"".join(parts)}</div>'


def block_to_html(block: Block) -> str:
    """Convert a Block AST node to an HTML string."""

    if block.type == "paragraph":
        inner = inline_to_html(block.children)
        return f'<div class="type-body w-content">{inner}</div>'

    if block.type == "heading4":
        inner = inline_to_html(block.children)
        return f'<div class="type-heading4">{inner}</div>'

    if block.type == "ul":
        items_html = _render_list_items_nested(block.children, "ul")
        return f'<div class="ul type-body">{items_html}</div>'

    if block.type == "ol":
        parts: list[str] = []
        for item in block.children:
            num = item.meta.get("number", 1)
            inner = inline_to_html(item.children)
            parts.append(
                f'<div class="ol-item">'
                f'<div class="ol-item__num type-body">{num}</div>'
                f'<div class="ol-item__text type-body">{inner}</div>'
                f"</div>"
            )
        return f'<div class="ol">{"".join(parts)}</div>'

    if block.type == "checklist":
        items_html = _render_list_items_nested(block.children, "ul")
        return f'<div class="ul type-body checklist">{items_html}</div>'

    if block.type == "table":
        headers = block.meta.get("headers", [])
        rows = block.meta.get("rows", [])
        thead = "".join(
            f"<th>{inline_to_html(_parse_cell(h))}</th>" for h in headers
        )
        tbody_rows: list[str] = []
        for row in rows:
            cells = "".join(
                f"<td>{inline_to_html(_parse_cell(c))}</td>" for c in row
            )
            tbody_rows.append(f"<tr>{cells}</tr>")
        return (
            f'<table class="data-table">'
            f"<thead><tr>{thead}</tr></thead>"
            f'<tbody>{"".join(tbody_rows)}</tbody>'
            f"</table>"
        )

    if block.type == "codeblock":
        lang = block.meta.get("lang", "")
        code = block.meta.get("code", "")
        lang_html = (
            f'<span class="codeblock__lang">{html.escape(lang, quote=True)}</span>'
            if lang
            else ""
        )
        code_html = _highlight_code(code, lang)
        return (
            f'<div class="codeblock">'
            f"{lang_html}"
            f'<pre class="type-code"><code>{code_html}</code></pre>'
            f"</div>"
        )

    if block.type == "callout":
        status = block.meta.get("status", "info")
        inner = inline_to_html(block.children)
        # Replace newlines with <br/> for multi-line callouts
        inner = inner.replace("\n", "<br/>")
        icon = _CALLOUT_ICONS.get(status, _CALLOUT_ICONS["info"])
        return (
            f'<div class="callout" data-status="{html.escape(status, quote=True)}">'
            f'<div class="callout__icon">{icon}</div>'
            f'<div class="type-body">{inner}</div>'
            f"</div>"
        )

    if block.type == "card":
        variant = block.meta.get("variant", "")
        eyebrow = block.meta.get("eyebrow", "")
        cls = "card card--accent" if variant == "accent" else "card"
        inner = "".join(block_to_html(child) for child in block.children)
        eyebrow_html = f'<div class="card__eyebrow type-eyebrow">{html.escape(eyebrow)}</div>' if eyebrow else ""
        return f'<div class="{cls}">{eyebrow_html}<div class="card__inner">{inner}</div></div>'

    if block.type == "badge":
        text = html.escape(block.meta.get("text", ""), quote=True)
        status = block.meta.get("status", "info")
        return f'<div class="block-badge block-badge--{html.escape(status, quote=True)}">{text}</div>'

    if block.type == "arrow":
        direction = block.meta.get("direction", "right")
        size = block.meta.get("size", "lg")
        color = block.meta.get("color", "secondary")
        return _render_arrow_svg(direction, size, color)

    if block.type == "steps":
        return _render_steps(block)

    if block.type == "image":
        src = html.escape(block.meta.get("src", ""), quote=True)
        alt = html.escape(block.meta.get("alt", ""), quote=True)
        caption = block.meta.get("caption", "")
        if caption:
            cap_html = html.escape(caption, quote=True)
            return (
                f'<figure class="image-block image-block--captioned">'
                f'<img src="{src}" alt="{alt}" />'
                f'<figcaption class="type-note">{cap_html}</figcaption>'
                f"</figure>"
            )
        return f'<div class="image-block"><img src="{src}" alt="{alt}" /></div>'

    return ""


def _parse_cell(text: str) -> list[Inline]:
    """Parse inline elements within a table cell."""
    from parser import parse_inline

    return parse_inline(text.strip())


def blocks_to_html(blocks: list[Block]) -> str:
    """Render a list of blocks to a single HTML string."""
    return "\n".join(block_to_html(b) for b in blocks)


# ---------------------------------------------------------------------------
# Column splitting (for 2col / 3col templates)
# ---------------------------------------------------------------------------

_COL_LABELS_2 = {"left", "right"}
_COL_LABELS_3 = {"col1", "col2", "col3"}


def _split_columns(
    blocks: list[Block], labels: set[str]
) -> dict[str, list[Block]]:
    """Split blocks by #### heading labels into columns."""
    columns: dict[str, list[Block]] = {label: [] for label in labels}
    current_col: str = ""
    sorted_labels = sorted(labels)

    for block in blocks:
        if block.type == "heading4":
            label_text = inline_to_html(block.children).strip().lower()
            if label_text in labels:
                current_col = label_text
                continue
        if current_col:
            columns[current_col].append(block)
        else:
            # No column label yet, put in first column
            if sorted_labels:
                columns[sorted_labels[0]].append(block)

    return columns


# ---------------------------------------------------------------------------
# Hero image extraction
# ---------------------------------------------------------------------------


def _extract_hero_image(blocks: list[Block]) -> tuple[list[Block], str, str]:
    """Extract the first image block for hero template. Returns (remaining_blocks, src, alt)."""
    remaining: list[Block] = []
    hero_src = ""
    hero_alt = ""
    found = False

    for block in blocks:
        if not found and block.type == "image":
            hero_src = block.meta.get("src", "")
            hero_alt = block.meta.get("alt", "")
            found = True
        else:
            remaining.append(block)

    return remaining, hero_src, hero_alt


# ---------------------------------------------------------------------------
# Deck rendering
# ---------------------------------------------------------------------------


def render_deck(
    deck: Deck,
    config: DesignConfig,
    templates_dir: Path,
    output_dir: Path,
    version: str,
    source_path: Path,
) -> None:
    """Render the full deck to HTML files."""
    # Set up Jinja2
    loader = FileSystemLoader(
        [str(templates_dir), str(templates_dir / "custom")]
    )
    env = Environment(loader=loader, autoescape=False)

    version_dir = output_dir / version
    pages_dir = version_dir / "slides" / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows: list[dict] = []
    deck_html_parts: list[str] = []
    idx = 1
    page = config.page_number.start

    # --- Cover ---
    if deck.cover:
        cover_html, cover_body = _render_slide(
            env, deck.cover, "cover", config, page, "../../styles"
        )
        _write_page(pages_dir, idx, "cover", cover_html)
        manifest_rows.append(_manifest_row(idx, page, f"{idx:02d}-cover.html", "cover", deck.cover.title))
        deck_html_parts.append(cover_body)
        idx += 1
        page += 1

    # --- Agenda ---
    if config.agenda.enabled and deck.sections:
        agenda_page = page
        resolved = resolve_slide("agenda", "", {}, config)

        # Compute section pages for agenda
        section_entries = []
        temp_page = page + 1  # after agenda itself
        for sec_slide, body_slides in deck.sections:
            section_entries.append({"title": sec_slide.title, "page": temp_page})
            temp_page += 1 + len(body_slides)  # section + bodies

        template = env.get_template("agenda.html.j2")
        agenda_vars = _base_vars(resolved, config, agenda_page, "../../styles")
        agenda_vars.update(
            slide_class="slide--body",
            page_title="Agenda",
            eyebrow=config.agenda.eyebrow,
            agenda_title=config.agenda.title,
            sections=section_entries,
            show_pages=config.agenda.show_pages,
            compact=resolved.compact,
        )
        full_html = template.render(**agenda_vars)
        body_html = _render_slide_div(template, agenda_vars)

        _write_page(pages_dir, idx, "agenda", full_html)
        manifest_rows.append(_manifest_row(idx, page, f"{idx:02d}-agenda.html", "agenda", "Agenda"))
        deck_html_parts.append(body_html)
        idx += 1
        page += 1

    # --- Sections + Bodies ---
    for sec_slide, body_slides in deck.sections:
        # Section slide
        sec_html, sec_body = _render_slide(
            env, sec_slide, "section", config, page, "../../styles"
        )
        _write_page(pages_dir, idx, "section", sec_html)
        manifest_rows.append(_manifest_row(idx, page, f"{idx:02d}-section.html", "section", sec_slide.title))
        deck_html_parts.append(sec_body)
        idx += 1
        page += 1

        # Body slides
        for body_slide in body_slides:
            body_html_full, body_body = _render_slide(
                env, body_slide, "body", config, page, "../../styles"
            )
            _write_page(pages_dir, idx, "body", body_html_full)
            manifest_rows.append(_manifest_row(idx, page, f"{idx:02d}-body.html", "body", body_slide.title))
            deck_html_parts.append(body_body)
            idx += 1
            page += 1

    # --- All-in-one slides.html ---
    all_in_one = _build_all_in_one(
        deck_html_parts, config.global_.lang, "../styles"
    )
    slides_dir = version_dir / "slides"
    (slides_dir / "slides.html").write_text(all_in_one, encoding="utf-8")

    # --- SLIDES.md ---
    _write_slides_md(version_dir, manifest_rows, source_path)

    # --- manifest.json ---
    _write_manifest(version_dir, version, source_path, manifest_rows, slides_dir)

    # --- Copy styles ---
    styles_src = templates_dir.parent / "styles"
    styles_dst = version_dir / "styles"
    if styles_src.is_dir():
        if styles_dst.exists():
            shutil.rmtree(styles_dst)
        shutil.copytree(styles_src, styles_dst)

    # --- Redirect entry ---
    _write_redirect(output_dir, version)

    print(f"generated: {version_dir} ({len(manifest_rows)} slides)")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _render_slide(
    env: Environment,
    slide: Slide,
    slide_type: str,
    config: DesignConfig,
    page: int,
    css_base: str,
) -> tuple[str, str]:
    """Render a single slide. Returns (full HTML, body-only HTML for deck)."""
    resolved = resolve_slide(slide_type, slide.title, slide.comment, config)
    template_name = resolved.template + ".html.j2"

    try:
        template = env.get_template(template_name)
    except Exception:
        template = env.get_template("body.html.j2")
        resolved.template = "body"

    slide_class_map = {
        "cover": "slide--cover",
        "section": "slide--section slide--section",
        "body-hero": "slide--body slide--fullimage",
    }
    slide_class = slide_class_map.get(
        resolved.template, "slide--body"
    )

    variables = _base_vars(resolved, config, page, css_base)
    variables.update(
        slide_class=slide_class,
        page_title=slide.title,
        title=slide.title,
        subtitle=slide.subtitle,
        eyebrow=slide.eyebrow,
        source=slide.source,
        show_source=bool(slide.source) or resolved.show_source,
        compact=resolved.compact,
    )

    # Template-specific content
    if resolved.template in ("body-2col",):
        columns = _split_columns(slide.blocks, _COL_LABELS_2)
        # Extract source from column tails when slide-level source is empty
        if not slide.source:
            from parser import _extract_source
            for col_key in ("right", "left"):
                col_blocks = columns.get(col_key, [])
                col_blocks, col_source = _extract_source(col_blocks)
                if col_source:
                    columns[col_key] = col_blocks
                    variables["source"] = col_source
                    variables["show_source"] = True
                    break
        variables["left"] = blocks_to_html(columns.get("left", []))
        variables["right"] = blocks_to_html(columns.get("right", []))
        variables["ratio"] = resolved.ratio
    elif resolved.template in ("body-3col",):
        columns = _split_columns(slide.blocks, _COL_LABELS_3)
        # Extract source from column tails when slide-level source is empty
        if not slide.source:
            from parser import _extract_source
            for col_key in ("col3", "col2", "col1"):
                col_blocks = columns.get(col_key, [])
                col_blocks, col_source = _extract_source(col_blocks)
                if col_source:
                    columns[col_key] = col_blocks
                    variables["source"] = col_source
                    variables["show_source"] = True
                    break
        variables["col1"] = blocks_to_html(columns.get("col1", []))
        variables["col2"] = blocks_to_html(columns.get("col2", []))
        variables["col3"] = blocks_to_html(columns.get("col3", []))
    elif resolved.template == "body-hero":
        remaining, hero_src, hero_alt = _extract_hero_image(slide.blocks)
        variables["hero_src"] = hero_src
        variables["hero_alt"] = hero_alt
        variables["content"] = blocks_to_html(remaining)
        variables["content"] = variables["content"].replace(
            'class="type-body ', 'class="type-hero '
        ).replace(
            'class="type-body"', 'class="type-hero"'
        )
    else:
        variables["content"] = blocks_to_html(slide.blocks)

    # body-text: upgrade type-body to type-body-spacious for readability
    if resolved.template == "body-text" and "content" in variables:
        variables["content"] = variables["content"].replace(
            'class="type-body ', 'class="type-body-spacious '
        ).replace(
            'class="type-body"', 'class="type-body-spacious"'
        )

    full_html = template.render(**variables)

    # For deck: render body-only (re-render with deck css path)
    deck_vars = dict(variables)
    deck_vars["css_base"] = "../styles"
    body_html = _render_slide_div(template, deck_vars)

    return full_html, body_html


def _base_vars(
    resolved: ResolvedSlideConfig,
    config: DesignConfig,
    page: int,
    css_base: str,
) -> dict:
    """Build the base template variables common to all slides."""
    return {
        "lang": config.global_.lang,
        "css_base": css_base,
        "badge_enabled": resolved.badge_enabled,
        "badge_text": resolved.badge_text,
        "accent_bar": resolved.accent_bar,
        "page_number_enabled": resolved.page_number_enabled,
        "page": page,
    }


def _render_slide_div(template, variables: dict) -> str:
    """Render only the slide div (for all-in-one embedding)."""
    full = template.render(**variables)
    # Extract the <div class="slide ...">...</div> portion
    start = full.find('<div class="slide')
    if start == -1:
        return full
    # Find matching closing </div> by counting depth
    depth = 0
    i = start
    while i < len(full):
        if full[i:].startswith("<div"):
            depth += 1
            i += 4
        elif full[i:].startswith("</div>"):
            depth -= 1
            if depth == 0:
                return full[start : i + 6]
            i += 6
        else:
            i += 1
    return full[start:]


def _write_page(pages_dir: Path, idx: int, kind: str, content: str) -> None:
    """Write a single page HTML file."""
    (pages_dir / f"{idx:02d}-{kind}.html").write_text(content, encoding="utf-8")


def _manifest_row(idx: int, page: int, filename: str, kind: str, title: str) -> dict:
    return {"idx": idx, "page": page, "file": filename, "type": kind, "title": title}


def _build_all_in_one(slide_parts: list[str], lang: str, css_base: str) -> str:
    """Build the all-in-one slides.html."""
    items = "\n".join(f'<div class="deck-item">{part}</div>' for part in slide_parts)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{css_base}/tokens.primitives.css" />
  <link rel="stylesheet" href="{css_base}/tokens.semantic.css" />
  <link rel="stylesheet" href="{css_base}/tokens.component.css" />
  <link rel="stylesheet" href="{css_base}/slide.css" />
  <title>All Slides</title>
</head>
<body>
<div class="deck" style="display:flex;flex-direction:column;gap:32px;align-items:center;">
{items}
</div>
<script src="{CAPTURE_SCRIPT}" async></script>
</body>
</html>
"""


def _write_slides_md(version_dir: Path, rows: list[dict], source_path: Path) -> None:
    lines = [
        "# Slides",
        "",
        f"- source: `{source_path}`",
        f"- generated files: `{len(rows)}`",
        "",
        "| No | Page | File | Type | Title |",
        "| --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        lines.append(f"| {r['idx']} | {r['page']} | `{r['file']}` | {r['type']} | {r['title']} |")
    (version_dir / "SLIDES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_manifest(
    version_dir: Path,
    version: str,
    source_path: Path,
    rows: list[dict],
    slides_dir: Path,
) -> None:
    manifest = {
        "version": version,
        "source_path": str(source_path),
        "source_sha256": hashlib.sha256(source_path.read_bytes()).hexdigest(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pages": len(rows),
        "capture_entry": str((slides_dir / "slides.html").resolve()),
    }
    (version_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def _write_redirect(output_dir: Path, version: str) -> None:
    (output_dir / "latest.txt").write_text(version + "\n", encoding="utf-8")
    redirect = f"""<!doctype html>
<html lang="ja">
<head><meta charset="utf-8" /><title>slides redirect</title></head>
<body>
<script>
  var target = "./{version}/slides/slides.html" + window.location.hash;
  window.location.replace(target);
</script>
</body>
</html>
"""
    (output_dir / "slides.html").write_text(redirect, encoding="utf-8")
