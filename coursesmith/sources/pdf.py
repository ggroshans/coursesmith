"""PDF files as a source: `pdf>source-name/file.pdf`.

For a manual, a specification or a paper that is only published as a PDF. The subject lists the files; nothing
else is ever fetched, so every PDF is vetted by name.

    - name: soil-survey-manual
      adapter: pdf
      files:
        - {url: "https://www.nrcs.usda.gov/sites/default/files/2022-09/SSM-ch3.pdf", name: "Soil Survey Manual, ch. 3"}
      tier: official
      license: {name: "Public domain (US government work)", class: public-domain}

A PDF's version is the SHA-256 of its bytes. Headings and paragraphs are recovered from the text layer as well
as it allows (text/pdf.py); a scanned PDF with no text layer is rejected, not guessed at.
"""
import hashlib
import re
from urllib.parse import unquote, urlparse

from .base import MissingSource, SourceAdapter, SourceError
from .keys import SEP, clean_id, make_key
from ..text.pdf import pdf_to_text


class PdfAdapter(SourceAdapter):
    adapter = "pdf"
    prefix = "pdf"
    default_tier = "primary"
    default_depth = 0

    def __init__(self, cfg=None, http=None, defaults=None):
        super().__init__(cfg, http, defaults)
        self.files = {}  # file name in the key -> {url, name}
        for f in self.cfg.get("files") or [{"url": u} for u in self.cfg.get("urls") or []]:
            f = {"url": f} if isinstance(f, str) else dict(f)
            fname = re.sub(r"[^A-Za-z0-9._-]+", "_", unquote(urlparse(f["url"]).path.rsplit("/", 1)[-1])) or "file.pdf"
            if fname in self.files:
                raise SourceError(f"pdf source '{self.cfg.get('name')}': two files are named {fname}; give one a "
                                  f"different `file:`")
            self.files[f.get("file") or fname] = f
        if not self.files:
            raise SourceError(f"pdf source '{self.cfg.get('name')}' lists no files")

    def hosts(self):
        return sorted({urlparse(f["url"]).netloc for f in self.files.values()})

    def _root(self):
        return f"pdf{SEP}{self.label}/"

    def key(self, fname):
        return make_key("pdf", f"{self.label}/{fname}")

    def owns(self, key):
        return key.startswith(self._root())

    def allowed(self, key):
        return self.owns(key) and key[len(self._root()):] in self.files

    def seeds(self):
        return [self.key(f) for f in self.files]

    def key_for_url(self, url, base_key=None):
        for fname, f in self.files.items():
            if f["url"] == url:
                return self.key(fname)
        return None

    def fetch(self, key):
        fname = key[len(self._root()):]
        f = self.files.get(fname)
        if f is None:
            raise MissingSource(f"{key}: not a file of source '{self.label}'")
        data = self.http.get(f["url"], binary=True)
        if not data:
            raise MissingSource(f"{f['url']}: not found")
        text, meta_title = pdf_to_text(data, f.get("name") or "")
        if len(text.split()) < 50:
            raise SourceError(f"{f['url']}: no text layer (a scanned PDF needs OCR, which is not supported)")
        name = f.get("name") or meta_title or fname
        version = hashlib.sha256(data).hexdigest()[:16]
        rec = self.record(key, name, f["url"], text if text.startswith("# ") else f"# {name}\n{text}", version,
                          source_id=f"{self.label}/{fname}")
        headings = len(re.findall(r"^#{2,6} ", text, re.M))
        rec["meta"] = {"description": name, "tags": [], "headings": headings, "bytes": len(data),
                       "dates": bool(self.cfg.get("dates"))}
        return rec

    def version_label(self, version):
        return f"sha {str(version)[:8]}" if version else ""

    def check(self):
        problems, notes = [], []
        if not self.license.get("name"):
            problems.append(f"{self.label}: declare the license of these PDFs under `license:`")
        for fname, f in self.files.items():
            try:
                rec = self.fetch(self.key(fname))
            except SourceError as e:
                problems.append(str(e))
                continue
            if rec["meta"]["headings"] == 0:
                notes.append(f"{fname}: no headings recovered; entries from it will cite sentences with no section")
        return {"problems": problems, "notes": notes}


ADAPTER = PdfAdapter
