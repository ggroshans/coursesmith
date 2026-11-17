"""finalize: validate draft entries and write the subject's final entry files.

    wikicourse finalize <subject> [CHAPTER|all] [--check FILE]
    wikicourse finalize <subject> CHAPTER --merge

--merge joins a split chapter's part files (entries/draft/<key>.partNN.jsonl, one per chunk, from passes that
shared the chapter) into <key>.jsonl. Entries drafted twice (same title, or same whole-page article) become one:
facts, sources, prerequisites, related entries and events are unioned, and facts over the limit keep their
sentence ids in mention_sent_ids. The part, progress and gaps files move to work/tmp/<key>/parts/, and the gaps
are joined into <key>.gaps.md.

Input: entries/draft/<chapter key>.jsonl (or .partNN.jsonl files, merged in name order), written by the
consolidation passes (guides/CONSOLIDATION_GUIDE.md). Output: entries/<chapter key>.jsonl.

Checks every draft entry for: a valid kind, weight and level; 1-8 facts (Landmark/Major at least 2), each at
most 40 words and citing known sent_ids; a definition citing known sent_ids; an `article` that was crawled
(or "Page#Section"). Then it:
  - keeps ids stable: an entry matching an existing one (same title, or same article + chapter) keeps its id;
    new entries get <short>-<part key>-<nnn>. Ids never change after `order lock`.
  - resolves prerequisites and related entries given as titles or articles to ids;
  - derives sources (title, url, revid, sent_ids) from every cited sentence, flags (citation_needed,
    contested), dated events for the history branch, and the curriculum tests passed;
  - lists likely duplicates (shared article, shared Wikidata QID, similar titles) in reports/duplicates.md.
"""
import json
import re
from collections import defaultdict

from ..extract import sentences as SN
from ..graph.build import load as load_graph
from ..util import atomic_write, read_json, read_jsonl, write_jsonl

KINDS = ["Concept", "Process", "Classification", "Method", "Material", "Practice", "Event", "Person/Institution",
         "Debate"]
WEIGHTS = ["Landmark", "Major", "Minor"]
LEVELS = ["Foundational", "Intermediate", "Advanced"]
MAX_FACT_WORDS = 40
KEEP = ("score", "score_parts", "selected", "unit", "position", "verification", "external", "source_tier",
        "image", "curriculum")


def frame_chapters(subject):
    """chapter key -> (part key, part title, chapter title)."""
    out = {}
    for p in (subject.frame or {}).get("parts") or []:
        for c in p.get("chapters") or []:
            out[c.get("key")] = (p.get("key"), p["title"], c["title"])
    return out


def load_drafts(subject, chapter="all"):
    out = defaultdict(list)
    if not subject.draft_dir.exists():
        return out
    for p in sorted(subject.draft_dir.glob("*.jsonl")):
        ck = p.name.split(".")[0]
        if chapter not in ("all", ck):
            continue
        for e in read_jsonl(p):
            e.setdefault("_chapter_key", ck)
            out[ck].append(e)
    return out


def _fact_cap(e):
    return 4 if e.get("weight") == "Minor" else 8


def _merge_into(a, b):
    """Fold draft entry b into a (same concept drafted by two passes)."""
    seen = {re.sub(r"\W+", " ", f.get("text", "").lower()).strip() for f in a.get("facts") or []}
    facts = list(a.get("facts") or [])
    for f in b.get("facts") or []:
        k = re.sub(r"\W+", " ", f.get("text", "").lower()).strip()
        if k and k not in seen:
            seen.add(k)
            facts.append(f)
    cap = _fact_cap(a)
    if len(facts) > cap:
        spill = [s for f in facts[cap:] for s in f.get("sent_ids") or []]
        a["mention_sent_ids"] = list(dict.fromkeys((a.get("mention_sent_ids") or []) + spill))
        facts = facts[:cap]
    a["facts"] = facts
    for key in ("prerequisites", "related", "distinct_from", "mention_sent_ids"):
        if b.get(key):
            a[key] = list(dict.fromkeys((a.get(key) or []) + b[key]))
    for key in ("events", "conflicts"):
        have = {json.dumps(x, sort_keys=True) for x in a.get(key) or []}
        a[key] = (a.get(key) or []) + [x for x in b.get(key) or [] if json.dumps(x, sort_keys=True) not in have]
    a["contested"] = bool(a.get("contested") or b.get("contested"))
    a["contested_note"] = a.get("contested_note") or b.get("contested_note")
    a["wants_image"] = bool(a.get("wants_image") or b.get("wants_image"))
    if b.get("notes") and b["notes"] != a.get("notes"):
        a["notes"] = "; ".join(x for x in (a.get("notes"), b["notes"]) if x)
    if not a.get("article") and b.get("article"):
        a["article"] = b["article"]
    return a


