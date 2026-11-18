import json
import sqlite3
import unittest

from coursesmith import config
from coursesmith.crawl import fetch as F
from coursesmith.crawl.store import Store, append_ledger, crawled_titles, read_ledger, slugify
from coursesmith.extract import sentences as SN
from coursesmith.sources.base import MissingSource, SourceError

from .fakes import FakeAdapter, FakeRegistry, FakeWikiClient, wiki_page
from .helpers import make_subject, temp_root

LEAD = "A network connects computers so that they can share data and services."


class StoreTest(unittest.TestCase):
    def test_wikipedia_record_keeps_old_layout(self):
        with temp_root():
            st = Store()
            st.save_page({"title": "Soil", "url": "u", "revid": 42}, "# Soil\n")
            entry = st.pages["Soil"]
            self.assertEqual(set(entry), {"revid", "stem"})
            self.assertTrue(entry["stem"].endswith("__42"))
            self.assertEqual(st.version("Soil"), "42")
            self.assertEqual(st.source("Soil"), "wikipedia")

    def test_non_wiki_record_uses_version_in_stem(self):
        with temp_root():
            st = Store()
            rec = {"title": "gh>o/r/README.md", "url": "u", "revid": None, "version": "ab12cd3-ef", "source": "primer"}
            st.save_page(rec, "# R\n")
            e = st.pages["gh>o/r/README.md"]
            self.assertTrue(e["stem"].endswith("__ab12cd3ef"))
            self.assertEqual((e["source"], e["version"]), ("primer", "ab12cd3-ef"))
            self.assertEqual(st.version("gh>o/r/README.md"), "ab12cd3-ef")
            self.assertEqual(st.source("gh>o/r/README.md"), "primer")
            self.assertTrue(st.has_page("gh>o/r/README.md"))
            self.assertEqual(st.load_text("gh>o/r/README.md"), "# R\n")

    def test_slug_never_collides_for_similar_keys(self):
        self.assertNotEqual(slugify("rfc>9110"), slugify("rfc_9110"))
        self.assertNotEqual(slugify("gh>a/b"), slugify("gh>a_b"))

    def test_old_pages_json_without_source_loads(self):
        with temp_root():
            config.CACHE.mkdir(parents=True)
            config.RAW_DIR.mkdir()
            config.TEXT_DIR.mkdir()
            config.PAGES_INDEX.write_text(json.dumps({"Soil": {"revid": 7, "stem": "Soil__x__7"}}))
            (config.RAW_DIR / "Soil__x__7.json").write_text(json.dumps({"title": "Soil", "revid": 7}))
            (config.TEXT_DIR / "Soil__x__7.txt").write_text("# Soil\n")
            st = Store()
            self.assertTrue(st.has_page("Soil"))
            self.assertEqual(st.version("Soil"), "7")
            self.assertEqual(st.source("Soil"), "wikipedia")
            self.assertEqual(st.revid("Soil"), 7)


class FetchDispatchTest(unittest.TestCase):
    def test_bare_title_goes_to_wikipedia_client(self):
        with temp_root():
            st, client = Store(), FakeWikiClient({"Soil": wiki_page("Soil", f"<div class='mw-parser-output'><p>{LEAD}</p></div>", 5)})
            rec, text, status = F.fetch_page(client, st, "Soil")
            self.assertEqual(status, "fetched")
            self.assertEqual(client.parsed, ["Soil"])
            self.assertEqual(rec["revid"], 5)
            self.assertNotIn("source", rec)  # Wikipedia records are unchanged
            _, _, again = F.fetch_page(client, st, "Soil")
            self.assertEqual(again, "cached")

    def test_qualified_key_goes_to_adapter(self):
        with temp_root():
            ad = FakeAdapter(pages={"fake>a/b.md": ("B doc", "# B\n" + LEAD, "v1", ["Soil"])})
            reg, st, client = FakeRegistry(ad), Store(), FakeWikiClient()
            rec, text, status = F.fetch_page(client, st, "fake>a/b.md", adapters=reg)
            self.assertEqual(status, "fetched")
            self.assertEqual(client.parsed, [])
            self.assertEqual(ad.fetched, ["fake>a/b.md"])
            self.assertNotIn("text", rec)
            self.assertEqual(text, "# B\n" + LEAD)
            self.assertEqual(st.version("fake>a/b.md"), "v1")
            self.assertEqual(rec["source"], "fake")
            self.assertEqual(rec["tier"], "curated")
            _, _, again = F.fetch_page(client, st, "fake>a/b.md", adapters=reg)
            self.assertEqual(again, "cached")
            self.assertEqual(ad.fetched, ["fake>a/b.md"])

    def test_qualified_key_without_registry_fails(self):
        with temp_root():
            with self.assertRaises(SourceError):
                F.fetch_page(FakeWikiClient(), Store(), "fake>a/b.md")

    def test_missing_adapter_page(self):
        with temp_root():
            with self.assertRaises(MissingSource):
                F.fetch_page(FakeWikiClient(), Store(), "fake>zzz", adapters=FakeRegistry(FakeAdapter()))

    def test_prescreen_skips_qualified_keys(self):
        with temp_root():
            client, st = FakeWikiClient(), Store()
            out = F.prescreen(client, st, ["Soil", "fake>a/b.md"])
            self.assertEqual(client.metaed, [["Soil"]])
            self.assertEqual(out["fake>a/b.md"], "fake>a/b.md")


