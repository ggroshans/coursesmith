"""Parsed-HTML -> cleaned plain text.

- Section headings become '## Heading' lines ('###' for h3, etc.).
- Table rows become pipe-separated lines; rowspan/colspan are expanded into a full
  grid so every row carries its context (e.g. 'Paleozoic | Cambrian | ... | 538.8').
- References, navboxes, sidebars, hatnotes, edit links, images and the
  'See also' / 'References' / 'External links' (etc.) sections are dropped.
- Inline maintenance tags are kept as text: '[citation needed]', '[dubious]' ...
- Footnote superscripts become '[^n]' markers; the reference list itself is parsed into
  structured citations (crawler/citations.py) and returned alongside the text.
- Also returns the article-body links (in order of appearance, deduplicated),
  which drive the crawl frontier; the API's full link list includes navbox and
  reference links and is kept separately in raw/.
"""
import re
from urllib.parse import unquote

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

from .citations import parse_citations, ref_marker

DROP_SECTIONS = {
    "references", "notes", "footnotes", "citations", "sources", "bibliography", "further reading",
    "external links", "see also", "notes and references", "references and notes", "works cited",
    "literature", "general references", "cited sources", "explanatory notes", "general and cited references",
    "general bibliography", "reference", "source", "gallery", "image gallery", "further information",
    "external link", "note", "related pages", "selected bibliography",
}

DROP_SELECTORS = [
    "style", "script", "link", "meta", "noscript",
    ".mw-editsection", "sup.reference", ".reflist", ".references", ".mw-references-wrap",
    ".navbox", ".navbox-styles", ".vertical-navbox", ".sidebar", ".hatnote", ".dablink",
    ".shortdescription", ".ambox", ".mbox-small", ".metadata", ".portalbox", ".sistersitebox",
    ".side-box", ".authority-control", ".mw-empty-elt", "#toc", ".toc", ".printfooter",
    "#coordinates", ".geo-nondefault", "figure", ".thumb", ".gallery", ".timeline-wrapper",
    ".mw-kartographer-container", "audio", "video", "img", ".noviewer",
    ".searchaux", ".navbar",  # graphical timeline widgets and their v-t-e boxes
]

HEADING_RE = re.compile(r"^h([2-6])$")
WS_RE = re.compile(r"\s+")


def _norm(s):
    s = WS_RE.sub(" ", s).strip()
    s = re.sub(r"\s+([,.;:!?)\]])", r"\1", s)
    s = re.sub(r"([(\[])\s+", r"\1", s)
    return s


def _prepare(soup, note_to_n):
    # Footnote superscripts -> '[^n]' markers keyed to the parsed citation list.
    for sup in soup.select("sup.reference"):
        mk = ref_marker(sup, note_to_n)
        sup.replace_with(NavigableString(mk) if mk else NavigableString(""))
    # Keep inline maintenance templates ([citation needed], [dubious], [when?]) as plain text.
    for sup in soup.select("sup.Inline-Template, sup.noprint.Template-Fact"):
        sup.replace_with(NavigableString(" " + _norm(sup.get_text()) + " "))
    # Powers of ten: 10<sup>5.48</sup> would read "105.48" once tags are stripped; keep it as "10^5.48".
    for sup in soup.find_all("sup"):
        prev = sup.previous_sibling
        if isinstance(prev, NavigableString) and re.search(r"10\s*$", str(prev)):
            sup.replace_with(NavigableString("^" + _norm(sup.get_text())))
    # Math: replace with its TeX annotation (or alt text).
    for m in soup.select("span.mwe-math-element"):
        ann = m.find("annotation")
        alt = ann.get_text() if ann else (m.find("img") or {}).get("alt", "")
        m.replace_with(NavigableString(" " + _norm(alt) + " "))
    for br in soup.find_all("br"):
        br.replace_with(NavigableString(" "))
    for sel in DROP_SELECTORS:
        for el in soup.select(sel):
            el.decompose()
    # NB: '.noprint' is NOT dropped wholesale: infobox ages ("2023 Ma") and fossil temporal
    # ranges sit inside noprint wrappers. Noisy noprint items are covered by DROP_SELECTORS.


def _heading(el):
    """Return (level, text) if el is a heading or a .mw-heading wrapper."""
    if not isinstance(el, Tag):
        return None
    h = el
    if "mw-heading" in (el.get("class") or []):
        h = el.find(re.compile(r"^h[2-6]$"))
        if h is None:
            return None
    m = HEADING_RE.match(h.name or "")
    if not m:
        return None
    return int(m.group(1)), _norm(h.get_text())


