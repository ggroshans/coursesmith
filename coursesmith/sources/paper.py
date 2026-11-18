"""Research papers as a source: `paper>10.1145/1773912.1773922` or `paper>arxiv:2301.00001`.

Each paper is listed by hand, so each is vetted by name. By default only the bibliographic record and the
abstract are used (from OpenAlex, with Crossref as a fallback, or the arXiv API); the abstract is text the
authors wrote to state the paper's claim, which is what a course cites. Full text is opt-in per source
(`fulltext: true`) and uses the open-access PDF OpenAlex reports.

    - name: foundational-papers
      adapter: paper
      dois: ["10.1145/1773912.1773922"]
      arxiv: ["1706.03762"]
      tier: primary
      fulltext: false

A paper's own license (when it is open access) is used; otherwise the publisher's terms apply and only the
abstract and metadata are cited, with attribution.
"""
import re
import xml.etree.ElementTree as ET

from . import licenses
from .base import MissingSource, SourceAdapter, SourceError
from .keys import SEP, make_key
from ..text.pdf import pdf_to_text
from ..verify import extsrc

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
PUBLISHER = {"name": "Publisher terms (abstract and bibliographic data only)", "url": "", "class": "all-rights-reserved"}


def norm_doi(d):
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:)", "", str(d).strip(), flags=re.I).lower()


def norm_arxiv(a):
    return re.sub(r"^(arxiv:|https?://arxiv\.org/abs/)", "", str(a).strip(), flags=re.I)


def parse_arxiv(xml_text):
    """First entry of an arXiv Atom response -> dict, or None."""
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return None
    e = root.find("a:entry", NS)
    if e is None or (e.findtext("a:title", "", NS) or "").strip().lower() == "error":
        return None
    abs_id = (e.findtext("a:id", "", NS) or "").strip()
    m = re.search(r"/abs/(.+?)(v\d+)?$", abs_id)
    return {
        "id": m.group(1) if m else abs_id, "version": (m.group(2) if m and m.group(2) else None),
        "title": re.sub(r"\s+", " ", (e.findtext("a:title", "", NS) or "")).strip(),
        "abstract": re.sub(r"\s+", " ", (e.findtext("a:summary", "", NS) or "")).strip(),
        "authors": [(a.findtext("a:name", "", NS) or "").strip() for a in e.findall("a:author", NS)],
        "published": (e.findtext("a:published", "", NS) or "")[:10], "updated": (e.findtext("a:updated", "", NS) or "")[:10],
        "doi": (e.findtext("x:doi", "", NS) or "").strip() or None,
        "categories": [c.get("term") for c in e.findall("a:category", NS)],
        "pdf": next((l.get("href") for l in e.findall("a:link", NS) if l.get("title") == "pdf"), None),
    }


