"""Files on this machine as a source: `local>source-name/relative/path.md`.

For a course made from material you hold yourself (notes, reports, saved pages, PDFs) that is not on Wikipedia.
The subject names a folder (or one file) and nothing else is ever read, so every file is vetted by being in it.

    - name: field-notes
      adapter: local
      path: ~/notes/field-notes          # a folder or a single file
      include: ["**/*.md", "**/*.pdf"]   # default: every .md .markdown .txt .html .htm .pdf
      exclude: ["drafts/**"]
      selector: "main"                   # html files only: the content container
      drop: [".toc"]                     # html files only: extra chrome to remove
      code: {max_lines: 80}              # keep fenced and <pre> code blocks as listings a writer can place
      tier: primary
      license: {name: "Private notes", class: all-rights-reserved}

Every file is a seed, so the crawl takes them all in. Links between files work as relative paths and as
Obsidian-style `[[wikilinks]]` (matched by file name). A file's version is the SHA-256 of its bytes; nothing is
fetched from the network.
"""
import hashlib
import re
from pathlib import Path
from urllib.parse import quote, unquote, urldefrag

from .base import MissingSource, SourceAdapter, SourceError, glob_match
from .github import plain_to_doc
from .keys import SEP, make_key
from ..text.docfx import code_listings
from ..text.html import html_to_doc
from ..text.markdown import markdown_to_doc
from ..text.pdf import pdf_to_text

EXTS = (".md", ".markdown", ".txt", ".html", ".htm", ".pdf")
_WIKILINK = re.compile(r"(!?)\[\[([^\]\|\n]+?)(?:\|([^\]\n]+))?\]\]")
_SCHEME = "wl:"


def _prepare_wikilinks(md):
    """Obsidian `[[Target#Heading|alias]]` -> a Markdown link to `wl:Target`; `![[embed]]` is dropped."""
    def sub(m):
        if m.group(1):
            return ""
        target, alias = m.group(2).split("#", 1)[0].strip(), (m.group(3) or m.group(2)).strip()
        alias = alias.split("#", 1)[0].strip() if not m.group(3) else alias
        return f"[{alias}]({_SCHEME}{quote(target)})" if target else alias
    return _WIKILINK.sub(sub, md)


