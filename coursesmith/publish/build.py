"""publish build: every unit EPUB plus the complete-course EPUB, into build/epubs/<subject>/."""
import hashlib
import json

from .. import config
from ..util import now_iso, write_json
from .edition import Edition


def build(subject, units=None, complete=True, log=print):
    ed = Edition(subject)
    out_dir = config.EPUB_DIR / subject.slug
    out_dir.mkdir(parents=True, exist_ok=True)
    wanted = set(units or [])
    manifest = {"subject": subject.slug, "built": now_iso(), "units": {}, "complete": None}
    old = out_dir / "manifest.json"
    if wanted and old.exists():
        manifest["units"] = json.loads(old.read_text(encoding="utf-8")).get("units", {})
    sizes = []
    for u in ed.units:
        if wanted and u["n"] not in wanted:
            continue
        path, size = ed.build_unit(u, out_dir)
        sizes.append(size)
        manifest["units"][str(u["n"])] = {"file": path.name, "bytes": size, "title": ed.unit_title(u),
                                          "sha1": hashlib.sha1(path.read_bytes()).hexdigest()}
    if complete and not wanted:
        path, size = ed.build_complete(out_dir)
        manifest["complete"] = {"file": path.name, "bytes": size, "title": f"{subject.title} — the complete course",
                                "sha1": hashlib.sha1(path.read_bytes()).hexdigest()}
    write_json(old, manifest)
    if sizes:
        log(f"[publish] {len(sizes)} unit EPUBs in {out_dir.relative_to(config.ROOT)} "
            f"({min(sizes) // 1024}-{max(sizes) // 1024} KB)"
            + (f"; complete edition {manifest['complete']['bytes'] // 1024} KB" if manifest.get("complete") else ""))
    return manifest
