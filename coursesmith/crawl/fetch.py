"""Fetch one page (or load it from the shared cache) and pre-screen link metadata in batches."""
from datetime import datetime, timezone

from ..sources.base import SourceError
from ..sources.keys import is_qualified
from .clean import clean_html
from .store import page_url


def fetch_page(client, store, title, force=False, adapters=None):
    """Fetch (or load from cache) one page. Returns (record, text, status).

    A bare title is a Wikipedia article, fetched through `client`. A qualified key (`rfc>9110`) goes to the
    adapter in `adapters` (a sources.Registry) that owns it."""
    if not force and store.has_page(title):
        return store.load_page(title), store.load_text(title), "cached"
    if is_qualified(title):
        if adapters is None:
            raise SourceError(f"'{title}' needs a source registry to fetch")
        rec = adapters.for_key(title).fetch(title)
        text = rec.pop("text")
        for frm, to in (rec.pop("aliases", None) or {}).items():
            store.add_alias(frm, to)
        store.save_page(rec, text)
        return rec, text, "fetched"
    p = client.parse_page(title)
    canonical = p["title"]
    for rd in p.get("redirects", []):
        store.add_alias(rd["from"], rd["to"])
    store.add_alias(title, canonical)
    html = p["text"]
    text, body_links, citations = clean_html(html, canonical)
    rec = {
        "title": canonical,
        "url": page_url(canonical),
        "revid": p.get("revid"),
        "pageid": p.get("pageid"),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "html": html,
        "links": [l["title"] for l in p.get("links", []) if l.get("ns") == 0 and l.get("exists", True)],
        "body_links": body_links,
        "lead_links": lead_links(html, canonical),
        "categories": [c["category"].replace("_", " ") for c in p.get("categories", []) if not c.get("hidden")],
        "hidden_categories": [c["category"].replace("_", " ") for c in p.get("categories", []) if c.get("hidden")],
        "sections": [{"level": s.get("level"), "line": s.get("line"), "anchor": s.get("anchor")}
                     for s in p.get("sections", [])],
        "templates": [t["title"] for t in p.get("templates", []) if t.get("ns") == 10],
        "citations": citations,
        "requested_title": title,
    }
    store.save_page(rec, text)
    return rec, text, "fetched"


def lead_links(html, own_title=""):
    """Article links in the lead section (before the first heading), in order. These carry the most weight
    in the concept graph and feed the lead-link prerequisite rule."""
    from bs4 import BeautifulSoup

    from .clean import _heading, _link_title

    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("div", class_="mw-parser-output") or soup
    for sel in (".navbox", ".sidebar", ".hatnote", ".infobox", ".reference", ".reflist", "table", "figure"):
        for el in root.select(sel):
            el.decompose()
    out, seen = [], set()
    for el in list(root.children):
        if _heading(el):
            break
        if getattr(el, "name", None) != "p":
            continue
        for a in el.find_all("a", href=True):
            t = _link_title(a)
            if t and t != own_title and t not in seen:
                seen.add(t)
                out.append(t)
    return out


def prescreen(client, store, titles):
    """Fill the link-metadata cache (categories, description, disambig, QID), 50 titles per request."""
    # qualified keys (other sources) have no Wikipedia metadata to fetch
    todo = list(dict.fromkeys(t for t in titles if not is_qualified(t) and store.canonical(t) not in store.meta))
    for i in range(0, len(todo), 50):
        resolved, meta = client.link_meta(todo[i:i + 50])
        for frm, to in resolved.items():
            store.add_alias(frm, to)
        store.meta.update(meta)
    return {t: store.canonical(t) for t in titles}
