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

from bs4 import BeautifulSoup, Comment, NavigableString

from ..text.emit import DROP_SECTIONS, Emitter, heading, norm, table_rows, _span  # noqa: F401
from .citations import parse_citations, ref_marker

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

_norm = norm  # kept under its old name for _prepare and the importers
WS_RE = re.compile(r"\s+")


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
    return heading(el, 2)


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


def clean_html(html, title=""):
    """Return (text, body_links, citations)."""
    soup = BeautifulSoup(html, "html.parser")
    root = soup.find("div", class_="mw-parser-output") or soup
    # the parser's own report (NewPP limit report, render ids) sits in HTML comments inside the output
    for c in root.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    citations, note_to_n = parse_citations(root)
    _prepare(root, note_to_n)
    em = Emitter(resolve_link=_link_title, drop_sections=DROP_SECTIONS)  # legacy mode: byte-identical to before
    text = em.run(root, title)
    return text, em.links, citations
