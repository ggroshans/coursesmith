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


def connect():
    config.SENT_DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(config.SENT_DB)
    db.executescript(SCHEMA)
    return db


def index_page(db, store, rec, text):
    """(Re)index one page revision. Returns the number of sentences written."""
    title = rec["title"]
    db.execute("DELETE FROM sentences WHERE title = ?", (title,))
    cits = {c["n"]: c for c in rec.get("citations", [])}
    pm = PageMentions(rec, store.canonical)
    rows, definition = [], None
    for i, (section, raw, is_row) in enumerate(iter_sentences(text)):
        plain, cites, tags = clean_sentence(raw)
        if len(plain) < 12:
            continue
        sid = sent_id(title, plain)
        is_lead = section == "(lead)"
        # the definition is the first real lead sentence: infobox titles ("Granulometry") sit in the lead too
        if definition is None and is_lead and not is_row and len(plain.split()) >= 6 and plain.endswith((".", ":")):
            definition = sid
        dois = sorted({w["doi"] for n in cites for w in cits.get(n, {}).get("works", []) if w.get("doi")})
        ds = [{k: d.get(k) for k in ("date_text", "date_ma", "young_ma", "kind")}
              for d in dates.find_dates(plain)] if any(ch.isdigit() for ch in plain) else []
        rows.append((sid, title, rec.get("revid"), section, i, plain, int(is_row), int(is_lead),
                     json.dumps(cites), json.dumps(dois), json.dumps(tags), json.dumps(pm(plain)),
                     json.dumps(cite_years(rec.get("citations"), cites)), json.dumps(ds) if ds else None))
    db.executemany("INSERT INTO sentences VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    qid = (store.meta.get(title) or {}).get("qid")
    db.execute("INSERT OR REPLACE INTO pages VALUES (?,?,?,?,?,?)",
               (title, rec["url"], rec.get("revid"), qid, definition, len(rows)))
    return len(rows)


def build(subject, store=None, force=False, log=print):
    store = store or Store()
    db = connect()
    have = dict(db.execute("SELECT title, revid FROM pages").fetchall())
    titles = crawled_titles(subject)
    n_pages = n_sent = 0
    for t in titles:
        if not store.has_page(t):
            continue
        rec = store.load_page(t)
        db.execute("INSERT OR IGNORE INTO subject_pages VALUES (?,?)", (subject.slug, rec["title"]))
        if not force and have.get(rec["title"]) == rec.get("revid"):
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
    """sent_id -> dict(title, url, revid, section, sentence, dois, links)."""
    out = {}
    q = ("SELECT s.sent_id, s.title, p.url, s.revid, s.section, s.sentence, s.dois, s.links, s.idx FROM sentences s "
         "JOIN pages p ON p.title = s.title WHERE s.sent_id = ?")
    for i in ids:
        row = db.execute(q, (i,)).fetchone()
        if row:
            out[row[0]] = {"title": row[1], "url": row[2], "revid": row[3], "section": row[4], "sentence": row[5],
                           "dois": json.loads(row[6] or "[]"), "links": json.loads(row[7] or "[]"), "idx": row[8]}
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
