import json
import unittest

from coursesmith.crawl.store import Store
from coursesmith.extract import sentences as SN
from coursesmith.publish import export
from coursesmith.publish.edition import Edition
from coursesmith.util import write_json, write_jsonl

from .helpers import make_subject, temp_root

YAML = """slug: mix
title: Mixed
short: mix
sources:
  - {name: primer, adapter: github, repo: o/r, tier: curated, license: {name: CC BY 4.0}}
  - {name: rfcs, adapter: rfc, ids: [2119]}
"""
KEY_GH, KEY_RFC = "gh>o/r/README.md", "rfc>2119"
S_WIKI = SN.sent_id("Cache", "A cache keeps copies of data so that it can be served faster.")
S_GH = SN.sent_id(KEY_GH, "A URL shortener maps a long URL to a short code.")
S_RFC = SN.sent_id(KEY_RFC, "The word MUST means an absolute requirement of the specification.")


def sources_for(*which):
    all_ = {
        "wiki": {"title": "Cache", "url": "https://en.wikipedia.org/wiki/Cache", "revid": 7, "sent_ids": [S_WIKI]},
        "gh": {"title": "URL shortener (primer)", "key": KEY_GH, "source": "primer", "version": "ae9bbd7b02d9",
               "url": "https://github.com/o/r/blob/ae9bbd7b02d9/README.md", "revid": None, "sent_ids": [S_GH],
               "license": {"name": "CC BY 4.0", "class": "cc-by"}},
        "rfc": {"title": "RFC 2119: Key words", "key": KEY_RFC, "source": "rfcs", "version": "March 1997",
                "url": "https://www.rfc-editor.org/rfc/rfc2119", "revid": None, "sent_ids": [S_RFC]},
    }
    return [all_[w] for w in which]


def build(yaml_text, entry_sources):
    subj = make_subject("mix", yaml_text)
    st = Store()
    st.save_page({"title": KEY_GH, "url": "u", "revid": None, "version": "ae9bbd7b02d9", "source": "primer",
                  "retrieved": "2026-11-18T10:00:00+00:00"}, "# x\n")
    ents = []
    for n, srcs in enumerate(entry_sources, 1):
        sids = [s["sent_ids"][0] for s in srcs]
        ents.append({"id": f"mix-a-{n:03d}", "title": f"Entry {n}", "kind": "Concept", "weight": "Major",
                     "level": "Foundational", "part": "Basics", "chapter": "Ch", "selected": True, "score": 1,
                     "definition": {"text": "d", "sent_ids": [sids[0]]},
                     "facts": [{"text": "f", "sent_ids": [s]} for s in sids], "sources": srcs})
    write_jsonl(subj.dir / "entries" / "ch.jsonl", ents)
    ids = [e["id"] for e in ents]
    write_json(subj.dir / "order.json", {"order": ids, "locked": True})
    write_json(subj.dir / "output" / "prose.json", {"entries": {i: {"title": f"Entry {k}", "text": "Some prose."}
                                                                for k, i in enumerate(ids, 1)},
                                                    "openers": {}, "reviews": {}, "glossary": {}, "questions": {},
                                                    "closing": None})
    write_json(subj.dir / "units.json", {"units": [{"n": 1, "entries": ids, "leaf": None, "openers": [], "reviews": [],
                                                    "terms": [], "question": None, "last_time": None,
                                                    "answer_prev": None, "next": None}], "built": "2026-11-18T00:00Z"})
    db = SN.connect()
    db.execute("INSERT INTO pages (title, url, revid) VALUES ('Cache','https://en.wikipedia.org/wiki/Cache',7)")
    db.execute("INSERT INTO sentences (sent_id,title,revid,section,idx,sentence) VALUES (?, 'Cache', 7, '', 0, ?)",
               (S_WIKI, "A cache keeps copies of data so that it can be served faster."))
    db.execute("INSERT INTO pages (title,url,revid,source,version,license,name) VALUES (?,?,NULL,'primer','ae9bbd7b02d9',?,?)",
               (KEY_GH, "https://github.com/o/r/blob/ae9bbd7b02d9/README.md",
                json.dumps({"name": "CC BY 4.0", "class": "cc-by"}), "URL shortener (primer)"))
    db.execute("INSERT INTO sentences (sent_id,title,revid,section,idx,sentence) VALUES (?, ?, NULL, '', 0, ?)",
               (S_GH, KEY_GH, "A URL shortener maps a long URL to a short code."))
    db.execute("INSERT INTO pages (title,url,revid,source,version,name) VALUES (?,?,NULL,'rfcs','March 1997','RFC 2119: Key words')",
               (KEY_RFC, "https://www.rfc-editor.org/rfc/rfc2119"))
    db.execute("INSERT INTO sentences (sent_id,title,revid,section,idx,sentence) VALUES (?, ?, NULL, '', 0, ?)",
               (S_RFC, KEY_RFC, "The word MUST means an absolute requirement of the specification."))
    db.commit()
    db.close()
    return subj


