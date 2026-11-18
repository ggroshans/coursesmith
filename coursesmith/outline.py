"""A subject's outline: the tree of headings its entries hang from.

Pedagogical subjects have two levels from frame.yaml (parts -> chapters). Chronological subjects can carry a
deeper tree in frame.yaml under `outline:` (earth history: eon -> era -> period -> epoch -> age), each node
with its time span. Every entry resolves to a path of node ids from the root to its leaf; chapter openers
and chapter reviews are keyed by node id.
"""
from .util import slug


class Outline:
    def __init__(self, nodes):
        self.nodes = {n["id"]: n for n in nodes}
        self.order = [n["id"] for n in nodes]
        self._by_title = {}
        for n in nodes:
            self._by_title.setdefault((n.get("parent"), n["title"].lower()), n["id"])

    @classmethod
    def from_subject(cls, subject):
        fr = subject.frame or {}
        if fr.get("outline"):
            return cls([dict(n) for n in fr["outline"]])
        nodes = []
        for p in fr.get("parts") or []:
            pid = p.get("id") or p.get("key") or slug(p["title"])
            nodes.append({"id": pid, "title": p["title"], "level": 1, "parent": None})
            for c in p.get("chapters") or []:
                cid = c.get("id") or c.get("key") or slug(c["title"])
                nodes.append({"id": cid, "title": c["title"], "level": 2, "parent": pid,
                              "share": c.get("share"), "seeds": c.get("seeds") or []})
        return cls(nodes)

    def add(self, node):
        if node["id"] not in self.nodes:
            self.nodes[node["id"]] = node
            self.order.append(node["id"])
            self._by_title.setdefault((node.get("parent"), node["title"].lower()), node["id"])
        return node["id"]

    def chain(self, nid):
        out, seen = [], set()
        while nid and nid in self.nodes and nid not in seen:
            seen.add(nid)
            out.append(nid)
            nid = self.nodes[nid].get("parent")
        return list(reversed(out))

    def title(self, nid):
        return self.nodes[nid]["title"] if nid in self.nodes else nid

    def children(self, nid):
        return [i for i in self.order if self.nodes[i].get("parent") == nid]

    def leaves(self):
        parents = {n.get("parent") for n in self.nodes.values()}
        return [i for i in self.order if i not in parents]

    def entry_path(self, e):
        """Node ids from the root to the entry's leaf. Unknown parts/chapters are added on the fly."""
        if e.get("path"):
            return [p for p in e["path"] if p in self.nodes] or list(e["path"])
        part, chap = e.get("part"), e.get("chapter")
        pid = self._by_title.get((None, (part or "").lower())) if part else None
        if part and not pid:
            pid = self.add({"id": slug(part), "title": part, "level": 1, "parent": None})
        if not chap:
            return [pid] if pid else []
        cid = self._by_title.get((pid, chap.lower()))
        if not cid:
            cid = self.add({"id": f"{pid}--{slug(chap)}" if pid else slug(chap), "title": chap, "level": 2,
                            "parent": pid})
        return [pid, cid] if pid else [cid]

    def leaf(self, e):
        p = self.entry_path(e)
        return p[-1] if p else None
