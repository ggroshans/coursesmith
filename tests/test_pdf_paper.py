import json
import unittest

from coursesmith.sources.base import MissingSource, SourceError
from coursesmith.sources.paper import PaperAdapter, norm_arxiv, norm_doi, parse_arxiv
from coursesmith.sources.pdf import PdfAdapter
from coursesmith.sources.registry import Registry
from coursesmith.verify import extsrc

from .fakes import FIXTURES, FakeHTTP, make_pdf
from .helpers import temp_root

URL = "https://example.org/files/handbook.pdf"
PAGES = [
    ["Acme Handbook", "1 Introduction", "A consistent hash ring maps keys to nodes so adding a node moves few keys.",
     "Every server owns many points on the ring, which evens out the load across all of the servers."],
    ["Acme Handbook", "2 Replication", "Replicas keep copies of each key on the next servers around the ring, so one",
     "server failure never loses data. Writes go to the primary and then to every replica in turn."],
    ["Acme Handbook", "3 Failure", "A failed server is detected by missed heartbeats and removed from the ring after a timeout."],
]


def pdf_adapter(**cfg):
    http = FakeHTTP({URL: make_pdf(PAGES)})
    return PdfAdapter({"name": "acme", "adapter": "pdf", "files": [{"url": URL, "name": "Acme Handbook"}],
                       "license": {"name": "CC BY 4.0"}, **cfg}, http=http)


class PdfAdapterTest(unittest.TestCase):
    KEY = "pdf>acme/handbook.pdf"

    def test_keys_and_allowlist(self):
        a = pdf_adapter()
        self.assertEqual(a.seeds(), [self.KEY])
        self.assertTrue(a.allowed(self.KEY))
        self.assertFalse(a.allowed("pdf>acme/other.pdf"))
        self.assertFalse(a.owns("pdf>zzz/handbook.pdf"))
        self.assertEqual(a.key_for_url(URL), self.KEY)
        self.assertIsNone(a.key_for_url("https://example.org/x.pdf"))

    def test_fetch(self):
        rec = pdf_adapter().fetch(self.KEY)
        self.assertEqual(rec["name"], "Acme Handbook")
        self.assertEqual(rec["url"], URL)
        self.assertEqual(len(rec["version"]), 16)
        self.assertTrue(rec["text"].startswith("# Acme Handbook\n"))
        self.assertIn("## 1 Introduction", rec["text"])
        self.assertEqual(rec["tier"], "primary")
        self.assertEqual(rec["meta"]["headings"], 3)

    def test_missing_file(self):
        a = pdf_adapter()
        a.http.mapping[URL] = None
        with self.assertRaises(MissingSource):
            a.fetch(self.KEY)

    def test_pdf_without_text_is_rejected(self):
        a = pdf_adapter()
        a.http.mapping[URL] = make_pdf([[]])
        with self.assertRaises(SourceError):
            a.fetch(self.KEY)

    def test_needs_files_and_unique_names(self):
        with self.assertRaises(SourceError):
            PdfAdapter({"name": "x"})
        with self.assertRaises(SourceError):
            PdfAdapter({"name": "x", "urls": ["https://a.org/m.pdf", "https://b.org/m.pdf"]})

    def test_check_requires_license(self):
        self.assertEqual(pdf_adapter().check()["problems"], [])
        self.assertTrue(any("declare the license" in p for p in pdf_adapter(license=None).check()["problems"]))

    def test_registry(self):
        r = Registry([{"name": "acme", "adapter": "pdf", "urls": [URL]}])
        self.assertTrue(r.allowed(self.KEY))
        self.assertEqual(r.tier(self.KEY), "primary")


def inverted(text):
    inv = {}
    for i, w in enumerate(text.split()):
        inv.setdefault(w, []).append(i)
    return inv


def openalex(doi, title, abstract, **extra):
    r = {"id": "https://openalex.org/W1", "doi": f"https://doi.org/{doi}", "title": title, "publication_year": 2010,
         "publication_date": "2010-06-10", "type": "article",
         "primary_location": {"source": {"display_name": "SIGMOD"}},
         "best_oa_location": extra.get("oa"), "authorships": [{"author": {"display_name": "Avinash Lakshman"}},
                                                              {"author": {"display_name": "Prashant Malik"}}],
         "cited_by_count": 5000, "abstract_inverted_index": inverted(abstract) if abstract else None}
    return r


DOI = "10.1145/1773912.1773922"
ABSTRACT = "Cassandra is a distributed storage system for managing very large amounts of structured data."


def paper_adapter(works=None, **cfg):
    works = works if works is not None else [openalex(DOI, "Cassandra: a decentralized structured storage system", ABSTRACT)]

    def oa(params):
        if "search" in params:
            return json.dumps({"results": works})
        wanted = params.get("filter", "")[4:].split("|")
        return json.dumps({"results": [w for w in works if w["doi"].replace("https://doi.org/", "") in wanted]})
    http = FakeHTTP({"https://api.openalex.org/works": oa,
                     "https://export.arxiv.org/api/query": FIXTURES / "paper" / "arxiv.xml"})
    return PaperAdapter({"name": "papers", "adapter": "paper", "dois": [DOI], "arxiv": ["1706.03762"], **cfg}, http=http)


