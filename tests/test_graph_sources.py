import json
import unittest

from coursesmith.consolidate import dossier
from coursesmith.crawl.store import Store, append_ledger
from coursesmith.extract import sentences as SN
from coursesmith.graph import build as G
from coursesmith.graph.build import find_mentions, mention_phrases

from .helpers import make_subject, temp_root

LEAD = "A cache keeps copies of recently used data so that later requests are served faster."


def page(store, key, text, source=None, tier=None, links=(), lead=(), name=None, version="v1", revid=None, **extra):
    rec = {"title": key, "url": f"https://x/{key}", "revid": revid, "html": None, "citations": [],
           "body_links": list(links), "lead_links": list(lead), "categories": [], "name": name or key}
    if source:
        rec.update({"source": source, "tier": tier or "curated", "version": version})
    rec.update(extra)
    store.save_page(rec, text)


YAML = """slug: tiny
title: Tiny
seeds: ["gh>o/r/README.md"]
sources:
  - {name: prim, adapter: github, repo: o/r, include: ["**/*.md"], tier: curated}
  - {name: solo, adapter: github, repo: p/q, include: ["**/*.md"], tier: curated, chapter_hint: c-misc}
frame:
  parts:
    - {key: found, title: Foundations, foundations: true}
    - {key: q, title: Questions}
scope: {threshold: 5}
"""
FRAME = """parts:
  - {key: found, title: Foundations, chapters: [{key: c-found, title: Basics, seeds: ["Consistent hashing"]}]}
  - key: q
    title: Questions
    question: true
    chapters:
      - {key: c-url, title: Design a URL shortener, question: true, seeds: ["gh>o/r/README.md"]}
      - {key: c-misc, title: Other, seeds: []}
"""


def setup(mention_fallback=True):
    subj = make_subject("tiny", YAML + ("" if mention_fallback else "graph: {mention_fallback: false}\n"))
    subj.frame_path.write_text(FRAME, encoding="utf-8")
    st = Store()
    page(st, "Consistent hashing", "# Consistent hashing\nConsistent hashing maps keys to servers on a ring.\n", revid=1)
    page(st, "gh>o/r/README.md", f"# URL shortener\n{LEAD}\nThe design uses consistent hashing to spread keys.\n",
         source="prim", links=["gh>o/r/notes.md"], name="URL shortener (prim)")
    page(st, "gh>o/r/notes.md", "# Notes\nThese notes cover the write path of the service in detail here.\n",
         source="prim", name="Notes (prim)")
    page(st, "gh>p/q/solo.md", "# Solo\nThis page names nothing else and links nowhere at all today.\n",
         source="solo", name="Solo (solo)")
    for t in ("Consistent hashing", "gh>o/r/README.md", "gh>o/r/notes.md", "gh>p/q/solo.md"):
        append_ledger(subj, {"title": t, "url": "u", "status": "fetched"})
    return subj, st


class MentionHelpersTest(unittest.TestCase):
    NODES = {"Consistent hashing": {"source": "wikipedia"}, "Cache (computing)": {"source": "wikipedia"},
             "Hash": {"source": "wikipedia"}, "gh>a/b.md": {"source": "p", "name": "URL shortener (prim)"},
             "rfc>9110": {"source": "rfcs", "name": "RFC 9110: HTTP Semantics"}}

    def test_phrases_need_two_words_or_eight_chars_and_drop_parentheticals(self):
        ph = mention_phrases(self.NODES, set(self.NODES))
        self.assertEqual(ph["consistent hashing"], "Consistent hashing")
        self.assertEqual(ph["url shortener"], "gh>a/b.md")
        self.assertEqual(ph["http semantics"], "rfc>9110")
        self.assertNotIn("hash", ph)  # one short word
        self.assertNotIn("cache", ph)  # the parenthetical goes and what is left is a short word

    def test_ambiguous_phrase_is_dropped(self):
        nodes = {"A": {"source": "wikipedia"}, "Load balancing (computing)": {"source": "wikipedia"},
                 "Load balancing (electrical)": {"source": "wikipedia"}}
        self.assertNotIn("load balancing", mention_phrases(nodes, set(nodes)))

    def test_find_mentions_longest_first_whole_words(self):
        ph = {"consistent hashing": "CH", "hashing": "H", "url shortener": "US"}
        got = find_mentions("We use Consistent Hashing, then a URL shortener. Hashing alone.", ph, "own")
        self.assertEqual(got, {"CH": "consistent hashing", "US": "url shortener", "H": "hashing"})
        self.assertEqual(find_mentions("consistent hashing", {"consistent hashing": "own"}, "own"), {})
        self.assertEqual(find_mentions("inconsistent hashingx", ph, "own"), {})


