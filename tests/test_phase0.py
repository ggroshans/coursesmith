import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from engine.crawl.judge import _lead
from engine.subject import DEFAULTS, _merge


class FakeStore:
    def __init__(self, text):
        self.text = text

    def has_page(self, title):
        return True

    def load_text(self, title):
        return self.text


class JudgeLeadTest(unittest.TestCase):
    def test_lead_follows_title_line(self):
        store = FakeStore("# Soil\nSoil is a mixture of minerals and life. It feeds plants.\n\n## Uses\nMore.")
        self.assertEqual(_lead(store, "Soil"), "Soil is a mixture of minerals and life. It feeds plants.")

    def test_lead_after_blank_line(self):
        store = FakeStore("# Soil\n\nSoil is a mixture. Second sentence. Third.")
        self.assertEqual(_lead(store, "Soil"), "Soil is a mixture. Second sentence.")


class MergeTest(unittest.TestCase):
    def test_null_keeps_default_dict(self):
        cfg = _merge(DEFAULTS, {"scope": None, "title": "X"})
        self.assertEqual(cfg["scope"]["include_terms"], [])
        self.assertEqual(cfg["title"], "X")

    def test_does_not_share_defaults(self):
        cfg = _merge(DEFAULTS, {"scope": {"include_terms": ["a"]}})
        cfg["targets"]["per_unit"].append(9)
        cfg["scope"]["exclude_terms"].append("z")
        self.assertEqual(DEFAULTS["targets"]["per_unit"], [4, 5])
        self.assertEqual(DEFAULTS["scope"]["exclude_terms"], [])

    def test_nested_override(self):
        cfg = _merge(DEFAULTS, {"edition": {"questions": True}})
        self.assertTrue(cfg["edition"]["questions"])
        self.assertFalse(cfg["edition"]["images"])


class HttpCacheTest(unittest.TestCase):
    def test_cache_only_never_touches_network(self):
        from engine import config
        from engine.verify import extsrc
        with tempfile.TemporaryDirectory() as d:
            old = config.HTTP_CACHE
            config.HTTP_CACHE = Path(d)
            try:
                http = extsrc.PoliteHTTP()
                http.s = SimpleNamespace(get=lambda *a, **k: (_ for _ in ()).throw(AssertionError("network used")),
                                         headers={})
                self.assertIsNone(http.get("https://example.org/x", cache_only=True))
                self.assertEqual(http.get("https://example.org/x", cache_only=True, want_headers=True), (None, {}))
            finally:
                config.HTTP_CACHE = old


if __name__ == "__main__":
    unittest.main()
