"""coursesmith export: one self-contained course.json for any renderer (web app, flashcards, EPUB, search).

    coursesmith export <subject> [--out PATH] [--images] [--strict]

The file holds the course in reading order: the outline, every selected entry with its facts, citations and
written prose (refs resolved to plain titles, and kept raw for renderers that link them), units, glossary,
questions, and the text of every cited Wikipedia sentence with its page, URL and revision, so nothing needs
the engine's cache to read. `docs/OUTPUT.md` documents the format.
"""
import shutil

from .. import __version__, config
from ..extract import sentences as SN
from . import attribution as A
from ..outline import Outline
from ..util import now_iso, read_json, read_jsonl, write_json
from ..write.render import load as load_prose
from ..write.render import resolve_refs

FORMAT = "wikicourse-course"  # a wire id readers match on; it stays when the tool is renamed
VERSION = 2  # 2 adds license.sources, per-source fields on pages/sources/sentences, subject.distribution
# working fields of the build that mean nothing to a reader
INTERNAL = {"selected", "score", "score_parts", "curriculum", "notes", "prerequisites_draft", "prerequisite_sources",
            "wants_image", "flags", "selection_note", "exclude", "mention_sent_ids", "origin", "_file"}


class ExportError(RuntimeError):
    pass


def _cited(e):
    ids = list((e.get("definition") or {}).get("sent_ids") or [])
    for k in ("facts", "events"):
        for f in e.get(k) or []:
            ids += f.get("sent_ids") or []
    return ids


def _wiki_permalink(url, revid):
    title = url.rsplit("/wiki/", 1)[-1] if url else ""
    return f"https://en.wikipedia.org/w/index.php?title={title}&oldid={revid}" if title and revid else url


def _page_record(row):
    """`license.pages[key]`: url, revid and permalink as before, plus what a reader needs for another source."""
    return {"url": row["url"], "revid": row["revid"], "permalink": row["permalink"], "name": row["name"],
            "source": row["source"], "version": row["version"], "version_label": row["version_label"],
            "license": row["license"].get("name"), "license_class": row["license_class"], "tier": row["tier"]}


def export(subject, out=None, images=False, strict=False, log=print):
    order = (subject.order() or {}).get("order") or []
    if not order:
        raise ExportError("no order.json; run `coursesmith order build` first")
    by_id = subject.entries_by_id()
    prose = load_prose(subject)
    units_doc = subject.units() or {}
    unit_of = {i: u["n"] for u in units_doc.get("units") or [] for i in u["entries"]}
    titles = {i: (prose["entries"].get(i) or {}).get("title") or by_id[i]["title"] for i in order if i in by_id}
    outline = Outline.from_subject(subject)

    entries, cited = [], []
    registry = A.course_registry(subject)
    from .figures import load as load_figures
    figs = load_figures(subject)
    for i in order:
        e = by_id.get(i)
        if not e:
            continue
        rec = {k: v for k, v in e.items() if k not in INTERNAL}
        rec["path"] = outline.entry_path(e)
        p = prose["entries"].get(i) or {}
        rec["title"] = titles[i]
        rec["text"] = p.get("text") or None
        rec["text_plain"] = resolve_refs(p.get("text") or "", titles) or None
        rec["figures"] = figs.get(i) or []
        rec["sources"] = [A.norm_source(s) for s in e.get("sources") or []]
        entries.append(rec)
        cited += _cited(e)
    from ..crawl.store import Store
    rows = A.source_rows([e for e in (by_id.get(i) for i in order) if e], registry, Store())
    pages = {r["key"]: _page_record(r) for r in rows}
    summary = A.summarize(rows, registry, subject.cfg.get("distribution") or "personal")

    glossary = (read_json(subject.glossary_path) or {}).get("terms", {})
    for t in glossary.values():
        cited += t.get("sent_ids") or []
    for q in prose["questions"].values():
        cited += (q or {}).get("sent_ids") or []
    cited = list(dict.fromkeys(cited))

    sentences = {}
    if config.SENT_DB.exists():
        db = SN.connect()
        try:
            for sid, r in SN.lookup(db, cited).items():
                sentences[sid] = {"title": r["title"], "url": r["url"], "revid": r["revid"],
                                  "section": r["section"], "sentence": r["sentence"],
                                  "key": r["title"], "source": r["source"], "version": r["version"]}
        finally:
            db.close()
    # a subject ported from elsewhere may carry a frozen copy of its cited sentences (subjects/<slug>/sentences.jsonl)
    frozen = subject.dir / "sentences.jsonl"
    if frozen.exists():
        for r in read_jsonl(frozen):
            if r["sent_id"] not in sentences:
                sentences[r["sent_id"]] = {k: r.get(k) for k in ("title", "url", "revid", "section", "sentence")}
    missing = [s for s in cited if s not in sentences]
    if strict and missing:
        raise ExportError(f"{len(missing)} cited sentences are not in the sentence index, e.g. {missing[:5]}")

    used = {n for e in entries for n in e["path"]}
    nodes = [dict(outline.nodes[n], id=n) for n in outline.order if n in used]
    for n in nodes:
        n.pop("seeds", None)
        n.pop("share", None)

    img_records = {e["id"]: e["image"] for e in entries if e.get("image")}
    doc = {
        "format": FORMAT, "version": VERSION, "built": now_iso(), "wikicourse": __version__,
        "subject": {"slug": subject.slug, "title": subject.title, "description": subject.cfg.get("description"),
                    "ordering": subject.ordering, "per_unit": subject.targets.get("per_unit"),
                    "distribution": subject.cfg.get("distribution") or "personal",
                    "course_type": subject.cfg.get("course_type") or "survey",
                    "kinds": sorted({e.get("kind") for e in entries if e.get("kind")})},
        "license": {"name": summary["name"], "url": summary["url"], "text": summary["text"], "pages": pages,
                    "sources": [dict(_page_record(r), key=r["key"], n_sentences=r["n_sentences"],
                                     retrieved=r["retrieved"]) for r in rows],
                    "images": {i: {k: r.get(k) for k in ("file", "license", "license_url", "artist", "page_url")}
                               for i, r in img_records.items()}},
        "outline": nodes,
        "openers": prose["openers"], "reviews": prose["reviews"], "closing": prose.get("closing"),
        "entries": entries,
        "units": units_doc.get("units") or [],
        "glossary": glossary,
        "questions": prose["questions"],
        "sentences": sentences,
        "missing_sentences": missing,
    }
    out = out or subject.output_dir / "course.json"
    write_json(out, doc)
    if images and img_records:
        d = out.parent / "images"
        d.mkdir(parents=True, exist_ok=True)
        n = 0
        for r in img_records.values():
            src = config.IMAGES_DIR / (r.get("local") or "")
            if r.get("local") and src.exists():
                shutil.copy2(src, d / r["local"])
                n += 1
        log(f"[export] copied {n} images to {d}")
    log(f"[export] {len(entries)} entries, {len(doc['units'])} units, {len(sentences):,} cited sentences"
        f"{f', {len(missing)} not in the index' if missing else ''} -> {out}")
    return doc
