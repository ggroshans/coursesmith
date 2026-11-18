"""verify: tiers B-D of the deep verification (tier A is the context crawl: `crawl --context`).

    coursesmith verify <subject> [--no-network]

Tier B, cited works: the DOIs behind each entry's cited sentences are resolved through OpenAlex (Crossref as
fallback); title and abstract only. Each work is compared with the entry's facts:
    numbers with units ("0.002 mm", "45%", "pH 5.5") and dates; classification names for Classification
    entries. Verdicts: supports / refines (inside a stated range) / differs (needs review) /
    no comparable claim / no abstract / not found.
Tier C, authorities: the registry in subject.yaml (`verification.authorities`). An authority with a fetcher
    (`fetcher: text_reference` and `urls`) is fetched once, cached, and compared the same way; an entry whose
    key claim an authority supports becomes source_tier `primary`. Authorities without a fetcher are listed
    as pending in the report: add fetchers one at a time, where entries make checkable claims.
Tier D, added context: verify/external.json holds facts from authorities or peer-reviewed abstracts that an
    entry needs and Wikipedia lacks ({id: [{source, url, retrieved, text}]}), written by the verification
    pass (guides/VERIFICATION_GUIDE.md). They are copied into the entry's `external` and shown as "+ source".

Every `differs` on an entry with no supporting source goes to verify/worklist.md. Hand verdicts live in
verify/reviews.json ({id: {doi-or-authority: {"reviewed_verdict", "note"}}}) and are re-applied on every run.
Scope: every selected entry plus every flagged one (contested, conflict, citation_needed).
"""
import hashlib
import json
import re
from collections import Counter
from html import unescape

from .. import config
from ..extract import dates as D
from ..extract import sentences as SN
from ..util import atomic_write, read_json, read_jsonl, write_jsonl
from . import extsrc

UNITS = r"(mm|µm|μm|nm|cm|m|km|ha|%|percent|g/cm3|g/cm³|mg/kg|g/kg|kg|t|°C|°F|cmol\(?\+?\)?/kg|cmolc/kg|meq/100 ?g|" \
        r"ppm|years?|kPa|MPa|bar)"
QTY = re.compile(rf"(?<![\w.])(\d+(?:[.,]\d+)?)(?:\s*(?:–|-|to)\s*(\d+(?:[.,]\d+)?))?\s*{UNITS}(?![\w/])")
PH = re.compile(r"\bpH\s*(?:of\s*)?(\d+(?:\.\d+)?)(?:\s*(?:–|-|to)\s*(\d+(?:\.\d+)?))?")
SUPPORTS = ("supports", "refines")


def _num(s):
    return float(s.replace(",", "."))


def quantities(text):
    """[(low, high, unit)] for numbers with units, and pH values."""
    out = []
    for m in QTY.finditer(text or ""):
        a = _num(m.group(1))
        b = _num(m.group(2)) if m.group(2) else a
        unit = m.group(3).replace("percent", "%").replace("μ", "µ").rstrip("s") if m.group(3) else ""
        out.append((min(a, b), max(a, b), unit))
    for m in PH.finditer(text or ""):
        a = float(m.group(1))
        b = float(m.group(2)) if m.group(2) else a
        out.append((min(a, b), max(a, b), "pH"))
    return out


def key_terms(e):
    terms = {e["title"].lower()}
    if e.get("article"):
        terms.add(e["article"].split("#")[0].lower())
    out = set()
    for t in terms:
        t = re.sub(r"\s*\(.*?\)", "", t).strip()
        out.add(t)
        out.add(t[:-1] if t.endswith("s") else t + "s")
    return {t for t in out if len(t) > 3}


def _sentences(text):
    return re.split(r"(?<=[.!?])\s+", text or "")


