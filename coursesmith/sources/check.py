"""coursesmith sources check <subject> [--fix-refs]

Verifies the subject's `sources:` against the sources themselves before anything is crawled:

  * each adapter reads its own evidence: a GitHub repo's license file (never a listing site's guess), a docs
    site's license statement, an RFC's obsolescence, a paper's abstract;
  * the declared license must match what was read, and every non-Wikipedia source must declare one;
  * allowlists are non-empty and every qualified seed (in subject.yaml and frame.yaml) is allowed;
  * with `distribution: public`, no source may carry a license that forbids redistribution;
  * a branch or tag `ref` is flagged; --fix-refs pins it to the commit it points at now (the one place the
    engine edits subject.yaml, and only the ref line).

When nothing is wrong it writes scope/sources.ok, a stamp of the sources block. `crawl` and `finalize` refuse to
run for a subject whose sources block has changed since the last passing check.
"""
import hashlib
import json
import re
from datetime import datetime, timezone

from ..util import atomic_write
from . import licenses
from .base import SourceError, tier_rank, TIERS
from .keys import is_qualified, page_part
from .registry import Registry


def ok_path(subject):
    return subject.scope_dir / "sources.ok"


def needs_check(subject):
    """True when the subject lists a source beyond the default Wikipedia."""
    return any(c.get("adapter", "wikipedia") != "wikipedia" or c.get("api_url")
               for c in subject.cfg.get("sources") or [])


