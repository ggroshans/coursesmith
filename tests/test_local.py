import tempfile
import unittest
from pathlib import Path

from coursesmith.sources.base import MissingSource
from coursesmith.sources.local import LocalAdapter
from coursesmith.sources.registry import Registry

INTRO = """# Beekeeping basics

A hive holds one queen, thousands of workers and a few drones. The queen lays the eggs, and the workers feed
the larvae, build comb and guard the entrance. See [[Hive inspection]] and [the honey notes](sub/honey.md).

## Colony roles

Workers change jobs as they age, from cleaning cells to nursing to foraging for nectar and pollen.
"""
INSPECT = """---
tags: [x]
---
# Hive inspection

Open a hive on a calm, warm day and work slowly. Check for eggs, larvae and capped brood in each frame, and
look for the queen or for signs that she is laying. Go back to [[Beekeeping basics#Colony roles|the roles]].
"""
HONEY = "<html><body><main><h1>Honey</h1><p>" + "Nectar is ripened into honey by workers fanning it. " * 6 + "</p></main></body></html>"


def make(root):
    root = Path(root)
    (root / "sub").mkdir()
    (root / ".obsidian").mkdir()
    (root / "Beekeeping basics.md").write_text(INTRO)
    (root / "Hive inspection.md").write_text(INSPECT)
    (root / "sub" / "honey.html").write_text(HONEY)
    (root / ".obsidian" / "x.md").write_text("hidden " * 40)
    (root / "image.png").write_bytes(b"x")
    return root


class LocalAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = make(self.tmp.name)
        self.a = LocalAdapter({"name": "notes", "adapter": "local", "path": str(self.dir)})

    def tearDown(self):
        self.tmp.cleanup()

    def test_files_are_seeds_and_hidden_or_binary_files_are_skipped(self):
        self.assertEqual(sorted(self.a.seeds()), ["local>notes/Beekeeping_basics.md", "local>notes/Hive_inspection.md",
                                                  "local>notes/sub/honey.html"])
        self.assertTrue(self.a.allowed("local>notes/Hive_inspection.md"))
        self.assertFalse(self.a.allowed("local>notes/image.png"))
        self.assertFalse(self.a.owns("local>other/Hive_inspection.md"))

    def test_wikilinks_and_relative_links_resolve(self):
        rec = self.a.fetch("local>notes/Beekeeping_basics.md")
        self.assertEqual(set(rec["body_links"]), {"local>notes/Hive_inspection.md", "local>notes/sub/honey.html"})
        back = self.a.fetch("local>notes/Hive_inspection.md")
        self.assertEqual(back["body_links"], ["local>notes/Beekeeping_basics.md"])
        self.assertNotIn("tags:", back["text"])
        self.assertIn("Colony roles", rec["text"])
        self.assertNotIn("[[", rec["text"])

    def test_html_and_version(self):
        rec = self.a.fetch("local>notes/sub/honey.html")
        self.assertIn("ripened into honey", rec["text"])
        self.assertEqual(rec["source"], "notes")
        self.assertEqual(rec["license"]["class"], "all-rights-reserved")
        self.assertEqual(rec["version"], self.a.fetch("local>notes/sub/honey.html")["version"])

    def test_missing_and_include_exclude(self):
        with self.assertRaises(MissingSource):
            self.a.fetch("local>notes/nope.md")
        b = LocalAdapter({"name": "notes", "path": str(self.dir), "include": ["**/*.md"], "exclude": ["Hive*"]})
        self.assertEqual(b.seeds(), ["local>notes/Beekeeping_basics.md"])

    def test_check_flags_a_missing_path(self):
        self.assertEqual(self.a.check()["problems"], [])
        self.assertTrue(LocalAdapter({"name": "n", "path": str(self.dir / "gone")}).check()["problems"])


class SourcesOnlyTest(unittest.TestCase):
    def test_no_wikipedia_when_sources_only(self):
        with tempfile.TemporaryDirectory() as d:
            make(d)
            cfg = [{"name": "notes", "adapter": "local", "path": d}]
            r = Registry(cfg, sources_only=True)
            self.assertEqual([a.adapter for a in r.adapters], ["local"])
            self.assertFalse(r.allowed("Soil"))
            self.assertEqual(len(r.all_seeds()), 3)
            self.assertTrue(Registry(cfg).allowed("Soil"))


if __name__ == "__main__":
    unittest.main()


class TableCellsTest(unittest.TestCase):
    ROW = "<table><tr><th>Capability</th><th>A</th><th>B</th></tr><tr><td>API</td><td>Yes</td><td>Yes</td></tr>" \
          "<tr><td colspan='2'>Wide</td><td>x</td></tr></table>"

    def test_span_mode_keeps_equal_neighbours_apart(self):
        from coursesmith.text.emit import table_rows
        from bs4 import BeautifulSoup
        t = BeautifulSoup(self.ROW, "html.parser").table
        self.assertEqual(table_rows(t)[1], ["API", "Yes"])                      # legacy: merged
        self.assertEqual(table_rows(t, "span")[1], ["API", "Yes", "Yes"])
        self.assertEqual(table_rows(t, "span")[2], ["Wide", "x"])               # a real colspan still merges
