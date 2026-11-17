"""Readers for the places Wikipedia maps a subject :

- navbox templates: groups and subgroups of article links (the best free hierarchy)
- an index page: a flat alphabetical list
- category trees: depth 1 is clean, depth 2 needs filtering, depth 3 drifts (never used)
- Vital Articles sections: a heading anchor on a Vital list page
- WikiProject importance: Top/High/Mid/Low-importance <Project> articles (talk-page categories)

Every reader caches its result under cache/hubs/ so a rerun of `frame build` costs no requests.
"""
import json
import re
from urllib.parse import unquote

from bs4 import BeautifulSoup

from .. import config
from ..crawl.clean import NON_ARTICLE_NS
from ..util import atomic_write, slug

HUB_CACHE = config.CACHE / "hubs"


def _cached(key, fn):
    p = HUB_CACHE / f"{slug(key, 120)}.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    v = fn()
    atomic_write(p, json.dumps(v, ensure_ascii=False))
    return v


def _title_of(a):
    href = a.get("href", "")
    if not href.startswith("/wiki/") or "redlink=1" in href:
        return None
    t = unquote(href[6:].split("#", 1)[0]).replace("_", " ").strip()
    if not t or (":" in t and t.split(":", 1)[0] in NON_ARTICLE_NS):
        return None
    return t


def navbox(client, template):
    """[{"group": str, "subgroup": str|None, "links": [titles]}] in navbox order."""
    def fetch():
        soup = BeautifulSoup(client.parse_html(template)["text"], "html.parser")
        out = []
        top = soup.select_one("table.navbox-inner") or soup

        def walk(table, parent):
            for tr in table.find_all("tr", recursive=False) or table.select(":scope > tbody > tr"):
                th = tr.find("th", class_="navbox-group", recursive=False)
                td = tr.find("td", class_="navbox-list", recursive=False)
                if not td:
                    continue
                name = th.get_text(" ", strip=True) if th else (parent or "General")
                sub = td.find("table", class_="navbox-subgroup")
                if sub:
                    walk(sub, name)
                    continue
                links = list(dict.fromkeys(t for t in (_title_of(a) for a in td.find_all("a")) if t))
                if links:
                    out.append({"group": parent or name, "subgroup": name if parent else None, "links": links})

        walk(_tbody(top), None)
        return out
    return _cached(f"navbox {template}", fetch)


def _tbody(t):
    return t.find("tbody", recursive=False) or t


def index_page(client, title):
    """Article links in an index page's body, in order."""
    def fetch():
        soup = BeautifulSoup(client.parse_html(title)["text"], "html.parser")
        root = soup.find("div", class_="mw-parser-output") or soup
        for el in root.select(".navbox, .reflist, .references, .hatnote, .sidebar"):
            el.decompose()
        return list(dict.fromkeys(t for t in (_title_of(a) for a in root.find_all("a")) if t and t != title))
    return _cached(f"index {title}", fetch)


def vital_section(client, spec):
    """'Page#Section' -> article links under that heading (until the next heading of the same level)."""
    page, _, anchor = spec.partition("#")

    def fetch():
        soup = BeautifulSoup(client.parse_html(page)["text"], "html.parser")
        root = soup.find("div", class_="mw-parser-output") or soup
        if not anchor:
            return list(dict.fromkeys(t for t in (_title_of(a) for a in root.find_all("a")) if t))
        want = anchor.replace(" ", "_")
        head = root.find(id=want) or root.find(id=anchor)
        if head is None:
            return []
        h = head if re.match(r"h[1-6]$", head.name or "") else head.find_parent(re.compile(r"^h[1-6]$")) or head
        wrapper = h.find_parent("div", class_="mw-heading") or h
        level = int(h.name[1]) if re.match(r"h[1-6]$", h.name or "") else 2
        out = []
        for el in wrapper.find_next_siblings():
            hh = el.find(re.compile(r"^h[1-6]$")) if "mw-heading" in (el.get("class") or []) else \
                (el if re.match(r"h[1-6]$", el.name or "") else None)
            if hh is not None and int(hh.name[1]) <= level:
                break
            out += [t for t in (_title_of(a) for a in el.find_all("a")) if t]
        return list(dict.fromkeys(out))
    return _cached(f"vital {spec}", fetch)


def category_tree(client, roots, depth=1, exclude=()):
    """{"categories": {cat: distance}, "pages": {title: distance}} for a BFS of the category graph."""
    excl = {e.removeprefix("Category:") for e in exclude}

    def fetch():
        cats, pages = {}, {}
        frontier = [(r.removeprefix("Category:"), 0) for r in roots]
        while frontier:
            cat, d = frontier.pop(0)
            if cat in cats or cat in excl:
                continue
            cats[cat] = d
            for title, ns in client.category_members(cat):
                if ns == 14:
                    sub = title.removeprefix("Category:")
                    if d + 1 <= depth and sub not in cats and sub not in excl:
                        frontier.append((sub, d + 1))
                elif ns == 0 and title not in pages:
                    pages[title] = d
        return {"categories": cats, "pages": pages}
    key = f"cattree {'|'.join(roots)} d{depth} x{len(excl)}"
    return _cached(key, fetch)


IMPORTANCE = ("Top", "High", "Mid", "Low")


def wikiproject_importance(client, project):
    """{title: importance} from the talk-page categories '<Imp>-importance <Project> articles'."""
    def fetch():
        out = {}
        for imp in IMPORTANCE:
            for title, ns in client.category_members(f"Category:{imp}-importance {project} articles", ns=(1,)):
                out.setdefault(title.removeprefix("Talk:"), imp)
        return out
    return _cached(f"wikiproject {project}", fetch)


def drop(key):
    p = HUB_CACHE / f"{slug(key, 120)}.json"
    if p.exists():
        p.unlink()
