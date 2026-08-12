#!/usr/bin/env python3
"""Serve and edit the SDR wiki drafts in a local-only MediaWiki-style sandbox."""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import random
import re
import shutil
import tempfile
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

try:
    from .wiki_renderer import RenderedPage, render_wikitext, validate_source
except ImportError:  # Direct execution via sandbox/start.sh.
    from wiki_renderer import RenderedPage, render_wikitext, validate_source


SANDBOX_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SANDBOX_DIR.parent
PAGES_DIR = PROJECT_DIR / "pages"
STATIC_DIR = SANDBOX_DIR / "static"
BACKUPS_DIR = SANDBOX_DIR / "backups"
CONFIG_PATH = SANDBOX_DIR / "config.json"
REFERENCE_SNAPSHOT_DIR = PROJECT_DIR / "reference" / "ihf_wiki_examples" / "snapshot"


def load_config() -> dict:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    missing = [name for name in config["pages"].values() if not (PAGES_DIR / name).is_file()]
    if missing:
        raise RuntimeError(f"Configured wiki source files are missing: {', '.join(missing)}")
    return config


CONFIG = load_config()
SITE_NAME: str = CONFIG["site_name"]
MAIN_PAGE: str = CONFIG["main_page"]
PAGE_FILES: dict[str, str] = CONFIG["pages"]


def page_url(title: str) -> str:
    return "/wiki/" + quote(title.replace(" ", "_"), safe="()_:-")


def index_url(title: str, action: str) -> str:
    return "/wiki/index.php?" + f"title={quote(title)}&action={quote(action)}"


def page_source(title: str) -> str:
    return (PAGES_DIR / PAGE_FILES[title]).read_text(encoding="utf-8")


def render_page_source(source: str) -> RenderedPage:
    return render_wikitext(source, link_base="/wiki")


