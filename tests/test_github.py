import base64
import json
import unittest

from coursesmith.sources import licenses
from coursesmith.sources.base import MissingSource, SourceError
from coursesmith.sources.github import ADAPTER, GithubAdapter, plain_to_doc
from coursesmith.sources.registry import Registry

from .fakes import FIXTURES, FakeHTTP

GH = FIXTURES / "github"
SHA = "ae9bbd7b02d90b9866215de185217d33f39ab733"
RAW = f"https://raw.githubusercontent.com/donnemartin/system-design-primer/{SHA}"
API = "https://api.github.com"


def adapter(**cfg):
    http = FakeHTTP({
        f"{RAW}/README.md": GH / "primer.README.md",
        f"{RAW}/solutions/system_design/pastebin/README.md": GH / "primer.pastebin.md",
        f"{API}/repos/donnemartin/system-design-primer/commits/master": GH / "primer.commit.json",
        f"{API}/repos/donnemartin/system-design-primer/license?ref={SHA}": GH / "primer.license.json",
        f"{API}/repos/donnemartin/system-design-primer/git/trees/{SHA}?recursive=1": GH / "primer.tree.json",
    })
    c = {"name": "system-design-primer", "adapter": "github", "repo": "donnemartin/system-design-primer", "ref": SHA,
         "include": ["README.md", "solutions/**/README.md"], "exclude": ["**/README-*.md"], **cfg}
    return GithubAdapter(c, http=http)


class KeysAndAllowlistTest(unittest.TestCase):
    def test_owns_and_allowed(self):
        a = adapter()
        k = "gh>donnemartin/system-design-primer/README.md"
        self.assertTrue(a.owns(k))
        self.assertTrue(a.allowed(k))
        self.assertTrue(a.allowed("gh>donnemartin/system-design-primer/solutions/system_design/pastebin/README.md"))
        self.assertFalse(a.allowed("gh>donnemartin/system-design-primer/README-ja.md"))  # translation
        self.assertFalse(a.allowed("gh>donnemartin/system-design-primer/CONTRIBUTING.md"))  # not included
        self.assertFalse(a.allowed("gh>donnemartin/system-design-primer/solutions/a/code.py"))
        self.assertFalse(a.owns("gh>someone/else/README.md"))

    def test_relative_links(self):
        a = adapter()
        base = "gh>donnemartin/system-design-primer/solutions/system_design/pastebin/README.md"
        pre = "gh>donnemartin/system-design-primer/"
        self.assertEqual(a.key_for_url("../mint/README.md", base), pre + "solutions/system_design/mint/README.md")
        self.assertEqual(a.key_for_url("../mint/", base), pre + "solutions/system_design/mint/README.md")
        self.assertEqual(a.key_for_url("/README.md", base), pre + "README.md")
        self.assertIsNone(a.key_for_url("#study-guide", base))
        self.assertIsNone(a.key_for_url("pastebin.png", base))
        self.assertIsNone(a.key_for_url("../../../../../etc/passwd", base))
        self.assertIsNone(a.key_for_url("mailto:a@b.c", base))

    def test_absolute_links(self):
        a = adapter()
        pre = "gh>donnemartin/system-design-primer/"
        self.assertEqual(a.key_for_url("https://github.com/donnemartin/system-design-primer/blob/master/README.md"), pre + "README.md")
        self.assertEqual(a.key_for_url(f"https://raw.githubusercontent.com/donnemartin/system-design-primer/master/a/b.md"), pre + "a/b.md")
        self.assertIsNone(a.key_for_url("https://github.com/other/repo/blob/master/README.md"))
        self.assertEqual(a.key_for_url("https://en.wikipedia.org/wiki/Cache_(computing)"), "Cache (computing)")
        self.assertIsNone(a.key_for_url("https://en.wikipedia.org/wiki/File:X.png"))
        self.assertIsNone(a.key_for_url("https://example.org/x.md"))

    def test_repo_must_be_owner_slash_name(self):
        with self.assertRaises(SourceError):
            GithubAdapter({"repo": "justaname"})


