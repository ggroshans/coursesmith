"""Parsed DOM -> cleaned plain text, for every source.

The cleaned text is a small Markdown subset the rest of the pipeline reads (extract/split.py, graph lead
statistics, dossiers):

- line 1 is `# <title>`; section headings are `## Heading` lines ('###' for h3, ...), each after a blank line;
- every paragraph is one line; list items are `- item` (two spaces of indent per level); definition lists are
  plain lines; quotes are `> text`;
- a table row is one line with cells joined by ` | `, rowspan and colspan expanded so each row carries its
  context, with an optional `Table: caption` line before the rows and a blank line after;
- footnote markers are `[^n]`, matching the citation list that came with the page;
- the References / See also / External links style sections are dropped.

`crawl/clean.py` is the Wikipedia front end (it prepares MediaWiki's HTML and parses its citations, then runs
this emitter in its legacy mode, which must stay byte-identical so every sent_id stays valid). Markdown, docs
sites and the other adapters use the options below: headings found at any depth, code blocks dropped, and a
literal pipe or leading `#` in prose neutralized so a sentence is never read as a table row or a heading.
"""
import re

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

DROP_SECTIONS = {
    "references", "notes", "footnotes", "citations", "sources", "bibliography", "further reading",
    "external links", "see also", "notes and references", "references and notes", "works cited",
    "literature", "general references", "cited sources", "explanatory notes", "general and cited references",
    "general bibliography", "reference", "source", "gallery", "image gallery", "further information",
    "external link", "note", "related pages", "selected bibliography",
}  # exactly the Wikipedia set: changing it would change cached text and so sent_ids

# for standards documents, READMEs, docs sites and papers
DOC_DROP_SECTIONS = DROP_SECTIONS | {
    "normative references", "informative references", "acknowledgements", "acknowledgments",
    "authors' addresses", "author's address", "table of contents", "contents", "license", "licence",
    "contributing", "contributors", "credits", "changelog", "change log", "sponsors", "backers",
    "star history", "support", "table of content",
}

WS_RE = re.compile(r"\s+")
PIPE = "∣"  # DIVIDES, stands in for a literal "|" in prose


def norm(s):
    s = WS_RE.sub(" ", s).strip()
    s = re.sub(r"\s+([,.;:!?)\]])", r"\1", s)
    s = re.sub(r"([(\[])\s+", r"\1", s)
    return s


def heading(el, min_level=2):
    """(level, text) if el is a heading, or a MediaWiki `.mw-heading` wrapper around one."""
    if not isinstance(el, Tag):
        return None
    h = el
    if "mw-heading" in (el.get("class") or []):
        h = el.find(re.compile(rf"^h[{min_level}-6]$"))
        if h is None:
            return None
    m = re.match(rf"^h([{min_level}-6])$", h.name or "")
    if not m:
        return None
    return int(m.group(1)), norm(h.get_text())


def _span(v):
    try:
        return max(1, int(re.sub(r"[^\d]", "", str(v)) or 1))
    except ValueError:
        return 1


def table_rows(table, merge="all"):
    """Expand a table into a list of row-lists, honouring rowspan/colspan.

    merge="all" (the default, kept so earlier courses keep their sentence ids) merges any neighbouring cells with
    equal text; merge="span" merges only the copies made by one cell's colspan, so a row of "Yes | Yes | Yes"
    stays three cells."""
    rows = [tr for tr in table.find_all("tr") if tr.find_parent("table") is table]
    grid, pending = [], {}  # pending: col -> [rows_remaining, text]
    for tr in rows:
        cells = tr.find_all(["th", "td"], recursive=False)
        row, col, ci, origin = [], 0, 0, []  # origin: which source cell each entry of `row` came from
        while ci < len(cells) or any(c >= col for c in pending):
            if col in pending:
                rem, txt = pending[col]
                row.append(txt)
                origin.append(("p", col))
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
            txt = norm(cell.get_text(" "))
            cs = _span(cell.get("colspan"))
            rs = min(_span(cell.get("rowspan")), 500)
            for _ in range(cs):
                row.append(txt)
                origin.append(("c", ci))
                if rs > 1:
                    pending[col] = [rs - 1, txt]
                col += 1
        # collapse colspan duplicates; drop empty trailing cells
        out, last = [], None
        for c, o in zip(row, origin):
            if not out or c != out[-1] or (merge == "span" and o != last):
                out.append(c)
            last = o
        while out and not out[-1]:
            out.pop()
        if any(out):
            grid.append(out)
    return grid


def pre_language(pre):
    """The language a <pre> block declares (class language-json, lang-json, highlight-json or data-lang), else ''."""
    for el in [pre, *pre.find_all("code", limit=1), *list(pre.parents)[:2]]:
        if el.get("data-lang"):
            return str(el["data-lang"]).strip().lower()
        for c in el.get("class") or []:
            for pfx in ("language-", "lang-", "highlight-", "source-"):
                if c.startswith(pfx) and len(c) > len(pfx):
                    return c[len(pfx):].lower()
    return ""


