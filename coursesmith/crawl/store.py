"""Shared on-disk page cache, keyed by title + revid, plus the per-subject ledger.

cache/raw/<slug>__<revid>.json   title, url, revid, fetched_at, html, links, body_links, categories,
                                 hidden_categories, sections, citations, templates
cache/text/<slug>__<revid>.txt   cleaned plain text (see clean.py)
cache/pages.json                 canonical title -> {"revid", "stem"} for the current revision
cache/aliases.json               requested title -> canonical title
cache/link_meta.json             title -> categories, description, disambig, missing, qid (pre-screen)

Several subjects share one cache, so a page crawled for earth history is free for soil science. A refresh
writes the new revision next to the old one and repoints pages.json.
"""
import csv
import hashlib
import json
import re
import unicodedata
from urllib.parse import quote

from .. import config
from ..util import atomic_write, read_json

LEDGER_FIELDS = ["title", "url", "revid", "depth", "linked_from", "in_scope_reason", "score", "status"]
REJECTED_FIELDS = ["title", "linked_from", "depth", "score", "reasons"]


def slugify(title):
    """Readable ASCII slug plus a short hash of the exact title, so near-identical titles never collide."""
    ascii_ = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    base = re.sub(r"[^A-Za-z0-9]+", "_", ascii_).strip("_")[:80] or "page"
    return f"{base}__{hashlib.sha1(title.encode('utf-8')).hexdigest()[:6]}"


def page_url(title):
    return config.WIKI_BASE + quote(title.replace(" ", "_"), safe="()_,'-.:~!*")


class Store:
    def __init__(self):
        config.RAW_DIR.mkdir(parents=True, exist_ok=True)
        config.TEXT_DIR.mkdir(parents=True, exist_ok=True)
        self.aliases = read_json(config.ALIASES_PATH, {})
        self.meta = read_json(config.META_CACHE_PATH, {})
        self.pages = read_json(config.PAGES_INDEX, {})

    # -- titles ------------------------------------------------------------
    def canonical(self, title):
        seen = set()
        while title in self.aliases and title not in seen:
            seen.add(title)
            title = self.aliases[title]
        return title

    def add_alias(self, frm, to):
        if frm != to:
            self.aliases[frm] = to

    # -- pages -------------------------------------------------------------
    def _stem(self, title, revid):
        return f"{slugify(title)}__{revid}"

    def has_page(self, title):
        p = self.pages.get(self.canonical(title))
        return bool(p) and (config.RAW_DIR / f"{p['stem']}.json").exists()

    def revid(self, title):
        p = self.pages.get(self.canonical(title))
        return p["revid"] if p else None

    def save_page(self, rec, text):
        stem = self._stem(rec["title"], rec.get("revid"))
        atomic_write(config.RAW_DIR / f"{stem}.json", json.dumps(rec, ensure_ascii=False))
        atomic_write(config.TEXT_DIR / f"{stem}.txt", text)
        self.pages[rec["title"]] = {"revid": rec.get("revid"), "stem": stem}
        atomic_write(config.PAGES_INDEX, json.dumps(self.pages, ensure_ascii=False))

    def load_page(self, title):
        p = self.pages[self.canonical(title)]
        return json.loads((config.RAW_DIR / f"{p['stem']}.json").read_text(encoding="utf-8"))

    def load_text(self, title):
        p = self.pages[self.canonical(title)]
        return (config.TEXT_DIR / f"{p['stem']}.txt").read_text(encoding="utf-8")

    def titles(self):
        return list(self.pages)

    # -- caches ------------------------------------------------------------
    def flush_caches(self):
        atomic_write(config.ALIASES_PATH, json.dumps(self.aliases, ensure_ascii=False, indent=0))
        atomic_write(config.META_CACHE_PATH, json.dumps(self.meta, ensure_ascii=False))


# -- per-subject ledger ------------------------------------------------------
def _append_csv(path, fields, row):
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in fields})


def append_ledger(subject, row):
    _append_csv(subject.ledger_path, LEDGER_FIELDS, row)


def append_rejected(subject, row):
    _append_csv(subject.scope_dir / "frontier_rejected.csv", REJECTED_FIELDS, row)


def read_ledger(subject):
    if not subject.ledger_path.exists():
        return []
    with subject.ledger_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def crawled_titles(subject):
    """Distinct pages the subject has fetched or loaded from the cache, in ledger order."""
    seen, out = set(), []
    for r in read_ledger(subject):
        if r["status"].startswith(("fetched", "cached")) and r["title"] not in seen:
            seen.add(r["title"])
            out.append(r["title"])
    return out
