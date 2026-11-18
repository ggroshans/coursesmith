import json
import unittest

from coursesmith.sources.base import MissingSource
from coursesmith.sources.rfc import ADAPTER, RfcAdapter, parse_rfc_text
from coursesmith.sources.registry import Registry

from .fakes import FIXTURES, FakeHTTP

RFC = FIXTURES / "rfc"


def adapter(**cfg):
    http = FakeHTTP({
        "https://www.rfc-editor.org/rfc/rfc2119.txt": RFC / "rfc2119.txt",
        "https://www.rfc-editor.org/rfc/rfc2119.json": RFC / "rfc2119.json",
        "https://www.rfc-editor.org/rfc/rfc2616.json": RFC / "rfc2616.json",
    })
    return RfcAdapter({"name": "rfcs", "adapter": "rfc", **cfg}, http=http)


class RfcParseTest(unittest.TestCase):
    def setUp(self):
        self.doc = parse_rfc_text((RFC / "rfc2119.txt").read_text(), 2119, "Key words for use in RFCs to Indicate Requirement Levels")

    def test_title_and_structure(self):
        t = self.doc["text"]
        self.assertTrue(t.startswith("# RFC 2119: Key words for use in RFCs to Indicate Requirement Levels\n"))
        self.assertIn("## Abstract", t)
        self.assertNotIn("Status of this Memo", t)
        self.assertNotIn("Network Working Group", t)

    def test_page_furniture_is_gone(self):
        t = self.doc["text"]
        self.assertNotIn("[Page 1]", t)
        self.assertNotIn("RFC Key Words    ", t)
        self.assertNotIn("\f", t)

    def test_paragraphs_are_single_lines(self):
        t = self.doc["text"]
        self.assertIn("In many standards track documents several words are used to signify the requirements in "
                      "the specification.", t)

    def test_numbered_items_stay_as_prose(self):
        # "1. MUST   This word..." is a paragraph in this RFC, not a section heading
        self.assertIn("MUST This word, or the terms", self.doc["text"])
        self.assertIn("SHOULD NOT This phrase, or the phrase", self.doc["text"])

    def test_old_single_space_headings(self):
        t = self.doc["text"]
        self.assertIn("\n## 6. Guidance in the use of these Imperatives\n", t)
        self.assertIn("\n## 7. Security Considerations\n", t)
        self.assertNotIn("Acknowledgments", t)  # dropped section
        self.assertNotIn("1350 Mass. Ave.", t)  # the author's address is dropped too

    def test_references_dropped_and_self_link_excluded(self):
        self.assertNotIn("Normative", self.doc["text"])
        self.assertNotIn("rfc>2119", self.doc["links"])


SAMPLE = """
Network Working Group                                         A. Writer
Request for Comments: 9999                                  Example Inc.
Category: Standards Track                                     March 2024


                      A Tiny Protocol

Abstract

   This document defines a tiny protocol that builds on RFC 7230 and
   explains how a server answers a request within a deadline.

1.  Introduction

   The protocol follows [RFC2119] and extends HTTP caching from RFC 9111.
   Servers should reply fast.

   o  Reply within 200 ms
   o  Keep connections alive
      across requests

   +-----+-----+
   | A   | B   |
   +-----+-----+

2.  Rules

2.1.  Timeouts

   A client MUST wait 30 seconds before it retries a request.

Writer                   Standards Track                        [Page 2]

RFC 9999                   Tiny Protocol                     March 2024

3.  References

3.1.  Normative References

   [RFC2119]  Bradner, S., "Key words for use in RFCs to Indicate
              Requirement Levels", BCP 14, RFC 2119, March 1997.
"""