class MixedExportTest(unittest.TestCase):
    def doc(self):
        subj = build(YAML, [sources_for("wiki", "gh"), sources_for("rfc")])
        return export.export(subj, strict=True, log=lambda *a: None)

    def test_format_and_version(self):
        with temp_root():
            d = self.doc()
            self.assertEqual((d["format"], d["version"]), ("wikicourse-course", 2))
            self.assertEqual(d["subject"]["distribution"], "personal")
            self.assertEqual(d["subject"]["course_type"], "survey")
            self.assertEqual(d["subject"]["kinds"], ["Concept"])

    def test_pages_are_keyed_by_key_with_source_details(self):
        with temp_root():
            p = self.doc()["license"]["pages"]
            self.assertEqual(set(p), {"Cache", KEY_GH, KEY_RFC})
            self.assertIn("oldid=7", p["Cache"]["permalink"])  # the old fields are unchanged
            self.assertEqual(p["Cache"]["url"], "https://en.wikipedia.org/wiki/Cache")
            gh = p[KEY_GH]
            self.assertEqual((gh["name"], gh["source"], gh["version_label"], gh["license"], gh["license_class"], gh["tier"]),
                             ("URL shortener (primer)", "primer", "commit ae9bbd7", "CC BY 4.0", "cc-by", "curated"))
            self.assertEqual(p[KEY_RFC]["tier"], "standard")

    def test_license_sources_list_and_derived_name(self):
        with temp_root():
            lic = self.doc()["license"]
            self.assertEqual({s["key"] for s in lic["sources"]}, {"Cache", KEY_GH, KEY_RFC})
            gh = next(s for s in lic["sources"] if s["key"] == KEY_GH)
            self.assertEqual((gh["n_sentences"], gh["retrieved"]), (1, "2026-11-18T10:00:00+00:00"))
            self.assertEqual(lic["name"], "Mixed open licenses, share-alike (see sources)")
            self.assertIn("CC BY 4.0: primer.", lic["text"])

    def test_entry_sources_carry_key_and_source(self):
        with temp_root():
            d = self.doc()
            s = d["entries"][0]["sources"]
            self.assertEqual([x["key"] for x in s], ["Cache", KEY_GH])
            self.assertEqual(s[0]["source"], "wikipedia")  # filled in for the old-style item
            self.assertEqual(s[0]["version"], "7")
            self.assertEqual(s[1]["title"], "URL shortener (primer)")

    def test_cited_sentences_carry_key_source_version(self):
        with temp_root():
            d = self.doc()
            self.assertEqual({k: d["sentences"][S_GH][k] for k in ("key", "source", "version")},
                             {"key": KEY_GH, "source": "primer", "version": "ae9bbd7b02d9"})
            self.assertEqual(d["sentences"][S_WIKI]["source"], "wikipedia")
            self.assertEqual(d["sentences"][S_WIKI]["version"], "7")
            self.assertEqual(d["sentences"][S_WIKI]["title"], "Cache")

    def test_wikipedia_only_license_is_unchanged(self):
        with temp_root():
            subj = build(YAML, [sources_for("wiki")])
            lic = export.export(subj, log=lambda *a: None)["license"]
            self.assertEqual(lic["name"], "CC BY-SA 4.0")
            self.assertEqual(lic["url"], "https://creativecommons.org/licenses/by-sa/4.0/")
            self.assertTrue(lic["text"].startswith("Adapted from Wikipedia articles available under"))
            self.assertEqual(set(lic["pages"]["Cache"]), {"url", "revid", "permalink", "name", "source", "version",
                                                          "version_label", "license", "license_class", "tier"})