def merge_parts(subject, chapter, log=print):
    d = subject.draft_dir
    parts = sorted(d.glob(f"{chapter}.part*.jsonl"))
    if not parts:
        log(f"[finalize] {chapter}: no part files to merge")
        return 0
    whole = d / f"{chapter}.jsonl"
    merged, by_title, by_page = [], {}, {}
    n_in = n_dup = 0
    for p in ([whole] if whole.exists() else []) + parts:
        for e in read_jsonl(p):
            n_in += 1
            t = re.sub(r"\s+", " ", e["title"].lower()).strip()
            art = (e.get("article") or "").lower()
            page = art if art and "#" not in art else None
            old = by_title.get(t) or (by_page.get(page) if page else None)
            if old is not None and e["title"] not in (old.get("distinct_from") or []):
                _merge_into(old, e)
                n_dup += 1
                continue
            merged.append(e)
            by_title.setdefault(t, e)
            if page:
                by_page.setdefault(page, e)
    write_jsonl(whole, merged)
    keep = subject.dir / "work" / "tmp" / chapter / "parts"
    keep.mkdir(parents=True, exist_ok=True)
    gaps = []
    for p in sorted(d.glob(f"{chapter}.*")):
        if p == whole:
            continue
        if ".gaps" in p.name:
            gaps.append(p.read_text(encoding="utf-8").strip())
        p.rename(keep / p.name)
    if gaps:
        atomic_write(d / f"{chapter}.gaps.md", "\n\n".join(g for g in gaps if g) + "\n")
    log(f"[finalize] {chapter}: {len(parts)} part files, {n_in} drafts -> {len(merged)} entries "
        f"({n_dup} merged); parts kept in {keep.relative_to(subject.dir)}")
    return len(merged)


STOP = frozenset(("the", "of", "and", "a", "in"))


def stop_words(subject):
    """Words every title in the subject may share ('soil' in soil science): ignored when comparing titles."""
    words = f"{subject.title} {subject.short}".lower()
    return STOP | set(re.findall(r"[a-z0-9]+", words))


def _tokens(t, stop=STOP):
    return {w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if w not in stop}


def validate(e, known, crawled):
    problems = []
    t = e.get("title") or "(untitled)"
    if not e.get("title"):
        problems.append("missing title")
    if e.get("kind") not in KINDS:
        problems.append(f"{t}: kind {e.get('kind')!r} not one of {KINDS}")
    if e.get("weight") not in WEIGHTS:
        problems.append(f"{t}: weight {e.get('weight')!r}")
    if e.get("level") not in LEVELS:
        problems.append(f"{t}: level {e.get('level')!r}")
    facts = e.get("facts") or []
    lo = 2 if e.get("weight") in ("Landmark", "Major") else 1
    if not lo <= len(facts) <= 8:
        problems.append(f"{t}: {len(facts)} facts (want {lo}-8)")
    for f in facts:
        if len((f.get("text") or "").split()) > MAX_FACT_WORDS:
            problems.append(f"{t}: fact over {MAX_FACT_WORDS} words: {f['text'][:60]}...")
        if not f.get("sent_ids"):
            problems.append(f"{t}: fact without sent_ids: {f.get('text', '')[:60]}")
    d = e.get("definition")
    if d and not d.get("sent_ids"):
        problems.append(f"{t}: definition without sent_ids")
    for sid in _all_sids(e):
        if sid not in known:
            problems.append(f"{t}: unknown sent_id {sid}")
    art = (e.get("article") or "").split("#")[0]
    if art and art not in crawled:
        problems.append(f"{t}: article {art!r} was not crawled")
    return problems


