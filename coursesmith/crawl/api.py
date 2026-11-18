"""Polite MediaWiki Action API client: <= 0.5 req/s, no parallelism, maxlag, backoff, retry-after.

Ported from the chronicle's crawler/api.py. New here: category members, transclusions, page assessments,
Wikidata QIDs, templates, section-aware link parsing, morelike search, page images and pageviews.
"""
import time

import requests

from .. import config


class ApiError(RuntimeError):
    pass


class MissingPage(ApiError):
    pass


class WikiClient:
    def __init__(self, min_interval=config.MIN_INTERVAL_S):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.USER_AGENT, "Accept-Encoding": "gzip"})
        self.min_interval = max(2.0, min_interval)
        self._last = 0.0
        self.requests_made = 0
        self.retries = 0

    # -- transport ---------------------------------------------------------
    def _throttle(self):
        wait = self.min_interval - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)

    def get(self, params, url=None):
        params = {**params, "format": "json", "formatversion": "2", "maxlag": config.MAXLAG}
        delay = 2.0
        for _ in range(config.MAX_RETRIES):
            self._throttle()
            try:
                r = self.session.get(url or config.API_URL, params=params, timeout=config.TIMEOUT_S)
            except requests.RequestException as e:
                self._last = time.monotonic()
                self._backoff(delay, f"network error: {e}")
                delay *= 2
                continue
            self._last = time.monotonic()
            self.requests_made += 1
            if r.status_code == 429 or r.status_code >= 500:
                self._backoff(_retry_after(r, delay), f"HTTP {r.status_code}")
                delay *= 2
                continue
            r.raise_for_status()
            data = r.json()
            err = data.get("error")
            if err:
                code = err.get("code")
                if code in ("maxlag", "ratelimited"):
                    self._backoff(max(_retry_after(r, 5.0), delay), code)
                    delay *= 2
                    continue
                if code in ("missingtitle", "invalidtitle", "pagecannotexist"):
                    raise MissingPage(f"{code}: {err.get('info')}")
                raise ApiError(f"{code}: {err.get('info')}")
            return data
        raise ApiError(f"gave up after {config.MAX_RETRIES} attempts: "
                       f"{params.get('action')} {params.get('page') or params.get('titles')}")

    def get_rest(self, url):
        """GET a JSON REST endpoint (pageviews) with the same throttle and backoff. None on 404."""
        delay = 2.0
        for _ in range(config.MAX_RETRIES):
            self._throttle()
            try:
                r = self.session.get(url, timeout=config.TIMEOUT_S)
            except requests.RequestException as e:
                self._last = time.monotonic()
                self._backoff(delay, f"network error: {e}")
                delay *= 2
                continue
            self._last = time.monotonic()
            self.requests_made += 1
            if r.status_code == 404:
                return None
            if r.status_code == 429 or r.status_code >= 500:
                self._backoff(_retry_after(r, delay), f"HTTP {r.status_code}")
                delay *= 2
                continue
            r.raise_for_status()
            return r.json()
        raise ApiError(f"gave up after {config.MAX_RETRIES} attempts: {url}")

    def get_bytes(self, url):
        """Download a file (an image thumbnail) with the same etiquette."""
        delay = 2.0
        for _ in range(config.MAX_RETRIES):
            self._throttle()
            try:
                r = self.session.get(url, timeout=config.TIMEOUT_S)
            except requests.RequestException as e:
                self._last = time.monotonic()
                self._backoff(delay, f"network error: {e}")
                delay *= 2
                continue
            self._last = time.monotonic()
            self.requests_made += 1
            if r.status_code == 429 or r.status_code >= 500:
                self._backoff(_retry_after(r, delay), f"HTTP {r.status_code}")
                delay *= 2
                continue
            r.raise_for_status()
            return r.content
        raise ApiError(f"gave up after {config.MAX_RETRIES} attempts: {url}")

    def _backoff(self, seconds, why):
        self.retries += 1
        print(f"  [api] {why}; backing off {seconds:.0f}s", flush=True)
        time.sleep(seconds)

    def query_all(self, params, list_key):
        """Run a list= query with continuation, yielding items of query[list_key]."""
        cont = {}
        while True:
            d = self.get({"action": "query", **params, **cont})
            for item in d.get("query", {}).get(list_key, []):
                yield item
            if "continue" not in d:
                return
            cont = d["continue"]

    # -- pages -------------------------------------------------------------
    def parse_page(self, title):
        """Full parsed page: HTML (keeps tables), links, categories, revid, sections."""
        d = self.get({
            "action": "parse", "page": title,
            "prop": "text|links|categories|revid|sections|displaytitle|templates",
            "redirects": 1, "disableeditsection": 1, "disabletoc": 1,
        })
        return d["parse"]

    def parse_html(self, title):
        """Parsed HTML only (navbox templates, Vital lists, WikiProject tables)."""
        d = self.get({"action": "parse", "page": title, "prop": "text|revid", "redirects": 1,
                      "disableeditsection": 1, "disabletoc": 1})
        return d["parse"]

    def link_meta(self, titles):
        """Batch pre-screen (<=50 titles): canonical title, non-hidden categories, short description,
        disambiguation flag, missing flag, Wikidata QID."""
        assert len(titles) <= 50
        out, alias = {}, {}
        params = {"action": "query", "titles": "|".join(titles), "prop": "categories|description|pageprops",
                  "clshow": "!hidden", "cllimit": "max", "ppprop": "disambiguation|wikibase_item", "redirects": 1}
        cont = {}
        while True:
            d = self.get({**params, **cont})
            q = d.get("query", {})
            for n in q.get("normalized", []):
                alias[n["from"]] = n["to"]
            for rd in q.get("redirects", []):
                alias[rd["from"]] = rd["to"]
            for p in q.get("pages", []):
                t = p["title"]
                m = out.setdefault(t, {"categories": [], "description": "", "disambig": False, "missing": False,
                                       "qid": None})
                if p.get("missing") or p.get("invalid"):
                    m["missing"] = True
                m["categories"] += [c["title"].removeprefix("Category:") for c in p.get("categories", [])]
                m["description"] = p.get("description", m["description"]) or m["description"]
                pp = p.get("pageprops", {})
                if "disambiguation" in pp:
                    m["disambig"] = True
                if pp.get("wikibase_item"):
                    m["qid"] = pp["wikibase_item"]
            if "continue" not in d:
                break
            cont = d["continue"]
        resolved = {t: _final(alias, t) for t in titles}
        return resolved, out

    def assessments(self, titles):
        """WikiProject quality/importance per title (<=50). Always redirects=1: redirect titles return {}."""
        assert len(titles) <= 50
        out, alias = {}, {}
        cont = {}
        while True:
            d = self.get({"action": "query", "titles": "|".join(titles), "prop": "pageassessments",
                          "palimit": "max", "redirects": 1, **cont})
            q = d.get("query", {})
            for n in q.get("normalized", []) + q.get("redirects", []):
                alias[n["from"]] = n["to"]
            for p in q.get("pages", []):
                out.setdefault(p["title"], {}).update(p.get("pageassessments") or {})
            if "continue" not in d:
                break
            cont = d["continue"]
        return {t: out.get(_final(alias, t), {}) for t in titles}

    def category_members(self, category, ns=(0, 14)):
        """Members of a category: (title, ns) for articles and subcategories."""
        cat = category if category.startswith("Category:") else "Category:" + category
        for m in self.query_all({"list": "categorymembers", "cmtitle": cat, "cmlimit": "max",
                                 "cmnamespace": "|".join(map(str, ns))}, "categorymembers"):
            yield m["title"], m["ns"]

    def embedded_in(self, template, ns=0):
        """Articles that transclude a template (navbox reach)."""
        for m in self.query_all({"list": "embeddedin", "eititle": template, "einamespace": ns,
                                 "eilimit": "max"}, "embeddedin"):
            yield m["title"]

    def templates(self, title, prefix="Template:"):
        d = self.get({"action": "query", "titles": title, "prop": "templates", "tlnamespace": 10,
                      "tllimit": "max", "redirects": 1})
        out = []
        for p in d.get("query", {}).get("pages", []):
            out += [t["title"] for t in p.get("templates", []) if t["title"].startswith(prefix)]
        return out

    def morelike(self, title, n=20):
        d = self.get({"action": "query", "list": "search", "srsearch": f"morelike:{title}", "srlimit": n,
                      "srnamespace": 0})
        return [s["title"] for s in d.get("query", {}).get("search", [])]

    def backlinks_count(self, title, cap=500):
        """Article-namespace, non-redirect backlinks, counted with continuation, capped."""
        n, cont = 0, {}
        while n < cap:
            d = self.get({"action": "query", "list": "backlinks", "bltitle": title, "blnamespace": 0,
                          "blfilterredir": "nonredirects", "bllimit": min(500, cap), **cont})
            n += len(d.get("query", {}).get("backlinks", []))
            if "continue" not in d:
                break
            cont = d["continue"]
        return min(n, cap)

    def page_image(self, title):
        """The page's lead image file name, or None."""
        d = self.get({"action": "query", "titles": title, "prop": "pageimages", "piprop": "name",
                      "redirects": 1})
        for p in d.get("query", {}).get("pages", []):
            if p.get("pageimage"):
                return "File:" + p["pageimage"]
        return None

    def image_info(self, file_title, width=600):
        """URL of a thumbnail no wider than `width`, plus the license metadata Commons publishes."""
        d = self.get({"action": "query", "titles": file_title, "prop": "imageinfo",
                      "iiprop": "url|extmetadata|mime|size", "iiurlwidth": width})
        for p in d.get("query", {}).get("pages", []):
            ii = (p.get("imageinfo") or [None])[0]
            if not ii:
                return None
            em = ii.get("extmetadata") or {}
            g = lambda k: (em.get(k) or {}).get("value")
            return {"file": p["title"], "thumb_url": ii.get("thumburl") or ii.get("url"),
                    "page_url": ii.get("descriptionurl"), "mime": ii.get("mime"),
                    "license": g("LicenseShortName"), "license_url": g("LicenseUrl"),
                    "artist": g("Artist"), "credit": g("Credit"), "usage_terms": g("UsageTerms")}
        return None

    def pageviews(self, title, start="20251101", end="20261031"):
        """Total user pageviews over a year (monthly granularity), or 0."""
        art = title.replace(" ", "_").replace("/", "%2F")
        d = self.get_rest(f"{config.PAGEVIEWS_URL}{requests.utils.quote(art, safe='_%')}/monthly/{start}/{end}")
        return sum(i.get("views", 0) for i in (d or {}).get("items", []))


def _final(alias, t):
    seen = set()
    while t in alias and t not in seen:
        seen.add(t)
        t = alias[t]
    return t


def _retry_after(r, default):
    try:
        return float(r.headers.get("Retry-After", default))
    except ValueError:
        return default