class RfcSampleTest(unittest.TestCase):
    def setUp(self):
        self.doc = parse_rfc_text(SAMPLE, 9999, "A Tiny Protocol")

    def test_headings_and_levels(self):
        t = self.doc["text"]
        self.assertIn("\n## 1. Introduction\n", t)
        self.assertIn("\n## 2. Rules\n", t)
        self.assertIn("\n### 2.1. Timeouts\n", t)
        self.assertNotIn("References", t)

    def test_lists_and_code(self):
        t = self.doc["text"]
        self.assertIn("- Reply within 200 ms", t)
        self.assertIn("- Keep connections alive across requests", t)
        self.assertNotIn("+-----+", t)
        self.assertEqual(self.doc["code_blocks"], 1)

    def test_citations_and_links(self):
        self.assertEqual(self.doc["links"], ["rfc>7230", "rfc>2119", "rfc>9111"])  # order of appearance
        self.assertEqual(self.doc["lead_links"], ["rfc>7230", "rfc>2119", "rfc>9111"])
        t = self.doc["text"]
        self.assertIn("follows [^1] and", t)
        self.assertEqual(self.doc["citations"][0]["works"][0]["rfc"], "2119")
        self.assertEqual(self.doc["anchors"]["RFC 9111"], "rfc>9111")

    def test_no_page_headers_in_body(self):
        self.assertNotIn("Page 2", self.doc["text"])
        self.assertNotIn("Tiny Protocol     ", self.doc["text"])


class RfcAdapterTest(unittest.TestCase):
    def test_owns_and_urls(self):
        a = adapter()
        self.assertTrue(a.owns("rfc>9110"))
        self.assertFalse(a.owns("RFC 9110"))
        self.assertFalse(a.owns("rfc>abc"))
        self.assertEqual(a.key_for_url("https://www.rfc-editor.org/rfc/rfc9110.html"), "rfc>9110")
        self.assertEqual(a.key_for_url("https://datatracker.ietf.org/doc/html/rfc7231"), "rfc>7231")
        self.assertEqual(a.key_for_url("RFC 6455"), "rfc>6455")
        self.assertIsNone(a.key_for_url("https://example.org/rfc/1"))

    def test_fetch_record(self):
        rec = adapter().fetch("rfc>2119")
        self.assertEqual(rec["title"], "rfc>2119")
        self.assertEqual(rec["name"], "RFC 2119: Key words for use in RFCs to Indicate Requirement Levels")
        self.assertEqual(rec["version"], "March 1997")
        self.assertEqual(rec["url"], "https://www.rfc-editor.org/rfc/rfc2119")
        self.assertEqual(rec["tier"], "standard")
        self.assertEqual(rec["license"]["class"], "ietf-trust")
        self.assertEqual(rec["meta"]["status"], "BEST CURRENT PRACTICE")
        self.assertEqual(rec["adapter"], "rfc")

    def test_missing_rfc(self):
        with self.assertRaises(MissingSource):
            adapter().fetch("rfc>9")

    def test_seeds_from_ids(self):
        self.assertEqual(adapter(ids=[9110, 6455]).seeds(), ["rfc>9110", "rfc>6455"])

    def test_check_warns_about_obsolete(self):
        res = adapter(ids=[2616, 2119]).check()
        self.assertTrue(any("RFC 2616 is obsoleted by RFC7230" in n for n in res["notes"]))
        self.assertEqual(res["problems"], [])
        self.assertEqual(adapter(ids=[1]).check()["problems"][0][:5], "RFC 1")

    def test_discover(self):
        a = adapter()
        a.http.mapping["https://datatracker.ietf.org/api/v1/doc/document/"] = json.dumps(
            {"objects": [{"rfc": "9110", "title": "HTTP Semantics", "abstract": "The HTTP protocol."}]})
        found = a.discover("HTTP semantics")
        self.assertEqual(found[0]["key"], "rfc>9110")
        self.assertEqual(found[0]["tier"], "standard")

    def test_registry_builds_it(self):
        r = Registry([{"name": "rfcs", "adapter": "rfc", "ids": [2119]}])
        self.assertIs(type(r.for_key("rfc>2119")), ADAPTER)
        self.assertTrue(r.allowed("rfc>9110"))
        self.assertEqual(r.tier("rfc>2119"), "standard")


if __name__ == "__main__":
    unittest.main()
