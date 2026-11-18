"""Split a subject's locked order into units of 4-5 entries (targets.per_unit).

A course too small for the unit size (3, 7 or 11 entries) gets the fewest units that fit; see size_bounds.

    coursesmith units build <subject> [--units N]

A course runs as many units as its entries need: 1,650 entries make about 370 units, 4,000 make about 900.
N comes from subject.yaml (targets.units) or defaults to about 4.5 entries per unit, clamped to what the unit
size allows. The split is chapter-aware: a dynamic program over the order picks unit boundaries that

  - never open a unit with a chapter's last entry (a lone straggler from the previous unit's chapter),
  - prefer ending a unit where a chapter ends,
  - avoid mixing chapters inside a unit, and avoid prerequisites landing in the same unit as their entry.

Writes units.json (per unit: entries, chapter openers and reviews to show, terms defined, the question, and
the "Last time" / "Next" lines), glossary.json (term -> defining entry and unit), and each entry's `unit`
and `position`.
"""
import math
import re

from ..outline import Outline
from ..util import now_iso, write_json
from ..write.render import load as load_prose

OPEN_WITH_LAST = 100.0   # a unit opening with a chapter's final entry
SAME_UNIT_PREREQ = 2.0   # an entry and its prerequisite in one unit
EXTRA_CHAPTER = 1.0      # each additional chapter mixed into a unit
END_AT_CHAPTER = -3.0    # a unit ending exactly where a chapter ends
MAX_TERMS = 6


QUESTION_TITLE = re.compile(r"^(how|what|why|when|which|design|build|explain|compare)\b|\?$", re.I)


def is_question_entry(e, question_course=False):
    """A worked answer or case study is titled for a question or a system, not for a term it defines, so it is
    never a glossary term. In a course of questions, an entry titled like one is exempt too."""
    if e.get("kind") in ("Worked example", "Case study"):
        return True
    return bool(question_course and QUESTION_TITLE.search(e.get("title") or ""))


class UnitError(RuntimeError):
    pass


def size_bounds(n_entries, lo_size=4, hi_size=5):
    """Unit sizes a course of n entries can use: per_unit when it divides, else the smallest size it forces.

    A small or awkward count (3, 7, 11 entries with per_unit 4-5) gets the fewest units of at most hi_size
    and lets the shortest one be as short as the remainder makes it: 11 -> sizes 3-5, 3 -> one unit of 3.
    """
    if n_entries < 1:
        raise UnitError("no entries to split into units")
    if math.ceil(n_entries / hi_size) <= n_entries // lo_size:
        return lo_size, hi_size
    return n_entries // math.ceil(n_entries / hi_size), hi_size


def choose_n(n_entries, lo_size=4, hi_size=5, want=None):
    lo_size, hi_size = size_bounds(n_entries, lo_size, hi_size)
    lo = math.ceil(n_entries / hi_size)
    hi = n_entries // lo_size
    n = want or round(n_entries / ((lo_size + hi_size) / 2))
    return max(lo, min(hi, n))


def split(order, leaf_of, prereqs, n_units, sizes=(4, 5)):
    """Return a list of (start, end) index pairs, exactly n_units long."""
    E = len(order)
    pos = {eid: i for i, eid in enumerate(order)}
    leaves = [leaf_of[e] for e in order]
    # chapter_last[i]: entry i is the last of its chapter and the chapter started before it
    chapter_last = [(i + 1 == E or leaves[i + 1] != leaves[i]) and i > 0 and leaves[i - 1] == leaves[i]
                    for i in range(E)]
    chapter_end = [i + 1 == E or leaves[i + 1] != leaves[i] for i in range(E)]

    def cost(a, b):
        c = 0.0
        if chapter_last[a]:
            c += OPEN_WITH_LAST
        if chapter_end[b - 1]:
            c += END_AT_CHAPTER
        c += EXTRA_CHAPTER * (len(set(leaves[a:b])) - 1)
        for i in range(a, b):
            for p in prereqs.get(order[i], ()):
                if a <= pos.get(p, -1) < b:
                    c += SAME_UNIT_PREREQ
        return c

    lo_s, hi_s = min(sizes), max(sizes)
    INF = float("inf")
    # best[k][i]: min cost of covering entries [0, i) with k units
    best = [dict() for _ in range(n_units + 1)]
    back = [dict() for _ in range(n_units + 1)]
    best[0][0] = 0.0
    for k in range(1, n_units + 1):
        rem = n_units - k
        for i_prev, c_prev in best[k - 1].items():
            for s in range(lo_s, hi_s + 1):
                i = i_prev + s
                if i > E or not (lo_s * rem <= E - i <= hi_s * rem):
                    continue
                c = c_prev + cost(i_prev, i)
                if c < best[k].get(i, INF):
                    best[k][i] = c
                    back[k][i] = i_prev
    if E not in best[n_units]:
        raise UnitError(f"no split of {E} entries into {n_units} units of {lo_s}-{hi_s}")
    spans, i = [], E
    for k in range(n_units, 0, -1):
        j = back[k][i]
        spans.append((j, i))
        i = j
    return list(reversed(spans))


def _per_unit(subject):
    sizes = subject.targets.get("per_unit") or (4, 5)
    return min(sizes), max(sizes)


