"""PDF bytes -> cleaned text with headings and paragraphs recovered as well as a text layer allows.

pypdf returns lines with no structure. This drops page furniture (running headers, footers, page numbers),
re-joins hyphenated words, groups lines into paragraphs and promotes numbered or all-caps lines to headings.
It is a heuristic: a PDF's own layout decides how good the result is, and `sources check` reports a
low-structure PDF so the human can decide whether to keep it.
"""
import io
import re
from collections import Counter

NUM_HEAD = re.compile(r"^(\d+(?:\.\d+){0,3})\.?\s+([A-Z][^.!?]{2,90})$")
WORD_HEAD = re.compile(r"^(Chapter|Section|Appendix|Part)\s+[\w.]+(?:[:.\s-]+.{0,80})?$")
PAGE_NUM = re.compile(r"^(?:page\s+)?\d{1,4}(?:\s+of\s+\d{1,4})?$", re.I)


def extract_pages(data):
    import logging
    logging.getLogger("pypdf").setLevel(logging.ERROR)  # font-encoding chatter, harmless for text extraction
    try:
        from pypdf import PdfReader
    except ImportError:
        raise SystemExit("a source is a PDF: `pip install pypdf` to read it")
    reader = PdfReader(io.BytesIO(data))
    meta = getattr(reader, "metadata", None)
    pages = [(pg.extract_text() or "") for pg in reader.pages]
    return pages, (getattr(meta, "title", None) or "") if meta else ""


def flat_text(data):
    """One whitespace-collapsed string, for comparing against a document (verification authorities)."""
    pages, _ = extract_pages(data)
    return re.sub(r"\s+", " ", " ".join(pages))


def _furniture(pages):
    """Lines that repeat on at least 40% of pages are running headers and footers."""
    if len(pages) < 3:
        return set()
    c = Counter()
    for p in pages:
        for l in {l.strip() for l in p.splitlines() if l.strip()}:
            if len(l) < 90:
                c[l] += 1
    return {l for l, n in c.items() if n >= max(3, 0.4 * len(pages))}


def structure(pages, title=""):
    skip = _furniture(pages)
    lines = []
    for p in pages:
        for l in p.splitlines():
            l = l.strip()
            if l in skip or PAGE_NUM.match(l):
                continue
            lines.append(l)
        lines.append("")
    # re-join words hyphenated at a line break
    joined, i = [], 0
    while i < len(lines):
        l = lines[i]
        if l.endswith("-") and len(l) > 1 and l[-2].isalpha() and i + 1 < len(lines) and lines[i + 1][:1].islower():
            lines[i + 1] = l[:-1] + lines[i + 1]
        else:
            joined.append(l)
        i += 1
    longest = max((len(l) for l in joined), default=0)
    out, para = [f"# {title}"] if title else [], []

    def flush():
        if para:
            out.append(" ".join(para))
            para.clear()

    for l in joined:
        if not l:
            flush()
            continue
        m = NUM_HEAD.match(l)
        if m and not l.endswith(","):
            flush()
            out += ["", "#" * (2 + m.group(1).count(".")) + " " + l]
            continue
        if WORD_HEAD.match(l) or (l.isupper() and 3 <= len(l) <= 80 and not l.endswith(".")):
            flush()
            out += ["", "## " + l.title() if l.isupper() else "## " + l]
            continue
        para.append(l)
        if l.endswith((".", ":", "?", "!")) and len(l) < 0.6 * longest:
            flush()
    flush()
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"


def pdf_to_text(data, title=""):
    pages, meta_title = extract_pages(data)
    return structure(pages, title or meta_title), meta_title
