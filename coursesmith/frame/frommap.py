"""frame from-map: frame.yaml for a one-source course from an ordered rule file, no scout crawl.

    coursesmith frame from-map <subject>          reads scope/frame_map.yaml, writes frame.yaml, reports/frame_map.md

A documentation repository already has its own structure, and every page is meant to be in the course. The map
says where each page goes. Parts and chapters are listed in reading order; a chapter lists glob patterns, and a
page goes to the first chapter (in file order) whose patterns match its path:

    source: dotnet-docs                  # the github source whose files are mapped
    parts:
      - key: start
        title: "Start here"
        chapters:
          - {key: what-is-dotnet, title: "What .NET is", include: ["docs/core/introduction.md"]}

A chapter may list `first:` patterns, pages that lead it (an overview before the details). Pages no chapter
matches are reported and left out, so a new page in the repository never goes missing silently. The chapters'
seeds are source keys, so `crawl` fetches exactly those pages.
"""
import yaml

from ..sources.base import glob_match
from ..util import atomic_write


def _rank(path, first):
    """Overviews first: the chapter's `first` pages, then index/overview files, then the rest by path."""
    f = next((k for k, g in enumerate(first) if glob_match(path, [g])), None)
    name = path.rsplit("/", 1)[-1]
    return (0, f, path) if f is not None else (1, 0, path) if name in ("index.md", "overview.md") else (2, 0, path)


def run(subject, log=print):
    from ..sources.registry import Registry
    path = subject.dir / "scope" / "frame_map.yaml"
    if not path.exists():
        raise SystemExit(f"{path.relative_to(subject.dir)} not found")
    spec = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    reg = Registry.from_subject(subject)
    adapter = next((a for a in reg.adapters if a.label == spec.get("source") or a.cfg.get("name") == spec.get("source")),
                   None)
    if adapter is None or not hasattr(adapter, "files"):
        raise SystemExit(f"source '{spec.get('source')}' is not a github source of this subject")
    files = adapter.files()
    chapters = [(p, c) for p in spec.get("parts") or [] for c in p.get("chapters") or []]
    got = {id(c): [] for _, c in chapters}
    left = []
    for f in files:
        hit = next((c for _, c in chapters if glob_match(f, c.get("include") or [])
                    and not glob_match(f, c.get("exclude") or [])), None)
        (got[id(hit)] if hit else left).append(f)
    parts = []
    for p in spec.get("parts") or []:
        chs = []
        for c in p.get("chapters") or []:
            pages = sorted(got[id(c)], key=lambda f: _rank(f, c.get("first") or []))
            if pages:
                chs.append({"key": c["key"], "title": c["title"], "seeds": [adapter.key(f) for f in pages]})
        if chs:
            parts.append({"key": p["key"], "title": p["title"], "chapters": chs})
    out = {"subject": subject.slug, "status": "built from scope/frame_map.yaml", "parts": parts}
    atomic_write(subject.dir / "frame.yaml", yaml.safe_dump(out, sort_keys=False, allow_unicode=True, width=120))
    L = [f"# Frame map: {subject.title}", "", f"{len(files) - len(left)} of {len(files)} pages placed; "
         f"{len(left)} matched no chapter.", ""]
    for p in parts:
        L.append(f"## {p['title']}")
        L += [f"- {c['title']}: {len(c['seeds'])}" for c in p["chapters"]]
        L.append("")
    if left:
        L += ["## Not placed", ""] + [f"- {f}" for f in left[:300]]
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "frame_map.md", "\n".join(L) + "\n")
    log(f"[frame] {len(files) - len(left)}/{len(files)} pages in {sum(len(p['chapters']) for p in parts)} chapters "
        f"of {len(parts)} parts; {len(left)} not placed -> frame.yaml, reports/frame_map.md")
    return left
