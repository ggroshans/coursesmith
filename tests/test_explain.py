"""Explain mode: settings, the scout and resolve steps, the writer packet, the audit rules, render, export, EPUB."""
import json
import unittest

from coursesmith import config
from coursesmith.explain import audit, items, own_sent_ids, settings, source_entries, text_of
from coursesmith.explain import background as B
from coursesmith.extract import sentences as SN
from coursesmith.publish import export
from coursesmith.publish.edition import Edition
from coursesmith.util import read_json, write_json, write_jsonl
from coursesmith.write import check as C
from coursesmith.write import render as R
from coursesmith.write import skeleton as K

from .fakes import FakeWikiClient, wiki_page
from .helpers import make_subject, temp_root

DI = "Dependency injection is a design pattern in which an object receives the other objects it depends on."
HTTP = "HTTP is an application-layer protocol that clients use to request pages from servers."
FACT = "A service container resolves 3 kinds of lifetime for each registered service."
YAML = """title: Tiny
short: tiny
explain:
  audience: a developer new to this framework
  blurbs: 1
  terms: 2
"""


class Search(FakeWikiClient):
    """A FakeWikiClient that also answers a search query with a canned top hit."""

    def __init__(self, pages, hits):
        super().__init__(pages)
        self.hits, self.searched = hits, []

    def get(self, params):
        self.searched.append(params["srsearch"])
        t = self.hits.get(params["srsearch"])
        return {"query": {"search": [{"title": t}] if t else []}}


def build_course(yaml_text=YAML):
    """A two-entry subject: an entry that assumes dependency injection, and one whose article is HTTP."""
    s = make_subject("tiny", yaml_text)
    sid = {k: SN.sent_id(t, x) for k, (t, x) in {"fact": ("gh>x/y/a.md", FACT)}.items()}
    e = lambda i, title, article, facts: {
        "id": i, "title": title, "kind": "Concept", "weight": "Major", "level": "Intermediate", "part": "Basics",
        "chapter": "Core", "selected": True, "article": article, "definition": {"text": facts[0][0], "sent_ids": [facts[0][1]]},
        "facts": [{"text": t, "sent_ids": [x]} for t, x in facts],
        "sources": [{"title": article, "url": "https://en.wikipedia.org/wiki/" + article, "revid": 7,
                     "sent_ids": [x for _, x in facts]}]}
    write_jsonl(s.entries_dir / "core.jsonl", [
        e("tiny-a", "Service lifetimes", "Services", [(FACT, sid["fact"])]),
        e("tiny-b", "Hypertext transfer", "HTTP", [("HTTP carries requests.", "aaaaaaaaaaaa")])])
    write_json(s.order_path, {"order": ["tiny-a", "tiny-b"], "locked": True})
    return s, sid["fact"]


def index_background(sentences):
    """Put page sentences in the sentence index the way `explain resolve` leaves them."""
    db = SN.connect()
    for title, sents in sentences.items():
        db.execute("INSERT OR REPLACE INTO pages (title, url, revid, n_sentences, source, version, name) "
                   "VALUES (?, ?, 5, ?, NULL, NULL, ?)", (title, f"https://en.wikipedia.org/wiki/{title}", len(sents), title))
        for i, t in enumerate(sents):
            db.execute("INSERT INTO sentences (sent_id, title, revid, section, idx, sentence, is_lead) "
                       "VALUES (?, ?, 5, '(lead)', ?, ?, 1)", (SN.sent_id(title, t), title, i, t))
    db.commit()
    db.close()


class Settings(unittest.TestCase):
    def test_off_by_default_on_with_a_block_or_true(self):
        with temp_root():
            self.assertIsNone(settings(make_subject("a")))
            self.assertIsNone(settings(make_subject("b", "title: B\nexplain: false\n")))
            self.assertEqual(settings(make_subject("c", "title: C\nexplain: true\n"))["blurbs"], 1)
            s = settings(make_subject("d", YAML))
            self.assertEqual((s["terms"], s["blurbs"], s["background"]), (2, 1, 3))
            self.assertEqual(s["audience"], "a developer new to this framework")
            self.assertIsNone(settings(make_subject("e", "title: E\nexplain:\n  enabled: false\n  terms: 5\n")))


