import json
import unittest
from types import SimpleNamespace

from coursesmith.order import order as O
from coursesmith.publish import units as U
from coursesmith.write import render as R
from coursesmith.write.skeleton import DEFAULT_RANGES, word_bounds, word_range


def subj(**word_ranges):
    return SimpleNamespace(targets={"word_ranges": word_ranges})


class WordRangeTest(unittest.TestCase):
    def e(self, kind="Concept", weight="Major"):
        return {"kind": kind, "weight": weight}

    def test_defaults_are_unchanged_for_existing_kinds(self):
        self.assertEqual(word_range(self.e(weight="Minor")), "40-90 words")
        self.assertEqual(word_range(self.e(weight="Landmark")), "100-250 words")
        for k in ("Classification", "Process", "Debate"):
            self.assertEqual(word_range(self.e(k)), "100-250 words")
        self.assertEqual(word_range(self.e()), "60-150 words")
        self.assertEqual(word_range(self.e(kind="Process", weight="Minor")), "40-90 words")  # Minor still wins

    def test_new_kinds_have_longer_defaults(self):
        self.assertEqual(word_range(self.e("Worked example")), "250-600 words")
        self.assertEqual(word_range(self.e("Case study", "Minor")), "150-400 words")

    def test_subject_overrides(self):
        s = subj(**{"Worked example": [300, 800], "Minor": [30, 60], "long": [120, 300], "default": [70, 170]})
        self.assertEqual(word_bounds(self.e("Worked example"), s), (300, 800))
        self.assertEqual(word_bounds(self.e(weight="Minor"), s), (30, 60))
        self.assertEqual(word_bounds(self.e(weight="Landmark"), s), (120, 300))
        self.assertEqual(word_bounds(self.e(), s), (70, 170))
        self.assertEqual(word_bounds(self.e("Concept"), subj()), DEFAULT_RANGES["default"])

    def test_a_kind_key_wins_over_weight(self):
        s = subj(Concept=[10, 20])
        self.assertEqual(word_bounds(self.e("Concept", "Minor"), s), (10, 20))

    def test_word_range_string_still_parses(self):
        lo, hi = map(int, word_range(self.e()).split()[0].split("-"))
        self.assertEqual((lo, hi), (60, 150))


class TidyTextTest(unittest.TestCase):
    def test_single_paragraph_text_is_what_it_always_was(self):
        self.assertEqual(R.tidy_text("  One line\nwrapped here.  "), "One line wrapped here.")
        self.assertEqual(R.tidy_text("  One line\nwrapped here.  ", False), "One line wrapped here.")

    def test_blank_lines_make_paragraphs_when_asked(self):
        self.assertEqual(R.tidy_text("First para\nstill first.\n\n\n  Second para.\n \nThird."),
                         "First para still first.\n\nSecond para.\n\nThird.")

    def test_without_paragraphs_the_old_collapse_applies(self):
        self.assertEqual(R.tidy_text("First.\n\n\nSecond.\nThird.", False), "First. Second. Third.")

    def merge(self, cfg, kinds, entries):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)
            (p / "fill.a.json").write_text(json.dumps({"entries": entries}))
            subject = SimpleNamespace(write_dir=p, cfg=cfg, entries=lambda: [{"id": i, "kind": k} for i, k in kinds.items()])
            return R.merge(subject)[0]["entries"]

    def test_existing_courses_keep_one_paragraph_per_entry(self):
        out = self.merge({"edition": {}}, {"x": "Concept"}, {"x": {"title": "A\nB", "text": "p1\n\np2"}})
        self.assertEqual(out["x"], {"title": "A B", "text": "p1 p2"})

    def test_paragraphs_for_worked_examples_and_case_studies_always(self):
        out = self.merge({"edition": {}}, {"w": "Worked example", "c": "Case study", "k": "Concept"},
                         {"w": {"text": "p1\n\np2"}, "c": {"text": "p1\n\np2"}, "k": {"text": "p1\n\np2"}})
        self.assertEqual((out["w"]["text"], out["c"]["text"], out["k"]["text"]), ("p1\n\np2", "p1\n\np2", "p1 p2"))

    def test_edition_paragraphs_turns_them_on_for_everything(self):
        out = self.merge({"edition": {"paragraphs": True}}, {"k": "Concept"}, {"k": {"text": "p1\n\np2"}})
        self.assertEqual(out["k"]["text"], "p1\n\np2")


class GlossaryExemptionTest(unittest.TestCase):
    def test_question_kinds_are_never_terms(self):
        self.assertTrue(U.is_question_entry({"kind": "Worked example", "title": "Rate limiter"}))
        self.assertTrue(U.is_question_entry({"kind": "Case study", "title": "Twitter"}))
        self.assertFalse(U.is_question_entry({"kind": "Concept", "title": "How caching works"}))  # a survey course

    def test_question_courses_exempt_question_shaped_titles(self):
        for t in ("Design a URL shortener", "How would you shard a database?", "What is a cache", "Compare SQL and NoSQL"):
            self.assertTrue(U.is_question_entry({"kind": "Concept", "title": t}, True), t)
        for t in ("Consistent hashing", "Cache", "Designated driver"):
            self.assertFalse(U.is_question_entry({"kind": "Concept", "title": t}, True), t)


