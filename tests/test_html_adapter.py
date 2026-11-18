import unittest

from coursesmith.sources.base import MissingSource, SourceError
from coursesmith.sources.html import ADAPTER, HtmlAdapter, norm_path
from coursesmith.sources.registry import Registry

from .fakes import FIXTURES, FakeHTTP

H = FIXTURES / "html"
BASE = "https://redis.io/docs/latest/"


def adapter(**cfg):
    http = FakeHTTP({
        "https://redis.io/robots.txt": H / "robots.txt",
        "https://redis.io/docs/latest/develop/data-types/hashes": H / "hashes.html",
        "https://redis.io/docs/latest/": H / "hashes.html",
    })
    c = {"name": "redis-docs", "adapter": "html", "base": BASE, "allow": ["/docs/latest/develop/", "/docs/latest/"],
         "deny": ["/docs/latest/commands/"], "selector": "main", "title": "Redis docs",
         "license": {"name": "CC BY-SA 4.0"}, **cfg}
    return HtmlAdapter(c, http=http)


class KeysTest(unittest.TestCase):
    def test_norm_path(self):
        self.assertEqual(norm_path("/docs/latest/x/index.html"), "/docs/latest/x")
        self.assertEqual(norm_path("/docs/latest/x/?a=1#b"), "/docs/latest/x")
        self.assertEqual(norm_path(""), "/")

    def test_key_round_trip_and_ownership(self):
        a = adapter()
        k = a.key("/docs/latest/develop/data-types/hashes/")
        self.assertEqual(k, "doc>redis.io/docs/latest/develop/data-types/hashes")
        self.assertEqual(a.url_of(k), "https://redis.io/docs/latest/develop/data-types/hashes")
        self.assertTrue(a.owns(k))
        self.assertFalse(a.owns("doc>other.io/docs/x"))

    def test_allow_and_deny(self):
        a = adapter(allow=["/docs/latest/develop/"])
        self.assertTrue(a.allowed("doc>redis.io/docs/latest/develop/data-types"))
        self.assertTrue(a.allowed("doc>redis.io/docs/latest/develop"))
        self.assertFalse(a.allowed("doc>redis.io/docs/latest/operate/x"))
        self.assertFalse(a.allowed("doc>redis.io/docs/latest/develop/logo.png"))
        b = adapter()
        self.assertFalse(b.allowed("doc>redis.io/docs/latest/commands/hset"))
        self.assertTrue(b.allowed("doc>redis.io/docs/latest/operate/x"))

    def test_links(self):
        a = adapter()
        base = "doc>redis.io/docs/latest/develop/data-types/hashes"
        self.assertEqual(a.key_for_url("../lists/", base), "doc>redis.io/docs/latest/develop/data-types/lists")
        self.assertEqual(a.key_for_url("/docs/latest/commands/hset/#x", base), "doc>redis.io/docs/latest/commands/hset")
        self.assertEqual(a.key_for_url("https://en.wikipedia.org/wiki/Hash_table", base), "Hash table")
        self.assertIsNone(a.key_for_url("https://example.org/x", base))
        self.assertIsNone(a.key_for_url("#top", base))
        self.assertIsNone(a.key_for_url("/img/logo.png", base))

    def test_base_required(self):
        with self.assertRaises(SourceError):
            HtmlAdapter({"name": "x", "base": "nonsense"})

    def test_pages_become_seeds(self):
        self.assertEqual(adapter(pages=["/docs/latest/develop/data-types/hashes/"]).seeds(),
                         ["doc>redis.io/docs/latest/develop/data-types/hashes"])


class FetchTest(unittest.TestCase):
    KEY = "doc>redis.io/docs/latest/develop/data-types/hashes"

    def test_record(self):
        rec = adapter().fetch(self.KEY)
        self.assertEqual(rec["name"], "Redis hashes (Redis docs)")
        self.assertEqual(rec["url"], "https://redis.io/docs/latest/develop/data-types/hashes")
        self.assertEqual(rec["tier"], "official")
        self.assertEqual(len(rec["version"]), 16)
        self.assertTrue(rec["text"].startswith("# Redis hashes\n"))
        self.assertIn("## Basic commands", rec["text"])
        self.assertIn("- HSET sets the value of one or more fields on a hash.", rec["text"])
        self.assertNotIn("Redis docs header", rec["text"])
        self.assertNotIn("Deimos", rec["text"])  # code block dropped
        self.assertNotIn("Edit this page", rec["text"])  # Contributing section dropped
        self.assertEqual(rec["meta"]["code_blocks"], 1)

    def test_links(self):
        rec = adapter().fetch(self.KEY)
        self.assertEqual(rec["body_links"], ["doc>redis.io/docs/latest/develop/data-types/lists",
                                             "doc>redis.io/docs/latest/commands/hset", "Hash table"])
        self.assertEqual(rec["anchors"]["hash table"], "Hash table")

    def test_version_is_a_content_hash(self):
        a = adapter()
        self.assertEqual(a.fetch(self.KEY)["version"], a.fetch(self.KEY)["version"])

    def test_robots_disallow(self):
        a = adapter(base="https://redis.io/private/")
        with self.assertRaises(SourceError):
            a.fetch("doc>redis.io/private/page")

    def test_robots_can_be_ignored_only_explicitly(self):
        a = adapter(base="https://redis.io/private/", robots=False)
        with self.assertRaises(MissingSource):  # not blocked, but the fixture has no such page
            a.fetch("doc>redis.io/private/page")

    def test_missing_page(self):
        with self.assertRaises(MissingSource):
            adapter().fetch("doc>redis.io/docs/latest/develop/nope")

    def test_trailing_slash_retry(self):
        a = adapter()
        a.http.mapping["https://redis.io/docs/latest/develop/lists/"] = H / "hashes.html"
        self.assertEqual(a.fetch("doc>redis.io/docs/latest/develop/lists")["title"], "doc>redis.io/docs/latest/develop/lists")


class CheckTest(unittest.TestCase):
    def test_license_found_and_matching(self):
        res = adapter().check()
        self.assertEqual(res["problems"], [])
        self.assertEqual(res["evidence"]["license"]["class"], "cc-by-sa")

    def test_declared_license_mismatch_fails(self):
        res = adapter(license={"name": "MIT"}).check()
        self.assertTrue(any("declares MIT" in p for p in res["problems"]))

    def test_undeclared_license_fails(self):
        res = adapter(license=None).check()
        self.assertTrue(any("declare the site's license" in p for p in res["problems"]))

    def test_no_statement_is_a_note(self):
        a = adapter()
        a.http.mapping[BASE] = "<html><body><main><h1>X</h1><p>plain</p></main></body></html>"
        res = a.check()
        self.assertTrue(any("no license statement" in n for n in res["notes"]))

    def test_unreachable_base(self):
        a = adapter()
        a.http.mapping[BASE] = None
        self.assertTrue(any("not reachable" in p for p in a.check()["problems"]))


class RegistryTest(unittest.TestCase):
    def test_registry_builds_html(self):
        r = Registry([{"name": "redis-docs", "adapter": "html", "base": BASE, "allow": ["/docs/latest/develop/"]}])
        k = "doc>redis.io/docs/latest/develop/data-types/hashes"
        self.assertIs(type(r.for_key(k)), ADAPTER)
        self.assertTrue(r.allowed(k))
        self.assertFalse(r.allowed("doc>redis.io/blog/x"))
        self.assertEqual(r.tier(k), "official")


if __name__ == "__main__":
    unittest.main()
