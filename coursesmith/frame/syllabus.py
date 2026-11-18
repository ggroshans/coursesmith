"""The syllabus: a top-down plan of the subject, resolved against Wikipedia and the course.

    coursesmith frame plan-packet <subject>     packet for the planner pass (guides/PLANNER_GUIDE.md)
    coursesmith frame resolve <subject>         map every planned concept to the course, a page, or phrases
    coursesmith dossier <subject> --phrases     dossiers for concepts with no page, built from sentence search

The planner writes scope/syllabus.json (branches, concepts with levels, expected pages and phrases). `resolve`
classifies each concept:
  covered  an entry already teaches it (its title or its article matches);
  page     a Wikipedia page exists: it is added to scope/judge.json as `in` (unless the judge ruled it out), so
           `crawl --judged` fetches it and a gap-fill pass drafts it;
  phrase   no page, but three or more crawled sentences use one of its phrases: a phrase dossier is built;
  none     Wikipedia has no coverage; listed in the report, never written from memory.
and writes scope/syllabus_resolved.json and reports/syllabus.md (per branch).
"""
import collections
import json
import re

from ..util import atomic_write, read_json, slug, write_json

MIN_PHRASE_SENTENCES = 3
MAX_PHRASE_SENTENCES = 60


def _norm(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def plan_packet(subject, log=print):
    from ..graph.build import chapters as frame_chapters
    entries = subject.entries()
    by_ch = collections.defaultdict(list)
    for e in entries:
        by_ch[e.get("chapter")].append(e)
    lines = [f"# Planner packet: {subject.cfg.get('title')}", "", (subject.cfg.get("description") or "").strip(), ""]
    out = (subject.cfg.get("scope") or {}).get("exclude_desc") or []
    if out:
        lines += [f"Out of scope by rule (short descriptions): {', '.join(out)}", ""]
    lines += ["## Current frame and entries", ""]
    last = None
    for pk, ck, ptitle, ctitle in frame_chapters(subject):
        if pk != last:
            lines += [f"### Part: {ptitle} ({pk})", ""]
            last = pk
        es = sorted(by_ch.get(ctitle, []) + by_ch.get(ck, []), key=lambda e: e.get("position") or 0)
        lines.append(f"- **{ck}**: {ctitle} ({len(es)} entries): "
                     + "; ".join(f"{e['title']} [{(e.get('level') or '?')[0]}]" for e in es))
    lines += ["", "## Gap lists from the consolidation passes", ""]
    for p in sorted((subject.dir / "entries" / "draft").glob("*.gaps*.md")):
        body = " ".join(l.strip("-* ").strip() for l in p.read_text(encoding="utf-8").splitlines()
                        if l.strip() and not l.startswith("#"))
        if body:
            lines.append(f"- {p.name.split('.gaps')[0]}: {body[:1500]}")
    judge = read_json(subject.scope_dir / "judge.json", {}) or {}
    new = collections.defaultdict(list)
    for t, v in judge.items():
        if str(v.get("ch") or "").startswith("new:") and v.get("v") != "out":
            new[v["ch"][4:].strip()].append(t)
    if new:
        lines += ["", "## New chapters the scope judge proposed (pages it placed there)", ""]
        for ch, ts in sorted(new.items(), key=lambda kv: -len(kv[1])):
            lines.append(f"- {ch} ({len(ts)}): {'; '.join(sorted(ts)[:40])}")
    path = subject.dir / "work" / "scope" / "plan-packet.md"
    atomic_write(path, "\n".join(lines) + "\n")
    log(f"[plan] packet: {path} ({len(entries)} entries, {len(new)} proposed chapters)")
    return path


def resolve(subject, log=print):
    from ..crawl.api import WikiClient
    from ..crawl.fetch import prescreen
    from ..crawl.store import Store
    from ..extract import sentences as SN
    plan = read_json(subject.scope_dir / "syllabus.json")
    if not plan:
        raise SystemExit("no scope/syllabus.json; run the planner pass (guides/PLANNER_GUIDE.md)")
    store, db = Store(), SN.connect()
    entries = subject.entries()
    by_title = {_norm(e["title"]): e["id"] for e in entries}
    by_art = {}
    for e in entries:
        a = (e.get("article") or "").split("#")[0]
        if a:
            by_art.setdefault(store.canonical(a), e["id"])
    concepts = plan.get("concepts") or []
    pages = [p for c in concepts for p in c.get("pages") or []]
    resolved = prescreen(WikiClient(), store, pages)
    store.flush_caches()
    judge = read_json(subject.scope_dir / "judge.json", {}) or {}
    branch_ch = {b["name"]: b.get("chapter") for b in plan.get("branches") or []}
    out, added = [], 0
    for c in concepts:
        r = {"name": c["name"], "branch": c.get("branch"), "level": c.get("level"),
             "chapter": branch_ch.get(c.get("branch"))}
        hit = by_title.get(_norm(c["name"]))
        live = []
        for p in c.get("pages") or []:
            can = resolved.get(p, p)
            m = store.meta.get(can) or {}
            if m and not m.get("missing") and not m.get("disambig"):
                if can in by_art and not hit:
                    hit = by_art[can]
                live.append(can)
        if hit:
            r.update(status="covered", entry=hit)
        elif live:
            r.update(status="page", pages=live)
            for p in live:
                v = judge.get(p)
                if v and v.get("v") == "out":
                    r.setdefault("judged_out", []).append(p)
                elif not v:
                    judge[p] = {"v": "in", "ch": r["chapter"], "why": f"syllabus: {c['name']}"[:80]}
                    added += 1
            if len(r.get("judged_out") or []) == len(live):
                r["status"] = "judged out"
        else:
            sents = {}
            for ph in [c["name"]] + list(c.get("phrases") or []):
                for sid, title, section, text in SN.search(db, subject.slug, ph, MAX_PHRASE_SENTENCES):
                    sents.setdefault(sid, (title, section, text))
            if len(sents) >= MIN_PHRASE_SENTENCES:
                r.update(status="phrase", phrases=[c["name"]] + list(c.get("phrases") or []), sentences=len(sents))
            else:
                r.update(status="none", sentences=len(sents))
        out.append(r)
    write_json(subject.scope_dir / "judge.json", judge)
    write_json(subject.scope_dir / "syllabus_resolved.json", out)
    _report(subject, plan, out)
    c = collections.Counter(r["status"] for r in out)
    log(f"[resolve] {len(out)} concepts: " + ", ".join(f"{k} {v}" for k, v in c.most_common())
        + f"; {added} pages added to the judge's in list")
    return out


def _report(subject, plan, rows):
    by_b = collections.defaultdict(list)
    for r in rows:
        by_b[r.get("branch") or "-"].append(r)
    L = ["# Syllabus coverage", "",
         "Each planned concept: **covered** (an entry teaches it), **page** (a Wikipedia page to crawl and draft), "
         "**phrase** (no page; a phrase dossier from crawled sentences), **judged out** (the scope judge rejected its "
         "page), **none** (Wikipedia has no coverage).", ""]
    tot = collections.Counter(r["status"] for r in rows)
    L += ["| Branch | Chapter | Concepts | Covered | Page | Phrase | None |", "|---|---|---|---|---|---|---|"]
    for b in plan.get("branches") or []:
        rs = by_b.get(b["name"], [])
        c = collections.Counter(r["status"] for r in rs)
        L.append(f"| {b['name']} | {b.get('chapter') or '-'} | {len(rs)} | {c['covered']} | {c['page']} | "
                 f"{c['phrase']} | {c['none']} |")
    L.append(f"| **All** | | {len(rows)} | {tot['covered']} | {tot['page']} | {tot['phrase']} | {tot['none']} |")
    for b, rs in sorted(by_b.items()):
        miss = [r for r in rs if r["status"] != "covered"]
        if not miss:
            continue
        L += ["", f"## {b}", ""]
        for r in miss:
            extra = {"page": ", ".join(r.get("pages") or []), "phrase": f"{r.get('sentences')} sentences",
                     "none": "no page, no sentences", "judged out": ", ".join(r.get("judged_out") or [])}[r["status"]]
            L.append(f"- {r['name']} ({r.get('level') or '?'}): {r['status']}, {extra}")
    atomic_write(subject.reports_dir / "syllabus.md", "\n".join(L) + "\n")


def phrase_dossiers(subject, log=print):
    """One dossier folder per chapter with phrase concepts: work/dossiers/phrase-<chapter>/chunk_NN.md."""
    from ..consolidate.dossier import CHUNK, _flags, _line
    from ..extract import sentences as SN
    rows = read_json(subject.scope_dir / "syllabus_resolved.json") or []
    db = SN.connect()
    by_ch = collections.defaultdict(list)
    for r in rows:
        if r["status"] == "phrase":
            by_ch[r.get("chapter") or "unplaced"].append(r)
    made = []
    for ch, rs in by_ch.items():
        key = "phrase-" + (slug(ch[4:]) if ch.startswith("new:") else ch)
        lines = []
        for r in rs:
            lines += ["", f"## {r['name']} [phrase concept, no page of its own] level {r.get('level') or '?'}",
                      f"Phrases searched: {'; '.join(r['phrases'])}. Draft with \"article\": null; every fact "
                      "cites these sentences (or others found with `search`)."]
            seen = set()
            for ph in r["phrases"]:
                for sid, title, section, text in SN.search(db, subject.slug, ph, MAX_PHRASE_SENTENCES):
                    if sid in seen or len(seen) >= MAX_PHRASE_SENTENCES or not 40 <= len(text) <= 600:
                        continue
                    seen.add(sid)
                    lines.append(_line(sid, section, text, [], [], _flags([], None, text), title))
        out = subject.dossier_dir / key
        out.mkdir(parents=True, exist_ok=True)
        for p in out.glob("chunk_*.md"):
            p.unlink()
        chunks, cur = [], []
        for l in lines:
            if l.startswith("## ") and len(cur) > CHUNK:
                chunks.append(cur)
                cur = []
            cur.append(l)
        if cur:
            chunks.append(cur)
        for k, c in enumerate(chunks, start=1):
            hdr = [f"# Phrase dossier: {ch}, chunk {k}/{len(chunks)}", "",
                   "Concepts the syllabus names that have no Wikipedia page. Each block lists sentences from crawled "
                   "pages that use the concept's phrases (`S:<sent_id> | <page> § <section> | sentence`).", ""]
            atomic_write(out / f"chunk_{k:02d}.md", "\n".join(hdr + c) + "\n")
        made.append((key, len(rs)))
        log(f"[dossier] {key}: {len(rs)} phrase concepts, {len(chunks)} chunks")
    return made
