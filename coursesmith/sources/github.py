"""A GitHub repository as a source: `gh>owner/repo/path/to/file.md`.

Pinned to a commit, so the same crawl reads the same text next month. Files come from raw.githubusercontent.com
(no API quota); the API is used only for the file tree, the license and resolving a branch or tag to a commit.
Set COURSESMITH_GITHUB_TOKEN (or GITHUB_TOKEN) to lift the 60 requests per hour of anonymous API use.

    - name: system-design-primer
      adapter: github
      repo: donnemartin/system-design-primer
      ref: ae9bbd7b02d90b9866215de185217d33f39ab733   # a commit; `sources check` suggests the current one
      include: ["README.md", "solutions/**/README.md"]
      exclude: ["**/README-*.md"]                      # translations
      seeds: ["README.md"]                             # crawled without listing them under `seeds:`
      split: {"README.md": 1}                          # a one-file course: each `# Chapter` becomes its own page
      depth: 1
      tier: curated
      license: {name: "CC BY 4.0"}

A split file is a page per section: `gh>owner/repo/README.md::load-balancing`. The slug is GitHub's own anchor
(so `[x](#load-balancing)` links resolve), the file's other sections are not part of a page, and the whole file
is not a page itself (its text would be counted twice). `coursesmith sources parts <subject>` lists the keys.
"""
import base64
import hashlib
import json
import os
import posixpath
import re
from urllib.parse import quote, unquote, urlparse

from . import licenses
from .base import MissingSource, SourceAdapter, SourceError, glob_match
from .keys import SEP, make_key
from ..text.markdown import markdown_to_doc

