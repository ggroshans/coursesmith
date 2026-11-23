"""frame build: a scout crawl of the subject's hubs, merged into a draft frame.yaml for review.

    coursesmith frame build <subject> [--scout N] [--refresh]

1. Hubs (subject.yaml `hubs` and `categories`): navboxes, the index page, Vital sections, WikiProject
   importance, the category tree (depth 1, filtered depth 2, never depth 3).
2. Pre-screen every candidate in batches of 50: canonical title, categories, description, Wikidata QID.
3. Scout crawl: fetch the seeds and the most central candidates (default 100 pages) into the shared cache.
4. Core-ness per candidate: navbox +2, index +1, Vital +3, importance Top 4 / High 3 / Mid 2 / Low 1,
   category depth 0 +2 / 1 +1, title term +1.
5. Parts and chapters from subject.yaml `frame:` hints (title x3, description x2, categories x1), with the
   navbox group as a fallback (`frame.navbox_parts`) and category clustering for parts without chapter hints.
   `frame.foundations` lists the ~5% of concepts most branches depend on; people, societies and journals go
   to the history part as summary candidates.
6. Writes frame.yaml (parts -> chapters -> seeds, candidates, share, target), reports/frame_report.md,
   scope/hubs.json (for the scope scorer) and scope/calibration.csv (borderline titles to label).

The owner edits frame.yaml before the main crawl; this step decides quality the way the ICS chart did.
"""
import re
from collections import Counter, defaultdict

import yaml

from ..crawl.api import WikiClient
from ..crawl.fetch import fetch_page, prescreen
from ..crawl.scope import Scope, save_hubs, write_calibration
from ..crawl.store import Store
from ..sources.keys import is_qualified
from ..sources.registry import Registry
from ..util import atomic_write, slug
from . import hubs as H

IMP_CORE = {"Top": 4, "High": 3, "Mid": 2, "Low": 1}
# Descriptions that mark a page about a person; a subject adds its own (scope.person_terms: [pedologist]).
PERSON_TERMS = ("scientist", "engineer", "researcher", "professor", "naturalist", "inventor", "physicist",
                "chemist", "biologist", "geologist", "ecologist", "botanist", "zoologist", "geographer",
                "microbiologist", "astronomer", "mathematician", "economist", "philosopher", "historian",
                "physician", "psychologist", "sociologist", "anthropologist", "archaeologist", "architect",
                "musician", "composer", "artist", "painter", "writer", "author", "poet", "politician",
                "businessman", "businesswoman", "businessperson", "entrepreneur", "explorer", "scholar")


def person_re(extra=()):
    terms = sorted({t.lower() for t in (*PERSON_TERMS, *(extra or ()))}, key=len, reverse=True)
    return re.compile(r"\b(" + "|".join(map(re.escape, terms)) + r")\b", re.I)
ORG_RE = re.compile(r"\b(society|journal|institute|university|association|union|council|agency|organi[sz]ation|"
                    r"initiative|program(me)?|conference|award|prize|magazine|publisher|company|centre|center)\b",
                    re.I)
SEED_MIN = 3
DRAFT_STATUS = "draft: review before the main crawl"


def _hint_score(hints, title, desc, cats):
    t, d, c = title.lower(), (desc or "").lower(), " | ".join(cats or []).lower()
    s = 0
    for h in hints or []:
        h = h.lower()
        # "~sol" matches anywhere (Acrisol, Andosols); "ped$" only the whole word; a plain hint starts a word
        if h.startswith("~"):
            rx = re.compile(re.escape(h[1:]))
        elif h.endswith("$"):
            rx = re.compile(rf"(?<![a-z]){re.escape(h[:-1])}(?![a-z])")
        else:
            rx = re.compile(rf"(?<![a-z]){re.escape(h)}")
        whole = re.compile(rf"(?<![a-z]){re.escape(h.strip('~$'))}(?![a-z])")
        s += 3 * bool(rx.search(t)) + 2 * bool(rx.search(d)) + 1 * bool(whole.search(c))
    return s


