"""Parse a Wikipedia page's reference list into structured citations.

Each footnote (<li id="cite_note-...">) becomes
    {"n": 7, "note_id": "cite_note-Bell2015-7", "text": "...", "works": [ {...}, ... ]}
where each work comes from the COinS metadata (span.Z3988) that Wikipedia's citation
templates emit: doi, title, container (journal/book), year, first author, genre,
pmid, bibcode, arxiv, isbn, url. Short footnotes ("Smith 2010, p. 5") are resolved
through their #CITEREF link to the full citation in the bibliography.

`n` numbers footnotes in document order; cleaned text carries matching '[^n]' markers
where the superscript reference links were, so an extracted sentence can be tied to
the citations attached to it.
"""
import re
from urllib.parse import parse_qs, unquote

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>&]+)", re.I)


def _clean_doi(d):
    d = unquote(d).strip().rstrip(".,;)")
    return d.lower() if d.lower().startswith("10.") else None


def _coins(span):
    q = parse_qs(span.get("title", ""), keep_blank_values=False)
    g = lambda k: (q.get(k) or [None])[0]
    w = {"genre": g("rft.genre"),
         "title": g("rft.atitle") or g("rft.btitle") or g("rft.title"),
         "container": g("rft.jtitle") or (g("rft.btitle") if g("rft.atitle") else None),
         "date": g("rft.date"),
         "volume": g("rft.volume"), "pages": g("rft.pages") or g("rft.spage"),
         "first_author": g("rft.au") or (" ".join(x for x in (g("rft.aufirst"), g("rft.aulast")) if x) or None),
         "isbn": g("rft.isbn"), "issn": g("rft.issn")}
    for rid in q.get("rft_id", []):
        if rid.startswith("info:doi/"):
            w["doi"] = _clean_doi(rid[len("info:doi/"):])
        elif rid.startswith("info:pmid/"):
            w["pmid"] = rid[len("info:pmid/"):]
        elif rid.startswith("info:bibcode/"):
            w["bibcode"] = rid[len("info:bibcode/"):]
        elif rid.startswith("info:arxiv/"):
            w["arxiv"] = rid[len("info:arxiv/"):]
        elif rid.startswith("http") and "url" not in w:
            w["url"] = rid
    if w.get("date"):
        m = re.search(r"\b(1[5-9]\d\d|20\d\d)\b", w["date"])
        w["year"] = int(m.group(1)) if m else None
    return {k: v for k, v in w.items() if v}


def _works_in(el, soup, seen_targets=None):
    works = [_coins(s) for s in el.select("span.Z3988")]
    # Short footnotes: follow #CITEREF... links to the full citation.
    for a in el.select('a[href^="#CITEREF"]'):
        tid = a["href"][1:]
        if seen_targets is not None and tid in seen_targets:
            continue
        tgt = soup.find(id=tid)
        if tgt is None:
            continue
        z = tgt.find_next_sibling("span", class_="Z3988") or tgt.find("span", class_="Z3988")
        if z is not None:
            w = _coins(z)
            w["via"] = tid
            works.append(w)
    # DOI links not covered by COinS (hand-written references).
    have = {w.get("doi") for w in works}
    for a in el.select('a[href*="doi.org/"]'):
        d = _clean_doi(a["href"].split("doi.org/", 1)[1])
        if d and d not in have:
            works.append({"doi": d, "title": a.get_text(" ", strip=True)[:300] or None, "source": "doi-link"})
            have.add(d)
    return works


def parse_citations(soup):
    """Return (citations, note_to_n). Call before references/navboxes are removed."""
    cits, note_to_n = [], {}
    for li in soup.select("ol.references > li[id]"):
        nid = li["id"]
        if nid in note_to_n:
            continue
        rt = li.select_one(".reference-text") or li
        text = re.sub(r"\s+", " ", rt.get_text(" ", strip=True))
        n = len(cits) + 1
        note_to_n[nid] = n
        works = _works_in(rt, soup)
        cits.append({"n": n, "note_id": nid, "text": text[:600], "works": works,
                     "kind": "citation" if works else ("note" if len(text) > 0 else "empty")})
    return cits, note_to_n


def ref_marker(sup, note_to_n):
    a = sup.find("a", href=True)
    if not a or not a["href"].startswith("#cite_note-"):
        return None
    n = note_to_n.get(a["href"][1:])
    return f"[^{n}]" if n else None
