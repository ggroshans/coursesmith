"""Finding candidate sources for a subject, with the evidence a human needs to approve them.

    coursesmith sources discover <subject> [--query Q]... [--limit N] [--offline]
    coursesmith sources packet <subject>      a brief for a Claude web-search session (guides/SOURCES_GUIDE.md)
    coursesmith sources merge <subject>       fold that session's work/sources/found.yaml into the candidates

Discovery never adds a source. It writes scope/sources.candidates.yaml: every candidate with machine-readable
signals (license, stars, contributors, recency, who maintains it), a score, a suggested trust tier and a
ready-to-paste `sources:` snippet. A human sets `status: accept`, copies the snippet into subject.yaml and runs
`coursesmith sources check`, which reads each license from the source itself. Search results rank popularity,
not authority, so the score orders the list for reading and decides nothing.
"""
import math
from datetime import datetime, timedelta, timezone

import yaml

from ..util import atomic_write
from . import licenses
from .base import SourceError
from .registry import Registry, adapter_class

CLASS_POINTS = {"official": 3, "standards": 3, "academic": 2, "community": 1, "personal": 0}
CLASS_TIER = {"official": "official", "standards": "standard", "academic": "primary", "community": "curated",
              "personal": "commentary"}
ADAPTER_CLASS = {"rfc": "standards", "paper": "academic"}
SEARCHERS = ("github", "rfc", "paper")
REQUIRED_FOUND = ("url", "adapter", "title", "license_seen", "license_url", "why")


def candidates_path(subject):
    return subject.scope_dir / "sources.candidates.yaml"


def found_path(subject):
    return subject.dir / "work" / "sources" / "found.yaml"


def packet_path(subject):
    return subject.dir / "work" / "sources" / "packet.md"


def load_candidates(subject):
    try:
        return yaml.safe_load(candidates_path(subject).read_text(encoding="utf-8")) or []
    except (OSError, yaml.YAMLError):
        return []


def _recent(date, now=None):
    try:
        d = datetime.fromisoformat(str(date).replace("Z", "+00:00"))
    except ValueError:
        return False
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return (now or datetime.now(timezone.utc)) - d < timedelta(days=365)


def domain_class(c, registry=None):
    if c.get("domain_class") in CLASS_POINTS:
        return c["domain_class"]
    if c.get("adapter") in ADAPTER_CLASS:
        return ADAPTER_CLASS[c["adapter"]]
    if registry is not None:
        for r in registry.global_["repos"]:
            if c.get("repo") and str(r.get("repo", "")).lower() == str(c["repo"]).lower() and r.get("class"):
                return r["class"]
    return "community"


def score(c, registry=None, now=None):
    """(score, parts). Higher reads first; nothing here approves a source."""
    ev = c.get("evidence") or {}
    seen = ev.get("license_spdx") or c.get("license_seen") or ""
    cls = licenses.classify(seen) if seen and seen != "NOASSERTION" else "unknown"
    parts = {
        "license": 3 if cls != "unknown" and licenses.is_public(cls) else 1 if cls != "unknown" else 0,
        "domain": CLASS_POINTS.get(domain_class(c, registry), 0),
        "stars": round(min(math.log10((ev.get("stars") or 0) + 1), 5), 2),
        "contributors": round(min((ev.get("contributors") or 0) / 25, 2), 2),
        "recent": 1 if _recent(ev.get("pushed_at") or ev.get("updated"), now) else 0,
        "maintainer": 1 if (ev.get("owner_type") == "Organization" or c.get("maintainer")) else 0,
        "archived": -3 if ev.get("archived") else 0,
    }
    return round(sum(parts.values()), 2), parts