GENERIC_DROP = "script, style, noscript, template, nav, footer, aside, svg, iframe, form, button, " \
               "[hidden], [aria-hidden=true]"


def generic_prepare(root, drop=()):
    """Page chrome and non-text elements out, comments out, <br> to a space. For sources other than MediaWiki."""
    for c in root.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for sel in (GENERIC_DROP, *drop):
        if not sel:
            continue
        for el in root.select(sel):
            el.decompose()
    for br in root.find_all("br"):
        br.replace_with(NavigableString(" "))


class Emitter:
    """Walks a DOM root and writes the cleaned text.

    resolve_link(a_tag) -> key or None names the page a link points at (None drops the link).
    nested_headings: find headings inside div/section/etc., not only among the root's direct children.
    code: "text" keeps <pre> as a paragraph (the Wikipedia legacy), "drop" removes it and counts it, "keep"
          writes a single `Code: <first line>` line.
    neutralize: a literal " | " in prose becomes U+2223 and a leading "#"/">" is escaped, so no sentence is
          mistaken for a table row, heading or quote.
    min_level: the shallowest heading level taken as a section (2 for Wikipedia, whose h1 is the page title).
    listings: a text.docfx.Listings; every <pre> goes into it and leaves a marker line (⟦L3⟧) in the text.
    table_cells: "all" merges neighbouring equal cells of a table row (legacy); "span" merges only colspan copies.
    """

    def __init__(self, resolve_link=None, drop_sections=DROP_SECTIONS, nested_headings=False, code="text",
                 neutralize=False, min_level=2, collect_anchors=False, table_cells="all", listings=None):
        self.table_cells = table_cells
        self.listings = listings
        self.resolve_link = resolve_link
        self.drop_sections = drop_sections
        self.nested = nested_headings
        self.code = code
        self.neutralize = neutralize
        self.min_level = min_level
        self.collect_anchors = collect_anchors
        self.lines, self.links, self.anchors, self.sections = [], [], {}, []
        self.lead_links = []  # links met before the first section heading
        self.code_blocks = 0
        self.skip_level = None
        self._seen_links = set()

    # -- links and text ------------------------------------------------------------
    def link_scan(self, el):
        if self.resolve_link is None or not isinstance(el, Tag):
            return
        for a in el.find_all("a", href=True):
            t = self.resolve_link(a)
            if not t:
                continue
            if t not in self._seen_links:
                self._seen_links.add(t)
                self.links.append(t)
                if not self.sections:
                    self.lead_links.append(t)
            if self.collect_anchors:
                text = norm(a.get_text())
                if len(text) >= 3 and re.search(r"[A-Za-z]{3}", text):
                    self.anchors.setdefault(text, t)

    def text(self, s, prefix=""):
        s = norm(s)
        if s and self.neutralize:
            s = s.replace(" | ", f" {PIPE} ").replace("|", PIPE)
            if not prefix and s[0] in "#>":
                s = "＃" + s[1:] if s[0] == "#" else "＞" + s[1:]
        if s:
            self.lines.append(prefix + s)

    # -- structure -----------------------------------------------------------------
    def on_heading(self, level, text):
        if self.skip_level is not None and level <= self.skip_level:
            self.skip_level = None
        if self.skip_level is None and text.lower().strip(" :") in self.drop_sections:
            self.skip_level = level
            return
        if self.skip_level is None:
            self.lines.append("")
            self.lines.append("#" * level + " " + text)
            self.sections.append((level, text))

    def block(self, el, depth=0):
        if self.nested and isinstance(el, Tag):
            h = heading(el, self.min_level)
            if h:
                self.on_heading(*h)
                return
        if self.skip_level is not None:
            return
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
            for row in table_rows(el, self.table_cells):
                self.lines.append(" | ".join(row))
            self.lines.append("")
        elif name == "blockquote":
            self.link_scan(el)
            self.text(el.get_text(), "> ")
        elif name == "pre" and self.listings is not None:
            self.code_blocks += 1
            self.lines.extend(self.listings.add(pre_language(el), el.get_text()))
        elif name == "pre" and self.code != "text":
            self.code_blocks += 1
            if self.code == "keep":
                first = next((l.strip() for l in el.get_text().splitlines() if l.strip()), "")
                if first:
                    self.lines.append("Code: " + first[:120].replace(" | ", f" {PIPE} "))
        elif name in ("div", "section", "center", "span") or (
                self.nested and name in ("article", "main", "details", "figure", "summary")):
            for c in el.children:
                self.block(c, depth)
        elif name in ("h2", "h3", "h4", "h5", "h6") or (self.nested and name == "h1"):
            pass  # handled by the caller (or ignored in legacy mode)
        else:
            self.link_scan(el)
            self.text(el.get_text())

    def run(self, root, title=""):
        """Emit the whole page under `root` and return the cleaned text."""
        if title:
            self.lines.append(f"# {title}")
        for el in list(root.children):
            h = heading(el, self.min_level)
            if h:
                self.on_heading(*h)
                continue
            if self.skip_level is not None:
                continue
            self.block(el)
        text = "\n".join(self.lines)
        return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def soup_root(html):
    return BeautifulSoup(html, "html.parser")
