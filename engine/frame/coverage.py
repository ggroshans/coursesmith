"""report coverage: how much of the subject's hub lists the crawl and the entries cover.

    wikicourse report coverage <subject> [--chapter KEY]

For every article in the navbox, the index, the Vital lists and the Top/High importance set: crawled or not,
in an entry or not (as its article, or as a source). Thin chapters are flagged against their share of the
target. Run after the crawl and again after consolidation; decide gap-fill crawls from it.
"""
from collections import Counter

from ..crawl.store import Store, crawled_titles
from ..util import atomic_write, read_json, write_json


def run(subject, chapter=None, log=print):
    hubs = read_json(subject.scope_dir / "hubs.json", {}) or {}
    store = Store()
    crawled = {store.canonical(t) for t in crawled_titles(subject)}
    entries = subject.entries()
    as_article = {(e.get("article") or "").split("#")[0] for e in entries}
    as_source = {s["title"] for e in entries for s in e.get("sources") or []}
    lists = {"navbox": hubs.get("navbox") or [], "index": hubs.get("index") or [], "vital": hubs.get("vital") or [],
             "top/high": [t for t, i in (hubs.get("importance") or {}).items() if i in ("Top", "High")]}
    frame_titles = None
    if chapter:
        frame_titles = set()
        for p in (subject.frame or {}).get("parts") or []:
            for c in p.get("chapters") or []:
                if chapter in (c.get("key"), c["title"]):
                    frame_titles |= set(c.get("seeds") or []) | set(c.get("also") or [])
    rows, summary = [], {}
    for name, titles in lists.items():
        ts = [store.canonical(t) for t in titles]
        if frame_titles is not None:
            ts = [t for t in ts if t in frame_titles]
        c = Counter()
        for t in ts:
            state = "entry" if t in as_article else "source" if t in as_source else "crawled" if t in crawled else "missing"
            c[state] += 1
            if state in ("missing", "crawled"):
                rows.append((name, t, state))
        n = len(ts) or 1
        summary[name] = {"total": len(ts), "crawled": c["entry"] + c["source"] + c["crawled"],
                         "in_entries": c["entry"] + c["source"],
                         "crawled_pct": round(100 * (c["entry"] + c["source"] + c["crawled"]) / n),
                         "entry_pct": round(100 * (c["entry"] + c["source"]) / n)}
    thin = []
    by_ch = Counter(e.get("chapter") for e in entries)
    for p in (subject.frame or {}).get("parts") or []:
        for c in p.get("chapters") or []:
            if chapter and chapter not in (c.get("key"), c["title"]):
                continue
            tgt = c.get("target") or 0
            if entries and tgt and by_ch[c["title"]] < 0.6 * tgt:
                thin.append((p["title"], c["title"], by_ch[c["title"]], tgt))
    L = [f"# Coverage: {subject.title}" + (f" (chapter {chapter})" if chapter else ""), "",
         "| Hub list | Articles | Crawled | In entries |", "|---|---:|---:|---:|"]
    for name, s in summary.items():
        L.append(f"| {name} | {s['total']} | {s['crawled']} ({s['crawled_pct']}%) | {s['in_entries']} ({s['entry_pct']}%) |")
    L += ["", "## Thin chapters (under 60% of target)", ""]
    L += [f"- {p} › {c}: {n} entries of {t}" for p, c, n, t in thin] or ["None (or no entries yet)."]
    L += ["", "## Hub articles not yet crawled", ""]
    L += [f"- [{n}] {t}" for n, t, s in rows if s == "missing"] or ["None."]
    L += ["", "## Crawled but in no entry", ""]
    L += [f"- [{n}] {t}" for n, t, s in rows if s == "crawled"] or ["None."]
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "coverage.md", "\n".join(L) + "\n")
    short = {k: f"{v['crawled_pct']}% crawled, {v['entry_pct']}% in entries" for k, v in summary.items()}
    write_json(subject.reports_dir / "coverage.json", {"summary": short, "detail": summary,
                                                        "thin": thin, "chapter": chapter})
    log(f"[coverage] {short}; {len(thin)} thin chapters -> reports/coverage.md")
    return summary
