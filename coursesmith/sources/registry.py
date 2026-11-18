"""The registry: which sources a subject may use, and what is known about each.

Two layers, subject over shared:
  * `sources:` in subject.yaml lists the subject's sources with their adapter settings, allowlists, tier and
    declared license;
  * sources/registry.yaml (repo root) holds what was vetted once for every subject: domains and GitHub
    repositories with a default tier and a verified license, plus the license classes.

A key is allowed only when an adapter built from the subject's list owns it and accepts it. Wikipedia is always
present, so bare titles work with no configuration.
"""
from fnmatch import fnmatch

import yaml

from .. import config
from . import licenses
from .base import MissingSource, SourceError, best_tier, tier_rank
from .keys import is_qualified, split_key


def load_global(path=None):
    path = path or config.REGISTRY_PATH
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        data = {}
    return {"domains": data.get("domains") or [], "repos": data.get("repos") or [],
            "license_classes": data.get("license_classes") or {}}


def adapter_class(name):
    """Adapter classes load on demand so a subject using only Wikipedia imports nothing else."""
    import importlib
    mods = {"wikipedia": "wikipedia", "github": "github", "html": "html", "rfc": "rfc", "pdf": "pdf",
            "paper": "paper"}
    if name not in mods:
        raise SourceError(f"unknown source adapter '{name}' (known: {', '.join(sorted(mods))})")
    try:
        mod = importlib.import_module(f".{mods[name]}", __package__)
    except ImportError as e:
        raise SourceError(f"source adapter '{name}' is not available: {e}")
    return getattr(mod, "ADAPTER")


class Registry:
    def __init__(self, sources_cfg=None, global_path=None, http=None, wiki_client=None):
        self.global_ = load_global(global_path)
        self.http = http
        cfgs = [dict(c) for c in (sources_cfg or [])]
        if not any(c.get("adapter", "wikipedia") == "wikipedia" and not c.get("api_url") for c in cfgs):
            cfgs.insert(0, {"name": "wikipedia", "adapter": "wikipedia"})
        self.adapters = []
        for c in cfgs:
            c.setdefault("adapter", "wikipedia")
            cls = adapter_class(c["adapter"])
            probe = cls(c, http=http)
            self.adapters.append(cls(c, http=http, defaults=self._defaults_for(c, probe.hosts())))
        self.default_wiki = next(a for a in self.adapters if a.adapter == "wikipedia" and a.prefix == "")
        if wiki_client is not None:
            self.default_wiki.client = wiki_client

    @classmethod
    def from_subject(cls, subject, **kw):
        return cls(subject.cfg.get("sources"), **kw)

    # -- shared defaults -----------------------------------------------------------
    def _defaults_for(self, cfg, hosts):
        repo = str(cfg.get("repo") or "").lower()
        if repo:
            for r in self.global_["repos"]:
                if str(r.get("repo", "")).lower() == repo:
                    return r
        for d in self.global_["domains"]:
            pat = str(d.get("host") or "").lower()
            if pat and any(fnmatch(h.lower(), pat) or h.lower().endswith("." + pat.lstrip("*.")) for h in hosts):
                return d
        return {}

    def license_overrides(self):
        return self.global_["license_classes"]

    # -- lookup ---------------------------------------------------------------------
    def maybe_for_key(self, key):
        for a in self.adapters:
            if a.owns(key):
                return a
        return None

    def for_key(self, key):
        a = self.maybe_for_key(key)
        if a is None:
            raise MissingSource(f"no source in this subject owns '{key}' (add it under `sources:` in subject.yaml)")
        return a

    def allowed(self, key):
        a = self.maybe_for_key(key)
        return bool(a and a.allowed(key))

    def tier(self, key):
        a = self.maybe_for_key(key)
        return a.tier if a else None

    def license(self, key):
        a = self.maybe_for_key(key)
        return a.license if a else None

    def source_entry(self, key):
        a = self.maybe_for_key(key)
        return a.cfg if a else None

    def by_label(self, label):
        return next((a for a in self.adapters if a.label == label), None)

    def is_public(self, cls):
        return licenses.is_public(cls, self.license_overrides())

    def best_tier(self, keys):
        return best_tier(self.tier(k) for k in keys)

    def all_seeds(self):
        """Keys the subject's sources ask to be crawled without being listed under `seeds:`."""
        out = []
        for a in self.adapters:
            out += a.seeds()
        return list(dict.fromkeys(out))

    def qualified_prefixes(self):
        return sorted({a.prefix for a in self.adapters if a.prefix})
