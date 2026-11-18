"""Test helpers: run code against a throwaway cache and subjects folder without a subprocess."""
import contextlib
import tempfile
from pathlib import Path

from coursesmith import config

PATHS = ["CACHE", "RAW_DIR", "TEXT_DIR", "PAGES_INDEX", "ALIASES_PATH", "META_CACHE_PATH", "SENT_DB",
         "HTTP_CACHE", "HUB_CACHE", "AUTHORITY_TEXT_DIR", "WORKS_DIR", "IMAGES_DIR", "SUBJECTS", "REGISTRY_PATH",
         "BUILD", "EPUB_DIR"]


@contextlib.contextmanager
def temp_root():
    """Point every config path at a fresh temp directory for the duration of the block."""
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        old = {k: getattr(config, k) for k in PATHS}
        config.CACHE = root / "cache"
        config.RAW_DIR = config.CACHE / "raw"
        config.TEXT_DIR = config.CACHE / "text"
        config.PAGES_INDEX = config.CACHE / "pages.json"
        config.ALIASES_PATH = config.CACHE / "aliases.json"
        config.META_CACHE_PATH = config.CACHE / "link_meta.json"
        config.SENT_DB = config.CACHE / "sentences.sqlite"
        config.HTTP_CACHE = config.CACHE / "http"
        config.HUB_CACHE = config.CACHE / "hubs"
        config.AUTHORITY_TEXT_DIR = config.CACHE / "authority_text"
        config.WORKS_DIR = config.CACHE / "works"
        config.IMAGES_DIR = config.CACHE / "images"
        config.SUBJECTS = root / "subjects"
        config.REGISTRY_PATH = root / "sources" / "registry.yaml"
        config.BUILD = root / "build"
        config.EPUB_DIR = config.BUILD / "epubs"
        try:
            yield root
        finally:
            for k, v in old.items():
                setattr(config, k, v)


def make_subject(slug="tiny", yaml_text=None):
    """Write subjects/<slug>/subject.yaml under the current (temp) config and load it."""
    from coursesmith.subject import load
    d = config.SUBJECTS / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "subject.yaml").write_text(yaml_text or f"slug: {slug}\ntitle: Tiny\n", encoding="utf-8")
    return load(slug)
