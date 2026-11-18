"""coursesmith sources parts <subject> [SOURCE]: the page keys of a split file, to paste into frame.yaml.

A one-file course (a README with a chapter per heading) is split into a page per section by the GitHub source's
`split` option. This lists each section's key, title and size, so a chapter's `seeds:` can name the sections it
draws on."""
from .base import SourceError
from .registry import Registry


def run(subject, source=None, registry=None, log=print):
    registry = registry or Registry.from_subject(subject)
    n = 0
    for ad in registry.adapters:
        if ad.adapter != "github" or not getattr(ad, "split", None) or (source and ad.label != source):
            continue
        for path in ad.split:
            try:
                parts = ad.parts(path)
            except SourceError as e:
                log(f"  {ad.label} {path}: {e}")
                continue
            log(f"# {ad.label}: {path} at {ad.sha()[:7]}, {len(parts)} sections split at level {ad.split[path]}")
            for slug, title, md in parts:
                log(f"{ad.key(path, slug)} | {title} | {len(md.split())} words")
                n += 1
    if not n:
        log("no split sources" + (f" named '{source}'" if source else "") + " in subject.yaml")
    return n
