from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
SYNC_PATH = PROJECT_DIR / "reference" / "ihf_wiki_examples" / "sync.py"
SPEC = importlib.util.spec_from_file_location("ihf_wiki_reference_sync", SYNC_PATH)
assert SPEC is not None and SPEC.loader is not None
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class ReferenceCorpusTests(unittest.TestCase):
    def test_sanitizer_removes_active_and_remote_loading_content(self) -> None:
        fragment = """
        <script src="https://example.invalid/a.js">alert(1)</script>
        <style>.x { background: url(https://example.invalid/a.png) }</style>
        <form action="https://example.invalid/"><input></form>
        <iframe src="https://example.invalid/"></iframe>
        <img src="https://example.invalid/a.png" srcset="x" alt="Original diagram">
        <div onclick="alert(1)" style="background:url(https://example.invalid/b.png)">text</div>
        <a href="https://example.invalid/reference">reference</a>
        """
        cleaned = SYNC.sanitize_fragment(fragment)
        for forbidden in ("<script", "<style", "<form", "<iframe", "<img", "onclick=", "src="):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, cleaned)
        self.assertIn("[Media omitted: Original diagram]", cleaned)
        self.assertIn("background:none", cleaned)
        self.assertIn('href="https://example.invalid/reference"', cleaned)

    def test_snapshot_links_resolve_selected_pages_only(self) -> None:
        fragment = '<a href="/wiki/Known_Page">known</a> <a href="/wiki/Missing">missing</a>'
        rewritten = SYNC.rewrite_snapshot_links(fragment, {"Known Page": 42})
        self.assertIn('href="/reference/42/"', rewritten)
        self.assertIn('href="#" data-unavailable-title="Missing"', rewritten)

    def test_hash_is_stable_and_sensitive_to_content(self) -> None:
        self.assertEqual(SYNC.sha256_text("same"), SYNC.sha256_text("same"))
        self.assertNotEqual(SYNC.sha256_text("same"), SYNC.sha256_text("different"))


if __name__ == "__main__":
    unittest.main()
