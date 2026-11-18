import unittest

from coursesmith.crawl.crawl import Crawler
from coursesmith.crawl.scope import Scope
from coursesmith.crawl.store import Store, read_ledger

from .fakes import FakeAdapter, FakeRegistry, FakeWikiClient
from .helpers import make_subject, temp_root

LEAD = "A network connects computers so that they can share data and services."
PAGES = {
    "fake>a/b.md": ("B", f"# B\n{LEAD}", "v1", ["fake>a/c.md", "fake>other/x.md", "Soil"]),
    "fake>a/c.md": ("C", f"# C\n{LEAD}", "v1", ["fake>a/d.md"]),
    "fake>a/d.md": ("D", f"# D\n{LEAD}", "v1", []),
    "fake>other/x.md": ("X", f"# X\n{LEAD}", "v1", []),
}
YAML = "slug: tiny\ntitle: Tiny\nseeds: ['fake>a/b.md']\nscope:\n  threshold: 5\n"


def run_crawl(depth=2, allow=("a/",), pages=PAGES):
    ad = FakeAdapter({"name": "fake-src", "allow": list(allow)}, pages=dict(pages))
    subj = make_subject("tiny", YAML)
    c = Crawler(subj, max_pages=50, max_depth=depth, client=FakeWikiClient(), store=Store(),
                registry=FakeRegistry(ad), log=lambda *a: None)
    c.run()
    return subj, ad, c


class ScopeTest(unittest.TestCase):
    def test_qualified_keys_score_by_allowlist(self):
        with temp_root():
            ad = FakeAdapter({"allow": ["a/"]})
            subj = make_subject("tiny", YAML)
            sc = Scope(subj, registry=FakeRegistry(ad))
            s_in, why_in = sc.score("fake>a/b.md")
            self.assertGreaterEqual(s_in, sc.threshold)
            self.assertEqual(why_in, ["allowlist"])
            s_out, why_out = sc.score("fake>other/x.md")
            self.assertEqual(s_out, -99)
            self.assertIn("allowlist", why_out[0])

    def test_forced_allowed_key_outscores_plain_allowed(self):
        with temp_root():
            sc = Scope(make_subject("tiny", YAML), registry=FakeRegistry(FakeAdapter({})))
            sc.forced.add("fake>a")
            self.assertGreater(sc.score("fake>a")[0], sc.score("fake>b")[0])


class CrawlSourcesTest(unittest.TestCase):
    def test_follows_only_allowlisted_links_within_depth(self):
        with temp_root():
            subj, ad, c = run_crawl()
            fetched = {r["title"] for r in read_ledger(subj) if r["status"].startswith("fetched")}
            self.assertEqual(fetched, {"fake>a/b.md", "fake>a/c.md"})
            self.assertNotIn("fake>other/x.md", ad.fetched)
            self.assertNotIn("fake>a/d.md", ad.fetched)  # one hop beyond the source's depth of 1
            rejected = (subj.scope_dir / "frontier_rejected.csv").read_text()
            self.assertIn("fake>other/x.md", rejected)
            self.assertIn("outside the sources allowlist", rejected)
            self.assertIn("fake>a/d.md", rejected)
            self.assertIn("beyond the source's depth", rejected)

    def test_per_source_depth_is_configurable(self):
        with temp_root():
            ad = FakeAdapter({"name": "fake-src", "allow": ["a/"], "depth": 2}, pages=dict(PAGES))
            subj = make_subject("tiny", YAML)
            Crawler(subj, max_pages=50, max_depth=3, client=FakeWikiClient(), store=Store(),
                    registry=FakeRegistry(ad), log=lambda *a: None).run()
            self.assertIn("fake>a/d.md", ad.fetched)

    def test_ledger_records_version_for_non_wikipedia_pages(self):
        with temp_root():
            subj, ad, c = run_crawl()
            row = next(r for r in read_ledger(subj) if r["title"] == "fake>a/b.md")
            self.assertEqual(row["revid"], "v1")
            self.assertEqual(row["in_scope_reason"], "frame")

    def test_disallowed_seed_is_skipped_with_a_message(self):
        with temp_root():
            logs = []
            ad = FakeAdapter({"allow": ["zzz/"]}, pages=dict(PAGES))
            subj = make_subject("tiny", YAML)
            Crawler(subj, max_pages=5, client=FakeWikiClient(), store=Store(), registry=FakeRegistry(ad),
                    log=logs.append).run()
            self.assertEqual(ad.fetched, [])
            self.assertTrue(any("skipped seed" in l for l in logs))

    def test_adapter_seeds_are_crawled_without_listing_them(self):
        with temp_root():
            class Seeded(FakeAdapter):
                def seeds(self):
                    return ["fake>a/b.md"]
            ad = Seeded({"allow": ["a/"]}, pages=dict(PAGES))
            subj = make_subject("tiny", "slug: tiny\ntitle: Tiny\nscope:\n  threshold: 5\n")
            reg = FakeRegistry(ad)
            reg.all_seeds = ad.seeds
            Crawler(subj, max_pages=5, max_depth=0, client=FakeWikiClient(), store=Store(), registry=reg,
                    log=lambda *a: None).run()
            self.assertEqual(ad.fetched, ["fake>a/b.md"])

    def test_missing_page_is_ledgered_not_fatal(self):
        with temp_root():
            subj, ad, c = run_crawl(pages={k: v for k, v in PAGES.items() if k != "fake>a/c.md"})
            status = {r["title"]: r["status"] for r in read_ledger(subj)}
            self.assertEqual(status["fake>a/c.md"], "missing")
            self.assertTrue(status["fake>a/b.md"].startswith("fetched"))


if __name__ == "__main__":
    unittest.main()
