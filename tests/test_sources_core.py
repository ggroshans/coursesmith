import tempfile
import unittest
from pathlib import Path

from coursesmith.sources import Registry, best_tier, display, is_qualified, make_key, page_part, split_key, tier_rank
from coursesmith.sources import licenses
from coursesmith.sources.base import MissingSource, SourceError
from coursesmith.sources.registry import adapter_class
from coursesmith.sources.wikipedia import WikipediaAdapter

from .fakes import FakeWikiClient, wiki_page


class KeysTest(unittest.TestCase):
    def test_bare_title_is_not_qualified(self):
        self.assertFalse(is_qualified("RFC 9110"))
        self.assertFalse(is_qualified("Consistent hashing"))
        self.assertEqual(split_key("Consistent hashing"), ("", "Consistent hashing"))

    def test_qualified(self):
        k = make_key("rfc", "9110")
        self.assertEqual(k, "rfc>9110")
        self.assertTrue(is_qualified(k))
        self.assertEqual(split_key("gh>o/r/docs/a.md"), ("gh", "o/r/docs/a.md"))

    def test_unsafe_characters_are_encoded(self):
        k = make_key("gh", "o/r/a#b|c[1]{x}.md")
        for ch in "#|[]{}":
            self.assertNotIn(ch, k)
        self.assertEqual(k.count(">"), 1)

    def test_page_part_strips_section(self):
        self.assertEqual(page_part("gh>o/r/README.md#Caching"), "gh>o/r/README.md")
        self.assertEqual(page_part("Soil#Horizons"), "Soil")
        self.assertEqual(page_part(None), "")

    def test_display(self):
        self.assertEqual(display("rfc>9110"), "RFC 9110")
        self.assertEqual(display("gh>o/r/docs/Load_balancing.md"), "Load balancing.md")
        self.assertEqual(display("Soil"), "Soil")


class LicensesTest(unittest.TestCase):
    def test_classify(self):
        cases = {"CC BY-SA 4.0": "cc-by-sa", "CC-BY-4.0": "cc-by", "CC BY 4.0": "cc-by",
                 "CC-BY-NC-ND-4.0": "cc-by-nc-nd", "CC BY-NC-ND 4.0": "cc-by-nc-nd", "CC-BY-NC-SA-4.0": "cc-by-nc-sa",
                 "CC-BY-NC-4.0": "cc-by-nc", "CC-BY-ND-4.0": "cc-by-nd", "CC0-1.0": "public-domain", "MIT": "permissive",
                 "Apache-2.0": "permissive", "GPL-3.0-only": "copyleft", "IETF Trust (BCP 78)": "ietf-trust",
                 "": "unknown", "Custom license": "unknown"}
        for name, cls in cases.items():
            self.assertEqual(licenses.classify(name), cls, name)

    def test_public(self):
        self.assertTrue(licenses.is_public("cc-by-sa"))
        self.assertFalse(licenses.is_public("cc-by-nc-nd"))
        self.assertFalse(licenses.is_public("unknown"))
        self.assertTrue(licenses.is_public("unknown", {"unknown": True}))

    def test_normalize(self):
        self.assertEqual(licenses.normalize("CC BY 4.0")["class"], "cc-by")
        self.assertEqual(licenses.normalize({"spdx": "CC-BY-NC-ND-4.0"})["class"], "cc-by-nc-nd")
        self.assertEqual(licenses.normalize(None, {"name": "x", "class": "cc-by"})["class"], "cc-by")
        self.assertIsNone(licenses.normalize(None))


class TiersTest(unittest.TestCase):
    def test_rank_and_best(self):
        self.assertLess(tier_rank("official"), tier_rank("reference"))
        self.assertLess(tier_rank("reference"), tier_rank("curated"))
        self.assertEqual(best_tier(["curated", "reference", None]), "reference")
        self.assertEqual(best_tier(["curated", "standard"]), "standard")
        self.assertIsNone(best_tier([]))


