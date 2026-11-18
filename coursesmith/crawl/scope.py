"""Scope scoring for a subject: is this page part of the course?

score = category distance to the subject roots   (+4 at depth 0, +3 at 1, +1 at 2; never deeper)
      + WikiProject tag                          (+3, and +3/+2/+1 for Top/High/Mid importance)
      + share of inlinks from in-scope pages     (+1 per in-scope page linking to it, up to +3)
      + lexical rules                            (include terms +2 in the title, +1 in the description;
                                                  exclude terms -5)
      + hub membership                           (navbox +3, index +2, Vital +3)
      + the scope judge's verdict                (in or support +20, out -20; scope/judge.json)
excluded categories -10, disambiguation pages and missing pages -99. Frame articles are always in.

The threshold comes from subject.yaml (scope.threshold), else from `scope tune` (scope/tuned.json, fitted
against the hand-labeled calibration set), else DEFAULT_THRESHOLD.
"""
import csv
import json
import re

from ..sources.keys import is_qualified
from ..util import read_json, write_json

DEFAULT_THRESHOLD = 5
CAT_POINTS = {0: 4, 1: 3, 2: 1}
IMP_POINTS = {"Top": 3, "High": 2, "Mid": 1, "Low": 0}


class Scope:
    def __init__(self, subject, hubs=None, registry=None):
        self.s = subject
        cfg = subject.cfg
        self.include = [t.lower() for t in cfg["scope"].get("include_terms") or []]
        self.exclude = [t.lower() for t in cfg["scope"].get("exclude_terms") or []]
        self.exclude_desc = [t.lower() for t in cfg["scope"].get("exclude_desc") or []]
        self.excl_cats = {c.removeprefix("Category:").lower() for c in cfg["categories"].get("exclude") or []}
        h = hubs or read_json(subject.scope_dir / "hubs.json", {}) or {}
        self.cat_dist = {k.lower(): v for k, v in (h.get("categories") or {}).items()}
        self.cat_pages = h.get("category_pages") or {}
        self.navbox = set(h.get("navbox") or [])
        self.index = set(h.get("index") or [])
        self.vital = set(h.get("vital") or [])
        self.importance = h.get("importance") or {}
        self.project = (cfg.get("hubs") or {}).get("wikiproject")
        self.forced = set(h.get("forced") or [])
        self.inlinks = {}  # title -> set of in-scope pages linking to it (filled during the crawl)
        self.judge = read_json(subject.scope_dir / "judge.json", {}) or {}
        self._registry = registry

    @property
    def registry(self):
        """The subject's source registry, built on first use so Wikipedia-only code never loads it."""
        if self._registry is None:
            from ..sources.registry import Registry
            self._registry = Registry.from_subject(self.s)
        return self._registry

    @property
    def threshold(self):
        t = self.s.cfg["scope"].get("threshold")
        if t is not None:
            return t
        tuned = read_json(self.s.scope_dir / "tuned.json")
        return tuned["threshold"] if tuned else DEFAULT_THRESHOLD

    def add_inlink(self, target, source):
        self.inlinks.setdefault(target, set()).add(source)

    def score(self, title, meta=None):
        """(score, reasons) for a canonical title with optional link metadata."""
        meta = meta or {}
        if is_qualified(title):
            # a page of another source is in scope exactly when the subject's source list allows it
            if self.registry.allowed(title):
                return self.threshold + 1 + (10 if title in self.forced else 0), ["allowlist"]
            return -99, ["not in the sources allowlist"]
        if meta.get("missing"):
            return -99, ["missing"]
        if meta.get("disambig"):
            return -99, ["disambiguation"]
        s, why = 0, []
        if title in self.forced:
            s += 10
            why.append("frame+10")
        v = (self.judge.get(title) or {}).get("v")
        if v in ("in", "support"):
            s += 20
            why.append(f"judge-{v}+20")
        elif v == "out":
            s -= 20
            why.append("judge-out-20")
        cats = [c.lower() for c in meta.get("categories") or []]
        if any(c in self.excl_cats for c in cats):
            s -= 10
            why.append("excluded-category-10")
        d = self.cat_pages.get(title)
        dists = [self.cat_dist[c] + 1 for c in cats if c in self.cat_dist]
        if d is not None:
            dists.append(d)
        if dists:
            best = min(dists)
            if best in CAT_POINTS:
                s += CAT_POINTS[best]
                why.append(f"category-d{best}+{CAT_POINTS[best]}")
        imp = self.importance.get(title)
        if imp:
            pts = 3 + IMP_POINTS.get(imp, 0)
            s += pts
            why.append(f"wikiproject-{imp}+{pts}")
        if title in self.navbox:
            s += 3
            why.append("navbox+3")
        if title in self.index:
            s += 2
            why.append("index+2")
        if title in self.vital:
            s += 3
            why.append("vital+3")
        n_in = len(self.inlinks.get(title, ()))
        if n_in:
            pts = min(3, n_in)
            s += pts
            why.append(f"inlinks{n_in}+{pts}")
        low_t, low_d = title.lower(), (meta.get("description") or "").lower()
        if any(_word(t, low_t) for t in self.include):
            s += 2
            why.append("title-term+2")
        elif any(_word(t, low_d) for t in self.include):
            s += 1
            why.append("desc-term+1")
        bad = [t for t in self.exclude if _word(t, low_t) or _word(t, low_d)]
        if bad:
            s -= 5
            why.append(f"exclude-term-5:{bad[0]}")
        bad_d = [t for t in self.exclude_desc if _word(t, low_d)]
        if bad_d and title not in self.forced:
            s -= 4
            why.append(f"exclude-desc-4:{bad_d[0]}")
        if low_t.startswith(("list of", "index of", "outline of", "glossary of")):
            s -= 1
            why.append("list-1")
        return s, why

    def in_scope(self, title, meta=None):
        s, _ = self.score(title, meta)
        return title in self.forced or s >= self.threshold


