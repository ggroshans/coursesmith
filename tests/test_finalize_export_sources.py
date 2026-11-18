import json
import unittest
from types import SimpleNamespace

from coursesmith.consolidate import finalize as F
from coursesmith.publish import attribution as A
from coursesmith.publish.attribution import norm_source, source_rows, summarize
from coursesmith.sources.base import best_tier
from coursesmith.sources.registry import Registry

REG = Registry([
    {"name": "primer", "adapter": "github", "repo": "o/r", "tier": "curated", "license": {"name": "CC BY 4.0"}},
    {"name": "nc", "adapter": "github", "repo": "n/c", "tier": "curated", "license": {"name": "CC BY-NC-ND 4.0"}},
    {"name": "rfcs", "adapter": "rfc", "ids": [2119]},
])
WIKI = {"title": "Cache (computing)", "url": "https://en.wikipedia.org/wiki/Cache_(computing)", "revid": 123, "sent_ids": ["a1"]}
PRIMER = {"title": "URL shortener (primer)", "key": "gh>o/r/README.md", "source": "primer", "version": "ae9bbd7b02d9",
          "url": "https://github.com/o/r/blob/ae9bbd7/README.md", "revid": None, "sent_ids": ["b1", "b2"]}
NC = {"title": "Design (nc)", "key": "gh>n/c/x.md", "source": "nc", "version": "ff00ff00ff00",
      "url": "https://github.com/n/c/blob/ff00/x.md", "revid": None, "sent_ids": ["c1"],
      "license": {"name": "CC BY-NC-ND 4.0", "class": "cc-by-nc-nd"}}
RFC = {"title": "RFC 2119: Key words", "key": "rfc>2119", "source": "rfcs", "version": "March 1997",
       "url": "https://www.rfc-editor.org/rfc/rfc2119", "revid": None, "sent_ids": ["d1"]}


class SourceItemTest(unittest.TestCase):
    def test_wikipedia_item_is_identical_apart_from_new_keys(self):
        row = {"title": "Cache (computing)", "url": WIKI["url"], "revid": 123, "source": "wikipedia", "version": "123",
               "license": None, "name": "Cache (computing)"}
        s = F._source("Cache (computing)", ["a1"], row)
        self.assertEqual({k: s[k] for k in ("title", "url", "revid", "sent_ids")},
                         {"title": "Cache (computing)", "url": WIKI["url"], "revid": 123, "sent_ids": ["a1"]})
        self.assertEqual((s["key"], s["source"], s["version"]), ("Cache (computing)", "wikipedia", "123"))
        self.assertNotIn("license", s)

    def test_other_source_item_has_human_title_and_key(self):
        row = {"title": "gh>o/r/README.md", "name": "URL shortener (primer)", "url": "u", "revid": None,
               "source": "primer", "version": "abc", "license": {"name": "CC BY 4.0"}}
        s = F._source("gh>o/r/README.md", ["b1"], row)
        self.assertEqual((s["title"], s["key"], s["source"]), ("URL shortener (primer)", "gh>o/r/README.md", "primer"))
        self.assertEqual(s["license"]["name"], "CC BY 4.0")

    def test_norm_source_fills_old_items(self):
        n = norm_source(WIKI)
        self.assertEqual((n["key"], n["source"], n["version"]), ("Cache (computing)", "wikipedia", "123"))


class SourceTierTest(unittest.TestCase):
    def e(self, *srcs, tier=None):
        return {"sources": list(srcs), **({"source_tier": tier} if tier else {})}

    def test_wikipedia_only_stays_wikipedia(self):
        self.assertEqual(F.source_tier(self.e(WIKI), REG), "wikipedia")
        self.assertEqual(F.source_tier(self.e(WIKI), None), "wikipedia")

    def test_best_tier_among_cited_sources(self):
        self.assertEqual(F.source_tier(self.e(WIKI, PRIMER), REG), "reference")
        self.assertEqual(F.source_tier(self.e(PRIMER), REG), "curated")
        self.assertEqual(F.source_tier(self.e(PRIMER, RFC), REG), "standard")

    def test_primary_from_verification_is_kept(self):
        self.assertEqual(F.source_tier(self.e(PRIMER, tier="primary"), REG), "primary")

    def test_stale_tier_is_recomputed(self):
        self.assertEqual(F.source_tier(self.e(PRIMER, RFC, tier="curated"), REG), "standard")


