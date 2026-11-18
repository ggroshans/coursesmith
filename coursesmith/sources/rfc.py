"""IETF RFCs as a source: `rfc>9110`.

Text comes from rfc-editor.org (plain text, the authoritative form) and metadata from its JSON (title, status,
obsoleted_by, DOI). An RFC never changes once published, so its version is its publication date. A
standards-track RFC is `standard` tier; a subject can lower that in subject.yaml.

    - name: http-rfcs
      adapter: rfc
      ids: [9110, 9111, 6455]     # crawled without listing them under `seeds:`
      depth: 1                    # also follow the RFCs these cite, one hop
"""
import json
import re

from . import licenses
from .base import MissingSource, SourceAdapter, SourceError
from .keys import SEP, make_key
from ..text import brackets
from ..text.emit import DOC_DROP_SECTIONS

TXT_URL = "https://www.rfc-editor.org/rfc/rfc{n}.txt"
JSON_URL = "https://www.rfc-editor.org/rfc/rfc{n}.json"
PAGE_URL = "https://www.rfc-editor.org/rfc/rfc{n}"
SEARCH_URL = "https://datatracker.ietf.org/api/v1/doc/document/"

FOOTER = re.compile(r"^\S.*\[Page \d+\]\s*$")
HEADER = re.compile(r"^RFC\s+\d+\s{3,}\S.*\s{3,}[A-Z][a-z]+\s+(?:19|20)\d\d\s*$")
NUM_HEAD = re.compile(r"^(\d+(?:\.\d+)*)\.?\s{2,}(\S.{0,100}?)\s*$")
# the older single-space style ("6. Guidance in the use of these Imperatives"), accepted only for a short
# capitalized line followed by a blank line, so "1. MUST   This word..." stays a paragraph
OLD_NUM_HEAD = re.compile(r"^(\d+(?:\.\d+)*)\.?\s(\S(?:(?!\s{3}).){0,70}?)\s*$")
APP_HEAD = re.compile(r"^((?:Appendix\s+)?[A-Z](?:\.\d+)*)\.?\s{2,}(\S.{0,100}?)\s*$")
PLAIN_HEAD = re.compile(r"^(Abstract|Status of This Memo|Copyright Notice|Table of Contents|Acknowledg\w+|"
                        r"Authors?'? Addresses?|Author'?s Address|Full Copyright Statement|"
                        r"Intellectual Property Statement|Index)\s*$", re.I)
LIST_ITEM = re.compile(r"^(\s*)(o|\*|-|•|\d{1,2}\.|\(\d{1,2}\)|[a-z]\))\s{1,}\S")
RFC_REF = re.compile(r"\bRFC\s?(\d{1,5})\b")
SYMBOLS = re.compile(r"[^A-Za-z0-9\s.,;:'\"?!()\-]")
RFC_DROP = DOC_DROP_SECTIONS | {"status of this memo", "copyright notice", "full copyright statement",
                                "intellectual property statement", "index", "ietf trust",
                                "authors' addresses", "author's address", "authors addresses"}


FRONT_HEAD = re.compile(r"^(Abstract|Status of This Memo|Copyright Notice|Table of Contents)\s*$", re.I)


def _heading_at(lines, i, front_only=False):
    """(number or None, title) when line i opens a section, else None. With front_only, a heading that can start
    the body of the document: a front-matter title or any numbered section (never the back matter, such as
    Acknowledgments or Index, which an old RFC may not reach until its last pages)."""
    l = lines[i]
    if not l.strip() or l.startswith(" "):
        return None
    head = None
    m = NUM_HEAD.match(l) or APP_HEAD.match(l)
    if m:
        head = (m.group(1), m.group(2))
    elif PLAIN_HEAD.match(l.strip()):
        head = (None, l.strip())
    else:
        m = OLD_NUM_HEAD.match(l)
        nxt_blank = i + 1 >= len(lines) or not lines[i + 1].strip()
        if m and nxt_blank and m.group(2)[:1].isupper():
            head = (m.group(1), m.group(2))
    if head and head[0] is not None:
        ttl = head[1]
        if ttl.endswith((".", ",", ":")) or re.search(r"\.{3,}", ttl) or len(ttl.split()) > 14:
            return None  # a sentence that starts with a number, or a table-of-contents dot leader
    if head and front_only and head[0] is None and not FRONT_HEAD.match(head[1]):
        return None
    return head


