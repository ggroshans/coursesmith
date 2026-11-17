"""Merge the writing passes' JSON batches into output/prose.json and render output/course.md.

Batch files live in work/write/ and are merged in name order; later files win for the same key:

    {"entries":   {id: {"title": "...", "text": "..."}},
     "openers":   {node_id: "3-5 sentences opening a part or chapter"},
     "reviews":   {node_id: "3-5 sentences closing a chapter, built only from its entries' facts"},
     "glossary":  {id: [{"term": "...", "text": "...", "sent_ids": ["..."]}]},
     "questions": {first_entry_id_of_unit: {"q": "...", "a": "...", "sent_ids": ["..."]}},
     "closing":   "optional closing narrative after the last unit"}

Prose refers to other entries by id ({{ref:soil-chem-006}}), resolved to titles and unit numbers at publish
time, so reordering never breaks a cross-reference.
"""
import json
import re

from ..outline import Outline
from ..util import atomic_write, read_json, write_json

REF_RE = re.compile(r"\{\{ref:([a-z0-9-]+)\}\}")
KEYS = ("entries", "openers", "reviews", "glossary", "questions")


def merge(subject):
    out = {k: {} for k in KEYS}
    out["closing"] = None
    files = sorted(subject.write_dir.glob("fill*.json"))
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        for k, v in (d.get("entries") or {}).items():
            out["entries"].setdefault(k, {}).update({kk: vv for kk, vv in v.items() if vv})
        for k in KEYS[1:]:
            out[k].update(d.get(k) or {})
        out["closing"] = d.get("closing") or out["closing"]
    for v in out["entries"].values():
        for kk in ("title", "text"):
            if isinstance(v.get(kk), str):
                v[kk] = re.sub(r"\s*\n\s*", " ", v[kk].strip())
    return out, files


def resolve_refs(text, titles, units=None):
    """{{ref:id}} -> the entry's written title, plus '(Unit N)' when unit numbers are known."""
    def sub(m):
        i = m.group(1)
        t = titles.get(i, i)
        u = (units or {}).get(i)
        return f"{t} (Unit {u})" if u else t
    return REF_RE.sub(sub, text or "")


def render(subject, log=print):
    prose, files = merge(subject)
    write_json(subject.prose_path, prose)
    order = (subject.order() or {}).get("order") or [e["id"] for e in subject.entries(selected_only=True)]
    entries = subject.entries_by_id()
    outline = Outline.from_subject(subject)
    titles = {i: (prose["entries"].get(i) or {}).get("title") or entries[i]["title"] for i in order if i in entries}
    lines = [f"# {subject.title}", ""]
    seen_nodes = set()
    missing = 0
    for i in order:
        e = entries.get(i)
        if not e:
            continue
        for nid in outline.entry_path(e):
            if nid in seen_nodes:
                continue
            seen_nodes.add(nid)
            lvl = min(6, 1 + outline.nodes.get(nid, {}).get("level", 1))
            lines += [f"{'#' * lvl} {outline.title(nid)}", ""]
            if prose["openers"].get(nid):
                lines += [prose["openers"][nid], ""]
        p = prose["entries"].get(i) or {}
        if not p.get("text"):
            missing += 1
        lines += [f"- **{titles.get(i, e['title'])}**" + (f" — {e['date_display']}" if e.get("date_display") else ""),
                  "", f"  {resolve_refs(p.get('text') or '{{TEXT:' + i + '}}', titles)}", "",
                  f"  <!-- {i} -->", ""]
    if prose.get("closing"):
        lines += ["## Closing", "", prose["closing"], ""]
    subject.output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.output_dir / "course.md", "\n".join(lines))
    log(f"[render] {len(files)} batch files -> {subject.prose_path.relative_to(subject.dir)}; "
        f"{len(order) - missing}/{len(order)} entries written, {len(prose['openers'])} openers, "
        f"{len(prose['reviews'])} reviews, {len(prose['questions'])} questions")
    return missing


def load(subject):
    return read_json(subject.prose_path) or {k: {} for k in KEYS}
