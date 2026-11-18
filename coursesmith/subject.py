"""A subject: its subject.yaml settings and the paths of everything it owns under subjects/<slug>/."""
import copy
from functools import cached_property

import yaml

from . import config
from .util import read_json, read_jsonl, slug as _slug, write_jsonl

DEFAULTS = {
    "ordering": "pedagogical",
    # per_unit: entries per unit (the owner may change it later from the entries' lengths); units: a fixed
    # count, else about 4.5 per unit; entries: only a guide for frame shares and the selection report
    "targets": {"entries": None, "per_unit": [4, 5], "units": None, "fact_caps": {}, "word_ranges": {},
                "max_words": None},
    "edition": {"images": False, "questions": False, "proportional_clock": False},
    "categories": {"roots": [], "depth": 1, "exclude": []},
    "scope": {"include_terms": [], "exclude_terms": [], "threshold": None, "person_terms": []},
    "hubs": {},
    "graph": {"mention_fallback": True},
    "distribution": "personal",
    "course_type": "survey",
    "sources": [],
    "seeds": [],
    "verification": {"works": "openalex", "authorities": []},
}


class SubjectError(RuntimeError):
    pass


class Subject:
    def __init__(self, slug):
        self.slug = slug
        self.dir = config.SUBJECTS / slug
        self.yaml_path = self.dir / "subject.yaml"
        if not self.yaml_path.exists():
            raise SubjectError(f"no subject.yaml for '{slug}' (looked in {self.yaml_path})")
        raw = yaml.safe_load(self.yaml_path.read_text(encoding="utf-8")) or {}
        self.cfg = _merge(DEFAULTS, raw)

    def __repr__(self):
        return f"Subject({self.slug!r})"

    # -- settings ------------------------------------------------------------
    @property
    def title(self):
        return self.cfg.get("title") or self.slug.replace("-", " ").title()

    @property
    def short(self):
        """Prefix for entry ids, e.g. 'soil' in soil-chem-014."""
        return self.cfg.get("short") or self.slug.split("-")[0]

    @property
    def ordering(self):
        return self.cfg["ordering"]

    @property
    def chronological(self):
        return self.ordering == "chronological"

    @property
    def targets(self):
        return self.cfg["targets"]

    @property
    def edition(self):
        return self.cfg["edition"]

    # -- paths ---------------------------------------------------------------
    frame_path = property(lambda s: s.dir / "frame.yaml")
    entries_dir = property(lambda s: s.dir / "entries")
    draft_dir = property(lambda s: s.dir / "entries" / "draft")
    order_path = property(lambda s: s.dir / "order.json")
    units_path = property(lambda s: s.dir / "units.json")
    glossary_path = property(lambda s: s.dir / "glossary.json")
    state_path = property(lambda s: s.dir / "STATE.md")
    ledger_path = property(lambda s: s.dir / "ledger.csv")
    scope_dir = property(lambda s: s.dir / "scope")
    work_dir = property(lambda s: s.dir / "work")
    dossier_dir = property(lambda s: s.dir / "work" / "dossiers")
    write_dir = property(lambda s: s.dir / "work" / "write")
    tmp_dir = property(lambda s: s.dir / "work" / "tmp")
    output_dir = property(lambda s: s.dir / "output")
    reports_dir = property(lambda s: s.dir / "reports")
    verify_dir = property(lambda s: s.dir / "verify")
    graph_path = property(lambda s: s.dir / "work" / "graph.json")
    prose_path = property(lambda s: s.dir / "output" / "prose.json")

    def tmp(self, pass_slug):
        """Private scratch folder for one pass. Passes run in parallel never share scratch files."""
        p = self.tmp_dir / pass_slug
        p.mkdir(parents=True, exist_ok=True)
        return p

    # -- data ----------------------------------------------------------------
    @cached_property
    def frame(self):
        if not self.frame_path.exists():
            return {}
        return yaml.safe_load(self.frame_path.read_text(encoding="utf-8")) or {}

    def entry_files(self):
        return sorted(p for p in self.entries_dir.glob("*.jsonl"))

    def entries(self, selected_only=False):
        out = []
        for p in self.entry_files():
            out += read_jsonl(p)
        if selected_only:
            out = [e for e in out if e.get("selected")]
        return out

    def entries_by_id(self, selected_only=False):
        return {e["id"]: e for e in self.entries(selected_only)}

    def save_entries(self, entries):
        """Write entries back, one file per chapter (or per file they came from, via '_file')."""
        groups = {}
        for e in entries:
            name = e.pop("_file", None) or _slug(e.get("chapter") or e.get("part") or "misc")
            groups.setdefault(name, []).append(e)
        self.entries_dir.mkdir(parents=True, exist_ok=True)
        keep = set()
        for name, es in groups.items():
            write_jsonl(self.entries_dir / f"{name}.jsonl", es)
            keep.add(f"{name}.jsonl")
        for p in self.entry_files():
            if p.name not in keep:
                p.unlink()

    def order(self):
        return read_json(self.order_path, {}) or {}

    def units(self):
        return read_json(self.units_path, {}) or {}

    def prose(self):
        return read_json(self.prose_path, {}) or {}


def load(slug):
    return Subject(slug)


def all_slugs():
    if not config.SUBJECTS.exists():
        return []
    return sorted(p.parent.name for p in config.SUBJECTS.glob("*/subject.yaml"))


def _merge(base, over):
    """Overlay subject.yaml on the defaults. Never shares the defaults' objects, and a YAML null (a key left
    empty) keeps a dict or list default instead of replacing it with None."""
    out = copy.deepcopy(base)
    for k, v in (over or {}).items():
        if v is None and isinstance(base.get(k), (dict, list)):
            continue
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            out[k] = _merge(base[k], v)
        else:
            out[k] = v
    return out