def _word(term, text):
    return re.search(rf"(?<![a-z]){re.escape(term)}", text) is not None


# -- calibration ---------------------------------------------------------------
CAL_FIELDS = ["title", "score", "reasons", "description", "suggested", "label"]


def write_calibration(subject, rows, n=100):
    """Borderline titles (score within a few points of the threshold) for hand labeling."""
    path = subject.scope_dir / "calibration.csv"
    old = {}
    if path.exists():
        with path.open(newline="", encoding="utf-8") as f:
            old = {r["title"]: r for r in csv.DictReader(f)}
    rows = sorted(rows, key=lambda r: (abs(r["score"] - DEFAULT_THRESHOLD), r["title"]))[:n]
    subject.scope_dir.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAL_FIELDS)
        w.writeheader()
        for r in sorted(rows, key=lambda r: r["title"]):
            prev = old.get(r["title"], {})
            w.writerow({"title": r["title"], "score": r["score"], "reasons": "; ".join(r["reasons"]),
                        "description": r.get("description", ""), "suggested": prev.get("suggested", ""),
                        "label": prev.get("label", "")})
    return path


def read_labels(subject):
    """title -> True/False from calibration.csv: the owner's `label`, else the `suggested` pre-label."""
    path = subject.scope_dir / "calibration.csv"
    if not path.exists():
        return {}, 0, 0
    out, owner, suggested = {}, 0, 0
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            v = (r.get("label") or "").strip().lower()
            if v:
                owner += 1
            else:
                v = (r.get("suggested") or "").strip().lower()
                suggested += bool(v)
            if v in ("in", "yes", "y", "1", "true"):
                out[r["title"]] = True
            elif v in ("out", "no", "n", "0", "false"):
                out[r["title"]] = False
    return out, owner, suggested


def tune(subject, log=print):
    """Pick the threshold that best separates the labeled calibration titles (max F1, ties: higher)."""
    labels, owner, suggested = read_labels(subject)
    if not labels:
        raise SystemExit("no labels in scope/calibration.csv (fill the `label` column with in/out)")
    with (subject.scope_dir / "calibration.csv").open(newline="", encoding="utf-8") as f:
        scores = {r["title"]: float(r["score"]) for r in csv.DictReader(f)}
    best = None
    for t in sorted(set(scores.values())) + [max(scores.values()) + 1]:
        tp = sum(1 for k, v in labels.items() if v and scores[k] >= t)
        fp = sum(1 for k, v in labels.items() if not v and scores[k] >= t)
        fn = sum(1 for k, v in labels.items() if v and scores[k] < t)
        p = tp / (tp + fp) if tp + fp else 0
        r = tp / (tp + fn) if tp + fn else 0
        f1 = 2 * p * r / (p + r) if p + r else 0
        if best is None or f1 > best["f1"] or (f1 == best["f1"] and t > best["threshold"]):
            best = {"threshold": t, "f1": round(f1, 3), "precision": round(p, 3), "recall": round(r, 3)}
    best.update({"labels": len(labels), "owner_labels": owner, "suggested_labels": suggested})
    write_json(subject.scope_dir / "tuned.json", best)
    log(f"[scope] threshold {best['threshold']} (F1 {best['f1']}, precision {best['precision']}, recall "
        f"{best['recall']}) from {len(labels)} labels ({owner} by the owner, {suggested} pre-labeled)")
    return best


def rescore(subject, log=print):
    """Re-score the calibration rows with the current scope settings, keeping every label."""
    from .store import Store
    store, sc = Store(), Scope(subject)
    path = subject.scope_dir / "calibration.csv"
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        s, why = sc.score(r["title"], store.meta.get(r["title"]))
        r["score"], r["reasons"] = s, "; ".join(why)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAL_FIELDS)
        w.writeheader()
        w.writerows(rows)
    log(f"[scope] re-scored {len(rows)} calibration rows")


def save_hubs(subject, hubs):
    write_json(subject.scope_dir / "hubs.json", hubs)


def dumps_reasons(r):
    return json.dumps(r)