def _join(titles):
    titles = [t for t in titles if t]
    if len(titles) <= 1:
        return "".join(titles)
    return "; ".join(titles[:-1]) + "; and " + titles[-1]


def build(subject, n_units=None, log=print):
    order_doc = subject.order()
    order = order_doc.get("order") or []
    if not order:
        raise UnitError("no order.json; run `coursesmith order` (and `order lock`) first")
    if not order_doc.get("locked"):
        log("[units] warning: order.json is not locked; run `coursesmith order lock` once the order is final")
    entries = subject.entries_by_id()
    missing = [i for i in order if i not in entries]
    if missing:
        raise UnitError(f"order.json names {len(missing)} unknown entries, e.g. {missing[:5]}")
    prose = load_prose(subject)
    outline = Outline.from_subject(subject)
    t = subject.targets
    sizes = size_bounds(len(order), *_per_unit(subject))
    n = choose_n(len(order), min(sizes), max(sizes), n_units or t.get("units"))
    leaf_of = {i: outline.leaf(entries[i]) for i in order}
    prereqs = {i: [p for p in entries[i].get("prerequisites") or [] if p in entries] for i in order}
    spans = split(order, leaf_of, prereqs, n, sizes)

    titles = {i: (prose["entries"].get(i) or {}).get("title") or entries[i]["title"] for i in order}
    last_entry_of_leaf = {}
    for i in order:
        last_entry_of_leaf[leaf_of[i]] = i

    question_course = (getattr(subject, "cfg", None) or {}).get("course_type") == "questions"
    units, glossary, seen_nodes = [], {}, set()
    for k, (a, b) in enumerate(spans, start=1):
        ids = order[a:b]
        openers = []
        for i in ids:
            for nid in outline.entry_path(entries[i]):
                if nid not in seen_nodes:
                    seen_nodes.add(nid)
                    if prose["openers"].get(nid):
                        openers.append(nid)
        reviews = [leaf_of[i] for i in ids if last_entry_of_leaf[leaf_of[i]] == i and prose["reviews"].get(leaf_of[i])]
        terms = []
        for i in sorted(ids, key=lambda x: ("Landmark", "Major", "Minor").index(entries[x].get("weight", "Minor"))
                        if entries[x].get("weight") in ("Landmark", "Major", "Minor") else 3):
            cands = []
            d = entries[i].get("definition") or {}
            if d.get("text") and not is_question_entry(entries[i], question_course):
                cands.append({"term": entries[i]["title"], "text": d["text"], "sent_ids": d.get("sent_ids") or []})
            cands += prose["glossary"].get(i) or []
            for c in cands:
                key = c["term"].strip().lower()
                if key in glossary or len(terms) >= MAX_TERMS:
                    continue
                glossary[key] = {"term": c["term"], "text": c["text"], "sent_ids": c.get("sent_ids") or [],
                                 "entry": i, "unit": k}
                terms.append(key)
        q = prose["questions"].get(ids[0])
        first_path = outline.entry_path(entries[ids[0]])
        units.append({"n": k, "entries": ids, "path": first_path, "leaf": first_path[-1] if first_path else None,
                      "openers": openers, "reviews": reviews, "terms": terms,
                      "question": q if subject.edition.get("questions") else None})

    for u in units:
        k = u["n"]
        prev = units[k - 2] if k > 1 else None
        nxt = units[k] if k < len(units) else None
        u["last_time"] = _join([titles[i] for i in prev["entries"]]) if prev else None
        u["answer_prev"] = (prev.get("question") or {}).get("a") if prev and prev.get("question") else None
        u["next"] = _join([titles[i] for i in nxt["entries"]]) if nxt else None

    unit_of = {i: u["n"] for u in units for i in u["entries"]}
    for e in entries.values():
        if e["id"] in unit_of:
            u = units[unit_of[e["id"]] - 1]
            e["unit"], e["position"] = u["n"], u["entries"].index(e["id"]) + 1
        else:
            e["unit"], e["position"] = None, None
    _save_entries_in_place(subject, entries)

    sizes_used = [len(u["entries"]) for u in units]
    doc = {"subject": subject.slug, "built": now_iso(), "n_units": len(units), "n_entries": len(order),
           "sizes": {str(s): sizes_used.count(s) for s in sorted(set(sizes_used))}, "units": units}
    write_json(subject.units_path, doc)
    write_json(subject.glossary_path, {"subject": subject.slug, "terms": glossary})
    stragglers = sum(1 for (a, b) in spans if a > 0 and leaf_of[order[a]] == leaf_of[order[a - 1]]
                     and (a + 1 == len(order) or leaf_of[order[a + 1]] != leaf_of[order[a]]))
    log(f"[units] {len(order)} entries -> {len(units)} units ({doc['sizes']}); {len(glossary)} glossary terms; "
        f"{stragglers} units open with a chapter's last entry")
    return doc


def _save_entries_in_place(subject, entries):
    """Write unit/position back without regrouping the entry files."""
    from ..util import read_jsonl, write_jsonl
    for p in subject.entry_files():
        rows = read_jsonl(p)
        write_jsonl(p, [entries.get(r["id"], r) for r in rows])
