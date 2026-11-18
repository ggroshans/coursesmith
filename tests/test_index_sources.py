import unittest

from coursesmith.crawl.store import Store
from coursesmith.extract import sentences as SN

from .helpers import temp_root

TEXT = ("# Doc\n## Intro\nA cache is a fast store of recently used data.\n"
        "The Cambrian period began 538.8 million years ago.\n")


def index(rec, text=TEXT):
    st = Store()
    st.save_page(rec, text)
    db = SN.connect()
    SN.index_page(db, st, rec, text)
    return db


class IndexSourcesTest(unittest.TestCase):
    def test_wikipedia_keeps_dates_and_strict_definition(self):
        with temp_root():
            db = index({"title": "Doc", "url": "u", "revid": 1, "html": "", "citations": []})
            dates = db.execute("SELECT dates FROM sentences WHERE sentence LIKE 'The Cambrian%'").fetchone()[0]
            self.assertIsNotNone(dates)
            self.assertIsNone(db.execute("SELECT definition_id FROM pages").fetchone()[0])  # no lead sentence

    def test_other_source_skips_dates_and_falls_back_for_definition(self):
        with temp_root():
            rec = {"title": "gh>o/r/doc.md", "url": "u", "revid": None, "version": "v1", "source": "primer",
                   "html": None, "citations": [], "meta": {}, "name": "Doc"}
            db = index(rec)
            self.assertIsNone(db.execute("SELECT dates FROM sentences WHERE sentence LIKE 'The Cambrian%'").fetchone()[0])
            sid = db.execute("SELECT definition_id FROM pages").fetchone()[0]
            self.assertEqual(SN.definition(db, "gh>o/r/doc.md")["text"], "A cache is a fast store of recently used data.")
            self.assertEqual(SN.lookup(db, [sid])[sid]["source"], "primer")

    def test_source_can_opt_in_to_dates(self):
        with temp_root():
            rec = {"title": "gh>o/r/doc.md", "url": "u", "revid": None, "version": "v1", "source": "geo",
                   "html": None, "citations": [], "meta": {"dates": True}}
            db = index(rec)
            self.assertIsNotNone(db.execute("SELECT dates FROM sentences WHERE sentence LIKE 'The Cambrian%'").fetchone()[0])

    def test_anchor_links_become_sentence_links(self):
        with temp_root():
            rec = {"title": "gh>o/r/doc.md", "url": "u", "revid": None, "version": "v1", "source": "primer",
                   "html": None, "citations": [], "anchors": {"fast store": "Cache (computing)", "recently used": "gh>o/r/doc.md"}}
            db = index(rec)
            links = db.execute("SELECT links FROM sentences WHERE sentence LIKE 'A cache%'").fetchone()[0]
            self.assertEqual(links, '["Cache (computing)"]')  # its own page is left out


if __name__ == "__main__":
    unittest.main()
