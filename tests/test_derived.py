import unittest

from coursesmith.publish import derived as D
from coursesmith.publish.check import allowed_numbers

ENTRY = {"id": "e1", "title": "URL shortener", "kind": "Worked example",
         "definition": {"text": "d", "sent_ids": ["s0"]},
         "facts": [{"text": "The service handles 1,000,000,000 new URLs per month and a read to write ratio of 100:1.",
                    "sent_ids": ["s1"]},
                   {"text": "Each URL needs 500 bytes of storage.", "sent_ids": ["s2"]}]}
ALLOWED = allowed_numbers(ENTRY)


class EvaluateTest(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(D.evaluate("1000000000 / (30 * 86400)")[0], 1000000000 / (30 * 86400))
        self.assertEqual(D.evaluate("2 ** 10")[0], 1024)
        self.assertEqual(D.evaluate("-5 + 3")[0], -2)
        self.assertEqual(D.evaluate("1,5".replace(",", "."))[0], 1.5)

    def test_literals_are_reported(self):
        self.assertEqual(D.evaluate("1000000000 / 86400")[1], {1000000000.0, 86400.0})

    def test_nothing_but_arithmetic(self):
        for bad in ("__import__('os')", "open('x')", "a + 1", "[1]", "1 if 1 else 2", "(1).real", "'a' * 3", "True + 1",
                    "1 < 2", "lambda: 1"):
            with self.assertRaises(D.DerivedError, msg=bad):
                D.evaluate(bad)

    def test_dangerous_arithmetic_is_refused(self):
        for bad in ("9 ** 9 ** 9", "10 ** 400", "1 / 0", "1000001 ** 2"):
            with self.assertRaises(D.DerivedError, msg=bad):
                D.evaluate(bad)

    def test_syntax_error(self):
        with self.assertRaises(D.DerivedError):
            D.evaluate("1 +")


class CheckItemTest(unittest.TestCase):
    GOOD = {"values": [385.8, 386], "from": ["s1"], "expr": "1000000000 / (30 * 86400)", "reason": "per month to per second"}

    def test_a_correct_declaration_holds(self):
        self.assertEqual(D.check_item(self.GOOD, ENTRY, ALLOWED), [])
        self.assertEqual(D.waived([self.GOOD], ENTRY, ALLOWED), ({385.8, 386.0}, []))

    def test_rounding_counts(self):
        item = dict(self.GOOD, values=[386, 385.8, 400])
        probs = D.check_item(item, ENTRY, ALLOWED)
        self.assertEqual(len(probs), 1)
        self.assertIn("value 400 is not the result", probs[0])

    def test_inputs_must_come_from_the_entrys_facts(self):
        item = dict(self.GOOD, expr="7000000000 / (30 * 86400)", values=[2700])
        self.assertTrue(any("not in the entry's facts: [7000000000.0]" in p for p in D.check_item(item, ENTRY, ALLOWED)))

    def test_unit_constants_and_small_integers_are_free(self):
        item = {"values": [4000], "from": ["s2"], "expr": "500 * 8", "reason": "bytes to bits"}
        self.assertEqual(D.check_item(item, ENTRY, ALLOWED), [])
        item = {"values": [43200], "from": ["s2"], "expr": "500 * 24 * 3600 / 1000", "reason": "x"}
        self.assertEqual(D.check_item(item, ENTRY, ALLOWED), [])

    def test_from_must_name_cited_sentences(self):
        item = dict(self.GOOD, **{"from": ["s1", "zzz"]})
        self.assertTrue(any("does not cite" in p for p in D.check_item(item, ENTRY, ALLOWED)))
        self.assertTrue(any("needs `from`" in p for p in D.check_item(dict(self.GOOD, **{"from": []}), ENTRY, ALLOWED)))

    def test_missing_pieces(self):
        self.assertTrue(any("needs `values`" in p for p in D.check_item({"from": ["s1"], "expr": "1+1"}, ENTRY, ALLOWED)))
        self.assertTrue(any("needs `expr`" in p for p in D.check_item({"values": [2], "from": ["s1"]}, ENTRY, ALLOWED)))
        self.assertTrue(D.check_item({"values": ["x"], "from": ["s1"], "expr": "1+1"}, ENTRY, ALLOWED))

    def test_a_declaration_that_fails_waives_nothing(self):
        bad = dict(self.GOOD, values=[999])
        vals, probs = D.waived([bad, {"values": [4000], "from": ["s2"], "expr": "500 * 8"}], ENTRY, ALLOWED)
        self.assertEqual(vals, {4000.0})
        self.assertEqual(len(probs), 1)

    def test_cited_sids(self):
        self.assertEqual(D.cited_sids(ENTRY), {"s0", "s1", "s2"})


class CheckerIntegrationTest(unittest.TestCase):
    """The writer's number check accepts a derived value only when the declaration holds."""

    def test_publish_check_numbers(self):
        from coursesmith.publish import check as PC
        from coursesmith.util import write_json, write_jsonl
        from .helpers import make_subject, temp_root
        text = "About 386 new URLs arrive each second, against 500 bytes each."
        for derived_decl, expect_problem in (
                ({"d-q-001": [{"values": [386], "from": ["s1"], "expr": "1000000000 / (30 * 86400)"}]}, False),
                ({}, True),
                ({"d-q-001": [{"values": [386], "from": ["s1"], "expr": "9000000000 / (30 * 86400)"}]}, True)):
            with temp_root():
                s = make_subject("d", "slug: d\ntitle: D\nshort: d\nedition: {questions: false}\n")
                e = dict(ENTRY, weight="Major", level="Intermediate", part="Q", chapter="C", selected=True, sources=[],
                         prerequisites=[], id="d-q-001")
                write_jsonl(s.entries_dir / "c.jsonl", [e])
                write_json(s.order_path, {"order": ["d-q-001"], "locked": True})
                write_json(s.prose_path, {"entries": {"d-q-001": {"title": "URL shortener", "text": text}}, "openers": {},
                                          "reviews": {}, "glossary": {}, "questions": {}, "derived": derived_decl})
                write_json(s.dir / "units.json", {"units": [{"n": 1, "entries": ["d-q-001"], "terms": [], "question": None,
                                                              "openers": [], "reviews": []}], "n_units": 1})
                problems, _ = PC.run(s, log=lambda *a: None)
                bad = [p for p in problems if "numbers not in its facts" in p or "derived number" in p]
                self.assertEqual(bool(bad), expect_problem, (derived_decl, problems))

    def test_waivers_json_can_carry_derived_numbers_too(self):
        from coursesmith.publish import check as PC
        from coursesmith.util import write_json, write_jsonl
        from .helpers import make_subject, temp_root
        with temp_root():
            s = make_subject("d", "slug: d\ntitle: D\nshort: d\n")
            e = dict(ENTRY, weight="Major", level="Intermediate", part="Q", chapter="C", selected=True, sources=[],
                     prerequisites=[], id="d-q-001")
            write_jsonl(s.entries_dir / "c.jsonl", [e])
            write_json(s.order_path, {"order": ["d-q-001"], "locked": True})
            write_json(s.prose_path, {"entries": {"d-q-001": {"title": "URL shortener", "text": "About 386 per second."}},
                                      "openers": {}, "reviews": {}, "glossary": {}, "questions": {}})
            write_json(s.dir / "units.json", {"units": [{"n": 1, "entries": ["d-q-001"], "terms": [], "question": None,
                                                          "openers": [], "reviews": []}], "n_units": 1})
            write_json(s.dir / "waivers.json", {"derived": {"d-q-001": [
                {"values": [386], "from": ["s1"], "expr": "1000000000 / (30 * 86400)", "reason": "r"}]}})
            problems, _ = PC.run(s, log=lambda *a: None)
            self.assertEqual([p for p in problems if "numbers not in its facts" in p or "derived" in p], [])


if __name__ == "__main__":
    unittest.main()
