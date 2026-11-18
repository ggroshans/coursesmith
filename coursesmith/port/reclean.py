"""Re-clean cached pages after a cleaner fix and carry every citation over to the new sentence ids.

    coursesmith reclean <subject> [--pattern REGEX] [--dry-run]

For each crawled page of the subject whose raw HTML matches PATTERN, the text is re-cleaned from the cached HTML
(no network) and re-indexed. A sentence whose only change is the cleaner's fix keeps its citations: its old id is
mapped to its new id, and every file under subjects/ that cites the old id is rewritten. Sentences that changed in
other ways are listed for review.
"""
import json
import re

from .. import config
from ..crawl.clean import clean_html
from ..crawl.store import Store, crawled_titles
from ..extract import sentences as SN
from ..extract.split import clean_sentence, iter_sentences

POWERS_OF_TEN = r"10(?:</a>)?<sup(?![^>]*reference)"


def _sentences(title, text):
    out = []
    for section, raw, is_row in iter_sentences(text):
        plain, _, _ = clean_sentence(raw)
        if len(plain) >= 12:
            out.append((SN.sent_id(title, plain), plain))
    return out


def run(subject, pattern=POWERS_OF_TEN, dry_run=False, log=print):
    store, db = Store(), SN.connect()
    rx = re.compile(pattern)
    titles = [t for t in crawled_titles(subject) if store.has_page(t)]
    mapping, other, pages = {}, [], []
    for t in titles:
        rec = store.load_page(t)
        if not rx.search(rec.get("html") or ""):
            continue
        old = _sentences(rec["title"], store.load_text(t))
        text, _, _ = clean_html(rec["html"], rec["title"])
        new = _sentences(rec["title"], text)
        new_by_plain = {p.replace("^", ""): sid for sid, p in new}
        new_ids = {sid for sid, _ in new}
        for sid, plain in old:
            if sid in new_ids:
                continue
            hit = new_by_plain.get(plain)
            if hit:
                mapping[sid] = hit
            else:
                other.append((rec["title"], sid, plain))
        pages.append((rec, text))
    log(f"[reclean] {len(pages)} pages; {len(mapping)} sentences re-identified; {len(other)} changed otherwise")
    if dry_run:
        return mapping, other
    for rec, text in pages:
        store.save_page(rec, text)
        SN.index_page(db, store, rec, text)
    db.commit()
    n_files = 0
    if mapping:
        rx_id = re.compile("|".join(map(re.escape, mapping)))
        for p in config.SUBJECTS.rglob("*"):
            if not p.is_file() or p.suffix not in (".jsonl", ".json", ".md", ".csv", ".yaml"):
                continue
            if "/work/tmp/" in str(p) or "/work/dossiers/" in str(p):
                continue
            s = p.read_text(encoding="utf-8")
            t = rx_id.sub(lambda m: mapping[m.group(0)], s)
            if t != s:
                p.write_text(t, encoding="utf-8")
                n_files += 1
    out = subject.dir / "work" / "reclean.json"
    out.write_text(json.dumps({"mapping": mapping, "changed": other}, ensure_ascii=False, indent=0), encoding="utf-8")
    log(f"[reclean] rewrote citations in {n_files} files; details in {out}")
    return mapping, other
