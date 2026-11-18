"""Per-sentence links and citation years (from the chronicle's crawler/mentions.py).

mentions: the Wikipedia articles a sentence links to. Each page's stored HTML gives an anchor-text ->
article map, and every anchor text found in the sentence (whole words) counts as a mention. The page's own
title is left out. This drives the concept graph, clustering, and the "mentioned on two or more in-scope
pages" curriculum test.

cite_years: publication years of the works cited by the sentence's footnotes (newest first).
"""
import html as htmllib
import re
from urllib.parse import unquote

A_RE = re.compile(r'<a\s[^>]*?href="/wiki/([^"#?]+)(?:#[^"]*)?"[^>]*>(.*?)</a>', re.S)
TAG_RE = re.compile(r"<[^>]+>")
NON_ARTICLE_NS = {"File", "Help", "Category", "Wikipedia", "Template", "Portal", "Special", "Talk",
                  "Template talk", "Module", "Draft", "MediaWiki", "Image", "User", "User talk",
                  "WP", "H", "Wikt", "Wiktionary", "Commons", "Media"}
# Drop the reference list and everything after it: citations are parsed separately.
REF_CUT = re.compile(r'<(?:div|ol)[^>]*class="[^"]*(?:reflist|references)[^"]*"', re.S)


def anchor_map(page_html, canonical, own_title, skip=None):
    cut = REF_CUT.search(page_html)
    body = page_html[:cut.start()] if cut else page_html
    out = {}
    for href, inner in A_RE.findall(body):
        target = unquote(href).replace("_", " ").strip()
        if not target or (":" in target and target.split(":", 1)[0] in NON_ARTICLE_NS):
            continue
        text = re.sub(r"\s+", " ", htmllib.unescape(TAG_RE.sub("", inner))).strip()
        if len(text) < 3 or not re.search(r"[A-Za-z]{3}", text):
            continue
        can = canonical(target)
        if can == own_title or (skip and skip(can)):
            continue
        out.setdefault(text, can)
    return out


class PageMentions:
    """Finds the articles a sentence links to, using one page's anchor map."""

    def __init__(self, rec, canonical, skip=None):
        anchors = rec.get("anchors")
        if anchors:  # another source's adapter supplied anchor text -> key directly
            self.map = {}
            for text, key in anchors.items():
                can = canonical(key)
                if can != rec["title"] and not (skip and skip(can)):
                    self.map.setdefault(text, can)
        else:
            self.map = anchor_map(rec.get("html") or "", canonical, rec["title"], skip)
        texts = sorted(self.map, key=len, reverse=True)
        self.rx = re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, texts)) + r")(?![\w-])") if texts else None

    def __call__(self, sentence):
        if not self.rx:
            return []
        seen, out = set(), []
        for m in self.rx.finditer(sentence):
            t = self.map[m.group(1)]
            if t not in seen:
                seen.add(t)
                out.append(t)
        return out


def cite_years(rec_citations, cites):
    by_n = {c["n"]: c for c in rec_citations or []}
    ys = {w["year"] for n in cites for w in by_n.get(n, {}).get("works", []) if isinstance(w.get("year"), int)}
    return sorted(ys, reverse=True)
