"""Small, dependency-free renderer for the MediaWiki subset used by the drafts."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from urllib.parse import quote


@dataclass(frozen=True)
class RenderedPage:
    html: str
    categories: tuple[str, ...]
    links: tuple[str, ...]
    headings: tuple[tuple[int, str, str], ...]


def validate_source(source: str) -> list[str]:
    errors: list[str] = []
    if source.count("{|") != source.count("|}"):
        errors.append("Unbalanced MediaWiki table markers ({| and |}).")
    if source.count("<pre>") != source.count("</pre>"):
        errors.append("Unbalanced <pre> blocks.")
    if source.count("<code>") != source.count("</code>"):
        errors.append("Unbalanced <code> elements.")
    if "`" in source:
        errors.append("Markdown backticks found; use <code> in MediaWiki source.")
    return errors


def _slug(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", cleaned).strip("_")
    return cleaned or "section"


def _internal_href(target: str, link_base: str) -> str:
    return link_base.rstrip("/") + "/" + quote(target.replace(" ", "_"), safe="()_-")


def _render_inline(text: str, link_base: str) -> str:
    escaped = html.escape(text, quote=False)

    def internal(match: re.Match[str]) -> str:
        target = html.unescape(match.group(1)).strip()
        label = html.unescape(match.group(2) or match.group(1)).strip()
        href = _internal_href(target, link_base)
        return f'<a href="{html.escape(href, quote=True)}">{html.escape(label)}</a>'

    def external(match: re.Match[str]) -> str:
        url = html.unescape(match.group(1))
        label = html.unescape(match.group(2) or match.group(1))
        return (
            f'<a class="external" href="{html.escape(url, quote=True)}" '
            f'target="_blank" rel="noopener noreferrer">{html.escape(label)}</a>'
        )

    escaped = re.sub(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", internal, escaped)
    escaped = re.sub(r"\[(https?://[^\s\]]+)(?:\s+([^\]]+))?\]", external, escaped)
    escaped = re.sub(r"'''(.+?)'''", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"''(.+?)''", r"<em>\1</em>", escaped)
    escaped = re.sub(r"&lt;code&gt;(.*?)&lt;/code&gt;", r"<code>\1</code>", escaped)
    escaped = escaped.replace("&lt;br&gt;", "<br>").replace("&lt;br/&gt;", "<br>")
    return escaped


def _parse_table(lines: list[str], start: int, link_base: str) -> tuple[str, int]:
    opening = lines[start]
    class_match = re.search(r'class="([^"]+)"', opening)
    style_match = re.search(r'style="([^"]+)"', opening)
    classes = class_match.group(1) if class_match else "wikitable"
    style = f' style="{html.escape(style_match.group(1), quote=True)}"' if style_match else ""
    rows: list[list[tuple[str, str, str]]] = []
    row: list[tuple[str, str, str]] = []
    index = start + 1

    def flush() -> None:
        nonlocal row
        if row:
            rows.append(row)
            row = []

    while index < len(lines):
        line = lines[index]
        if line.startswith("|}"):
            flush()
            index += 1
            break
        if line.startswith("|-"):
            flush()
            index += 1
            continue
        if line.startswith(("!", "|")):
            tag = "th" if line[0] == "!" else "td"
            cell = line[1:].strip()
            attributes = ""
            if " | " in cell:
                possible_attributes, possible_text = cell.split(" | ", 1)
                if "=" in possible_attributes:
                    attributes = " " + possible_attributes.strip()
                    cell = possible_text
            row.append((tag, attributes, cell))
        index += 1

    rendered_rows = []
    for cells in rows:
        rendered_cells = "".join(
            f"<{tag}{attrs}>{_render_inline(value, link_base)}</{tag}>"
            for tag, attrs, value in cells
        )
        rendered_rows.append(f"<tr>{rendered_cells}</tr>")
    table = f'<table class="{html.escape(classes, quote=True)}"{style}>{"".join(rendered_rows)}</table>'
    return table, index


def render_wikitext(source: str, link_base: str = "/wiki") -> RenderedPage:
    errors = validate_source(source)
    if errors:
        raise ValueError(" ".join(errors))

    lines = source.splitlines()
    categories = tuple(
        dict.fromkeys(re.findall(r"\[\[Category:([^\]]+)\]\]", source, flags=re.IGNORECASE))
    )
    links = tuple(
        dict.fromkeys(
            target.strip()
            for target in re.findall(r"\[\[([^|\]]+)(?:\|[^\]]+)?\]\]", source)
            if not target.lower().startswith("category:")
        )
    )
    headings: list[tuple[int, str, str]] = []
    output: list[str] = []
    list_type: str | None = None
    index = 0

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            output.append(f"</{list_type}>")
            list_type = None

    while index < len(lines):
        stripped = lines[index].strip()

        if re.fullmatch(r"\[\[Category:[^\]]+\]\]", stripped, flags=re.IGNORECASE):
            index += 1
            continue
        if stripped == "__TOC__":
            close_list()
            output.append("__LOCAL_TOC__")
            index += 1
            continue
        if stripped.startswith("{|"):
            close_list()
            table, index = _parse_table(lines, index, link_base)
            output.append(table)
            continue
        if stripped == "<pre>":
            close_list()
            block: list[str] = []
            index += 1
            while index < len(lines) and lines[index].strip() != "</pre>":
                block.append(lines[index])
                index += 1
            output.append(f"<pre>{html.escape(html.unescape(chr(10).join(block)))}</pre>")
            index += 1
            continue

        heading_match = re.fullmatch(r"(={2,4})\s*(.*?)\s*\1", stripped)
        if heading_match:
            close_list()
            level = len(heading_match.group(1))
            title = heading_match.group(2)
            anchor = _slug(title)
            headings.append((level, title, anchor))
            output.append(f'<h{level} id="{anchor}">{_render_inline(title, link_base)}</h{level}>')
            index += 1
            continue

        if stripped.startswith("* ") or stripped.startswith("# "):
            wanted = "ul" if stripped[0] == "*" else "ol"
            if list_type != wanted:
                close_list()
                output.append(f"<{wanted}>")
                list_type = wanted
            output.append(f"<li>{_render_inline(stripped[2:], link_base)}</li>")
            index += 1
            continue

        close_list()
        if stripped:
            output.append(f"<p>{_render_inline(stripped, link_base)}</p>")
        index += 1

    close_list()

    toc_items = []
    for level, title, anchor in headings:
        indent = max(0, level - 2)
        toc_items.append(
            f'<li style="margin-left:{indent * 1.25}em"><a href="#{anchor}">'
            f'{_render_inline(title, link_base)}</a></li>'
        )
    toc = (
        '<nav class="toc"><div class="toctitle">Inhaltsverzeichnis</div><ol>'
        + "".join(toc_items)
        + "</ol></nav>"
    )
    fragment = "\n".join(output).replace("__LOCAL_TOC__", toc)

    if categories:
        category_links = " <span aria-hidden=\"true\">|</span> ".join(
            f'<a href="{html.escape(_internal_href("Kategorie:" + category, link_base), quote=True)}">'
            f'{html.escape(category)}</a>'
            for category in categories
        )
        fragment += (
            '<div class="catlinks"><strong>Kategorien:</strong> '
            + category_links
            + "</div>"
        )

    return RenderedPage(fragment, categories, links, tuple(headings))
