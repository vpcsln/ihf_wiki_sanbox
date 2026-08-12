#!/usr/bin/env python3
"""Build standalone HTML previews without contacting the live IHF Wiki."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote

from sandbox.serve import skin
from sandbox.wiki_renderer import render_wikitext


ROOT = Path(__file__).resolve().parent
PAGES_DIR = ROOT / "pages"
PREVIEWS_DIR = ROOT / "previews"
CONFIG = json.loads((ROOT / "sandbox" / "config.json").read_text(encoding="utf-8"))
STATIC_DIR = ROOT / "sandbox" / "static"
STYLES = "\n".join(
    (STATIC_DIR / path).read_text(encoding="utf-8")
    for path in ("vendor/ihf/vector-legacy.css", "vendor/ihf/site.css", "vector.css")
).replace("/static/vendor/ihf/", "../sandbox/static/vendor/ihf/")


def local_page_path(title: str) -> str:
    return "/wiki/" + quote(title.replace(" ", "_"), safe="()_-:")


def preview_filename(source_filename: str) -> str:
    return Path(source_filename).with_suffix(".html").name


def make_links_standalone(fragment: str) -> str:
    """Point configured page links at sibling previews instead of any wiki."""
    for title, source_filename in CONFIG["pages"].items():
        fragment = fragment.replace(
            f'href="{html.escape(local_page_path(title), quote=True)}"',
            f'href="{html.escape(preview_filename(source_filename), quote=True)}"',
        )
    return fragment


def build_html(title: str, fragment: str) -> str:
    document = skin(title, f'<div class="mw-parser-output">{fragment}</div>')
    document = re.sub(
        r'\s*<link rel="stylesheet" href="/static/(?:vendor/ihf/(?:vector-legacy|site)|vector)\.css">',
        "",
        document,
    )
    document = document.replace("</head>", f"  <style>{STYLES}</style>\n</head>")
    document = document.replace(
        'href="/static/vendor/ihf/', 'href="../sandbox/static/vendor/ihf/'
    ).replace('src="/static/vendor/ihf/', 'src="../sandbox/static/vendor/ihf/')
    return make_links_standalone(document)


def main() -> None:
    PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)
    report: dict[str, dict[str, object]] = {}

    for title, source_filename in CONFIG["pages"].items():
        source_path = PAGES_DIR / source_filename
        preview_name = preview_filename(source_filename)
        rendered = render_wikitext(source_path.read_text(encoding="utf-8"), link_base="/wiki")
        (PREVIEWS_DIR / preview_name).write_text(
            build_html(title, rendered.html), encoding="utf-8"
        )
        report[title] = {
            "source": source_filename,
            "preview": preview_name,
            "categories": list(rendered.categories),
            "links": list(rendered.links),
        }
        print(f"Wrote {preview_name}")

    (PREVIEWS_DIR / "validation.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Rendered {len(report)} pages locally in {PREVIEWS_DIR}")


if __name__ == "__main__":
    main()
