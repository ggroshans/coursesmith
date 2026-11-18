"""A mixed-source course (Wikipedia, a GitHub repo, an RFC) through every stage, offline, from `sources check` to
the EPUB and course.json. The consolidation and writing passes are people or models in real life; here their
output is written by hand, and everything the engine does around them runs for real."""
import io
import json
import unittest
import zipfile

from coursesmith.consolidate import dossier, finalize
from coursesmith.crawl.crawl import Crawler
from coursesmith.crawl.store import Store, read_ledger
from coursesmith.extract import sentences as SN
from coursesmith.graph import build as graph
from coursesmith.order import order as order_mod
from coursesmith.order import select
from coursesmith.publish import build as pbuild
from coursesmith.publish import check as pcheck
from coursesmith.publish import export, units
from coursesmith.sources import check as sources_check
from coursesmith.sources.registry import Registry
from coursesmith.util import read_jsonl, write_json, write_jsonl
from coursesmith.write import check as wcheck
from coursesmith.write import render, skeleton

from .fakes import FIXTURES, FakeHTTP, FakeWikiClient, wiki_page
from .helpers import make_subject, temp_root

GH, RFC = FIXTURES / "github", FIXTURES / "rfc"
SHA = "ae9bbd7b02d90b9866215de185217d33f39ab733"
RAW = f"https://raw.githubusercontent.com/donnemartin/system-design-primer/{SHA}"
API = "https://api.github.com"
PASTEBIN = "gh>donnemartin/system-design-primer/solutions/system_design/pastebin/README.md"

YAML = f"""slug: sysd
title: System Design Interviews
short: sysd
description: Interview questions about designing systems, answered from vetted sources.
course_type: questions
distribution: personal
sources:
  - name: primer
    adapter: github
    repo: donnemartin/system-design-primer
    ref: {SHA}
    include: ["solutions/**/README.md"]
    seeds: ["solutions/system_design/pastebin/README.md"]
    depth: 1
    tier: curated
    license: {{name: "CC BY 4.0"}}
  - {{name: rfcs, adapter: rfc, ids: [2119]}}
seeds: ["Consistent hashing"]
scope: {{threshold: 5}}
targets:
  per_unit: [2, 3]
  fact_caps: {{"Worked example": 16}}
verification:
  units: [ms, QPS, GB, KB, bytes]
"""
FRAME = f"""status: reviewed
parts:
  - key: found
    title: Foundations
    chapters:
      - {{key: c-basics, title: Basics, seeds: ["Consistent hashing", "rfc>2119"]}}
  - key: q
    title: Interview questions
    question: true
    chapters:
      - {{key: c-pastebin, title: Design a pastebin, question: true, seeds: ["{PASTEBIN}"]}}
"""
WIKI_HTML = ("<div class='mw-parser-output'><p><b>Consistent hashing</b> is a distributed hashing scheme that operates "
             "independently of the number of servers in a hash table.</p><h2>Overview</h2><p>It spreads keys over a "
             "ring so that adding a server moves only a small share of the keys to the new server.</p></div>")


def http():
    return FakeHTTP({
        f"{API}/repos/donnemartin/system-design-primer/license?ref={SHA}": GH / "primer.license.json",
        f"{API}/repos/donnemartin/system-design-primer/git/trees/{SHA}?recursive=1": GH / "primer.tree.json",
        f"{RAW}/solutions/system_design/pastebin/README.md": GH / "primer.pastebin.md",
        "https://www.rfc-editor.org/rfc/rfc2119.txt": RFC / "rfc2119.txt",
        "https://www.rfc-editor.org/rfc/rfc2119.json": RFC / "rfc2119.json",
    })


def quiet(*a, **k):
    pass


def sid(db, title, phrase):
    row = db.execute("SELECT sent_id FROM sentences WHERE title = ? AND sentence LIKE ? ORDER BY idx LIMIT 1",
                     (title, f"%{phrase}%")).fetchone()
    assert row, f"no sentence in {title} with {phrase!r}"
    return row[0]


