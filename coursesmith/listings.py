"""Code listings: the code blocks of a source page, placed in an entry's text by the writer.

A source with `code:` (see sources/github.py) keeps each page's code blocks. They are indexed beside the sentences
(extract/sentences.py, table `listings`), each with an id (sha1 of page, language and code) and the sentence it
follows. The code is never typed by a writer: an entry's text holds a token `{{code:<id>}}` on a paragraph of its
own, and every renderer swaps in the stored code, verbatim.

Which listings an entry may place: those of the pages it cites, that follow a sentence the entry cites or sit in a
section it cites from (`available`). subject.yaml:

    code:
      per_entry: 3      # most listings in one entry (default 3)
      max_lines: 40     # longest listing a writer is offered (default 40)

`audit` holds the writers to it: the id must be one the entry may place, each at most once, on its own paragraph.
"""
import re

from . import config

CODE_RE = re.compile(r"\{\{code:([0-9a-f]{12})\}\}")
PER_ENTRY, MAX_LINES, OFFERED = 3, 40, 8


def settings(subject):
    """The subject's `code:` settings, or None when the subject has none."""
    c = (getattr(subject, "cfg", None) or {}).get("code")
    if not c:
        return None
    c = c if isinstance(c, dict) else {}
    return {"per_entry": int(c.get("per_entry") or PER_ENTRY), "max_lines": int(c.get("max_lines") or MAX_LINES)}


def strip(text):
    """The text without its code tokens (for word counts, number checks and plain-text output)."""
    return re.sub(r"\n{3,}", "\n\n", CODE_RE.sub("", text or "")).strip()


def blocks(text):
    """[("text", paragraph) | ("code", id)] in order; a token inside a paragraph splits it."""
    out = []
    for para in re.split(r"\n\s*\n", text or ""):
        pos = 0
        for m in CODE_RE.finditer(para):
            if para[pos:m.start()].strip():
                out.append(("text", para[pos:m.start()].strip()))
            out.append(("code", m.group(1)))
            pos = m.end()
        if para[pos:].strip():
            out.append(("text", para[pos:].strip()))
    return out


def used(prose, eid):
    return CODE_RE.findall((prose["entries"].get(eid) or {}).get("text") or "")


def available(subject, e, db=None):
    """[{id, lang, code, lines, title, section, after_sid, source}] the entry may place, best first."""
    cfg = settings(subject)
    if not cfg or not config.SENT_DB.exists():
        return []
    from .explain import own_sent_ids
    from .extract import sentences as SN
    own = db or SN.connect()
    try:
        sids = own_sent_ids(e)
        rows = SN.lookup(own, sorted(sids))
        pages = {r["title"] for r in rows.values()}
        sections = {(r["title"], r["section"]) for r in rows.values()}
        out = []
        for t in sorted(pages):
            for cid, n, section, after, lang, code, source in SN.page_listings(own, t):
                lines = code.count("\n") + 1
                if lines > cfg["max_lines"] or not ((after in sids) or ((t, section) in sections)):
                    continue
                out.append({"id": cid, "lang": lang, "code": code, "lines": lines, "title": t, "section": section,
                            "after_sid": after, "source": source, "n": n, "first": after in sids})
        out.sort(key=lambda x: (not x["first"], x["title"], x["n"]))
        seen, uniq = set(), []
        for x in out:
            if x["id"] not in seen:
                seen.add(x["id"])
                uniq.append(x)
        return uniq
    finally:
        if db is None:
            own.close()


def lookup(ids):
    """id -> {lang, code, source, url, name, title, ...} from the index (empty without one)."""
    if not ids or not config.SENT_DB.exists():
        return {}
    from .extract import sentences as SN
    db = SN.connect()
    try:
        return SN.listing_lookup(db, sorted(set(ids)))
    finally:
        db.close()


def audit(subject, prose, entries, order):
    """(problems, warnings) for the tokens writers placed."""
    cfg = settings(subject)
    problems, warnings = [], []
    if not cfg:
        for i in order:
            if used(prose, i):
                problems.append(f"{i}: {{{{code:..}}}} used but subject.yaml has no `code:` block")
        return problems, warnings
    from .extract import sentences as SN
    db = SN.connect() if config.SENT_DB.exists() else None
    try:
        for i in order:
            ids = used(prose, i)
            if not ids:
                continue
            text = (prose["entries"].get(i) or {}).get("text") or ""
            if len(ids) > cfg["per_entry"]:
                problems.append(f"{i}: {len(ids)} listings (code.per_entry allows {cfg['per_entry']})")
            for d in {x for x in ids if ids.count(x) > 1}:
                problems.append(f"{i}: listing {d} placed twice")
            for para in re.split(r"\n\s*\n", text):
                if CODE_RE.search(para) and CODE_RE.sub("", para).strip():
                    problems.append(f"{i}: a {{{{code:id}}}} token shares a paragraph with text; give it a paragraph "
                                    "of its own (edition.paragraphs must be true)")
                    break
            if db is not None:
                ok = {x["id"] for x in available(subject, entries[i], db)}
                for d in dict.fromkeys(ids):
                    if d not in ok:
                        problems.append(f"{i}: listing {d} is not one this entry may place (see the LISTING lines of "
                                        "its packet)")
    finally:
        if db is not None:
            db.close()
    return problems, warnings