def sources_hash(subject):
    blob = json.dumps({"sources": subject.cfg.get("sources") or [],
                       "distribution": subject.cfg.get("distribution")}, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def require_ok(subject):
    """Stop a crawl or finalize on sources nobody has verified."""
    if not needs_check(subject):
        return
    try:
        stamp = json.loads(ok_path(subject).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        stamp = {}
    if stamp.get("hash") != sources_hash(subject):
        raise SystemExit(f"{subject.slug}: the `sources:` in subject.yaml have not passed "
                         f"`coursesmith sources check {subject.slug}` since they last changed")


def qualified_seeds(subject):
    seeds = [s for s in subject.cfg.get("seeds") or [] if is_qualified(str(s))]
    for src in ((subject.frame or {}).get("parts") or []) + ((subject.cfg.get("frame") or {}).get("parts") or []):
        for c in src.get("chapters") or []:
            seeds += [s for s in (c.get("seeds") or []) + (c.get("also") or []) if is_qualified(str(s))]
    return list(dict.fromkeys(seeds))


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def set_ref(text, repo, sha):
    """Pin `repo`'s source entry to `sha` by editing only its `ref:` value (or adding one), keeping every comment
    and the layout of subject.yaml. Handles the flow ({name: x, repo: o/r, ...}) form on one line and the block
    form; returns None when the entry cannot be found."""
    m = re.search(rf"(?m)^(?P<flow>[ \t]*(?:-[ \t]*)?)(?P<map>\{{[^\n]*\brepo:\s*{re.escape(repo)}\b[^\n]*\}})[ \t]*$", text)
    if m:
        line = m.group("map")
        if re.search(r"\bref:\s*[^,}\s]+", line):
            new = re.sub(r"(\bref:\s*)[^,}\s]+", rf"\g<1>{sha}", line, count=1)
        else:
            new = line[:-1].rstrip() + f", ref: {sha}" + "}"
        return text[:m.start("map")] + new + text[m.end("map"):]
    lines = text.split("\n")
    rx = re.compile(rf"^(?P<pre>[ \t]*(?:-[ \t]+)?)repo:[ \t]*{re.escape(repo)}[ \t]*(?:#.*)?$")
    i = next((k for k, l in enumerate(lines) if rx.match(l)), None)
    if i is None:
        return None
    key_col = len(rx.match(lines[i]).group("pre").replace("-", " "))
    start = i
    while start > 0:  # earlier keys of the same entry, up to and including its `- ` line
        prev = lines[start - 1]
        if prev.strip() == "" or _indent(prev) < key_col and not prev.lstrip().startswith("- "):
            break
        start -= 1
        if _indent(prev) < key_col:  # the dash line that opens the entry
            break
    end = i + 1
    while end < len(lines) and (lines[end].strip() == "" or _indent(lines[end]) >= key_col):
        end += 1
    while end > i + 1 and lines[end - 1].strip() == "":
        end -= 1
    for k in range(start, end):
        m2 = re.match(r"^(?P<a>[ \t]*(?:-[ \t]+)?ref:[ \t]*)\S+(?P<b>.*)$", lines[k])
        if m2:
            lines[k] = f"{m2.group('a')}{sha}{m2.group('b')}"
            return "\n".join(lines)
    lines.insert(i + 1, " " * key_col + f"ref: {sha}")
    return "\n".join(lines)


def run(subject, fix_refs=False, registry=None, log=print):
    registry = registry
    problems, notes, rows = [], [], []
    try:
        registry = registry or Registry.from_subject(subject)
    except SourceError as e:
        problems.append(str(e))
        registry = None
    distribution = subject.cfg.get("distribution") or "personal"
    if distribution not in ("personal", "public"):
        problems.append(f"distribution must be personal or public, not {distribution!r}")
    fixes = {}
    for ad in (registry.adapters if registry else []):
        if ad.adapter == "wikipedia" and ad.prefix == "":
            continue
        label = ad.label
        if ad.tier not in TIERS:
            problems.append(f"{label}: tier {ad.tier!r} is not one of {', '.join(TIERS)}")
        lic = ad.license
        if ad.adapter in ("github", "html", "pdf") and not lic.get("name"):
            problems.append(f"{label}: declare its license under `license:`")
        if distribution == "public" and lic.get("name") and not registry.is_public(lic.get("class") or "unknown"):
            problems.append(f"{label}: {lic['name']} ({lic.get('class')}) does not allow public distribution; "
                            f"use `distribution: personal` or drop it")
        try:
            res = ad.check() or {}
        except SourceError as e:
            res = {"problems": [f"{label}: {e}"]}
        for p in res.get("problems") or []:
            problems.append(p if p.startswith(label) or label in p else f"{label}: {p}")
        for n in res.get("notes") or []:
            notes.append(n)
        sha = (res.get("evidence") or {}).get("sha")
        if sha and ad.adapter == "github" and sha != str(ad.cfg.get("ref") or ""):
            fixes[ad.repo] = sha
        ev = (res.get("evidence") or {}).get("license") or res.get("license") or {}
        rows.append({"name": label, "adapter": ad.adapter, "tier": ad.tier, "declared": lic.get("name") or "",
                     "class": lic.get("class"), "read": ev.get("class") or "", "ref": str(ad.cfg.get("ref") or ""),
                     "sha": sha or ""})
    if registry:
        for k in qualified_seeds(subject):
            if not registry.allowed(k):
                problems.append(f"seed {k}: no source in subject.yaml allows it")
        for ad in registry.adapters:
            if ad.adapter == "github" and not ad.include:
                problems.append(f"{ad.label}: include is empty, so nothing from {ad.repo} is allowed")
    if fixes and fix_refs:
        text = subject.yaml_path.read_text(encoding="utf-8")
        done = []
        for repo, sha in fixes.items():
            new = set_ref(text, repo, sha)
            if new is None:
                notes.append(f"could not find {repo} in subject.yaml to pin it; add `ref: {sha}` yourself")
            else:
                text = new
                done.append(f"{repo} -> {sha[:7]}")
        if done:
            atomic_write(subject.yaml_path, text)
            log(f"[sources] pinned refs in subject.yaml: {', '.join(done)}")
            notes = [n for n in notes if not any(f"ref: {s}" in n for s in fixes.values())]
    write_report(subject, rows, problems, notes)
    if problems:
        if ok_path(subject).exists():
            ok_path(subject).unlink()
        for p in problems:
            log(f"  PROBLEM {p}")
        log(f"[sources] {subject.slug}: {len(problems)} problems, {len(notes)} notes -> reports/sources.md")
        return problems
    if fixes and not fix_refs:
        notes.append("refs are not commits; run with --fix-refs to pin them")
    # the stamp covers the sources block as it is now (after any pinning)
    if fix_refs:
        from ..subject import load
        subject = load(subject.slug)
    atomic_write(ok_path(subject), json.dumps({"hash": sources_hash(subject), "checked": datetime.now(timezone.utc)
                                              .isoformat(timespec="seconds"), "sources": len(rows)}))
    for n in notes:
        log(f"  note: {n}")
    log(f"[sources] {subject.slug}: {len(rows)} sources verified, {len(notes)} notes -> reports/sources.md")
    return []


def write_report(subject, rows, problems, notes):
    L = [f"# Sources: {subject.title}", "", f"Distribution: {subject.cfg.get('distribution') or 'personal'}", "",
         "| Source | Adapter | Tier | Declared license | License read from the source | Pinned to |", "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r['name']} | {r['adapter']} | {r['tier']} | {r['declared'] or '-'} | {r['read'] or '-'} | "
                 f"{(r['sha'] or r['ref'] or '-')[:12]} |")
    L += ["", "## Problems", ""] + ([f"- {p}" for p in problems] or ["None."])
    L += ["", "## Notes", ""] + ([f"- {n}" for n in notes] or ["None."])
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "sources.md", "\n".join(L) + "\n")
