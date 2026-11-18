"""order: foundational to advanced (pedagogical) or by time (chronological).

    coursesmith order packet <subject>    work/order/packet.md for the ordering pass (guides/ORDERING_GUIDE.md)
    coursesmith order <subject>           order.json (draft) + output/curriculum.md
    coursesmith order lock <subject>      freeze the order (after hand edits to curriculum.md)

Prerequisites come from three signals:
  1. the ordering pass (work/order/prereqs*.json): 3-5 prerequisites per entry with a reason. Authoritative;
  2. the consolidation pass's `prerequisites`;
  3. for entries the ordering pass has not covered: lead links that RefD also supports (both signals agree).

Pedagogical order: parts in frame order, chapters in frame order, then a topological sort of each chapter's
entries by prerequisites, ties broken by importance (descending) and difficulty (ascending). A prerequisite
in a later chapter or part would break "prerequisites land in an earlier unit", so that edge moves to
`related` and is listed in reports/order.md for the curriculum review; cycles are broken by importance.
The automatic order is a draft: reorder entries by moving their lines in output/curriculum.md, then lock.
"""
import heapq
import json
import re
from collections import defaultdict

from ..graph.build import load as load_graph
from ..outline import Outline
from ..util import atomic_write, now_iso, read_json, read_jsonl, write_json, write_jsonl

ID_RE = re.compile(r"<!-- ([a-z0-9]+(?:-[a-z0-9]+)*-\d{3}) -->")


