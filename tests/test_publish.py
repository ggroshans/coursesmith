import tempfile
import unittest
import xml.dom.minidom
import zipfile
from pathlib import Path

from engine.publish import clock
from engine.publish.check import nums
from engine.publish.epub import Epub


class Clock(unittest.TestCase):
    def test_span(self):
        self.assertEqual(clock.fmt_span(538.8, 521), "539 to 521 million years ago")
        self.assertEqual(clock.fmt_age(0.0117), "11,700 years ago")
        self.assertEqual(clock.fmt_age(-6.1e-05), "2011 CE")

    def test_clock_line(self):
        self.assertIn("December 26", clock.clock_line(66.0, 66.0, 4567))
        self.assertIn("11:58:39 pm on December 31", clock.clock_line(0.0117, 0.0117, 4567))
        self.assertIn("between January 1 and January 6", clock.clock_line(4567, 4500, 4567))
        self.assertIn("last second", clock.clock_line(0.0001, 0.0001, 4567))


class Numbers(unittest.TestCase):
    def test_nums(self):
        self.assertEqual(nums("about 18.6 km³ and 5,550 years, 0.002 mm"), {18.6, 5550.0, 0.002})


class EpubWriter(unittest.TestCase):
    def test_structure(self):
        book = Epub("urn:uuid:00000000-0000-0000-0000-000000000000", "Test 1/2", "2026-01-01T00:00:00Z",
                    series="Test", series_index=1)
        book.add("css", "style.css", "text/css", "body{}")
        book.add_page("unit", "unit.xhtml", "Unit 1", "<h1>Unit 1</h1><p>Text &amp; more.</p>",
                      toc_children=[{"title": "Entry", "href": "unit.xhtml#e1"}])
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "t.epub"
            book.write(p)
            z = zipfile.ZipFile(p)
            names = z.namelist()
            self.assertEqual(names[0], "mimetype")
            self.assertEqual(z.getinfo("mimetype").compress_type, zipfile.ZIP_STORED)
            for n in names:
                if n.endswith((".xhtml", ".opf", ".ncx", ".xml")):
                    xml.dom.minidom.parseString(z.read(n))
            opf = z.read("OEBPS/content.opf").decode()
            self.assertIn('properties="nav"', opf)
            self.assertIn("calibre:series_index", opf)

    def test_reproducible(self):
        def build(path):
            b = Epub("urn:x", "T", "2026-01-01T00:00:00Z")
            b.add_page("p", "p.xhtml", "P", "<p>x</p>")
            b.write(path)
            return path.read_bytes()
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(build(Path(d) / "a.epub"), build(Path(d) / "b.epub"))


if __name__ == "__main__":
    unittest.main()
