"""The subject crawl: priority-ordered breadth-first search from the seeds and the frame's articles.

    coursesmith crawl <subject> [--chapter KEY] [--max-pages N] [--depth D] [--resume]

Priority = scope score - DEPTH_PENALTY * depth; frame articles (and the subject's seeds) are forced in with a
high priority. Only in-scope pages are expanded. A link is pre-screened (categories, description) only if its
best possible score could still reach the threshold, which keeps the request count down at <= 0.5 req/s.
Borderline links go to scope/frontier_review.csv for a skim; rejected ones to scope/frontier_rejected.csv.

--chapter limits the forced set to one frame chapter (the pilot), --depth 1 keeps the crawl to the frame
articles and their direct in-scope links. --hubs also queues every hub-list page (navboxes, index, Vital, the
WikiProject table, the category tree, from scope/hubs.json) that passes the threshold on its metadata, one hop
below the frame, so the hub lists are crawled rather than reached only by links. --judged queues every page the
scope judge marked in or support (scope/judge.json), not expanded.
"""
import csv
import heapq

from ..sources.base import MissingSource, SourceError
from ..sources.keys import is_qualified
from ..sources.registry import Registry
from ..util import read_json, write_json
from .api import ApiError, MissingPage, WikiClient
from .fetch import fetch_page, prescreen
from .scope import Scope
from .store import Store, append_ledger, append_rejected, read_ledger

DEPTH_PENALTY = 1.5
META_BONUS_MAX = 5  # what link metadata can add on top of a title-only score: category +4, description +1


def frame_articles(subject, chapter=None):
    """Seed articles of every frame chapter (or of one chapter, by key, id or title)."""
    out = []
    for p in (subject.frame or {}).get("parts") or []:
        for c in p.get("chapters") or []:
            keys = {str(c.get("key") or ""), str(c.get("id") or ""), c.get("title", "").lower()}
            if chapter and chapter.lower() not in {k.lower() for k in keys if k}:
                continue
            out += (c.get("seeds") or []) + (c.get("also") or [] if chapter else [])
    return list(dict.fromkeys(out))


