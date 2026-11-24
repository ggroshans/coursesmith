"""explain packet / explain resolve: find what each entry assumes, then fetch the Wikipedia pages that explain it.

    coursesmith explain packet <subject>     work/explain/packet-NNN.md   (the scout pass reads these)
    coursesmith explain resolve <subject>    explain/background.json, reports/explain.md

The scout pass (guides/EXPLAIN_GUIDE.md) answers each packet with work/explain/assumes.NNN.json:

    {"assumes": {"<entry id>": ["Dependency injection", "HTTP"]}}      # short Wikipedia search phrases

`resolve` searches Wikipedia for each phrase (once: answers are kept in cache/explain_search.json), skips
disambiguation pages and pages the course already has as an entry, fetches the rest into the shared cache,
indexes their sentences, and writes each entry's background: the lead sentences of every page, with sent_ids,
for the writer to cite. A wrong hit is fixed by hand in work/explain/pages.json ({"phrase": "Page title"}) and
`resolve` run again.
"""
import re

from .. import config
from ..util import atomic_write, now_iso, read_json, write_json
from . import settings

CHUNK = 60            # entries per scout packet
LEAD_WORDS = 200      # of each page's lead given to the writer (about 8 sentences)
FACT_CHARS = 380      # of each fact shown to the scout
FACTS_SHOWN = 5


def _chunks(subject):
    order = (subject.order() or {}).get("order") or []
    if not order:
        raise SystemExit("no order.json; run `coursesmith order` first")
    entries = subject.entries_by_id()
    return [[entries[i] for i in order[k:k + CHUNK] if i in entries] for k in range(0, len(order), CHUNK)]


def packet(subject, log=print):
    cfg = settings(subject)
    if not cfg:
        raise SystemExit(f"{subject.slug} has no `explain:` block in subject.yaml")
    d = subject.explain_work
    d.mkdir(parents=True, exist_ok=True)
    n = 0
    for k, group in enumerate(_chunks(subject), 1):
        L = [f"# Scout packet {k:03d}: {subject.title}", "",
             f"Reader: {cfg['audience'] or 'a smart, curious newcomer to this field'}",
             *([f"Reader especially wants: {cfg['focus']}"] if cfg["focus"] else []), "",
             f"For each entry, name up to {cfg['background']} pieces of background it assumes the reader already "
             "has (guides/EXPLAIN_GUIDE.md). Return {\"assumes\": {\"<entry id>\": [\"phrase\", ...]}} in "
             f"work/explain/assumes.{k:03d}.json. Leave an entry out if it assumes nothing.", ""]
        for e in group:
            L.append(f"### {e['id']} | {e['title']} | {e.get('part')} › {e.get('chapter')} | {e.get('level')}")
            d0 = (e.get("definition") or {}).get("text")
            if d0:
                L.append(f"- Definition: {d0[:FACT_CHARS]}")
            L += [f"- Fact: {f['text'][:FACT_CHARS]}" for f in (e.get("facts") or [])[:FACTS_SHOWN]]
            L.append("")
        atomic_write(d / f"packet-{k:03d}.md", "\n".join(L) + "\n")
        n += 1
    log(f"[explain] {n} scout packets in {d.relative_to(subject.dir)}/ ({CHUNK} entries each)")
    return n


def _assumes(subject):
    out = {}
    for f in sorted(subject.explain_work.glob("assumes*.json")):
        doc = read_json(f, {}) or {}
        for eid, phrases in (doc.get("assumes") or {}).items():
            out[eid] = [" ".join(str(p).split()) for p in phrases or [] if isinstance(p, str) and p.strip()]
    return out


def _article(e):
    return (e.get("article") or "").split("#")[0].strip().casefold()


def _is_disambiguation(rec):
    cats = list(rec.get("categories") or []) + list(rec.get("hidden_categories") or [])
    return any("disambiguation" in c.casefold() for c in cats)


def search_title(client, phrase):
    """The top Wikipedia article for a search phrase, or ''."""
    d = client.get({"action": "query", "list": "search", "srsearch": phrase, "srlimit": 1, "srnamespace": 0})
    hits = d.get("query", {}).get("search", [])
    return hits[0]["title"] if hits else ""


def lead(db, key, limit=LEAD_WORDS):
    """[(sent_id, text)] from the top of a page, about `limit` words, ending at a sentence."""
    from ..extract import sentences as SN
    rows = [r for r in SN.page_sentences(db, key) if not r[4]]         # no table rows
    rows = [r for r in rows if r[5]] or rows[:8]                         # the lead, else the first sentences
    out, count = [], 0
    for sid, _section, _idx, text, _row, _lead, _links, _dates in rows:
        if out and count + len(text.split()) > limit:
            break
        out.append({"sent_id": sid, "text": text})
        count += len(text.split())
    return out


