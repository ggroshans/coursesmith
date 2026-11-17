"""Repo paths, the shared cache layout and crawler etiquette. Override via environment variables."""
import os
import warnings
from pathlib import Path

# urllib3 v2 warns on macOS's LibreSSL-built Python; harmless here.
warnings.filterwarnings("ignore", message=".*OpenSSL.*")

ROOT = Path(os.environ.get("WIKICOURSE_ROOT") or Path(__file__).resolve().parent.parent)

SUBJECTS = ROOT / "subjects"
GUIDES = ROOT / "guides"

# Shared, gitignored cache. Pages are keyed by title + revid so subjects that overlap share fetches and a
# refresh can keep the old snapshot next to the new one.
CACHE = ROOT / "cache"
RAW_DIR = CACHE / "raw"              # raw/<slug>__<revid>.json
TEXT_DIR = CACHE / "text"            # text/<slug>__<revid>.txt
PAGES_INDEX = CACHE / "pages.json"   # canonical title -> current revid + file stem
ALIASES_PATH = CACHE / "aliases.json"
META_CACHE_PATH = CACHE / "link_meta.json"
SENT_DB = CACHE / "sentences.sqlite"
HTTP_CACHE = CACHE / "http"
WORKS_DIR = CACHE / "works"          # one JSON per DOI: metadata and abstract only
IMAGES_DIR = CACHE / "images"

BUILD = ROOT / "build"
EPUB_DIR = BUILD / "epubs"

# --- Wikipedia API -----------------------------------------------------------
API_URL = "https://en.wikipedia.org/w/api.php"
WIKI_BASE = "https://en.wikipedia.org/wiki/"
PAGEVIEWS_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"


def contact():
    c = os.environ.get("WIKICOURSE_CONTACT", "").strip()
    if not c and (CACHE / "contact.txt").exists():
        c = (CACHE / "contact.txt").read_text(encoding="utf-8").strip()
    return c


CONTACT = contact()
USER_AGENT = (
    "wikicourse/0.1 "
    f"({'contact: ' + CONTACT if CONTACT else 'personal course builder, sequential, <=0.5 req/s'}) "
    "python-requests"
)

# Anonymous requests at 1 req/1.2 s tripped HTTP 429 on 2026-11-14, so the budget is <= 0.5 req/s.
MIN_INTERVAL_S = max(2.0, float(os.environ.get("WIKICOURSE_MIN_INTERVAL", "2.0")))
MAXLAG = 5
MAX_RETRIES = 8
TIMEOUT_S = 60
