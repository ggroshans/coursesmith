"""coursesmith status [subject]: where each subject stands, read from what is on disk.

Per subject: pipeline stage reached, pages crawled, sentences indexed, entries drafted/selected, coverage of
the hub lists, verification tiers, prose written, units built, and EPUBs built.
"""
import csv
from collections import Counter

from . import config
from .subject import all_slugs, load
from .util import read_json, read_jsonl

STAGES = ["frame", "crawl", "extract", "graph", "dossiers", "consolidate", "select", "order", "verify", "write",
          "units", "publish"]


def _ledger_count(s):
    if not s.ledger_path.exists():
        return 0
    with s.ledger_path.open(newline="", encoding="utf-8") as f:
        return len({r["title"] for r in csv.DictReader(f) if r["status"].startswith(("fetched", "cached"))})


def _sentences(s):
    if not config.SENT_DB.exists():
        return 0
    import sqlite3
    db = sqlite3.connect(config.SENT_DB)
    try:
        return db.execute("SELECT COUNT(*) FROM sentences x JOIN subject_pages p ON p.title = x.title "
                          "WHERE p.subject = ?", (s.slug,)).fetchone()[0]
    except sqlite3.OperationalError:
        return 0
    finally:
        db.close()


def subject_status(s):
    st = {"slug": s.slug, "title": s.title, "ordering": s.ordering}
    st["frame"] = s.frame_path.exists()
    st["sources"] = _sources(s)
    labels = s.scope_dir / "calibration.csv"
    if labels.exists():
        with labels.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        st["calibration"] = (sum(1 for r in rows if (r.get("label") or "").strip()), len(rows))
    st["pages"] = _ledger_count(s)
    st["sentences"] = _sentences(s)
    st["graph"] = s.graph_path.exists()
    st["dossiers"] = len(list(s.dossier_dir.glob("*/chunk_*.md"))) if s.dossier_dir.exists() else 0
    drafts = sum(len(read_jsonl(p)) for p in s.draft_dir.glob("*.jsonl")) if s.draft_dir.exists() else 0
    entries = s.entries()
    sel = [e for e in entries if e.get("selected")]
    st["entries"] = {"draft": drafts, "final": len(entries), "selected": len(sel)}
    order = s.order()
    st["order"] = {"n": len(order.get("order") or []), "locked": bool(order.get("locked"))}
    st["tiers"] = dict(Counter(e.get("source_tier") or "unverified" for e in sel))
    st["verified"] = sum(1 for e in sel if e.get("verification"))
    prose = read_json(s.prose_path) or {}
    st["written"] = sum(1 for e in sel if ((prose.get("entries") or {}).get(e["id"]) or {}).get("text"))
    if st["entries"]["draft"]:
        from .frame import gaps
        st["gaps"] = gaps.summary(s)
    cov = read_json(s.reports_dir / "coverage.json")
    if cov:
        st["coverage"] = cov.get("summary")
    units = s.units()
    st["units"] = units.get("n_units") or 0
    st["epubs"] = len(list((config.EPUB_DIR / s.slug).glob(f"{s.slug}-unit-*.epub")))
    st["stage"] = _stage(st)
    return st


def _sources(s):
    """None for a Wikipedia-only subject, else (how many other sources, whether `sources check` is current)."""
    from .sources import check
    others = [c for c in s.cfg.get("sources") or [] if c.get("adapter", "wikipedia") != "wikipedia" or c.get("api_url")]
    if not others:
        return None
    try:
        check.require_ok(s)
        ok = True
    except SystemExit:
        ok = False
    return len(others), ok


def _stage(st):
    if st["epubs"]:
        return "publish"
    if st["units"]:
        return "units"
    if st["written"]:
        return "write"
    if st["verified"]:
        return "verify"
    if st["order"]["n"]:
        return "order"
    if st["entries"]["selected"]:
        return "select"
    if st["entries"]["final"] or st["entries"]["draft"]:
        return "consolidate"
    if st["dossiers"]:
        return "dossiers"
    if st["graph"]:
        return "graph"
    if st["sentences"]:
        return "extract"
    if st["pages"]:
        return "crawl"
    if st["frame"]:
        return "frame"
    return "new"


def show(slug=None, log=print):
    slugs = [slug] if slug else all_slugs()
    for sl in slugs:
        st = subject_status(load(sl))
        e, o = st["entries"], st["order"]
        log(f"{st['title']} ({sl}, {st['ordering']}): stage {st['stage']}")
        if st.get("sources"):
            n, ok = st["sources"]
            log(f"  sources: Wikipedia + {n} other{'s' if n != 1 else ''}; "
                + ("checked" if ok else f"NOT CHECKED: run `coursesmith sources check {sl}`"))
        cal = f", calibration labeled {st['calibration'][0]}/{st['calibration'][1]}" if st.get("calibration") else ""
        log(f"  frame {'yes' if st['frame'] else 'no'}{cal}; pages {st['pages']:,}; sentences {st['sentences']:,}; "
            f"graph {'yes' if st['graph'] else 'no'}; dossier chunks {st['dossiers']}")
        log(f"  entries: {e['draft']} drafted, {e['final']} final, {e['selected']} selected; order {o['n']} "
            f"({'locked' if o['locked'] else 'not locked'})")
        if st.get("coverage"):
            log(f"  coverage: {st['coverage']}")
        if st.get("gaps") and any(st["gaps"]):
            log(f"  gaps: {st['gaps'][0]} unresolved names, {st['gaps'][1]} thin entries; "
                f"`coursesmith report gaps {sl}`")
        tiers = ", ".join(f"{k} {v}" for k, v in sorted(st["tiers"].items(), key=lambda kv: -kv[1])) or "-"
        log(f"  verification: {st['verified']} entries checked; tiers {tiers}")
        log(f"  written {st['written']}/{e['selected']}; units {st['units']}; EPUBs {st['epubs']}")
