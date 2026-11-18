import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

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


if __name__ == "__main__":
    unittest.main()