def snippet(c, registry=None):
    """The `sources:` entry to paste into subject.yaml once the candidate is accepted."""
    tier = c.get("suggested_tier") or CLASS_TIER[domain_class(c, registry)]
    lic = {"name": c.get("license_seen") or (c.get("evidence") or {}).get("license_spdx") or ""}
    name = (c.get("repo") or c.get("title") or c["id"]).split("/")[-1].lower().replace(" ", "-")[:40]
    if c.get("adapter") == "github":
        return {"name": name, "adapter": "github", "repo": c["repo"], "ref": "<run `sources check --fix-refs`>",
                "include": ["README.md", "**/*.md"], "depth": 1, "tier": tier, "license": lic}
    if c.get("adapter") == "html":
        return {"name": name, "adapter": "html", "base": c.get("url"), "allow": ["<path prefixes>"], "depth": 2,
                "tier": tier, "license": lic}
    if c.get("adapter") == "rfc":
        return {"name": "rfcs", "adapter": "rfc", "ids": [int(c["key"].split(">")[1])] if c.get("key") else [],
                "tier": "standard"}
    if c.get("adapter") == "paper":
        return {"name": "papers", "adapter": "paper", "dois": [c["key"].split(">", 1)[1]] if c.get("key") else [],
                "tier": "primary"}
    return {"name": name, "adapter": c.get("adapter"), "tier": tier, "license": lic}


def default_queries(subject):
    qs = [subject.title]
    qs += [s for s in subject.cfg.get("seeds") or [] if "$" not in str(s) and ">" not in str(s)][:3]
    return list(dict.fromkeys(q for q in qs if q))


def from_registry(registry, queries, include_terms):
    """Sources already vetted for other subjects whose topics or name touch this one."""
    words = {w.lower() for q in list(queries) + list(include_terms) for w in str(q).split() if len(w) > 3}
    out = []
    for r in registry.global_["repos"]:
        hay = " ".join([str(r.get("repo", "")), str(r.get("note", "")), " ".join(r.get("topics") or [])]).lower()
        if any(w in hay for w in words):
            lic = r.get("license") or {}
            out.append({"id": f"gh:{r['repo']}", "adapter": "github", "repo": r["repo"], "title": r["repo"].split("/")[1],
                        "url": f"https://github.com/{r['repo']}", "origin": "registry", "suggested_tier": r.get("tier"),
                        "license_seen": lic.get("name") or lic.get("spdx"), "domain_class": r.get("class"),
                        "evidence": {"registry": True, "verified": str(lic.get("verified") or "")}})
    return out


def merge_candidates(old, new):
    """New evidence replaces old; a human's `status` and `note` are kept."""
    by_id = {c["id"]: c for c in old}
    for c in new:
        prev = by_id.get(c["id"])
        if prev:
            c = {**prev, **{k: v for k, v in c.items() if k not in ("status", "note")}}
            c["status"], c["note"] = prev.get("status", "candidate"), prev.get("note", "")
        else:
            c.setdefault("status", "candidate")
            c.setdefault("note", "")
        by_id[c["id"]] = c
    return list(by_id.values())


def finish(cands, registry):
    for c in cands:
        s, parts = score(c, registry)
        c["score"], c["score_parts"] = s, parts
        c["suggested_tier"] = c.get("suggested_tier") or CLASS_TIER[domain_class(c, registry)]
        c["subject_yaml"] = snippet(c, registry)
    return sorted(cands, key=lambda c: (-c["score"], c["id"]))


def write_candidates(subject, cands):
    atomic_write(candidates_path(subject), "# Candidate sources. Set `status: accept` (or reject), copy `subject_yaml` into\n"
                 "# subject.yaml under `sources:`, then run `coursesmith sources check`.\n"
                 + yaml.safe_dump(cands, sort_keys=False, allow_unicode=True, width=110))


def run(subject, queries=None, limit=20, network=True, registry=None, log=print):
    registry = registry or Registry.from_subject(subject)
    qs = list(queries or default_queries(subject))
    include = (subject.cfg.get("scope") or {}).get("include_terms") or []
    new = from_registry(registry, qs, include)
    if network:
        for name in SEARCHERS:
            try:
                ad = adapter_class(name).for_discovery(http=registry.http)
                for q in qs:
                    for c in ad.discover(q, limit):
                        c.setdefault("origin", "api")
                        new.append(c)
                if name == "github":
                    top = sorted((c for c in new if c["adapter"] == "github" and c.get("origin") == "api"),
                                 key=lambda c: -((c.get("evidence") or {}).get("stars") or 0))[:10]
                    for c in top:
                        n = ad.contributors(c["repo"])
                        if n is not None:
                            c["evidence"]["contributors"] = n
            except SourceError as e:
                log(f"[sources] {name} search failed: {e}")
    cands = finish(merge_candidates(load_candidates(subject), new), registry)
    write_candidates(subject, cands)
    log(f"[sources] {len(cands)} candidates for {subject.slug} -> {candidates_path(subject).relative_to(subject.dir)}; "
        f"review them, set status, and paste accepted ones into subject.yaml")
    return cands


