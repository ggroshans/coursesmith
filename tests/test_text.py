import json
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

from coursesmith.crawl.clean import clean_html
from coursesmith.extract.split import iter_sentences
from coursesmith.text import brackets
from coursesmith.text import pdf as textpdf
from coursesmith.text.emit import DOC_DROP_SECTIONS, DROP_SECTIONS, Emitter
from coursesmith.text.html import html_to_doc
from coursesmith.text.markdown import markdown_to_doc, strip_front_matter

from .fakes import make_pdf

FIX = Path(__file__).parent / "fixtures"


class LegacyParityTest(unittest.TestCase):
    """clean_html must give exactly what it gave before the emitter was shared: every cached sent_id depends on it."""

    def test_wikipedia_fixture_matches_pre_refactor_output(self):
        html = (FIX / "wiki" / "soil_excerpt.html").read_text(encoding="utf-8")
        want = json.loads((FIX / "wiki" / "soil_excerpt.expected.json").read_text(encoding="utf-8"))
        text, links, cites = clean_html(html, "Soil")
        self.assertEqual(text, want["text"])
        self.assertEqual(links, want["links"])
        self.assertEqual(cites, want["citations"])

    def test_wikipedia_drop_sections_are_unchanged(self):
        self.assertEqual(len(DROP_SECTIONS), 27)
        self.assertNotIn("contents", DROP_SECTIONS)
        self.assertIn("contents", DOC_DROP_SECTIONS)

    def test_legacy_mode_ignores_nested_headings_and_keeps_pre_as_text(self):
        soup = BeautifulSoup("<div><div><h2>Nested</h2><p>Body text here.</p></div><pre>a | b</pre></div>", "html.parser")
        text = Emitter().run(soup.div, "T")
        self.assertNotIn("## Nested", text)
        self.assertIn("a | b", text)


class GenericEmitterTest(unittest.TestCase):
    def emit(self, html, **kw):
        soup = BeautifulSoup(f"<div>{html}</div>", "html.parser")
        em = Emitter(nested_headings=True, code="drop", neutralize=True, **kw)
        return em, em.run(soup.div, "Page")

    def test_nested_headings_are_found(self):
        _, t = self.emit("<section><div><h2>Deep</h2><p>Some prose in the section.</p></div></section>")
        self.assertIn("\n## Deep\nSome prose in the section.", t)

    def test_code_blocks_are_dropped_and_counted(self):
        em, t = self.emit("<p>Run this.</p><pre><code># install\nls | grep x\n</code></pre><p>Done now.</p>")
        self.assertEqual(em.code_blocks, 1)
        self.assertNotIn("install", t)
        self.assertNotIn(" | ", t)

    def test_prose_pipe_and_leading_hash_are_neutralized(self):
        _, t = self.emit("<p>Use a | b to pipe output into the next stage of work.</p><p># not a heading at all</p>")
        rows = list(iter_sentences(t))
        self.assertFalse(any(is_row for _, _, is_row in rows))
        self.assertFalse(any(l.startswith("# not") for l in t.splitlines()))

    def test_real_table_rows_stay_rows(self):
        _, t = self.emit("<table><tr><th>Op</th><th>Cost</th></tr><tr><td>read</td><td>2</td></tr></table>")
        self.assertIn("Op | Cost", t)
        self.assertTrue(any(is_row for _, _, is_row in iter_sentences(t)))

    def test_links_and_anchors(self):
        soup = BeautifulSoup('<div><p>See <a href="/a">the cache layer</a> and <a href="/zz">nothing</a>.</p></div>', "html.parser")
        em = Emitter(resolve_link=lambda a: "doc>x" + a["href"] if a["href"] == "/a" else None, nested_headings=True,
                     collect_anchors=True)
        em.run(soup.div, "P")
        self.assertEqual(em.links, ["doc>x/a"])
        self.assertEqual(em.anchors, {"the cache layer": "doc>x/a"})

    def test_doc_sections_dropped(self):
        _, t = self.emit("<h2>Intro</h2><p>Some real content for the page.</p><h2>Contributing</h2><p>Send PRs.</p>",
                         drop_sections=DOC_DROP_SECTIONS)
        self.assertIn("Some real content", t)
        self.assertNotIn("Send PRs", t)


class HtmlDocTest(unittest.TestCase):
    def test_main_selector_and_chrome_removed(self):
        html = ("<html><head><title>Hashes | Docs</title></head><body><nav>menu menu</nav>"
                "<main><h1>Redis hashes</h1><p>Hashes map string fields to string values.</p>"
                "<aside>ad</aside></main><footer>copyright</footer></body></html>")
        d = html_to_doc(html)
        self.assertEqual(d.name, "Redis hashes")
        self.assertIn("Hashes map string fields", d.text)
        self.assertNotIn("menu", d.text)
        self.assertNotIn("copyright", d.text)
        self.assertTrue(d.text.startswith("# Redis hashes\n"))

    def test_custom_selector(self):
        html = "<body><div id='a'><p>Not this one at all.</p></div><div id='b'><p>Only this content counts.</p></div></body>"
        d = html_to_doc(html, name="X", selector="#b")
        self.assertIn("Only this content", d.text)
        self.assertNotIn("Not this", d.text)