class FetchTest(unittest.TestCase):
    def test_readme_record(self):
        rec = adapter().fetch("gh>donnemartin/system-design-primer/README.md")
        self.assertEqual(rec["name"], "The System Design Primer")
        self.assertEqual(rec["version"], SHA)
        self.assertEqual(rec["url"], f"https://github.com/donnemartin/system-design-primer/blob/{SHA}/README.md")
        self.assertEqual(rec["tier"], "curated")
        self.assertEqual(rec["source"], "system-design-primer")
        self.assertTrue(rec["text"].startswith("# The System Design Primer\n"))
        self.assertIn("## Motivation", rec["text"])
        self.assertNotIn("<img", rec["text"])
        self.assertNotIn("```", rec["text"])
        self.assertEqual(rec["meta"]["path"], "README.md")

    def test_links_are_keys_and_lead_links_come_first(self):
        rec = adapter().fetch("gh>donnemartin/system-design-primer/README.md")
        self.assertIn("gh>donnemartin/system-design-primer/TRANSLATIONS.md", rec["body_links"])
        self.assertNotIn("gh>donnemartin/system-design-primer/README.md", rec["body_links"])
        # the English/translation switcher sits before the first section heading
        self.assertIn("gh>donnemartin/system-design-primer/README-ja.md", rec["lead_links"])
        self.assertTrue(set(rec["lead_links"]) <= set(rec["body_links"]))

    def test_solution_page_named_with_repo(self):
        rec = adapter().fetch("gh>donnemartin/system-design-primer/solutions/system_design/pastebin/README.md")
        self.assertIn("(system-design-primer)", rec["name"])
        self.assertIn("pastebin", rec["name"].lower())
        self.assertEqual(rec["source_id"], "donnemartin/system-design-primer/solutions/system_design/pastebin/README.md")

    def test_missing_file(self):
        with self.assertRaises(MissingSource):
            adapter().fetch("gh>donnemartin/system-design-primer/NOPE.md")

    def test_branch_ref_resolves_to_commit(self):
        a = adapter(ref="master")
        self.assertEqual(a.sha(), SHA)
        self.assertEqual(a.fetch("gh>donnemartin/system-design-primer/README.md")["version"], SHA)

    def test_version_label(self):
        self.assertEqual(adapter().version_label(SHA), "commit ae9bbd7")

    def test_plain_text_and_rst(self):
        t = plain_to_doc("Title here\n==========\n\nFirst paragraph\nwraps.\n\nSecond.", "doc.rst")
        self.assertIn("## Title here", t)
        self.assertIn("First paragraph wraps.", t)


class CheckTest(unittest.TestCase):
    def test_license_read_from_the_file_when_github_cannot_detect_one(self):
        res = adapter(license={"name": "CC BY 4.0"}).check()
        self.assertEqual(res["problems"], [])
        self.assertEqual(res["evidence"]["license"]["class"], "cc-by")
        self.assertEqual(res["evidence"]["license"]["spdx"], "NOASSERTION")
        self.assertIn("Creative Commons Attribution 4.0", res["evidence"]["license"]["head"])
        self.assertEqual(len(res["evidence"]["license"]["sha256"]), 64)
        self.assertGreater(res["evidence"]["matched_files"], 5)

    def test_declared_license_must_match_the_file(self):
        res = adapter(license={"name": "MIT"}).check()
        self.assertTrue(any("declares MIT" in p for p in res["problems"]))

    def test_undeclared_license_is_a_note(self):
        res = adapter().check()
        self.assertTrue(any("no license declared" in n for n in res["notes"]))

    def test_branch_ref_note_suggests_pin(self):
        res = adapter(ref="master", license={"name": "CC BY 4.0"}).check()
        self.assertTrue(any(f"ref: {SHA}" in n for n in res["notes"]))

    def test_no_file_matches(self):
        res = adapter(include=["nothing/**.md"], license={"name": "CC BY 4.0"}).check()
        self.assertTrue(any("match no files" in p for p in res["problems"]))

    def test_unknown_repo_reports_problem(self):
        a = GithubAdapter({"repo": "x/y", "ref": "0" * 40}, http=FakeHTTP({}))
        res = a.check()
        self.assertTrue(res["problems"])

    def test_files_lists_matches(self):
        files = adapter().files()
        self.assertIn("README.md", files)
        self.assertIn("solutions/system_design/pastebin/README.md", files)
        self.assertNotIn("README-ja.md", files)


