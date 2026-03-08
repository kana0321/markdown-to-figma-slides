"""Markdown parser that produces a Deck AST."""

from __future__ import annotations

import re
from models import Block, Deck, Inline, Slide

# ---------------------------------------------------------------------------
# Inline parsing
# ---------------------------------------------------------------------------

_INLINE_PATTERNS = [
    # order matters: code first, then bold-link combo, then individual
    ("code", re.compile(r"`([^`]+)`")),
    ("bold-link", re.compile(r"\*\*\[([^\]]+)\]\(([^)]+)\)\*\*")),
    ("link", re.compile(r"\[([^\]]+)\]\(([^)]+)\)")),
    ("bold", re.compile(r"\*\*([^*]+)\*\*")),
]


def parse_inline(text: str) -> list[Inline]:
    """Parse inline elements from a text string."""
    result: list[Inline] = []
    while text:
        earliest_match = None
        earliest_pos = len(text)
        earliest_kind = ""

        for kind, pat in _INLINE_PATTERNS:
            m = pat.search(text)
            if m and m.start() < earliest_pos:
                earliest_match = m
                earliest_pos = m.start()
                earliest_kind = kind

        if earliest_match is None:
            result.append(Inline(type="text", text=text))
            break

        if earliest_pos > 0:
            result.append(Inline(type="text", text=text[:earliest_pos]))

        if earliest_kind == "code":
            result.append(Inline(type="code", text=earliest_match.group(1)))
        elif earliest_kind == "bold-link":
            result.append(
                Inline(
                    type="bold-link",
                    text=earliest_match.group(1),
                    href=earliest_match.group(2),
                )
            )
        elif earliest_kind == "bold":
            result.append(Inline(type="bold", text=earliest_match.group(1)))
        elif earliest_kind == "link":
            result.append(
                Inline(
                    type="link",
                    text=earliest_match.group(1),
                    href=earliest_match.group(2),
                )
            )

        text = text[earliest_match.end() :]

    return result


# ---------------------------------------------------------------------------
# Slide comment parsing
# ---------------------------------------------------------------------------

_COMMENT_RE = re.compile(r"<!--\s*slide:\s*(.*?)\s*-->")
_VALID_KEYS = {
    "template",
    "confidential",
    "show_source",
    "eyebrow",
    "subtitle",
    "ratio",
    "compact",
}

_GRID_OPEN_RE = re.compile(r"<!--\s*grid\s*:\s*(.*?)\s*-->")
_GRID_CLOSE_RE = re.compile(r"<!--\s*/grid\s*-->", re.IGNORECASE)
_CELL_OPEN_RE = re.compile(r"<!--\s*cell\s*:\s*(.*?)\s*-->")
_CELL_CLOSE_RE = re.compile(r"<!--\s*/cell\s*-->", re.IGNORECASE)

_GRID_ALLOWED_KEYS = {"columns", "rows", "gap", "col_gap", "row_gap"}
_GRID_REQUIRED_KEYS = {"columns", "rows"}
_GRID_GAP_VALUES = {"sm", "md", "lg"}
_CELL_ALLOWED_KEYS = {"col", "row", "col_span", "row_span"}
_CELL_REQUIRED_KEYS = {"col", "row"}
_LEGACY_COL_LABELS_2 = ("left", "right")
_LEGACY_COL_LABELS_3 = ("col1", "col2", "col3")


class MarkdownParseError(ValueError):
    """Raised when markdown violates slide grammar."""


def _slide_name(slide_title: str) -> str:
    return slide_title or "(untitled)"


def _raise_parse_error(message: str, slide_title: str) -> None:
    raise MarkdownParseError(f"{message} on slide '{_slide_name(slide_title)}'")


def parse_slide_comment(line: str) -> dict | None:
    """Parse a <!-- slide: key=value; ... --> comment. Returns None if not a slide comment."""
    m = _COMMENT_RE.match(line.strip())
    if not m:
        return None
    result = {}
    for part in m.group(1).split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            key, val = part.split("=", 1)
            key = key.strip().lower()
            val = val.strip()
            if key in _VALID_KEYS:
                result[key] = val
        # ignore parts without =
    return result