def packet(subject, log=print):
    """The brief a Claude session follows to search the web for sources (guides/SOURCES_GUIDE.md)."""
    parts = [f"# Source search: {subject.title}", "",
             f"Follow `guides/SOURCES_GUIDE.md`. Write your answer to `subjects/{subject.slug}/work/sources/found.yaml` "
             "and nothing else.", "", "## The subject", "",
             (subject.cfg.get("description") or "").strip() or subject.title, ""]
    frame = subject.frame or {}
    if frame.get("parts"):
        parts += ["## Chapters the course will have", ""]
        for p in frame["parts"]:
            parts.append(f"- **{p['title']}**" + (" (each chapter is one question)" if p.get("question") else "") + ": "
                         + "; ".join(c["title"] for c in p.get("chapters") or []))
        parts.append("")
    cur = subject.cfg.get("sources") or []
    parts += ["## Sources already in subject.yaml", ""] + ([f"- {c.get('name')}: {c.get('adapter')} "
                                                            f"{c.get('repo') or c.get('base') or ''}" for c in cur] or ["None yet (Wikipedia is always on)."])
    cands = load_candidates(subject)
    parts += ["", "## Candidates found by API search so far", ""]
    parts += [f"- {c['id']} (score {c.get('score')}): {c.get('title')}, license {c.get('license_seen') or (c.get('evidence') or {}).get('license_spdx') or 'unknown'}"
              for c in cands[:40]] or ["None."]
    parts += ["", f"Distribution: {subject.cfg.get('distribution') or 'personal'} "
              f"({'every source must allow public redistribution' if subject.cfg.get('distribution') == 'public' else 'attributed non-commercial sources are fine'}).", ""]
    atomic_write(packet_path(subject), "\n".join(parts))
    log(f"[sources] packet -> {packet_path(subject).relative_to(subject.dir)}")
    return packet_path(subject)


def merge(subject, log=print):
    """Fold the web-search session's found.yaml into the candidates, rejecting entries missing required evidence."""
    try:
        found = yaml.safe_load(found_path(subject).read_text(encoding="utf-8")) or []
    except OSError:
        raise SystemExit(f"no {found_path(subject).relative_to(subject.dir)}; run the search session first")
    new, bad = [], []
    for f in found:
        miss = [k for k in REQUIRED_FOUND if not f.get(k)]
        if miss:
            bad.append(f"{f.get('url') or f.get('title') or '?'}: missing {', '.join(miss)}")
            continue
        cid = f.get("id") or (f"gh:{f['repo']}" if f["adapter"] == "github" and f.get("repo")
                              else f"{f['adapter']}:{f['url'].rstrip('/').split('://')[-1]}")
        new.append({"id": cid, "adapter": f["adapter"], "repo": f.get("repo"), "title": f["title"], "url": f["url"],
                    "snippet": f["why"], "origin": "session", "license_seen": f["license_seen"],
                    "domain_class": f.get("domain_class"), "suggested_tier": f.get("suggested_tier"),
                    "maintainer": f.get("maintainer"),
                    "evidence": {"license_url": f["license_url"], "updated": f.get("updated"),
                                 "nc_nd": bool(f.get("nc_nd")), "session": True}})
    registry = Registry.from_subject(subject)
    cands = finish(merge_candidates(load_candidates(subject), new), registry)
    write_candidates(subject, cands)
    for b in bad:
        log(f"[sources] rejected: {b}")
    log(f"[sources] merged {len(new)} session candidates ({len(bad)} rejected); {len(cands)} in total")
    return cands
