"""An allowlisted docs site as a source: `doc>host/path`.

For official documentation that has no repository to pin (or whose rendered pages are the thing to cite). The
subject lists the site, the path prefixes a crawl may enter, and the CSS selector of the page content:

    - name: redis-docs
      adapter: html
      base: https://redis.io/docs/latest/
      allow: ["/docs/latest/develop/", "/docs/latest/operate/oss_and_stack/"]
      deny: ["/docs/latest/commands/"]
      selector: "main"            # else the first <main>, <article> or similar
      drop: [".sidebar", ".toc"]  # extra chrome to remove
      pages: ["/docs/latest/develop/data-types/"]   # crawled without listing them under `seeds:`
      depth: 2
      code: {max_lines: 80}       # keep code blocks as listings a writer can place (see README)
      table_cells: span           # keep equal neighbouring table cells apart ("Yes | Yes | Yes"); default merges them
      tier: official
      license: {name: "CC BY-SA 4.0", url: "https://creativecommons.org/licenses/by-sa/4.0/"}

robots.txt is honored. A page's version is a hash of its cleaned text, so the same content never re-indexes;
the retrieval date is kept on the record. The license is declared by the human; `sources check` looks for the
site's own statement and fails when it disagrees.
"""
import hashlib
import re
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser

from . import licenses
from .base import MissingSource, SourceAdapter, SourceError
from .keys import SEP, clean_id
from ..text.docfx import code_listings
from ..text.html import html_to_doc

SKIP_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".pdf", ".zip", ".gz", ".tar", ".mp4", ".css", ".js",
            ".json", ".xml", ".ico", ".woff", ".woff2")
USER_AGENT_TOKEN = "coursesmith"
LICENSE_HINTS = [
    (re.compile(r"creative commons attribution[- ]noncommercial[- ]noderivatives|cc[- ]by[- ]nc[- ]nd", re.I), "cc-by-nc-nd"),
    (re.compile(r"creative commons attribution[- ]noncommercial[- ]sharealike|cc[- ]by[- ]nc[- ]sa", re.I), "cc-by-nc-sa"),
    (re.compile(r"creative commons attribution[- ]noncommercial|cc[- ]by[- ]nc", re.I), "cc-by-nc"),
    (re.compile(r"creative commons attribution[- ]sharealike|cc[- ]by[- ]sa", re.I), "cc-by-sa"),
    (re.compile(r"creative commons attribution|cc[- ]by\b", re.I), "cc-by"),
    (re.compile(r"\bcc0\b|public domain", re.I), "public-domain"),
    (re.compile(r"apache license|\bMIT license\b|\bBSD\b", re.I), "permissive"),
]


def norm_path(path):
    """Site path -> the form used inside keys: no query, no fragment, no index.html, no trailing slash."""
    p = urlparse(path).path or "/"
    p = re.sub(r"/index\.html?$", "/", p)
    return p.rstrip("/") or "/"


