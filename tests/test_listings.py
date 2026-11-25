"""Code listings: DocFX code references, indexing and anchoring, what an entry may place, the audit, render."""
import unittest

from coursesmith import listings as LS
from coursesmith.extract import sentences as SN
from coursesmith.text import docfx as D
from coursesmith.util import write_json, write_jsonl
from coursesmith.write import render as R
from coursesmith.write import skeleton as K

from .helpers import make_subject, temp_root

FILES = {"d/snippets/p.cs": "using X;\n// <one>\nvar a = 1;\n    // <inner>\n    Foo();\n    // </inner>\n// </one>\nclass B{}\n",
         "d/snippets/q.vb": "Dim x", "samples/r.cs": "#region Snip\nint z = 2;\n#endregion\n"}
MD = """# T

The service reads a value.

```csharp
int x = 1;
  y();
```

:::code language="csharp" source="snippets/p.cs" id="one":::

[!code-csharp[n](snippets/p.cs#L7-L8)]

:::code language="vb" source="snippets/q.vb":::

[!code-csharp[n](~/samples/r.cs#Snip)]
"""


class Extract(unittest.TestCase):
    def test_all_three_forms_become_markers_and_snippets_are_cut(self):
        L = D.Listings(drop=["vb"], read=lambda p: FILES.get(p[2:] if p.startswith("~/") else "d/" + p))
        text = D.clean(MD, L)
        self.assertEqual(text.count("⟦L"), 4)
        self.assertEqual([x["code"] for x in L.items],
                         ["int x = 1;\n  y();", "var a = 1;\n    Foo();", "class B{}", "int z = 2;"])
        self.assertEqual(L.skipped["language"], 1)

    def test_without_a_collector_code_is_still_dropped(self):
        self.assertNotIn("⟦L", D.clean(MD))

    def test_long_and_missing_blocks_are_skipped(self):
        L = D.Listings(max_lines=2, read=lambda p: None)
        D.clean("# T\n\n```\na\nb\nc\n```\n\n:::code language=\"csharp\" source=\"x.cs\":::\n", L)
        self.assertEqual((L.items, L.skipped["long"], L.skipped["missing"]), ([], 1, 1))


def page(title="gh>o/r/a.md"):
    text = "# T\n\nThe host builds a service. It then runs.\n\n⟦L0⟧\n\n## More\n\nLater text is here today.\n\n⟦L1⟧\n"
    rec = {"title": title, "url": "https://x/a", "revid": None, "source": "github", "version": "abc", "name": "T",
           "listings": [{"n": 0, "lang": "csharp", "code": "var a = 1;", "source": None},
                        {"n": 1, "lang": "csharp", "code": "var b = 2;", "source": None}]}
    return rec, text


class Index(unittest.TestCase):
    def test_marker_does_not_change_sentence_ids_and_anchors_the_code(self):
        with temp_root():
            rec, text = page()
            db = SN.connect()
            SN.index_page(db, type("S", (), {"meta": {}, "canonical": staticmethod(lambda t: t)})(), rec, text)
            rows = {r[3]: r[0] for r in SN.page_sentences(db, rec["title"])}
            self.assertEqual(len(rows), 3)
            first = SN.page_listings(db, rec["title"])
            self.assertEqual(first[0][3], rows["It then runs."])
            self.assertEqual(first[1][2], "More")
            self.assertEqual(SN.sent_id(rec["title"], "It then runs."), rows["It then runs."])
            self.assertEqual(SN.listing_lookup(db, [first[0][0]])[first[0][0]]["code"], "var a = 1;")


class Writing(unittest.TestCase):
    def setup(self):
        s = make_subject("tiny", "title: Tiny\nshort: tiny\nedition: {paragraphs: true}\ncode: {per_entry: 1}\n")
        rec, text = page()
        db = SN.connect()
        SN.index_page(db, type("S", (), {"meta": {}, "canonical": staticmethod(lambda t: t)})(), rec, text)
        db.commit()
        ids = {r[3]: r[0] for r in SN.page_sentences(db, rec["title"])}
        codes = [r[0] for r in SN.page_listings(db, rec["title"])]
        db.close()
        e = {"id": "tiny-a", "title": "Host", "kind": "Concept", "weight": "Major", "level": "Beginner",
             "part": "P", "chapter": "C", "selected": True,
             "definition": {"text": "The host builds a service.", "sent_ids": [ids["The host builds a service."]]},
             "facts": [{"text": "It then runs.", "sent_ids": [ids["It then runs."]]}],
             "sources": [{"title": rec["title"], "sent_ids": list(ids.values())}]}
        write_jsonl(s.entries_dir / "core.jsonl", [e])
        write_json(s.order_path, {"order": ["tiny-a"], "locked": True})
        return s, e, codes

    def test_only_listings_near_cited_sentences_are_offered(self):
        with temp_root():
            s, e, codes = self.setup()
            got = LS.available(s, e)
            self.assertEqual([x["id"] for x in got], [codes[0]])      # the second sits in a section it does not cite
            packet = "\n".join(K._entry_block(e, {}, s, None, __import__("coursesmith.extract.sentences", fromlist=["x"]).connect()))
            self.assertIn(f"LISTING {codes[0]} | csharp | 1 lines", packet)

    def test_audit_and_render(self):
        with temp_root():
            s, e, codes = self.setup()
            ok = {"entries": {"tiny-a": {"text": f"The host builds a service.\n\n{{{{code:{codes[0]}}}}}"}}}
            self.assertEqual(LS.audit(s, ok, {"tiny-a": e}, ["tiny-a"])[0], [])
            for text, why in [(f"Text {{{{code:{codes[0]}}}}} inline", "paragraph"),
                              (f"{{{{code:{codes[1]}}}}}", "may place"),
                              (f"{{{{code:{codes[0]}}}}}\n\n{{{{code:{codes[0]}}}}}", "twice")]:
                bad = {"entries": {"tiny-a": {"text": text}}}
                self.assertTrue(any(why in p for p in LS.audit(s, bad, {"tiny-a": e}, ["tiny-a"])[0]), why)
            self.assertEqual(LS.strip(ok["entries"]["tiny-a"]["text"]), "The host builds a service.")
            md = "\n".join(R._text_md(ok["entries"]["tiny-a"]["text"], {}))
            self.assertIn("```csharp\n  var a = 1;\n  ```", md)


if __name__ == "__main__":
    unittest.main()