def compare(e, text, kind="paper"):
    """Compare an entry's facts with a text (abstract or authority page)."""
    if not text:
        return {"verdict": "no abstract", "matched": None}
    low = text.lower()
    terms = key_terms(e)
    mentions = [s for s in _sentences(text) if any(t in s.lower() for t in terms)]
    if e.get("kind") == "Classification" and kind == "authority":
        name = re.sub(r"\s*\(.*?\)", "", e["title"]).strip()
        m = re.search(rf"(?<![\w-]){re.escape(name.lower())}(?![\w-])", low)
        if m:
            return {"verdict": "supports", "matched": f"lists {name}",
                    "evidence": text[max(0, m.start() - 120):m.end() + 180]}
    fact_q = [q for f in e.get("facts") or [] for q in quantities(f.get("text"))]
    if not mentions:
        return {"verdict": "no comparable claim", "matched": None}
    text_q = [(q, s) for s in mentions for q in quantities(s)]
    if fact_q and text_q:
        for lo, hi, u in fact_q:
            same = [(a, b, s) for (a, b, uu), s in text_q if uu == u]
            for a, b, s in same:
                if abs(a - lo) <= 0.02 * max(abs(lo), 1e-9) and abs(b - hi) <= 0.02 * max(abs(hi), 1e-9):
                    return {"verdict": "supports", "matched": f"{a:g}–{b:g} {u}" if a != b else f"{a:g} {u}",
                            "evidence": s[:300]}
            for a, b, s in same:
                if lo <= a <= hi and lo <= b <= hi and (a, b) != (lo, hi):
                    return {"verdict": "refines", "matched": f"{a:g}–{b:g} {u}", "evidence": s[:300]}
        units_f = {u for _, _, u in fact_q}
        hits = [((a, b, u), s) for (a, b, u), s in text_q if u in units_f]
        if hits:
            return {"verdict": "differs", "matched": "; ".join(f"{a:g} {u}" for (a, b, u), _ in hits)[:200],
                    "evidence": hits[0][1][:300]}
    # dates (history branch)
    fd = [d for f in e.get("facts") or [] for d in D.find_dates(f.get("text") or "")]
    if fd:
        td = [d for s in mentions for d in D.find_dates(s)]
        for x in fd:
            for y in td:
                if x.get("date_ma") is not None and y.get("date_ma") is not None and \
                        abs(x["date_ma"] - y["date_ma"]) <= 0.02 * max(abs(x["date_ma"]), 1e-9):
                    return {"verdict": "supports", "matched": y.get("date_text")}
    return {"verdict": "no comparable claim", "matched": None}


def _flagged(e):
    return bool(set(e.get("flags") or []) & {"contested", "conflict", "citation_needed"})


def _authority_text(a, network=True):
    """Fetch an authority's pages once (cached) and return their plain text. With network=False only what is
    already cached is read."""
    from bs4 import BeautifulSoup
    texts = []
    for url in a.get("urls") or ([a["url"]] if a.get("url") else []):
        if url.lower().endswith(".pdf"):
            # a long manual takes minutes to parse; keep its text next to the cached download
            cached = config.AUTHORITY_TEXT_DIR / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".txt")
            if cached.exists():
                texts.append(cached.read_text(encoding="utf-8"))
                continue
            data = extsrc.HTTP.get(url, binary=True, cache_only=not network)
            if data:
                t = _pdf_text(data)
                cached.parent.mkdir(parents=True, exist_ok=True)
                atomic_write(cached, t)
                texts.append(t)
            continue
        raw = extsrc.HTTP.get(url, cache_only=not network)
        if not raw:
            continue
        soup = BeautifulSoup(raw, "html.parser")
        for el in soup.select("script, style, nav, header, footer"):
            el.decompose()
        texts.append(re.sub(r"\s+", " ", unescape(soup.get_text(" "))))
    return " ".join(texts)


def _pdf_text(data):
    import logging
    logging.getLogger("pypdf").setLevel(logging.ERROR)  # font-encoding chatter, harmless for text extraction
    try:
        from pypdf import PdfReader
    except ImportError:
        raise SystemExit("an authority is a PDF: `pip install pypdf` to read it")
    import io
    reader = PdfReader(io.BytesIO(data))
    return re.sub(r"\s+", " ", " ".join((pg.extract_text() or "") for pg in reader.pages))