class HtmlAdapter(SourceAdapter):
    adapter = "html"
    prefix = "doc"
    default_tier = "official"
    default_depth = 2

    def __init__(self, cfg=None, http=None, defaults=None):
        super().__init__(cfg, http, defaults)
        base = self.cfg.get("base")
        if not base or not urlparse(base).netloc:
            raise SourceError(f"html source '{self.cfg.get('name')}': base must be a full URL")
        u = urlparse(base)
        self.scheme, self.host = u.scheme or "https", u.netloc.lower()
        self.allow = [norm_path(p) for p in (self.cfg.get("allow") or [u.path or "/"])]
        self.deny = [norm_path(p) for p in self.cfg.get("deny") or []]
        self._robots = None

    def hosts(self):
        return [self.host]

    # -- keys ------------------------------------------------------------------------
    def key(self, path):
        return f"doc{SEP}{self.host}{clean_id(norm_path(path))}"

    def path_of(self, key):
        return key[len(f"doc{SEP}{self.host}"):] or "/"

    def url_of(self, key):
        return f"{self.scheme}://{self.host}{self.path_of(key)}"

    def owns(self, key):
        return key.lower().startswith(f"doc{SEP}{self.host}/") or key.lower() == f"doc{SEP}{self.host}"

    @staticmethod
    def _under(path, prefixes):
        return any(path == p.rstrip("/") or path.startswith(p.rstrip("/") + "/") or p == "/" for p in prefixes)

    def allowed(self, key):
        if not self.owns(key):
            return False
        p = self.path_of(key)
        return self._under(p, self.allow) and not (self.deny and self._under(p, self.deny)) \
            and not p.lower().endswith(SKIP_EXT)

    def seeds(self):
        return [self.key(p) for p in self.cfg.get("pages") or []]

    def key_for_url(self, url, base_key=None):
        href = (url or "").strip()
        if not href or href.startswith(("#", "mailto:", "javascript:", "tel:")):
            return None
        page_url = self.url_of(base_key) if base_key and self.owns(base_key) else f"{self.scheme}://{self.host}/"
        if "." not in page_url.rstrip("/").rsplit("/", 1)[-1]:
            page_url = page_url.rstrip("/") + "/"  # clean-URL docs pages are served as directories
        absu = urldefrag(urljoin(page_url, href))[0]
        u = urlparse(absu)
        if u.netloc.lower().endswith("wikipedia.org") and u.path.startswith("/wiki/"):
            t = re.sub(r"_", " ", u.path[len("/wiki/"):]).strip()
            return t if t and ":" not in t.split(" ")[0] else None
        if u.netloc.lower() != self.host or u.path.lower().endswith(SKIP_EXT):
            return None
        return self.key(u.path)

    # -- fetching --------------------------------------------------------------------
    def robots_ok(self, url):
        if self.cfg.get("robots", True) is False:
            return True
        if self._robots is None:
            rp = RobotFileParser()
            txt = self.http.get(f"{self.scheme}://{self.host}/robots.txt") or ""
            rp.parse(txt.splitlines())
            self._robots = rp
        return self._robots.can_fetch(USER_AGENT_TOKEN, url)

    def fetch(self, key):
        url = self.url_of(key)
        if not self.robots_ok(url):
            raise SourceError(f"robots.txt at {self.host} disallows {url}")
        raw = self.http.get(url)
        if raw is None and not url.endswith("/"):
            raw = self.http.get(url + "/")  # docs sites often serve a page only at its trailing-slash URL
        if raw is None:
            raise MissingSource(f"{url}: not found or not allowed")
        listings = code_listings(self.cfg.get("code"))
        doc = html_to_doc(raw, selector=self.cfg.get("selector"), drop=self.cfg.get("drop") or (),
                          resolve_link=lambda a: self.key_for_url(a.get("href", ""), key),
                          table_cells=self.cfg.get("table_cells") or "all", listings=listings)
        if len(doc.text.split()) < 20:
            raise SourceError(f"{url}: no readable content (selector {self.cfg.get('selector') or 'auto'})")
        title = self.cfg.get("title") or self.host
        name = doc.name or self.path_of(key).rsplit("/", 1)[-1].replace("-", " ").replace("_", " ").title()
        if name != title:
            name = f"{name} ({title})"
        version = hashlib.sha256(doc.text.encode("utf-8")).hexdigest()[:16]
        rec = self.record(key, name, url, doc.text, version, source_id=f"{self.host}{self.path_of(key)}")
        rec.update({"body_links": [l for l in doc.links if l != key], "lead_links": [l for l in doc.lead_links if l != key],
                    "anchors": doc.anchors})
        if listings is not None and listings.items:
            rec["listings"] = listings.items
        rec["meta"] = {"description": doc.name, "tags": [], "code_blocks": doc.code_blocks,
                       "dates": bool(self.cfg.get("dates"))}
        return rec

    # -- presentation ----------------------------------------------------------------
    def version_label(self, version):
        return f"snapshot {str(version)[:8]}" if version else ""

    def permalink(self, src):
        if self.cfg.get("archive") and src.get("url"):
            return f"https://web.archive.org/web/{src['url']}"
        return src.get("url") or ""

    # -- checks ----------------------------------------------------------------------
    def detect_license(self, html):
        """The license a page states about itself: rel=license, then footer or body text."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        el = soup.find("a", rel=lambda v: v and "license" in (v if isinstance(v, list) else [v])) \
            or soup.find("link", rel=lambda v: v and "license" in (v if isinstance(v, list) else [v]))
        hay = []
        if el is not None:
            hay.append((el.get("href") or "") + " " + el.get_text(" "))
        for sel in ("footer", "[class*=license]", "[id*=license]", "[class*=copyright]"):
            hay += [e.get_text(" ") for e in soup.select(sel)]
        text = " ".join(hay)
        hrefs = " ".join(a.get("href", "") for a in soup.select("footer a, a[rel~=license]"))
        for pat, cls in LICENSE_HINTS:
            if pat.search(text) or pat.search(hrefs.replace("/", " ").replace("-", " ")):
                return cls, " ".join(text.split())[:200]
        m = re.search(r"creativecommons\.org/licenses/([a-z\-]+)/", hrefs)
        if m:
            return licenses.classify("cc-" + m.group(1)), m.group(0)
        return None, ""

    def check(self):
        problems, notes, ev = [], [], {}
        decl = self.license
        if not decl.get("name"):
            problems.append(f"{self.cfg.get('name')}: declare the site's license under `license:` "
                            f"(its terms of use, or the page footer)")
        base = self.cfg.get("base")
        try:
            if not self.robots_ok(base):
                problems.append(f"robots.txt at {self.host} disallows {base}")
            raw = self.http.get(base)
        except SourceError as e:
            return {"problems": [str(e)], "notes": notes, "evidence": ev}
        if raw is None:
            problems.append(f"{base} is not reachable")
            return {"problems": problems, "notes": notes, "evidence": ev}
        cls, snippet = self.detect_license(raw)
        ev["license"] = {"class": cls, "snippet": snippet, "from": base}
        if cls is None:
            notes.append(f"{self.host}: no license statement found on {base}; the declared license "
                         f"({decl.get('name') or 'none'}) rests on your reading of the site's terms")
        elif decl.get("name") and decl.get("class") != cls:
            problems.append(f"{self.host}: subject.yaml declares {decl['name']} ({decl['class']}) but the page says "
                            f"{cls}: {snippet[:100]}")
        if not self.allow:
            problems.append(f"{self.cfg.get('name')}: allow must list at least one path prefix")
        return {"license": ev["license"], "problems": problems, "notes": notes, "evidence": ev}


ADAPTER = HtmlAdapter