class ValidateTest(unittest.TestCase):
    def entry(self, **kw):
        e = {"title": "T", "kind": "Concept", "weight": "Major", "level": "Intermediate",
             "facts": [{"text": "x y z", "sent_ids": ["a"]}, {"text": "q r s", "sent_ids": ["b"]}]}
        e.update(kw)
        return e

    def test_new_kinds_and_fact_caps(self):
        many = [{"text": f"fact {i}", "sent_ids": ["a"]} for i in range(12)]
        e = self.entry(kind="Worked example", facts=many)
        self.assertTrue(any("12 facts (want 2-8)" in p for p in F.validate(e, {"a"}, set())))
        self.assertEqual(F.validate(e, {"a"}, set(), {"Worked example": 16}), [])
        self.assertTrue(any("(want 2-16)" in p for p in F.validate(self.entry(kind="Worked example", facts=many[:1]), {"a"}, set(), {"Worked example": 16})))

    def test_fact_cap_helper(self):
        self.assertEqual(F._fact_cap({"weight": "Minor", "kind": "Concept"}), 4)
        self.assertEqual(F._fact_cap({"weight": "Major", "kind": "Worked example"}, {"Worked example": 16}), 16)
        self.assertEqual(F._fact_cap({"weight": "Major", "kind": "Concept"}, {"Worked example": 16}), 8)

    def test_article_must_be_allowed(self):
        e = self.entry(article="gh>o/r/README.md")
        crawled = {"gh>o/r/README.md"}
        self.assertEqual(F.validate(e, {"a", "b"}, crawled, None, REG.allowed), [])
        e2 = self.entry(article="gh>z/z/x.md")
        self.assertTrue(any("was not crawled" in p for p in F.validate(e2, {"a", "b"}, crawled, None, REG.allowed)))
        e3 = self.entry(article="gh>z/z/x.md")
        self.assertTrue(any("outside the sources" in p for p in F.validate(e3, {"a", "b"}, {"gh>z/z/x.md"}, None, REG.allowed)))

    def test_default_validate_signature_still_works(self):
        self.assertEqual(F.validate(self.entry(), {"a", "b"}, set()), [])


class DeriveTest(unittest.TestCase):
    def test_curriculum_tests_for_vetted_and_question_entries(self):
        e = {"kind": "Worked example", "article": "rfc>2119", "facts": [{"text": "t", "sent_ids": ["d1"]}]}
        found = {"d1": {"title": "rfc>2119", "name": "RFC 2119: Key words", "url": "u", "revid": None,
                        "source": "rfcs", "version": "March 1997", "license": None}}

        class DB:
            def execute(self, *a):
                return SimpleNamespace(fetchone=lambda: None)
        nodes = {"rfc>2119": {"source": "rfcs", "tier": "standard"}}
        F._derive(e, found, nodes, DB(), REG)
        self.assertIn("vetted source", e["curriculum"])
        self.assertIn("question entry", e["curriculum"])
        self.assertIn("own article", e["curriculum"])
        self.assertEqual(e["source_tier"], "standard")
        self.assertEqual(e["sources"][0]["title"], "RFC 2119: Key words")
        self.assertEqual(e["sources"][0]["key"], "rfc>2119")


class AttributionTest(unittest.TestCase):
    def rows(self, *srcs):
        return source_rows([{"id": "e1", "sources": list(srcs)}], REG)

    def test_wikipedia_only_keeps_the_exact_old_license(self):
        s = summarize(self.rows(WIKI), REG)
        self.assertTrue(s["wikipedia_only"])
        self.assertEqual(s["name"], "CC BY-SA 4.0")
        self.assertEqual(s["url"], "https://creativecommons.org/licenses/by-sa/4.0/")
        self.assertEqual(s["text"], A.WIKIPEDIA_TEXT)

    def test_rows(self):
        rows = self.rows(WIKI, PRIMER, RFC)
        by = {r["key"]: r for r in rows}
        self.assertEqual(by["Cache (computing)"]["version_label"], "revision 123")
        self.assertEqual(by["Cache (computing)"]["tier"], "reference")
        self.assertEqual(by["gh>o/r/README.md"]["version_label"], "commit ae9bbd7")
        self.assertEqual(by["gh>o/r/README.md"]["license_class"], "cc-by")
        self.assertEqual(by["gh>o/r/README.md"]["n_sentences"], 2)
        self.assertEqual(by["rfc>2119"]["license_class"], "ietf-trust")
        self.assertEqual(by["rfc>2119"]["version_label"], "published March 1997")

    def test_mixed_open_licenses(self):
        s = summarize(self.rows(WIKI, PRIMER, RFC), REG)
        self.assertFalse(s["wikipedia_only"])
        self.assertEqual(s["name"], "Mixed open licenses, share-alike (see sources)")
        self.assertEqual(s["restricted"], [])
        self.assertIn("CC BY 4.0: primer.", s["text"])

    def test_non_public_source_makes_it_personal_use(self):
        s = summarize(self.rows(WIKI, NC), REG)
        self.assertEqual(s["name"], "Personal use only (mixed sources)")
        self.assertEqual(s["restricted"], ["cc-by-nc-nd"])
        self.assertIn("personal reading only", s["text"])

    def test_distribution_gate(self):
        entries = [{"id": "e1", "sources": [WIKI, NC]}, {"id": "e2", "sources": [PRIMER]}]
        self.assertEqual(A.distribution_problems(entries, REG, "personal"), [])
        probs = A.distribution_problems(entries, REG, "public")
        self.assertEqual(len(probs), 1)
        self.assertIn("e1", probs[0])
        self.assertIn("does not allow public distribution", probs[0])

    def test_unknown_license_is_not_public(self):
        reg = Registry([{"name": "x", "adapter": "github", "repo": "u/v"}])
        probs = A.distribution_problems([{"id": "e", "sources": [{"title": "T", "key": "gh>u/v/a.md", "url": "u",
                                                                  "source": "x", "sent_ids": []}]}], reg, "public")
        self.assertEqual(len(probs), 1)


if __name__ == "__main__":
    unittest.main()
