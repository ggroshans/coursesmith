"""images: one image per entry where the subject needs it (edition.images: true).

    coursesmith images <subject> [--all-landmarks] [--force]

Takes the lead image of the entry's own article, only if Commons lists its license as CC BY-SA, CC BY, CC0
or public domain; converts it to grayscale, dithers it to 16 levels, caps the width at 600 px, and stores it
in cache/images/. The entry gets an `image` record (file, license, license_url, artist, page_url, local,
caption) which the attribution page credits. Candidates: entries the consolidation pass marked
`wants_image: true`, plus every Landmark entry with --all-landmarks.
"""
import io
import re
from html import unescape

from PIL import Image

from .. import config
from ..crawl.api import WikiClient
from ..util import read_jsonl, slug, write_jsonl
from .cover import dither16

OK = re.compile(r"^(CC[ -]BY(-SA)?[ -]?\d|CC0|Public domain|PD\b|PD-)", re.I)
MAX_W = 600


def _plain(html):
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html or ""))).strip()


def section_image(title, section):
    """File title of the first image in a section of a crawled page, or None."""
    from urllib.parse import unquote

    from bs4 import BeautifulSoup

    from ..crawl.clean import _heading
    from ..crawl.store import Store
    store = Store()
    if not store.has_page(title):
        return None
    soup = BeautifulSoup(store.load_page(title)["html"], "html.parser")
    root = soup.find("div", class_="mw-parser-output") or soup
    inside, level = False, None
    for el in root.children:
        h = _heading(el)
        if h:
            lv, text = h
            if inside and lv <= level:
                return None
            if not inside and text.strip().lower() == section.replace("_", " ").strip().lower():
                inside, level = True, lv
            continue
        if inside and hasattr(el, "select"):
            for a in el.select("a.mw-file-description, a.image"):
                href = a.get("href", "")
                if "/wiki/File:" in href:
                    return "File:" + unquote(href.split("/wiki/File:", 1)[1]).replace("_", " ")
    return None


def fetch(subject, all_landmarks=False, force=False, log=print):
    if not subject.edition.get("images"):
        raise SystemExit(f"{subject.slug}: edition.images is false")
    client = WikiClient()
    config.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    entries = subject.entries()
    n_new = n_skip = 0
    for e in entries:
        if not e.get("selected") or not e.get("article"):
            continue
        if not (e.get("wants_image") or (all_landmarks and e.get("weight") == "Landmark")):
            continue
        if e.get("image") and not force:
            continue
        art, _, section = e["article"].partition("#")
        # a section entry takes the first image inside its own section; a page's lead image is about the page
        f = section_image(art, section) if section else client.page_image(art)
        if not f:
            continue
        info = client.image_info(f, MAX_W)
        if not info or not info.get("license") or not OK.search(info["license"]):
            n_skip += 1
            log(f"  [images] {e['id']}: {f} skipped (license {info.get('license') if info else 'unknown'})")
            continue
        if not (info.get("mime") or "").startswith("image/") or info["mime"] == "image/svg+xml" and not info.get("thumb_url"):
            continue
        raw = client.get_bytes(info["thumb_url"])
        img = Image.open(io.BytesIO(raw))
        if img.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
            img = Image.alpha_composite(bg, img.convert("RGBA"))
        img = img.convert("L")
        if img.width > MAX_W:
            img = img.resize((MAX_W, round(img.height * MAX_W / img.width)), Image.LANCZOS)
        img = dither16(img)
        local = f"{slug(e['id'])}.png"
        img.save(config.IMAGES_DIR / local, format="PNG", optimize=True)
        e["image"] = {"file": info["file"], "license": info["license"], "license_url": info.get("license_url"),
                      "artist": _plain(info.get("artist")) or None, "page_url": info.get("page_url"),
                      "local": local, "caption": f"{_plain(info.get('artist')) or 'Unknown author'}, "
                                                 f"{info['license']}, via Wikimedia Commons"}
        n_new += 1
    by_id = {e["id"]: e for e in entries}
    for p in subject.entry_files():
        write_jsonl(p, [by_id.get(r["id"], r) for r in read_jsonl(p)])
    log(f"[images] {n_new} images added, {n_skip} skipped for their license")