class RegistryTest(unittest.TestCase):
    def reg(self, sources=None, glob=None):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "registry.yaml"
            if glob:
                p.write_text(glob, encoding="utf-8")
            return Registry(sources, global_path=p)

    def test_wikipedia_is_implicit(self):
        r = self.reg()
        self.assertEqual(len(r.adapters), 1)
        a = r.for_key("Soil")
        self.assertIsInstance(a, WikipediaAdapter)
        self.assertEqual(a.tier, "reference")
        self.assertEqual(a.license["class"], "cc-by-sa")
        self.assertTrue(r.allowed("Soil"))

    def test_unknown_qualified_key_has_no_owner(self):
        r = self.reg()
        self.assertFalse(r.allowed("rfc>9110"))
        with self.assertRaises(MissingSource):
            r.for_key("rfc>9110")

    def test_other_wiki_owns_only_its_keys(self):
        r = self.reg([{"name": "wikibooks", "adapter": "wikipedia",
                       "api_url": "https://en.wikibooks.org/w/api.php", "base": "https://en.wikibooks.org/wiki/"}])
        self.assertEqual(len(r.adapters), 2)
        self.assertTrue(r.allowed("wiki>en.wikibooks.org/Computer_Networks"))
        self.assertFalse(r.allowed("wiki>en.wikiversity.org/Computer_Networks"))
        self.assertIs(r.for_key("Soil"), r.default_wiki)

    def test_unknown_adapter_name(self):
        with self.assertRaises(SourceError):
            adapter_class("nope")

    def test_shared_defaults_apply_and_subject_wins(self):
        glob = ("domains:\n  - {host: en.wikibooks.org, tier: curated, "
                "license: {name: 'CC BY-SA 4.0', class: cc-by-sa}}\n")
        src = {"name": "wb", "adapter": "wikipedia", "api_url": "https://en.wikibooks.org/w/api.php",
               "base": "https://en.wikibooks.org/wiki/"}
        r = self.reg([src], glob)
        self.assertEqual(r.tier("wiki>en.wikibooks.org/X"), "curated")
        r2 = self.reg([dict(src, tier="official")], glob)
        self.assertEqual(r2.tier("wiki>en.wikibooks.org/X"), "official")

    def test_wildcard_domain_default(self):
        glob = "domains:\n  - {host: '*.wikibooks.org', tier: primary}\n"
        src = {"name": "wb", "adapter": "wikipedia", "api_url": "https://en.wikibooks.org/w/api.php"}
        self.assertEqual(self.reg([src], glob).tier("wiki>en.wikibooks.org/X"), "primary")

    def test_missing_global_file_is_fine(self):
        r = Registry(None, global_path=Path("/nonexistent/registry.yaml"))
        self.assertTrue(r.allowed("Soil"))