class PaperAdapterTest(unittest.TestCase):
    def test_normalizers(self):
        self.assertEqual(norm_doi("https://doi.org/10.1145/ABC"), "10.1145/abc")
        self.assertEqual(norm_doi("doi:10.1/x"), "10.1/x")
        self.assertEqual(norm_arxiv("arXiv:1706.03762"), "1706.03762")
        self.assertEqual(norm_arxiv("https://arxiv.org/abs/1706.03762"), "1706.03762")

    def test_keys_and_allowlist(self):
        a = paper_adapter()
        self.assertEqual(a.seeds(), [f"paper>{DOI}", "paper>arxiv:1706.03762"])
        self.assertTrue(a.allowed(f"paper>{DOI}"))
        self.assertTrue(a.allowed("paper>arxiv:1706.03762"))
        self.assertFalse(a.allowed("paper>10.9999/other"))  # each paper is vetted by name
        self.assertFalse(a.allowed("paper>arxiv:0000.00000"))
        self.assertEqual(a.key_for_url(f"https://doi.org/{DOI}"), f"paper>{DOI}")
        self.assertIsNone(a.key_for_url("https://doi.org/10.9/z"))
        self.assertEqual(a.key_for_url("https://arxiv.org/abs/1706.03762v3"), "paper>arxiv:1706.03762")

    def test_parse_arxiv(self):
        m = parse_arxiv((FIXTURES / "paper" / "arxiv.xml").read_text())
        self.assertEqual(m["id"], "1706.03762")
        self.assertEqual(m["version"], "v7")
        self.assertEqual(m["title"], "Attention Is All You Need")
        self.assertTrue(m["abstract"].startswith("The dominant sequence transduction models"))
        self.assertEqual(m["authors"], ["Ashish Vaswani", "Noam Shazeer"])
        self.assertIsNone(parse_arxiv("not xml"))

    def test_fetch_doi(self):
        with temp_root():
            rec = paper_adapter().fetch(f"paper>{DOI}")
        self.assertEqual(rec["name"], "Cassandra: a decentralized structured storage system (Lakshman et al., 2010)")
        self.assertIn("## Abstract\nCassandra is a distributed storage system", rec["text"])
        self.assertEqual(rec["version"], "2010-06-10")
        self.assertEqual(rec["url"], f"https://doi.org/{DOI}")
        self.assertEqual(rec["tier"], "primary")
        self.assertEqual(rec["license"]["class"], "all-rights-reserved")
        self.assertEqual(rec["meta"]["venue"], "SIGMOD")

    def test_open_access_license_is_used(self):
        w = openalex(DOI, "T", ABSTRACT, oa={"license": "cc-by", "pdf_url": "https://x.org/p.pdf"})
        with temp_root():
            rec = paper_adapter([w]).fetch(f"paper>{DOI}")
        self.assertEqual(rec["license"]["class"], "cc-by")

    def test_fetch_arxiv(self):
        rec = paper_adapter().fetch("paper>arxiv:1706.03762")
        self.assertEqual(rec["name"], "Attention Is All You Need (Vaswani et al., 2017)")
        self.assertEqual(rec["version"], "v7")
        self.assertEqual(rec["url"], "https://arxiv.org/abs/1706.03762")
        self.assertIn("Transformer", rec["text"])
        self.assertEqual(rec["categories"], ["cs.CL"])

    def test_unknown_doi_and_missing_abstract(self):
        with temp_root():
            with self.assertRaises(MissingSource):
                paper_adapter([]).fetch(f"paper>{DOI}")
        with temp_root():
            with self.assertRaises(SourceError):
                paper_adapter([openalex(DOI, "T", None)]).fetch(f"paper>{DOI}")

    def test_fulltext_appends_open_access_pdf(self):
        w = openalex(DOI, "T", ABSTRACT, oa={"license": "cc-by", "pdf_url": "https://x.org/p.pdf"})
        with temp_root():
            a = paper_adapter([w], fulltext=True)
            a.http.mapping["https://x.org/p.pdf"] = make_pdf(PAGES)
            rec = a.fetch(f"paper>{DOI}")
        self.assertIn("## Full text", rec["text"])
        self.assertIn("consistent hash ring", rec["text"])
        self.assertTrue(rec["meta"]["fulltext"])

    def test_discover(self):
        with temp_root():
            out = paper_adapter().discover("cassandra")
        self.assertEqual(out[0]["key"], f"paper>{DOI}")
        self.assertTrue(out[0]["evidence"]["has_abstract"])

    def test_check_notes_restricted_license(self):
        with temp_root():
            res = paper_adapter().check()
        self.assertEqual(res["problems"], [])
        self.assertTrue(any("abstract and metadata only" in n for n in res["notes"]))

    def test_registry(self):
        r = Registry([{"name": "p", "adapter": "paper", "dois": [DOI]}])
        self.assertTrue(r.allowed(f"paper>{DOI}"))
        self.assertEqual(r.tier(f"paper>{DOI}"), "primary")

    def test_lookup_dois_requests_license_fields(self):
        with temp_root():
            seen = {}
            http = FakeHTTP({"https://api.openalex.org/works": lambda p: seen.update(p) or json.dumps({"results": []}),
                             f"https://api.crossref.org/works/{DOI}": None})
            extsrc.lookup_dois([DOI], http=http)
        self.assertIn("best_oa_location", seen["select"])


if __name__ == "__main__":
    unittest.main()