class LicenseTextTest(unittest.TestCase):
    def test_detect_from_text(self):
        self.assertEqual(licenses.detect_from_text("Creative Commons Attribution 4.0 International"), "cc-by")
        self.assertEqual(licenses.detect_from_text("Attribution-NonCommercial-NoDerivatives 4.0 International"), "cc-by-nc-nd")
        self.assertEqual(licenses.detect_from_text("Permission is hereby granted, free of charge, to any person"), "permissive")
        self.assertEqual(licenses.detect_from_text("hello"), "unknown")


class DiscoverTest(unittest.TestCase):
    def test_discover_maps_search_results(self):
        a = adapter()
        q = "system%20design%20stars:>200"
        a.http.mapping[f"{API}/search/repositories?q={q}&sort=stars&order=desc&per_page=5"] = json.dumps({"items": [
            {"full_name": "a/b", "name": "b", "html_url": "https://github.com/a/b", "description": "d",
             "stargazers_count": 900, "forks_count": 50, "pushed_at": "2026-10-01T00:00:00Z",
             "license": {"spdx_id": "CC-BY-4.0"}, "topics": ["x"], "owner": {"type": "User"}, "default_branch": "main"}]})
        out = a.discover("system design", limit=5)
        self.assertEqual(out[0]["repo"], "a/b")
        self.assertEqual(out[0]["evidence"]["stars"], 900)
        self.assertEqual(out[0]["evidence"]["license_spdx"], "CC-BY-4.0")

    def test_contributors_from_link_header(self):
        a = adapter()

        class H(FakeHTTP):
            def get(self, url, **kw):
                return ("[{}]", {"link": '<https://api.github.com/x?per_page=1&anon=true&page=240>; rel="last"'}) \
                    if kw.get("want_headers") else "[{}]"
        a._http = H()
        self.assertEqual(a.contributors("a/b"), 240)


class RegistryTest(unittest.TestCase):
    def test_registry_builds_github(self):
        r = Registry([{"name": "p", "adapter": "github", "repo": "donnemartin/system-design-primer",
                       "include": ["README.md"]}])
        self.assertIs(type(r.for_key("gh>donnemartin/system-design-primer/README.md")), ADAPTER)
        self.assertTrue(r.allowed("gh>donnemartin/system-design-primer/README.md"))
        self.assertFalse(r.allowed("gh>donnemartin/system-design-primer/docs/other.md"))
        self.assertFalse(r.allowed("gh>other/repo/README.md"))
        self.assertEqual(r.tier("gh>donnemartin/system-design-primer/README.md"), "curated")


if __name__ == "__main__":
    unittest.main()


