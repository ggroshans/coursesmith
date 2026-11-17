"""write skeleton: writer packets, one per part, in the locked order (guides/WRITING_GUIDE.md).

    wikicourse write skeleton <subject>             work/write/packet-<part>.md
    wikicourse write questions <subject>            work/write/questions-packet.md (after `units build`)

A packet lists, in course order: an OPENER slot for the part and each chapter (with the facts it may draw
on), every entry (id, working title, kind, level, weight, word range, definition, facts, builds-on ids,
contested notes, conflicts, external facts), and a REVIEW slot at each chapter's end. Writers return JSON
batches (work/write/fill.*.json); see engine/write/render.py for the format.
"""
from ..outline import Outline
from ..util import atomic_write, slug


def word_range(e):
    if e.get("weight") == "Minor":
        return "40-90 words"
    if e.get("weight") == "Landmark" or e.get("kind") in ("Classification", "Process", "Debate"):
        return "100-250 words"
    return "60-150 words"


def _entry_block(e, by_id):
    L = [f"### {e['id']} | {e['title']} | {e.get('kind')} | {e.get('level')} | {e.get('weight')} | "
         f"{word_range(e)}"]
    d = e.get("definition") or {}
    if d.get("text"):
        L.append(f"- Definition: {d['text']}")
    pre = [p for p in e.get("prerequisites") or [] if p in by_id]
    if pre:
        L.append("- Builds on (refer with {{ref:id}} when the facts support the link): "
                 + "; ".join(f"{p} ({by_id[p]['title']})" for p in pre))
    L += [f"- Fact: {f['text']}" for f in e.get("facts") or []]
    if e.get("contested"):
        L.append(f"- CONTESTED: {e.get('contested_note') or 'the sources call this debated'} (say so plainly)")
    for c in e.get("conflicts") or []:
        L.append(f"- OTHER VALUE IN THE SOURCES: {c.get('text') or c.get('note') or c}")
    for v in e.get("verification") or []:
        if v.get("reviewed_verdict") == "genuine conflict":
            L.append(f"- MUST MENTION (checked against {v.get('doi') or v.get('source')}): {v.get('note')}")
    for x in e.get("external") or []:
        L.append(f"- EXTERNAL (+ {x.get('source')}): {x.get('text')}")
    for ev in e.get("events") or []:
        if ev.get("date_text"):
            L.append(f"- DATE IN THE FACTS: {ev['date_text']}")
    return L


def build(subject, log=print):
    order = (subject.order() or {}).get("order") or []
    if not order:
        raise SystemExit("no order.json; run `wikicourse order` first")
    entries = subject.entries_by_id()
    by_id = {i: entries[i] for i in order if i in entries}
    outline = Outline.from_subject(subject)
    packets, cur_part = {}, None
    seen = set()
    last_in_leaf = {}
    for i in order:
        last_in_leaf[outline.leaf(entries[i])] = i
    for i in order:
        e = entries[i]
        path = outline.entry_path(e)
        part = path[0] if path else "misc"
        L = packets.setdefault(part, [f"# Writer packet: {subject.title} › {outline.title(part)}", "",
                                      "The facts here are the only content you may use (guides/WRITING_GUIDE.md). "
                                      "Write titles, texts, openers, reviews and glossary terms as JSON batches "
                                      "in work/write/fill.<part>.NN.json.", ""])
        for nid in path:
            if nid in seen:
                continue
            seen.add(nid)
            members = [j for j in order if nid in outline.entry_path(entries[j])]
            L += [f"## OPENER {nid} ({outline.title(nid)}): 3-5 sentences that set the scene, built only from these "
                  "facts", ""]
            for j in members[:12]:
                d = (entries[j].get("definition") or {}).get("text")
                f0 = (entries[j].get("facts") or [{}])[0].get("text")
                if d or f0:
                    L.append(f"- [{j}] {d or f0}")
            L.append("")
        L += _entry_block(e, by_id) + [""]
        leaf = path[-1] if path else None
        if leaf and last_in_leaf.get(leaf) == i and len(path) > 1:
            mem = [j for j in order if outline.leaf(entries[j]) == leaf]
            L += [f"## REVIEW {leaf} ({outline.title(leaf)}): 3-5 sentences tying the chapter together, using only the "
                  f"facts of its entries ({', '.join(mem)})", ""]
    subject.write_dir.mkdir(parents=True, exist_ok=True)
    for part, L in packets.items():
        atomic_write(subject.write_dir / f"packet-{slug(part, 30)}.md", "\n".join(L) + "\n")
    log(f"[write] {len(packets)} packets for {len(by_id)} entries in work/write/")
    return list(packets)


def questions(subject, log=print):
    units = (subject.units() or {}).get("units") or []
    if not units:
        raise SystemExit("no units.json; run `wikicourse units build` first")
    entries = subject.entries_by_id()
    L = ["# Question packet", "", "One question per unit, answered by the unit's own facts (guides/WRITING_GUIDE.md, "
         "Questions). Return {\"questions\": {\"<first entry id>\": {\"q\": ..., \"a\": ..., \"sent_ids\": [...]}}}.", ""]
    for u in units:
        first = u["entries"][0]
        L.append(f"## QUESTION {first} (Unit {u['n']})")
        for i in u["entries"]:
            for f in entries[i].get("facts") or []:
                L.append(f"- [{i}] {f['text']} (sent_ids: {', '.join(f.get('sent_ids') or [])})")
        L.append("")
    atomic_write(subject.write_dir / "questions-packet.md", "\n".join(L) + "\n")
    log(f"[write] question packet for {len(units)} units -> work/write/questions-packet.md")