README = """---
title: ignored
---
# System Design Primer

[![Build](https://img.shields.io/b.svg)](https://ci.example/x) ![logo](logo.png)

> Learn how to design large-scale systems.

## Caching

A cache stores copies of data so later requests are served faster.[^1] See [load balancing](docs/lb.md) and
[Wikipedia](https://en.wikipedia.org/wiki/Cache_(computing)).

| Layer | Latency |
|---|---|
| L1 | 1 ns |
| RAM | 100 ns |

```sh
# install it
cat file | grep x
```

- Client caching
  - Browser cache
- CDN caching

## Contributing

Send pull requests.

# Second title

Text under a later H1 stays.
"""


class MarkdownTest(unittest.TestCase):
    def resolve(self, a):
        h = a["href"]
        if h.startswith("docs/"):
            return "gh>o/r/" + h
        if "wikipedia.org/wiki/" in h:
            return h.split("/wiki/")[1].replace("_", " ")
        return None

    def doc(self):
        return markdown_to_doc(README, resolve_link=self.resolve)

    def test_name_and_structure(self):
        d = self.doc()
        self.assertEqual(d.name, "System Design Primer")
        self.assertTrue(d.text.startswith("# System Design Primer\n"))
        self.assertIn("## Caching", d.text)
        self.assertIn("## Second title", d.text)  # a later H1 is demoted to a section
        self.assertNotIn("Contributing", d.text)
        self.assertNotIn("Send pull requests", d.text)

    def test_badges_and_code_are_gone(self):
        d = self.doc()
        self.assertNotIn("shields", d.text)
        self.assertNotIn("install it", d.text)
        self.assertNotIn("grep", d.text)
        self.assertEqual(d.code_blocks, 1)

    def test_table_and_lists(self):
        d = self.doc()
        self.assertIn("Layer | Latency", d.text)
        self.assertIn("RAM | 100 ns", d.text)
        self.assertIn("- Client caching\n  - Browser cache\n- CDN caching", d.text)

    def test_links_resolve_across_sources(self):
        d = self.doc()
        self.assertEqual(d.links, ["gh>o/r/docs/lb.md", "Cache (computing)"])
        self.assertEqual(d.anchors["load balancing"], "gh>o/r/docs/lb.md")

    def test_front_matter_stripped(self):
        self.assertFalse(strip_front_matter(README).startswith("---"))

    def test_sentences_come_out_clean(self):
        d = self.doc()
        sents = [s for _, s, _ in iter_sentences(d.text)]
        self.assertTrue(any(s.startswith("A cache stores copies") for s in sents))
        self.assertFalse(any(s.startswith("# ") for s in sents))


RFC_RAW = """
7.  References

7.1.  Normative References

   [RFC2119]  Bradner, S., "Key words for use in RFCs to Indicate
              Requirement Levels", BCP 14, RFC 2119,
              DOI 10.17487/RFC2119, March 1997,
              <https://www.rfc-editor.org/info/rfc2119>.

   [Fielding2000]  Fielding, R., "Architectural Styles and the Design of
              Network-based Software Architectures", 2000.
"""


class BracketsTest(unittest.TestCase):
    def test_parse_references(self):
        refs = brackets.parse_references(RFC_RAW)
        self.assertEqual(set(refs), {"RFC2119", "Fielding2000"})
        self.assertIn("Requirement Levels", refs["RFC2119"])
        self.assertIn("March 1997", refs["RFC2119"])

    def test_number_citations(self):
        refs = brackets.parse_references(RFC_RAW)
        body = "Servers MUST follow [RFC2119]. A cache is explained in [Fielding2000]. Again [RFC2119]. Array a[0] stays."
        text, cits = brackets.number_citations(body, refs)
        self.assertEqual(text, "Servers MUST follow [^1]. A cache is explained in [^2]. Again [^1]. Array a[0] stays.")
        self.assertEqual([c["n"] for c in cits], [1, 2])
        w = cits[0]["works"][0]
        self.assertEqual((w["doi"], w["rfc"], w["year"]), ("10.17487/rfc2119", "2119", 1997))
        self.assertEqual(w["url"], "https://www.rfc-editor.org/info/rfc2119")
        self.assertEqual(cits[1]["works"][0]["year"], 2000)


class PdfTest(unittest.TestCase):
    PAGES = [
        ["Acme Handbook", "1 Introduction", "A consistent hash ring maps keys to nodes so adding a node moves few", "keys. This is the core idea."],
        ["Acme Handbook", "1.1 Virtual nodes", "Each server owns many points on the ring, which evens the load across ser-", "vers when one fails."],
        ["Acme Handbook", "2 Replication", "Replicas keep copies of each key on the next servers around the ring."],
    ]

    def test_structure_from_pages(self):
        pages = ["\n".join(p) + "\n" for p in self.PAGES]
        t = textpdf.structure(pages, "Handbook")
        self.assertTrue(t.startswith("# Handbook\n"))
        self.assertIn("## 1 Introduction", t)
        self.assertIn("### 1.1 Virtual nodes", t)
        self.assertIn("## 2 Replication", t)
        self.assertNotIn("Acme Handbook", t)  # running header repeated on every page
        self.assertIn("across servers when one fails", t)  # hyphenated at the line break

    def test_pdf_round_trip(self):
        data = make_pdf(self.PAGES)
        flat = textpdf.flat_text(data)
        self.assertIn("consistent hash ring", flat)
        text, title = textpdf.pdf_to_text(data, "Handbook")
        self.assertIn("## 1 Introduction", text)
        self.assertIn("Replicas keep copies", text)


if __name__ == "__main__":
    unittest.main()
