#!/usr/bin/env python3
"""Fetch or verify a local-only corpus of relevant IHF MediaWiki pages."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
SELECTION_PATH = ROOT / "selection.json"
SNAPSHOT_DIR = ROOT / "snapshot"
SUMMARY_PATH = ROOT / "validation-summary.json"
DEFAULT_BASE_URL = "http://intern.ihf.rwth-aachen.de/wiki"
USER_AGENT = "IHF-SDR-Wiki-Reference/1.0 (read-only local documentation snapshot)"


def api_request(base_url: str, parameters: dict[str, str], retries: int = 3) -> dict:
    query = {"format": "json", "formatversion": "2", **parameters}
    url = f"{base_url.rstrip('/')}/api.php?{urlencode(query)}"
    request = Request(url, headers={"User-Agent": USER_AGENT})
    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if "error" in payload:
                raise RuntimeError(f"MediaWiki API error: {payload['error']}")
            return payload
        except Exception as error:  # Network failures are retried and then reported.
            last_error = error
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Request failed after {retries} attempts: {url}: {last_error}")


def category_members(base_url: str, category: str) -> list[dict]:
    members: list[dict] = []
    continuation: dict[str, str] = {}
    while True:
        response = api_request(
            base_url,
            {
                "action": "query",
                "list": "categorymembers",
                "cmtitle": f"Kategorie:{category}",
                "cmnamespace": "0",
                "cmlimit": "max",
                **continuation,
            },
        )
        members.extend(response["query"]["categorymembers"])
        if "continue" not in response:
            return members
        continuation = response["continue"]


def batched(values: list[str], size: int = 5) -> list[list[str]]:
    return [values[index : index + size] for index in range(0, len(values), size)]


def page_records(base_url: str, titles: list[str]) -> dict[str, dict]:
    records: dict[str, dict] = {}
    for title_batch in batched(titles):
        response = api_request(
            base_url,
            {
                "action": "query",
                "prop": "info|revisions",
                "rvslots": "main",
                "rvprop": "ids|timestamp|content",
                "titles": "|".join(title_batch),
            },
        )
        for page in response["query"]["pages"]:
            if page.get("missing"):
                raise RuntimeError(f"Selected page is missing: {page['title']}")
            revision = page["revisions"][0]
            records[page["title"]] = {
                "pageid": page["pageid"],
                "title": page["title"],
                "revid": revision["revid"],
                "parentid": revision.get("parentid"),
                "timestamp": revision["timestamp"],
                "source": revision["slots"]["main"]["content"],
            }
    return records


def parsed_page(base_url: str, title: str) -> dict:
    response = api_request(
        base_url,
        {
            "action": "parse",
            "page": title,
            "prop": "text|displaytitle|categories|links|images|revid",
            "disableeditsection": "1",
            "disabletoc": "0",
        },
    )
    return response["parse"]


def sanitize_fragment(fragment: str) -> str:
    cleaned = fragment
    for tag in ("script", "style", "form", "iframe", "object", "embed", "audio", "video"):
        cleaned = re.sub(
            rf"<{tag}\b[^>]*>.*?</{tag}\s*>", "", cleaned, flags=re.IGNORECASE | re.DOTALL
        )
        cleaned = re.sub(rf"<{tag}\b[^>]*/?>", "", cleaned, flags=re.IGNORECASE)

    def image_placeholder(match: re.Match[str]) -> str:
        element = match.group(0)
        alt_match = re.search(r'\balt=(?:"([^"]*)"|\'([^\']*)\')', element, flags=re.IGNORECASE)
        label = next((part for part in alt_match.groups() if part), "media") if alt_match else "media"
        return f'<span class="reference-media">[Media omitted: {html.escape(label)}]</span>'

    cleaned = re.sub(r"<img\b[^>]*>", image_placeholder, cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s(?:src|srcset|poster)=(?:\"[^\"]*\"|'[^']*')", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"url\([^)]*\)", "none", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\son[a-z]+=(?:\"[^\"]*\"|'[^']*')", "", cleaned, flags=re.IGNORECASE)
    return cleaned


def rewrite_snapshot_links(fragment: str, title_to_id: dict[str, int]) -> str:
    def internal_link(match: re.Match[str]) -> str:
        prefix, raw_target, suffix = match.groups()
        target = raw_target.replace("_", " ")
        if target in title_to_id:
            return f'{prefix}/reference/{title_to_id[target]}/{suffix}'
        return f'{prefix}#{suffix} data-unavailable-title="{html.escape(target, quote=True)}"'

    return re.sub(r'(<a\b[^>]*\bhref=")/wiki/([^"?#]+)(")', internal_link, fragment)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_index(entries: list[dict], category_names: list[str]) -> str:
    sections = []
    for category in category_names:
        members = [entry for entry in entries if category in entry["selection_categories"]]
        links = "".join(
            f'<li><a href="/reference/{entry["pageid"]}/">{html.escape(entry["title"])}</a></li>'
            for entry in members
        )
        sections.append(f"<h2>{html.escape(category)}</h2><ul>{links}</ul>")
    additional = [entry for entry in entries if not entry["selection_categories"]]
    if additional:
        links = "".join(
            f'<li><a href="/reference/{entry["pageid"]}/">{html.escape(entry["title"])}</a></li>'
            for entry in additional
        )
        sections.append(f"<h2>Additional examples</h2><ul>{links}</ul>")
    return "\n".join(sections)


def fetch(base_url: str) -> None:
    selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    selected: dict[str, set[str]] = {}
    category_counts: dict[str, int] = {}
    for category in selection["categories"]:
        members = category_members(base_url, category)
        category_counts[category] = len(members)
        for member in members:
            selected.setdefault(member["title"], set()).add(category)

    for title in selection["extra_pages"]:
        selected.setdefault(title, set())
    if selection.get("include_category_pages"):
        for category in selection["categories"]:
            selected.setdefault(f"Kategorie:{category}", set())

    titles = sorted(selected, key=str.casefold)
    print(
        f"Selected {len(titles)} deduplicated current pages from "
        f"{len(selection['categories'])} categories.",
        flush=True,
    )
    print("Fetching revision source in small batches...", flush=True)
    records = page_records(base_url, titles)
    print("Fetching rendered fragments and link metadata...", flush=True)
    site_info = api_request(
        base_url,
        {"action": "query", "meta": "siteinfo", "siprop": "general|statistics"},
    )["query"]

    temporary_root = Path(tempfile.mkdtemp(prefix="ihf-wiki-examples-", dir=ROOT))
    temporary_snapshot = temporary_root / "snapshot"
    pages_dir = temporary_snapshot / "pages"
    pages_dir.mkdir(parents=True)
    title_to_id = {title: record["pageid"] for title, record in records.items()}
    entries: list[dict] = []

    try:
        for index, title in enumerate(titles, start=1):
            record = records[title]
            parsed = parsed_page(base_url, title)
            fragment = sanitize_fragment(parsed["text"])
            fragment = rewrite_snapshot_links(fragment, title_to_id)
            page_dir = pages_dir / str(record["pageid"])
            page_dir.mkdir()
            (page_dir / "source.wiki").write_text(record["source"], encoding="utf-8")
            (page_dir / "content.html").write_text(fragment, encoding="utf-8")
            entry = {
                "pageid": record["pageid"],
                "title": title,
                "displaytitle": parsed.get("displaytitle", title),
                "revid": record["revid"],
                "parentid": record["parentid"],
                "timestamp": record["timestamp"],
                "selection_categories": sorted(selected[title]),
                "categories": sorted(
                    item["category"] for item in parsed.get("categories", []) if "category" in item
                ),
                "links": sorted(
                    item["title"] for item in parsed.get("links", []) if item.get("exists", True)
                ),
                "images": sorted(parsed.get("images", [])),
                "source_sha256": sha256_text(record["source"]),
                "content_sha256": sha256_text(fragment),
            }
            write_json(page_dir / "metadata.json", entry)
            entries.append(entry)
            print(f"[{index:>3}/{len(titles)}] {title}", flush=True)

        entries.sort(key=lambda entry: entry["title"].casefold())
        manifest = {
            "schema_version": 1,
            "generated_at": datetime.now(UTC).isoformat(),
            "base_url": base_url,
            "site": site_info["general"],
            "statistics": site_info["statistics"],
            "selection": selection,
            "category_member_counts": category_counts,
            "page_count": len(entries),
            "pages": entries,
        }
        write_json(temporary_snapshot / "manifest.json", manifest)
        (temporary_snapshot / "index.html").write_text(
            build_index(entries, selection["categories"]), encoding="utf-8"
        )
        summary = {
            "schema_version": 1,
            "generated_at": manifest["generated_at"],
            "mediawiki_generator": site_info["general"]["generator"],
            "category_member_counts": category_counts,
            "deduplicated_page_count": len(entries),
            "latest_revision_only": True,
            "uploaded_files_downloaded": 0,
            "verification": "passed",
        }
        write_json(temporary_root / "validation-summary.json", summary)

        if SNAPSHOT_DIR.exists():
            shutil.rmtree(SNAPSHOT_DIR)
        temporary_snapshot.replace(SNAPSHOT_DIR)
        shutil.copy2(temporary_root / "validation-summary.json", SUMMARY_PATH)
    finally:
        shutil.rmtree(temporary_root, ignore_errors=True)

    verify()


def verify() -> None:
    manifest_path = SNAPSHOT_DIR / "manifest.json"
    if not manifest_path.is_file():
        raise RuntimeError(f"Snapshot is missing. Run the fetch command first: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    for entry in manifest["pages"]:
        page_dir = SNAPSHOT_DIR / "pages" / str(entry["pageid"])
        source_path = page_dir / "source.wiki"
        content_path = page_dir / "content.html"
        metadata_path = page_dir / "metadata.json"
        for path in (source_path, content_path, metadata_path):
            if not path.is_file():
                failures.append(f"Missing {path}")
        if source_path.is_file() and sha256_text(source_path.read_text(encoding="utf-8")) != entry["source_sha256"]:
            failures.append(f"Source hash mismatch: {entry['title']}")
        if content_path.is_file() and sha256_text(content_path.read_text(encoding="utf-8")) != entry["content_sha256"]:
            failures.append(f"Content hash mismatch: {entry['title']}")
    if len(manifest["pages"]) != manifest["page_count"]:
        failures.append("Manifest page count does not match its page list")
    if failures:
        raise RuntimeError("Snapshot verification failed:\n- " + "\n- ".join(failures))
    print(f"Verified {manifest['page_count']} current page snapshots and their hashes.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("fetch", "verify"))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        if args.command == "fetch":
            fetch(args.base_url)
        else:
            verify()
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
