"""The concept graph: one node per crawled article, weighted edges, and per-node importance, difficulty and
chapter, plus RefD prerequisite scores.

    coursesmith graph build <subject> [--pageviews]

Edges: a link from A's lead weighs 3, a link from A's body 1; two articles in the same navbox group get +1;
two seeds of the same frame chapter +2, of the same part +0.5.

Importance = WikiProject importance (Top 8, High 6, Mid 4, Low 2) + 2 log(1 + in-scope inlinks)
             + Vital 3 + navbox 1 [+ 0.5 log10(pageviews) with --pageviews;
             counts from earlier builds are kept, so --pageviews only fetches new pages].
Difficulty = lexical complexity of the lead (share of long words, mean sentence length) + depth in the frame.
Chapter    = the frame chapter whose seeds the node is most strongly tied to (seeds keep their own chapter).

RefD (Liang et al., EMNLP 2015): represent each concept by the articles it links to. B is a prerequisite of
A when A's neighbors refer to B more than B's neighbors refer to A:
    RefD(A, B) = |L(A) & In(B)| / |L(A)| - |L(B) & In(A)| / |L(B)|, kept when > theta (0.05).
Computed only for linked pairs, which is where prerequisites live.
"""
import math
import re
from collections import defaultdict

from ..crawl.api import WikiClient
from ..crawl.scope import Scope
from ..crawl.store import Store, crawled_titles
from ..frame import hubs as H
from ..util import read_json, write_json

THETA = 0.05
IMP = {"Top": 8, "High": 6, "Mid": 4, "Low": 2}
LONG_WORD = re.compile(r"\b[a-zA-Z]{10,}\b")


def frame_index(subject):
    """seed title -> (part key, chapter key, part index, chapter index)."""
    out = {}
    for pi, p in enumerate((subject.frame or {}).get("parts") or []):
        for ci, c in enumerate(p.get("chapters") or []):
            for t in c.get("seeds") or []:
                out.setdefault(t, (p.get("key"), c.get("key"), pi, ci))
    return out


def chapters(subject):
    """[(part key, chapter key, part title, chapter title)] in frame order."""
    out = []
    for p in (subject.frame or {}).get("parts") or []:
        for c in p.get("chapters") or []:
            out.append((p.get("key"), c.get("key"), p["title"], c["title"]))
    return out


def _lead_stats(text):
    lead = []
    for line in text.splitlines()[1:]:
        if line.startswith("#"):
            break
        if line.strip() and " | " not in line:
            lead.append(line)
    t = " ".join(lead)
    words = re.findall(r"[A-Za-z]+", t)
    sents = max(1, len(re.findall(r"[.!?](\s|$)", t)))
    if not words:
        return 0.5
    long_share = len(LONG_WORD.findall(t)) / len(words)
    mean_len = len(words) / sents
    return round(min(1.0, long_share * 2.5 + max(0.0, mean_len - 15) / 40), 3)


