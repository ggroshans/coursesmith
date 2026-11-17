"""publish check: fail the build when a unit edition breaks the course's rules.

Fails when:
  - a unit has fewer or more entries than targets.per_unit allows (4-5);
  - units.json and the locked order disagree (an entry missing, repeated, or out of order);
  - a prerequisite lands in a later unit (same unit: warning);
  - a selected entry has no fact with sent_ids, or no written text;
  - a number in an entry's prose is absent from its facts (and its date line, title, notes);
  - a glossary term is used in an earlier unit's prose than the unit that defines it;
  - a question's answer is not supported by its unit's facts (sent_ids, numbers);
  - an image lacks a license record (or the license is not CC BY-SA, CC0 or public domain);
  - an EPUB exceeds 1 MB (2 MB with images).

Known false alarms go in subjects/<slug>/waivers.json, each with a reason:
  {"numbers": {"<entry id>": {"values": [4.5], "reason": "..."}},
   "terms": {"<term>": "reason"}, "questions": {"<first entry id>": "reason"}}
"""
import re

from .. import config
from ..util import read_json
from ..write.render import REF_RE
from ..write.render import load as load_prose

NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
from .units import _per_unit, size_bounds
from .images import OK as OK_LICENSES  # one rule for fetching and checking: CC BY, CC BY-SA, CC0, PD


def nums(text):
    out = set()
    for m in NUM.findall(text or ""):
        try:
            out.add(float(m.replace(",", "")))
        except ValueError:
            pass
    return out


def allowed_numbers(e):
    texts = [e.get("title") or "", e.get("date_display") or "", e.get("contested_note") or "",
             (e.get("definition") or {}).get("text") or "", e.get("notes") or ""]
    texts += [f.get("text") or "" for f in e.get("facts") or []]
    # other values the sources give (conflicts) and the entry's dated events are sourced too
    texts += [f"{c.get('text') or ''} {c.get('date_text') or ''} {c.get('date_ma') or ''}" for c in e.get("conflicts") or []]
    texts += [str(ev.get("date_text") or "") for ev in e.get("events") or []]
    texts += [str(v.get("note") or "") for v in e.get("verification") or []]
    texts += [str(x.get("text") or "") for x in e.get("external") or []]
    out = set()
    for t in texts:
        out |= nums(t)
    for k in ("date_ma", "date_young_ma", "uncertainty_ma"):
        if isinstance(e.get(k), (int, float)):
            out.add(float(e[k]))
    return out