def strip_wikitext(source: str) -> str:
    text = re.sub(r"\[\[Category:[^\]]+\]\]", "", source, flags=re.IGNORECASE)
    text = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[(https?://\S+)\s+([^\]]+)\]", r"\2", text)
    text = re.sub(r"^\{\|[^\n]*$|^\|-.*$|^\|\}.*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[!|]\s*(?:[^\n|]*\|\s*)?", "", text, flags=re.MULTILINE)
    text = re.sub(r"__TOC__", "", text)
    text = re.sub(r"</?(?:pre|code)>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"[={}|'*#<>]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def navigation_table() -> str:
    links = "".join(
        f'<li><a href="{page_url(title)}">{html.escape(title)}</a></li>'
        for title in PAGE_FILES
    )
    return f"<ul>{links}</ul>"


def skin(title: str, body: str, action: str = "view", saved: bool = False) -> str:
    content_selected = " selected" if action == "view" else ""
    edit_selected = " selected" if action == "edit" else ""
    history_selected = " selected" if action == "history" else ""
    saved_notice = (
        '<div class="validation-ok">Local source saved. A backup of the previous version was created.</div>'
        if saved
        else ""
    )
    safe_title = html.escape(title)
    return f"""<!doctype html>
<html class="client-nojs" lang="de" dir="ltr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_title} – {html.escape(SITE_NAME)}</title>
  <link rel="stylesheet" href="/static/vendor/ihf/vector-legacy.css">
  <link rel="stylesheet" href="/static/vendor/ihf/site.css">
  <link rel="stylesheet" href="/static/vector.css">
  <link rel="shortcut icon" href="/static/vendor/ihf/favicon.ico">
</head>
<body class="mediawiki ltr sitedir-ltr mw-hide-empty-elt ns-0 ns-subject skin-vector action-{html.escape(action)} skin-vector-legacy">
<div id="mw-page-base" class="noprint"></div>
<div id="mw-head-base" class="noprint"></div>

<div id="content" class="mw-body" role="main">
  <a id="top"></a>
  <div id="siteNotice">
    <div class="sandbox-notice"><strong>Nur lokale Vorschau:</strong> Diese Sandbox ist nicht mit dem IHF-Wiki verbunden und kann dort nichts veröffentlichen.</div>
    {saved_notice}
  </div>
  <div class="mw-indicators"></div>
  <h1 id="firstHeading" class="firstHeading">{safe_title}</h1>
  <div id="bodyContent" class="vector-body">
    <div id="siteSub" class="noprint">Aus der lokalen IHF-Wiki-Sandbox</div>
    <div id="contentSub"></div>
    <div id="contentSub2"></div>
    <div id="jump-to-nav"></div>
    <a class="mw-jump-link" href="#mw-head">Zur Navigation springen</a>
    <a class="mw-jump-link" href="#searchInput">Zur Suche springen</a>
    <div id="mw-content-text" class="mw-body-content mw-content-ltr" lang="en" dir="ltr">{body}</div>
  </div>
</div>

<div id="mw-navigation">
  <h2>Navigationsmenü</h2>
  <div id="mw-head">
    <nav id="p-personal" class="mw-portlet mw-portlet-personal vector-user-menu-legacy vector-menu" aria-labelledby="p-personal-label" role="navigation">
      <h3 id="p-personal-label" class="vector-menu-heading"><span>Meine Werkzeuge</span></h3>
      <div class="vector-menu-content">
        <ul class="vector-menu-content-list">
          <li class="mw-list-item"><span>Lokale Sandbox</span></li>
          <li class="mw-list-item"><a href="/wiki/index.php?title=Sandbox&amp;action=about">Über diese Sandbox</a></li>
        </ul>
      </div>
    </nav>

    <div id="left-navigation">
      <nav id="p-namespaces" class="mw-portlet mw-portlet-namespaces vector-menu vector-menu-tabs" aria-labelledby="p-namespaces-label" role="navigation">
        <h3 id="p-namespaces-label" class="vector-menu-heading"><span>Namensräume</span></h3>
        <div class="vector-menu-content">
          <ul class="vector-menu-content-list">
            <li id="ca-nstab-main" class="mw-list-item{content_selected}"><a href="{page_url(title)}">Seite</a></li>
            <li id="ca-talk" class="mw-list-item"><a href="{index_url(title, 'talk')}">Diskussion</a></li>
          </ul>
        </div>
      </nav>
    </div>

    <div id="right-navigation">
      <nav id="p-views" class="mw-portlet mw-portlet-views vector-menu vector-menu-tabs" aria-labelledby="p-views-label" role="navigation">
        <h3 id="p-views-label" class="vector-menu-heading"><span>Ansichten</span></h3>
        <div class="vector-menu-content">
          <ul class="vector-menu-content-list">
            <li id="ca-view" class="mw-list-item{content_selected}"><a href="{page_url(title)}">Lesen</a></li>
            <li id="ca-edit" class="mw-list-item{edit_selected}"><a href="{index_url(title, 'edit')}">Quelltext bearbeiten</a></li>
            <li id="ca-history" class="mw-list-item{history_selected}"><a href="{index_url(title, 'history')}">Versionsgeschichte</a></li>
          </ul>
        </div>
      </nav>
      <div id="p-search" role="search" class="vector-search-box">
        <div>
          <h3><label for="searchInput">Suche</label></h3>
          <form action="/wiki/index.php" id="searchform" method="get">
            <div id="simpleSearch" data-search-loc="header-navigation">
              <input type="search" name="search" placeholder="IHF-Wiki-Sandbox durchsuchen" id="searchInput">
              <input type="hidden" name="title" value="Spezial:Suche">
              <input type="submit" name="fulltext" value="Suchen" id="mw-searchButton" class="searchButton mw-fallbackSearchButton">
              <input type="submit" name="go" value="Seite" id="searchButton" class="searchButton">
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>

  <div id="mw-panel">
    <div id="p-logo" role="banner"><a class="mw-wiki-logo" href="{page_url(MAIN_PAGE)}" title="SDR-Hauptseite"></a></div>

    <nav id="p-navigation" class="mw-portlet mw-portlet-navigation vector-menu vector-menu-portal portal" aria-labelledby="p-navigation-label" role="navigation">
      <h3 id="p-navigation-label" class="vector-menu-heading"><span>Navigation</span></h3>
      <div class="vector-menu-content">
        <ul class="vector-menu-content-list">
          <li class="mw-list-item"><a href="{page_url(MAIN_PAGE)}">SDR-Hauptseite</a></li>
          <li class="mw-list-item"><a href="/reference/">IHF-Wiki-Beispiele</a></li>
          <li class="mw-list-item"><a href="/wiki/Spezial:Letzte_%C3%84nderungen">Letzte Änderungen</a></li>
          <li class="mw-list-item"><a href="/wiki/Spezial:Zuf%C3%A4llige_Seite">Zufällige Seite</a></li>
        </ul>
      </div>
    </nav>

    <nav id="p-sdr" class="mw-portlet mw-portlet-sdr vector-menu vector-menu-portal portal" aria-labelledby="p-sdr-label" role="navigation">
      <h3 id="p-sdr-label" class="vector-menu-heading"><span>SDR-Dokumentation</span></h3>
      <div class="vector-menu-content">{navigation_table()}</div>
    </nav>

    <nav id="p-tb" class="mw-portlet mw-portlet-tb vector-menu vector-menu-portal portal" aria-labelledby="p-tb-label" role="navigation">
      <h3 id="p-tb-label" class="vector-menu-heading"><span>Werkzeuge</span></h3>
      <div class="vector-menu-content">
        <ul class="vector-menu-content-list">
          <li class="mw-list-item"><a href="{index_url(title, 'edit')}">Quelltext bearbeiten</a></li>
          <li class="mw-list-item"><a href="{index_url(title, 'history')}">Lokale Versionen</a></li>
          <li class="mw-list-item"><a href="javascript:window.print()">Druckversion</a></li>
          <li class="mw-list-item"><a href="/wiki/index.php?title=Sandbox&amp;action=about">Seiteninformationen</a></li>
        </ul>
      </div>
    </nav>
  </div>
</div>

<footer id="footer" class="mw-footer" role="contentinfo">
  <ul id="footer-info">
    <li id="footer-info-lastmod">Lokale Vorschau der versionierten SDR-Wiki-Entwürfe.</li>
    <li>Keine Anmeldung und keine Live-Wiki-Schreibfunktion.</li>
  </ul>
  <ul id="footer-places">
    <li><a href="/wiki/index.php?title=Sandbox&amp;action=about">Über diese Sandbox</a></li>
    <li><a href="{index_url(title, 'edit')}">Lokalen Quelltext bearbeiten</a></li>
  </ul>
  <ul id="footer-icons" class="noprint">
    <li id="footer-poweredbyico"><img src="/static/vendor/ihf/poweredby_mediawiki_88x31.png" srcset="/static/vendor/ihf/poweredby_mediawiki_132x47.png 1.5x, /static/vendor/ihf/poweredby_mediawiki_176x62.png 2x" alt="Powered by MediaWiki-compatible local renderer" width="88" height="31"></li>
  </ul>
</footer>
</body>
</html>
"""


def view_body(title: str) -> str:
    rendered = render_page_source(page_source(title))
    return f'<div class="mw-parser-output">{rendered.html}</div>'


def edit_body(title: str, source: str, preview: bool = False) -> str:
    errors = validate_source(source)
    validation = (
        '<div class="validation-error"><strong>Validation failed:</strong><ul>'
        + "".join(f"<li>{html.escape(error)}</li>" for error in errors)
        + "</ul></div>"
        if errors
        else '<div class="validation-ok">Local syntax checks passed.</div>'
    )
    preview_html = ""
    if preview and not errors:
        rendered = render_page_source(source)
        preview_html = (
            '<h2 class="preview-heading">Vorschau</h2>'
            f'<div class="mw-parser-output">{rendered.html}</div>'
            '<h2 class="preview-heading">Quelltext</h2>'
        )
    return f"""
{validation}
{preview_html}
<form class="edit-form" method="post" action="/wiki/index.php">
  <input type="hidden" name="title" value="{html.escape(title, quote=True)}">
  <textarea name="wpTextbox1" spellcheck="false" aria-label="MediaWiki-Quelltext">{html.escape(source)}</textarea>
  <div class="edit-buttons">
    <button class="primary" type="submit" name="wpSave" value="1">Lokale Änderungen speichern</button>
    <button class="secondary" type="submit" name="wpPreview" value="1">Vorschau zeigen</button>
    <a class="secondary" style="padding:7px 14px" href="{page_url(title)}">Abbrechen</a>
  </div>
  <p>Beim Speichern wird nur die lokale <code>.wiki</code>-Datei geändert. Die vorherige Version wird unter <code>sandbox/backups/</code> gesichert.</p>
</form>
"""


def save_local_source(title: str, source: str) -> None:
    errors = validate_source(source)
    if errors:
        raise ValueError(" ".join(errors))
    target = PAGES_DIR / PAGE_FILES[title]
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    backup_dir = BACKUPS_DIR / target.stem
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target, backup_dir / f"{timestamp}.wiki")
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=PAGES_DIR, prefix=target.name + ".", delete=False
    ) as temporary:
        temporary.write(source)
        temporary_path = Path(temporary.name)
    temporary_path.replace(target)


def history_body(title: str) -> str:
    target = PAGES_DIR / PAGE_FILES[title]
    backup_dir = BACKUPS_DIR / target.stem
    backups = sorted(backup_dir.glob("*.wiki"), reverse=True) if backup_dir.exists() else []
    rows = [
        "<tr><th>Version</th><th>Location</th></tr>",
        f"<tr><td>Current local source</td><td><code>pages/{html.escape(target.name)}</code></td></tr>",
    ]
    rows.extend(
        f"<tr><td>{html.escape(item.stem)}</td><td><code>sandbox/backups/{html.escape(target.stem)}/{html.escape(item.name)}</code></td></tr>"
        for item in backups
    )
    note = "No local edit backups exist yet." if not backups else f"{len(backups)} local backup(s)."
    return f"<p>{note}</p><table class=\"wikitable\">{''.join(rows)}</table>"


def category_body(category: str) -> str:
    members = []
    for title in PAGE_FILES:
        rendered = render_page_source(page_source(title))
        if category.casefold() in (item.casefold() for item in rendered.categories):
            members.append(title)
    items = "".join(f'<li><a href="{page_url(title)}">{html.escape(title)}</a></li>' for title in members)
    return f"<p>Lokale Seiten in dieser Kategorie:</p><ul>{items or '<li>Keine lokalen Seiten.</li>'}</ul>"


def search_body(query: str) -> str:
    normalized = query.casefold().strip()
    if not normalized:
        return "<p>Enter a search term.</p>"
    results = []
    for title in PAGE_FILES:
        plain = strip_wikitext(page_source(title))
        if normalized in title.casefold() or normalized in plain.casefold():
            position = plain.casefold().find(normalized)
            start = max(0, position - 90) if position >= 0 else 0
            snippet = plain[start : start + 260]
            if start:
                snippet = "…" + snippet
            if start + 260 < len(plain):
                snippet += "…"
            results.append(
                '<div class="search-result">'
                f'<h3><a href="{page_url(title)}">{html.escape(title)}</a></h3>'
                f'<p>{html.escape(snippet)}</p></div>'
            )
    return f"<p>{len(results)} result(s) for <strong>{html.escape(query)}</strong>.</p>" + "".join(results)


def recent_changes_body() -> str:
    items = []
    if BACKUPS_DIR.exists():
        for path in sorted(BACKUPS_DIR.glob("*/*.wiki"), key=lambda p: p.stat().st_mtime, reverse=True):
            items.append(f"<li>{html.escape(path.stem)} — <code>{html.escape(str(path.relative_to(PROJECT_DIR)))}</code></li>")
    return "<p>Local sandbox saves:</p><ul>" + ("".join(items) or "<li>No local saves yet.</li>") + "</ul>"


def reference_index_body() -> str:
    index_path = REFERENCE_SNAPSHOT_DIR / "index.html"
    if not index_path.is_file():
        return (
            "<p>The local example snapshot is not available. Fetch it from the project directory:</p>"
            "<pre>python3 reference/ihf_wiki_examples/sync.py fetch</pre>"
        )
    return (
        "<p><strong>Read-only local reference:</strong> these are sanitized snapshots of selected "
        "IHF Wiki pages. They are examples for structure and style; editing remains disabled.</p>"
        + index_path.read_text(encoding="utf-8")
    )


def reference_page_body(page_id: str) -> tuple[str, str] | None:
    if not page_id.isdigit():
        return None
    page_dir = REFERENCE_SNAPSHOT_DIR / "pages" / page_id
    metadata_path = page_dir / "metadata.json"
    content_path = page_dir / "content.html"
    if not metadata_path.is_file() or not content_path.is_file():
        return None
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = str(metadata["title"])
    details = (
        '<p><a href="/reference/">← All local examples</a></p>'
        '<div class="sandbox-notice"><strong>Read-only snapshot:</strong> '
        f'revision {html.escape(str(metadata["revid"]))} from '
        f'{html.escape(str(metadata["timestamp"]))}. Remote media and active content are omitted.</div>'
    )
    return title, details + content_path.read_text(encoding="utf-8")


class SandboxHandler(BaseHTTPRequestHandler):
    server_version = "IHFSDRSandbox/1.0"

    def log_message(self, format: str, *args: object) -> None:
        print(f"[{self.log_date_time_string()}] {format % args}")

    def send_html(self, title: str, body: str, action: str = "view", status: int = 200, saved: bool = False) -> None:
        payload = skin(title, body, action=action, saved=saved).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
            "script-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; "
            "form-action 'self'",
        )
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def serve_static(self, relative: str) -> None:
        target = (STATIC_DIR / relative).resolve()
        if STATIC_DIR.resolve() not in target.parents or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        payload = target.read_bytes()
        content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(payload)

    def do_HEAD(self) -> None:
        self.do_GET()

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/":
            self.redirect(page_url(MAIN_PAGE))
            return
        if path.startswith("/static/"):
            self.serve_static(unquote(path[len("/static/") :]))
            return
        if path in {"/reference", "/reference/"}:
            self.send_html("IHF Wiki examples", reference_index_body())
            return
        reference_match = re.fullmatch(r"/reference/(\d+)/?", path)
        if reference_match:
            reference_page = reference_page_body(reference_match.group(1))
            if reference_page is None:
                self.send_html(
                    "Reference page not found",
                    '<p>The selected page is not present in the local snapshot. <a href="/reference/">Return to the index.</a></p>',
                    status=404,
                )
            else:
                title, body = reference_page
                self.send_html(f"Reference: {title}", body)
            return
        if path == "/wiki/index.php":
            if "search" in query:
                term = query.get("search", [""])[0]
                self.send_html("Suchergebnisse", search_body(term))
                return
            title = query.get("title", [MAIN_PAGE])[0]
            action = query.get("action", ["view"])[0]
            if action == "about":
                self.send_html("Über diese Sandbox", "<p>This is a local-only preview and editing tool. It has no live-wiki credentials or publishing endpoint.</p>")
                return
            if title not in PAGE_FILES:
                self.send_html("Seite nicht gefunden", "<p>This title is not configured in the local sandbox.</p>", status=404)
                return
            if action == "edit":
                self.send_html(title, edit_body(title, page_source(title)), action="edit")
            elif action == "history":
                self.send_html(title, history_body(title), action="history")
            elif action == "talk":
                self.send_html(f"Diskussion:{title}", "<p>No local discussion page exists. Use the source repository for review comments.</p>")
            else:
                self.redirect(page_url(title))
            return
        if path.startswith("/wiki/"):
            title = unquote(path[len("/wiki/") :]).replace("_", " ")
            if title == "Hauptseite":
                self.redirect(page_url(MAIN_PAGE))
            elif title == "Spezial:Letzte Änderungen":
                self.send_html(title, recent_changes_body())
            elif title == "Spezial:Zufällige Seite":
                self.redirect(page_url(random.choice(tuple(PAGE_FILES))))
            elif title.startswith("Kategorie:"):
                category = title.split(":", 1)[1]
                self.send_html(title, category_body(category))
            elif title in PAGE_FILES:
                saved = query.get("saved", ["0"])[0] == "1"
                self.send_html(title, view_body(title), saved=saved)
            else:
                self.send_html(title or "Seite nicht gefunden", "<p>This page is not part of the local SDR documentation set.</p>", status=404)
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/wiki/index.php":
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST)
            return
        if length > 2_000_000:
            self.send_error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return
        form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
        title = form.get("title", [""])[0]
        source = form.get("wpTextbox1", [""])[0]
        if title not in PAGE_FILES:
            self.send_html("Invalid page", "<p>The requested page is not configured.</p>", status=400)
            return
        if "wpPreview" in form:
            self.send_html(title, edit_body(title, source, preview=True), action="edit")
            return
        if "wpSave" in form:
            errors = validate_source(source)
            if errors:
                self.send_html(title, edit_body(title, source), action="edit", status=400)
                return
            save_local_source(title, source)
            self.redirect(page_url(title) + "?saved=1")
            return
        self.send_error(HTTPStatus.BAD_REQUEST)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="TCP port (default: 8765)")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.host not in {"127.0.0.1", "::1", "localhost"}:
        raise SystemExit("Refusing a non-loopback bind address. This sandbox is local-only.")
    server = ThreadingHTTPServer((args.host, args.port), SandboxHandler)
    print(f"IHF SDR Wiki Sandbox: http://{args.host}:{args.port}/")
    print("Local files only; no IHF Wiki connection or publishing capability.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping sandbox.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