class PaperAdapter(SourceAdapter):
    adapter = "paper"
    prefix = "paper"
    default_tier = "primary"
    default_depth = 0
    default_license = PUBLISHER

    def __init__(self, cfg=None, http=None, defaults=None):
        super().__init__(cfg, http, defaults)
        self.dois = [norm_doi(d) for d in self.cfg.get("dois") or []]
        self.arxiv = [norm_arxiv(a) for a in self.cfg.get("arxiv") or []]

    def hosts(self):
        return ["api.openalex.org", "api.crossref.org", "export.arxiv.org"]

    # -- keys ------------------------------------------------------------------------
    def key_doi(self, doi):
        return make_key("paper", norm_doi(doi))

    def key_arxiv(self, aid):
        return make_key("paper", f"arxiv:{norm_arxiv(aid)}")

    def owns(self, key):
        return key.startswith(f"paper{SEP}")

    def ident(self, key):
        return key.split(SEP, 1)[1]

    def allowed(self, key):
        if not self.owns(key):
            return False
        i = self.ident(key)
        return (i[6:] in self.arxiv) if i.startswith("arxiv:") else (i.lower() in self.dois)

    def seeds(self):
        return [self.key_doi(d) for d in self.dois] + [self.key_arxiv(a) for a in self.arxiv]

    def key_for_url(self, url, base_key=None):
        m = re.search(r"doi\.org/(10\.\d{4,9}/\S+)", url or "", re.I)
        if m:
            return self.key_doi(m.group(1)) if norm_doi(m.group(1)) in self.dois else None
        m = re.search(r"arxiv\.org/(?:abs|pdf)/([\w.\-/]+?)(?:v\d+)?(?:\.pdf)?$", url or "", re.I)
        return self.key_arxiv(m.group(1)) if m and m.group(1) in self.arxiv else None

    # -- fetching --------------------------------------------------------------------
    def _arxiv_meta(self, aid):
        raw = self.http.get(ARXIV_API, params={"id_list": aid})
        return parse_arxiv(raw) if raw else None

    def fetch(self, key):
        ident = self.ident(key)
        if ident.startswith("arxiv:"):
            return self._fetch_arxiv(key, ident[6:])
        return self._fetch_doi(key, ident.lower())

    def _fetch_arxiv(self, key, aid):
        m = self._arxiv_meta(aid)
        if not m:
            raise MissingSource(f"arXiv {aid} not found")
        if not m["abstract"]:
            raise SourceError(f"arXiv {aid} has no abstract")
        year = m["published"][:4]
        name = f"{m['title']} ({self._who(m['authors'], year)})"
        text = f"# {m['title']}\n\n## Abstract\n{m['abstract']}\n"
        version = m["version"] or m["updated"]
        rec = self.record(key, name, f"https://arxiv.org/abs/{aid}", text, version, source_id=f"arxiv:{aid}")
        rec["license"] = self.license
        rec["categories"] = m["categories"]
        rec["meta"] = {"description": m["title"], "tags": m["categories"], "doi": m["doi"], "year": year,
                       "authors": m["authors"], "venue": "arXiv", "dates": False, "fulltext": False}
        if self.cfg.get("fulltext") and m["pdf"]:
            self._add_fulltext(rec, m["pdf"], m["title"])
        return rec

    def _fetch_doi(self, key, doi):
        works = extsrc.lookup_dois([doi], http=self.http)
        w = works.get(doi) or {}
        if w.get("not_found") or not w:
            raise MissingSource(f"DOI {doi} not found in OpenAlex or Crossref")
        if not w.get("abstract"):
            raise SourceError(f"DOI {doi} ({w.get('title')}) has no abstract to cite; "
                              f"list its arXiv id, or set fulltext: true if it is open access")
        year = w.get("year")
        authors = w.get("authors") or []
        name = f"{w.get('title')} ({self._who(authors, year)})"
        text = f"# {w['title']}\n\n## Abstract\n{w['abstract']}\n"
        rec = self.record(key, name, f"https://doi.org/{doi}", text, w.get("date") or str(year or "doi"),
                          source_id=doi)
        oa = w.get("oa_license")
        rec["license"] = licenses.normalize({"name": oa, "class": licenses.classify(oa)}) if oa else self.license
        rec["categories"] = [w["venue"]] if w.get("venue") else []
        rec["meta"] = {"description": w.get("title"), "tags": [], "doi": doi, "year": year, "authors": authors,
                       "venue": w.get("venue"), "cited_by_count": w.get("cited_by_count"), "oa_url": w.get("oa_url"),
                       "abstract_source": w.get("abstract_source"), "dates": False, "fulltext": False}
        if self.cfg.get("fulltext") and w.get("oa_url", "").lower().endswith(".pdf"):
            self._add_fulltext(rec, w["oa_url"], w.get("title"))
        return rec

    def _add_fulltext(self, rec, url, title):
        data = self.http.get(url, binary=True)
        if not data:
            return
        text, _ = pdf_to_text(data, title)
        body = text.split("\n", 1)[1] if text.startswith("# ") else text
        rec["text"] = rec["text"].rstrip("\n") + "\n\n## Full text\n" + body.lstrip("\n")
        rec["meta"]["fulltext"] = True

    @staticmethod
    def _who(authors, year):
        first = (authors[0].split()[-1] if authors else "")
        return f"{first} et al., {year}" if len(authors) > 1 else f"{first}, {year}" if first else str(year or "")

    # -- presentation ----------------------------------------------------------------
    def version_label(self, version):
        return f"published {version}" if version and not str(version).startswith("v") else f"version {version}"

    # -- discovery and checks --------------------------------------------------------
    def discover(self, query, limit=10):
        out = []
        for w in extsrc.openalex_search(query, limit, http=self.http):
            if w.get("doi"):
                out.append({"id": f"paper:{w['doi']}", "adapter": "paper", "title": w.get("title"),
                            "url": f"https://doi.org/{w['doi']}", "key": self.key_doi(w["doi"]), "tier": "primary",
                            "snippet": (w.get("abstract") or "")[:300],
                            "evidence": {"year": w.get("year"), "venue": w.get("venue"),
                                         "cited_by": w.get("cited_by_count"), "has_abstract": bool(w.get("abstract"))}})
        return out

    def check(self):
        problems, notes = [], []
        for k in self.seeds():
            try:
                rec = self.fetch(k)
            except SourceError as e:
                problems.append(str(e))
                continue
            if not licenses.is_public(rec["license"].get("class")):
                notes.append(f"{self.ident(k)}: abstract and metadata only ({rec['license'].get('name')})")
        return {"problems": problems, "notes": notes}


ADAPTER = PaperAdapter
