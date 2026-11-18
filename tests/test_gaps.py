"""report gaps and frame add: the gap-fill step is mechanical, so it is tested."""
import json
import unittest

import yaml

from coursesmith import config
from coursesmith.frame import add, gaps
from tests.helpers import make_subject, temp_root

SUBJECT = """slug: tiny
title: Tiny
frame:
  parts:
    - key: blocks
      title: "Building blocks"
      chapters:
        - title: "Caching"
          seeds: ["Cache (computing)", "rfc>9111"]   # keep this comment
        - title: "Load balancing"
          seeds: ["Load balancing (computing)"]
        - title: "Storage"
"""

FRAME = {"subject": "tiny", "status": "draft: x", "parts": [{"key": "blocks", "title": "Building blocks", "chapters": [
    {"key": "caching", "title": "Caching", "seeds": ["Cache (computing)", "rfc>9111"]},
    {"key": "load-balancing", "title": "Load balancing", "seeds": ["Load balancing (computing)"]},
    {"key": "storage", "title": "Storage", "seeds": []}]}]}


class FakeStore:
    def canonical(self, t):
        return {"cache": "Cache (computing)", "Hash table": "Hash table"}.get(t, t)


def setup(subject_yaml=SUBJECT):
    s = make_subject("tiny", subject_yaml)
    s.frame_path.write_text(yaml.safe_dump(FRAME, sort_keys=False), encoding="utf-8")
    return s


def draft(s, chapter, entries):
    s.draft_dir.mkdir(parents=True, exist_ok=True)
    (s.draft_dir / f"{chapter}.jsonl").write_text("".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")


def entry(title, **kw):
    return {"title": title, "kind": "Concept", "article": None, "prerequisites": [], "related": [], **kw}


class FrameAddTest(unittest.TestCase):
    def test_adds_to_frame_and_mirrors_into_subject_yaml(self):
        with temp_root():
            s = setup()
            added, skipped = add.run(s, "caching", ["Hash table", "Cache (computing)", "rfc>9111", "Memoization"],
                                     store=FakeStore(), log=lambda *_: None)
            self.assertEqual(added, ["Hash table", "Memoization"])
            self.assertEqual([p for p, _ in skipped], ["Cache (computing)", "rfc>9111"])
            frame = yaml.safe_load(s.frame_path.read_text())
            self.assertEqual(frame["parts"][0]["chapters"][0]["seeds"],
                             ["Cache (computing)", "rfc>9111", "Hash table", "Memoization"])
            text = (s.dir / "subject.yaml").read_text()
            self.assertIn('seeds: ["Cache (computing)", "rfc>9111", "Hash table", "Memoization"]', text)
            cfg = yaml.safe_load(text)
            self.assertEqual(cfg["frame"]["parts"][0]["chapters"][1]["seeds"], ["Load balancing (computing)"])

    def test_page_in_another_chapter_is_skipped(self):
        with temp_root():
            s = setup()
            added, skipped = add.run(s, "Storage", ["Load balancing (computing)"], store=FakeStore(),
                                     log=lambda *_: None)
            self.assertEqual(added, [])
            self.assertEqual(skipped, [("Load balancing (computing)", "Load balancing")])

    def test_chapter_without_a_list_gets_one_and_also_is_separate(self):
        with temp_root():
            s = setup()
            add.run(s, "Storage", ["RAID"], store=FakeStore(), log=lambda *_: None)
            add.run(s, "Storage", ["Disk"], also=True, store=FakeStore(), log=lambda *_: None)
            cfg = yaml.safe_load((s.dir / "subject.yaml").read_text())
            ch = cfg["frame"]["parts"][0]["chapters"][2]
            self.assertEqual(ch["seeds"], ["RAID"])
            self.assertEqual(ch["also"], ["Disk"])

    def test_comments_survive_and_unknown_chapter_stops(self):
        with temp_root():
            s = setup()
            add.run(s, "load-balancing", ["Failover"], store=FakeStore(), log=lambda *_: None)
            self.assertIn("# keep this comment", (s.dir / "subject.yaml").read_text())
            with self.assertRaises(SystemExit):
                add.run(s, "no-such-chapter", ["Failover"], store=FakeStore(), log=lambda *_: None)

    def test_subject_without_a_hand_frame_only_changes_frame_yaml(self):
        with temp_root():
            s = setup("slug: tiny\ntitle: Tiny\nframe: {}\n")
            add.run(s, "caching", ["Memoization"], store=FakeStore(), log=lambda *_: None)
            self.assertEqual((s.dir / "subject.yaml").read_text(), "slug: tiny\ntitle: Tiny\nframe: {}\n")
            self.assertIn("Memoization", s.frame_path.read_text())


class GapsTest(unittest.TestCase):
    def test_unresolved_thin_and_files(self):
        with temp_root():
            s = setup()
            draft(s, "caching", [
                entry("Cache", article="Cache (computing)", prerequisites=["Hash function", "Memoization"]),
                entry("Eviction", prerequisites=["Cache", "Hash function"], related=["cache"]),
                entry("Designing X", kind="Worked example", notes="thin: no estimates", prerequisites=["Cache"])])
            (s.draft_dir / "caching.gaps.md").write_text("# gaps\n- Memoization\n- Hash function\nnote\n")
            (s.draft_dir / "caching.part01.jsonl").write_text(json.dumps(entry("Part", prerequisites=["Zzz"])) + "\n")
            g = gaps.collect(s)
            names = {r["name"]: r for r in g["unresolved"]}
            self.assertEqual(set(names), {"Hash function", "Memoization"})
            self.assertEqual(names["Hash function"]["n"], 2)
            self.assertEqual(g["unresolved"][0]["name"], "Hash function")  # most named first
            self.assertEqual(names["Hash function"]["suggest_chapter"], "caching")
            self.assertEqual([t["title"] for t in g["thin"]], ["Designing X"])
            self.assertEqual(g["files"], [{"file": "caching.gaps.md", "bullets": 2}])
            self.assertEqual(gaps.summary(s), (2, 1))

    def test_accepted_gaps_drop_out(self):
        with temp_root():
            s = setup(SUBJECT + 'gaps:\n  accepted: {"hash function": "no source", "Designing X": "thin on purpose"}\n')
            draft(s, "caching", [
                entry("Cache", prerequisites=["Hash function", "Memoization"]),
                entry("Designing X", kind="Worked example", notes="Thin: nothing")])
            g = gaps.collect(s)
            self.assertEqual([r["name"] for r in g["unresolved"]], ["Memoization"])
            self.assertEqual(g["thin"], [])
            self.assertEqual(g["accepted"], 2)

    def test_run_writes_report_and_no_gaps_says_so(self):
        with temp_root():
            s = setup()
            draft(s, "caching", [entry("Cache", prerequisites=["Hash function"])])
            lines = []
            gaps.run(s, log=lines.append)
            md = (s.reports_dir / "gaps.md").read_text()
            self.assertIn("| Hash function | 1 | Cache | caching |", md)
            self.assertEqual(json.loads((s.reports_dir / "gaps.json").read_text())["unresolved"][0]["name"],
                             "Hash function")
            draft(s, "caching", [entry("Cache"), entry("Hash function")])
            gaps.run(s, log=lines.append)
            self.assertIn("No open gaps.", (s.reports_dir / "gaps.md").read_text())


if __name__ == "__main__":
    unittest.main()
