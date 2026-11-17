"""Chapter dossiers: the candidate sentences a consolidation pass turns into entries.

    wikicourse dossier <subject> [CHAPTER|all]

One folder per frame chapter, work/dossiers/<chapter key>/, with chunk_NN.md files of about 250 lines. Pages
are grouped by concept (one block per article: the chapter's seeds first, then pages the graph assigned to the
chapter), most important first. Each block carries:

  - the page's importance, WikiProject class, Vital and navbox flags, QID, in-scope inlinks;
  - prerequisites the graph suggests (lead links and RefD) among in-scope pages;
  - its definition (first lead sentence) and its informative sentences, one per line:
      S:<sent_id> | § <section> | <sentence> | links: <articles> | cites: <years> | <flags>
  - sentences on other in-scope pages that mention it ("also on").

Flags: CITATION NEEDED and other maintenance tags, DATED (a date the history branch may use), CONTESTED
(words such as debated, disputed, controversial).
"""
import json
import re
from collections import defaultdict

from ..extract import sentences as SN
from ..graph.build import chapters as frame_chapters
from ..graph.build import load as load_graph
from ..util import atomic_write

CHUNK = 250
MAX_SEED = 80
MAX_OTHER = 25
MAX_ALSO = 8
CONTESTED = re.compile(r"\b(debat\w*|disput\w*|controvers\w*|contested|unclear|uncertain|disagree\w*)\b", re.I)
SKIP_SECTIONS = re.compile(r"(in popular culture|in fiction|gallery|filmography|discography)", re.I)


def _flags(tags, dates_json, text):
    f = []
    if tags:
        f += [t.upper() for t in tags]
    if dates_json:
        f.append("DATED")
    if CONTESTED.search(text):
        f.append("CONTESTED")
    return f


def _line(sid, section, text, links, years, flags, page=None):
    where = f"{page} § {section}" if page else f"§ {section}"
    return (f"S:{sid} | {where} | {text} | links: {'; '.join(links[:6]) or '-'} | "
            f"cites: {','.join(map(str, years[:4])) or '-'}" + (f" | {' '.join(flags)}" if flags else ""))


def _informative(row):
    sid, section, idx, text, is_row, is_lead, links, dates = row
    if SKIP_SECTIONS.search(section or ""):
        return False
    if is_row and section != "infobox":
        return len(text) > 25 and bool(re.search(r"[A-Za-z]{4}", text))
    return 40 <= len(text) <= 600


def chapter_pages(subject, graph, chapter_key):
    nodes = graph["nodes"]
    seeds = []
    for p in (subject.frame or {}).get("parts") or []:
        for c in p.get("chapters") or []:
            if c.get("key") == chapter_key:
                # `also`: pages owned by another chapter that this one draws on (Soil texture for its details)
                seeds = [s for s in (c.get("seeds") or []) + (c.get("also") or []) if s in nodes]
    assigned = [t for t, n in nodes.items() if n.get("chapter") == chapter_key and t not in seeds]
    assigned.sort(key=lambda t: -nodes[t]["importance"])
    return seeds, assigned


