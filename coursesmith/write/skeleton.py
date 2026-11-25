"""write skeleton: writer packets, one per part, in the locked order (guides/WRITING_GUIDE.md).

    coursesmith write skeleton <subject>             work/write/packet-<part>.md
    coursesmith write questions <subject>            work/write/questions-packet.md (after `units build`)

A packet lists, in course order: an OPENER slot for the part and each chapter (with the facts it may draw
on), every entry (id, working title, kind, level, weight, word range, definition, facts, builds-on ids,
contested notes, conflicts, external facts), and a REVIEW slot at each chapter's end. Writers return JSON
batches (work/write/fill.*.json); see coursesmith/write/render.py for the format.
"""
from ..outline import Outline
from ..util import atomic_write, slug


DEFAULT_RANGES = {"Minor": (40, 90), "long": (100, 250), "default": (60, 150),
                  "Worked example": (250, 600), "Case study": (150, 400)}
LONG_KINDS = ("Classification", "Process", "Debate")


def word_bounds(e, subject=None):
    """(lo, hi) words for an entry. `targets.word_ranges` in subject.yaml overrides: a kind name wins over a
    weight (Minor) or a class (`long` for Landmark and the long kinds, `default` for the rest)."""
    cfg = ((getattr(subject, "targets", None) or {}).get("word_ranges") or {}) if subject is not None else {}

    def pick(key):
        return tuple(int(x) for x in cfg[key]) if cfg.get(key) else DEFAULT_RANGES[key]
    kind, weight = e.get("kind"), e.get("weight")
    if kind in cfg:
        return tuple(int(x) for x in cfg[kind])
    if kind in ("Worked example", "Case study"):
        return DEFAULT_RANGES[kind]
    if weight == "Minor":
        return pick("Minor")
    if weight == "Landmark" or kind in LONG_KINDS:
        return pick("long")
    return pick("default")


def word_range(e, subject=None):
    lo, hi = word_bounds(e, subject)
    return f"{lo}-{hi} words"


def _explain_lines(e, cfg, bg):
    """What the writer may use to explain an entry: its background pages' sentences, topics the course covers
    itself, and the caps. Every sentence carries the sent_id an explanation cites."""
    L = []
    for p in (bg.get("entries") or {}).get(e["id"]) or []:
        L += [f"- BACKGROUND ({p['key']}) [{s['sent_id']}] {s['text']}" for s in p.get("sentences") or []]
    for c in (bg.get("covered") or {}).get(e["id"]) or []:
        L.append(f"- COVERED BY THE COURSE: {c['phrase']} is entry {c['entry']}; point to it with "
                 f"{{{{ref:{c['entry']}}}}} instead of explaining it")
    L.append(f"- EXPLAIN: up to {cfg['terms']} terms and {cfg['blurbs']} blurb(s), citing sent_ids from the Fact "
             "and BACKGROUND lines of this entry only (guides/WRITING_GUIDE.md, Explain mode)")
    return L


PREVIEW_LINES = 6


def _listing_lines(e, subject, db):
    """The code the entry may place with {{code:id}}: id, language, length, the sentence it follows and a preview."""
    from .. import listings as LS
    from ..extract import sentences as SN
    cfg = LS.settings(subject)
    avail = LS.available(subject, e, db)[:LS.OFFERED]
    if not avail:
        return []
    L = [f"- LISTINGS: place up to {cfg['per_entry']} of these with {{{{code:ID}}}} on a paragraph of its own, right "
         "after the sentence it illustrates. The code is inserted for you, verbatim; never retype it."]
    for x in avail:
        after = SN.lookup(db, [x["after_sid"]]).get(x["after_sid"], {}).get("sentence") if x["after_sid"] else ""
        L.append(f"  - LISTING {x['id']} | {x['lang']} | {x['lines']} lines | follows: {(after or '(page start)')[:110]}")
        L += [f"      {ln}" for ln in x["code"].split("\n")[:PREVIEW_LINES]]
        if x["lines"] > PREVIEW_LINES:
            L.append("      ...")
    return L


def _entry_block(e, by_id, subject=None, explain=None, code_db=None):
    L = [f"### {e['id']} | {e['title']} | {e.get('kind')} | {e.get('level')} | {e.get('weight')} | "
         f"{word_range(e, subject)}"]
    d = e.get("definition") or {}
    if d.get("text"):
        ids = f" [{', '.join(d.get('sent_ids') or [])}]" if explain else ""
        L.append(f"- Definition{ids}: {d['text']}")
    pre = [p for p in e.get("prerequisites") or [] if p in by_id]
    if pre:
        L.append("- Builds on (refer with {{ref:id}} when the facts support the link): "
                 + "; ".join(f"{p} ({by_id[p]['title']})" for p in pre))
    if explain:  # the writer cites sentences, so each fact shows the ids it rests on
        L += [f"- Fact [{', '.join(f.get('sent_ids') or [])}]: {f['text']}" for f in e.get("facts") or []]
    else:
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
    if explain:
        L += _explain_lines(e, *explain)
    if code_db is not None:
        L += _listing_lines(e, subject, code_db)
    return L


def build(subject, log=print):
    order = (subject.order() or {}).get("order") or []
    if not order:
        raise SystemExit("no order.json; run `coursesmith order` first")
    entries = subject.entries_by_id()
    by_id = {i: entries[i] for i in order if i in entries}
    outline = Outline.from_subject(subject)
    from .. import explain as X
    cfg = X.settings(subject)
    bg = X.load_background(subject) if cfg else {}
    if cfg and not bg:
        log("[write] warning: explain mode is on but there is no explain/background.json; explanations can only "
            "draw on each entry's own facts (run `explain packet`, the scout pass and `explain resolve`)")
    explain = (cfg, bg) if cfg else None
    from .. import listings as LS
    from ..extract import sentences as SN
    code_db = SN.connect() if LS.settings(subject) else None
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
                                      "in work/write/fill.<part>.NN.json.", ""]
                           + ([f"EXPLAIN MODE. Reader: {cfg['audience'] or 'a smart, curious newcomer to this field'}."
                               + (f" The reader especially wants: {cfg['focus']}." if cfg["focus"] else ""),
                               "Where an entry leans on something the reader may not know, add a term or a blurb "
                               "to the batch's `explain` key (guides/WRITING_GUIDE.md, Explain mode).", ""]
                              if cfg else []))
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
        L += _entry_block(e, by_id, subject, explain, code_db) + [""]
        leaf = path[-1] if path else None
        if leaf and last_in_leaf.get(leaf) == i and len(path) > 1:
            mem = [j for j in order if outline.leaf(entries[j]) == leaf]
            L += [f"## REVIEW {leaf} ({outline.title(leaf)}): 3-5 sentences tying the chapter together, using only the "
                  f"facts of its entries ({', '.join(mem)})", ""]
    if code_db is not None:
        code_db.close()
    subject.write_dir.mkdir(parents=True, exist_ok=True)
    for part, L in packets.items():
        atomic_write(subject.write_dir / f"packet-{slug(part, 30)}.md", "\n".join(L) + "\n")
    log(f"[write] {len(packets)} packets for {len(by_id)} entries in work/write/")
    return list(packets)


def questions(subject, log=print):
    units = (subject.units() or {}).get("units") or []
    if not units:
        raise SystemExit("no units.json; run `coursesmith units build` first")
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
