"""Repo paths, the shared cache layout and crawler etiquette. Override via environment variables."""
import os
import warnings
from pathlib import Path

# urllib3 v2 warns on macOS's LibreSSL-built Python; harmless here.
warnings.filterwarnings("ignore", message=".*OpenSSL.*")

def env(name, default=""):
    """COURSESMITH_<name>, falling back to the old WIKICOURSE_<name> so existing shells keep working."""
    return os.environ.get(f"COURSESMITH_{name}") or os.environ.get(f"WIKICOURSE_{name}") or default


ROOT = Path(env("ROOT") or Path(__file__).resolve().parent.parent)

# Where courses live. The engine reads and writes subjects/<slug>/ under the workspace, which defaults to the
# engine checkout; point COURSESMITH_WORKSPACE (or --workspace) at any other folder, e.g. a repo of your courses.
WORKSPACE = Path(env("WORKSPACE") or ROOT).expanduser().resolve()
SUBJECTS = WORKSPACE / "subjects"
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
HUB_CACHE = CACHE / "hubs"
AUTHORITY_TEXT_DIR = CACHE / "authority_text"
WORKS_DIR = CACHE / "works"          # one JSON per DOI: metadata and abstract only
IMAGES_DIR = CACHE / "images"

# Vetted-source registry shared by every subject (domains and repos with default tiers and licenses).
REGISTRY_PATH = ROOT / "sources" / "registry.yaml"

BUILD = ROOT / "build"
EPUB_DIR = BUILD / "epubs"

# --- Wikipedia API -----------------------------------------------------------
API_URL = "https://en.wikipedia.org/w/api.php"
WIKI_BASE = "https://en.wikipedia.org/wiki/"
PAGEVIEWS_URL = "https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"


def contact():
    c = env("CONTACT").strip()
    if not c and (CACHE / "contact.txt").exists():
        c = (CACHE / "contact.txt").read_text(encoding="utf-8").strip()
    return c


CONTACT = contact()
USER_AGENT = (
    "coursesmith/0.1 "
    f"({'contact: ' + CONTACT if CONTACT else 'personal course builder, sequential, <=0.5 req/s'}) "
    "python-requests"
)

# Anonymous requests at 1 req/1.2 s tripped HTTP 429 on 2026-11-14, so the budget is <= 0.5 req/s.
MIN_INTERVAL_S = max(2.0, float(env("MIN_INTERVAL", "2.0")))
# Seconds between requests per host for the non-Wikipedia sources; any other host waits MIN_INTERVAL_S.
MIN_INTERVAL_BY_HOST = {
    "api.github.com": 1.0,
    "raw.githubusercontent.com": 1.0,
    "export.arxiv.org": 3.0,  # arXiv's terms: no more than one request every three seconds
}
MAXLAG = 5
MAX_RETRIES = 8
TIMEOUT_S = 60