class OrderKeyTest(unittest.TestCase):
    def key(self, kind, title="T", imp=5.0):
        nodes = {"p": {"importance": imp, "difficulty": 0.5}}
        return O._sort_key({"kind": kind, "weight": "Major", "article": "p", "title": title}, nodes)

    def test_a_worked_example_sorts_after_every_other_kind(self):
        self.assertGreater(self.key("Worked example", imp=99), self.key("Concept", imp=0))
        self.assertGreater(self.key("Case study", imp=99), self.key("Method", imp=0))

    def test_other_kinds_keep_their_old_relative_order(self):
        a, b = self.key("Concept", "A", 5), self.key("Concept", "B", 9)
        self.assertLess(b, a)  # more important first
        self.assertEqual(a[0], b[0])


if __name__ == "__main__":
    unittest.main()


class OrderBuildTest(unittest.TestCase):
    FRAME = """parts:
  - key: q
    title: Questions
    question: true
    chapters:
      - {key: c-url, title: Design a URL shortener, question: true, seeds: []}
      - {key: c-rate, title: Design a rate limiter, question: true, seeds: []}
"""

    def entry(self, i, title, kind, chapter, pre=()):
        return {"id": i, "title": title, "kind": kind, "weight": "Major", "level": "Foundational", "part": "Questions",
                "chapter": chapter, "selected": True, "prerequisites": list(pre),
                "facts": [{"text": "x", "sent_ids": ["a"]}], "sources": []}

    def test_worked_example_is_last_in_its_chapter_and_chapters_stay_in_frame_order(self):
        from coursesmith.util import write_jsonl
        from .helpers import make_subject, temp_root
        with temp_root():
            subj = make_subject("q", "slug: q\ntitle: Q\nshort: q\ncourse_type: questions\n")
            subj.frame_path.write_text(self.FRAME)
            es = [
                self.entry("q-1", "Design: URL shortener answer", "Worked example", "Design a URL shortener"),  # first in file
                self.entry("q-2", "Hash function", "Concept", "Design a URL shortener"),
                self.entry("q-3", "Base62 encoding", "Method", "Design a URL shortener", pre=["q-2"]),
                self.entry("q-4", "Token bucket", "Concept", "Design a rate limiter"),
                self.entry("q-5", "Rate limiter answer", "Worked example", "Design a rate limiter"),
            ]
            write_jsonl(subj.entries_dir / "ch.jsonl", es)
            order = O.build(subj, log=lambda *a: None)
            self.assertEqual(order, ["q-2", "q-3", "q-1", "q-4", "q-5"])


class VerifyUnitsTest(unittest.TestCase):
    def test_defaults_are_unchanged(self):
        from coursesmith.verify.verify import quantities
        self.assertEqual(quantities("Clay is below 0.002 mm and the soil holds 12 years of water."),
                         [(0.002, 0.002, "mm"), (12.0, 12.0, "year")])
        self.assertEqual(quantities("Latency is 5 ms and the cache holds 10 GB."), [])  # unknown units stay unknown

    def test_extra_units(self):
        from coursesmith.verify.verify import SYSTEMS_UNITS, quantities
        q = quantities("A read takes 5 ms (sometimes 200 µs); the cache holds 10 GB at 100,000 QPS. Use 3 replicas, 2 s.",
                       SYSTEMS_UNITS)
        self.assertEqual(q[:3], [(5.0, 5.0, "ms"), (200.0, 200.0, "µs"), (10.0, 10.0, "GB")])
        self.assertIn((3.0, 3.0, "replica"), q)
        self.assertIn((2.0, 2.0, "s"), q)  # seconds keep their s
        self.assertNotIn((5.0, 5.0, "m"), q)  # ms is not metres

    def test_longest_unit_wins(self):
        from coursesmith.verify.verify import quantities
        self.assertEqual(quantities("5 ms", ["ms"])[0][2], "ms")
        self.assertEqual(quantities("5 m and 5 ms", ["ms"]), [(5.0, 5.0, "m"), (5.0, 5.0, "ms")])

    def test_compare_uses_the_extra_units(self):
        from coursesmith.verify.verify import SYSTEMS_UNITS, compare
        e = {"title": "Cache hit", "kind": "Concept", "facts": [{"text": "A cache hit takes 5 ms.", "sent_ids": ["a"]}]}
        self.assertEqual(compare(e, "A cache hit takes 5 ms on average.", "paper")["verdict"], "no comparable claim")
        self.assertEqual(compare(e, "A cache hit takes 5 ms on average.", "paper", SYSTEMS_UNITS)["verdict"], "supports")
        self.assertEqual(compare(e, "A cache hit takes 9 ms on average.", "paper", SYSTEMS_UNITS)["verdict"], "differs")