API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
TEXT_EXT = (".md", ".markdown", ".rst", ".txt")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def token():
    return os.environ.get("COURSESMITH_GITHUB_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""


PART = "::"


def slug_of(heading):
    """GitHub's anchor for a heading: lowercase, punctuation dropped, spaces to hyphens."""
    s = re.sub(r"[^\w\- ]", "", re.sub(r"`|\*|_(?=\w)|\[|\]", "", str(heading)).strip().lower())
    return re.sub(r"\s", "-", s).strip("-")


def split_markdown(md, level=1):
    """[(slug, title, markdown)] for each heading of `level` in the file, in order. A section runs to the next
    heading of the same or a shallower level, and its headings are shifted up so its own heading is a `#`. Text
    before the first such heading, and headings inside code fences, are not sections. A repeated heading gets
    `-1`, `-2` like GitHub's anchors."""
    from ..text.markdown import strip_front_matter
    lines, fence, marks = strip_front_matter(md).split("\n"), False, []
    for i, l in enumerate(lines):
        if re.match(r"^\s*(```|~~~)", l):
            fence = not fence
            continue
        m = None if fence else re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", l)
        if m:
            marks.append((i, len(m.group(1)), m.group(2).strip()))
    out, seen = [], {}
    for k, (i, lvl, title) in enumerate(marks):
        if lvl != level:
            continue
        end = next((j for j, l2, _ in marks[k + 1:] if l2 <= level), len(lines))
        body, fence2 = [], False
        for l in lines[i:end]:
            if re.match(r"^\s*(```|~~~)", l):
                fence2 = not fence2
            m = None if fence2 else re.match(r"^(#{1,6})(\s.*)$", l)
            body.append("#" * max(1, len(m.group(1)) - level + 1) + m.group(2) if m else l)
        slug = slug_of(title) or "section"
        n = seen.get(slug, 0)
        seen[slug] = n + 1
        out.append((slug if n == 0 else f"{slug}-{n}", title, "\n".join(body)))
    return out


def plain_to_doc(text, name=""):
    """A .txt or .rst file as cleaned text: blank-line paragraphs, RST underlined titles as headings."""
    lines, out, para = text.replace("\r\n", "\n").split("\n"), [f"# {name}"] if name else [], []

    def flush():
        if para:
            out.append(" ".join(l.strip() for l in para))
            para.clear()

    for i, l in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        if l.strip() and re.fullmatch(r"([=\-~^\"#*+])\1{2,}", nxt.strip()) and len(nxt.strip()) >= len(l.strip()) - 1:
            flush()
            out += ["", "## " + l.strip()]
            lines[i + 1] = ""
            continue
        if not l.strip():
            flush()
        else:
            para.append(l)
    flush()
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip() + "\n"


class GithubAdapter(SourceAdapter):
    adapter = "github"
    prefix = "gh"
    default_tier = "curated"
    default_depth = 1

    def __init__(self, cfg=None, http=None, defaults=None):
        super().__init__(cfg, http, defaults)
        repo = str(self.cfg.get("repo") or "")
        if repo.count("/") != 1:
            raise SourceError(f"github source '{self.cfg.get('name')}': repo must be owner/name, got '{repo}'")
        self.repo = repo
        self.owner, self.name = repo.split("/")
        self.include = self.cfg.get("include") or ["README.md", "**/*.md"]
        self.exclude = self.cfg.get("exclude") or []
        self.split = {str(p): int(l) for p, l in (self.cfg.get("split") or {}).items()}
        self._sha = None
        self._parts = {}

    @classmethod
    def for_discovery(cls, http=None):
        return cls({"name": "github", "repo": "search/search"}, http=http)

    def hosts(self):
        return ["github.com", "raw.githubusercontent.com", "api.github.com"]

    # -- keys ------------------------------------------------------------------------
    def _root(self):
        return f"gh{SEP}{self.repo}/"

    def path_of(self, key):
        """The file's path in the repository (a split section's key carries `::slug` after it)."""
        return key[len(self._root()):].split(PART, 1)[0]

    def part_of(self, key):
        rest = key[len(self._root()):]
        return rest.split(PART, 1)[1] if PART in rest else None

    def key(self, path, part=None):
        return make_key("gh", f"{self.repo}/{path.lstrip('/')}" + (f"{PART}{part}" if part else ""))

    def owns(self, key):
        return key.lower().startswith(self._root().lower())

    def allowed(self, key):
        if not self.owns(key):
            return False
        p, part = self.path_of(key), self.part_of(key)
        if p in self.split and not part:
            return False  # a split file is its sections; the whole file would count its text twice
        if part and p not in self.split:
            return False
        return p.lower().endswith(TEXT_EXT) and glob_match(p, self.include) and not glob_match(p, self.exclude)

    def seeds(self):
        return [self.key(p) for p in self.cfg.get("seeds") or []]

    def key_for_url(self, url, base_key=None):
        """A link in a markdown file: relative path, GitHub blob/tree URL of this repo, or a Wikipedia article."""
        href = url.strip()
        if href.startswith("#"):  # an anchor inside a split file points at that section
            here = self.path_of(base_key) if base_key and self.owns(base_key) else None
            slug = href[1:].strip().lower()
            return self.key(here, slug) if here in self.split and slug else None
        if not href or href.startswith(("mailto:", "javascript:")):
            return None
        u = urlparse(href)
        if u.scheme in ("http", "https"):
            host, path = u.netloc.lower(), unquote(u.path)
            if host.endswith("wikipedia.org") and path.startswith("/wiki/"):
                t = path[len("/wiki/"):].replace("_", " ").strip()
                return t if t and ":" not in t.split(" ")[0] else None
            m = re.match(rf"^/{re.escape(self.repo)}/(?:blob|tree)/[^/]+/(.+)$", path, re.I) \
                if host in ("github.com", "www.github.com") else \
                re.match(rf"^/{re.escape(self.repo)}/[^/]+/(.+)$", path, re.I) if host == "raw.githubusercontent.com" else None
            return self._path_key(m.group(1)) if m else None
        if u.scheme:
            return None
        base_dir = posixpath.dirname(self.path_of(base_key)) if base_key and self.owns(base_key) else ""
        target = unquote(u.path)
        joined = posixpath.normpath(posixpath.join(base_dir, target)) if not target.startswith("/") else target.lstrip("/")
        return self._path_key(joined, u.fragment)

    def _path_key(self, path, fragment=""):
        path = path.strip("/")
        if not path or path.startswith(".."):
            return None
        last = path.rsplit("/", 1)[-1]
        if "." not in last:  # a directory link: its README
            path = f"{path}/README.md"
        elif not path.lower().endswith(TEXT_EXT):
            return None
        if path in self.split:  # only a link to a section of a split file names a page
            return self.key(path, fragment.lower()) if fragment else None
        return self.key(path)

    # -- GitHub API ------------------------------------------------------------------
    def _headers(self):
        h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if token():
            h["Authorization"] = f"Bearer {token()}"
        return h

    def api(self, path, params=None, want_headers=False):
        url = f"{API}{path}"
        if params:
            url += "?" + "&".join(f"{k}={quote(str(v), safe=':>=<,+')}" for k, v in params.items())
        got = self.http.get(url, headers=self._headers(), want_headers=want_headers)
        body, meta = got if want_headers else (got, {})
        try:
            data = json.loads(body) if body else None
        except ValueError:
            raise SourceError(f"GitHub returned something that is not JSON for {path}")
        return (data, meta) if want_headers else data

    def sha(self):
        """The commit the crawl reads: `ref` if it is a commit, else the commit a branch or tag points at now."""
        if self._sha:
            return self._sha
        ref = str(self.cfg.get("ref") or "")
        if SHA_RE.match(ref):
            self._sha = ref
            return ref
        d = self.api(f"/repos/{self.repo}/commits/{quote(ref or 'HEAD', safe='')}")
        if not d or not d.get("sha"):
            raise SourceError(f"cannot resolve {self.repo}@{ref or 'HEAD'} to a commit (does the repo exist?)")
        self._sha = d["sha"]
        return self._sha

    def tree(self):
        d = self.api(f"/repos/{self.repo}/git/trees/{self.sha()}", {"recursive": 1})
        if not d:
            raise SourceError(f"no file tree for {self.repo}@{self.sha()}")
        return d

    def files(self):
        """Paths in the repo that match include/exclude, from the pinned commit's tree."""
        d = self.tree()
        return sorted(e["path"] for e in d.get("tree", []) if e.get("type") == "blob"
                      and self.key_allowed_path(e["path"]))

    def key_allowed_path(self, p):
        return p.lower().endswith(TEXT_EXT) and glob_match(p, self.include) and not glob_match(p, self.exclude)

    # -- fetching --------------------------------------------------------------------
    def parts(self, path):
        """[(slug, title, markdown)] of a split file at the pinned commit (cached for this run)."""
        if path not in self._parts:
            raw = self.http.get(f"{RAW}/{self.repo}/{self.sha()}/{quote(path)}")
            if raw is None:
                raise MissingSource(f"{self.repo}@{self.sha()[:7]}: no file {path}")
            self._parts[path] = split_markdown(raw, self.split[path])
        return self._parts[path]

    def fetch(self, key):
        path, part = self.path_of(key), self.part_of(key)
        sha = self.sha()
        if part:
            hit = next((p for p in self.parts(path) if p[0] == part), None)
            if hit is None:
                raise MissingSource(f"{self.repo}@{sha[:7]}: {path} has no section '{part}'")
            raw, fallback = hit[2], hit[1]
        else:
            raw = self.http.get(f"{RAW}/{self.repo}/{sha}/{quote(path)}")
            if raw is None:
                raise MissingSource(f"{self.repo}@{sha[:7]}: no file {path}")
            fallback = path.rsplit("/", 1)[-1]
        if path.lower().endswith((".md", ".markdown")):
            doc = markdown_to_doc(raw, resolve_link=lambda a: self.key_for_url(a.get("href", ""), key))
            text, dname, links, anchors, code = doc.text, doc.name, doc.links, doc.anchors, doc.code_blocks
            lead_links = doc.lead_links
        else:
            dname = fallback
            text, links, anchors, code, lead_links = plain_to_doc(raw, fallback), [], {}, 0, []
        title = self.cfg.get("title") or self.repo.split("/")[1]
        name = dname or fallback
        if (path != "README.md" or part) and name != title:
            name = f"{name} ({title})"
        links = [l for l in links if l != key]
        url = f"https://github.com/{self.repo}/blob/{sha}/{quote(path)}" + (f"#{part}" if part else "")
        rec = self.record(key, name, url, text, sha,
                          source_id=f"{self.repo}/{path}" + (f"{PART}{part}" if part else ""))
        rec.update({"body_links": links, "lead_links": [l for l in lead_links if l != key], "anchors": anchors})
        rec["meta"] = {"description": dname, "tags": [], "path": path, "part": part, "repo": self.repo, "ref": sha,
                       "code_blocks": code, "dates": bool(self.cfg.get("dates")), "hash": hashlib.sha256(raw.encode()).hexdigest()[:16]}
        return rec

    # -- presentation ----------------------------------------------------------------
    def permalink(self, src):
        return src.get("url") or ""

    def version_label(self, version):
        return f"commit {str(version)[:7]}" if version else ""

    # -- discovery and checks --------------------------------------------------------
    def contributors(self, repo):
        try:
            d, meta = self.api(f"/repos/{repo}/contributors", {"per_page": 1, "anon": "true"}, want_headers=True)
        except SourceError:
            return None
        link = (meta or {}).get("link") or ""
        m = re.search(r'[?&]page=(\d+)>; rel="last"', link)
        return int(m.group(1)) if m else (len(d) if isinstance(d, list) else None)

    def discover(self, query, limit=20):
        d = self.api("/search/repositories", {"q": f"{query} stars:>200", "sort": "stars", "order": "desc",
                                              "per_page": min(limit, 30)})
        out = []
        for it in (d or {}).get("items", [])[:limit]:
            lic = (it.get("license") or {}).get("spdx_id")
            out.append({"id": f"gh:{it['full_name']}", "adapter": "github", "repo": it["full_name"],
                        "title": it.get("name"), "url": it.get("html_url"), "snippet": it.get("description") or "",
                        "evidence": {"stars": it.get("stargazers_count"), "forks": it.get("forks_count"),
                                     "pushed_at": it.get("pushed_at"), "license_spdx": lic,
                                     "topics": it.get("topics") or [], "owner_type": (it.get("owner") or {}).get("type"),
                                     "default_branch": it.get("default_branch"), "archived": it.get("archived")}})
        return out

    def check(self):
        """Evidence from the repository itself: its license file (read directly, never inferred from a listing),
        the commit the ref resolves to, and how many files the allowlist matches."""
        problems, notes, ev = [], [], {}
        ref = str(self.cfg.get("ref") or "")
        try:
            sha = self.sha()
            ev["sha"] = sha
            if not SHA_RE.match(ref):
                notes.append(f"ref '{ref or 'default branch'}' is not a commit; pin it with ref: {sha} so every crawl "
                             f"reads the same text")
            lic = self.api(f"/repos/{self.repo}/license", {"ref": sha})
        except SourceError as e:
            return {"problems": [str(e)], "notes": notes, "evidence": ev}
        if not lic:
            problems.append(f"{self.repo} has no license file: its terms cannot be verified")
        else:
            text = ""
            try:
                text = base64.b64decode(lic.get("content") or "").decode("utf-8", "replace")
            except ValueError:
                pass
            spdx = (lic.get("license") or {}).get("spdx_id")
            detected = licenses.classify(spdx) if spdx and spdx != "NOASSERTION" else licenses.detect_from_text(text)
            ev["license"] = {"spdx": spdx, "file": lic.get("path"), "class": detected,
                             "sha256": hashlib.sha256(text.encode()).hexdigest(), "head": " ".join(text.split())[:480]}
            declared = self.license
            if declared.get("name") and declared.get("class") != detected:
                problems.append(f"{self.repo}: subject.yaml declares {declared['name']} ({declared['class']}) but its "
                                f"license file reads as {detected}: {ev['license']['head'][:120]}")
            elif not declared.get("name"):
                notes.append(f"{self.repo}: no license declared; the license file reads as {detected}")
            if detected == "unknown":
                problems.append(f"{self.repo}: cannot tell what its license file allows; read it")
        try:
            n = len(self.files())
            ev["matched_files"] = n
            if n == 0:
                problems.append(f"{self.repo}: include/exclude match no files at {self.sha()[:7]}")
        except SourceError as e:
            problems.append(str(e))
        return {"license": ev.get("license"), "problems": problems, "notes": notes, "evidence": ev}


ADAPTER = GithubAdapter