class SplitTest(unittest.TestCase):
    COURSE = (GH / "course.md")

    def adapter(self, **cfg):
        http = FakeHTTP({f"{RAW}/course.md": self.COURSE, f"{RAW}/README.md": GH / "primer.README.md",
                         f"{API}/repos/donnemartin/system-design-primer/commits/master": GH / "primer.commit.json"})
        c = {"name": "course", "adapter": "github", "repo": "donnemartin/system-design-primer", "ref": SHA,
             "include": ["course.md", "README.md"], "split": {"course.md": 1}, **cfg}
        return GithubAdapter(c, http=http)

    def test_slugs_match_githubs_anchors(self):
        from coursesmith.sources.github import slug_of
        self.assertEqual(slug_of("Load Balancing"), "load-balancing")
        self.assertEqual(slug_of("Content Delivery Network (CDN)"), "content-delivery-network-cdn")
        self.assertEqual(slug_of("SSL, TLS, mTLS"), "ssl-tls-mtls")
        self.assertEqual(slug_of("What's an API?"), "whats-an-api")
        self.assertEqual(slug_of("`code` and *emphasis*"), "code-and-emphasis")

    def test_split_markdown(self):
        from coursesmith.sources.github import split_markdown
        parts = split_markdown(self.COURSE.read_text(), 1)
        self.assertEqual([p[0] for p in parts], ["system-design-course", "load-balancing", "caching", "caching-1",
                                                 "content-delivery-network-cdn"])
        lb = dict((p[0], p) for p in parts)["load-balancing"]
        self.assertTrue(lb[2].startswith("# Load Balancing\n"))
        self.assertIn("## Types", lb[2])  # its own subsections stay, one level down from the chapter
        self.assertNotIn("A cache stores copies", lb[2])  # the next chapter is not part of it
        self.assertIn("# not a heading", lb[2])  # a comment inside a code fence is not a heading

    def test_split_level_two_shifts_headings_up(self):
        from coursesmith.sources.github import split_markdown
        parts = split_markdown("# T\n\n## A\n\ntext a\n\n### A1\n\nmore\n\n## B\n\ntext b\n", 2)
        self.assertEqual([p[0] for p in parts], ["a", "b"])
        self.assertEqual(parts[0][2].split("\n")[0], "# A")
        self.assertIn("\n## A1\n", parts[0][2])

    def test_keys_and_allowlist(self):
        a = self.adapter()
        pre = "gh>donnemartin/system-design-primer/"
        self.assertEqual(a.key("course.md", "caching"), pre + "course.md::caching")
        self.assertEqual((a.path_of(pre + "course.md::caching"), a.part_of(pre + "course.md::caching")), ("course.md", "caching"))
        self.assertTrue(a.allowed(pre + "course.md::caching"))
        self.assertFalse(a.allowed(pre + "course.md"))  # the whole split file would count its text twice
        self.assertTrue(a.allowed(pre + "README.md"))  # an unsplit file is a page as before
        self.assertFalse(a.allowed(pre + "README.md::intro"))  # only a split file has sections
        self.assertFalse(a.allowed(pre + "other.md::x"))

    def test_fetch_a_section(self):
        rec = self.adapter().fetch("gh>donnemartin/system-design-primer/course.md::caching")
        self.assertEqual(rec["name"], "Caching (system-design-primer)")
        self.assertTrue(rec["text"].startswith("# Caching\n"))
        self.assertIn("A cache stores copies of data", rec["text"])
        self.assertIn("## Eviction policies", rec["text"])
        self.assertNotIn("A load balancer spreads", rec["text"])
        self.assertEqual(rec["url"], f"https://github.com/donnemartin/system-design-primer/blob/{SHA}/course.md#caching")
        self.assertEqual((rec["meta"]["part"], rec["meta"]["path"]), ("caching", "course.md"))
        self.assertEqual(rec["source_id"], "donnemartin/system-design-primer/course.md::caching")

    def test_anchor_links_become_section_keys(self):
        rec = self.adapter().fetch("gh>donnemartin/system-design-primer/course.md::load-balancing")
        pre = "gh>donnemartin/system-design-primer/course.md::"
        self.assertEqual(rec["body_links"], [pre + "caching", pre + "content-delivery-network-cdn"])
        self.assertEqual(rec["anchors"]["caching"], pre + "caching")

    def test_repeated_title_has_a_numbered_section(self):
        rec = self.adapter().fetch("gh>donnemartin/system-design-primer/course.md::caching-1")
        self.assertIn("second chapter with the same title", rec["text"])

    def test_missing_section(self):
        with self.assertRaises(MissingSource):
            self.adapter().fetch("gh>donnemartin/system-design-primer/course.md::nope")

    def test_links_from_other_files_to_a_split_file(self):
        a = self.adapter()
        base = "gh>donnemartin/system-design-primer/README.md"
        pre = "gh>donnemartin/system-design-primer/"
        self.assertEqual(a.key_for_url("course.md#Caching", base), pre + "course.md::caching")
        self.assertIsNone(a.key_for_url("course.md", base))  # which section? the link does not say
        self.assertEqual(a.key_for_url("#anything", base), None)  # README.md is not split

    def test_parts_listing(self):
        slugs = [p[0] for p in self.adapter().parts("course.md")]
        self.assertEqual(slugs[:3], ["system-design-course", "load-balancing", "caching"])


