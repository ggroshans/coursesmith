"""Wikipedia, and any other MediaWiki site, as a source.

The default Wikipedia keeps bare titles. A MediaWiki with its own `api_url` and `base` in subject.yaml
(Wikibooks, Wikiversity, a project wiki) gets keys like `wiki>en.wikibooks.org/Computer_Networks`.

    - name: wikibooks
      adapter: wikipedia
      api_url: https://en.wikibooks.org/w/api.php
      base: https://en.wikibooks.org/wiki/
      tier: reference
"""
from urllib.parse import quote, unquote, urlparse

from .. import config
from . import licenses
from .base import MissingSource, SourceAdapter, SourceError
from .keys import SEP, is_qualified, make_key, split_key

CC_BY_SA = {"name": "CC BY-SA 4.0", "url": "https://creativecommons.org/licenses/by-sa/4.0/", "class": "cc-by-sa"}


class WikipediaAdapter(SourceAdapter):
    adapter = "wikipedia"
    default_tier = "reference"
    default_license = CC_BY_SA

    def __init__(self, cfg=None, http=None, defaults=None):
        super().__init__(cfg, http, defaults)
        self.api_url = self.cfg.get("api_url") or None
        self.base = self.cfg.get("base") or (None if not self.api_url else self.api_url.replace("/w/api.php", "/wiki/"))
        self.is_default = self.api_url is None
        self.host = urlparse(self.base or config.WIKI_BASE).netloc
        self.prefix = "" if self.is_default else "wiki"
        self.client = None  # the crawl hands in its WikiClient; other wikis build their own

    def hosts(self):
        return [self.host]

    def _client(self):
        if self.client is None:
            from ..crawl.api import WikiClient
            self.client = WikiClient(api_url=self.api_url)
        return self.client

    # -- keys ------------------------------------------------------------------------
    def owns(self, key):
        if self.is_default:
            return not is_qualified(key)
        return key.startswith(f"wiki{SEP}{self.host}/")

    def key(self, title):
        return title if self.is_default else make_key("wiki", f"{self.host}/{title.replace(' ', '_')}")

    def title_of(self, key):
        if self.is_default:
            return key
        return unquote(split_key(key)[1].split("/", 1)[1]).replace("_", " ")

    def url(self, title):
        base = self.base or config.WIKI_BASE
        return base + quote(title.replace(" ", "_"), safe="()_,'-.:~!*")

    def key_for_url(self, url, base_key=None):
        u = urlparse(url)
        path = u.path
        if u.netloc and u.netloc != self.host:
            return None
        if "/wiki/" not in path:
            return None
        title = unquote(path.split("/wiki/", 1)[1]).replace("_", " ")
        return self.key(title) if title else None

    # -- fetching --------------------------------------------------------------------
    def fetch(self, key):
        from ..crawl.api import ApiError, MissingPage
        from ..crawl.clean import clean_html
        if self.is_default:
            raise SourceError("the default Wikipedia is fetched by crawl.fetch.fetch_page")
        title = self.title_of(key)
        try:
            p = self._client().parse_page(title)
        except MissingPage as e:
            raise MissingSource(str(e))
        except ApiError as e:
            raise SourceError(str(e))
        canonical = p["title"]
        k = self.key(canonical)
        html = p["text"]
        text, body_links, citations = clean_html(html, canonical)
        rec = self.record(k, canonical, self.url(canonical), text, p.get("revid"), source_id=canonical)
        rec.update({
            "revid": p.get("revid"), "pageid": p.get("pageid"), "html": html,
            "body_links": [self.key(t) for t in body_links],
            "lead_links": [],
            "categories": [c["category"].replace("_", " ") for c in p.get("categories", []) if not c.get("hidden")],
            "citations": citations, "requested_title": title,
        })
        rec["aliases"] = {key: k} if key != k else {}
        return rec

    # -- presentation ----------------------------------------------------------------
    def permalink(self, src):
        url, revid = src.get("url") or "", src.get("revid")
        if not revid or "/wiki/" not in url:
            return url
        head, title = url.split("/wiki/", 1)
        return f"{head}/w/index.php?title={title}&oldid={revid}"

    def version_label(self, version):
        return f"revision {version}" if version else ""

    def discover(self, query, limit=20):
        try:
            d = self._client().get({"action": "query", "list": "search", "srsearch": query, "srlimit": limit},
                                   url=self.api_url)
        except Exception:
            return []
        return [{"title": r["title"], "url": self.url(r["title"]), "snippet": r.get("snippet", "")}
                for r in d.get("query", {}).get("search", [])]


ADAPTER = WikipediaAdapter
