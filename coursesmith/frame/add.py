"""frame add: put pages into a chapter's seeds, the mechanical half of a gap-fill.

    coursesmith frame add <subject> <chapter> <page-or-key>... [--also]

A gap-fill (guides/GAPFILL_GUIDE.md) starts by naming the pages a chapter is missing. This writes them into
frame.yaml, and into the `frame:` section of subject.yaml when the subject has a hand-written one (a later
`frame build` regenerates frame.yaml from it, so the pages would be lost otherwise). `--also` adds them as
context pages (`also:`) instead of seeds.

A page belongs to one chapter. One that any chapter already lists is skipped and reported, with where it is.
"""
import json
import re

import yaml

from ..crawl.store import Store
from ..util import atomic_write
from ..sources.keys import is_qualified

LISTS = ("seeds", "also")


def _find(parts, chapter):
    """(part, chapter) whose key or title is `chapter` (case-insensitive), or None."""
    want = chapter.strip().lower()
    for p in parts:
        for c in p.get("chapters") or []:
            if want in ((c.get("key") or "").lower(), (c.get("title") or "").lower()):
                return p, c
    return None


def _where(parts, canon):
    """page -> chapter title for every page a chapter lists, under its canonical Wikipedia title."""
    out = {}
    for p in parts:
        for c in p.get("chapters") or []:
            for k in LISTS + ("candidates",):
                for t in c.get(k) or []:
                    out.setdefault(t if is_qualified(t) else canon(t), c["title"])
    return out


def _patch_subject_yaml(subject, chapter_title, which, pages):
    """Append to the chapter's `seeds: [...]` / `also: [...]` flow list in subject.yaml's `frame:` section.
    Returns True when the file was changed. Only the one list line is rewritten, so comments stay."""
    path = subject.dir / "subject.yaml"
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    head = re.compile(r"^(\s*)- title:\s*(.+?)\s*$")
    start = None
    for i, ln in enumerate(lines):
        m = head.match(ln)
        if m and str(yaml.safe_load(m.group(2))) == chapter_title and any(
                l.startswith("frame:") for l in lines[:i]):
            start = i
            break
    if start is None:
        return False
    indent = len(head.match(lines[start]).group(1))
    flow = re.compile(rf"^(\s*){which}:\s*(\[.*\])(\s+#.*)?\s*$")
    anyform = re.compile(rf"^(\s*){which}:")
    for j in range(start + 1, len(lines)):
        ln = lines[j]
        h = head.match(ln)
        if h and len(h.group(1)) <= indent:
            break  # the next chapter
        m = flow.match(ln)
        if m:
            cur = yaml.safe_load(m.group(2)) or []
            new = cur + [p for p in pages if p not in cur]
            items = ", ".join(json.dumps(x, ensure_ascii=False) for x in new)
            lines[j] = f"{m.group(1)}{which}: [{items}]{m.group(3) or ''}\n"
            atomic_write(path, "".join(lines))
            return True
        if anyform.match(ln):
            return False  # a block-style list: leave subject.yaml alone rather than guess
    # the chapter has no such list yet: add one after its title line
    items = ", ".join(json.dumps(x, ensure_ascii=False) for x in pages)
    pad = " " * (indent + 2)
    lines.insert(start + 1, f"{pad}{which}: [{items}]\n")
    atomic_write(path, "".join(lines))
    return True


def run(subject, chapter, pages, also=False, store=None, log=print):
    frame = subject.frame
    parts = frame.get("parts") or []
    hit = _find(parts, chapter)
    if not hit:
        names = ", ".join(c.get("key") or c["title"] for p in parts for c in p.get("chapters") or [])
        raise SystemExit(f"no chapter '{chapter}' in {subject.frame_path.name}; chapters: {names}")
    _, ch = hit
    store = store or Store()
    where = _where(parts, store.canonical)
    which = "also" if also else "seeds"
    added, skipped = [], []
    for raw in pages:
        page = raw.strip()
        if not page:
            continue
        if not is_qualified(page):
            page = store.canonical(page)
        if page in where:
            skipped.append((page, where[page]))
            continue
        where[page] = ch["title"]
        added.append(page)
    if added:
        ch.setdefault(which, []).extend(added)
        doc = {k: v for k, v in frame.items()}
        atomic_write(subject.frame_path, yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=110))
        mirrored = _patch_subject_yaml(subject, ch["title"], which, added)
        if not mirrored and (subject.cfg.get("frame") or {}).get("parts"):
            log("  note: could not edit the chapter's list in subject.yaml (not a one-line list); add the pages there "
                "too or the next `frame build` drops them")
        subject.__dict__.pop("frame", None)
    else:
        mirrored = False
    for page, ck in skipped:
        log(f"  skipped {page}: already in '{ck}'")
    log(f"[frame] {ch['title']}: added {len(added)} {which}"
        + (" (also in subject.yaml)" if mirrored else "") + (f", skipped {len(skipped)}" if skipped else ""))
    return added, skipped
