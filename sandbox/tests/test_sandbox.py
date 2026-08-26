from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


SANDBOX_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = SANDBOX_DIR.parent
sys.path.insert(0, str(SANDBOX_DIR))

from wiki_renderer import render_wikitext, validate_source  # noqa: E402


class WikiSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads((SANDBOX_DIR / "config.json").read_text(encoding="utf-8"))

    def test_every_configured_source_exists_and_validates(self) -> None:
        for title, filename in self.config["pages"].items():
            with self.subTest(title=title):
                path = PROJECT_DIR / "pages" / filename
                self.assertTrue(path.is_file())
                self.assertEqual(validate_source(path.read_text(encoding="utf-8")), [])

    def test_every_page_renders_with_local_links(self) -> None:
        for title, filename in self.config["pages"].items():
            with self.subTest(title=title):
                source = (PROJECT_DIR / "pages" / filename).read_text(encoding="utf-8")
                rendered = render_wikitext(source, link_base="/wiki")
                self.assertIn("mw-parser-output", f'<div class="mw-parser-output">{rendered.html}</div>')
                self.assertNotIn("intern.ihf.rwth-aachen.de/wiki/", rendered.html)
                self.assertTrue(rendered.headings)

    def test_hub_links_to_every_detail_page(self) -> None:
        main = self.config["main_page"]
        source = (PROJECT_DIR / "pages" / self.config["pages"][main]).read_text(encoding="utf-8")
        rendered = render_wikitext(source, link_base="/wiki")
        for title in self.config["pages"]:
            if title != main:
                self.assertIn(title, rendered.links)

    def test_expected_categories_are_present(self) -> None:
        expected = {
            "Software Defined Radio (SDR)": {"Hardware", "Software"},
            "NI USRP-2954R": {"Hardware", "Messtechnik"},
            "OFDM-based Joint Communication and Sensing (JCAS)": {
                "Projekte",
                "Forschungsthemen",
                "Software",
            },
        }
        for title, categories in expected.items():
            source = (PROJECT_DIR / "pages" / self.config["pages"][title]).read_text(encoding="utf-8")
            rendered = render_wikitext(source, link_base="/wiki")
            self.assertEqual(set(rendered.categories), categories)

    def test_three_level_hierarchy_is_linked_in_both_directions(self) -> None:
        titles = tuple(self.config["pages"])
        self.assertEqual(
            titles,
            (
                "Software Defined Radio (SDR)",
                "NI USRP-2954R",
                "OFDM-based Joint Communication and Sensing (JCAS)",
            ),
        )
        for title, filename in self.config["pages"].items():
            source = (PROJECT_DIR / "pages" / filename).read_text(encoding="utf-8")
            rendered = render_wikitext(source, link_base="/wiki")
            with self.subTest(title=title):
                for related_title in titles:
                    if related_title != title:
                        self.assertIn(related_title, rendered.links)

    def test_hierarchy_uses_dedicated_sections_not_navigation_bar(self) -> None:
        hub = (PROJECT_DIR / "pages" / self.config["pages"]["Software Defined Radio (SDR)"]).read_text(encoding="utf-8")
        hardware = (PROJECT_DIR / "pages" / self.config["pages"]["NI USRP-2954R"]).read_text(encoding="utf-8")
        project = (PROJECT_DIR / "pages" / self.config["pages"]["OFDM-based Joint Communication and Sensing (JCAS)"]).read_text(encoding="utf-8")
        for source in (hub, hardware, project):
            self.assertNotIn("SDR documentation", source)
        self.assertIn("== Hardware ==", hub)
        self.assertIn("=== NI USRP-2954R ===", hub)
        self.assertIn("==== Project on this hardware ====", hub)
        self.assertIn("== SDR hierarchy ==", hardware)
        self.assertIn("== Project on this hardware ==", hardware)
        self.assertIn("== SDR hierarchy ==", project)

    def test_pages_do_not_use_ascii_arrow_diagrams(self) -> None:
        for title, filename in self.config["pages"].items():
            source = (PROJECT_DIR / "pages" / filename).read_text(encoding="utf-8")
            with self.subTest(title=title):
                self.assertNotIn("->", source)
                self.assertNotIn("→", source)

    def test_jcas_source_links_target_gitlab_main(self) -> None:
        source = (PROJECT_DIR / "pages" / self.config["pages"]["OFDM-based Joint Communication and Sensing (JCAS)"]).read_text(encoding="utf-8")
        self.assertIn("https://git.rwth-aachen.de/ihf/sdr/jcas-ofdm/-/tree/main", source)
        self.assertIn("https://git.rwth-aachen.de/ihf/sdr/jcas-ofdm/-/blob/main/Flow_graphs/OFDMJCAS.grc", source)

    def test_recorded_receiver_results_are_labelled_and_present(self) -> None:
        source = (PROJECT_DIR / "pages" / self.config["pages"]["OFDM-based Joint Communication and Sensing (JCAS)"]).read_text(encoding="utf-8")
        for value in ("-47.87", "-29.59", "-25.13 dBm", "6.94 dBm", "dBFS"):
            with self.subTest(value=value):
                self.assertIn(value, source)

    def test_public_pages_do_not_expose_local_research_files(self) -> None:
        forbidden = (
            "Docs/",
            "Docs.zip",
            "First tests.docx",
            "project_facts.txt",
            "/home/",
        )
        for title, filename in self.config["pages"].items():
            source = (PROJECT_DIR / "pages" / filename).read_text(encoding="utf-8")
            with self.subTest(title=title):
                for value in forbidden:
                    self.assertNotIn(value, source)

    def test_critical_project_distinctions_remain_explicit(self) -> None:
        project_source = (
            PROJECT_DIR
            / "pages"
            / self.config["pages"]["OFDM-based Joint Communication and Sensing (JCAS)"]
        ).read_text(encoding="utf-8")
        required = (
            "there are no UHD Source or UHD Sink blocks",
            "two inputs and three outputs",
            "100000 samples/s",
            "200 MHz USRP master clock",
            "Target detection",
            "Not implemented",
            "labels the axis as velocity in m/s",
        )
        for value in required:
            with self.subTest(value=value):
                self.assertIn(value, project_source)

    def test_rejects_markdown_backticks_that_mediawiki_would_not_render(self) -> None:
        self.assertTrue(validate_source("`code`"))
        self.assertEqual(validate_source("# Valid MediaWiki numbered-list item"), [])


if __name__ == "__main__":
    unittest.main()
