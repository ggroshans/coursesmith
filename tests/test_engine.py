import unittest

from coursesmith.consolidate.dossier import _chunk
from coursesmith.consolidate.finalize import possible_duplicates, validate
from coursesmith.extract.sentences import sent_id
from coursesmith.verify.verify import compare, quantities


class SentId(unittest.TestCase):
    def test_matches_the_chronicle_formula(self):
        import hashlib
        self.assertEqual(sent_id("Soil", "Soil is a mixture."),
                         hashlib.sha1("Soil\nSoil is a mixture.".encode()).hexdigest()[:12])


class Finalize(unittest.TestCase):
    def entry(self, **kw):
        e = {"title": "Clay", "kind": "Material", "weight": "Major", "level": "Foundational", "article": "Clay",
             "definition": {"text": "Fine particles.", "sent_ids": ["a"]},
             "facts": [{"text": "One.", "sent_ids": ["a"]}, {"text": "Two.", "sent_ids": ["b"]}]}
        e.update(kw)
        return e

    def test_valid(self):
        self.assertEqual(validate(self.entry(), {"a", "b"}, {"Clay"}), [])

    def test_problems(self):
        p = validate(self.entry(kind="Thing", facts=[{"text": "x", "sent_ids": ["zz"]}]), {"a"}, {"Clay"})
        joined = " ".join(p)
        self.assertIn("kind", joined)
        self.assertIn("facts", joined)
        self.assertIn("unknown sent_id zz", joined)

    def test_duplicates(self):
        es = [{"id": "x-001", "title": "Soil texture", "article": "Soil texture"},
              {"id": "x-002", "title": "Texture of soil", "article": "Soil texture"},
              {"id": "x-003", "title": "Sand", "article": "Sand", "distinct_from": []}]
        d = possible_duplicates(es)
        self.assertEqual(len(d), 1)
        self.assertEqual(d[0][4], "same article Soil texture")


class MergeParts(unittest.TestCase):
    def test_joins_parts_and_folds_duplicates(self):
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace

        from coursesmith.consolidate.finalize import merge_parts
        from coursesmith.util import read_jsonl, write_jsonl
        with tempfile.TemporaryDirectory() as tmp:
            s = SimpleNamespace(dir=Path(tmp), draft_dir=Path(tmp) / "entries" / "draft")
            s.draft_dir.mkdir(parents=True)
            fact = lambda t, i: {"text": t, "sent_ids": [i]}
            write_jsonl(s.draft_dir / "ch.part01.jsonl", [
                {"title": "Porosity", "article": "Porosity", "weight": "Minor", "facts": [fact("A.", "1")],
                 "prerequisites": ["Bulk density"]},
                {"title": "Classes", "article": "Soil texture#Classification", "facts": [fact("B.", "2")]}])
            write_jsonl(s.draft_dir / "ch.part05.jsonl", [
                {"title": "Soil porosity", "article": "Porosity", "weight": "Minor",
                 "facts": [fact("A.", "1")] + [fact(f"F{i}.", f"x{i}") for i in range(4)],
                 "prerequisites": ["Void ratio"]},
                {"title": "Triangle", "article": "Soil texture#Classification", "facts": [fact("C.", "3")]}])
            (s.draft_dir / "ch.gaps.part01.md").write_text("- Air-filled porosity\n")
            self.assertEqual(merge_parts(s, "ch", log=lambda *a: None), 3)
            out = read_jsonl(s.draft_dir / "ch.jsonl")
            por = out[0]
            self.assertEqual(len(por["facts"]), 4)  # Minor cap
            self.assertEqual(por["mention_sent_ids"], ["x3"])
            self.assertEqual(por["prerequisites"], ["Bulk density", "Void ratio"])
            self.assertEqual([e["title"] for e in out[1:]], ["Classes", "Triangle"])  # sections stay apart
            self.assertEqual(sorted(p.name for p in s.draft_dir.iterdir()), ["ch.gaps.md", "ch.jsonl"])

    def test_a_part_entry_marked_replaces_takes_the_old_ones_place(self):
        import tempfile
        from pathlib import Path
        from types import SimpleNamespace

        from coursesmith.consolidate.finalize import merge_parts
        from coursesmith.util import read_jsonl, write_jsonl
        with tempfile.TemporaryDirectory() as tmp:
            s = SimpleNamespace(dir=Path(tmp), draft_dir=Path(tmp) / "entries" / "draft")
            s.draft_dir.mkdir(parents=True)
            fact = lambda t, i: {"text": t, "sent_ids": [i]}
            write_jsonl(s.draft_dir / "ch.jsonl", [
                {"title": "Designing Gmail", "article": "gh>x/design-gmail.md", "notes": "thin: no estimates",
                 "distinct_from": ["Email"], "facts": [fact("Old.", "1")]},
                {"title": "SMTP", "facts": [fact("S.", "2")]}])
            write_jsonl(s.draft_dir / "ch.part02.jsonl", [
                {"title": "designing gmail", "article": "gh>x/design-gmail.md", "replaces": True,
                 "facts": [fact("New first.", "3"), fact("Old.", "1")]},
                {"title": "SMTP", "facts": [fact("S.", "2"), fact("T.", "4")]}])
            self.assertEqual(merge_parts(s, "ch", log=lambda *a: None), 2)
            out = read_jsonl(s.draft_dir / "ch.jsonl")
            self.assertEqual([e["title"] for e in out], ["designing gmail", "SMTP"])  # same place in the file
            self.assertEqual([f["text"] for f in out[0]["facts"]], ["New first.", "Old."])
            self.assertNotIn("replaces", out[0])
            self.assertNotIn("notes", out[0])  # the thin note went with the old entry
            self.assertEqual(out[0]["distinct_from"], ["Email"])
            self.assertEqual(len(out[1]["facts"]), 2)  # without the flag, parts still merge


class Verify(unittest.TestCase):
    def test_quantities(self):
        q = quantities("Clay particles are smaller than 0.002 mm; sand ranges 0.05–2 mm; pH 5.5 to 6.5.")
        self.assertIn((0.002, 0.002, "mm"), q)
        self.assertIn((0.05, 2.0, "mm"), q)
        self.assertIn((5.5, 6.5, "pH"), q)

    def test_compare_supports_and_differs(self):
        e = {"title": "Clay", "kind": "Material", "facts": [{"text": "Clay particles are smaller than 0.002 mm."}]}
        self.assertEqual(compare(e, "Clay is defined as particles below 0.002 mm.")["verdict"], "supports")
        self.assertEqual(compare(e, "Clay is defined as particles below 0.004 mm.")["verdict"], "differs")
        self.assertEqual(compare(e, "Sand drains fast.")["verdict"], "no comparable claim")

    def test_classification_authority(self):
        e = {"title": "Vertisols", "kind": "Classification", "facts": []}
        self.assertEqual(compare(e, "The twelve orders include Vertisols and Mollisols.", "authority")["verdict"],
                         "supports")


class Dossier(unittest.TestCase):
    def test_chunks_keep_blocks_whole(self):
        lines = []
        for k in range(6):
            lines += [f"## Page {k}"] + [f"S:{k}{i}" for i in range(99)]
        chunks = _chunk(lines)
        for ch in chunks:
            self.assertTrue(ch[0].startswith("## "))
        self.assertEqual(sum(len(c) for c in chunks), len(lines))


if __name__ == "__main__":
    unittest.main()