class Scout(unittest.TestCase):
    def test_packets_are_chunked_and_name_the_reader(self):
        with temp_root():
            s, _ = build_course()
            self.assertEqual(B.packet(s, log=lambda *a: None), 1)
            text = (s.explain_work / "packet-001.md").read_text()
            self.assertIn("Reader: a developer new to this framework", text)
            self.assertIn("### tiny-a | Service lifetimes", text)
            self.assertIn("up to 3 pieces of background", text)

    def test_resolve_fetches_lead_sentences_and_skips_covered_and_disambiguation(self):
        with temp_root():
            s, _ = build_course()
            s.explain_work.mkdir(parents=True)
            write_json(s.explain_work / "assumes.001.json", {"assumes": {
                "tiny-a": ["dependency injection", "HTTP protocol", "mercury", "nothing at all"]}})
            page = lambda t, text, cats=(): dict(wiki_page(t, f"<div class='mw-parser-output'><p>{text}</p></div>", 5),
                                                 categories=[{"category": c} for c in cats])
            client = Search({"Dependency injection": page("Dependency injection", DI),
                             "HTTP": page("HTTP", HTTP),
                             "Mercury": page("Mercury", "Mercury may refer to a planet or a metal.",
                                             ["All disambiguation pages"])},
                            {"dependency injection": "Dependency injection", "HTTP protocol": "HTTP",
                             "mercury": "Mercury"})
            out = B.resolve(s, client=client, log=lambda *a: None)
            mine = out["entries"]["tiny-a"]
            self.assertEqual([p["key"] for p in mine], ["Dependency injection"])
            self.assertEqual(mine[0]["sentences"][0]["sent_id"], SN.sent_id("Dependency injection", DI))
            self.assertEqual(out["covered"]["tiny-a"], [{"phrase": "HTTP protocol", "entry": "tiny-b"}])
            self.assertEqual({u["phrase"]: u["reason"] for u in out["unresolved"]["tiny-a"]},
                             {"mercury": "a disambiguation page"})
            self.assertTrue((s.reports_dir / "explain.md").exists())
            # the cited sentence is now in the index, and a second run searches nothing new
            self.assertIn(SN.sent_id("Dependency injection", DI), SN.lookup(SN.connect(), [SN.sent_id("Dependency injection", DI)]))
            again = Search(client.pages, client.hits)
            B.resolve(s, client=again, log=lambda *a: None)
            self.assertEqual(again.searched, [])

    def test_a_hand_override_wins_over_the_search(self):
        with temp_root():
            s, _ = build_course()
            s.explain_work.mkdir(parents=True)
            write_json(s.explain_work / "assumes.001.json", {"assumes": {"tiny-a": ["dependency injection"]}})
            write_json(s.explain_work / "pages.json", {"Dependency Injection": "Inversion of control"})
            ioc = wiki_page("Inversion of control", "<div class='mw-parser-output'><p>Inversion of control hands "
                            "the flow of a program to a framework.</p></div>", 5)
            client = Search({"Inversion of control": ioc}, {"dependency injection": "Dependency injection"})
            out = B.resolve(s, client=client, log=lambda *a: None)
            self.assertEqual(out["entries"]["tiny-a"][0]["key"], "Inversion of control")
            self.assertEqual(client.searched, [])