def resolve(subject, client=None, store=None, log=print):
    cfg = settings(subject)
    if not cfg:
        raise SystemExit(f"{subject.slug} has no `explain:` block in subject.yaml")
    assumes = _assumes(subject)
    if not assumes:
        raise SystemExit("no work/explain/assumes*.json; run `explain packet` and the scout pass first")
    from ..crawl.api import MissingPage, WikiClient
    from ..crawl.fetch import fetch_page
    from ..crawl.store import Store
    from ..extract import sentences as SN
    client, store = client or WikiClient(), store or Store()
    entries = subject.entries_by_id()
    article_of = {}
    for e in entries.values():
        if _article(e):
            article_of.setdefault(_article(e), e["id"])
    overrides = {k.casefold(): v for k, v in (read_json(subject.explain_work / "pages.json", {}) or {}).items()}
    cache_path = config.CACHE / "explain_search.json"
    searched = read_json(cache_path, {}) or {}

    phrases = list(dict.fromkeys(p for ps in assumes.values() for p in ps[:cfg["background"]]))
    title_of, new = {}, 0
    for p in phrases:
        key = p.casefold()
        if key in overrides:
            title_of[p] = overrides[key]
            continue
        if key not in searched:
            searched[key] = search_title(client, p)
            new += 1
            if new % 25 == 0:
                write_json(cache_path, searched)
        title_of[p] = searched[key]
    write_json(cache_path, searched)

    db = SN.connect()
    pages, bad = {}, {}
    for title in dict.fromkeys(t for t in title_of.values() if t):
        try:
            rec, text, _status = fetch_page(client, store, title)
        except MissingPage:
            bad[title] = "missing"
            continue
        if _is_disambiguation(rec):
            bad[title] = "a disambiguation page"
            continue
        key = rec["title"]
        have = db.execute("SELECT revid FROM pages WHERE title = ?", (key,)).fetchone()
        if not have or have[0] != rec.get("revid"):
            SN.index_page(db, store, rec, text)
        pages[title] = {"key": key, "name": rec["title"], "url": rec["url"], "revid": rec.get("revid"),
                        "sentences": lead(db, key)}
    store.flush_caches()
    db.commit()
    db.close()

    out = {"built": now_iso(), "entries": {}, "covered": {}, "unresolved": {}}
    for eid, ps in assumes.items():
        if eid not in entries:
            continue
        mine, seen = [], {_article(entries[eid])}
        for p in ps[:cfg["background"]]:
            page = pages.get(title_of.get(p) or "")
            if not page:
                out["unresolved"].setdefault(eid, []).append(
                    {"phrase": p, "reason": bad.get(title_of.get(p) or "") or "no Wikipedia match"})
                continue
            low = page["key"].casefold()
            if low in seen:
                continue
            seen.add(low)
            if low in article_of and article_of[low] != eid:
                out["covered"].setdefault(eid, []).append({"phrase": p, "entry": article_of[low]})
                continue
            if page["sentences"]:
                mine.append({"phrase": p, **page})
        if mine:
            out["entries"][eid] = mine
    subject.explain_dir.mkdir(parents=True, exist_ok=True)
    write_json(subject.explain_dir / "background.json", out)
    _report(subject, out, entries, title_of)
    n_pages = len({p["key"] for ps in out["entries"].values() for p in ps})
    log(f"[explain] {len(out['entries'])} entries have background ({n_pages} pages); "
        f"{sum(len(v) for v in out['covered'].values())} topics are already course entries; "
        f"{sum(len(v) for v in out['unresolved'].values())} phrases did not resolve -> reports/explain.md")
    return out


def _report(subject, doc, entries, title_of):
    """reports/explain.md: which phrase became which page (to spot a wrong hit), and what did not resolve."""
    by_phrase = {}
    for eid, ps in doc["entries"].items():
        for p in ps:
            by_phrase.setdefault((p["phrase"], p["key"]), []).append(eid)
    L = [f"# Explain background: {subject.title}", "",
         f"{len(doc['entries'])} entries, {len(by_phrase)} phrase-to-page pairs. A wrong match goes in "
         "work/explain/pages.json as {\"phrase\": \"Page title\"}; then run `explain resolve` again.", "",
         "## Phrase → Wikipedia page (most used first)", ""]
    for (phrase, key), ids in sorted(by_phrase.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        L.append(f"- {phrase} → **{key}** ({len(ids)} entries)")
    if any(doc["unresolved"].values()):
        L += ["", "## Did not resolve", ""]
        seen = {}
        for eid, items in doc["unresolved"].items():
            for it in items:
                seen.setdefault((it["phrase"], it["reason"]), []).append(eid)
        for (phrase, why), ids in sorted(seen.items(), key=lambda kv: (-len(kv[1]), kv[0])):
            L.append(f"- {phrase}: {why} ({len(ids)} entries)")
    if any(doc["covered"].values()):
        L += ["", "## Already a course entry (the writer links to it with {{ref:id}})", ""]
        seen = {}
        for eid, items in doc["covered"].items():
            for it in items:
                seen.setdefault((it["phrase"], it["entry"]), []).append(eid)
        for (phrase, tgt), ids in sorted(seen.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:200]:
            L.append(f"- {phrase} → {tgt} ({len(ids)} entries)")
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "explain.md", "\n".join(L) + "\n")