def run(subject, network=True, log=print):
    entries = subject.entries()
    scope = [e for e in entries if e.get("selected") or _flagged(e)]
    db = SN.connect()
    reviews = read_json(subject.verify_dir / "reviews.json", {}) or {}
    external = read_json(subject.verify_dir / "external.json", {}) or {}
    # tier B
    dois_of = {}
    for e in scope:
        sids = [s for f in e.get("facts") or [] for s in f.get("sent_ids") or []]
        sids += (e.get("definition") or {}).get("sent_ids") or []
        found = SN.lookup(db, sids)
        dois_of[e["id"]] = sorted({d for r in found.values() for d in r["dois"]})
    all_dois = sorted({d for v in dois_of.values() for d in v})
    works = extsrc.lookup_dois(all_dois, network=network) if all_dois else {}
    # tier C
    auths = [a for a in (subject.cfg.get("verification") or {}).get("authorities") or []]
    live = [a for a in auths if a.get("fetcher") == "text_reference" and (a.get("urls") or a.get("url"))]
    pending = [a["name"] for a in auths if a not in live]
    auth_text = {a["name"]: _authority_text(a, network) for a in live}

    verdicts = Counter()
    worklist = []
    for e in scope:
        v_list = []
        for d in dois_of.get(e["id"], []):
            w = works.get(d) or {}
            if w.get("not_found") or not w:
                v = {"verdict": "not found", "matched": None}
            else:
                v = compare(e, w.get("abstract"), "paper")
                if v["verdict"] in ("no abstract", "no comparable claim") and w.get("title"):
                    t = compare(e, w["title"], "paper")
                    if t["verdict"] in SUPPORTS:
                        v = dict(t, field="title")
            item = {"doi": d, "title": w.get("title"), "year": w.get("year"), "venue": w.get("venue"),
                    "source": w.get("source"), **v}
            v_list.append(item)
        for a in live:
            applies = a.get("kinds")
            if applies and e.get("kind") not in applies:
                continue
            v = compare(e, auth_text.get(a["name"]), "authority")
            if v["verdict"] == "no abstract":
                continue
            v_list.append({"source": a["name"], "url": (a.get("urls") or [a.get("url")])[0], "kind": "authority", **v})
        for item in v_list:
            key = item.get("doi") or item.get("source")
            r = (reviews.get(e["id"]) or {}).get(key)
            if r:
                item["reviewed_verdict"], item["note"] = r.get("reviewed_verdict"), r.get("note")
            verdicts[item.get("reviewed_verdict") or item["verdict"]] += 1
        e["verification"] = [x for x in v_list if x["verdict"] in SUPPORTS + ("differs",) or x.get("reviewed_verdict")]
        e["external"] = external.get(e["id"]) or []
        supported = any((x.get("reviewed_verdict") or x["verdict"]) in SUPPORTS for x in v_list)
        e["source_tier"] = "primary" if supported else "wikipedia"
        if not supported and any(x["verdict"] == "differs" and not x.get("reviewed_verdict") for x in v_list):
            worklist.append(e)
    # a run takes minutes to hours: write back only verify's own fields onto the records as they are now, so
    # finalize, select or order runs that happened meanwhile are not undone
    by_id = {e["id"]: e for e in scope}
    for p in subject.entry_files():
        rows = read_jsonl(p)
        for r in rows:
            v = by_id.get(r["id"])
            if v:
                for k in ("verification", "external", "source_tier"):
                    r[k] = v.get(k)
        write_jsonl(p, rows)
    _report(subject, scope, verdicts, worklist, pending, len(all_dois), live)
    tiers = Counter(e["source_tier"] for e in scope)
    log(f"[verify] {len(scope)} entries, {len(all_dois)} DOIs, {len(live)} authorities live "
        f"({len(pending)} pending); verdicts {dict(verdicts)}; tiers {dict(tiers)}; {len(worklist)} to review")
    return worklist


def _report(subject, scope, verdicts, worklist, pending, n_dois, live):
    L = ["# Verification", "", f"Entries checked: {len(scope)} (selected plus flagged). DOIs looked up: {n_dois}.",
         f"Authorities with a fetcher: {', '.join(a['name'] for a in live) or 'none yet'}.",
         f"Authorities pending a fetcher: {', '.join(pending) or 'none'}.", "", "## Verdicts", ""]
    L += [f"- {k}: {v}" for k, v in verdicts.most_common()]
    tiers = Counter(e["source_tier"] for e in scope)
    L += ["", "## Source tiers", ""] + [f"- {k}: {v}" for k, v in tiers.most_common()]
    L += ["", "## Automatic supports (spot-check: a matching number near the term is evidence, not proof)", ""]
    for e in scope:
        for x in e["verification"]:
            if x["verdict"] in SUPPORTS and not x.get("reviewed_verdict"):
                L.append(f"- {e['id']} **{e['title']}** vs {x.get('doi') or x.get('source')}: {x.get('matched')} — "
                         f"“{(x.get('evidence') or '').strip()[:200]}”")
    L += ["", "## To review (differs, nothing supports)", ""]
    for e in worklist:
        for x in e["verification"]:
            if x["verdict"] == "differs":
                L.append(f"- {e['id']} **{e['title']}** vs {x.get('doi') or x.get('source')}: {x.get('matched')}")
    if not worklist:
        L.append("None.")
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "verification.md", "\n".join(L) + "\n")
    w = ["# Verification worklist", "", "Read each, then record the outcome in verify/reviews.json as "
         '{"<entry id>": {"<doi or authority>": {"reviewed_verdict": "supports|different object|older estimate|'
         'genuine conflict", "note": "..."}}}. A genuine conflict is mentioned in the prose in one plain sentence.', ""]
    for e in worklist:
        w.append(f"## {e['id']} {e['title']}")
        w += [f"- fact: {f['text']}" for f in e.get("facts") or []]
        for x in e["verification"]:
            if x["verdict"] == "differs":
                w.append(f"- {x.get('doi') or x.get('source')} ({x.get('year') or ''}): {x.get('title') or ''} "
                         f"— gives {x.get('matched')}")
        w.append("")
    subject.verify_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.verify_dir / "worklist.md", "\n".join(w) + "\n")


def load_reviews(subject):
    return json.loads((subject.verify_dir / "reviews.json").read_text(encoding="utf-8")) \
        if (subject.verify_dir / "reviews.json").exists() else {}