def run(subject, log=print):
    problems, warnings = [], []
    entries = subject.entries_by_id()
    prose = load_prose(subject)
    units = (subject.units() or {}).get("units") or []
    waivers = read_json(subject.dir / "waivers.json", {}) or {}
    if not units:
        return [f"{subject.slug}: no units.json"], []
    lo, hi = size_bounds(sum(len(u["entries"]) for u in units), *_per_unit(subject))

    unit_of, seq = {}, []
    for u in units:
        if not lo <= len(u["entries"]) <= hi:
            problems.append(f"unit {u['n']}: {len(u['entries'])} entries (want {lo}-{hi})")
        for i in u["entries"]:
            if i in unit_of:
                problems.append(f"{i} appears in units {unit_of[i]} and {u['n']}")
            unit_of[i] = u["n"]
            seq.append(i)
    order = (subject.order() or {}).get("order") or []
    if order and seq != order:
        problems.append("units.json does not follow order.json; re-run `units build`")
    selected = [i for i, e in entries.items() if e.get("selected")]
    missing = [i for i in selected if i not in unit_of]
    if missing:
        problems.append(f"{len(missing)} selected entries are in no unit, e.g. {missing[:5]}")

    for i in seq:
        e = entries.get(i)
        if not e:
            problems.append(f"{i}: in units.json but not in entries")
            continue
        if not any(f.get("sent_ids") for f in e.get("facts") or []) and not e.get("external"):
            problems.append(f"{i}: no fact with sent_ids")
        for p in e.get("prerequisites") or []:
            if p not in unit_of:
                continue
            if unit_of[p] > unit_of[i]:
                problems.append(f"{i} (unit {unit_of[i]}): prerequisite {p} lands later, in unit {unit_of[p]}")
            elif unit_of[p] == unit_of[i] and seq.index(p) > seq.index(i):
                problems.append(f"{i}: prerequisite {p} comes after it in the same unit")
            elif unit_of[p] == unit_of[i]:
                warnings.append(f"{i}: prerequisite {p} is in the same unit ({unit_of[i]})")
        p = prose["entries"].get(i) or {}
        if not p.get("text"):
            problems.append(f"{i}: no written text")
            continue
        body = REF_RE.sub("", p["text"]) + " " + (p.get("title") or "")
        allowed = allowed_numbers(e)
        waived = set(map(float, ((waivers.get("numbers") or {}).get(i) or {}).get("values") or []))
        extra = sorted(x for x in nums(body) if x not in allowed and x not in waived and not (x <= 12 and x == int(x)))
        if extra:
            problems.append(f"{i}: numbers not in its facts: {extra[:6]}")
        img = e.get("image")
        if img and subject.edition.get("images"):
            if not img.get("license") or not OK_LICENSES.search(img["license"]) or not img.get("file"):
                problems.append(f"{i}: image without an acceptable license record ({img.get('license')})")

    # terms used before the unit that defines them
    glossary = (read_json(subject.glossary_path) or {}).get("terms", {})
    term_waivers = waivers.get("terms") or {}
    if glossary:
        unit_text = {}
        for u in units:
            unit_text[u["n"]] = " ".join((prose["entries"].get(i) or {}).get("text") or "" for i in u["entries"])
        for key, t in glossary.items():
            if key in term_waivers:
                continue
            rx = re.compile(rf"(?<![\w-]){re.escape(t['term'])}(?:s|es)?(?![\w-])", re.I)
            early = [n for n in range(1, t["unit"]) if rx.search(unit_text.get(n, ""))]
            if early:
                problems.append(f"term '{t['term']}' is used in unit {early[0]} before unit {t['unit']} defines it")

    # questions
    if subject.edition.get("questions"):
        qw = waivers.get("questions") or {}
        for u in units:
            q = u.get("question")
            if not q:
                warnings.append(f"unit {u['n']}: no question")
                continue
            if u["entries"][0] in qw:
                continue
            facts = [f for i in u["entries"] for f in entries[i].get("facts") or []]
            unit_sids = {s for f in facts for s in f.get("sent_ids") or []}
            if not q.get("sent_ids") or not set(q["sent_ids"]) <= unit_sids:
                problems.append(f"unit {u['n']}: question answer cites sentences outside the unit's facts")
            allowed = set()
            for i in u["entries"]:
                allowed |= allowed_numbers(entries[i])
            extra = [x for x in nums(q.get("a")) if x not in allowed and not (x <= 12 and x == int(x))]
            if extra:
                problems.append(f"unit {u['n']}: question answer has numbers not in the unit's facts: {extra}")

    # EPUB sizes
    limit = (2 if subject.edition.get("images") else 1) * 1024 * 1024
    built = sorted((config.EPUB_DIR / subject.slug).glob(f"{subject.slug}-unit-*.epub"))
    for p in built:
        if p.stat().st_size > limit:
            problems.append(f"{p.name}: {p.stat().st_size // 1024} KB exceeds {limit // 1024} KB")
    if not built:
        warnings.append("no EPUBs built yet (run `publish build`)")

    log(f"[check] {subject.slug}: {len(units)} units, {len(seq)} entries, {len(problems)} problems, "
        f"{len(warnings)} warnings")
    for p in problems[:200]:
        log(f"  PROBLEM {p}")
    for w in warnings[:40]:
        log(f"  warn {w}")
    return problems, warnings