def _ordering_pass(subject):
    out = {}
    for p in sorted((subject.work_dir / "order").glob("prereqs*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        for eid, items in (d.get("entries") or d).items():
            out[eid] = [(i["id"] if isinstance(i, dict) else i) for i in items]
    return out


def prerequisites(subject, entries, graph):
    """id -> (prerequisite ids, source of each)."""
    nodes, refd = graph["nodes"], graph["refd"]
    art_to_id = {}
    for e in entries:
        if e.get("article") and "#" not in e["article"]:  # a section entry never stands for its whole page
            art_to_id.setdefault(e["article"], e["id"])
    llm = _ordering_pass(subject)
    ids = {e["id"] for e in entries}
    out = {}
    for e in entries:
        pre, why = [], {}
        for p in llm.get(e["id"], []):
            if p in ids and p != e["id"]:
                pre.append(p)
                why[p] = "ordering pass"
        # what consolidation said, not what an earlier `order build` wrote back
        for p in e.get("prerequisites_draft", e.get("prerequisites")) or []:
            if p in ids and p != e["id"] and p not in why:
                pre.append(p)
                why[p] = "consolidation"
        if e["id"] not in llm:
            art = (e.get("article") or "").split("#")[0]
            for l in (nodes.get(art) or {}).get("lead_links") or []:
                p = art_to_id.get(l)
                if p and p != e["id"] and p not in why and l in (refd.get(art) or {}):
                    pre.append(p)
                    why[p] = f"lead link + RefD {refd[art][l]}"
        out[e["id"]] = (pre, why)
    return out


WEIGHT_BONUS = {"Landmark": 4.0, "Major": 2.0, "Minor": 0.0}
QUESTION_KINDS = ("Worked example", "Case study")


def _sort_key(e, nodes):
    """Ties: a worked answer after every other ready entry of its chapter, then importance (a section entry counts
    half its page's), weight, then difficulty ascending. The first component is 0 for every other kind, so a
    course with no question chapters orders exactly as before."""
    art = e.get("article") or ""
    n = nodes.get(art.split("#")[0]) or {}
    imp = (n.get("importance") or 0.0) * (0.5 if "#" in art else 1.0) + WEIGHT_BONUS.get(e.get("weight"), 0.0)
    return (1 if e.get("kind") in QUESTION_KINDS else 0, -imp, n.get("difficulty") or 0.5, e["title"])


def build(subject, force=False, log=print):
    cur = subject.order()
    if cur.get("locked") and not force:
        raise SystemExit("order.json is locked; pass --force to rebuild it (ids stay as they are)")
    entries = [e for e in subject.entries() if e.get("selected")]
    if not entries:
        raise SystemExit("no selected entries; run `coursesmith select` first")
    graph = load_graph(subject)
    nodes = graph["nodes"]
    by_id = {e["id"]: e for e in entries}
    dropped, cycles = [], []
    if subject.chronological:
        order = [e["id"] for e in sorted(entries, key=lambda e: (-(e.get("date_ma") or 0), e["title"]))]
        pre = {e["id"]: ([], {}) for e in entries}
    else:
        pre = prerequisites(subject, entries, graph)
        outline = Outline.from_subject(subject)
        rank = {nid: k for k, nid in enumerate(outline.order)}
        pos = {}
        for e in entries:
            path = outline.entry_path(e)
            pos[e["id"]] = tuple(rank.get(p, 999) for p in path) + (999,) * (2 - len(path))
        # drop edges pointing to a later chapter or part
        for eid, (ps, why) in pre.items():
            keep = []
            for p in ps:
                if pos[p] > pos[eid]:
                    dropped.append((eid, p, why[p]))
                else:
                    keep.append(p)
            pre[eid] = (keep, why)
        order = []
        groups = defaultdict(list)
        for e in entries:
            groups[pos[e["id"]]].append(e["id"])
        placed = set()
        for g in sorted(groups):
            mem = set(groups[g])
            indeg = {i: sum(1 for p in pre[i][0] if p in mem) for i in mem}
            kids = defaultdict(list)
            for i in mem:
                for p in pre[i][0]:
                    if p in mem:
                        kids[p].append(i)
            heap = [(_sort_key(by_id[i], nodes), i) for i in mem if indeg[i] == 0]
            heapq.heapify(heap)
            done = []
            while len(done) < len(mem):
                if not heap:
                    # cycle: release the most important entry still waiting
                    left = sorted((i for i in mem if i not in done and i not in [h[1] for h in heap]),
                                  key=lambda i: _sort_key(by_id[i], nodes))
                    i = left[0]
                    blockers = [p for p in pre[i][0] if p in mem and p not in done]
                    cycles.append((i, blockers))
                    pre[i] = ([p for p in pre[i][0] if p not in blockers], pre[i][1])
                    for p in blockers:
                        dropped.append((i, p, "cycle"))
                    indeg[i] = 0
                    heapq.heappush(heap, (_sort_key(by_id[i], nodes), i))
                k, i = heapq.heappop(heap)
                if i in placed:
                    continue
                placed.add(i)
                done.append(i)
                for c in kids[i]:
                    if i in pre[c][0]:
                        indeg[c] -= 1
                        if indeg[c] == 0:
                            heapq.heappush(heap, (_sort_key(by_id[c], nodes), c))
            order += done
    # write prerequisites (dropped edges become related)
    drop_map = defaultdict(set)
    for eid, p, _ in dropped:
        drop_map[eid].add(p)
    for e in entries:
        ps, why = pre[e["id"]]
        e.setdefault("prerequisites_draft", e.get("prerequisites") or [])
        e["prerequisites"] = ps
        e["prerequisite_sources"] = {p: why.get(p) for p in ps}
        if drop_map[e["id"]]:
            e["related"] = list(dict.fromkeys((e.get("related") or []) + sorted(drop_map[e["id"]])))
    _save(subject, by_id)
    write_json(subject.order_path, {"strategy": subject.ordering, "locked": False, "built": now_iso(),
                                    "order": order})
    curriculum(subject, order, by_id)
    _report(subject, dropped, cycles, by_id)
    log(f"[order] {len(order)} entries ({subject.ordering}); {len(dropped)} prerequisite edges moved to related, "
        f"{len(cycles)} cycles broken; output/curriculum.md, reports/order.md")
    return order


def curriculum(subject, order, by_id):
    outline = Outline.from_subject(subject)
    L = [f"# {subject.title}: curriculum", "",
         "_Reorder by moving entry lines (keep each `<!-- id -->`), then run `coursesmith order lock`. "
         "Prerequisites must stay above the entries that build on them._", ""]
    seen = set()
    num = {i: k for k, i in enumerate(order, start=1)}
    for i in order:
        e = by_id[i]
        for nid in outline.entry_path(e):
            if nid not in seen:
                seen.add(nid)
                lvl = outline.nodes.get(nid, {}).get("level", 1)
                L += ["", f"{'#' * min(6, lvl + 1)} {outline.title(nid)}", ""]
        pre = ", ".join(f"{by_id[p]['title']} ({num.get(p, '?')})" for p in e.get("prerequisites") or [] if p in by_id)
        L.append(f"{num[i]}. **{e['title']}** — {e.get('level')} · {e.get('kind')} · {e.get('weight')}"
                 + (f" · builds on: {pre}" if pre else "") + f" <!-- {i} -->")
    subject.output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.output_dir / "curriculum.md", "\n".join(L) + "\n")


def lock(subject, log=print):
    cur = subject.order()
    order = cur.get("order") or []
    if not order:
        raise SystemExit("no order.json; run `coursesmith order` first")
    path = subject.output_dir / "curriculum.md"
    if path.exists():
        edited = ID_RE.findall(path.read_text(encoding="utf-8"))
        if edited and edited != order:
            if sorted(edited) != sorted(order):
                missing = sorted(set(order) - set(edited))[:5]
                extra = sorted(set(edited) - set(order))[:5]
                raise SystemExit(f"curriculum.md and order.json hold different entries (missing {missing}, "
                                 f"extra {extra}); fix the file or re-run `order`")
            log(f"[order] taking the hand-edited order from output/curriculum.md")
            order = edited
    entries = subject.entries_by_id()
    pos = {i: k for k, i in enumerate(order)}
    late = [(i, p) for i in order for p in entries[i].get("prerequisites") or [] if p in pos and pos[p] > pos[i]]
    if late:
        raise SystemExit("prerequisites after the entries that build on them: "
                         + "; ".join(f"{entries[i]['title']} needs {entries[p]['title']}" for i, p in late[:10]))
    write_json(subject.order_path, {**cur, "order": order, "locked": True, "locked_at": now_iso()})
    curriculum(subject, order, entries)
    log(f"[order] locked {len(order)} entries; ids are now frozen")


def packet(subject, log=print):
    """The ordering pass's input: every selected entry with its definition and the automatic suggestions."""
    entries = [e for e in subject.entries() if e.get("selected")]
    graph = load_graph(subject)
    sug = prerequisites(subject, entries, graph)
    by_id = {e["id"]: e for e in entries}
    nodes, refd = graph["nodes"], graph["refd"]
    art_to_id = {e["article"]: e["id"] for e in entries if e.get("article") and "#" not in e["article"]}
    L = ["# Ordering packet", "", f"{len(entries)} entries. Follow guides/ORDERING_GUIDE.md. Entry list first, then "
         "one block per entry.", "", "## Entry list", ""]
    L += [f"- {e['id']} | {e['title']} | {e.get('part')} › {e.get('chapter')} | {e.get('level')}" for e in entries]
    L += ["", "## Entries", ""]
    for e in entries:
        art = (e.get("article") or "").split("#")[0]
        lead = [art_to_id[l] for l in (nodes.get(art) or {}).get("lead_links") or [] if l in art_to_id]
        rd = [art_to_id[b] for b in (refd.get(art) or {}) if b in art_to_id]
        L += [f"### {e['id']} | {e['title']} | {e.get('kind')} | {e.get('level')}",
              f"- Definition: {(e.get('definition') or {}).get('text') or (e.get('facts') or [{}])[0].get('text', '')}",
              f"- Consolidation said: {', '.join(e.get('prerequisites_draft', e.get('prerequisites')) or []) or '-'}",
              f"- Lead links: {', '.join(x for x in lead if x != e['id']) or '-'}",
              f"- RefD: {', '.join(x for x in rd if x != e['id']) or '-'}",
              f"- Current choice: {', '.join(sug[e['id']][0]) or '-'}", ""]
    out = subject.work_dir / "order" / "packet.md"
    atomic_write(out, "\n".join(L) + "\n")
    log(f"[order] packet for {len(entries)} entries -> {out.relative_to(subject.dir)}")


def _report(subject, dropped, cycles, by_id):
    L = ["# Order report", "", "## Prerequisite edges moved to `related`", "",
         "Each points to a later chapter or part (or closed a cycle). Move an entry, reorder chapters in frame.yaml, "
         "or accept the edge as a forward reference.", ""]
    L += [f"- {by_id[a]['title']} ({a}) needed {by_id[b]['title']} ({b}) — {why}" for a, b, why in dropped] or ["None."]
    L += ["", "## Cycles broken", ""]
    L += [f"- released {by_id[i]['title']} ahead of {', '.join(by_id[b]['title'] for b in bl)}" for i, bl in cycles] \
        or ["None."]
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "order.md", "\n".join(L) + "\n")


def _save(subject, by_id):
    for p in subject.entry_files():
        write_jsonl(p, [by_id.get(r["id"], r) for r in read_jsonl(p)])


def load(subject):
    return read_json(subject.order_path, {}) or {}