def _strip_num(title):
    """A heading's title without the `1.2.` / `A.1.` / `Appendix B.` number this module put in front of it."""
    return re.sub(r"^(?:Appendix\s+)?(?:\d+|[A-Z])(?:\.\d+)*\.\s+", "", title.strip())


def _is_code(block):
    """ASCII art, ABNF, message examples and tables: kept out of the prose."""
    body = " ".join(block)
    if not body.strip():
        return True
    cols = sum(1 for l in block if re.search(r"\S {3,}\S", l.strip()))
    if cols >= 2 and cols > len(block) / 2:
        return True  # most lines have internal column gaps: a table or diagram
    return len(SYMBOLS.findall(body)) / max(len(body), 1) > 0.12


def _paragraphs(lines):
    """Blank-line separated blocks of one section -> output lines (prose paragraphs and `- item` lines)."""
    out, block, code = [], [], 0

    def flush():
        nonlocal code
        if not block:
            return
        if _is_code(block):
            code += 1
        elif LIST_ITEM.match(block[0]):
            item = []
            indent = LIST_ITEM.match(block[0]).group(1)

            def push():
                if item:
                    out.append("- " + _join(item))
                    item.clear()
            for l in block:
                m = LIST_ITEM.match(l)
                if m and m.group(1) == indent:
                    push()
                    item.append(re.sub(r"^\s*(o|\*|-|•|\d{1,2}\.|\(\d{1,2}\)|[a-z]\))\s+", "", l))
                else:
                    item.append(l.strip())
            push()
        else:
            out.append(_join(block))
        block.clear()

    for l in lines:
        if l.strip():
            block.append(l.rstrip())
        else:
            flush()
    flush()
    return out, code


def _join(lines):
    s = ""
    for l in lines:
        l = l.strip()
        s = s + l if s.endswith("-") and not s.endswith(" -") else (s + " " + l if s else l)
    return re.sub(r"\s+", " ", s).strip()


def parse_rfc_text(raw, number, title=""):
    """Plain-text RFC -> {text, name, links, lead_links, anchors, citations, sections, code_blocks}."""
    lines = [l for l in raw.replace("\r\n", "\n").replace("\f", "\n").split("\n")
             if not FOOTER.match(l) and not HEADER.match(l)]
    start = next((i for i in range(len(lines)) if _heading_at(lines, i, front_only=True)), 0)
    head_block, lines = lines[:start], lines[start:]
    if not title:
        centered = [l.strip() for l in head_block if l.startswith("      ") and l.strip()]
        title = centered[0] if centered else f"RFC {number}"
    refs = brackets.parse_references("\n".join(lines))

    sections, cur = [], {"level": 2, "title": "", "lines": []}
    for i, l in enumerate(lines):
        head = _heading_at(lines, i)
        if head:
            num, ttl = head
            sections.append(cur)
            cur = {"level": min(2 + (num.count(".") if num else 0), 6),
                   "title": f"{num}. {ttl}" if num else ttl, "lines": []}
            continue
        cur["lines"].append(l)
    sections.append(cur)

    out, links, lead_links, code_blocks, skip, n_numbered = [f"# RFC {number}: {title}"], [], [], 0, None, 0
    seen = set()
    for s in sections:
        if s["title"]:
            if skip is not None and s["level"] <= skip:
                skip = None
            if skip is None and _strip_num(s["title"]).lower().strip(" :") in RFC_DROP:
                skip = s["level"]
                continue
            if skip is not None:
                continue
            out += ["", "#" * s["level"] + " " + s["title"]]
            if re.match(r"^\d+\.", s["title"]):
                n_numbered += 1
        elif skip is not None:
            continue
        paras, code = _paragraphs(s["lines"])
        code_blocks += code
        out += paras
        for p in paras:
            for r in RFC_REF.findall(p):  # also matches the label in "[RFC2119]"
                if int(r) != int(number) and r not in seen:
                    seen.add(r)
                    links.append(make_key("rfc", int(r)))
                    if n_numbered <= 1:
                        lead_links.append(make_key("rfc", int(r)))
    body = "\n".join(out)
    anchors = {f"RFC {r}": make_key("rfc", int(r)) for r in seen if len(r) >= 1}
    body, citations = brackets.number_citations(body, refs)
    return {"text": re.sub(r"\n{3,}", "\n\n", body).strip() + "\n", "name": f"RFC {number}: {title}",
            "title": title, "links": links, "lead_links": lead_links, "anchors": anchors, "citations": citations,
            "code_blocks": code_blocks}


