"""Fakes for offline tests: a Wikipedia client, a source adapter and an HTTP layer served from fixtures."""
from pathlib import Path

from coursesmith.sources.base import MissingSource, SourceAdapter
from coursesmith.sources.keys import SEP

FIXTURES = Path(__file__).parent / "fixtures"


class FakeWikiClient:
    """Stands in for crawl.api.WikiClient: canned parse_page and link_meta results keyed by title."""

    def __init__(self, pages=None, meta=None):
        self.pages = pages or {}
        self.meta = meta or {}
        self.requests_made = 0
        self.parsed = []
        self.metaed = []

    def parse_page(self, title):
        self.parsed.append(title)
        self.requests_made += 1
        if title not in self.pages:
            from coursesmith.crawl.api import MissingPage
            raise MissingPage(f"missingtitle: {title}")
        return self.pages[title]

    def link_meta(self, titles):
        self.metaed.append(list(titles))
        self.requests_made += 1
        return {}, {t: self.meta.get(t, {"categories": [], "description": ""}) for t in titles}


def wiki_page(title, html, revid=1, links=()):
    return {"title": title, "pageid": 1, "revid": revid, "text": html,
            "links": [{"ns": 0, "title": t, "exists": True} for t in links], "categories": [], "sections": [],
            "templates": []}


class FakeAdapter(SourceAdapter):
    """A source whose pages are a dict key -> (name, text, version, [links])."""
    adapter = "fake"
    prefix = "fake"
    default_tier = "curated"

    def __init__(self, cfg=None, http=None, defaults=None, pages=None):
        super().__init__(cfg, http, defaults)
        self.pages = pages or {}
        self.fetched = []

    def owns(self, key):
        return key.startswith(f"fake{SEP}")

    def allowed(self, key):
        allow = self.cfg.get("allow")
        return self.owns(key) and (not allow or any(key.startswith(f"fake{SEP}{a}") for a in allow))

    def fetch(self, key):
        self.fetched.append(key)
        if key not in self.pages:
            raise MissingSource(key)
        name, text, version, links = self.pages[key]
        return self.record(key, name, f"https://fake.example/{key.split(SEP, 1)[1]}", text, version,
                           body_links=list(links))


class FakeRegistry:
    """Just enough of sources.Registry for fetch_page and the crawl."""

    def __init__(self, adapter):
        self.adapter = adapter
        self.adapters = [adapter]

    def for_key(self, key):
        if not self.adapter.owns(key):
            raise MissingSource(key)
        return self.adapter

    def maybe_for_key(self, key):
        return self.adapter if self.adapter.owns(key) else None

    def allowed(self, key):
        return self.adapter.allowed(key)


class FakeHTTP:
    """Same get() as verify.extsrc.PoliteHTTP, answered from a dict url -> body (str/bytes/Path) or None."""

    def __init__(self, mapping=None):
        self.mapping = dict(mapping or {})
        self.calls = []

    def get(self, url, params=None, cache=True, binary=False, headers=None, max_age_s=None, cache_only=False,
            want_headers=False):
        self.calls.append(url)
        body = self.mapping.get(url)
        if callable(body):
            body = body(params or {})
        if isinstance(body, Path):
            body = body.read_bytes() if binary else body.read_text(encoding="utf-8")
        if isinstance(body, bytes) and not binary:
            body = body.decode("utf-8")
        if isinstance(body, str) and binary:
            body = body.encode("utf-8")
        return (body, {}) if want_headers else body


def make_pdf(pages):
    """A minimal valid PDF whose pages each hold the given lines of Helvetica text."""
    objs = {1: "<< /Type /Catalog /Pages 2 0 R >>", 3: "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"}
    kids = []
    for i, lines in enumerate(pages):
        page_id, cont_id = 4 + 2 * i, 5 + 2 * i
        kids.append(f"{page_id} 0 R")
        ops = ["BT", "/F1 11 Tf", "14 TL", "50 750 Td"]
        for l in lines:
            ops.append("(" + l.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)") + ") Tj T*")
        ops.append("ET")
        stream = "\n".join(ops)
        objs[cont_id] = f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream"
        objs[page_id] = (f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {cont_id} 0 R "
                         f"/Resources << /Font << /F1 3 0 R >> >> >>")
    objs[2] = f"<< /Type /Pages /Kids [{' '.join(kids)}] /Count {len(pages)} >>"
    out, offsets = b"%PDF-1.4\n", {}
    for n in sorted(objs):
        offsets[n] = len(out)
        out += f"{n} 0 obj\n{objs[n]}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode()
    for n in sorted(objs):
        out += f"{offsets[n]:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return out
