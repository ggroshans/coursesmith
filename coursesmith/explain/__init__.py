"""Explain mode: an optional layer that teaches what an entry assumes the reader already knows.

Off unless subject.yaml has an `explain:` block:

    explain:
      audience: "a developer who knows another language but is new to .NET"   # who is reading
      focus: ""        # optional: what the reader most wants out of the course
      background: 3    # background pages a scout may name per entry
      blurbs: 1        # boxed mini-lessons per entry, at most
      terms: 3         # one-line definitions of assumed words per entry, at most

It follows the one rule of the engine: every explanation is built from cited sentences. A scout pass names the
background an entry assumes (`explain packet`), `explain resolve` finds those pages on Wikipedia, fetches them
into the shared cache and indexes their sentences, and the writing pass then writes, for an entry, up to `terms`
short definitions and `blurbs` short lessons, each citing sentences from the entry's own facts or from its
background pages. `write check` and `publish check` hold them to the same rules as the entry text: cited
sentences must exist and belong to the entry, and no number may be absent from the sentences cited.

Files: explain/background.json (the pages each entry assumes, with their lead sentences and sent_ids),
work/explain/ (scout packets and answers), reports/explain.md. In output/prose.json the writer's items live
under `explain`: {entry id: {"terms": [{"term", "text", "sent_ids"}], "blurbs": [{"heading", "text", "sent_ids"}]}}.
"""
import re

from .. import config
from ..util import read_json

# length guides, in words (warnings, not failures)
BLURB_WORDS = (50, 160)
TERM_WORDS = 55


def settings(subject):
    """The subject's explain settings (ints clamped to >= 0), or None when explain mode is off."""
    ex = getattr(subject, "explain", None)
    if not ex:
        return None
    out = dict(ex)
    for k in ("background", "blurbs", "terms"):
        try:
            out[k] = max(0, int(out.get(k) or 0))
        except (TypeError, ValueError):
            out[k] = 0
    out["audience"] = " ".join(str(out.get("audience") or "").split())
    out["focus"] = " ".join(str(out.get("focus") or "").split())
    return out


def load_background(subject):
    """explain/background.json: {entries: {id: [page]}, covered: {id: [...]}, unresolved: {id: [...]}}."""
    return read_json(subject.explain_dir / "background.json", {}) or {}


def own_sent_ids(e):
    """Every sentence an entry itself cites (its definition, facts and dated events)."""
    ids = list((e.get("definition") or {}).get("sent_ids") or [])
    for k in ("facts", "events"):
        for f in e.get(k) or []:
            ids += f.get("sent_ids") or []
    return set(ids)


def background_ids(bg, eid):
    return {s["sent_id"] for p in (bg.get("entries") or {}).get(eid) or [] for s in p.get("sentences") or []}


def items(prose, eid):
    """(terms, blurbs) the writer gave an entry; either list may be empty."""
    d = (prose.get("explain") or {}).get(eid) or {}
    return list(d.get("terms") or []), list(d.get("blurbs") or [])


def text_of(prose, eid):
    """All the prose of an entry's explanations (definitions and blurb bodies, not their headings), for the
    term-before-entry scans."""
    terms, blurbs = items(prose, eid)
    return " ".join([t.get("text") or "" for t in terms] + [b.get("text") or "" for b in blurbs])


def words(prose, eid):
    terms, blurbs = items(prose, eid)
    return sum(len(((x.get("term") or x.get("heading") or "") + " " + (x.get("text") or "")).split())
               for x in terms + blurbs)


def _sentence_rows(sids):
    """sent_id -> row from the sentence index (empty when there is no index)."""
    if not sids or not config.SENT_DB.exists():
        return {}
    from ..extract import sentences as SN
    db = SN.connect()
    try:
        return SN.lookup(db, sorted(sids))
    finally:
        db.close()


