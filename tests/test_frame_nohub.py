import unittest

import yaml

from coursesmith.crawl.store import Store
from coursesmith.frame import build as FB

from .fakes import FakeAdapter, FakeRegistry, FakeWikiClient
from .helpers import make_subject, temp_root

LEAD = "A network connects computers so that they can share data and services."
YAML = """slug: tiny
title: Tiny
sources:
  - {name: fake-src, adapter: fake}
frame:
  parts:
    - key: found
      title: Foundations
      foundations: true
      chapters:
        - {title: Basics, seeds: ["fake>a/basics.md"]}
    - key: q
      title: Questions
      question: true
      chapters:
        - {title: Design a URL shortener, key: c-url, question: true, seeds: ["fake>a/url.md", "fake>a/extra.md"]}
        - {title: Design a rate limiter, seeds: ["fake>a/rate.md"]}
"""
PAGES = {k: (k.split("/")[-1], f"# {k}\n{LEAD}", "v1", []) for k in
         ("fake>a/basics.md", "fake>a/url.md", "fake>a/extra.md", "fake>a/rate.md")}


class NoHubFrameTest(unittest.TestCase):
    def run_build(self, yaml_text=YAML, allow=None):
        subj = make_subject("tiny", yaml_text)
        ad = FakeAdapter({"name": "fake-src", **({"allow": allow} if allow else {})}, pages=dict(PAGES))
        client = FakeWikiClient()
        logs = []
        doc = FB.build(subj, scout=10, log=logs.append, client=client, store=Store(), registry=FakeRegistry(ad))
        return subj, doc, ad, client, logs

    def test_seeds_only_frame_comes_out_of_subject_yaml(self):
        with temp_root():
            subj, doc, ad, client, logs = self.run_build()
            parts = {p["key"]: p for p in doc["parts"]}
            self.assertEqual(list(parts), ["found", "q"])
            self.assertEqual([c["title"] for c in parts["q"]["chapters"]], ["Design a URL shortener", "Design a rate limiter"])
            self.assertEqual(set(parts["q"]["chapters"][0]["seeds"]), {"fake>a/url.md", "fake>a/extra.md"})

    def test_question_flags_and_chapter_keys_carry_through(self):
        with temp_root():
            subj, doc, *_ = self.run_build()
            q = next(p for p in doc["parts"] if p["key"] == "q")
            self.assertTrue(q["question"])
            self.assertEqual(q["chapters"][0]["key"], "c-url")
            self.assertTrue(q["chapters"][0]["question"])
            self.assertNotIn("question", q["chapters"][1])
            self.assertEqual(q["chapters"][1]["key"], "design-a-rate-limiter")  # no key given: slug of the title
            written = yaml.safe_load(subj.frame_path.read_text())
            self.assertTrue(written["parts"][1]["question"])

    def test_wikipedia_is_not_asked_about_qualified_seeds(self):
        with temp_root():
            subj, doc, ad, client, logs = self.run_build()
            self.assertEqual(client.metaed, [])  # no prescreen of anything
            self.assertEqual(sorted(ad.fetched), sorted(PAGES))  # the scout fetched them through the adapter

    def test_forced_set_includes_qualified_seeds(self):
        with temp_root():
            subj, *_ = self.run_build()
            import json
            hubs = json.loads((subj.scope_dir / "hubs.json").read_text())
            self.assertEqual(set(hubs["forced"]), set(PAGES))

    def test_disallowed_seed_is_not_scouted(self):
        with temp_root():
            subj, doc, ad, client, logs = self.run_build(allow=["a/basics", "a/url"])
            self.assertNotIn("fake>a/rate.md", ad.fetched)
            self.assertTrue(any("skipped, no source" in l and "rate.md" in l for l in logs))

    def test_calibration_set_leaves_qualified_keys_out(self):
        with temp_root():
            subj, *_ = self.run_build()
            cal = subj.scope_dir / "calibration.csv"
            self.assertFalse(cal.exists() and "fake>" in cal.read_text())


if __name__ == "__main__":
    unittest.main()


class RedirectedSeedTest(unittest.TestCase):
    """Wikipedia redirects some titles ("Representational state transfer" is the article "REST"); the seed named in
    subject.yaml must still land in its chapter."""

    YAML = """slug: tiny
title: Tiny
frame:
  parts:
    - key: api
      title: APIs
      chapters:
        - {title: REST and friends, seeds: ["Representational state transfer", "GraphQL"]}
        - {title: Other, seeds: ["Remote procedure call"]}
"""

    def test_redirected_seeds_are_assigned_not_left_unassigned(self):
        with temp_root():
            subj = make_subject("tiny", self.YAML)
            st = Store()
            class Client(FakeWikiClient):
                def link_meta(self, titles):
                    return {"Representational state transfer": "REST"}, {
                        t if t != "Representational state transfer" else "REST": {"categories": [], "description": ""}
                        for t in titles}

                def parse_page(self, title):
                    return wiki_page(title, "<div class='mw-parser-output'><p>Some text here about it.</p></div>", 1)
            doc = FB.build(subj, scout=0, log=lambda *a: None, client=Client(), store=st, registry=FakeRegistry(FakeAdapter()))
            chapters = {c["title"]: c["seeds"] for p in doc["parts"] for c in p["chapters"]}
            self.assertIn("REST", chapters["REST and friends"])
            self.assertEqual(sorted(chapters["REST and friends"]), ["GraphQL", "REST"])
            report = (subj.reports_dir / "frame_report.md").read_text()
            self.assertNotIn("REST (", report.split("## Unassigned")[1])  # it is not listed as unassigned
