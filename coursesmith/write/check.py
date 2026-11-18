"""write check: the WRITING_GUIDE rules a script can test.

Problems (must be fixed): an entry without text, a number not in the entry's facts, a banned phrase, an
exclamation mark, more than one "imagine"/"picture" per unit, a {{ref:id}} to an unknown entry, a number in an
opener or review that is not in its chapter's facts, a figure (figures.json) that does not draw or states a
number not in its entry's facts.
Warnings (read each): an entry over 300 words or outside its word range, a sentence over 28 words, a term used
anywhere earlier in the course than the entry that defines it (publish check fails on these once units exist:
write {{ref:<id>}} or say it in plain words), an opener or review outside 3-5 sentences, a long title.

    coursesmith write check <subject> [--part KEY]

--part reports only that part's entries, openers and reviews, for writers working on one part in parallel.
"""
import re

from ..outline import Outline
from ..publish.check import allowed_numbers, nums
from .render import REF_RE
from .render import load as load_prose
from .skeleton import word_range

BANNED = ["paved the way", "set the stage", "a testament to", "it's important to note", "it’s important to note",
          "delve", "tapestry", "the dawn of", "ushered in", "in the annals of", "plays a crucial role",
          "plays a vital role", "in today's world", "it is worth noting", "game-changer", "unlock the secrets"]
IMAGINE = re.compile(r"\b(imagine|picture)\b", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?])[\"”’)]?\s+(?=[A-Z0-9“\"‘(])")


def sentences(t):
    t = re.sub(r"\b(c|ca|e\.g|i\.e|vs|approx|Mt|St|Dr|No)\.", lambda m: m.group(0).replace(".", "§"), t or "")
    return [s for s in SENT_SPLIT.split(t.strip()) if s.strip()]