def _all_sids(e):
    out = []
    for f in e.get("facts") or []:
        out += f.get("sent_ids") or []
    out += (e.get("definition") or {}).get("sent_ids") or []
    for ev in e.get("events") or []:
        out += ev.get("sent_ids") or []
    out += e.get("mention_sent_ids") or []
    for c in e.get("conflicts") or []:
        out += ([c["sent_id"]] if c.get("sent_id") else []) + list(c.get("sent_ids") or [])
    return list(dict.fromkeys(out))


def finalize(subject, chapter="all", check_file=None, log=print):
    db = SN.connect()
    graph = load_graph(subject)
    nodes = graph["nodes"]
    crawled = set(nodes) or {r[0] for r in db.execute(
        "SELECT title FROM subject_pages WHERE subject = ?", (subject.slug,))}
    chapters = frame_chapters(subject)
    if check_file:
        drafts = {"check": read_jsonl(check_file)}
    else:
        drafts = load_drafts(subject, chapter)
    every = [e for es in drafts.values() for e in es]
    sids = {s for e in every for s in _all_sids(e)}
    found = SN.lookup(db, sids)
    known = set(found)

    problems = []
    for e in every:
        problems += validate(e, known, crawled)
    if check_file:
        log(f"[finalize] {check_file}: {len(every)} entries, {len(problems)} problems")
        for p in problems:
            log(f"  PROBLEM {p}")
        return problems

    existing = {e["id"]: e for e in subject.entries()}
    by_title = {e["title"].lower(): e for e in existing.values()}
    by_art = {((e.get("article") or "").lower(), e.get("chapter")): e for e in existing.values() if e.get("article")}
    used = set(existing)
    counters = defaultdict(int)
    for i in used:
        m = re.match(r"^(.*)-(\d{3})$", i)
        if m:
            counters[m.group(1)] = max(counters[m.group(1)], int(m.group(2)))

    out_by_chapter = defaultdict(list)
    for ck, es in drafts.items():
        pk, ptitle, ctitle = chapters.get(ck, ("misc", "Unplaced", ck))
        for e in es:
            e.pop("_chapter_key", None)
            e.setdefault("part", ptitle)
            e.setdefault("chapter", ctitle)
            old = by_title.get(e["title"].lower()) or by_art.get(((e.get("article") or "").lower(), e["chapter"]))
            if old:
                e["id"] = old["id"]
                for k in KEEP:
                    if k in old and k not in e:
                        e[k] = old[k]
            else:
                prefix = f"{subject.short}-{pk}"
                counters[prefix] += 1
                e["id"] = f"{prefix}-{counters[prefix]:03d}"
                used.add(e["id"])
            out_by_chapter[ck].append(e)

    finals = [e for es in out_by_chapter.values() for e in es]
    # untouched chapters keep their entries; a processed chapter is exactly what its drafts say, so an entry
    # merged away or deleted from a draft disappears
    done = {chapters.get(ck, (None, None, ck))[2] for ck in drafts}
    have = {f["id"] for f in finals}
    for e in existing.values():
        if e["id"] not in have and e.get("chapter") not in done:
            finals.append(e)
    title_to_id = {}
    for e in finals:
        title_to_id.setdefault(e["title"].lower(), e["id"])
        if e.get("article"):
            title_to_id.setdefault(e["article"].lower(), e["id"])
    unresolved = []
    for e in finals:
        for key in ("prerequisites", "related"):
            ids = []
            for p in e.get(key) or []:
                pid = p if any(f["id"] == p for f in finals) else title_to_id.get(str(p).lower())
                if pid and pid != e["id"]:
                    ids.append(pid)
                elif not pid:
                    unresolved.append(f"{e['id']} {key}: {p}")
            e[key] = list(dict.fromkeys(ids))
        _derive(e, found, nodes, db)

    dups = possible_duplicates(finals, stop_words(subject))
    _write_dups(subject, dups)
    groups = defaultdict(list)
    for e in finals:
        ck = next((k for k, v in chapters.items() if v[2] == e.get("chapter")), None) or "misc"
        groups[ck].append(e)
    for p in subject.entries_dir.glob("*.jsonl"):
        p.unlink()
    for ck, es in groups.items():
        write_jsonl(subject.entries_dir / f"{ck}.jsonl", es)
    log(f"[finalize] {len(finals)} entries in {len(groups)} chapters; {len(problems)} problems, "
        f"{len(unresolved)} unresolved prerequisite/related names, {len(dups)} possible duplicates "
        f"(reports/duplicates.md)")
    for p in problems[:80]:
        log(f"  PROBLEM {p}")
    for u in unresolved[:30]:
        log(f"  unresolved {u}")
    return problems