class LocalAdapter(SourceAdapter):
    adapter = "local"
    prefix = "local"
    default_tier = "primary"
    default_license = {"name": "Private material", "url": "", "class": "all-rights-reserved"}
    default_depth = 0

    def __init__(self, cfg=None, http=None, defaults=None):
        super().__init__(cfg, http, defaults)
        raw = self.cfg.get("path")
        if not raw:
            raise SourceError(f"local source '{self.label}' needs a `path:`")
        self.base = Path(str(raw)).expanduser().resolve()
        self.files = {}   # key -> path relative to the base, with forward slashes
        self.rel = {}     # relative path -> key
        self._scan()

    # -- discovery of files ----------------------------------------------------------
    def _scan(self):
        if not self.base.exists():
            return  # `check` reports it; a course built earlier keeps working from its stored pages
        include, exclude = self.cfg.get("include"), self.cfg.get("exclude") or []
        if self.base.is_file():
            found, root = [self.base], self.base.parent
        else:
            found, root = sorted(p for p in self.base.rglob("*") if p.is_file()), self.base
        for p in found:
            rel = p.relative_to(root).as_posix()
            if any(part.startswith(".") for part in rel.split("/")):
                continue
            if include:
                if not glob_match(rel, include):
                    continue
            elif p.suffix.lower() not in EXTS:
                continue
            if exclude and glob_match(rel, exclude):
                continue
            key = make_key("local", f"{self.label}/{rel}")
            self.files[key] = rel
            self.rel[rel] = key
        self.root = root

    def _root(self):
        return f"local{SEP}{self.label}/"

    # -- keys ------------------------------------------------------------------------
    def owns(self, key):
        return key.startswith(self._root())

    def allowed(self, key):
        return key in self.files

    def seeds(self):
        return list(self.files)

    def key_for_url(self, url, base_key=None):
        href = (url or "").strip()
        if not href or href.startswith(("#", "mailto:", "javascript:", "tel:", "http://", "https://")):
            return None
        if href.startswith(_SCHEME):
            return self._by_name(unquote(href[len(_SCHEME):]))
        path = unquote(urldefrag(href)[0])
        if not path:
            return None
        here = self.files.get(base_key, "") if base_key else ""
        parts = [] if path.startswith("/") else here.split("/")[:-1]
        for seg in path.lstrip("/").split("/"):
            if seg == "..":
                if not parts:
                    return None
                parts.pop()
            elif seg not in ("", "."):
                parts.append(seg)
        rel = "/".join(parts)
        return self.rel.get(rel) or self._by_name(rel)

    def _by_name(self, name):
        """A file by its relative path or bare name, with or without the extension, ignoring case."""
        want = name.strip().lower().replace("\\", "/")
        want = re.sub(r"\.(md|markdown|txt|html?|pdf)$", "", want)
        hits = [k for rel, k in self.rel.items()
                if re.sub(r"\.(md|markdown|txt|html?|pdf)$", "", rel.lower()) in (want,)
                or re.sub(r"\.(md|markdown|txt|html?|pdf)$", "", rel.lower().rsplit("/", 1)[-1]) == want]
        return hits[0] if len(hits) == 1 else None

    # -- fetching --------------------------------------------------------------------
    def fetch(self, key):
        rel = self.files.get(key)
        if rel is None:
            raise MissingSource(f"{key}: not a file of source '{self.label}'")
        path = self.root / rel
        try:
            data = path.read_bytes()
        except OSError as e:
            raise MissingSource(f"{path}: {e.strerror or e}")
        suffix, resolve = path.suffix.lower(), (lambda a: self.key_for_url(a.get("href", ""), key))
        fallback = re.sub(r"[-_]+", " ", path.stem).strip()
        links, lead, anchors, code = [], [], {}, 0
        if suffix == ".pdf":
            text, meta_title = pdf_to_text(data, fallback)
            name = meta_title or fallback
            if len(text.split()) < 50:
                raise SourceError(f"{path}: no text layer (a scanned PDF needs OCR, which is not supported)")
            text = text if text.startswith("# ") else f"# {name}\n{text}"
        else:
            raw = data.decode("utf-8", errors="replace").replace("\r\n", "\n")
            listings = code_listings(self.cfg.get("code"))
            if suffix in (".md", ".markdown"):
                doc = markdown_to_doc(_prepare_wikilinks(raw), resolve_link=resolve, table_cells="span", listings=listings)
            elif suffix in (".html", ".htm"):
                doc = html_to_doc(raw, selector=self.cfg.get("selector"), drop=self.cfg.get("drop") or (),
                                  resolve_link=resolve, table_cells="span", listings=listings)
            else:
                doc = None
            if doc is not None:
                text, name, links, lead, anchors, code = (doc.text, doc.name or fallback, doc.links, doc.lead_links,
                                                          doc.anchors, doc.code_blocks)
            else:
                name, text = fallback, plain_to_doc(raw, fallback)
        if len(text.split()) < 20:
            raise SourceError(f"{path}: no readable content")
        title = self.cfg.get("title") or self.label
        if name != title:
            name = f"{name} ({title})"
        version = hashlib.sha256(data).hexdigest()[:16]
        rec = self.record(key, name, path.as_uri(), text, version, source_id=f"{self.label}/{rel}")
        if suffix != ".pdf" and listings is not None and listings.items:
            rec["listings"] = listings.items
        rec.update({"body_links": [l for l in links if l != key], "lead_links": [l for l in lead if l != key],
                    "anchors": anchors})
        rec["meta"] = {"description": name, "tags": [], "path": rel, "code_blocks": code, "bytes": len(data),
                       "dates": bool(self.cfg.get("dates"))}
        return rec

    # -- presentation ----------------------------------------------------------------
    def version_label(self, version):
        return f"file sha {str(version)[:8]}" if version else ""

    def permalink(self, src):
        return src.get("url") or ""

    # -- checks ----------------------------------------------------------------------
    def check(self):
        problems, notes = [], []
        if not self.base.exists():
            return {"problems": [f"{self.label}: path {self.base} does not exist"], "notes": notes}
        if not self.files:
            problems.append(f"{self.label}: no files under {self.base} match `include:`")
        if not self.license.get("name"):
            problems.append(f"{self.label}: declare the license of these files under `license:`")
        for key in self.files:
            try:
                self.fetch(key)
            except SourceError as e:
                problems.append(str(e))
        return {"problems": problems, "notes": notes}


ADAPTER = LocalAdapter