def _parse_strict_comment_attrs(
    raw: str,
    *,
    allowed_keys: set[str],
    required_keys: set[str],
    kind: str,
    slide_title: str,
) -> dict[str, str]:
    """Parse 'key=value; key2=value2' and reject unknown / duplicate keys."""
    result: dict[str, str] = {}
    seen: set[str] = set()

    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            _raise_parse_error(
                f"{kind} attributes must use key=value syntax",
                slide_title,
            )
        key, value = part.split("=", 1)
        key = key.strip().lower()
        value = value.strip()
        if key in seen:
            _raise_parse_error(f"duplicate {kind} attribute '{key}'", slide_title)
        if key not in allowed_keys:
            _raise_parse_error(f"unknown {kind} attribute '{key}'", slide_title)
        seen.add(key)
        result[key] = value

    missing = [key for key in sorted(required_keys) if key not in result]
    if missing:
        missing_list = ", ".join(missing)
        _raise_parse_error(
            f"{kind} is missing required attribute(s): {missing_list}",
            slide_title,
        )

    return result


def _parse_positive_int(
    value: str,
    *,
    attr_name: str,
    kind: str,
    slide_title: str,
    min_value: int = 1,
    max_value: int | None = None,
) -> int:
    try:
        parsed = int(value)
    except ValueError:
        parsed = -1

    if parsed < min_value or (max_value is not None and parsed > max_value):
        if max_value is None:
            _raise_parse_error(
                f"{kind} attribute '{attr_name}' must be a positive integer",
                slide_title,
            )
        _raise_parse_error(
            f"{kind} attribute '{attr_name}' must be an integer between {min_value} and {max_value}",
            slide_title,
        )
    return parsed


# ---------------------------------------------------------------------------
# Card / Badge comment parsing
# ---------------------------------------------------------------------------

_CARD_COMMENT_RE = re.compile(
    r"<!--\s*card\s*(?::\s*(accent))?\s*(?:;\s*eyebrow=([^>]*?))?\s*-->", re.IGNORECASE
)
_CARD_CLOSE_RE = re.compile(r"<!--\s*/card\s*-->", re.IGNORECASE)
_BADGE_COMMENT_RE = re.compile(
    r"<!--\s*badge:\s*([^;>]+?)(?:;\s*status=(\w+))?\s*-->", re.IGNORECASE
)
_ARROW_COMMENT_RE = re.compile(
    r"<!--\s*arrow:\s*(right|left|up|down)"
    r"(?:\s*;\s*size=(lg|sm))?(?:\s*;\s*color=(secondary|accent-subtle))?\s*-->",
    re.IGNORECASE,
)
_STEPS_COMMENT_RE = re.compile(
    r"<!--\s*steps\s*(?::\s*([^>]*?))?\s*-->", re.IGNORECASE
)
_STEPS_CLOSE_RE = re.compile(r"<!--\s*/steps\s*-->", re.IGNORECASE)


def _parse_kv_params(raw: str) -> dict:
    """Parse 'key=value; key2=value2' into a dict."""
    params: dict[str, str] = {}
    if not raw:
        return params
    for part in raw.split(";"):
        part = part.strip()
        if "=" in part:
            key, val = part.split("=", 1)
            params[key.strip().lower()] = val.strip()
    return params


# ---------------------------------------------------------------------------
# Block parsing
# ---------------------------------------------------------------------------

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_UL_RE = re.compile(r"^(\s*)([-*])\s+(.*)$")
_OL_RE = re.compile(r"^(\s*)(\d+)\.\s+(.*)$")
_CHECKBOX_RE = re.compile(r"^(\s*)[-*]\s+\[([ xX])\]\s+(.*)$")
_FENCE_RE = re.compile(r"^```(\w*)$")
_TABLE_SEP_RE = re.compile(r"^\|[\s\-:|]+\|$")
_IMAGE_RE = re.compile(r'^!\[([^\]]*)\]\(([^)"]+)(?:\s+"([^"]*)")?\)$')
_CALLOUT_START_RE = re.compile(r"^>\s*\[!(\w+)\]")
_CALLOUT_LINE_RE = re.compile(r"^>\s?(.*)$")
_SOURCE_RE = re.compile(r"^(?:Source|source):\s*(.+)$")


