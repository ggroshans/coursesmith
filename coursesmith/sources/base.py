"""The source adapter interface.

An adapter turns one kind of vetted source (Wikipedia, a GitHub repository, an IETF RFC, a docs site, a PDF, a
paper) into page records the rest of the pipeline already understands: a key, cleaned text in the shape
`crawl/clean.py` produces, links to other keys, and citations. Everything after the sentence index is
source-agnostic.

A subject lists its sources in subject.yaml (`sources:`); `registry.Registry` builds one adapter per entry and
layers the shared defaults from sources/registry.yaml underneath. The crawl never fetches a key that no adapter
owns and allows.
"""
import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from . import licenses

# Trust tiers, best first. A fact from a better tier wins when sources disagree (CONSOLIDATION_GUIDE).
TIERS = ["official", "standard", "primary", "reference", "curated", "commentary"]


def tier_rank(tier):
    return TIERS.index(tier) if tier in TIERS else len(TIERS)


def best_tier(tiers):
    ts = [t for t in tiers if t]
    return min(ts, key=tier_rank) if ts else None


class SourceError(RuntimeError):
    """A fetch failed for a reason that may pass (network, quota, a bad response)."""


class MissingSource(SourceError):
    """The page does not exist or is not available."""


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _glob_regex(pat):
    """`**/` is zero or more directories, `**` anything, `*` anything but a slash, `?` one character."""
    out, i = "", 0
    while i < len(pat):
        if pat.startswith("**/", i):
            out += "(?:.*/)?"
            i += 3
        elif pat.startswith("**", i):
            out += ".*"
            i += 2
        elif pat[i] == "*":
            out += "[^/]*"
            i += 1
        elif pat[i] == "?":
            out += "[^/]"
            i += 1
        else:
            out += re.escape(pat[i])
            i += 1
    return re.compile(out + r"\Z")


def glob_match(path, patterns):
    return any(_glob_regex(p).match(path) for p in patterns or [])


class SourceAdapter:
    adapter = ""            # the `adapter:` value in subject.yaml
    prefix = ""             # key prefix; "" means bare Wikipedia titles
    default_tier = "reference"
    default_license = None  # {name, url, class}
    default_depth = 1       # link hops followed from a seed inside this source

    def __init__(self, cfg=None, http=None, defaults=None):
        self.cfg = dict(cfg or {})
        self.defaults = dict(defaults or {})  # shared registry entry: {tier, license, ...}
        self._http = http

    # -- identity and policy -----------------------------------------------------
    @property
    def label(self):
        """The name this source goes by in subject.yaml, ledgers and the attribution page."""
        return self.cfg.get("name") or self.adapter

    @property
    def tier(self):
        return self.cfg.get("tier") or self.defaults.get("tier") or self.default_tier

    @property
    def license(self):
        return licenses.normalize(self.cfg.get("license") or self.defaults.get("license"),
                                  self.default_license) or {"name": "", "url": "", "class": "unknown"}

    @property
    def max_depth(self):
        d = self.cfg.get("depth")
        return self.default_depth if d is None else int(d)

    @property
    def http(self):
        if self._http is None:
            from ..verify import extsrc
            self._http = extsrc.HTTP
        return self._http

    def hosts(self):
        """Hostnames this adapter fetches from; the shared registry matches its domain entries on these."""
        base = self.cfg.get("base")
        return [urlparse(base).netloc] if base else []

    # -- keys --------------------------------------------------------------------
    def owns(self, key):
        raise NotImplementedError

    def allowed(self, key):
        """True when the key is inside this source's allowlist. The default is simply ownership."""
        return self.owns(key)

    def key_for_url(self, url, base_key=None):
        """The key a link or URL points at, or None when it is not this source's."""
        return None

    def canonical(self, key):
        return key

    # -- fetching ----------------------------------------------------------------
    def fetch(self, key):
        """A page record (see `record`) with the cleaned text under "text". Raises MissingSource or SourceError."""
        raise NotImplementedError

    def current_version(self, key):
        """A cheap check of the upstream version, or None when unknown."""
        return None

    def links_of(self, rec):
        return rec.get("body_links") or []

    def seeds(self):
        """Keys a subject should crawl without listing them (an RFC list, a PDF list); default none."""
        return []

    # -- presentation ------------------------------------------------------------
    def permalink(self, src):
        """A stable link to the exact version a source record cites."""
        return src.get("url") or ""

    def version_label(self, version):
        return f"retrieved {version}" if version else ""

    # -- discovery and checks ----------------------------------------------------
    def discover(self, query, limit=20):
        """Candidate sources or pages for `sources discover`; adapters that cannot search return []."""
        return []

    def check(self):
        """Evidence for `sources check`: {license: {...}, problems: [...], notes: [...]}."""
        return {}

    # -- record ------------------------------------------------------------------
    def record(self, key, name, url, text, version, source_id=None, **extra):
        """The common page record. `text` is cleaned text; the store keeps it apart from the JSON."""
        lic = self.license
        rec = {
            "title": key, "name": name, "source": self.label, "adapter": self.adapter,
            "source_id": source_id if source_id is not None else key, "url": url,
            "revid": None, "version": str(version) if version is not None else None,
            "license": lic, "tier": self.tier, "retrieved": now_iso(), "fetched_at": now_iso(),
            "html": None, "links": [], "body_links": [], "lead_links": [], "categories": [],
            "hidden_categories": [], "sections": [], "templates": [], "citations": [],
            "anchors": {}, "meta": {}, "requested_title": key, "text": text,
        }
        rec.update(extra)
        return rec