class GraphSourcesTest(unittest.TestCase):
    def build(self, **kw):
        subj, st = setup(**kw)
        return subj, G.build(subj, log=lambda *a: None)

    def test_nodes_carry_source_tier_and_bonus(self):
        with temp_root():
            subj, g = self.build()
            n = g["nodes"]["gh>o/r/README.md"]
            self.assertEqual((n["source"], n["tier"], n["version"]), ("prim", "curated", "v1"))
            self.assertEqual(g["nodes"]["Consistent hashing"]["source"], "wikipedia")
            self.assertTrue(n["in_scope"])
            wiki_imp = g["nodes"]["Consistent hashing"]["importance"]
            self.assertGreaterEqual(g["nodes"]["gh>o/r/notes.md"]["importance"], 1 + 0)  # curated bonus
            self.assertEqual(wiki_imp, 0)

    def test_title_mention_edge_and_same_source_edges(self):
        with temp_root():
            subj, g = self.build()
            edges = {(a, b): w for a, b, w in g["edges"]}
            self.assertEqual(g["nodes"]["gh>o/r/README.md"]["mentions"], {"Consistent hashing": "consistent hashing"})
            # a lone 0.5 mention is below the 1.0 edge cutoff: it only adds to chapter scoring
            self.assertNotIn(("gh>o/r/README.md", "Consistent hashing"), edges)
            self.assertEqual(edges[("gh>o/r/README.md", "gh>o/r/notes.md")], 1.5)  # a body link plus same source

    def test_mention_fallback_can_be_switched_off(self):
        with temp_root():
            subj, g = self.build(mention_fallback=False)
            self.assertNotIn("mentions", g["nodes"]["gh>o/r/README.md"])

    def test_chapter_assignment_and_hint(self):
        with temp_root():
            subj, g = self.build()
            self.assertEqual(g["nodes"]["gh>o/r/README.md"]["chapter"], "c-url")  # a seed keeps its chapter
            self.assertEqual(g["nodes"]["gh>o/r/notes.md"]["chapter"], "c-url")  # tied to the seed by a link
            self.assertEqual(g["nodes"]["gh>p/q/solo.md"]["chapter"], "c-misc")  # no edge to any seed: the hint

    def test_foundations_key_comes_from_the_frame(self):
        with temp_root():
            subj, _ = setup()
            self.assertEqual(G.foundations_key(subj), "found")
        with temp_root():
            subj = make_subject("t2", "slug: t2\nframe:\n  parts:\n    - {key: basics, title: B, foundations: true}\n")
            self.assertEqual(G.foundations_key(subj), "basics")
        with temp_root():
            self.assertEqual(G.foundations_key(make_subject("t3")), "found")


class DossierSourcesTest(unittest.TestCase):
    def dossier(self):
        subj, st = setup()
        G.build(subj, log=lambda *a: None)
        SN.build(subj, st, log=lambda *a: None)
        dossier.build(subj, "c-url", log=lambda *a: None)
        return "\n".join(p.read_text() for p in sorted((subj.dossier_dir / "c-url").glob("chunk_*.md")))

    def test_question_chapter_dossier(self):
        with temp_root():
            d = self.dossier()
            self.assertIn("QUESTION: Design a URL shortener", d)
            self.assertIn('exactly one entry of kind "Worked example"', d)

    def test_non_wikipedia_header_names_source_tier_version_license(self):
        with temp_root():
            d = self.dossier()
            head = next(l for l in d.splitlines() if l.startswith("## gh>o/r/README.md"))
            self.assertIn('"URL shortener (prim)"', head)
            self.assertIn("prim · curated", head)
            self.assertIn("in-scope inlinks", head)

    def test_also_on_line_from_a_title_mention(self):
        with temp_root():
            subj, st = setup()
            G.build(subj, log=lambda *a: None)
            SN.build(subj, st, log=lambda *a: None)
            dossier.build(subj, "c-found", log=lambda *a: None)
            d = "\n".join(p.read_text() for p in (subj.dossier_dir / "c-found").glob("chunk_*.md"))
            self.assertIn("also on: ", d)
            self.assertIn("The design uses consistent hashing to spread keys.", d)

    def test_wikipedia_header_is_unchanged(self):
        with temp_root():
            d = self.dossier()
            self.assertEqual(sum(1 for l in d.splitlines() if l.startswith("## ")), 2)


if __name__ == "__main__":
    unittest.main()