def build(subject, chapter="all", log=print):
    graph = load_graph(subject)
    if not graph["nodes"]:
        raise SystemExit("no graph yet; run `wikicourse graph build` first")
    nodes = graph["nodes"]
    db = SN.connect()
    in_scope = {t for t, n in nodes.items() if n["in_scope"]}
    # mentions: page -> sentences on other in-scope pages linking to it
    also = defaultdict(list)
    q = ("SELECT s.sent_id, s.title, s.section, s.sentence, s.links FROM sentences s JOIN subject_pages p "
         "ON p.title = s.title WHERE p.subject = ? AND s.links != '[]'")
    for sid, title, section, text, links in db.execute(q, (subject.slug,)):
        if title not in in_scope:
            continue
        for l in json.loads(links):
            if l != title and l in nodes and len(also[l]) < 40:
                also[l].append((sid, title, section, text))
    wanted = [c for c in frame_chapters(subject) if chapter in ("all", c[1], c[3])]
    if not wanted:
        raise SystemExit(f"no frame chapter '{chapter}'")
    summary = []
    for pk, ck, ptitle, ctitle in wanted:
        seeds, assigned = chapter_pages(subject, graph, ck)
        lines = []
        for t in seeds + assigned:
            n = nodes[t]
            rows = SN.page_sentences(db, t)
            if not rows:
                continue
            flags = [x for x, on in (("seed", t in seeds), ("vital", n["vital"]), ("navbox", n["navbox"])) if on]
            head = (f"## {t} [{', '.join(flags) or 'assigned'}] importance {n['importance']}"
                    f"{' · ' + n['importance_class'] if n.get('importance_class') else ''}"
                    f"{' · ' + n['qid'] if n.get('qid') else ''} · in-scope inlinks {n['inlinks_in_scope']}")
            lines += ["", head]
            pre = [l for l in n.get("lead_links") or [] if l in in_scope][:8]
            rd = sorted((graph["refd"].get(t) or {}).items(), key=lambda kv: -kv[1])[:6]
            if pre or rd:
                lines.append(f"Suggested prerequisites: lead links: {'; '.join(pre) or '-'} | RefD: "
                             + ("; ".join(f"{b} ({s})" for b, s in rd) or "-"))
            d = SN.definition(db, t)
            if d:
                lines.append(f"Definition: S:{d['sent_id']} | {d['text']}")
            cap = MAX_SEED if t in seeds else MAX_OTHER
            pool = [r for r in rows if _informative(r) and (not d or r[0] != d["sent_id"])]
            kept, cut = _spread(pool, cap)
            prev_section = None
            for sid, section, idx, text, is_row, is_lead, links, dates in kept:
                if prev_section is not None and section != prev_section and cut.get(prev_section):
                    lines.append(f"(§ {prev_section}: {cut.pop(prev_section)} more sentences; "
                                 f"`wikicourse page {subject.slug} \"{t}\" --section \"{prev_section}\"`)")
                prev_section = section
                full = db.execute("SELECT cites, tags, cite_years FROM sentences WHERE sent_id = ?", (sid,)).fetchone()
                tags = json.loads(full[1] or "[]")
                years = json.loads(full[2] or "[]")
                lines.append(_line(sid, section, text, json.loads(links or "[]"), years, _flags(tags, dates, text)))
            for sec, n in cut.items():
                lines.append(f"(§ {sec}: {n} more sentences; `wikicourse page {subject.slug} \"{t}\" --section \"{sec}\"`)")
            for sid, title, section, text in also.get(t, [])[:MAX_ALSO]:
                if title not in (seeds + assigned):
                    lines.append("also on: " + _line(sid, section, text, [], [], _flags([], None, text), title))
        out = subject.dossier_dir / ck
        if out.exists():
            for p in out.glob("chunk_*.md"):
                p.unlink()
        chunks = _chunk(lines)
        for k, ch in enumerate(chunks, start=1):
            hdr = [f"# Dossier: {ptitle} › {ctitle}, chunk {k}/{len(chunks)}", "",
                   "Format: `S:<sent_id>` | § section | sentence | links | cites | flags. Blocks are pages (concepts), "
                   "most important first; `also on:` lines are sentences on other pages that mention it.", ""]
            atomic_write(out / f"chunk_{k:02d}.md", "\n".join(hdr + ch) + "\n")
        summary.append((ck, len(seeds), len(assigned), len(lines), len(chunks)))
        log(f"[dossier] {ck}: {len(seeds)} seeds + {len(assigned)} assigned pages, {len(lines)} lines, "
            f"{len(chunks)} chunks")
    return summary


def _spread(pool, cap):
    """Keep at most `cap` sentences, spread across sections (round-robin in page order), so a long early section
    never crowds out the later ones. Returns (kept rows in page order, {section: sentences left out})."""
    if len(pool) <= cap:
        return pool, {}
    by_sec = defaultdict(list)
    order = []
    for r in pool:
        if r[1] not in by_sec:
            order.append(r[1])
        by_sec[r[1]].append(r)
    picked, k = set(), 0
    while len(picked) < cap:
        added = False
        for sec in order:
            if k < len(by_sec[sec]) and len(picked) < cap:
                picked.add(by_sec[sec][k][0])
                added = True
        if not added:
            break
        k += 1
    kept = [r for r in pool if r[0] in picked]
    cut = {sec: sum(1 for r in by_sec[sec] if r[0] not in picked) for sec in order}
    return kept, {s: n for s, n in cut.items() if n}


def _chunk(lines):
    """Split at page blocks, about CHUNK lines per chunk."""
    blocks, cur = [], []
    for l in lines:
        if l.startswith("## ") and cur:
            blocks.append(cur)
            cur = []
        cur.append(l)
    if cur:
        blocks.append(cur)
    chunks, cur = [], []
    for b in blocks:
        if cur and len(cur) + len(b) > CHUNK:
            chunks.append(cur)
            cur = []
        cur += b
    if cur:
        chunks.append(cur)
    return chunks or [[]]