class MixedSourcePipelineTest(unittest.TestCase):
    def test_from_sources_check_to_epub_and_course_json(self):
        with temp_root():
            subj = make_subject("sysd", YAML)
            subj.frame_path.write_text(FRAME)
            reg = Registry.from_subject(subj, http=http())
            client = FakeWikiClient({"Consistent hashing": wiki_page("Consistent hashing", WIKI_HTML, revid=11)})

            # 1. nothing may be crawled until the sources have been checked
            with self.assertRaises(SystemExit):
                sources_check.require_ok(subj)
            self.assertEqual(sources_check.run(subj, registry=reg, log=quiet), [])
            sources_check.require_ok(subj)

            # 2. crawl: Wikipedia seed, RFC from its `ids`, the repo's own seed; nothing else
            Crawler(subj, max_pages=20, max_depth=1, client=client, store=Store(), registry=reg, log=quiet).run()
            fetched = {r["title"] for r in read_ledger(subj) if r["status"].startswith("fetched")}
            self.assertEqual(fetched, {"Consistent hashing", "rfc>2119", PASTEBIN})

            # 3. extract, graph, dossier
            SN.build(subj, log=quiet)
            g = graph.build(subj, log=quiet)
            self.assertEqual(g["nodes"][PASTEBIN]["chapter"], "c-pastebin")
            self.assertEqual((g["nodes"]["rfc>2119"]["source"], g["nodes"]["rfc>2119"]["tier"]), ("rfcs", "standard"))
            dossier.build(subj, "all", log=quiet)
            dtext = "\n".join(p.read_text() for p in (subj.dossier_dir / "c-pastebin").glob("chunk_*.md"))
            self.assertIn("QUESTION: Design a pastebin", dtext)
            self.assertIn("10 million paste writes per month", dtext)

            # 4. consolidation (by hand): one concept per source, and the worked answer
            db = SN.connect()
            s_ch = sid(db, "Consistent hashing", "distributed hashing scheme")
            s_ch2 = sid(db, "Consistent hashing", "adding a server moves only")
            s_rfc = sid(db, "rfc>2119", "absolute requirement")
            s_w = sid(db, PASTEBIN, "10 million paste writes per month")
            s_r = sid(db, PASTEBIN, "100 million paste reads per month")
            s_q = sid(db, PASTEBIN, "define some use cases")
            fact = lambda t, *ids: {"text": t, "sent_ids": list(ids)}
            base = {"level": "Foundational", "weight": "Major", "related": []}
            drafts_basics = [
                dict(base, title="Consistent hashing", kind="Concept", article="Consistent hashing",
                     definition=fact("A hashing scheme that works independent of the number of servers.", s_ch),
                     facts=[fact("It spreads keys over a ring.", s_ch), fact("Adding a server moves only a few keys.", s_ch2)]),
                dict(base, title="MUST in a specification", kind="Concept", article="rfc>2119",
                     definition=fact("MUST marks an absolute requirement of a specification.", s_rfc),
                     facts=[fact("MUST is an absolute requirement.", s_rfc), fact("Implementations may not skip it.", s_rfc)]),
            ]
            drafts_q = [
                dict(base, title="Designing a pastebin", kind="Worked example", level="Intermediate", weight="Landmark",
                     article=PASTEBIN, prerequisites=["Consistent hashing"],
                     facts=[fact("The service takes 10 million paste writes per month.", s_w),
                            fact("It serves 100 million paste reads per month.", s_r),
                            fact("An interview scopes use cases and constraints first.", s_q)]),
            ]
            subj.draft_dir.mkdir(parents=True, exist_ok=True)
            write_jsonl(subj.draft_dir / "c-basics.jsonl", drafts_basics)
            write_jsonl(subj.draft_dir / "c-pastebin.jsonl", drafts_q)
            self.assertEqual(finalize.finalize(subj, "all", log=quiet), [])
            entries = {e["title"]: e for e in subj.entries()}
            self.assertEqual({e["source_tier"] for e in entries.values()}, {"wikipedia", "standard", "curated"})
            w = entries["Designing a pastebin"]
            self.assertEqual(w["sources"][0]["key"], PASTEBIN)
            self.assertEqual(w["sources"][0]["title"], "Design Pastebin.com (or Bit.ly) (system-design-primer)")
            self.assertIn("question entry", w["curriculum"])
            self.assertIn("vetted source", entries["MUST in a specification"]["curriculum"])

            # 5. select, order, lock
            select.run(subj, log=quiet)
            order = order_mod.build(subj, log=quiet)
            self.assertEqual(order[-1], w["id"])  # the worked answer closes its chapter, after the concepts
            order_mod.lock(subj, log=quiet)

            # 6. writing: packet, a batch with a derived capacity number, render, check
            packets = skeleton.build(subj, log=quiet)
            ptext = "\n".join((subj.write_dir / f"packet-{p}.md").read_text() for p in
                              [p.name[len("packet-"):-3] for p in subj.write_dir.glob("packet-*.md")])
            self.assertIn("| Worked example | Intermediate | Landmark | 250-600 words", ptext)
            ids = {t: e["id"] for t, e in entries.items()}
            write_json(subj.write_dir / "fill.a.json", {
                "entries": {
                    ids["Consistent hashing"]: {"title": "Why adding a server moves so few keys",
                                                "text": "Keys sit on a ring. Adding a server moves only a few of them."},
                    ids["MUST in a specification"]: {"title": "What MUST means in a specification",
                                                     "text": "MUST marks an absolute requirement, and nothing may skip it."},
                    w["id"]: {"title": "Designing a pastebin from the ground up",
                              "text": ("A pastebin takes 10 million paste writes per month and serves 100 million reads.\n\n"
                                       "That is roughly 4 writes a second, a small load for one database, so the first "
                                       "step is to scope use cases and constraints.")}},
                "derived": {w["id"]: [{"values": [4], "from": [s_w], "expr": "10 * 1000000 / (30 * 86400)",
                                       "reason": "paste writes per month to per second"}]}})
            render.render(subj, log=quiet)
            prose = render.load(subj)
            self.assertIn("\n\n", prose["entries"][w["id"]]["text"])  # worked answers keep their paragraphs
            self.assertNotIn("\n", prose["entries"][ids["Consistent hashing"]]["text"])
            wproblems, _ = wcheck.run(subj, log=quiet)
            self.assertEqual(wproblems, [])  # the derived number holds, so nothing is flagged

            # 7. units, publish check (the derived number must hold), export, EPUB
            units.build(subj, log=quiet)
            probs, _ = pcheck.run(subj, log=quiet)
            self.assertEqual(probs, [])
            doc = export.export(subj, strict=True, log=quiet)
            self.assertEqual((doc["format"], doc["version"]), ("wikicourse-course", 2))
            self.assertEqual([e["kind"] for e in doc["entries"]][-1], "Worked example")
            self.assertIn("\n\n", doc["entries"][-1]["text_plain"])
            lic = doc["license"]
            self.assertEqual(lic["name"], "Mixed open licenses, share-alike (see sources)")
            by_key = {s["key"]: s for s in lic["sources"]}
            self.assertEqual(set(by_key), {"Consistent hashing", "rfc>2119", PASTEBIN})
            self.assertEqual((by_key[PASTEBIN]["license"], by_key[PASTEBIN]["tier"], by_key[PASTEBIN]["version_label"]),
                             ("CC BY 4.0", "curated", "commit ae9bbd7"))
            self.assertEqual(by_key["rfc>2119"]["version_label"], "published March 1997")
            self.assertIn("oldid=11", by_key["Consistent hashing"]["permalink"])
            self.assertEqual(doc["subject"]["course_type"], "questions")
            self.assertEqual(doc["subject"]["kinds"], ["Concept", "Worked example"])

            from coursesmith import config
            man = pbuild.build(subj, log=quiet)
            epub = config.EPUB_DIR / "sysd" / man["units"]["1"]["file"]
            z = zipfile.ZipFile(epub)
            sources = z.read("OEBPS/sources.xhtml").decode()
            tags = "".join(zipfile.ZipFile(config.EPUB_DIR / "sysd" / u["file"]).read("OEBPS/unit.xhtml").decode()
                           for u in man["units"].values())
            self.assertIn("Sources: Design Pastebin.com (or Bit.ly) (system-design-primer)", tags)
            self.assertIn("Sources: Consistent hashing", tags)
            self.assertIn("Sources and license", sources)
            self.assertIn("adapted from the sources listed below", sources)
            self.assertIn("commit ae9bbd7", sources)
            self.assertNotIn("<p>The text of this edition is adapted from Wikipedia articles", sources)
            self.assertIn("dc:rights", z.read("OEBPS/content.opf").decode())


if __name__ == "__main__":
    unittest.main()