def _derive(e, found, nodes, db):
    by_page = defaultdict(list)
    tags = set()
    events = list(e.get("events") or [])
    for sid in _all_sids(e):
        r = found.get(sid)
        if not r:
            continue
        by_page[r["title"]].append(sid)
    for sid in _all_sids(e):
        row = db.execute("SELECT tags, dates FROM sentences WHERE sent_id = ?", (sid,)).fetchone()
        if row:
            tags |= set(json.loads(row[0] or "[]"))
            if row[1] and not e.get("events") and any(sid in (f.get("sent_ids") or []) for f in e.get("facts") or []):
                for d in json.loads(row[1])[:1]:
                    events.append({"date_text": d.get("date_text"), "date_ma": d.get("date_ma"), "sent_ids": [sid]})
    e["sources"] = [{"title": t, "url": found[s[0]]["url"], "revid": found[s[0]]["revid"], "sent_ids": s}
                    for t, s in sorted(by_page.items(), key=lambda kv: (kv[0] != (e.get("article") or "").split("#")[0],
                                                                        -len(kv[1]), kv[0]))]
    e["events"] = events[:3]
    flags = set(e.get("flags") or [])
    if "citation needed" in tags:
        flags.add("citation_needed")
    if e.get("contested"):
        flags.add("contested")
    if e.get("conflicts"):
        flags.add("conflict")
    e["flags"] = sorted(flags)
    e.setdefault("contested", False)
    e.setdefault("conflicts", [])
    e.setdefault("related", [])
    e.setdefault("verification", [])
    e.setdefault("external", [])
    e["source_tier"] = e.get("source_tier") or "wikipedia"
    art = (e.get("article") or "").split("#")[0]
    n = nodes.get(art) or {}
    # a section entry is not the page's Wikidata item
    e["qid"] = e.get("qid") or (n.get("qid") if "#" not in (e.get("article") or "") else None)
    tests = []
    if e.get("article"):
        tests.append("own article" if "#" not in e["article"] else "own section")
    if n.get("navbox") or n.get("vital"):
        tests.append("hub list")
    if n.get("importance_class") in ("Top", "High"):
        tests.append("Top/High importance")
    if len(by_page) >= 2:
        tests.append("mentioned on 2+ pages")
    e["curriculum"] = tests


def possible_duplicates(entries, stop=STOP):
    out = []
    for i, a in enumerate(entries):
        for b in entries[i + 1:]:
            if b["title"] in (a.get("distinct_from") or []) or a["title"] in (b.get("distinct_from") or []):
                continue
            why = None
            if a.get("article") and a.get("article") == b.get("article"):
                why = f"same article {a['article']}"
            elif a.get("qid") and a.get("qid") == b.get("qid") and "#" not in (a.get("article") or "") + (b.get("article") or ""):
                why = f"same QID {a['qid']}"
            else:
                ta, tb = _tokens(a["title"], stop), _tokens(b["title"], stop)
                if ta and tb and len(ta & tb) / len(ta | tb) >= 0.75:
                    why = "similar titles"
            if why:
                out.append((a["id"], a["title"], b["id"], b["title"], why))
    return out


def _write_dups(subject, dups):
    L = ["# Possible duplicates", "",
         "Merge each pair into one entry, or list each title in the other's `distinct_from`, then re-run "
         "`finalize`.", ""]
    L += [f"- {a} **{ta}** ↔ {b} **{tb}** ({why})" for a, ta, b, tb, why in dups] or ["None."]
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "duplicates.md", "\n".join(L) + "\n")


def known_ids(subject):
    return read_json(subject.order_path, {}).get("order") or []