def run(subject, part=None, log=print):
    prose = load_prose(subject)
    entries = subject.entries_by_id()
    order = (subject.order() or {}).get("order") or [i for i, e in entries.items() if e.get("selected")]
    outline = Outline.from_subject(subject)
    problems, warnings = [], []
    for i in order:
        e = entries[i]
        p = prose["entries"].get(i) or {}
        t = p.get("text") or ""
        if not t:
            problems.append(f"{i}: no text")
            continue
        for r in REF_RE.findall(t):
            if r not in entries:
                problems.append(f"{i}: {{{{ref:{r}}}}} names no entry")
        body = REF_RE.sub("", t)
        low = body.lower()
        for b in BANNED:
            if b in low:
                problems.append(f"{i}: banned phrase {b!r}")
        if "!" in body:
            problems.append(f"{i}: exclamation mark")
        extra = sorted(x for x in nums(body + " " + (p.get("title") or "")) if x not in allowed_numbers(e)
                       and not (x <= 12 and x == int(x)))
        if extra:
            problems.append(f"{i}: numbers not in its facts: {extra[:6]}")
        n = len(body.split())
        lo, hi = map(int, word_range(e).split()[0].split("-"))
        if n > 300:
            warnings.append(f"{i}: {n} words (over 300: review)")
        elif not lo * 0.8 <= n <= hi * 1.2:
            warnings.append(f"{i}: {n} words (range {lo}-{hi})")
        for s in sentences(body):
            if len(s.split()) > 28:
                warnings.append(f"{i}: long sentence ({len(s.split())} words): {s[:70]}...")
        if len((p.get("title") or "").split()) > 12:
            warnings.append(f"{i}: long title")
    # figures: they draw, and every number in one is in its entry's facts
    from ..publish import figures as figmod
    for i, figs in figmod.load(subject).items():
        if i not in entries:
            problems.append(f"{i}: figures.json names no entry")
            continue
        for k, fig in enumerate(figs, 1):
            for msg in figmod.validate(fig):
                problems.append(f"{i}: figure {k}: {msg}")
            extra = sorted(x for x in figmod.numbers(fig) if x not in allowed_numbers(entries[i])
                           and not (x <= 12 and x == int(x)))
            if extra:
                problems.append(f"{i}: figure {k}: numbers not in its facts: {extra[:6]}")
    # imagine/picture per unit
    for u in (subject.units() or {}).get("units") or []:
        txt = " ".join((prose["entries"].get(i) or {}).get("text") or "" for i in u["entries"])
        txt += " " + " ".join(prose["openers"].get(o) or "" for o in u.get("openers") or [])
        k = len(IMAGINE.findall(txt))
        if k > 1:
            problems.append(f"unit {u['n']}: 'imagine'/'picture' used {k} times (at most once per edition)")
    # terms used before their defining entry, anywhere earlier in the course (one pass with a single regex)
    pos = {i: k for k, i in enumerate(order)}
    term_of = {}
    for i in order:
        if (entries[i].get("definition") or {}).get("text"):
            term = re.sub(r"\s*\(.*?\)", "", entries[i]["title"]).strip()
            if len(term) >= 4:
                term_of.setdefault(term.lower(), i)
    if term_of:
        rx = re.compile(r"(?<![\w-])(" + "|".join(re.escape(t) for t in sorted(term_of, key=len, reverse=True))
                        + r")(?:s|es)?(?![\w-])", re.I)  # plurals count too: "Mollisols" uses "Mollisol"
        for j in order:
            text = REF_RE.sub("", (prose["entries"].get(j) or {}).get("text") or "")
            for t in dict.fromkeys(m.lower() for m in rx.findall(text)):
                i = term_of[t]
                if pos[i] > pos[j]:
                    warnings.append(f"{j} uses '{t}' before {i} ({entries[i]['title']}) defines it: write "
                                    f"{{{{ref:{i}}}}} or say it in plain words")
    # openers and reviews
    facts_under = {}
    for i in order:
        for nid in outline.entry_path(entries[i]):
            facts_under.setdefault(nid, set()).update(allowed_numbers(entries[i]))
    # facts written for openers (the chronicle's scene facts) count for their node
    from ..util import read_json
    for nid, fs in (read_json(subject.write_dir / "opener_facts.json", {}) or {}).items():
        for f in fs:
            facts_under.setdefault(nid, set()).update(nums(f.get("text")))
    for kind in ("openers", "reviews"):
        for nid, t in (prose.get(kind) or {}).items():
            t = REF_RE.sub("", t)  # a {{ref:id}} is a link, not a number
            k = len(sentences(t))
            if not 3 <= k <= 5:
                warnings.append(f"{kind[:-1]} {nid}: {k} sentences (want 3-5)")
            extra = sorted(x for x in nums(t) if x not in facts_under.get(nid, set()) and not (x <= 12 and x == int(x)))
            if extra:
                problems.append(f"{kind[:-1]} {nid}: numbers not in its chapter's facts: {extra[:6]}")
            for b in BANNED:
                if b in t.lower():
                    problems.append(f"{kind[:-1]} {nid}: banned phrase {b!r}")
    if part:
        keys = {pt.get("key"): pt for pt in (subject.frame or {}).get("parts") or []}
        if part not in keys:
            raise SystemExit(f"no part '{part}' in frame.yaml")
        mine = {i for i in order if entries[i].get("part") == keys[part]["title"]}
        nodes = {part} | {c.get("key") for c in keys[part].get("chapters") or []}
        def ours(msg):
            head = msg.split(":")[0].split()
            return (head and head[0] in mine) or (len(head) > 1 and head[0] in ("opener", "review") and head[1] in nodes)
        problems, warnings = [m for m in problems if ours(m)], [m for m in warnings if ours(m)]
        order = [i for i in order if i in mine]
    log(f"[write check] {subject.slug}: {len(order)} entries, {len(problems)} problems, {len(warnings)} warnings")
    for p in problems[:200]:
        log(f"  PROBLEM {p}")
    for w in warnings[:300]:
        log(f"  warn {w}")
    return problems, warnings
