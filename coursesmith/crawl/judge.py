"""The scope judge: a pass that reads borderline pages' metadata and decides in / support / out.

    coursesmith scope judge-packets <subject> [--size N]
    coursesmith scope judge-merge <subject>

Candidates: pages the crawl rejected just under the threshold, pages three or more entry articles link to, and
hub-list pages, minus pages that are already entry articles. The calibration titles go in unlabeled, so the merge
can measure the judge against them. Packets go to work/scope/judge-packet-NN.md (guides/JUDGE_GUIDE.md); passes
write scope/judge/batch-NN.json; the merge writes scope/judge.json, which the scope scorer applies (+20 for in and
support, -20 for out) and `crawl --judged` queues.
"""
import collections
import csv
import json
import re

from ..util import read_json, write_json

BAND_LOW = 2
MIN_LINKS = 3
VERDICTS = ("in", "support", "out")


def _entry_articles(subject, store):
    out = set()
    for e in subject.entries():
        a = (e.get("article") or "").split("#")[0]
        if a:
            out.add(store.canonical(a))
    return out


def _lead(store, title, n=2, cap=240):
    if not store.has_page(title):
        return ""
    text = store.load_text(title) or ""
    if text.startswith("# "):  # the title line shares its block with the lead, so drop it first
        text = text.split("\n", 1)[1] if "\n" in text else ""
    paras = [p for p in text.split("\n\n") if p.strip() and p.lstrip()[0] not in "#-|[!>*"]
    lead = re.sub(r"\[\^?\d+\]", "", " ".join(paras[0].split())) if paras else ""
    sents = re.split(r"(?<=[.!?])\s+", lead)
    return " ".join(sents[:n])[:cap]


def candidates(subject, store, scope):
    thr = scope.threshold
    arts = _entry_articles(subject, store)
    links = collections.Counter()
    for a in arts:
        if store.has_page(a):
            for l in set(store.load_page(a).get("body_links") or []):
                links[store.canonical(l)] += 1
    cand = set()
    p = subject.scope_dir / "frontier_rejected.csv"
    if p.exists():
        with p.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                try:
                    if BAND_LOW <= float(r["score"]) < thr:
                        cand.add(store.canonical(r["title"]))
                except (TypeError, ValueError):
                    pass
    cand |= {t for t, n in links.items() if n >= MIN_LINKS}
    h = read_json(subject.scope_dir / "hubs.json", {}) or {}
    for k in ("navbox", "index", "vital", "importance", "category_pages"):
        cand |= {store.canonical(t) for t in (h.get(k) or [])}
    from .scope import read_labels
    labels, _, _ = read_labels(subject)
    cand -= arts
    cand -= set(scope.forced)
    cand |= {store.canonical(t) for t in labels}
    out = []
    for t in sorted(cand):
        m = store.meta.get(t)
        if not m or m.get("missing") or m.get("disambig"):
            continue
        out.append(t)
    return out, links


def packets(subject, size=600, log=print):
    from .scope import Scope
    from .store import Store
    store, sc = Store(), Scope(subject)
    titles, links = candidates(subject, store, sc)
    done = merged(subject)
    titles = [t for t in titles if t not in done]
    chapters = []
    for p in (subject.frame or {}).get("parts") or []:
        for c in p.get("chapters") or []:
            chapters.append(f"- {c.get('key')}: {c.get('title')} ({p.get('title')})")
    head = [f"# Scope judge packet: {subject.cfg.get('title')}", "",
            (subject.cfg.get("description") or "").strip(), "", "## Chapters", *chapters, "", "## Pages", ""]
    out_dir = subject.dir / "work" / "scope"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("judge-packet-*.md"):
        old.unlink()
    n = 0
    for i in range(0, len(titles), size):
        n += 1
        lines = list(head)
        for t in titles[i:i + size]:
            m = store.meta.get(t) or {}
            cats = "; ".join((m.get("categories") or [])[:6])
            lead = _lead(store, t)
            row = f"{t} | {m.get('description') or '-'} | cats: {cats or '-'} | linked from {links.get(t, 0)} entries"
            if lead:
                row += f" | lead: {lead}"
            lines.append(row)
        (out_dir / f"judge-packet-{n:02d}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"[judge] {len(titles)} pages in {n} packets of up to {size} ({len(done)} already judged)")
    return n


def merged(subject):
    return read_json(subject.scope_dir / "judge.json", {}) or {}


def merge(subject, log=print):
    out = merged(subject)
    bad = 0
    for p in sorted((subject.scope_dir / "judge").glob("batch-*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            log(f"[judge] {p.name}: {e}")
            bad += 1
            continue
        for t, v in d.items():
            if isinstance(v, dict) and v.get("v") in VERDICTS:
                out[t] = {k: v.get(k) for k in ("v", "ch", "why") if v.get(k)}
            else:
                bad += 1
    write_json(subject.scope_dir / "judge.json", out)
    c = collections.Counter(v["v"] for v in out.values())
    new = collections.Counter(v["ch"] for v in out.values() if str(v.get("ch") or "").startswith("new:"))
    log(f"[judge] {len(out)} verdicts: in {c['in']}, support {c['support']}, out {c['out']}; {bad} malformed")
    for ch, k in new.most_common():
        log(f"[judge]   {ch}: {k}")
    from .scope import read_labels
    labels, _, _ = read_labels(subject)
    seen = [(t, y) for t, y in labels.items() if t in out]
    if seen:
        tp = sum(1 for t, y in seen if y and out[t]["v"] != "out")
        fp = sum(1 for t, y in seen if not y and out[t]["v"] != "out")
        fn = sum(1 for t, y in seen if y and out[t]["v"] == "out")
        p = tp / (tp + fp) if tp + fp else 0
        r = tp / (tp + fn) if tp + fn else 0
        f1 = 2 * p * r / (p + r) if p + r else 0
        log(f"[judge] calibration ({len(seen)} labeled titles): F1 {f1:.3f}, precision {p:.3f}, recall {r:.3f}")
    return out
