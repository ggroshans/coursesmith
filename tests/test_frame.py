import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from coursesmith.frame import hubs as H
from coursesmith.frame.build import _chapters, _report


def _kept(titles, cats):
    return {t: {"core": 4, "categories": cats.get(t, []), "description": ""} for t in titles}


class Frame(unittest.TestCase):
    def test_chapters_by_category_without_hints(self):
        cats = {t: ["Loudspeakers"] for t in ("A", "B", "C")}
        cats["D"] = ["Audio engineering"]
        kept = _kept(["A", "B", "C", "D"], cats)
        chs = _chapters({"key": "main", "title": "Speakers"}, list(kept), kept)
        self.assertEqual(chs[0]["title"], "Loudspeakers")
        self.assertEqual(sorted(chs[0]["seeds"]), ["A", "B", "C"])
        self.assertEqual(chs[-1]["title"], "Speakers: other topics")

    def test_report_without_targets(self):
        with tempfile.TemporaryDirectory() as d:
            subj = SimpleNamespace(title="Speakers", dir=Path(d), reports_dir=Path(d) / "reports")
            parts = [{"key": "main", "title": "Speakers",
                      "chapters": [{"key": "x", "title": "X", "seeds": ["A"], "share": 1.0}]}]
            _report(subj, parts, _kept(["A"], {}), [], __import__("collections").Counter(), 0,
                    Path(d) / "scope" / "calibration.csv")
            text = (Path(d) / "reports" / "frame_report.md").read_text()
            self.assertIn("(share 100.0%)", text)
            self.assertNotIn("target", text.split("## Parts")[1].split("## Unassigned")[0])


class ImportanceLevels(unittest.TestCase):
    def _client(self, seen):
        class C:
            def category_members(self, cat, ns=(0, 14)):
                seen.append(cat)
                return [("Talk:" + cat.split(":")[1].split("-")[0] + " page", 1)]
        return C()

    def test_limited_levels_read_only_those_categories_and_cache_apart(self):
        seen = []
        with tempfile.TemporaryDirectory() as d, mock.patch.object(H, "HUB_CACHE", Path(d)):
            out = H.wikiproject_importance(self._client(seen), "Philosophy", ("Top", "High"))
            self.assertEqual(out, {"Top page": "Top", "High page": "High"})
            self.assertEqual(seen, ["Category:Top-importance Philosophy articles",
                                    "Category:High-importance Philosophy articles"])
            full = H.wikiproject_importance(self._client(seen), "Philosophy")
            self.assertEqual(len(full), 4)

    def test_default_levels_keep_the_old_cache_key(self):
        seen = []
        with tempfile.TemporaryDirectory() as d, mock.patch.object(H, "HUB_CACHE", Path(d)):
            H.wikiproject_importance(self._client(seen), "Soil")
            self.assertTrue((Path(d) / "wikiproject_soil.json").exists()
                            or any(p.name.startswith("wikiproject") for p in Path(d).iterdir()))


if __name__ == "__main__":
    unittest.main()