def gather(subject, client, store, log=print):
    cfg = subject.cfg
    hc = cfg.get("hubs") or {}
    cand = defaultdict(dict)
    nav_titles = []
    skip = set((cfg.get("frame") or {}).get("navbox_skip") or [])
    for tpl in hc.get("navboxes") or []:
        for g in H.navbox(client, tpl):
            label = f"{g['group']} / {g['subgroup']}" if g.get("subgroup") else g["group"]
            if label in skip or (g.get("subgroup") or g["group"]) in skip:
                continue
            for t in g["links"]:
                cand[t].setdefault("navbox", label)
                nav_titles.append(t)
    # `index` is one page or a list of them (a large field has an outline, an index and a glossary)
    idx = hc.get("index")
    for page in [idx] if isinstance(idx, str) else idx or []:
        for t in H.index_page(client, page):
            cand[t]["index"] = True
    for spec in hc.get("vital") or []:
        for t in H.vital_section(client, spec):
            cand[t]["vital"] = True
    # `importance` limits the WikiProject levels read: a field with 14,000 Low-importance pages lists Top to Mid
    imp = (H.wikiproject_importance(client, hc["wikiproject"], hc.get("importance") or H.IMPORTANCE)
           if hc.get("wikiproject") else {})
    for t, i in imp.items():
        cand[t]["importance"] = i
    cats = cfg.get("categories") or {}
    tree = {"categories": {}, "pages": {}}
    if cats.get("roots"):
        tree = H.category_tree(client, cats["roots"], int(cats.get("depth") or 1), cats.get("exclude") or [])
        for t, d in tree["pages"].items():
            cand[t]["catdist"] = d
    for t in cfg.get("seeds") or []:
        cand[t]["seed"] = True
    # seeds pinned to a chapter in subject.yaml are candidates even when no hub lists them
    for p in (cfg.get("frame") or {}).get("parts") or []:
        for ch in p.get("chapters") or []:
            for t in ch.get("seeds") or []:
                cand[t]["seed"] = True
    for t in (cfg.get("frame") or {}).get("foundations") or []:
        cand[t]["foundation"] = True
    log(f"[frame] {len(cand)} candidates: navbox {len(set(nav_titles))}, index "
        f"{sum(1 for c in cand.values() if c.get('index'))}, vital {sum(1 for c in cand.values() if c.get('vital'))}, "
        f"wikiproject {len(imp)}, categories {len(tree['pages'])} pages in {len(tree['categories'])} categories")
    # canonical titles + metadata, 50 per request
    resolved = prescreen(client, store, list(cand))
    merged = defaultdict(dict)
    for t, c in cand.items():
        can = resolved.get(t, t)
        m = merged[can]
        for k, v in c.items():
            if k == "catdist":
                m[k] = min(v, m.get(k, 9))
            elif k == "importance":
                m[k] = min((m.get(k), v), key=lambda x: list(IMP_CORE).index(x) if x in IMP_CORE else 9) or v
            else:
                m.setdefault(k, v)
    store.flush_caches()
    return merged, tree


def core(c, title, include_terms):
    s = 0
    s += 2 if c.get("navbox") else 0
    s += 1 if c.get("index") else 0
    s += 3 if c.get("vital") else 0
    s += IMP_CORE.get(c.get("importance"), 0)
    s += {0: 2, 1: 1}.get(c.get("catdist"), 0)
    s += 1 if any(re.search(rf"(?<![a-z]){re.escape(t)}", title.lower()) for t in include_terms) else 0
    s += 10 if c.get("foundation") or c.get("seed") else 0
    return s


