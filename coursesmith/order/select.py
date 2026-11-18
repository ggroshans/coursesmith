"""select: curriculum test, score, trim to target.

    coursesmith select <subject> [--chapter KEY] [--trim]

An entry needs at least one curriculum test: its own article or its own section on a hub page; listed in a
navbox, the index or Vital Articles; rated Top or High importance; prerequisite of two or more selected
entries; mentioned on two or more in-scope pages. Entries marked `exclude: true` by consolidation never pass.
The course keeps every entry that passes: a subject runs as long as its material does, and the curriculum
test (plus the consolidation guide's exclusions) is what keeps out the very niche.

score = graph importance of its article + weight (Landmark 6, Major 3, Minor 0) + tests passed
        + log2(1 + source pages) + 1.5 per entry that builds on it

--trim cuts each frame chapter to its target (share x targets.entries) by score, nudged toward a 10 / 35 / 55 %
Landmark / Major / Minor mix, for a subject that must fit a fixed length. "Never pad": a chapter short of its
target is reported, not filled. --chapter limits selection to one chapter (the pilot).
"""
import math
from collections import Counter, defaultdict

from ..graph.build import load as load_graph
from ..util import atomic_write, read_jsonl, write_jsonl

WEIGHT_PTS = {"Landmark": 6, "Major": 3, "Minor": 0}


def run(subject, chapter=None, trim=False, log=print):
    graph = load_graph(subject)
    nodes = graph["nodes"]
    entries = subject.entries()
    if not entries:
        raise SystemExit("no final entries; run `coursesmith finalize` first")
    builds_on = Counter(p for e in entries for p in e.get("prerequisites") or [])
    targets = {}
    for p in (subject.frame or {}).get("parts") or []:
        for c in p.get("chapters") or []:
            targets[c["title"]] = c.get("target") or round((c.get("share") or 0) * (subject.targets.get("entries") or 0))
    by_chapter = defaultdict(list)
    for e in entries:
        art = (e.get("article") or "").split("#")[0]
        n = nodes.get(art) or {}
        tests = list(e.get("curriculum") or [])
        if builds_on[e["id"]] >= 2 and "prerequisite of 2+" not in tests:
            tests.append("prerequisite of 2+")
        e["curriculum"] = tests
        parts = {"importance": n.get("importance", 0.0), "weight": WEIGHT_PTS.get(e.get("weight"), 0),
                 "tests": len(tests), "pages": round(math.log2(1 + len(e.get("sources") or [])), 2),
                 "builds_on_it": 1.5 * builds_on[e["id"]]}
        e["score"] = round(sum(parts.values()), 2)
        e["score_parts"] = parts
        by_chapter[e.get("chapter")].append(e)

    report = ["# Selection", "", "| Chapter | Drafted | Passing | Target | Selected | L/M/m | Short by |",
              "|---|---:|---:|---:|---:|---|---:|"]
    for ch, es in by_chapter.items():
        in_play = chapter is None or _matches(chapter, ch, subject)
        passing = [e for e in es if e["curriculum"] and not e.get("exclude")]
        for e in es:
            if e not in passing:
                e["selected"] = False
                e["selection_note"] = "excluded" if e.get("exclude") else "no curriculum test"
        if not in_play:
            for e in es:
                e["selected"] = False
            continue
        tgt = targets.get(ch) or len(passing)
        keep = passing if not trim or len(passing) <= tgt else _trim(passing, tgt)
        for e in passing:
            e["selected"] = e in keep
            if e["selected"]:
                e.pop("selection_note", None)
            else:
                e["selection_note"] = "below cut-off"
        w = Counter(e["weight"] for e in keep)
        short = max(0, tgt - len(keep))
        report.append(f"| {ch} | {len(es)} | {len(passing)} | {tgt} | {len(keep)} | {w['Landmark']}/{w['Major']}/"
                      f"{w['Minor']} | {short or ''} |")
    _save(subject, entries)
    sel = [e for e in entries if e.get("selected")]
    w = Counter(e["weight"] for e in sel)
    tot = max(1, len(sel))
    report += ["", f"Selected **{len(sel)}** of {len(entries)} entries: Landmark {w['Landmark'] / tot:.0%}, Major "
               f"{w['Major'] / tot:.0%}, Minor {w['Minor'] / tot:.0%} (aim 10 / 35 / 55).",
               "", "Every passing entry is kept" + (" (trimmed to chapter targets)." if trim else ".")
               + " Short chapters are not padded: widen the frame or gap-fill instead."]
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "selection.md", "\n".join(report) + "\n")
    log(f"[select] {len(sel)} selected of {len(entries)} (L/M/m {w['Landmark']}/{w['Major']}/{w['Minor']}); "
        "reports/selection.md")
    from ..frame import gaps
    n_names, n_thin = gaps.summary(subject)
    if n_names or n_thin:
        log(f"[select] warning: {n_names} unresolved prerequisite names and {n_thin} thin entries are still open; "
            f"run `coursesmith report gaps {subject.slug}` and gap-fill, or accept them under `gaps:` in subject.yaml")
    return sel


def _matches(key, chapter_title, subject):
    for p in (subject.frame or {}).get("parts") or []:
        for c in p.get("chapters") or []:
            if c["title"] == chapter_title and key in (c.get("key"), c["title"]):
                return True
    return False


def _trim(passing, target):
    """Best by score, nudged toward the 10/35/55 weight mix."""
    quota = {"Landmark": max(1, round(target * 0.10)), "Major": round(target * 0.35)}
    quota["Minor"] = target - quota["Landmark"] - quota["Major"]
    ranked = sorted(passing, key=lambda e: -e["score"])
    keep, used = [], Counter()
    for e in ranked:
        if used[e["weight"]] < quota.get(e["weight"], 0):
            keep.append(e)
            used[e["weight"]] += 1
    for e in ranked:
        if len(keep) >= target:
            break
        if e not in keep:
            keep.append(e)
    return keep


def _save(subject, entries):
    by_id = {e["id"]: e for e in entries}
    for p in subject.entry_files():
        write_jsonl(p, [by_id.get(r["id"], r) for r in read_jsonl(p)])
