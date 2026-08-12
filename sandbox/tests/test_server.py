from __future__ import annotations

import hashlib
import re
import sys
import unittest
from pathlib import Path


SANDBOX_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SANDBOX_DIR))

from serve import PAGE_FILES, edit_body, page_source, page_url, search_body, view_body  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
