"""The shared sentence index: every sentence of every crawled page, with the chronicle's sent_id.

sent_id = sha1(title + "\\n" + plain sentence)[:12], so unchanged sentences keep their ids across refreshes and
earth history's ids stay valid. One sqlite file (cache/sentences.sqlite) serves all subjects; each subject's
pages are listed in subject_pages.

Per sentence: section, position, plain text, footnote numbers, DOIs of the cited works, maintenance tags,
the articles it links to (mentions), publication years of its citations, any dates in it, and whether it is
a table/infobox row. Each page's first lead sentence is its definition.

    coursesmith extract <subject>              index the subject's crawled pages (incremental)
    coursesmith sent <subject> ID [ID ...]     look sentences up by id
    coursesmith ctx <subject> TITLE PHRASE     sentences around the first one containing PHRASE
    coursesmith search <subject> PHRASE        sentences containing PHRASE across the subject's pages
"""
import hashlib
import json
import sqlite3

from .. import config
from ..crawl.store import Store, crawled_titles
from . import dates
from .mentions import PageMentions, cite_years
from .split import clean_sentence, iter_sentences

SCHEMA = """
CREATE TABLE IF NOT EXISTS pages (title TEXT PRIMARY KEY, url TEXT, revid INTEGER, qid TEXT,
    definition_id TEXT, n_sentences INTEGER);
CREATE TABLE IF NOT EXISTS sentences (sent_id TEXT, title TEXT, revid INTEGER, section TEXT, idx INTEGER,
    sentence TEXT, is_row INTEGER, is_lead INTEGER, cites TEXT, dois TEXT, tags TEXT, links TEXT,
    cite_years TEXT, dates TEXT);
CREATE TABLE IF NOT EXISTS subject_pages (subject TEXT, title TEXT, PRIMARY KEY (subject, title));
CREATE INDEX IF NOT EXISTS s_id ON sentences (sent_id);
CREATE INDEX IF NOT EXISTS s_page ON sentences (title, idx);
"""


def sent_id(title, plain):
    return hashlib.sha1(f"{title}\n{plain}".encode()).hexdigest()[:12]


NEW_PAGE_COLUMNS = (("source", "TEXT"), ("version", "TEXT"), ("license", "TEXT"), ("name", "TEXT"))


def _migrate(db):
    """Add the columns other sources need to a database made before they existed. No rows change and no
    sent_id changes: sqlite adds a nullable column without rewriting the table."""
    have = {r[1] for r in db.execute("PRAGMA table_info(pages)")}
    for col, typ in NEW_PAGE_COLUMNS:
        if col not in have:
            db.execute(f"ALTER TABLE pages ADD COLUMN {col} {typ}")


def connect():
    config.SENT_DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(config.SENT_DB)
    db.executescript(SCHEMA)
    _migrate(db)
    return db