class PartsCommandTest(unittest.TestCase):
    def test_lists_section_keys(self):
        from coursesmith.sources import parts
        from coursesmith.sources.registry import Registry
        h = FakeHTTP({f"{RAW}/course.md": GH / "course.md"})
        reg = Registry([{"name": "course", "adapter": "github", "repo": "donnemartin/system-design-primer", "ref": SHA,
                         "include": ["course.md"], "split": {"course.md": 1}}], http=h)
        lines = []
        self.assertEqual(parts.run(None, registry=reg, log=lines.append), 5)
        self.assertIn("gh>donnemartin/system-design-primer/course.md::load-balancing | Load Balancing |", "\n".join(lines))
        self.assertTrue(lines[0].startswith("# course: course.md at ae9bbd7, 5 sections split at level 1"))
        lines.clear()
        self.assertEqual(parts.run(None, "other", registry=reg, log=lines.append), 0)
        self.assertIn("no split sources named 'other'", lines[0])


class LicenseFilesAsFoundTest(unittest.TestCase):
    """The license texts of the three system design guides, as their repositories carry them."""

    def test_html_snippet_with_a_cc_link_and_abbreviation(self):
        bbg = ('## License\n\n<p xmlns:cc="http://creativecommons.org/ns#" >This work is licensed under '
               '<a href="http://creativecommons.org/licenses/by-nc-nd/4.0/" target="_blank">CC BY-NC-ND 4.0</a></p>')
        self.assertEqual(licenses.detect_from_text(bbg), "cc-by-nc-nd")

    def test_primer_license_txt(self):
        txt = ("I am providing code and resources in this repository to you under an open source license.\n\n"
               "Copyright 2017 Donne Martin\n\nCreative Commons Attribution 4.0 International License (CC BY 4.0)\n\n"
               "http://creativecommons.org/licenses/by/4.0/\n")
        self.assertEqual(licenses.detect_from_text(txt), "cc-by")

    def test_full_legal_code(self):
        self.assertEqual(licenses.detect_from_text("Attribution-NonCommercial-NoDerivatives 4.0 International\n=====\n"),
                         "cc-by-nc-nd")

    def test_cc_legal_text_ending_with_cc0_boilerplate_is_not_public_domain(self):
        # the real LICENSE of karanpratapsingh/system-design: titled NC-ND, its last pages mention the CC0 dedication
        text = (GH / "karan.license.txt").read_text()
        self.assertIn("CC0", text)
        self.assertEqual(licenses.detect_from_text(text), "cc-by-nc-nd")

    def test_earliest_mention_decides(self):
        self.assertEqual(licenses.detect_from_text("MIT License. Docs under CC BY 4.0."), "permissive")
        self.assertEqual(licenses.detect_from_text("Docs under CC BY 4.0. Code: MIT License"), "cc-by")

    def test_abbreviations_and_urls(self):
        for text, cls in (("licensed under CC BY-SA 4.0", "cc-by-sa"), ("CC-BY-NC 3.0", "cc-by-nc"),
                          ("see https://creativecommons.org/licenses/by-sa/4.0/", "cc-by-sa"),
                          ("https://creativecommons.org/publicdomain/zero/1.0/", "public-domain"),
                          ("CC0 1.0 Universal", "public-domain"), ("CC BY 4.0", "cc-by")):
            self.assertEqual(licenses.detect_from_text(text), cls, text)

    def test_the_cc_license_in_a_readme_is_not_confused_with_a_word_that_contains_cc(self):
        self.assertEqual(licenses.detect_from_text("Tuned for acc by tuning; nothing about licensing."), "unknown")