class Crawler:
    def __init__(self, subject, chapter=None, max_pages=300, max_depth=2, client=None, store=None, log=print,
                 hubs=False, judged=False, registry=None):
        self.s, self.log, self.hubs, self.judged = subject, log, hubs, judged
        self.client, self.store = client or WikiClient(), store or Store()
        self.registry = registry or Registry.from_subject(subject, wiki_client=self.client)
        self.scope = Scope(subject, registry=self.registry)
        self.max_pages, self.max_depth = max_pages, max_depth
        source_seeds = [] if chapter else list(getattr(self.registry, "all_seeds", lambda: [])())
        self.forced = list(dict.fromkeys(
            frame_articles(subject, chapter) + ([] if chapter else list(subject.cfg.get("seeds") or [])) + source_seeds))
        self.scope.forced |= set(self.forced)
        self.state_path = subject.scope_dir / f"crawl_state{'_' + chapter if chapter else ''}.json"
        self.heap, self.counter = [], 0
        self.visited = {r["title"] for r in read_ledger(subject) if r["status"].startswith(("fetched", "cached"))}
        self.queued = set()
        self.rejected_seen = set()
        self.review_path = subject.scope_dir / "frontier_review.csv"
        self.n_done = 0

    def push(self, title, depth, parent, priority, reason):
        if title in self.queued or title in self.visited:
            return
        self.queued.add(title)
        self.counter += 1
        heapq.heappush(self.heap, (-priority, self.counter, title, depth, parent, reason))

    def seed(self):
        resolved = prescreen(self.client, self.store, self.forced)
        for t in self.forced:
            if is_qualified(t) and not self.registry.allowed(t):
                self.log(f"[crawl] skipped seed '{t}': no source in subject.yaml allows it")
                continue
            self.push(resolved.get(t, t), 0, "", 100.0, "frame")
        if self.hubs:
            self.seed_hubs()
        if self.judged:
            n = 0
            for t, v in self.scope.judge.items():
                if v.get("v") in ("in", "support") and t not in self.visited:
                    self.push(t, self.max_depth, "", 60.0, f"judge-{v['v']}")
                    n += 1
            self.log(f"[crawl] judged: {n} pages queued")

    def hub_titles(self):
        h = read_json(self.s.scope_dir / "hubs.json", {}) or {}
        out = list(h.get("navbox") or []) + list(h.get("index") or []) + list(h.get("vital") or [])
        out += list(h.get("importance") or {}) + list(h.get("category_pages") or {})
        return list(dict.fromkeys(out))

    def seed_hubs(self):
        """Queue every hub-list page that passes the threshold on its metadata, one hop below the frame."""
        titles = self.hub_titles()
        resolved = prescreen(self.client, self.store, titles)
        thr, n = self.scope.threshold, 0
        depth = max(self.max_depth - 1, 0)
        for t in titles:
            c = resolved.get(t, t)
            if c in self.visited or c in self.queued:
                continue
            s, why = self.scope.score(c, self.store.meta.get(c))
            if s >= thr:
                self.push(c, depth, "", 50.0 + s, "hub list; " + "; ".join(why))
                n += 1
        self.store.flush_caches()
        self.log(f"[crawl] hubs: {n} hub-list pages queued of {len(titles)}")

    def save_state(self):
        write_json(self.state_path, {"heap": self.heap, "counter": self.counter, "queued": sorted(self.queued)})

    def load_state(self):
        st = read_json(self.state_path)
        if not st:
            return False
        self.heap = [tuple(x) for x in st["heap"]]
        heapq.heapify(self.heap)
        self.counter, self.queued = st["counter"], set(st["queued"])
        return True

    def run(self, resume=False):
        if not (resume and self.load_state()):
            self.seed()
        thr = self.scope.threshold
        # inlinks from pages crawled earlier count toward the share-of-inlinks signal
        for t in list(self.visited):
            if self.store.has_page(t):
                for l in self.store.load_page(t).get("body_links") or []:
                    self.scope.add_inlink(self.store.canonical(l), t)
        while self.heap and self.n_done < self.max_pages:
            negp, _, title, depth, parent, reason = heapq.heappop(self.heap)
            title = self.store.canonical(title)
            if title in self.visited:
                continue
            try:
                rec, text, status = fetch_page(self.client, self.store, title, adapters=self.registry)
            except (MissingPage, MissingSource):
                append_ledger(self.s, {"title": title, "depth": depth, "linked_from": parent, "status": "missing"})
                continue
            except (ApiError, SourceError) as e:
                append_ledger(self.s, {"title": title, "depth": depth, "linked_from": parent,
                                       "status": f"error: {e}"[:200]})
                continue
            self.visited.add(rec["title"])
            self.n_done += 1
            score, why = self.scope.score(rec["title"], {"categories": rec.get("categories"),
                                                          "description": (self.store.meta.get(rec["title"]) or {}).get("description")})
            append_ledger(self.s, {"title": rec["title"], "url": rec["url"],
                                   "revid": rec.get("revid") if rec.get("revid") is not None else rec.get("version"),
                                   "depth": depth, "linked_from": parent, "in_scope_reason": reason,
                                   "score": score, "status": status})
            for l in rec.get("body_links") or []:
                self.scope.add_inlink(self.store.canonical(l), rec["title"])
            if depth < self.max_depth and (rec["title"] in self.scope.forced or score >= thr):
                self.expand(rec, depth)
            if self.n_done % 10 == 0:
                self.store.flush_caches()
                self.save_state()
                self.log(f"[crawl] {self.n_done} pages ({self.client.requests_made} requests), queue {len(self.heap)}")
        self.store.flush_caches()
        self.save_state()
        self.log(f"[crawl] done: {self.n_done} pages this run, {len(self.visited)} total for {self.s.slug}; "
                 f"{self.client.requests_made} requests, queue {len(self.heap)} left")
        return self.n_done

    def expand_qualified(self, key, rec, depth):
        """A link into another source: followed only inside that source's allowlist and hop limit."""
        ad = self.registry.maybe_for_key(key)
        if ad is not None and ad.allowed(key) and depth + 1 <= ad.max_depth:
            s, why = self.scope.score(key)
            self.push(key, depth + 1, rec["title"], s - DEPTH_PENALTY * (depth + 1), f"allowlist:{ad.label}")
        elif key not in self.rejected_seen:
            self.rejected_seen.add(key)
            why = "outside the sources allowlist" if ad is None or not ad.allowed(key) else "beyond the source's depth"
            append_rejected(self.s, {"title": key, "linked_from": rec["title"], "depth": depth + 1,
                                     "score": 0, "reasons": why})

    def expand(self, rec, depth):
        thr = self.scope.threshold
        links = [l for l in dict.fromkeys(rec.get("body_links") or []) if self.store.canonical(l) not in self.visited]
        # title-only bound first: skip the pre-screen for links that cannot reach the threshold
        hopeful = []
        for l in links:
            c = self.store.canonical(l)
            if is_qualified(c):
                self.expand_qualified(c, rec, depth)
                continue
            s0, _ = self.scope.score(c, self.store.meta.get(c))
            if c in self.store.meta or s0 + META_BONUS_MAX >= thr:
                hopeful.append(l)
            elif c not in self.rejected_seen:
                self.rejected_seen.add(c)
                append_rejected(self.s, {"title": c, "linked_from": rec["title"], "depth": depth + 1,
                                         "score": s0, "reasons": "title-only bound below threshold"})
        resolved = prescreen(self.client, self.store, hopeful)
        review = []
        for l in hopeful:
            c = resolved.get(l, l)
            s, why = self.scope.score(c, self.store.meta.get(c))
            pri = s - DEPTH_PENALTY * (depth + 1)
            if s >= thr:
                self.push(c, depth + 1, rec["title"], pri, "; ".join(why))
                if s <= thr + 1:
                    review.append((c, s, why))
            else:
                if s >= thr - 2:
                    review.append((c, s, why))
                if c not in self.rejected_seen:
                    self.rejected_seen.add(c)
                    append_rejected(self.s, {"title": c, "linked_from": rec["title"], "depth": depth + 1,
                                             "score": s, "reasons": "; ".join(why)})
        if review:
            new = not self.review_path.exists()
            with self.review_path.open("a", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                if new:
                    w.writerow(["title", "score", "threshold", "linked_from", "reasons"])
                for c, s, why in review:
                    w.writerow([c, s, thr, rec["title"], "; ".join(why)])


def crawl(subject, chapter=None, max_pages=300, max_depth=2, resume=False, log=print, hubs=False, judged=False):
    return Crawler(subject, chapter, max_pages, max_depth, log=log, hubs=hubs, judged=judged).run(resume=resume)


def context(subject, max_pages=300, log=print):
    """Tier A of the verification: fetch every page linked from the lead of each selected entry's article (depth 1
    from the entry), so dossiers and the verification pass carry the context Wikipedia itself provides."""
    store = Store()
    sel = subject.entries(selected_only=True)
    want = []
    for e in sel:
        art = (e.get("article") or "").split("#")[0]
        if art and store.has_page(art):
            want += store.load_page(art).get("lead_links") or []
    want = list(dict.fromkeys(want))
    c = Crawler(subject, max_pages=max_pages, max_depth=0, store=store, log=log)
    c.seed = lambda: None  # only the lead links, not the frame articles
    resolved = prescreen(c.client, store, want)
    for t in want:
        c.push(resolved.get(t, t), 0, "lead link", 50.0, "context (tier A)")
    c.scope.forced |= {resolved.get(t, t) for t in want}
    log(f"[crawl] context: {len(want)} lead links of {len(sel)} selected entries")
    return c.run()