def index_page(db, store, rec, text):
    """(Re)index one page revision. Returns the number of sentences written."""
    title = rec["title"]
    db.execute("DELETE FROM sentences WHERE title = ?", (title,))
    cits = {c["n"]: c for c in rec.get("citations", [])}
    pm = PageMentions(rec, store.canonical)
    rows, definition, fallback = [], None, None
    # other sources are technical text: AD/BP/CE and "Ma" readings are only for Wikipedia (or a source that asks)
    use_dates = not rec.get("source") or bool((rec.get("meta") or {}).get("dates"))
    for i, (section, raw, is_row) in enumerate(iter_sentences(text)):
        plain, cites, tags = clean_sentence(raw)
        if len(plain) < 12:
            continue
        sid = sent_id(title, plain)
        is_lead = section == "(lead)"
        # the definition is the first real lead sentence: infobox titles ("Granulometry") sit in the lead too
        if definition is None and is_lead and not is_row and len(plain.split()) >= 6 and plain.endswith((".", ":")):
            definition = sid
        if fallback is None and not is_row and len(plain.split()) >= 6 and plain.endswith((".", ":")):
            fallback = sid
        dois = sorted({w["doi"] for n in cites for w in cits.get(n, {}).get("works", []) if w.get("doi")})
        ds = [{k: d.get(k) for k in ("date_text", "date_ma", "young_ma", "kind")}
              for d in dates.find_dates(plain)] if use_dates and any(ch.isdigit() for ch in plain) else []
        rows.append((sid, title, rec.get("revid"), section, i, plain, int(is_row), int(is_lead),
                     json.dumps(cites), json.dumps(dois), json.dumps(tags), json.dumps(pm(plain)),
                     json.dumps(cite_years(rec.get("citations"), cites)), json.dumps(ds) if ds else None))
    if definition is None and rec.get("source"):
        definition = fallback  # a README or spec has no encyclopedia lead; its first prose sentence defines it
    db.executemany("INSERT INTO sentences VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    qid = (store.meta.get(title) or {}).get("qid")
    lic = rec.get("license")
    db.execute("INSERT OR REPLACE INTO pages (title, url, revid, qid, definition_id, n_sentences, source, version, "
               "license, name) VALUES (?,?,?,?,?,?,?,?,?,?)",
               (title, rec["url"], rec.get("revid"), qid, definition, len(rows), rec.get("source"),
                rec.get("version"), json.dumps(lic) if lic else None, rec.get("name")))
    return len(rows)


def build(subject, store=None, force=False, log=print):
    store = store or Store()
    db = connect()
    have = {t: (r, v) for t, r, v in db.execute("SELECT title, revid, version FROM pages")}
    titles = crawled_titles(subject)
    n_pages = n_sent = 0
    for t in titles:
        if not store.has_page(t):
            continue
        rec = store.load_page(t)
        db.execute("INSERT OR IGNORE INTO subject_pages VALUES (?,?)", (subject.slug, rec["title"]))
        if not force and have.get(rec["title"]) == (rec.get("revid"), rec.get("version")):
            continue
        n_sent += index_page(db, store, rec, store.load_text(t))
        n_pages += 1
    db.commit()
    total = db.execute("SELECT COUNT(*) FROM sentences s JOIN subject_pages p ON p.title = s.title "
                       "WHERE p.subject = ?", (subject.slug,)).fetchone()[0]
    db.close()
    log(f"[extract] indexed {n_pages} new page revisions ({n_sent:,} sentences); "
        f"{subject.slug}: {len(titles)} pages, {total:,} sentences")
    return total


def lookup(db, ids):
    """sent_id -> dict(title, url, revid, section, sentence, dois, links, idx, source, version, license, name).
    `title` is the page key. Pages indexed before other sources existed read as source "wikipedia", version =
    the revision id, license None (the registry knows Wikipedia's)."""
    out = {}
    q = ("SELECT s.sent_id, s.title, p.url, s.revid, s.section, s.sentence, s.dois, s.links, s.idx, "
         "p.source, p.version, p.license, p.name FROM sentences s "
         "JOIN pages p ON p.title = s.title WHERE s.sent_id = ?")
    for i in ids:
        row = db.execute(q, (i,)).fetchone()
        if row:
            out[row[0]] = {"title": row[1], "url": row[2], "revid": row[3], "section": row[4], "sentence": row[5],
                           "dois": json.loads(row[6] or "[]"), "links": json.loads(row[7] or "[]"), "idx": row[8],
                           "source": row[9] or "wikipedia",
                           "version": row[10] or (str(row[3]) if row[3] is not None else None),
                           "license": json.loads(row[11]) if row[11] else None, "name": row[12] or row[1]}
    return out


def context(db, title, phrase, n=6):
    rows = db.execute("SELECT idx, sent_id, section, sentence FROM sentences WHERE title = ? ORDER BY idx",
                      (title,)).fetchall()
    hit = next((k for k, r in enumerate(rows) if phrase.lower() in r[3].lower()), None)
    if hit is None:
        return []
    return rows[max(0, hit - n):hit + n + 1]


def search(db, subject_slug, phrase, limit=40):
    return db.execute(
        "SELECT s.sent_id, s.title, s.section, s.sentence FROM sentences s JOIN subject_pages p "
        "ON p.title = s.title WHERE p.subject = ? AND s.sentence LIKE ? LIMIT ?",
        (subject_slug, f"%{phrase}%", limit)).fetchall()


def page_sentences(db, title):
    return db.execute("SELECT sent_id, section, idx, sentence, is_row, is_lead, links, dates FROM sentences "
                      "WHERE title = ? ORDER BY idx", (title,)).fetchall()


def sections(db, title):
    """[(section, n_sentences)] in page order."""
    out = []
    for (section,) in db.execute("SELECT section FROM sentences WHERE title = ? ORDER BY idx", (title,)):
        if out and out[-1][0] == section:
            out[-1][1] += 1
        else:
            out.append([section, 1])
    return [tuple(x) for x in out]


def definition(db, title):
    row = db.execute("SELECT s.sent_id, s.sentence FROM pages p JOIN sentences s ON s.sent_id = p.definition_id "
                     "WHERE p.title = ?", (title,)).fetchone()
    return {"sent_id": row[0], "text": row[1]} if row else None
