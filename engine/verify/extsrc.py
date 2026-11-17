"""External sources for verification: OpenAlex (Crossref as fallback) for the DOIs Wikipedia cites, and a
polite cached HTTP client for authority fetchers. Ported from the chronicle's crawler/extsrc.py.

Metadata and abstracts only, never full text. Same etiquette as the crawler: the contact User-Agent, at least
2 s between requests to each host, backoff on 429/5xx, everything cached under cache/http/ and cache/works/.
"""
import hashlib
import json
import re
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests

from .. import config

UA = config.USER_AGENT.replace("python-requests", "python-requests (verification)")


class PoliteHTTP:
    def __init__(self, min_interval=2.0):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Encoding": "gzip"})
        self.min_interval = max(2.0, min_interval)
        self.last = {}
        self.calls = 0

    def get(self, url, params=None, cache=True, binary=False):
        key = hashlib.sha1((url + "?" + json.dumps(params or {}, sort_keys=True)).encode()).hexdigest()
        host = urlparse(url).netloc
        path = config.HTTP_CACHE / host / (key + (".bin" if binary else ".txt"))
        if cache and path.exists():
            return path.read_bytes() if binary else path.read_text(encoding="utf-8")
        delay = 2.0
        for _ in range(6):
            wait = self.min_interval - (time.monotonic() - self.last.get(host, 0))
            if wait > 0:
                time.sleep(wait)
            try:
                r = self.s.get(url, params=params, timeout=120)
            except requests.RequestException as e:
                self.last[host] = time.monotonic()
                print(f"  [ext] {host}: {e}; retry in {delay:.0f}s")
                time.sleep(delay)
                delay *= 2
                continue
            self.last[host] = time.monotonic()
            self.calls += 1
            if r.status_code == 429 or r.status_code >= 500:
                ra = r.headers.get("Retry-After")
                time.sleep(float(ra) if ra and ra.isdigit() else delay)
                delay *= 2
                continue
            if r.status_code in (403, 404, 410):
                return None
            r.raise_for_status()
            path.parent.mkdir(parents=True, exist_ok=True)
            if binary:
                path.write_bytes(r.content)
                return r.content
            path.write_text(r.text, encoding="utf-8")
            return r.text
        raise RuntimeError(f"gave up: {url}")


HTTP = PoliteHTTP()


def _slug(doi):
    return re.sub(r"[^a-z0-9]+", "_", doi.lower()).strip("_")[:120] + "__" + hashlib.sha1(doi.encode()).hexdigest()[:6]


def _openalex_abstract(inv):
    if not inv:
        return None
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def _from_openalex(r):
    return {
        "doi": (r.get("doi") or "").replace("https://doi.org/", "").lower(),
        "source": "openalex", "openalex_id": r.get("id"), "title": r.get("title"),
        "year": r.get("publication_year"), "type": r.get("type"),
        "venue": ((r.get("primary_location") or {}).get("source") or {}).get("display_name"),
        "authors": [a["author"]["display_name"] for a in (r.get("authorships") or [])[:5] if a.get("author")],
        "cited_by_count": r.get("cited_by_count"),
        "abstract": _openalex_abstract(r.get("abstract_inverted_index")),
    }


def _from_crossref(m):
    abstract = m.get("abstract")
    if abstract:
        abstract = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", abstract)).strip()
    issued = (m.get("issued") or {}).get("date-parts") or [[None]]
    return {
        "doi": (m.get("DOI") or "").lower(), "source": "crossref", "title": (m.get("title") or [None])[0],
        "year": issued[0][0], "type": m.get("type"), "venue": (m.get("container-title") or [None])[0],
        "authors": [" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in (m.get("author") or [])[:5]],
        "cited_by_count": m.get("is-referenced-by-count"), "abstract": abstract,
    }


def lookup_dois(dois, crossref=True, network=True):
    """Metadata + abstract per DOI, cached under cache/works/. OpenAlex first (50 per request), Crossref for
    anything OpenAlex lacks or has no abstract for. Without network, only the cache is read."""
    config.WORKS_DIR.mkdir(parents=True, exist_ok=True)
    dois = sorted({d.lower() for d in dois if d})
    out, todo = {}, []
    for d in dois:
        p = config.WORKS_DIR / f"{_slug(d)}.json"
        if p.exists():
            out[d] = json.loads(p.read_text(encoding="utf-8"))
        else:
            todo.append(d)
    if not network:
        return out
    extra = {"mailto": config.CONTACT} if "@" in config.CONTACT else {}
    for i in range(0, len(todo), 50):
        batch = todo[i:i + 50]
        txt = HTTP.get("https://api.openalex.org/works", {
            "filter": "doi:" + "|".join(batch), "per-page": 50,
            "select": "id,doi,title,publication_year,type,primary_location,authorships,cited_by_count,"
                      "abstract_inverted_index", **extra})
        for r in (json.loads(txt).get("results", []) if txt else []):
            w = _from_openalex(r)
            out[w["doi"]] = w
    for d in todo:
        if d in out and out[d].get("abstract"):
            continue
        if crossref:
            txt = HTTP.get(f"https://api.crossref.org/works/{d}", extra or None)
            if txt:
                cr = _from_crossref(json.loads(txt)["message"])
                if d not in out:
                    out[d] = cr
                elif cr.get("abstract"):
                    out[d]["abstract"], out[d]["abstract_source"] = cr["abstract"], "crossref"
        if d not in out:
            out[d] = {"doi": d, "source": None, "not_found": True}
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for d in todo:
        w = out[d]
        w.setdefault("abstract_source", w.get("source") if w.get("abstract") else None)
        w["fetched_at"] = now
        (config.WORKS_DIR / f"{_slug(d)}.json").write_text(json.dumps(w, ensure_ascii=False, indent=1),
                                                           encoding="utf-8")
    return out


def openalex_search(query, n=5):
    txt = HTTP.get("https://api.openalex.org/works", {
        "search": query, "per-page": n, "sort": "relevance_score:desc",
        "select": "id,doi,title,publication_year,type,primary_location,authorships,cited_by_count,"
                  "abstract_inverted_index"})
    return [_from_openalex(r) for r in (json.loads(txt).get("results", []) if txt else [])]