def audit(subject, prose, entries, order, log=None):
    """The rules a script can test on the writers' explanations. Returns (problems, warnings).

    Problems: more items than the subject allows; an item with no sent_ids; a cited sentence that is not in the
    entry's own facts or its background pages, or not in the sentence index; a number that is in none of the
    sentences it cites (or the entry's own facts); a banned phrase or an exclamation mark; a {{ref:id}} to an
    unknown entry; a term that does not appear in the entry's text or blurbs.
    Warnings: a blurb or definition outside its length guide, a sentence over 28 words."""
    from ..publish.check import allowed_numbers, nums
    from ..write.check import BANNED, sentences
    from ..write.render import REF_RE
    cfg = settings(subject)
    problems, warnings = [], []
    if not cfg:
        return problems, warnings
    bg = load_background(subject)
    ex = prose.get("explain") or {}
    unknown = [i for i in ex if i not in entries]
    for i in unknown:
        problems.append(f"{i}: explain names no entry")
    cited = {sid for i in order if i in ex for item in items(prose, i)[0] + items(prose, i)[1]
             for sid in item.get("sent_ids") or []}
    rows = _sentence_rows(cited)
    for i in order:
        if i not in ex:
            continue
        e = entries[i]
        terms, blurbs = items(prose, i)
        if len(terms) > cfg["terms"]:
            problems.append(f"{i}: {len(terms)} terms (explain.terms allows {cfg['terms']})")
        if len(blurbs) > cfg["blurbs"]:
            problems.append(f"{i}: {len(blurbs)} blurbs (explain.blurbs allows {cfg['blurbs']})")
        allowed_ids = own_sent_ids(e) | background_ids(bg, i)
        own_numbers = allowed_numbers(e)
        body = REF_RE.sub("", (prose["entries"].get(i) or {}).get("text") or "")
        shown = (body + " " + text_of(prose, i) + " " + " ".join(b.get("heading") or "" for b in blurbs)).lower()
        for kind, group in (("term", terms), ("blurb", blurbs)):
            for k, item in enumerate(group, 1):
                label = item.get("term") or item.get("heading") or f"{kind} {k}"
                where = f"{i}: {kind} '{label}'"
                text = item.get("text") or ""
                if not text.strip() or not (item.get("term") if kind == "term" else item.get("heading")):
                    problems.append(f"{where}: needs a {'term' if kind == 'term' else 'heading'} and a text")
                    continue
                sids = item.get("sent_ids") or []
                if not sids:
                    problems.append(f"{where}: no sent_ids (an explanation cites the sentences it rests on)")
                bad = [s for s in sids if s not in allowed_ids]
                if bad:
                    problems.append(f"{where}: cites sentences that are not in the entry's facts or its background "
                                    f"pages: {bad[:3]}")
                gone = [s for s in sids if s in allowed_ids and s not in rows]
                if gone and config.SENT_DB.exists():
                    problems.append(f"{where}: cites sentences missing from the sentence index: {gone[:3]}")
                for r in REF_RE.findall(text):
                    if r not in entries:
                        problems.append(f"{where}: {{{{ref:{r}}}}} names no entry")
                plain = REF_RE.sub("", text)
                low = plain.lower()
                for b in BANNED:
                    if b in low:
                        problems.append(f"{where}: banned phrase {b!r}")
                if "!" in plain:
                    problems.append(f"{where}: exclamation mark")
                ok_numbers = set(own_numbers)
                for s in sids:
                    ok_numbers |= nums((rows.get(s) or {}).get("sentence"))
                extra = sorted(x for x in nums(plain) if x not in ok_numbers and not (x <= 12 and x == int(x)))
                if extra:
                    problems.append(f"{where}: numbers not in the sentences it cites: {extra[:6]}")
                if kind == "term":
                    bare = re.sub(r"^(the|a|an)\s+", "", label.casefold())
                    if not re.search(r"(?<!\w)" + re.escape(bare), shown):
                        problems.append(f"{where}: the term is not used in the entry's text")
                    n = len(plain.split())
                    if n > TERM_WORDS:
                        warnings.append(f"{where}: {n} words (a definition is one or two sentences)")
                else:
                    n = len(plain.split())
                    if not BLURB_WORDS[0] * 0.8 <= n <= BLURB_WORDS[1] * 1.2:
                        warnings.append(f"{where}: {n} words (blurbs run {BLURB_WORDS[0]}-{BLURB_WORDS[1]})")
                for s in sentences(plain):
                    if len(s.split()) > 28:
                        warnings.append(f"{where}: long sentence ({len(s.split())} words): {s[:60]}...")
    return problems, warnings


def source_entries(subject, prose, entries):
    """Pseudo-entries ({id, sources}) crediting the background pages the explanations cite, so the license list,
    the EPUB's sources page and the distribution gate see them. Only sentences outside an entry's own sources."""
    ex = prose.get("explain") or {}
    if not ex:
        return []
    cited = {}
    for i, d in ex.items():
        own = own_sent_ids(entries[i]) if i in entries else set()
        for item in (d.get("terms") or []) + (d.get("blurbs") or []):
            for s in item.get("sent_ids") or []:
                if s not in own:
                    cited.setdefault(i, []).append(s)
    rows = _sentence_rows({s for ids in cited.values() for s in ids})
    out = []
    for i, ids in cited.items():
        by_page = {}
        for s in dict.fromkeys(ids):
            r = rows.get(s)
            if r:
                by_page.setdefault(r["title"], []).append((s, r))
        srcs = []
        for key, group in by_page.items():
            r = group[0][1]
            src = {"title": r["name"], "key": key, "url": r["url"], "revid": r["revid"], "source": r["source"],
                   "version": r["version"], "sent_ids": [s for s, _ in group]}
            if r.get("license"):
                src["license"] = r["license"]
            srcs.append(src)
        if srcs:
            out.append({"id": i, "sources": srcs})
    return out