class EditionTest(unittest.TestCase):
    def test_mixed_attribution_page(self):
        with temp_root():
            subj = build(YAML, [sources_for("wiki", "gh"), sources_for("rfc")])
            ed = Edition(subj)
            html = ed.attribution_html(["mix-a-001", "mix-a-002"])
            self.assertIn("adapted from the sources listed below", html)
            self.assertIn("<b>CC BY 4.0</b>: primer.", html)
            self.assertIn("Wikipedia articles are available under the", html)
            self.assertIn('<a href="https://github.com/o/r/blob/ae9bbd7b02d9/README.md">URL shortener (primer)</a> '
                          "(commit ae9bbd7, retrieved 2026-11-18)", html)
            self.assertIn("(revision 7)", html)
            self.assertIn("(published March 1997)", html)
            self.assertNotIn("for personal reading only", html)
            self.assertEqual(ed.rights, ed.license["name"])
            self.assertEqual(ed.creator, "Wikipedia contributors, primer, rfcs")
            self.assertIn("(a Wikipedia revision, a repository commit", ed._about_html(2))

    def test_wikipedia_only_attribution_wording_is_exactly_the_old_one(self):
        with temp_root():
            subj = build(YAML, [sources_for("wiki")])
            ed = Edition(subj)
            html = ed.attribution_html(["mix-a-001"])
            self.assertIn("The text of this edition is adapted from Wikipedia articles, which are available under the "
                          '<a href="https://creativecommons.org/licenses/by-sa/4.0/">Creative Commons '
                          "Attribution-ShareAlike 4.0 License</a>. Facts were extracted from the revisions listed "
                          "below, consolidated and rewritten; the full list of authors of each article is in its "
                          "page history. This edition is shared under the same license.", html)
            self.assertIn('<a href="https://en.wikipedia.org/wiki/Cache">Cache</a> (revision 7)', html)
            self.assertEqual((ed.creator, ed.rights), ("Wikipedia contributors", "CC BY-SA 4.0"))
            self.assertIn("Every fact traces to a Wikipedia revision", ed._about_html(1))
            self.assertEqual(ed.tagline, "Wikipedia subjects as sourced courses, one unit at a time.")

    def test_restricted_source_says_personal_use(self):
        yaml_text = YAML + "  - {name: nc, adapter: github, repo: n/c, license: {name: CC BY-NC-ND 4.0}}\n"
        with temp_root():
            subj = build(yaml_text, [sources_for("wiki")])
            e = subj.entries_by_id()["mix-a-001"]
            e["sources"].append({"title": "Design (nc)", "key": "gh>n/c/x.md", "source": "nc", "version": "ff", "url": "u",
                                 "revid": None, "sent_ids": [], "license": {"name": "CC BY-NC-ND 4.0", "class": "cc-by-nc-nd"}})
            write_jsonl(subj.dir / "entries" / "ch.jsonl", [e])
            ed = Edition(subj)
            self.assertIn("for personal reading only", ed.attribution_html(["mix-a-001"]))
            self.assertEqual(ed.rights, "Personal use only (mixed sources)")

    def test_tag_line_names_sources_by_their_human_names(self):
        with temp_root():
            subj = build(YAML, [sources_for("wiki", "gh")])
            ed = Edition(subj)
            tl = ed.tag_line(ed.entries["mix-a-001"])
            self.assertIn("Sources: Cache; URL shortener (primer)", tl)

    def test_custom_tagline(self):
        with temp_root():
            subj = build(YAML + "edition: {tagline: 'Answers, one unit a day.'}\n", [sources_for("wiki")])
            self.assertEqual(Edition(subj).tagline, "Answers, one unit a day.")


if __name__ == "__main__":
    unittest.main()