class SentenceDbTest(unittest.TestCase):
    OLD_SCHEMA = """
    CREATE TABLE pages (title TEXT PRIMARY KEY, url TEXT, revid INTEGER, qid TEXT, definition_id TEXT, n_sentences INTEGER);
    CREATE TABLE sentences (sent_id TEXT, title TEXT, revid INTEGER, section TEXT, idx INTEGER, sentence TEXT,
        is_row INTEGER, is_lead INTEGER, cites TEXT, dois TEXT, tags TEXT, links TEXT, cite_years TEXT, dates TEXT);
    CREATE TABLE subject_pages (subject TEXT, title TEXT, PRIMARY KEY (subject, title));
    """

    def test_old_database_is_upgraded_in_place(self):
        with temp_root():
            config.CACHE.mkdir(parents=True)
            old = sqlite3.connect(config.SENT_DB)
            old.executescript(self.OLD_SCHEMA)
            old.execute("INSERT INTO pages VALUES ('Soil','u',9,'Q1','abc',1)")
            old.execute("INSERT INTO sentences VALUES ('abc','Soil',9,'(lead)',0,?,0,1,'[]','[]','[]','[]','[]',NULL)", (LEAD,))
            old.commit()
            old.close()
            db = SN.connect()
            cols = {r[1] for r in db.execute("PRAGMA table_info(pages)")}
            self.assertTrue({"source", "version", "license", "name"} <= cols)
            self.assertEqual(db.execute("SELECT title, revid, source FROM pages").fetchall(), [("Soil", 9, None)])
            hit = SN.lookup(db, ["abc"])["abc"]
            self.assertEqual((hit["source"], hit["version"], hit["name"], hit["license"]), ("wikipedia", "9", "Soil", None))
            SN.connect().close()  # migrating twice is a no-op

    def test_incremental_build_is_a_noop_for_wikipedia_and_reindexes_on_new_version(self):
        with temp_root():
            subj = make_subject()
            st = Store()
            st.save_page({"title": "Soil", "url": "u", "revid": 3, "html": "<p>x</p>", "citations": []},
                         f"# Soil\n{LEAD}\n")
            ad = FakeAdapter(pages={"fake>a/b.md": ("B doc", f"# B\n{LEAD}\n", "v1", [])})
            F.fetch_page(FakeWikiClient(), st, "fake>a/b.md", adapters=FakeRegistry(ad))
            for t in ("Soil", "fake>a/b.md"):
                append_ledger(subj, {"title": t, "url": "u", "status": "fetched"})
            logs = []
            SN.build(subj, st, log=logs.append)
            self.assertIn("indexed 2 new", logs[-1])
            logs.clear()
            SN.build(subj, st, log=logs.append)
            self.assertIn("indexed 0 new", logs[-1])
            db = SN.connect()
            row = db.execute("SELECT source, version, name FROM pages WHERE title = 'fake>a/b.md'").fetchone()
            self.assertEqual(row, ("fake", "v1", "B doc"))
            self.assertEqual(db.execute("SELECT source, version FROM pages WHERE title = 'Soil'").fetchone(), (None, None))
            # the sentence id formula is unchanged: sha1(key + newline + sentence)
            sid = SN.sent_id("fake>a/b.md", LEAD)
            self.assertIn(sid, SN.lookup(db, [sid]))
            db.close()
            ad.pages["fake>a/b.md"] = ("B doc", f"# B\n{LEAD} It is new.\n", "v2", [])
            F.fetch_page(FakeWikiClient(), st, "fake>a/b.md", force=True, adapters=FakeRegistry(ad))
            logs.clear()
            SN.build(subj, st, log=logs.append)
            self.assertIn("indexed 1 new", logs[-1])

    def test_crawled_titles_includes_qualified_keys(self):
        with temp_root():
            subj = make_subject()
            append_ledger(subj, {"title": "fake>a", "status": "fetched", "revid": "v1"})
            self.assertEqual(crawled_titles(subj), ["fake>a"])
            self.assertEqual(read_ledger(subj)[0]["revid"], "v1")


if __name__ == "__main__":
    unittest.main()