class WikipediaAdapterTest(unittest.TestCase):
    def adapter(self):
        a = WikipediaAdapter({"name": "wikibooks", "api_url": "https://en.wikibooks.org/w/api.php",
                              "base": "https://en.wikibooks.org/wiki/"})
        return a

    def test_default_keys_are_bare(self):
        a = WikipediaAdapter({})
        self.assertEqual(a.key("Soil"), "Soil")
        self.assertEqual(a.key_for_url("https://en.wikipedia.org/wiki/Soil_pH"), "Soil pH")
        self.assertIsNone(a.key_for_url("https://example.org/x"))

    def test_other_wiki_keys(self):
        a = self.adapter()
        self.assertEqual(a.key("Computer Networks"), "wiki>en.wikibooks.org/Computer_Networks")
        self.assertEqual(a.title_of("wiki>en.wikibooks.org/Computer_Networks"), "Computer Networks")
        self.assertEqual(a.key_for_url("https://en.wikibooks.org/wiki/Computer_Networks"),
                         "wiki>en.wikibooks.org/Computer_Networks")
        self.assertIsNone(a.key_for_url("https://en.wikipedia.org/wiki/Soil"))

    def test_permalink_and_version_label(self):
        a = WikipediaAdapter({})
        src = {"url": "https://en.wikipedia.org/wiki/Soil_pH", "revid": 123}
        self.assertEqual(a.permalink(src), "https://en.wikipedia.org/w/index.php?title=Soil_pH&oldid=123")
        self.assertEqual(a.version_label("123"), "revision 123")

    def test_fetch_other_wiki(self):
        a = self.adapter()
        a.client = FakeWikiClient({"Computer Networks": wiki_page(
            "Computer Networks", "<div class='mw-parser-output'><p>A network connects computers together "
            "so that they can share data and services.</p></div>", revid=77)})
        rec = a.fetch("wiki>en.wikibooks.org/Computer_Networks")
        self.assertEqual(rec["title"], "wiki>en.wikibooks.org/Computer_Networks")
        self.assertEqual(rec["name"], "Computer Networks")
        self.assertEqual(rec["revid"], 77)
        self.assertEqual(rec["version"], "77")
        self.assertEqual(rec["license"]["class"], "cc-by-sa")
        self.assertIn("network connects computers", rec["text"])
        self.assertTrue(rec["url"].startswith("https://en.wikibooks.org/wiki/"))

    def test_fetch_missing_other_wiki(self):
        a = self.adapter()
        a.client = FakeWikiClient({})
        with self.assertRaises(MissingSource):
            a.fetch("wiki>en.wikibooks.org/Nope")

    def test_default_wiki_does_not_fetch_through_adapter(self):
        with self.assertRaises(SourceError):
            WikipediaAdapter({}).fetch("Soil")


if __name__ == "__main__":
    unittest.main()


class GlobTest(unittest.TestCase):
    def test_double_star_means_zero_or_more_directories(self):
        from coursesmith.sources.base import glob_match
        self.assertTrue(glob_match("README.md", ["**/*.md"]))
        self.assertTrue(glob_match("a/b/c.md", ["**/*.md"]))
        self.assertTrue(glob_match("solutions/README.md", ["solutions/**/README.md"]))
        self.assertTrue(glob_match("solutions/a/b/README.md", ["solutions/**/README.md"]))
        self.assertFalse(glob_match("other/README.md", ["solutions/**/README.md"]))
        self.assertTrue(glob_match("README-ja.md", ["**/README-*.md"]))
        self.assertFalse(glob_match("a/b.md", ["*.md"]))  # a single star stays inside one directory
        self.assertTrue(glob_match("b.md", ["*.md"]))
        self.assertTrue(glob_match("docs/x.md", ["docs/**"]))
        self.assertFalse(glob_match("x.md", []))


class YamlDatesTest(unittest.TestCase):
    """sources/registry.yaml writes `verified: 2026-11-18`, which YAML reads as a date; a record carries the license
    and must stay JSON-serializable."""

    def test_normalize_turns_dates_into_text(self):
        import datetime
        lic = licenses.normalize({"name": "CC BY 4.0", "verified": datetime.date(2026, 11, 18)})
        self.assertEqual(lic["verified"], "2026-11-18")

    def test_a_registry_license_survives_a_store_write(self):
        import json
        from coursesmith.crawl.store import Store
        from coursesmith import config
        from .helpers import temp_root
        with temp_root() as root:
            (root / "sources").mkdir()
            config.REGISTRY_PATH.write_text("repos:\n  - {repo: o/r, tier: curated, license: {name: CC BY 4.0, "
                                            "class: cc-by, verified: 2026-11-18}}\n")
            from coursesmith.sources.registry import Registry
            from .fakes import FakeHTTP
            reg = Registry([{"name": "p", "adapter": "github", "repo": "o/r", "ref": "a" * 40}],
                           http=FakeHTTP({f"https://raw.githubusercontent.com/o/r/{'a' * 40}/README.md":
                                          "# R\n\nA readable sentence about a system design topic follows here."}))
            rec = reg.for_key("gh>o/r/README.md").fetch("gh>o/r/README.md")
            self.assertEqual(rec["license"]["verified"], "2026-11-18")
            json.dumps(rec)  # would raise on a date object
            text = rec.pop("text")
            Store().save_page(rec, text)
