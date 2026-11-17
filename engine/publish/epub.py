"""A small EPUB 3 writer (zip + XHTML + OPF), with an EPUB 2 NCX alongside the nav document so older
reading systems get a table of contents too.

Output is reproducible: zip entries carry a fixed timestamp and `modified` is passed in, so the same content
always yields the same bytes.
"""
import zipfile
from html import escape

XHTML_HEAD = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="{lang}" lang="{lang}">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<link rel="stylesheet" type="text/css" href="style.css"/>
</head>
<body{body_attrs}>
"""
XHTML_TAIL = "\n</body>\n</html>\n"
ZIP_DATE = (2026, 1, 1, 0, 0, 0)


def xhtml(title, body, lang="en", body_class=None):
    attrs = f' class="{body_class}"' if body_class else ""
    return XHTML_HEAD.format(lang=lang, title=escape(title), body_attrs=attrs) + body + XHTML_TAIL


class Epub:
    def __init__(self, identifier, title, modified, language="en", creator="Wikipedia contributors",
                 publisher="wikicourse", rights="CC BY-SA 4.0", description=None, series=None, series_index=None):
        self.identifier, self.title, self.modified = identifier, title, modified
        self.language, self.creator, self.publisher, self.rights = language, creator, publisher, rights
        self.description, self.series, self.series_index = description, series, series_index
        self.items = []      # (id, href, media_type, data, properties)
        self.spine = []      # item ids
        self.toc = []        # nested: {"title", "href", "children": [...]}
        self.cover_id = None

    def add(self, item_id, href, media_type, data, properties=None):
        if isinstance(data, str):
            data = data.encode("utf-8")
        self.items.append((item_id, href, media_type, data, properties))
        return item_id

    def add_page(self, item_id, href, title, body, toc=True, toc_children=None, body_class=None):
        self.add(item_id, href, "application/xhtml+xml", xhtml(title, body, self.language, body_class))
        self.spine.append(item_id)
        if toc:
            self.toc.append({"title": title, "href": href, "children": toc_children or []})

    def set_cover(self, png_bytes, title="Cover"):
        self.cover_id = self.add("cover-image", "cover.png", "image/png", png_bytes, "cover-image")
        body = f'<div class="cover"><img src="cover.png" alt="{escape(title)}"/></div>'
        self.add("cover", "cover.xhtml", "application/xhtml+xml", xhtml(title, body, self.language, "cover"))
        self.spine.insert(0, "cover")

    # -- package documents -------------------------------------------------
    def _opf(self):
        meta = [
            f'<dc:identifier id="bookid">{escape(self.identifier)}</dc:identifier>',
            f"<dc:title>{escape(self.title)}</dc:title>",
            f"<dc:language>{self.language}</dc:language>",
            f"<dc:creator>{escape(self.creator)}</dc:creator>",
            f"<dc:publisher>{escape(self.publisher)}</dc:publisher>",
            f"<dc:rights>{escape(self.rights)}</dc:rights>",
            f'<meta property="dcterms:modified">{self.modified}</meta>',
        ]
        if self.description:
            meta.append(f"<dc:description>{escape(self.description)}</dc:description>")
        if self.cover_id:
            meta.append(f'<meta name="cover" content="{self.cover_id}"/>')
        if self.series:
            meta += [f'<meta property="belongs-to-collection" id="series">{escape(self.series)}</meta>',
                     '<meta refines="#series" property="collection-type">series</meta>',
                     f'<meta name="calibre:series" content="{escape(self.series)}"/>']
            if self.series_index is not None:
                meta += [f'<meta refines="#series" property="group-position">{self.series_index}</meta>',
                         f'<meta name="calibre:series_index" content="{self.series_index}"/>']
        manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                    '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>']
        for iid, href, mt, _, props in self.items:
            p = f' properties="{props}"' if props else ""
            manifest.append(f'<item id="{iid}" href="{href}" media-type="{mt}"{p}/>')
        spine = [f'<itemref idref="{i}"/>' for i in self.spine]
        guide = '<guide><reference type="cover" title="Cover" href="cover.xhtml"/></guide>' if self.cover_id else ""
        return ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" '
                f'xml:lang="{self.language}">\n'
                '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">\n'
                + "\n".join(meta) + "\n</metadata>\n<manifest>\n" + "\n".join(manifest)
                + '\n</manifest>\n<spine toc="ncx">\n' + "\n".join(spine) + "\n</spine>\n" + guide + "\n</package>\n")

    def _nav(self):
        def ol(nodes):
            out = ["<ol>"]
            for n in nodes:
                out.append(f'<li><a href="{n["href"]}">{escape(n["title"])}</a>')
                if n.get("children"):
                    out.append(ol(n["children"]))
                out.append("</li>")
            out.append("</ol>")
            return "\n".join(out)
        body = f'<nav epub:type="toc" id="toc"><h1>Contents</h1>\n{ol(self.toc)}\n</nav>'
        return xhtml("Contents", body, self.language)

    def _ncx(self):
        counter = [0]

        def points(nodes):
            out = []
            for n in nodes:
                counter[0] += 1
                k = counter[0]
                out.append(f'<navPoint id="np{k}" playOrder="{k}"><navLabel><text>{escape(n["title"])}</text>'
                           f'</navLabel><content src="{n["href"]}"/>')
                if n.get("children"):
                    out.append(points(n["children"]))
                out.append("</navPoint>")
            return "\n".join(out)
        nav = points(self.toc)
        return ('<?xml version="1.0" encoding="utf-8"?>\n'
                '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">\n'
                f'<head><meta name="dtb:uid" content="{escape(self.identifier)}"/>'
                '<meta name="dtb:depth" content="3"/><meta name="dtb:totalPageCount" content="0"/>'
                '<meta name="dtb:maxPageNumber" content="0"/></head>\n'
                f"<docTitle><text>{escape(self.title)}</text></docTitle>\n<navMap>\n{nav}\n</navMap>\n</ncx>\n")

    def write(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        with zipfile.ZipFile(tmp, "w") as z:
            def put(name, data, compress=True):
                zi = zipfile.ZipInfo(name, date_time=ZIP_DATE)
                zi.compress_type = zipfile.ZIP_DEFLATED if compress else zipfile.ZIP_STORED
                zi.external_attr = 0o644 << 16
                z.writestr(zi, data)
            put("mimetype", b"application/epub+zip", compress=False)
            put("META-INF/container.xml",
                '<?xml version="1.0" encoding="utf-8"?>\n<container version="1.0" '
                'xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>'
                '<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
                "</rootfiles></container>\n")
            put("OEBPS/content.opf", self._opf())
            put("OEBPS/nav.xhtml", self._nav())
            put("OEBPS/toc.ncx", self._ncx())
            for _, href, _, data, _ in self.items:
                put(f"OEBPS/{href}", data, compress=not href.endswith((".png", ".jpg")))
        tmp.replace(path)
        return path.stat().st_size