def build(subject, scout=100, refresh=False, log=print, client=None, store=None, registry=None):
    client, store = client or WikiClient(), store or Store()
    if refresh:
        hc = subject.cfg.get("hubs") or {}
        for tpl in hc.get("navboxes") or []:
            H.drop(f"navbox {tpl}")
    cand, tree = gather(subject, client, store, log)
    fcfg = subject.cfg.get("frame") or {}
    include = [t.lower() for t in subject.cfg["scope"].get("include_terms") or []]
    exclude = [t.lower() for t in subject.cfg["scope"].get("exclude_terms") or []]
    excl_cats = {c.removeprefix("Category:").lower() for c in subject.cfg["categories"].get("exclude") or []}
    drop_prefixes = [x.lower() for x in fcfg.get("drop_category_prefixes") or []]

    kept, dropped = {}, Counter()
    for t, c in cand.items():
        m = store.meta.get(t) or {}
        if m.get("missing") or m.get("disambig"):
            dropped["missing or disambiguation"] += 1
            continue
        cats = [x.lower() for x in m.get("categories") or []]
        if any(x.startswith(pre) for x in cats for pre in drop_prefixes) and not c.get("vital"):
            dropped["regional page without global significance"] += 1
            continue
        if any(x in excl_cats for x in cats) and not (c.get("navbox") or c.get("vital") or c.get("foundation")):
            dropped["excluded category"] += 1
            continue
        if c.get("catdist", 0) >= 2 and not any(c.get(k) for k in ("navbox", "index", "vital", "importance")):
            if not any(re.search(rf"(?<![a-z]){re.escape(x)}", t.lower()) for x in include):
                dropped["category depth 2 without another signal"] += 1
                continue
        low = (t + " " + (m.get("description") or "")).lower()
        if any(re.search(rf"(?<![a-z]){re.escape(x)}", low) for x in exclude) and not (c.get("navbox") or c.get("vital")):
            dropped["exclude term"] += 1
            continue
        c["core"] = core(c, t, include)
        c["description"] = m.get("description") or ""
        c["categories"] = m.get("categories") or []
        c["qid"] = m.get("qid")
        kept[t] = c

    # scout crawl: seeds + the most central candidates
    ranked = sorted(kept, key=lambda t: (-kept[t]["core"], t))
    n_fetched = 0
    registry = registry or Registry.from_subject(subject, wiki_client=client)
    for t in ranked[:scout]:
        if is_qualified(t) and not registry.allowed(t):
            log(f"  [scout] {t}: skipped, no source in subject.yaml allows it")
            continue
        try:
            _, _, status = fetch_page(client, store, t, adapters=registry)
            n_fetched += status == "fetched"
        except Exception as e:  # a missing page never stops the scout
            log(f"  [scout] {t}: {e}")
    store.flush_caches()

    # parts
    # no parts in subject.yaml: one part named for the subject, chapters by category clustering
    parts_cfg = fcfg.get("parts") or [{"key": "main", "title": subject.title}]
    single = parts_cfg[0]["key"] if len(parts_cfg) == 1 else None
    is_person = person_re(subject.cfg["scope"].get("person_terms"))
    nav_parts = fcfg.get("navbox_parts") or {}
    foundations = set(fcfg.get("foundations") or [])
    hist_key = next((p["key"] for p in parts_cfg if p.get("history")), None)
    found_key = next((p["key"] for p in parts_cfg if p.get("foundations")), None)
    assign = {}
    # a seed Wikipedia redirects ("Representational state transfer" -> "REST") is a candidate under its canonical
    # title, so it is pinned under that title too
    pinned_part = {store.canonical(t): p["key"] for p in parts_cfg for ch in p.get("chapters") or []
                   for t in ch.get("seeds") or []}
    for t, c in kept.items():
        if t in pinned_part:
            assign[t] = pinned_part[t]
            continue
        if (t in foundations or c.get("foundation")) and found_key:
            assign[t] = found_key
            continue
        desc = c["description"]
        if hist_key and (is_person.search(desc) or ORG_RE.search(t + " " + desc) or t.lower().startswith("history of")):
            assign[t] = hist_key
            continue
        scores = {p["key"]: _hint_score(p.get("hints"), t, desc, c["categories"]) for p in parts_cfg
                  if not p.get("foundations")}
        best = max(scores.items(), key=lambda kv: kv[1]) if scores else (None, 0)
        if best[1] > 0:
            assign[t] = best[0]
        elif single:
            assign[t] = single
        elif c.get("navbox"):
            for label, key in nav_parts.items():
                if c["navbox"].endswith(label) or c["navbox"] == label:
                    assign[t] = key
                    break
    unassigned = sorted((t for t in kept if t not in assign), key=lambda t: -kept[t]["core"])

    frame_parts = []
    target_total = int(subject.targets.get("entries") or 0)  # 0: shares only, the course is as long as it needs
    weights = {}
    for p in parts_cfg:
        members = [t for t in kept if assign.get(t) == p["key"]]
        chapters = _chapters(p, members, kept, store.canonical)
        fp = {"key": p["key"], "title": p["title"], "chapters": chapters}
        if p.get("question"):
            fp["question"] = True
        frame_parts.append(fp)
        for ch in chapters:
            weights[(p["key"], ch["title"])] = sum(kept[t]["core"] for t in ch["seeds"] + ch.get("candidates", [])) or 1
    total_w = sum(weights.values()) or 1
    for fp in frame_parts:
        for ch in fp["chapters"]:
            share = weights[(fp["key"], ch["title"])] / total_w
            ch["share"] = round(share, 4)
            if target_total:
                ch["target"] = max(1, round(share * target_total))

    doc = {"subject": subject.slug, "status": DRAFT_STATUS,
           "note": "Edit freely: reorder parts and chapters, move seeds, rename. Seeds are forced into the crawl; "
                   "candidates are crawled only if they pass the scope threshold. `share` is the chapter's share "
                   "of the entry target.", "parts": frame_parts}
    if subject.frame_path.exists() and (subject.frame or {}).get("status") != DRAFT_STATUS:
        out = subject.dir / "frame.draft.yaml"
        log(f"[frame] frame.yaml has been edited by hand; wrote the new draft to {out.name} instead")
    else:
        out = subject.frame_path
    atomic_write(out, yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=110))

    # scope inputs + calibration set
    hubs_doc = {"categories": tree["categories"], "category_pages": tree["pages"],
                "navbox": [t for t, c in kept.items() if c.get("navbox")],
                "index": [t for t, c in kept.items() if c.get("index")],
                "vital": [t for t, c in kept.items() if c.get("vital")],
                "importance": {t: c["importance"] for t, c in cand.items() if c.get("importance")},
                "forced": sorted({s for fp in frame_parts for ch in fp["chapters"] for s in ch["seeds"]})}
    save_hubs(subject, hubs_doc)
    sc = Scope(subject, hubs_doc)
    rows = []
    for t, c in cand.items():
        m = store.meta.get(t) or {}
        if m.get("missing") or m.get("disambig") or t in hubs_doc["forced"] or is_qualified(t):
            continue
        s, why = sc.score(t, m)
        rows.append({"title": t, "score": s, "reasons": why, "description": m.get("description") or ""})
    cal = write_calibration(subject, rows)
    _report(subject, frame_parts, kept, unassigned, dropped, n_fetched, cal)
    n_seeds = sum(len(ch["seeds"]) for fp in frame_parts for ch in fp["chapters"])
    log(f"[frame] {len(kept)} kept ({sum(dropped.values())} dropped), {len(frame_parts)} parts, "
        f"{sum(len(fp['chapters']) for fp in frame_parts)} chapters, {n_seeds} seeds, {len(unassigned)} unassigned; "
        f"scout fetched {n_fetched} pages; {client.requests_made} requests -> {out.name}")
    return doc