class RfcAdapter(SourceAdapter):
    adapter = "rfc"
    prefix = "rfc"
    default_tier = "standard"
    default_license = {"name": "IETF Trust (BCP 78)", "url": "https://trustee.ietf.org/license-info/",
                       "class": "ietf-trust"}
    default_depth = 1

    def hosts(self):
        return ["rfc-editor.org", "datatracker.ietf.org"]

    def ids(self):
        return [int(i) for i in self.cfg.get("ids") or []]

    def seeds(self):
        return [make_key("rfc", i) for i in self.ids()]

    # -- keys ------------------------------------------------------------------------
    def owns(self, key):
        return bool(re.fullmatch(rf"rfc{re.escape(SEP)}\d{{1,5}}", key))

    @staticmethod
    def number(key):
        return int(key.split(SEP, 1)[1])

    def key_for_url(self, url, base_key=None):
        m = re.search(r"rfc-editor\.org/(?:rfc|info)/rfc(\d{1,5})|datatracker\.ietf\.org/doc/(?:html/)?rfc(\d{1,5})",
                      url, re.I)
        if m:
            return make_key("rfc", int(m.group(1) or m.group(2)))
        m = RFC_REF.fullmatch(url.strip())
        return make_key("rfc", int(m.group(1))) if m else None

    # -- fetching --------------------------------------------------------------------
    def meta(self, n):
        try:
            raw = self.http.get(JSON_URL.format(n=n))
            return json.loads(raw) if raw else {}
        except (ValueError, TypeError):
            return {}

    def fetch(self, key):
        n = self.number(key)
        raw = self.http.get(TXT_URL.format(n=n))
        if not raw:
            raise MissingSource(f"RFC {n} not found at rfc-editor.org")
        meta = self.meta(n)
        doc = parse_rfc_text(raw, n, meta.get("title") or "")
        if not doc["text"].strip() or len(doc["text"]) < 200:
            raise SourceError(f"RFC {n}: no readable text")
        pub = meta.get("pub_date") or ""
        rec = self.record(key, doc["name"], PAGE_URL.format(n=n), doc["text"], pub or f"rfc{n}", source_id=str(n))
        rec.update({"body_links": doc["links"], "lead_links": doc["lead_links"], "anchors": doc["anchors"],
                    "citations": doc["citations"],
                    "categories": [x for x in [meta.get("pub_status") or meta.get("status")] if x]})
        rec["meta"] = {"description": (meta.get("title") or doc["title"]), "tags": meta.get("keywords") or [],
                       "status": meta.get("pub_status") or meta.get("status"), "pub_date": pub,
                       "authors": meta.get("authors") or [], "obsoleted_by": meta.get("obsoleted_by") or [],
                       "obsoletes": meta.get("obsoletes") or [], "updated_by": meta.get("updated_by") or [],
                       "doi": meta.get("doi"), "errata_url": meta.get("errata_url"),
                       "code_blocks": doc["code_blocks"], "definition_hint": None}
        return rec

    # -- presentation ----------------------------------------------------------------
    def version_label(self, version):
        v = str(version or "")
        return f"published {v}" if v and not v.startswith("rfc") else "as published"

    def permalink(self, src):
        return src.get("url") or ""

    # -- discovery and checks --------------------------------------------------------
    def discover(self, query, limit=20):
        try:
            raw = self.http.get(SEARCH_URL, params={"type": "rfc", "title__icontains": query, "limit": limit,
                                                    "format": "json"})
            objs = (json.loads(raw) if raw else {}).get("objects") or []
        except (ValueError, TypeError, AttributeError):
            return []
        return [{"id": f"rfc:{o.get('rfc')}", "adapter": "rfc", "title": f"RFC {o.get('rfc')}: {o.get('title')}",
                 "url": PAGE_URL.format(n=o.get("rfc")), "key": make_key("rfc", int(o["rfc"])),
                 "snippet": (o.get("abstract") or "")[:300], "tier": "standard"}
                for o in objs if o.get("rfc")]

    def check(self):
        problems, notes = [], []
        for n in self.ids():
            m = self.meta(n)
            if not m:
                problems.append(f"RFC {n}: no metadata at rfc-editor.org (does it exist?)")
                continue
            if m.get("obsoleted_by"):
                notes.append(f"RFC {n} is obsoleted by {', '.join(m['obsoleted_by'])}: "
                             f"facts from it may be out of date; consider the newer RFC")
        return {"license": licenses.normalize(self.license), "problems": problems, "notes": notes}


ADAPTER = RfcAdapter
