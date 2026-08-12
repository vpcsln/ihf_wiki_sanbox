from __future__ import annotations

import hashlib
import re
import sys
import unittest
from pathlib import Path


SANDBOX_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SANDBOX_DIR))

from serve import (  # noqa: E402
    PAGE_FILES,
    REFERENCE_SNAPSHOT_DIR,
    edit_body,
    page_source,
    page_url,
    reference_index_body,
    reference_page_body,
    search_body,
    view_body,
)


class LocalServerTests(unittest.TestCase):
    def test_original_ihf_logo_and_local_skin_dependencies(self) -> None:
        static_dir = SANDBOX_DIR / "static"
        logo = static_dir / "vendor" / "ihf" / "Logo_IHF.png"
        self.assertEqual(
            hashlib.sha256(logo.read_bytes()).hexdigest(),
            "428e22aebbe8412260cdd311b2e85215bb7eb9a76f45f097b11938daffe1516f",
        )
        styles = "\n".join(
            (static_dir / "vendor" / "ihf" / name).read_text(encoding="utf-8")
            for name in ("vector-legacy.css", "site.css")
        )
        references = re.findall(r"url\(([^)]+)\)", styles)
        self.assertTrue(references)
        for reference in references:
            local_url = reference.strip("\"'").split("?", 1)[0]
            with self.subTest(url=local_url):
                self.assertTrue(local_url.startswith("/static/vendor/ihf/"))
                target = static_dir / local_url.removeprefix("/static/")
                self.assertTrue(target.is_file())

    def test_every_view_renders_without_live_wiki_links(self) -> None:
        for title in PAGE_FILES:
            with self.subTest(title=title):
                body = view_body(title)
                self.assertIn('class="mw-parser-output"', body)
                self.assertNotIn("intern.ihf.rwth-aachen.de/wiki/", body)
                self.assertTrue(page_url(title).startswith("/wiki/"))

    def test_search_returns_clean_local_results(self) -> None:
        body = search_body("OFDM")
        self.assertIn("3 result(s)", body)
        self.assertNotIn("class &quot;wikitable&quot;", body)
        self.assertNotIn("intern.ihf.rwth-aachen.de", body)

    def test_editor_preview_is_non_saving_and_renders_source(self) -> None:
        title = "Software Defined Radio (SDR)"
        body = edit_body(title, page_source(title), preview=True)
        self.assertIn("Local syntax checks passed.", body)
        self.assertIn("Vorschau", body)
        self.assertIn("wpPreview", body)
        self.assertIn("wpSave", body)

    def test_reference_index_is_safe_when_snapshot_is_present_or_absent(self) -> None:
        body = reference_index_body()
        if (REFERENCE_SNAPSHOT_DIR / "manifest.json").is_file():
            self.assertIn("Read-only local reference", body)
            self.assertIn("/reference/", body)
        else:
            self.assertIn("snapshot is not available", body)
            self.assertIn("sync.py fetch", body)

    def test_reference_page_uses_numeric_ids_and_local_sanitized_content(self) -> None:
        self.assertIsNone(reference_page_body("../1"))
        manifest_path = REFERENCE_SNAPSHOT_DIR / "manifest.json"
        if not manifest_path.is_file():
            return
        import json

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        page_id = str(manifest["pages"][0]["pageid"])
        result = reference_page_body(page_id)
        self.assertIsNotNone(result)
        title, body = result
        self.assertTrue(title)
        self.assertIn("Read-only snapshot", body)
        self.assertNotIn("<script", body.lower())
        self.assertNotIn("<iframe", body.lower())


if __name__ == "__main__":
    unittest.main()