class Writing(unittest.TestCase):
    def setUp(self):
        self.ctx = temp_root()
        self.ctx.__enter__()
        self.addCleanup(self.ctx.__exit__, None, None, None)
        self.s, self.fact = build_course()
        self.di = SN.sent_id("Dependency injection", DI)
        index_background({"Dependency injection": [DI]})
        db = SN.connect()
        db.execute("INSERT OR REPLACE INTO pages (title, url, revid, n_sentences) VALUES ('Services', 'u', 7, 2)")
        for k, (sid, t) in enumerate([(self.fact, FACT), ("aaaaaaaaaaaa", "HTTP carries requests.")]):
            db.execute("INSERT INTO sentences (sent_id, title, revid, section, idx, sentence) VALUES (?, 'Services', 7, '', ?, ?)",
                       (sid, k, t))
        db.commit()
        write_json(self.s.explain_dir / "background.json", {"entries": {"tiny-a": [
            {"phrase": "dependency injection", "key": "Dependency injection", "name": "Dependency injection",
             "url": "u", "revid": 5, "sentences": [{"sent_id": self.di, "text": DI}]}]}, "covered": {
            "tiny-a": [{"phrase": "HTTP protocol", "entry": "tiny-b"}]}})
        self.good = {"tiny-a": {
            "terms": [{"term": "service container", "sent_ids": [self.di],
                       "text": "An object that hands other objects the things they depend on."}],
            "blurbs": [{"heading": "Why objects ask for their helpers", "sent_ids": [self.di, self.fact],
                        "text": ("Dependency injection is a design pattern in which an object receives the other "
                                 "objects it depends on, instead of building them itself. A service container does "
                                 "the handing over, and it resolves 3 kinds of lifetime for each registered service. "
                                 "See {{ref:tiny-b}} for how requests arrive. ") * 2}]}}

    def write(self, explain=None, text="A service container resolves lifetimes for every service."):
        self.s.write_dir.mkdir(parents=True, exist_ok=True)
        write_json(self.s.write_dir / "fill.a.01.json", {
            "entries": {"tiny-a": {"title": "Service lifetimes", "text": text},
                        "tiny-b": {"title": "Hypertext transfer", "text": "HTTP carries requests."}},
            "explain": explain if explain is not None else self.good})
        R.render(self.s, log=lambda *a: None)
        return R.load(self.s)

    def problems(self, **kw):
        prose = self.write(**kw)
        p, w = audit(self.s, prose, self.s.entries_by_id(), ["tiny-a", "tiny-b"])
        return p, w

    def test_the_packet_shows_sent_ids_background_and_caps(self):
        K.build(self.s, log=lambda *a: None)
        text = next(self.s.write_dir.glob("packet-*.md")).read_text()
        self.assertIn("EXPLAIN MODE. Reader: a developer new to this framework.", text)
        self.assertIn(f"- Fact [{self.fact}]: {FACT}", text)
        self.assertIn(f"- BACKGROUND (Dependency injection) [{self.di}] {DI}", text)
        self.assertIn("COVERED BY THE COURSE: HTTP protocol is entry tiny-b", text)
        self.assertIn("EXPLAIN: up to 2 terms and 1 blurb(s)", text)

    def test_a_subject_without_explain_gets_the_packet_it_always_got(self):
        s = make_subject("plain")
        write_jsonl(s.entries_dir / "core.jsonl", [{"id": "plain-a", "title": "T", "kind": "Concept",
                                                     "weight": "Major", "level": "Foundational", "part": "P", "chapter": "C",
                                                     "selected": True, "definition": {"text": "D.", "sent_ids": ["x"]},
                                                     "facts": [{"text": "F.", "sent_ids": ["y"]}]}])
        write_json(s.order_path, {"order": ["plain-a"], "locked": True})
        K.build(s, log=lambda *a: None)
        text = next(s.write_dir.glob("packet-*.md")).read_text()
        self.assertIn("- Fact: F.", text)
        self.assertNotIn("EXPLAIN", text)
        self.assertIn("- Definition: D.", text)

    def test_good_explanations_pass_and_render(self):
        p, w = self.problems()
        self.assertEqual(p, [])
        md = (self.s.output_dir / "course.md").read_text()
        self.assertIn("> **service container**:", md)
        self.assertIn("> **Why objects ask for their helpers**", md)
        self.assertIn("See Hypertext transfer for how requests arrive.", md)

    def test_a_later_batch_replaces_an_entrys_items(self):
        self.write()
        write_json(self.s.write_dir / "fill.a.02.json", {"explain": {"tiny-a": {"terms": [], "blurbs": []}}})
        R.render(self.s, log=lambda *a: None)
        self.assertEqual(items(R.load(self.s), "tiny-a"), ([], []))

    def test_the_rules(self):
        g = self.good["tiny-a"]
        blurb, term = g["blurbs"][0], g["terms"][0]

        def with_(**kw):
            d = {"terms": [dict(term, **kw.get("term", {}))], "blurbs": [dict(blurb, **kw.get("blurb", {}))]}
            return {"tiny-a": d}
        cases = {
            "no sent_ids": (with_(blurb={"sent_ids": []}), "no sent_ids"),
            "a sentence from nowhere": (with_(blurb={"sent_ids": ["ffffffffffff"]}), "not in the entry's facts"),
            "a number the sources lack": (with_(blurb={"text": blurb["text"] + " It runs 4096 requests."}),
                                          "numbers not in the sentences it cites"),
            "a banned phrase": (with_(blurb={"text": blurb["text"] + " It will delve."}), "banned phrase"),
            "an unknown ref": (with_(blurb={"text": blurb["text"] + " {{ref:nope}}"}), "names no entry"),
            "a term the text never uses": (with_(term={"term": "monad"}), "not used in the entry's text"),
        }
        for name, (explain, expect) in cases.items():
            with self.subTest(name):
                p, _ = self.problems(explain=explain)
                self.assertTrue(any(expect in m for m in p), (expect, p))
        too_many = {"tiny-a": {"terms": [term] * 3, "blurbs": [blurb] * 2}}
        p, _ = self.problems(explain=too_many)
        self.assertTrue(any("3 terms" in m for m in p) and any("2 blurbs" in m for m in p), p)

    def test_numbers_from_the_cited_sentence_or_the_entry_are_fine(self):
        p, _ = self.problems()           # "3" comes from the entry's own fact it cites
        self.assertEqual(p, [])

    def test_short_blurbs_warn_and_do_not_fail(self):
        short = {"tiny-a": {"terms": [], "blurbs": [dict(self.good["tiny-a"]["blurbs"][0],
                                                          text="Short but sourced.")]}}
        p, w = self.problems(explain=short)
        self.assertEqual(p, [])
        self.assertTrue(any("words (blurbs run" in m for m in w), w)

    def test_write_check_runs_the_audit_and_the_term_scan_sees_blurbs(self):
        self.write(explain={"tiny-a": {"terms": [], "blurbs": [dict(self.good["tiny-a"]["blurbs"][0],
                                                                    text="Hypertext transfer comes up. " * 2)]}})
        problems, warnings = C.run(self.s, log=lambda *a: None)
        self.assertFalse([m for m in problems if "explain" in m])
        self.assertTrue(any("uses 'hypertext transfer' before tiny-b" in m for m in warnings), warnings)

    def test_export_carries_items_sentences_and_background_pages(self):
        self.write()
        write_json(self.s.units_path, {"units": [{"n": 1, "entries": ["tiny-a", "tiny-b"], "path": [], "openers": [],
                                                  "reviews": [], "terms": []}]})
        doc = export.export(self.s, strict=True, log=lambda *a: None)
        a = doc["entries"][0]
        self.assertEqual([t["term"] for t in a["explain"]["terms"]], ["service container"])
        self.assertIn("See Hypertext transfer for", a["explain"]["blurbs"][0]["text_plain"])
        self.assertIn("{{ref:tiny-b}}", a["explain"]["blurbs"][0]["text"])
        self.assertNotIn("explain", doc["entries"][1])
        self.assertIn(self.di, doc["sentences"])
        self.assertIn("Dependency injection", doc["license"]["pages"])
        self.assertEqual(doc["missing_sentences"], [])

    def test_the_epub_shows_terms_blurbs_and_background_credit(self):
        self.write()
        write_json(self.s.units_path, {"built": "2026-01-01T00:00Z", "units": [
            {"n": 1, "entries": ["tiny-a", "tiny-b"], "path": ["basics", "core"], "leaf": "core", "openers": [],
             "reviews": [], "terms": []}]})
        ed = Edition(self.s)
        html = ed.entry_html("tiny-a")
        self.assertIn('<p class="term"><b>service container</b>:', html)
        self.assertIn('<blockquote class="blurb"><p><b>Why objects ask for their helpers</b></p>', html)
        self.assertIn("See Hypertext transfer (Unit 1) for how requests arrive.", html)
        self.assertIn("Background: Dependency injection", html)
        self.assertNotIn("blurb", ed.entry_html("tiny-b"))
        self.assertIn("Background:", ed.attribution_html(["tiny-a"]))

    def test_source_entries_credit_only_outside_sentences(self):
        prose = self.write()
        srcs = source_entries(self.s, prose, self.s.entries_by_id())
        self.assertEqual([x["id"] for x in srcs], ["tiny-a"])
        self.assertEqual([x["key"] for x in srcs[0]["sources"]], ["Dependency injection"])
        self.assertEqual(own_sent_ids(self.s.entries_by_id()["tiny-a"]), {self.fact})
        self.assertIn("hands other objects", text_of(prose, "tiny-a"))


if __name__ == "__main__":
    unittest.main()