def build(subject, pageviews=False, log=print):
    store = Store()
    scope = Scope(subject)
    hubs = read_json(subject.scope_dir / "hubs.json", {}) or {}
    titles = [t for t in crawled_titles(subject) if store.has_page(t)]
    if not titles:
        raise SystemExit("nothing crawled yet; run `coursesmith crawl` first")
    crawled = set(titles)
    fidx = frame_index(subject)
    nav_groups = []
    for tpl in (subject.cfg.get("hubs") or {}).get("navboxes") or []:
        try:
            nav_groups += [set(store.canonical(t) for t in g["links"]) for g in H.navbox(None, tpl)]
        except AttributeError:  # not cached yet
            pass

    nodes, links, lead = {}, {}, {}
    for t in titles:
        rec = store.load_page(t)
        body = [store.canonical(l) for l in rec.get("body_links") or []]
        ll = [store.canonical(l) for l in rec.get("lead_links") or []]
        links[t] = {l for l in body if l in crawled and l != t}
        lead[t] = [l for l in dict.fromkeys(ll) if l in crawled and l != t]
        meta = {"categories": rec.get("categories"), "description": (store.meta.get(t) or {}).get("description")}
        s, _ = scope.score(t, meta)
        nodes[t] = {"in_scope": t in scope.forced or t in fidx or s >= scope.threshold, "scope_score": s,
                    "qid": (store.meta.get(t) or {}).get("qid"), "importance_class": hubs.get("importance", {}).get(t),
                    "vital": t in set(hubs.get("vital") or []), "navbox": t in set(hubs.get("navbox") or []),
                    "difficulty_lex": _lead_stats(store.load_text(t)), "lead_links": lead[t],
                    "url": rec["url"], "revid": rec.get("revid")}
    inl = defaultdict(set)
    for a, ls in links.items():
        for b in ls:
            inl[b].add(a)

    # edges
    w = defaultdict(float)
    for a in titles:
        for b in links[a]:
            w[(a, b)] += 3.0 if b in lead[a] else 1.0
    for g in nav_groups:
        mem = sorted(g & crawled)
        if len(mem) > 60:
            continue  # huge groups (a soil-type list) say little about any pair
        for i, a in enumerate(mem):
            for b in mem[i + 1:]:
                w[(a, b)] += 1.0
                w[(b, a)] += 1.0
    by_chapter, by_part = defaultdict(list), defaultdict(list)
    for t, (pk, ck, _, _) in fidx.items():
        if t in crawled:
            by_chapter[(pk, ck)].append(t)
            by_part[pk].append(t)
    for mem in by_chapter.values():
        for a in mem:
            for b in mem:
                if a != b:
                    w[(a, b)] += 2.0
    for mem in by_part.values():
        if len(mem) <= 150:
            for a in mem:
                for b in mem:
                    if a != b:
                        w[(a, b)] += 0.5

    # importance, difficulty
    # pageviews fetched by an earlier build are kept; --pageviews fetches only pages that have none yet
    views = {t: n["pageviews"] for t, n in (load(subject).get("nodes") or {}).items()
             if n.get("pageviews") is not None}
    if pageviews:
        client = WikiClient()
        for t in titles:
            if nodes[t]["in_scope"] and t not in views:
                views[t] = client.pageviews(t)
    for t, n in nodes.items():
        n_in = sum(1 for a in inl[t] if nodes[a]["in_scope"])
        imp = IMP.get(n["importance_class"], 0) + 2 * math.log1p(n_in) + 3 * n["vital"] + 1 * n["navbox"]
        if t in views:
            imp += 0.5 * math.log10(views[t] + 1)
            n["pageviews"] = views[t]
        n["inlinks_in_scope"] = n_in
        n["importance"] = round(imp, 3)
        depth = 0.0 if fidx.get(t, (None,))[0] == "found" else (0.5 if t in fidx else 1.0)
        n["difficulty"] = round(0.7 * n["difficulty_lex"] + 0.3 * depth, 3)

    # chapter assignment
    seeds_of = {k: set(v) for k, v in by_chapter.items()}
    for t, n in nodes.items():
        if t in fidx:
            n["part"], n["chapter"] = fidx[t][0], fidx[t][1]
            continue
        if not n["in_scope"]:
            n["part"] = n["chapter"] = None
            continue
        best, best_s = None, 0.0
        for k, mem in seeds_of.items():
            sc = sum(w.get((t, m), 0) + w.get((m, t), 0) for m in mem)
            if sc > best_s:
                best, best_s = k, sc
        n["part"], n["chapter"] = best if best else (None, None)

    # RefD for linked pairs of in-scope nodes
    refd = defaultdict(dict)
    pairs = set()
    for a in titles:
        if not nodes[a]["in_scope"]:
            continue
        for b in links[a]:
            if nodes[b]["in_scope"]:
                pairs.add((a, b))
                pairs.add((b, a))
    for a, b in pairs:
        la, lb = links[a], links[b]
        if not la or not lb:
            continue
        r = len(la & inl[b]) / len(la) - len(lb & inl[a]) / len(lb)
        if r > THETA:
            refd[a][b] = round(r, 3)

    edges = [[a, b, round(v, 2)] for (a, b), v in w.items() if v >= 1.0]
    doc = {"subject": subject.slug, "theta": THETA, "nodes": nodes, "edges": edges, "refd": refd}
    write_json(subject.graph_path, doc, indent=None)
    n_scope = sum(1 for n in nodes.values() if n["in_scope"])
    n_assigned = sum(1 for n in nodes.values() if n.get("chapter"))
    log(f"[graph] {len(nodes)} nodes ({n_scope} in scope, {n_assigned} with a chapter), {len(edges)} edges, "
        f"{sum(len(v) for v in refd.values())} RefD prerequisite pairs > {THETA}")
    return doc


def load(subject):
    return read_json(subject.graph_path) or {"nodes": {}, "edges": [], "refd": {}}
