"""Bracketed references ([RFC2119], [12], [Fielding2000]) -> numbered footnotes and a citation list.

Wikipedia marks a footnote `[^n]` and ships a parsed citation list, and the sentence index reads both: it ties
each sentence to the works it cites, and the DOIs among them feed the verification pass. Standards documents
and papers cite with bracketed labels and a References section. This module turns those into the same shape
so tier-B verification and cite years work for them too.
"""
import re

BRACKET_RE = re.compile(r"\[([A-Za-z][A-Za-z0-9._-]{1,40}|\d{1,3})\]")
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[^\s\"<>,;]+)", re.I)
RFC_RE = re.compile(r"\bRFC\s?(\d{1,5})\b", re.I)
YEAR_RE = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")
URL_RE = re.compile(r"<?(https?://[^\s>]+)>?")
ENTRY_RE = re.compile(r"^\s{0,6}\[([^\]\s]{1,41})\]:?\s+(\S.*)$")
REFS_HEAD = re.compile(r"^\s*(?:\d+(?:\.\d+)*\.?\s+)?(normative references|informative references|references|"
                       r"bibliography|works cited)\s*$", re.I)


def parse_references(raw):
    """{label: raw reference text} from the reference sections of a document's raw text."""
    refs, in_refs, label = {}, False, None
    for line in raw.splitlines():
        if REFS_HEAD.match(line.strip("# ").strip()) or REFS_HEAD.match(line):
            in_refs, label = True, None
            continue
        if not in_refs:
            continue
        m = ENTRY_RE.match(line)
        if m:
            label = m.group(1)
            refs[label] = m.group(2).strip()
        elif label and line.strip() and line[:1] in " \t":
            refs[label] += " " + line.strip()
        elif not line.strip():
            label = None
    return refs


def _work(label, raw):
    w = {"genre": "reference", "title": raw[:160], "source": "bracket"}
    d = DOI_RE.search(raw)
    if d:
        w["doi"] = d.group(1).rstrip(".)").lower()
    r = RFC_RE.search(label) or RFC_RE.search(raw)
    if r:
        w["rfc"] = r.group(1)
        w["url"] = f"https://www.rfc-editor.org/info/rfc{r.group(1)}"
    u = URL_RE.search(raw)
    if u and "url" not in w:
        w["url"] = u.group(1).rstrip(".,)")
    ys = YEAR_RE.findall(raw)
    if ys:
        w["year"] = int(ys[-1])
    return w


def number_citations(text, refs):
    """Replace each in-body `[label]` that names a known reference with `[^n]` and return (text, citations).

    Citations are numbered in order of first appearance; a label cited twice reuses its number. A bracket
    that is not a known reference is left alone, so `[0]` array indexes and the like survive."""
    n_of, citations = {}, []

    def sub(m):
        label = m.group(1)
        if label not in refs:
            return m.group(0)
        if label not in n_of:
            n_of[label] = len(citations) + 1
            raw = refs[label]
            citations.append({"n": n_of[label], "note_id": f"ref-{label}", "text": raw[:600], "kind": "citation",
                              "works": [_work(label, raw)]})
        return f"[^{n_of[label]}]"

    return BRACKET_RE.sub(sub, text), citations