def _chapters(p, members, kept, canon=lambda t: t):
    """Chapters of one part: by chapter hints if given, else by category clustering."""
    chs_cfg = p.get("chapters") or []
    groups = defaultdict(list)
    if chs_cfg:
        pinned = {canon(t): ch["title"] for ch in chs_cfg for t in ch.get("seeds") or []}
        for t in members:
            c = kept[t]
            if t in pinned:
                groups[pinned[t]].append(t)
                continue
            sc = [(_hint_score(ch.get("hints"), t, c["description"], c["categories"]), -k)
                  for k, ch in enumerate(chs_cfg)]
            best = max(sc)
            groups[chs_cfg[-best[1]]["title"] if best[0] > 0 else f"{p['title']}: other topics"].append(t)
        order = [ch["title"] for ch in chs_cfg] + [f"{p['title']}: other topics"]
    else:
        left = set(members)
        order = []
        while left:
            cnt = Counter(c for t in left for c in kept[t]["categories"])
            cat, n = cnt.most_common(1)[0] if cnt else (None, 0)
            if not cat or n < 3:
                break
            title = cat
            mem = [t for t in left if cat in kept[t]["categories"]]
            groups[title] += mem
            order.append(title)
            left -= set(mem)
        if left:
            groups[f"{p['title']}: other topics"] += sorted(left)
            order.append(f"{p['title']}: other topics")
    out = []
    for title in order:
        mem = sorted(groups.get(title, []), key=lambda t: (-kept[t]["core"], t))
        if not mem:
            continue
        seeds = [t for t in mem if kept[t]["core"] >= SEED_MIN]
        cands = [t for t in mem if kept[t]["core"] < SEED_MIN]
        cc = next((c for c in chs_cfg if c.get("title") == title), {})
        ch = {"key": cc.get("key") or slug(title, 40), "title": title, "seeds": seeds}
        if cc.get("question"):
            ch["question"] = True
        if cands:
            ch["candidates"] = cands
        out.append(ch)
    return out


def _report(subject, parts, kept, unassigned, dropped, n_fetched, cal_path):
    L = [f"# Frame report: {subject.title}", "",
         f"Draft frame from the hubs in subject.yaml. {len(kept)} candidate articles kept; scout crawl fetched "
         f"{n_fetched} new pages. Calibration set: `{cal_path.relative_to(subject.dir)}` (label each row in/out).", "",
         "## Dropped", ""] + [f"- {k}: {v}" for k, v in dropped.most_common()] + ["", "## Parts", ""]
    for p in parts:
        n = sum(len(c["seeds"]) + len(c.get("candidates", [])) for c in p["chapters"])
        L.append(f"### {p['title']} ({n} articles)")
        L.append("")
        for c in p["chapters"]:
            target = f", target {c['target']}" if c.get("target") else ""
            L.append(f"- **{c['title']}** (share {c['share']:.1%}{target}): "
                     + ", ".join(c["seeds"][:25]) + (" …" if len(c["seeds"]) > 25 else "")
                     + (f" — plus {len(c.get('candidates', []))} candidates" if c.get("candidates") else ""))
        L.append("")
    L += ["## Unassigned (no hint matched; most central first)", "",
          ", ".join(f"{t} ({kept[t]['core']})" for t in unassigned[:150]), ""]
    subject.reports_dir.mkdir(parents=True, exist_ok=True)
    atomic_write(subject.reports_dir / "frame_report.md", "\n".join(L))