def _indent_level(indent: str) -> int:
    """Convert indentation string to nesting depth (0-based, 2-space increments)."""
    spaces = len(indent.replace("\t", "    "))
    return min(spaces // 2, 2)  # max depth 2 (3 levels: 0, 1, 2)


def _parse_list_items(
    lines: list[str], start: int, list_type: str
) -> tuple[list[Block], int]:
    """Parse list items (ul, ol, checklist) with nesting up to 3 levels.

    Returns (list of li blocks, next line index).
    """
    items: list[Block] = []
    i = start

    if list_type == "checklist":
        item_re = _CHECKBOX_RE
    elif list_type == "ol":
        item_re = _OL_RE
    else:
        item_re = _UL_RE

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Check if line is a checklist item
        cm = _CHECKBOX_RE.match(line)
        if cm and list_type == "checklist":
            indent = _indent_level(cm.group(1))
            checked = cm.group(2).lower() == "x"
            text = cm.group(3)
            items.append(
                Block(
                    type="li",
                    children=parse_inline(text),
                    meta={"checked": checked, "depth": indent},
                )
            )
            i += 1
            continue

        # Check if line is a UL item
        um = _UL_RE.match(line)
        if um and list_type == "ul":
            # But first check it's not a checkbox
            if _CHECKBOX_RE.match(line):
                break
            indent = _indent_level(um.group(1))
            text = um.group(3)
            items.append(
                Block(
                    type="li",
                    children=parse_inline(text),
                    meta={"depth": indent},
                )
            )
            i += 1
            continue

        # Check if line is an OL item
        om = _OL_RE.match(line)
        if om and list_type == "ol":
            indent = _indent_level(om.group(1))
            text = om.group(3)
            items.append(
                Block(
                    type="li",
                    children=parse_inline(text),
                    meta={"number": int(om.group(2)), "depth": indent},
                )
            )
            i += 1
            continue

        # Not a matching list item, stop
        break

    return items, i


def _parse_table(lines: list[str], start: int) -> tuple[Block, int]:
    """Parse a markdown table starting at `start`. Returns (Block, next line index)."""
    headers: list[str] = []
    rows: list[list[str]] = []
    i = start

    # Header row
    header_line = lines[i].strip()
    headers = [c.strip() for c in header_line.strip("|").split("|")]
    i += 1

    # Separator row
    if i < len(lines) and _TABLE_SEP_RE.match(lines[i].strip()):
        i += 1

    # Data rows
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
        i += 1

    return Block(type="table", meta={"headers": headers, "rows": rows}), i


def _parse_callout(lines: list[str], start: int) -> tuple[Block, int]:
    """Parse a callout block. Returns (Block, next line index)."""
    first = lines[start]
    m = _CALLOUT_START_RE.match(first)
    raw_type = m.group(1).upper() if m else "NOTE"

    status_map = {"NOTE": "info", "TIP": "success", "WARNING": "warning", "CAUTION": "danger"}
    status = status_map.get(raw_type, "info")

    content_lines: list[str] = []
    i = start + 1

    while i < len(lines):
        cm = _CALLOUT_LINE_RE.match(lines[i])
        if cm:
            content_lines.append(cm.group(1))
            i += 1
        else:
            break

    text = "\n".join(content_lines).strip()
    return Block(type="callout", children=parse_inline(text), meta={"status": status}), i


def _parse_codeblock(lines: list[str], start: int) -> tuple[Block, int]:
    """Parse a fenced code block. Returns (Block, next line index)."""
    m = _FENCE_RE.match(lines[start].strip())
    lang = m.group(1) if m else ""
    code_lines: list[str] = []
    i = start + 1

    while i < len(lines):
        if lines[i].strip() == "```":
            i += 1
            break
        code_lines.append(lines[i])
        i += 1

    return Block(type="codeblock", meta={"lang": lang, "code": "\n".join(code_lines)}), i


def parse_blocks(lines: list[str]) -> list[Block]:
    """Parse a list of content lines into Block elements."""
    blocks: list[Block] = []
    i = 0
    pending_card: str | None = None  # None or "" or "accent"
    pending_card_eyebrow: str = ""
    card_collecting: bool = False  # True when inside <!-- card --> ... <!-- /card -->
    card_children: list[Block] = []
    steps_collecting: bool = False  # True when inside <!-- steps --> ... <!-- /steps -->
    steps_children: list[Block] = []
    steps_meta: dict = {}

    def _wrap_single_block_if_pending(block: Block) -> Block:
        """Wrap a single block in a card if pending_card is set (legacy single-block mode)."""
        nonlocal pending_card, pending_card_eyebrow
        if pending_card is not None and not card_collecting:
            block = Block(
                type="card",
                children=[block],
                meta={"variant": pending_card or "", "eyebrow": pending_card_eyebrow},
            )
            pending_card = None
            pending_card_eyebrow = ""
        return block

    def _append_block(block: Block) -> None:
        """Append block to card_children if collecting, steps_children if steps collecting, otherwise to blocks."""
        if card_collecting:
            card_children.append(block)
        elif steps_collecting:
            steps_children.append(block)
        else:
            blocks.append(block)

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            i += 1
            continue

        # Card close comment
        if _CARD_CLOSE_RE.match(stripped):
            if card_collecting:
                card_block = Block(
                    type="card",
                    children=list(card_children),
                    meta={"variant": pending_card or "", "eyebrow": pending_card_eyebrow},
                )
                card_children.clear()
                card_collecting = False
                pending_card = None
                pending_card_eyebrow = ""
                if steps_collecting:
                    steps_children.append(card_block)
                else:
                    blocks.append(card_block)
            i += 1
            continue

        # Card open comment
        cm = _CARD_COMMENT_RE.match(stripped)
        if cm:
            pending_card = cm.group(1) or ""
            pending_card_eyebrow = (cm.group(2) or "").strip()
            # Look ahead: if <!-- /card --> exists later, enter collecting mode
            for j in range(i + 1, len(lines)):
                if _CARD_CLOSE_RE.match(lines[j].strip()):
                    card_collecting = True
                    break
                # Stop looking at slide/section boundaries
                if lines[j].strip() == "---":
                    break
            i += 1
            continue

        # Badge comment
        bm = _BADGE_COMMENT_RE.match(stripped)
        if bm:
            badge_text = bm.group(1).strip()
            badge_status = (bm.group(2) or "info").lower()
            if badge_status not in ("info", "success", "warning", "danger"):
                badge_status = "info"
            _append_block(
                Block(type="badge", meta={"text": badge_text, "status": badge_status})
            )
            i += 1
            continue

        # Arrow comment
        am = _ARROW_COMMENT_RE.match(stripped)
        if am:
            _append_block(
                Block(
                    type="arrow",
                    meta={
                        "direction": am.group(1).lower(),
                        "size": (am.group(2) or "lg").lower(),
                        "color": (am.group(3) or "secondary").lower(),
                    },
                )
            )
            i += 1
            continue

        # Steps close comment
        if _STEPS_CLOSE_RE.match(stripped):
            if steps_collecting:
                blocks.append(Block(
                    type="steps",
                    children=list(steps_children),
                    meta=dict(steps_meta),
                ))
                steps_children.clear()
                steps_collecting = False
                steps_meta = {}
            i += 1
            continue

        # Steps open comment
        sm = _STEPS_COMMENT_RE.match(stripped)
        if sm:
            raw_params = sm.group(1) or ""
            steps_meta = _parse_kv_params(raw_params)
            steps_collecting = True
            i += 1
            continue

        # Slide comment (skip, already parsed at slide level)
        if _COMMENT_RE.match(stripped):
            i += 1
            continue

        # Other HTML comments (skip)
        if stripped.startswith("<!--"):
            i += 1
            continue

        # Fenced code block
        if _FENCE_RE.match(stripped):
            block, i = _parse_codeblock(lines, i)
            block = _wrap_single_block_if_pending(block)
            _append_block(block)
            continue

        # Callout
        if _CALLOUT_START_RE.match(stripped):
            block, i = _parse_callout(lines, i)
            _append_block(block)
            continue

        # Table
        if stripped.startswith("|"):
            # Look ahead for separator
            if i + 1 < len(lines) and _TABLE_SEP_RE.match(lines[i + 1].strip()):
                block, i = _parse_table(lines, i)
                _append_block(block)
                continue

        # Image
        im = _IMAGE_RE.match(stripped)
        if im:
            _append_block(
                Block(
                    type="image",
                    meta={
                        "alt": im.group(1),
                        "src": im.group(2),
                        "caption": im.group(3) or "",
                    },
                )
            )
            i += 1
            continue

        # Checkbox list
        if _CHECKBOX_RE.match(line):
            items, i = _parse_list_items(lines, i, "checklist")
            _append_block(Block(type="checklist", children=items))
            continue

        # Unordered list
        if _UL_RE.match(line) and not _CHECKBOX_RE.match(line):
            items, i = _parse_list_items(lines, i, "ul")
            block = Block(type="ul", children=items)
            block = _wrap_single_block_if_pending(block)
            _append_block(block)
            continue

        # Ordered list
        if _OL_RE.match(line):
            items, i = _parse_list_items(lines, i, "ol")
            block = Block(type="ol", children=items)
            block = _wrap_single_block_if_pending(block)
            _append_block(block)
            continue

        # Heading 4
        hm = _HEADING_RE.match(stripped)
        if hm and len(hm.group(1)) == 4:
            _append_block(
                Block(type="heading4", children=parse_inline(hm.group(2).strip()))
            )
            i += 1
            continue

        # Paragraph (default)
        para_lines: list[str] = []
        while i < len(lines):
            s = lines[i].strip()
            if not s:
                i += 1
                break
            # Stop at block-level elements
            if (
                _FENCE_RE.match(s)
                or _CALLOUT_START_RE.match(s)
                or (s.startswith("|") and i + 1 < len(lines) and _TABLE_SEP_RE.match(lines[i + 1].strip()))
                or _IMAGE_RE.match(s)
                or _UL_RE.match(lines[i])
                or _OL_RE.match(lines[i])
                or _CHECKBOX_RE.match(lines[i])
                or _HEADING_RE.match(s)
                or _COMMENT_RE.match(s)
                or _CARD_COMMENT_RE.match(s)
                or _CARD_CLOSE_RE.match(s)
                or _BADGE_COMMENT_RE.match(s)
                or _ARROW_COMMENT_RE.match(s)
                or _STEPS_COMMENT_RE.match(s)
                or _STEPS_CLOSE_RE.match(s)
                or s.startswith("<!--")
            ):
                break
            if lines[i].rstrip("\n").endswith("  "):
                para_lines.append(s + "\u000A")
            else:
                para_lines.append(s)
            i += 1

        if para_lines:
            text = " ".join(para_lines)
            block = Block(type="paragraph", children=parse_inline(text))
            block = _wrap_single_block_if_pending(block)
            _append_block(block)

    return blocks


def _build_grid_block(
    *,
    columns: list[str],
    rows: list[str],
    col_gap: str,
    row_gap: str,
    source_kind: str,
    declared_columns: int,
    declared_rows: int,
    children: list[Block],
) -> Block:
    return Block(
        type="grid",
        meta={
            "columns": columns,
            "rows": rows,
            "col_gap": col_gap,
            "row_gap": row_gap,
            "source_kind": source_kind,
            "declared_columns": declared_columns,
            "declared_rows": declared_rows,
        },
        children=children,
    )


def _build_grid_cell(
    *,
    col: int,
    row: int,
    col_span: int,
    row_span: int,
    cell_index: int,
    children: list[Block],
) -> Block:
    return Block(
        type="grid_cell",
        meta={
            "col": col,
            "row": row,
            "col_span": col_span,
            "row_span": row_span,
            "cell_index": cell_index,
        },
        children=children,
    )


def _parse_body_grid_blocks(
    lines: list[str],
    slide_title: str,
    *,
    source_kind: str = "body-grid",
) -> list[Block]:
    """Parse a strict body-grid slide body."""
    blocks: list[Block] = []
    i = 0

    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue

        gm = _GRID_OPEN_RE.match(stripped)
        if gm:
            if blocks:
                _raise_parse_error(
                    "body-grid requires exactly one <!-- grid: ... --> block",
                    slide_title,
                )
            grid_block, i = _parse_grid_block(lines, i, slide_title, source_kind)
            blocks.append(grid_block)
            continue

        _raise_parse_error(
            "body-grid does not allow content outside <!-- cell --> blocks",
            slide_title,
        )

    if len(blocks) != 1:
        _raise_parse_error(
            "body-grid requires exactly one <!-- grid: ... --> block",
            slide_title,
        )

    return blocks


def _resolve_grid_gap(attrs: dict[str, str], slide_title: str) -> tuple[str, str]:
    """Resolve shorthand/explicit gap values into (col_gap, row_gap)."""
    gap = attrs.get("gap", "").lower()
    col_gap = attrs.get("col_gap", "").lower()
    row_gap = attrs.get("row_gap", "").lower()

    for attr_name, value in (("gap", gap), ("col_gap", col_gap), ("row_gap", row_gap)):
        if value and value not in _GRID_GAP_VALUES:
            _raise_parse_error(
                f"grid attribute '{attr_name}' must be one of {', '.join(sorted(_GRID_GAP_VALUES))}",
                slide_title,
            )

    fallback = gap or "md"
    return col_gap or fallback, row_gap or fallback


def _parse_grid_block(
    lines: list[str],
    start: int,
    slide_title: str,
    source_kind: str = "body-grid",
) -> tuple[Block, int]:
    """Parse a strict grid block and return (grid_block, next_index)."""
    gm = _GRID_OPEN_RE.match(lines[start].strip())
    raw_attrs = gm.group(1) if gm else ""
    attrs = _parse_strict_comment_attrs(
        raw_attrs,
        allowed_keys=_GRID_ALLOWED_KEYS,
        required_keys=_GRID_REQUIRED_KEYS,
        kind="grid",
        slide_title=slide_title,
    )

    declared_columns = _parse_positive_int(
        attrs["columns"],
        attr_name="columns",
        kind="grid",
        slide_title=slide_title,
        min_value=1,
        max_value=6,
    )
    declared_rows = _parse_positive_int(
        attrs["rows"],
        attr_name="rows",
        kind="grid",
        slide_title=slide_title,
        min_value=1,
        max_value=6,
    )
    col_gap, row_gap = _resolve_grid_gap(attrs, slide_title)

    cells: list[Block] = []
    i = start + 1
    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped:
            i += 1
            continue

        if _GRID_CLOSE_RE.match(stripped):
            if not cells:
                _raise_parse_error(
                    "body-grid requires at least one <!-- cell: ... --> block",
                    slide_title,
                )
            _validate_grid_cells(cells, declared_columns, declared_rows, slide_title)
            return (
                _build_grid_block(
                    columns=["1fr"] * declared_columns,
                    rows=["1fr"] * declared_rows,
                    col_gap=col_gap,
                    row_gap=row_gap,
                    source_kind=source_kind,
                    declared_columns=declared_columns,
                    declared_rows=declared_rows,
                    children=cells,
                ),
                i + 1,
            )

        if _CELL_OPEN_RE.match(stripped):
            cell_block, i = _parse_grid_cell(lines, i, slide_title, len(cells))
            cells.append(cell_block)
            continue

        if _CELL_CLOSE_RE.match(stripped):
            _raise_parse_error(
                "<!-- /cell --> found without matching <!-- cell: ... -->",
                slide_title,
            )
        if _GRID_OPEN_RE.match(stripped):
            _raise_parse_error("nested <!-- grid: ... --> blocks are not supported", slide_title)

        _raise_parse_error(
            "body-grid does not allow content outside <!-- cell --> blocks",
            slide_title,
        )

    _raise_parse_error("unclosed <!-- grid: ... --> block", slide_title)


def _parse_grid_cell(
    lines: list[str],
    start: int,
    slide_title: str,
    cell_index: int,
) -> tuple[Block, int]:
    """Parse a strict cell block and return (cell_block, next_index)."""
    cm = _CELL_OPEN_RE.match(lines[start].strip())
    raw_attrs = cm.group(1) if cm else ""
    attrs = _parse_strict_comment_attrs(
        raw_attrs,
        allowed_keys=_CELL_ALLOWED_KEYS,
        required_keys=_CELL_REQUIRED_KEYS,
        kind="cell",
        slide_title=slide_title,
    )

    col = _parse_positive_int(
        attrs["col"],
        attr_name="col",
        kind="cell",
        slide_title=slide_title,
    )
    row = _parse_positive_int(
        attrs["row"],
        attr_name="row",
        kind="cell",
        slide_title=slide_title,
    )
    col_span = _parse_positive_int(
        attrs.get("col_span", "1"),
        attr_name="col_span",
        kind="cell",
        slide_title=slide_title,
    )
    row_span = _parse_positive_int(
        attrs.get("row_span", "1"),
        attr_name="row_span",
        kind="cell",
        slide_title=slide_title,
    )

    cell_lines: list[str] = []
    i = start + 1
    while i < len(lines):
        stripped = lines[i].strip()
        if _CELL_CLOSE_RE.match(stripped):
            return (
                _build_grid_cell(
                    col=col,
                    row=row,
                    col_span=col_span,
                    row_span=row_span,
                    cell_index=cell_index,
                    children=parse_blocks(cell_lines),
                ),
                i + 1,
            )
        if _CELL_OPEN_RE.match(stripped):
            _raise_parse_error("nested <!-- cell: ... --> blocks are not supported", slide_title)
        if _GRID_OPEN_RE.match(stripped):
            _raise_parse_error("nested <!-- grid: ... --> blocks are not supported", slide_title)
        if _GRID_CLOSE_RE.match(stripped):
            _raise_parse_error("<!-- /grid --> found before <!-- /cell -->", slide_title)
        cell_lines.append(lines[i])
        i += 1

    _raise_parse_error("unclosed <!-- cell: ... --> block", slide_title)


def _validate_grid_cells(
    cells: list[Block],
    declared_columns: int,
    declared_rows: int,
    slide_title: str,
) -> None:
    """Validate bounds and overlap for grid cells."""
    occupied: set[tuple[int, int]] = set()

    for cell in cells:
        col = cell.meta["col"]
        row = cell.meta["row"]
        col_span = cell.meta["col_span"]
        row_span = cell.meta["row_span"]
        col_end = col + col_span - 1
        row_end = row + row_span - 1

        if col_end > declared_columns or row_end > declared_rows:
            _raise_parse_error(
                f"cell at row={row} col={col} exceeds declared grid size {declared_columns}x{declared_rows}",
                slide_title,
            )

        for rr in range(row, row_end + 1):
            for cc in range(col, col_end + 1):
                if (rr, cc) in occupied:
                    _raise_parse_error(
                        f"grid cells overlap at row={rr} col={cc}",
                        slide_title,
                    )
                occupied.add((rr, cc))


def _split_legacy_columns(
    blocks: list[Block],
    labels: tuple[str, ...],
) -> dict[str, list[Block]]:
    columns: dict[str, list[Block]] = {label: [] for label in labels}
    current_col = labels[0]

    for block in blocks:
        if block.type == "heading4":
            label_text = "".join(inline.text for inline in block.children).strip().lower()
            if label_text in columns:
                current_col = label_text
                continue
        columns[current_col].append(block)

    return columns


def _normalize_legacy_grid_blocks(
    blocks: list[Block],
    *,
    template: str,
    ratio: str,
) -> list[Block]:
    """Normalize legacy 2col / 3col body blocks into a grid block."""
    if template == "body-2col":
        labels = _LEGACY_COL_LABELS_2
        columns_by_label = _split_legacy_columns(blocks, labels)
        if ratio == "6040":
            columns = ["3fr", "2fr"]
        elif ratio == "4060":
            columns = ["2fr", "3fr"]
        else:
            columns = ["1fr", "1fr"]
    else:
        labels = _LEGACY_COL_LABELS_3
        columns_by_label = _split_legacy_columns(blocks, labels)
        columns = ["1fr", "1fr", "1fr"]

    cells: list[Block] = []
    for idx, label in enumerate(labels, start=1):
        cells.append(
            _build_grid_cell(
                col=idx,
                row=1,
                col_span=1,
                row_span=1,
                cell_index=idx - 1,
                children=columns_by_label[label],
            )
        )

    return [
        _build_grid_block(
            columns=columns,
            rows=["1fr"],
            col_gap="lg",
            row_gap="lg",
            source_kind=template,
            declared_columns=len(columns),
            declared_rows=1,
            children=cells,
        )
    ]

# ---------------------------------------------------------------------------
# Source extraction
# ---------------------------------------------------------------------------

_SOURCE_RE = re.compile(
    r"^((?:出典|参照|参考|Sources?|References?|Refs?|Citation)\s*[:：])\s*(.+)$",
    re.IGNORECASE,
)


def _extract_source(blocks: list[Block]) -> tuple[list[Block], str]:
    """Extract footer source from the last paragraph if it starts with 'Source:'/'出典:'/'参照:'/'参考:' etc."""
    if not blocks:
        return blocks, ""

    last = blocks[-1]
    if last.type != "paragraph" or not last.children:
        return blocks, ""

    # Reconstruct text from inline children
    full_text = ""
    for inline in last.children:
        full_text += inline.text

    m = _SOURCE_RE.match(full_text)
    if m:
        return blocks[:-1], f"{m.group(1)} {m.group(2).strip()}"

    return blocks, ""


def _extract_grid_source(blocks: list[Block]) -> tuple[list[Block], str]:
    """Extract footer source from the last grid cell that contains one."""
    if len(blocks) != 1 or blocks[0].type != "grid":
        return blocks, ""

    grid = blocks[0]
    cells = list(grid.children)
    for cell in reversed(cells):
        cell_children, source = _extract_source(cell.children)
        if source:
            cell.children = cell_children
            grid.children = cells
            return [grid], source

    return blocks, ""


# ---------------------------------------------------------------------------
# Top-level parser
# ---------------------------------------------------------------------------


def parse_markdown(text: str) -> Deck:
    """Parse a full markdown document into a Deck AST."""
    lines = text.splitlines()
    deck = Deck()

    # Phase 1: Split into slide-level chunks by headings
    chunks: list[dict] = []
    current_chunk: dict | None = None

    in_fence = False
    for line in lines:
        if _FENCE_RE.match(line.strip()):
            in_fence = not in_fence

        if not in_fence:
            hm = _HEADING_RE.match(line)
            if hm:
                level = len(hm.group(1))
                title = hm.group(2).strip()

                if level <= 3:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = {"level": level, "title": title, "lines": []}
                    continue

        if current_chunk is not None:
            current_chunk["lines"].append(line)

    if current_chunk:
        chunks.append(current_chunk)

    # Phase 1.5: Attach slide comments to the correct chunk.
    # A <!-- slide: ... --> comment that appears at the END of a chunk's lines
    # (i.e. just before the next ### heading) should belong to the NEXT chunk,
    # not the current one.
    for ci in range(len(chunks)):
        chunk = chunks[ci]
        # Cover (level 1) comments always belong to the cover itself — skip.
        if chunk["level"] == 1:
            continue
        lines_list = chunk["lines"]
        # Collect trailing slide comments (from end of lines, skipping blanks)
        trailing_comments: list[dict] = []
        trim_from = len(lines_list)
        j = len(lines_list) - 1
        while j >= 0:
            stripped_ln = lines_list[j].strip()
            if not stripped_ln:
                j -= 1
                continue
            sc = parse_slide_comment(stripped_ln)
            if sc is not None:
                trailing_comments.append((j, sc))
                j -= 1
            else:
                break
        # If there are trailing slide comments AND a next chunk exists,
        # move them to the next chunk's "pre_comment"
        if trailing_comments and ci + 1 < len(chunks):
            merged = {}
            # trailing_comments are in reverse order, so reverse to apply in order
            for idx_ln, sc_dict in reversed(trailing_comments):
                merged.update(sc_dict)
                lines_list[idx_ln] = ""  # remove from current chunk
            chunks[ci + 1].setdefault("pre_comment", {})
            chunks[ci + 1]["pre_comment"].update(merged)

    # Phase 2: Process each chunk into Slide objects
    current_section: Slide | None = None
    current_body_slides: list[Slide] = []

    def flush_section():
        nonlocal current_section, current_body_slides
        if current_section is not None:
            deck.sections.append((current_section, current_body_slides))
            current_section = None
            current_body_slides = []

    for chunk in chunks:
        level = chunk["level"]
        title = chunk["title"]
        content_lines = chunk["lines"]

        # Extract slide comment from content lines + pre_comment from previous chunk
        comment = dict(chunk.get("pre_comment", {}))
        remaining_lines: list[str] = []
        for ln in content_lines:
            sc = parse_slide_comment(ln)
            if sc is not None:
                comment.update(sc)
            else:
                remaining_lines.append(ln)

        if level == 1:
            # Cover
            subtitle = comment.pop("subtitle", "")
            deck.cover = Slide(
                type="cover",
                title=title,
                subtitle=subtitle,
                comment=comment,
            )

        elif level == 2:
            # Section
            flush_section()
            subtitle = comment.pop("subtitle", "")
            current_section = Slide(
                type="section",
                title=title,
                subtitle=subtitle,
                comment=comment,
            )

        elif level == 3:
            # Body
            if current_section is None:
                # Body without section: create implicit section
                current_section = Slide(type="section", title="")

            eyebrow = comment.pop("eyebrow", "") or current_section.title
            comment.pop("subtitle", None)
            template_name = comment.get("template", "")
            if template_name in ("body-grid", "body-grid-full"):
                blocks = _parse_body_grid_blocks(
                    remaining_lines,
                    title,
                    source_kind=template_name,
                )
                blocks, source = _extract_grid_source(blocks)
            else:
                blocks = parse_blocks(remaining_lines)
                if template_name in ("body-2col", "body-3col"):
                    blocks = _normalize_legacy_grid_blocks(
                        blocks,
                        template=template_name,
                        ratio=comment.get("ratio", ""),
                    )
                    blocks, source = _extract_grid_source(blocks)
                else:
                    blocks, source = _extract_source(blocks)

            slide = Slide(
                type="body",
                title=title,
                eyebrow=eyebrow,
                blocks=blocks,
                source=source,
                comment=comment,
            )
            current_body_slides.append(slide)

    flush_section()
    return deck