def table_rows(table):
    """Expand a table into a list of row-lists, honouring rowspan/colspan."""
    rows = [tr for tr in table.find_all("tr") if tr.find_parent("table") is table]
    grid, pending = [], {}  # pending: col -> [rows_remaining, text]
    for tr in rows:
        cells = tr.find_all(["th", "td"], recursive=False)
        row, col, ci = [], 0, 0
        while ci < len(cells) or any(c >= col for c in pending):
            if col in pending:
                rem, txt = pending[col]
                row.append(txt)
                if rem - 1 > 0:
                    pending[col] = [rem - 1, txt]
                else:
                    del pending[col]
                col += 1
                continue
            if ci >= len(cells):
                col += 1
                continue
            cell = cells[ci]
            ci += 1
            txt = _norm(cell.get_text(" "))
            cs = _span(cell.get("colspan"))
            rs = min(_span(cell.get("rowspan")), 500)
            for _ in range(cs):
                row.append(txt)
                if rs > 1:
                    pending[col] = [rs - 1, txt]
                col += 1
        # collapse colspan duplicates; drop empty trailing cells
        out = []
        for c in row:
            if not out or c != out[-1]:
                out.append(c)
        while out and not out[-1]:
            out.pop()
        if any(out):
            grid.append(out)
    return grid


def _span(v):
    try:
        return max(1, int(re.sub(r"[^\d]", "", str(v)) or 1))
    except ValueError:
        return 1


def _link_title(a):
    href = a.get("href", "")
    if not href.startswith("/wiki/"):
        return None
    target = unquote(href[len("/wiki/"):].split("#", 1)[0]).replace("_", " ").strip()
    if not target:
        return None
    if ":" in target and target.split(":", 1)[0] in NON_ARTICLE_NS:
        return None
    return target


NON_ARTICLE_NS = {"File", "Help", "Category", "Wikipedia", "Template", "Portal", "Special", "Talk",
                  "Template talk", "Module", "Draft", "MediaWiki", "Image", "User", "User talk",
                  "WP", "H", "Wikt", "Wiktionary", "Commons", "Media"}


class _Emitter:
    def __init__(self):
        self.lines = []
        self.links = []
        self._seen_links = set()

    def link_scan(self, el):
        for a in el.find_all("a", href=True) if isinstance(el, Tag) else []:
            t = _link_title(a)
            if t and t not in self._seen_links:
                self._seen_links.add(t)
                self.links.append(t)

    def text(self, s, prefix=""):
        s = _norm(s)
        if s:
            self.lines.append(prefix + s)

    def block(self, el, depth=0):
        if isinstance(el, NavigableString):
            self.text(str(el))
            return
        if not isinstance(el, Tag):
            return
        name = el.name
        if name == "p":
            self.link_scan(el)
            self.text(el.get_text())
        elif name in ("ul", "ol"):
            for li in el.find_all("li", recursive=False):
                nested = [c for c in li.find_all(["ul", "ol"], recursive=False)]
                for n in nested:
                    n.extract()
                self.link_scan(li)
                self.text(li.get_text(), "  " * depth + "- ")
                for n in nested:
                    self.block(n, depth + 1)
        elif name == "dl":
            for c in el.find_all(["dt", "dd"], recursive=False):
                self.link_scan(c)
                self.text(c.get_text(), "" if c.name == "dt" else "  ")
        elif name == "table":
            self.link_scan(el)
            cap = el.find("caption")
            if cap:
                self.text(cap.get_text(), "Table: ")
            for row in table_rows(el):
                self.lines.append(" | ".join(row))
            self.lines.append("")
        elif name == "blockquote":
            self.link_scan(el)
            self.text(el.get_text(), "> ")
        elif name in ("div", "section", "center", "span"):
            for c in el.children:
                self.block(c, depth)
        elif name in ("h2", "h3", "h4", "h5", "h6"):
            pass  # handled by caller
        else:
            self.link_scan(el)
            self.text(el.get_text())


def clean_html(html, title=""):
    """Return (text, body_links, citations)."""
    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("div", class_="mw-parser-output") or soup
    # the parser's own report (NewPP limit report, render ids) sits in HTML comments inside the output
    for c in root.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    citations, note_to_n = parse_citations(root)
    _prepare(root, note_to_n)
    em = _Emitter()
    if title:
        em.lines.append(f"# {title}")
    skip_level = None
    for el in list(root.children):
        h = _heading(el)
        if h:
            level, text = h
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and text.lower().strip(" :") in DROP_SECTIONS:
                skip_level = level
                continue
            if skip_level is None:
                em.lines.append("")
                em.lines.append("#" * level + " " + text)
            continue
        if skip_level is not None:
            continue
        em.block(el)
    text = "\n".join(em.lines)
    text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
    return text, em.links, citations
