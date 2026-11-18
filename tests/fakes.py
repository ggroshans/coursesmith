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
        if isinstance(body, Path):
            body = body.read_bytes() if binary else body.read_text(encoding="utf-8")
        if isinstance(body, bytes) and not binary:
            body = body.decode("utf-8")
        if isinstance(body, str) and binary:
            body = body.encode("utf-8")
        return (body, {}) if want_headers else body
