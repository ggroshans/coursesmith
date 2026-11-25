"""A generic HTML page (a docs site, rendered Markdown) -> cleaned text, via the shared emitter."""
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

from .emit import DOC_DROP_SECTIONS, Emitter, generic_prepare, norm

MAIN_CANDIDATES = ["main", "article", "[role=main]", "#content", "#main", ".content", ".markdown-body", ".main-content"]


@dataclass
class Doc:
    text: str
    name: str = ""
    links: list = field(default_factory=list)
    lead_links: list = field(default_factory=list)
    anchors: dict = field(default_factory=dict)
    sections: list = field(default_factory=list)
    code_blocks: int = 0


def find_main(soup, selector=None):
    """The element holding the page's content: the configured selector, else the first of the usual containers."""
    for sel in ([selector] if selector else []) + MAIN_CANDIDATES:
        try:
            el = soup.select_one(sel)
        except Exception:
            el = None
        if el is not None and el.get_text(strip=True):
            return el
    return soup.body or soup


def html_to_doc(html, name="", selector=None, drop=(), resolve_link=None, drop_sections=DOC_DROP_SECTIONS,
                demote_h1=True, table_cells="all"):
    soup = BeautifulSoup(html, "html.parser")
    title_tag = soup.find("title")
    root = find_main(soup, selector)
    generic_prepare(root, drop)
    # <a> that wrap only an image (badges, logos) carry no text; the image itself is dropped below
    for img in root.find_all("img"):
        img.decompose()
    h1s = root.find_all("h1")
    if h1s:
        first = norm(h1s[0].get_text())
        if first and not name:
            name = first
        h1s[0].decompose()
        if demote_h1:
            for h in h1s[1:]:
                h.name = "h2"
    if not name and title_tag:
        name = norm(title_tag.get_text())
    em = Emitter(resolve_link=resolve_link, drop_sections=drop_sections, nested_headings=True, code="drop",
                 neutralize=True, min_level=2, collect_anchors=True, table_cells=table_cells)
    text = em.run(root, name)
    return Doc(text=text, name=name, links=em.links, lead_links=em.lead_links, anchors=em.anchors,
               sections=em.sections, code_blocks=em.code_blocks)
