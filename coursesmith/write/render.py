"""Merge the writing passes' JSON batches into output/prose.json and render output/course.md.

Batch files live in work/write/ and are merged in name order; later files win for the same key:

    {"entries":   {id: {"title": "...", "text": "..."}},
     "openers":   {node_id: "3-5 sentences opening a part or chapter"},
     "reviews":   {node_id: "3-5 sentences closing a chapter, built only from its entries' facts"},
     "glossary":  {id: [{"term": "...", "text": "...", "sent_ids": ["..."]}]},
     "questions": {first_entry_id_of_unit: {"q": "...", "a": "...", "sent_ids": ["..."]}},
     "explain":   {id: {"terms":  [{"term": "...", "text": "...", "sent_ids": ["..."]}],
                        "blurbs": [{"heading": "...", "text": "...", "sent_ids": ["..."]}]}},   (explain mode)
     "closing":   "optional closing narrative after the last unit"}

Prose refers to other entries by id ({{ref:soil-chem-006}}), resolved to titles and unit numbers at publish
time, so reordering never breaks a cross-reference.
"""
import json
import re

from ..outline import Outline
from ..util import atomic_write, read_json, write_json

REF_RE = re.compile(r"\{\{ref:([a-z0-9-]+)\}\}")
KEYS = ("entries", "openers", "reviews", "glossary", "questions", "derived")


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
        for k, v in (d.get("explain") or {}).items():       # explain mode: a later file replaces an entry's items
            out.setdefault("explain", {})[k] = v
    for eid, v in (out.get("explain") or {}).items():
        v["terms"] = [_tidy_item(x) for x in v.get("terms") or []]
        v["blurbs"] = [_tidy_item(x) for x in v.get("blurbs") or []]
    keep_paras = bool(((getattr(subject, "cfg", None) or {}).get("edition") or {}).get("paragraphs"))
    kinds = None
    for eid, v in out["entries"].items():
        if isinstance(v.get("title"), str):
            v["title"] = re.sub(r"\s*\n\s*", " ", v["title"].strip())
        if isinstance(v.get("text"), str):
            if not keep_paras and "\n\n" in v["text"] and kinds is None:
                kinds = {e["id"]: e.get("kind") for e in subject.entries()}
            paragraphs = keep_paras or (kinds or {}).get(eid) in PARAGRAPH_KINDS
            v["text"] = tidy_text(v["text"], paragraphs)
    return out, files


def _tidy_item(x):
    """One explanation item with its strings on single lines and its sent_ids a list."""
    out = {k: re.sub(r"\s*\n\s*", " ", v.strip()) if isinstance(v, str) else v for k, v in dict(x).items()}
    out["sent_ids"] = [s for s in out.get("sent_ids") or [] if isinstance(s, str)]
    return out


# A worked answer or case study is long enough to need paragraphs. Every other entry is one paragraph unless the
# subject sets `edition.paragraphs: true`: courses written before paragraphs existed keep the look they were
# published with, even where a writer left a blank line in a batch.
PARAGRAPH_KINDS = ("Worked example", "Case study")


def tidy_text(text, paragraphs=True):
    """An entry's text. A single newline inside a block is only a wrapped line (it becomes a space). With
    `paragraphs`, a blank line starts a new paragraph; without, the whole text is one paragraph."""
    if not paragraphs:
        return re.sub(r"\s*\n\s*", " ", text.strip())
    paras = [re.sub(r"\s*\n\s*", " ", p.strip()) for p in re.split(r"\n\s*\n", text.strip())]
    return "\n\n".join(p for p in paras if p)


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
    from ..publish.figures import load as load_figures
    figs = load_figures(subject)
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
                  "", "  " + resolve_refs(p.get("text") or "{{TEXT:" + i + "}}", titles).replace("\n\n", "\n\n  "), "",
                  f"  <!-- {i} -->", ""]
        for fig in figs.get(i) or []:
            lines += _figure_md(fig)
        lines += _explain_md(prose, i, titles)
    if prose.get("closing"):
        lines += ["## Closing", "", prose["closing"], ""]
    subject.output_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.output_dir / "course.md", "\n".join(lines))
    log(f"[render] {len(files)} batch files -> {subject.prose_path.relative_to(subject.dir)}; "
        f"{len(order) - missing}/{len(order)} entries written, {len(prose['openers'])} openers, "
        f"{len(prose['reviews'])} reviews, {len(prose['questions'])} questions")
    return missing


def _explain_md(prose, eid, titles):
    """An entry's explanations in course.md: a definition per line, then each blurb as a quote."""
    from ..explain import items
    terms, blurbs = items(prose, eid)
    lines = []
    for t in terms:
        lines += [f"  > **{t.get('term')}**: {resolve_refs(t.get('text'), titles)}", ""]
    for b in blurbs:
        lines += [f"  > **{b.get('heading')}**", "  >", f"  > {resolve_refs(b.get('text'), titles)}", ""]
    return lines


def _figure_md(fig):
    """A figure in course.md: tables as tables, flows as Mermaid (GitHub draws it), the rest by caption."""
    cap = f"  *Figure: {fig.get('caption') or ''}*"
    if fig.get("type") == "table":
        rows = [fig.get("header") or [""] * len(fig["rows"][0])] + fig["rows"]
        md = ["  | " + " | ".join(str(c) for c in rows[0]) + " |", "  |" + "---|" * len(rows[0])]
        md += ["  | " + " | ".join(str(c) for c in r) + " |" for r in rows[1:]]
        return [cap, ""] + md + [""]
    if fig.get("type") == "flow":
        return [cap, "", "  ```mermaid"] + [f"  {ln}" for ln in fig["mermaid"].strip().splitlines()] + ["  ```", ""]
    return [cap + f" ({fig.get('type')}; drawn in the EPUB)", ""]


def load(subject):
    return read_json(subject.prose_path) or {k: {} for k in KEYS}
