"""report gaps: everything the consolidation passes could not teach, in one list to act on.

    coursesmith report gaps <subject> [--probe]

Three kinds of gap, all read from the drafts in entries/draft/:
  * unresolved names: a prerequisite or related title that no entry has. The concept is real, the course just
    never explains it. Each is listed with how often it is named and by which chapters;
  * thin entries: an entry whose notes start with "thin:" (the sources held too little for it);
  * gaps files: each pass's `<chapter>.gaps.md` (pages it expected and did not find), counted per chapter.

`--probe` asks Wikipedia whether a page of that name exists and under which title, so the next step is
`coursesmith frame add <subject> <chapter> "<title>"`. A gap the owner decides to live with goes under `gaps:
accepted:` in subject.yaml, as a name (unresolved) or an entry title (thin), each with a reason, and drops out of
the report. Writes reports/gaps.md and reports/gaps.json; `status` shows the counts and `select` warns while any
are open. See guides/GAPFILL_GUIDE.md.
"""
import re
from collections import Counter, defaultdict

from ..util import atomic_write, read_jsonl, write_json


def _accepted(subject):
    acc = (subject.cfg.get("gaps") or {}).get("accepted") or {}
    if isinstance(acc, list):
        acc = {a: "" for a in acc}
    return {str(k).lower(): v for k, v in acc.items()}


def draft_entries(subject):
    """(chapter key, entry) for every drafted entry; part files of a split chapter are not drafts yet."""
    out = []
    if not subject.draft_dir.exists():
        return out
    for p in sorted(subject.draft_dir.glob("*.jsonl")):
        if re.search(r"\.part\d+\.jsonl$", p.name):
            continue
        out += [(p.stem, e) for e in read_jsonl(p)]
    return out


def collect(subject):
    """The gaps as data: {unresolved: [...], thin: [...], files: [...], accepted: n}."""
    drafts = draft_entries(subject)
    have = set()
    for _, e in drafts:
        have.add(str(e.get("title") or "").lower())
        if e.get("article"):
            have.add(str(e["article"]).lower())
        if e.get("id"):
            have.add(str(e["id"]).lower())
    accepted = _accepted(subject)
    names = defaultdict(lambda: {"n": 0, "chapters": Counter(), "by": []})
    for ck, e in drafts:
        for key in ("prerequisites", "related"):
            for p in e.get(key) or []:
                if str(p).lower() in have:
                    continue
                d = names[str(p)]
                d["n"] += 1
                d["chapters"][ck] += 1
                if len(d["by"]) < 3 and e["title"] not in d["by"]:
                    d["by"].append(e["title"])
    unresolved, n_accepted = [], 0
    for name, d in names.items():
        if name.lower() in accepted:
            n_accepted += 1
            continue
        unresolved.append({"name": name, "n": d["n"], "chapters": dict(d["chapters"].most_common()),
                           "suggest_chapter": d["chapters"].most_common(1)[0][0], "cited_by": d["by"]})
    unresolved.sort(key=lambda r: (-r["n"], r["name"]))
    thin = []
    for ck, e in drafts:
        note = str(e.get("notes") or "")
        if re.match(r"\s*thin\b", note, re.I):
            if str(e["title"]).lower() in accepted:
                n_accepted += 1
                continue
            thin.append({"title": e["title"], "chapter": ck, "kind": e.get("kind"), "note": note.strip()})
    files = []
    for p in sorted(subject.draft_dir.glob("*.gaps*.md")) if subject.draft_dir.exists() else []:
        bullets = [ln for ln in p.read_text(encoding="utf-8").splitlines() if ln.lstrip().startswith("- ")]
        files.append({"file": p.name, "bullets": len(bullets)})
    return {"unresolved": unresolved, "thin": thin, "files": files, "accepted": n_accepted}


def summary(subject):
    """(open unresolved names, open thin entries) without writing anything."""
    g = collect(subject)
    return len(g["unresolved"]), len(g["thin"])


def _probe(subject, names, log):
    """name -> (state, canonical title): state is exists, redirect, disambiguation or missing."""
    from ..crawl.api import WikiClient
    from ..crawl.store import Store
    store, client = Store(), WikiClient()
    out = {}
    for i in range(0, len(names), 50):
        batch = names[i:i + 50]
        resolved, meta = client.link_meta(batch)
        for frm, to in resolved.items():
            store.add_alias(frm, to)
        store.meta.update(meta)
        for n in batch:
            c = store.canonical(n)
            m = store.meta.get(c) or {}
            state = ("missing" if m.get("missing") else "disambiguation" if m.get("disambig")
                     else "redirect" if c != n else "exists")
            out[n] = (state, c)
    return out


def run(subject, probe=False, log=print):
    g = collect(subject)
    probed = _probe(subject, [r["name"] for r in g["unresolved"]], log) if probe and g["unresolved"] else {}
    L = [f"# Gaps: {subject.title}", "",
         f"{len(g['unresolved'])} unresolved names, {len(g['thin'])} thin entries, {len(g['files'])} gaps files"
         + (f"; {g['accepted']} accepted (subject.yaml `gaps: accepted:`)" if g["accepted"] else ""), ""]
    if g["unresolved"]:
        L += ["## Unresolved prerequisite and related names", "",
              "Named by entries, explained by none. Seed the page into the chapter that should teach it "
              "(`coursesmith frame add <subject> <chapter> \"<page>\"`), crawl, consolidate; or alias the name to an "
              "entry that exists; or accept it with a reason.", "",
              "| Name | Named | Cited by | Chapter (most citations) |" + (" Wikipedia |" if probed else ""),
              "|---|---:|---|---|" + ("---|" if probed else "")]
        for r in g["unresolved"]:
            row = f"| {r['name']} | {r['n']} | {', '.join(r['cited_by'])} | {r['suggest_chapter']} |"
            if probed:
                st, c = probed[r["name"]]
                row += f" {st}" + (f" as {c}" if st in ("redirect",) else "") + " |"
            L.append(row)
        L.append("")
    if g["thin"]:
        L += ["## Thin entries", "",
              "The sources held too little. Add pages to the chapter (`frame add`), find a richer vetted source "
              "(`sources discover`, guides/SOURCES_GUIDE.md), or accept it: a thin entry is better than a padded one.",
              "", "| Entry | Chapter | Kind | What is missing |", "|---|---|---|---|"]
        for t in g["thin"]:
            L.append(f"| {t['title']} | {t['chapter']} | {t['kind']} | {t['note'].removeprefix('thin:').strip()} |")
        L.append("")
    if g["files"]:
        L += ["## Gaps files", "", "Each pass listed the pages it expected and did not find, in "
              "`entries/draft/<chapter>.gaps.md`. Read the ones with many bullets when choosing seeds.", "",
              "| File | Bullets |", "|---|---:|"]
        L += [f"| {f['file']} | {f['bullets']} |" for f in sorted(g["files"], key=lambda f: -f["bullets"])]
        L.append("")
    if not (g["unresolved"] or g["thin"]):
        L.append("No open gaps.")
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "gaps.md", "\n".join(L) + "\n")
    write_json(subject.reports_dir / "gaps.json", {**g, "probe": {k: list(v) for k, v in probed.items()}})
    log(f"[gaps] {len(g['unresolved'])} unresolved names, {len(g['thin'])} thin entries, {len(g['files'])} gaps files"
        f" -> reports/gaps.md")
    return g
