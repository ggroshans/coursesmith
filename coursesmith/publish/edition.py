"""Render editions: one EPUB per unit, plus one complete-course EPUB per subject.

A unit edition reads, in order: where you are (part > chapter, or the time span and the proportional clock
for chronological subjects), unit n / N, reading time, "second pass" after a wrap; last time (and the answer
to the previous question); chapter openers; the 4-5 entries with their tag lines; chapter reviews; terms
defined in this unit; the question; next; and an attribution page.
"""
import math
import re
import uuid
from html import escape

from .. import config
from ..crawl.store import Store
from ..outline import Outline
from ..util import read_json
from ..write.render import REF_RE
from ..write.render import load as load_prose
from . import attribution as A
from . import clock, cover, figures
from .epub import Epub

WPM = 230
LICENSE_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
CSS = """\
body { font-family: serif; line-height: 1.45; margin: 0 0.3em; }
h1 { font-size: 1.45em; margin: 0.3em 0 0.2em; }
h2 { font-size: 1.15em; margin: 1.3em 0 0.4em; padding-bottom: 0.1em; border-bottom: 1px solid #000; }
h3 { font-size: 1.05em; margin: 1.1em 0 0.15em; }
p { margin: 0 0 0.55em; }
.where { font-size: 0.8em; text-transform: uppercase; letter-spacing: 0.04em; margin: 0 0 0.2em; }
.meta, .span, .clock { font-size: 0.85em; font-style: italic; margin: 0.1em 0; }
.lasttime, .answer, .next { font-size: 0.95em; }
.opener { font-style: italic; }
.date { font-size: 0.85em; font-weight: bold; margin: 0 0 0.25em; }
.tags { font-size: 0.72em; font-family: sans-serif; margin: 0.25em 0 0; }
.entry { margin: 0 0 1.1em; }
.unitmark { font-size: 0.75em; font-family: sans-serif; text-transform: uppercase; letter-spacing: 0.05em;
  margin: 1.4em 0 0.2em; }
dl { margin: 0.3em 0; } dt { font-weight: bold; } dd { margin: 0 0 0.45em 1em; }
.attribution { font-size: 0.78em; } .attribution p { margin: 0 0 0.45em; }
figure { margin: 0.6em 0; text-align: center; } figure img { max-width: 100%; }
figcaption { font-size: 0.72em; }
figure.fig { margin: 0.8em 0 1em; page-break-inside: avoid; } figure.fig figcaption { font-size: 0.8em; font-style: italic;
  margin: 0.25em 0 0; text-align: left; }
table.fig { border-collapse: collapse; width: 100%; font-size: 0.82em; margin: 0.3em 0; text-align: left; }
table.fig th, table.fig td { border: 1px solid #000; padding: 0.2em 0.35em; vertical-align: top; }
table.fig th { font-weight: bold; background: #ddd; }
pre.code { font-family: monospace; font-size: 0.78em; line-height: 1.3; margin: 0.4em 0 0.8em; padding: 0.4em 0.5em;
  border: 1px solid #000; white-space: pre-wrap; word-wrap: break-word; page-break-inside: avoid; }
pre.code code { font-family: monospace; }
p.term { font-size: 0.92em; margin: 0 0 0.35em 0.8em; }
blockquote.blurb { margin: 0.6em 0 0.8em; padding: 0.05em 0.7em; border-left: 3px solid #000; font-size: 0.95em; }
blockquote.blurb p { margin: 0.25em 0; }
body.cover { margin: 0; padding: 0; text-align: center; } .cover img { max-width: 100%; max-height: 100%; }
"""


def _inline(text):
    """Escape, then allow *emphasis*."""
    t = escape(text or "", quote=False)
    return re.sub(r"(?<![\w*])\*(?!\s)([^*]+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)


def _cap(s):
    """Capitalize a date line, leaving 'c. 565 million years ago' alone."""
    return s if s.startswith("c. ") else s[:1].upper() + s[1:]


def _paras(text):
    return "".join(f"<p>{_inline(p)}</p>" for p in re.split(r"\n\s*\n", text or "") if p.strip())


class Edition:
    def __init__(self, subject):
        self.s = subject
        self.entries = subject.entries_by_id()
        self.prose = load_prose(subject)
        self.units_doc = subject.units()
        if not self.units_doc.get("units"):
            raise SystemExit("no units.json; run `coursesmith units build` first")
        self.units = self.units_doc["units"]
        self.total = len(self.units)
        self.outline = Outline.from_subject(subject)
        self.glossary = (read_json(subject.glossary_path) or {}).get("terms", {})
        self.unit_of = {i: u["n"] for u in self.units for i in u["entries"]}
        self.titles = {i: (self.prose["entries"].get(i) or {}).get("title") or e["title"]
                       for i, e in self.entries.items()}
        self.modified = (self.units_doc.get("built") or "2026-01-01T00:00Z").replace("Z", ":00Z")
        self.width = max(3, len(str(self.total)))
        self.origin_ma = subject.edition.get("clock_origin_ma")
        self.figs = figures.load(subject)
        self.registry = A.course_registry(subject)
        used = [e for e in self.entries.values() if e.get("selected")]
        from .. import explain as X
        # background pages an entry's explanations cite are sources too (explain mode)
        self.extra_sources = {x["id"]: x["sources"] for x in X.source_entries(subject, self.prose, self.entries)}
        self.rows = A.source_rows(used + [{"id": i, "sources": s} for i, s in self.extra_sources.items()],
                                  self.registry, Store())
        self.rowmap = {r["key"]: r for r in self.rows}
        self.license = A.summarize(self.rows, self.registry, subject.cfg.get("distribution") or "personal")
        self.wiki_only = self.license["wikipedia_only"]
        wiki = ["Wikipedia contributors"] if any(r["adapter"] == "wikipedia" for r in self.rows) else []
        others = sorted({r["source_label"] for r in self.rows if r["adapter"] != "wikipedia"})
        self.creator = "Wikipedia contributors" if self.wiki_only else ", ".join(wiki + others)[:200]
        self.rights = "CC BY-SA 4.0" if self.wiki_only else self.license["name"]
        self.tagline = (subject.edition.get("tagline")
                        or "Wikipedia subjects as sourced courses, one unit at a time.")

    # -- pieces --------------------------------------------------------------
    def text(self, eid):
        """The entry's prose with refs resolved and no code (word counts, plain uses)."""
        from .. import listings as LS
        t = (self.prose["entries"].get(eid) or {}).get("text") or ""
        return REF_RE.sub(lambda m: self._ref(m.group(1)), LS.strip(t))

    def body_html(self, eid):
        """The entry's paragraphs, each {{code:id}} as a <pre> of the stored code."""
        from .. import listings as LS
        raw = (self.prose["entries"].get(eid) or {}).get("text") or ""
        code = LS.lookup(LS.CODE_RE.findall(raw))
        out = []
        for kind, v in LS.blocks(raw):
            if kind == "text":
                out.append(f"<p>{_inline(REF_RE.sub(lambda m: self._ref(m.group(1)), v))}</p>")
            elif v in code:
                out.append(f'<pre class="code"><code class="language-{escape(code[v]["lang"])}">'
                           f'{escape(code[v]["code"], quote=False)}</code></pre>')
        return "".join(out)

    def explain_html(self, eid):
        """An entry's explanations: each term's definition, then each blurb as a boxed lesson."""
        from .. import explain as X
        terms, blurbs = X.items(self.prose, eid)
        out = []
        for t in terms:
            out.append(f'<p class="term"><b>{_inline(t.get("term"))}</b>: {_inline(self._plain(t.get("text")))}</p>')
        for b in blurbs:
            out.append(f'<blockquote class="blurb"><p><b>{_inline(b.get("heading"))}</b></p>'
                       f'{_paras(self._plain(b.get("text")))}</blockquote>')
        return "".join(out)

    def _plain(self, text):
        return REF_RE.sub(lambda m: self._ref(m.group(1)), text or "")

    def _ref(self, eid):
        t = self.titles.get(eid, eid)
        u = self.unit_of.get(eid)
        return f"{t} (Unit {u})" if u else t

    def source_names(self, e, limit=6):
        cited = set()
        for f in e.get("facts") or []:
            cited |= set(f.get("sent_ids") or [])
        for ev in e.get("events") or []:
            cited |= set(ev.get("sent_ids") or [])
        if (e.get("definition") or {}).get("sent_ids"):
            cited |= set(e["definition"]["sent_ids"])
        srcs = [A.norm_source(s) for s in e.get("sources") or []]
        pages = [(s["key"], s["title"], len(set(s.get("sent_ids") or []) & cited)) for s in srcs]
        pages = [p for p in pages if p[2]] or [(s["key"], s["title"], 0) for s in srcs]
        art = e.get("article")
        pages.sort(key=lambda p: (p[0] != art, -p[2], p[1]))
        names = list(dict.fromkeys(p[1] for p in pages))
        if len(names) > limit:
            return "; ".join(names[:limit]) + f"; and {len(names) - limit} more"
        return "; ".join(names)

    def tag_line(self, e):
        parts = []
        if self.s.chronological:
            parts += [e.get("branch") or e.get("kind"), e.get("weight")]
        else:
            parts += [e.get("branch") or e.get("part"), e.get("level"), e.get("kind"), e.get("weight")]
        bits = [" · ".join(escape(p) for p in parts if p)]
        pre = [p for p in e.get("prerequisites") or [] if p in self.entries]
        if pre:
            bits.append("Builds on: " + "; ".join(escape(self._ref(p)) for p in pre))
        src = self.source_names(e)
        if src:
            bits.append("Sources: " + escape(src))
        bg = [x["title"] for x in self.extra_sources.get(e["id"]) or []]
        if bg:
            bits.append("Background: " + escape("; ".join(dict.fromkeys(bg))))
        ext = list(dict.fromkeys(x.get("source") for x in e.get("external") or [] if x.get("source")))
        if ext:
            bits.append(" ".join("+ " + escape(x) for x in ext))
        return " · ".join(bits)

    def entry_html(self, eid, images=None, level="h3"):
        e = self.entries[eid]
        out = [f'<div class="entry" id="{eid}"><{level}>{_inline(self.titles[eid])}</{level}>']
        if self.s.chronological and e.get("date_display"):
            out.append(f'<p class="date">{escape(_cap(e["date_display"]))}</p>')
        img = e.get("image")
        if img and images is not None and img.get("file") and self.s.edition.get("images"):
            href = images(img)
            if href:
                out.append(f'<figure><img src="{href}" alt="{escape(img.get("alt") or self.titles[eid])}"/>'
                           f'<figcaption>{escape(img.get("caption") or "")}</figcaption></figure>')
        out.append(self.body_html(eid))
        if self.figs.get(eid) and images is not None:
            out.append(figures.figures_html(self.figs[eid], images.figs, eid))
        out.append(self.explain_html(eid))
        out.append(f'<p class="tags">{self.tag_line(e)}</p></div>')
        return "".join(out)

    def where(self, u):
        path = u.get("path") or []
        if self.s.chronological:
            path = [p for p in path if self.outline.nodes.get(p, {}).get("level", 0) >= 2] or path
        return " › ".join(escape(self.outline.title(p)) for p in path)

    def unit_words(self, u):
        from .. import explain as X
        n = sum(len((self.text(i) + " " + self.titles[i]).split()) + X.words(self.prose, i) for i in u["entries"])
        n += sum(len((self.prose["openers"].get(o) or "").split()) for o in u.get("openers") or [])
        n += sum(len((self.prose["reviews"].get(r) or "").split()) for r in u.get("reviews") or [])
        return n

    def attribution_html(self, ids, heading="h1"):
        out = [f'<div class="attribution"><{heading}>Sources and license</{heading}>']
        if self.wiki_only:
            out.append("<p>The text of this edition is adapted from Wikipedia articles, which are available under the "
                       f'<a href="{LICENSE_URL}">Creative Commons Attribution-ShareAlike 4.0 License</a>. Facts were '
                       "extracted from the revisions listed below, consolidated and rewritten; the full list of authors "
                       "of each article is in its page history. This edition is shared under the same license.</p>")
        else:
            out.append("<p>The text of this edition is adapted from the sources listed below, consolidated and "
                       "rewritten. Facts were extracted from the versions named; each source's authors are credited "
                       "at the link given.</p>")
            for lname, labels in sorted(self.license["by_license"].items()):
                out.append(f"<p><b>{escape(lname)}</b>: {escape(', '.join(labels))}.</p>")
            if any(r["adapter"] == "wikipedia" for r in self.rows):
                out.append("<p>Wikipedia articles are available under the "
                           f'<a href="{LICENSE_URL}">Creative Commons Attribution-ShareAlike 4.0 License</a>; the '
                           "full list of authors of each article is in its page history.</p>")
            if self.license["restricted"]:
                out.append("<p>Some sources do not allow redistribution or derivative works, so this edition is "
                           "for personal reading only.</p>")
        credits, checked = [], []
        for i in ids:
            e = self.entries[i]
            pages = "; ".join(self._source_ref(s) for s in e.get("sources") or [])
            if self.extra_sources.get(i):
                bg = "; ".join(self._source_ref(s) for s in self.extra_sources[i])
                pages = f"{pages}. Background: {bg}" if pages else f"Background: {bg}"
            out.append(f"<p><b>{_inline(self.titles[i])}</b>: {pages or 'no source recorded'}</p>")
            img = e.get("image")
            if img and img.get("file") and self.s.edition.get("images"):
                credits.append(f"<p><b>{escape(img['file'])}</b> ({_inline(self.titles[i])}): "
                               f"{escape(img.get('artist') or 'unknown author')}, {escape(img.get('license') or '')}"
                               f"{', ' + escape(img['page_url']) if img.get('page_url') else ''}. Converted to "
                               "grayscale and dithered.</p>")
            for v in e.get("verification") or []:
                final = v.get("reviewed_verdict") or v.get("verdict")
                if final not in ("supports", "refines", "matches", "genuine conflict"):
                    continue  # checked, but neither support nor a conflict worth naming
                verdict = escape(str(final))
                if v.get("doi"):
                    what = (f"{escape(v.get('title') or v['doi'])} ({v.get('year') or 'n.d.'}), "
                            f"doi:{escape(v['doi'])}")
                else:
                    what = escape(f"{v.get('source') or v.get('dataset') or 'authority'}"
                                  + (f", record {v['record']}" if v.get("record") else ""))
                checked.append(f"<p>{what}: {verdict} ({_inline(self.titles[i])})</p>")
            for x in e.get("external") or []:
                what = x.get("record") or x.get("url") or x.get("text") or ""
                checked.append(f"<p>{escape(x.get('source') or '')}: {escape(str(what))[:200]} "
                               f"({_inline(self.titles[i])})</p>")
        if credits:
            out += [f"<{heading[0]}{int(heading[1]) + 1}>Image credits</{heading[0]}{int(heading[1]) + 1}>"] + credits
        if checked:
            h = f"h{int(heading[1]) + 1}"
            out += [f"<{h}>External sources checked</{h}>"] + checked
        out.append("</div>")
        return "".join(out)

    def _source_ref(self, s):
        ns = A.norm_source(s)
        r = self.rowmap.get(ns["key"]) or {}
        label = r.get("version_label") or (f"revision {ns['revid']}" if ns.get("revid") else "")
        if r.get("retrieved") and r.get("adapter") != "wikipedia":
            label = (label + ", " if label else "") + f"retrieved {str(r['retrieved'])[:10]}"
        return f'<a href="{escape(ns["url"] or "")}">{escape(ns["title"])}</a> ({escape(label)})'

    # -- unit edition ----------------------------------------------------------
    def unit_body(self, u, pass_no=1, images=None):
        n = u["n"]
        out = []
        where = self.where(u)
        if where:
            out.append(f'<p class="where">{where}</p>')
        out.append(f"<h1>Unit {n} / {self.total}</h1>")
        mins = max(1, math.ceil(self.unit_words(u) / WPM))
        meta = f"About {mins} minute{'s' if mins != 1 else ''} of reading"
        if pass_no > 1:
            meta += " · " + ("second pass" if pass_no == 2 else f"pass {pass_no}")
        out.append(f'<p class="meta">{meta}</p>')
        if self.s.chronological:
            es = [self.entries[i] for i in u["entries"]]
            old = max(e["date_ma"] for e in es if e.get("date_ma") is not None)
            young = min((e.get("date_young_ma") if e.get("date_young_ma") is not None else e["date_ma"])
                        for e in es if e.get("date_ma") is not None)
            out.append(f'<p class="span">{escape(_cap(clock.fmt_span(old, young)))}</p>')
            if self.s.edition.get("proportional_clock") and self.origin_ma:
                out.append(f'<p class="clock">{escape(clock.clock_line(old, young, self.origin_ma))}</p>')
        if u.get("last_time"):
            out.append(f'<p class="lasttime"><b>Last time:</b> {_inline(u["last_time"])}.</p>')
        if u.get("answer_prev"):
            out.append(f'<p class="answer"><b>Answer to last time\'s question:</b> {_inline(u["answer_prev"])}</p>')
        openers = set(u.get("openers") or [])
        reviews = set(u.get("reviews") or [])
        shown_heads = set()
        prev_path = None
        for i in u["entries"]:
            path = self.outline.entry_path(self.entries[i])
            new_nodes = [p for p in path if p in openers and p not in shown_heads]
            changed = prev_path is not None and path[-1:] != prev_path[-1:]
            for p in new_nodes:
                shown_heads.add(p)
                out.append(f"<h2>{escape(self.outline.title(p))}</h2>")
                out.append(f'<p class="opener">{_inline(self.prose["openers"][p])}</p>')
            if changed and not new_nodes and path:
                out.append(f"<h2>{escape(self.outline.title(path[-1]))}</h2>")
            prev_path = path
            out.append(self.entry_html(i, images))
            leaf = path[-1] if path else None
            if leaf in reviews:
                out.append(f"<h2>Chapter review: {escape(self.outline.title(leaf))}</h2>")
                out.append(_paras(self.prose["reviews"][leaf]))
                reviews.discard(leaf)
        if n == self.total and self.prose.get("closing"):
            out.append("<h2>The whole story</h2>")
            out.append(_paras(self.prose["closing"]))
        terms = [self.glossary[t] for t in u.get("terms") or [] if t in self.glossary]
        if terms:
            out.append("<h2>Terms defined in this unit</h2><dl>")
            out += [f"<dt>{_inline(t['term'])}</dt><dd>{_inline(t['text'])}</dd>" for t in terms]
            out.append("</dl>")
        if u.get("question") and self.s.edition.get("questions"):
            out.append(f"<h2>Question</h2><p>{_inline(u['question']['q'])}</p>")
            if n < self.total:
                out.append("<p><i>The answer opens the next unit.</i></p>")
            else:  # no next unit to carry the answer
                out.append(f"<p><i>Answer:</i> {_inline(u['question']['a'])}</p>")
        if u.get("next"):
            out.append(f'<p class="next"><b>Next:</b> {_inline(u["next"])}.</p>')
        elif n == self.total:
            out.append('<p class="next"><b>Next:</b> the course starts again at Unit 1.</p>')
        return "".join(out)

    def unit_title(self, u, pass_no=1):
        leaf = self.outline.title(u["leaf"]) if u.get("leaf") else ""
        t = f"{self.s.title} {u['n']:0{self.width}d}/{self.total}"
        if pass_no > 1:
            t += f" (pass {pass_no})"
        return f"{t} — {leaf}" if leaf else t

    def unit_filename(self, n, pass_no=1):
        return f"{self.s.slug}-unit-{n:03d}{'-pass' + str(pass_no) if pass_no > 1 else ''}.epub"

    def identifier(self, kind, n=None, pass_no=1):
        key = f"https://wikicourse.local/{self.s.slug}/{kind}" + (f"/{n}" if n else "") + \
              (f"/pass{pass_no}" if pass_no > 1 else "")
        return "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, key))

    def build_unit(self, u, out_dir=None, pass_no=1):
        out_dir = out_dir or config.EPUB_DIR / self.s.slug
        n = u["n"]
        book = Epub(self.identifier("unit", n, pass_no), self.unit_title(u, pass_no), self.modified,
                    creator=self.creator, rights=self.rights, description=f"Unit {n} of {self.total}: " + "; ".join(self.titles[i] for i in u["entries"]),
                    series=self.s.title, series_index=n)
        book.add("css", "style.css", "text/css", CSS)
        leaf = self.outline.title(u["leaf"]) if u.get("leaf") else ""
        book.set_cover(cover.unit_cover(self.s.title, n, self.total, leaf, pass_no=pass_no),
                       title=self.unit_title(u, pass_no))
        imgs = _ImageSink(book)
        body = self.unit_body(u, pass_no, imgs)
        book.add_page("unit", "unit.xhtml", f"Unit {n} / {self.total}", body,
                      toc_children=[{"title": self.titles[i], "href": f"unit.xhtml#{i}"} for i in u["entries"]])
        book.add_page("sources", "sources.xhtml", "Sources and license", self.attribution_html(u["entries"]))
        size = book.write(out_dir / self.unit_filename(n, pass_no))
        return out_dir / self.unit_filename(n, pass_no), size

    # -- complete edition ------------------------------------------------------
    def build_complete(self, out_dir=None):
        out_dir = out_dir or config.EPUB_DIR / self.s.slug
        order = [i for u in self.units for i in u["entries"]]
        book = Epub(self.identifier("complete"), f"{self.s.title} — the complete course", self.modified,
                    creator=self.creator, rights=self.rights,
                    description=(self.s.cfg.get("description") or "").strip() or None, series=self.s.title,
                    series_index=0)
        book.add("css", "style.css", "text/css", CSS)
        book.set_cover(cover.course_cover(self.s.title, self.total, len(order), self.tagline),
                       title=self.s.title)
        book.add_page("about", "about.xhtml", "About this course", self._about_html(len(order)))
        imgs = _ImageSink(book)
        # group consecutive entries by part
        groups = []
        for i in order:
            part = self.entries[i].get("part") or ""
            if not groups or groups[-1][0] != part:
                groups.append((part, []))
            groups[-1][1].append(i)
        seen, unit_start = set(), {u["entries"][0]: u["n"] for u in self.units}
        for k, (part, ids) in enumerate(groups, start=1):
            href = f"part-{k:03d}.xhtml"
            out, children = [f"<h1>{escape(part)}</h1>"], []
            for i in ids:
                path = self.outline.entry_path(self.entries[i])
                for nid in path:
                    if nid in seen:
                        continue
                    seen.add(nid)
                    title = self.outline.title(nid)
                    if title != part:
                        out.append(f'<h2 id="n-{nid}">{escape(title)}</h2>')
                        children.append({"title": title, "href": f"{href}#n-{nid}"})
                    if self.prose["openers"].get(nid):
                        out.append(f'<p class="opener">{_inline(self.prose["openers"][nid])}</p>')
                if i in unit_start:
                    out.append(f'<p class="unitmark">Unit {unit_start[i]}</p>')
                out.append(self.entry_html(i, imgs))
                leaf = path[-1] if path else None
                if leaf and self.prose["reviews"].get(leaf) and self._last_of_leaf(leaf) == i:
                    out.append(f"<h3>Chapter review</h3>{_paras(self.prose['reviews'][leaf])}")
            book.add_page(f"p{k:03d}", href, part or f"Part {k}", "".join(out), toc_children=children)
        if self.prose.get("closing"):
            book.add_page("closing", "closing.xhtml", "The whole story",
                          "<h1>The whole story</h1>" + _paras(self.prose["closing"]))
        if self.glossary:
            items = sorted(self.glossary.values(), key=lambda t: t["term"].lower())
            book.add_page("glossary", "glossary.xhtml", "Glossary", "<h1>Glossary</h1><dl>" + "".join(
                f"<dt>{_inline(t['term'])} <small>(Unit {t['unit']})</small></dt><dd>{_inline(t['text'])}</dd>"
                for t in items) + "</dl>")
        book.add_page("sources", "sources.xhtml", "Sources and license", self.attribution_html(order))
        path = out_dir / f"{self.s.slug}-complete.epub"
        return path, book.write(path)

    def _last_of_leaf(self, leaf):
        if not hasattr(self, "_leaf_last"):
            self._leaf_last = {}
            for u in self.units:
                for i in u["entries"]:
                    self._leaf_last[self.outline.leaf(self.entries[i])] = i
        return self._leaf_last.get(leaf)

    def _unit_sizes(self):
        sizes = sorted({len(u["entries"]) for u in self.units}) or [0]
        return f"{sizes[0]}–{sizes[-1]}" if sizes[0] != sizes[-1] else str(sizes[0])

    def _about_html(self, n_entries):
        desc = (self.s.cfg.get("description") or "").strip()
        tiers = {}
        for e in self.entries.values():
            if e.get("selected"):
                tiers[e.get("source_tier", "wikipedia")] = tiers.get(e.get("source_tier", "wikipedia"), 0) + 1
        tier_txt = ", ".join(f"{v:,} {k}" for k, v in sorted(tiers.items(), key=lambda kv: -kv[1]))
        if self.wiki_only:
            trace = ("Every fact traces to a "
                     "Wikipedia revision listed under Sources and license at the end of this book, or to a verified "
                     "external source named in the entry's tag line. Nothing comes from general knowledge.</p>")
        else:
            trace = ("Every fact traces to a source version listed under Sources and license at the end of this book "
                     "(a Wikipedia revision, a repository commit, an RFC, a documentation snapshot or a paper), or to "
                     "a verified external source named in the entry's tag line. Nothing comes from general "
                     "knowledge.</p>")
        return (f"<h1>About this course</h1>{_paras(desc)}"
                f"<p>{n_entries:,} entries in {self.total} units of {self._unit_sizes()} entries each. "
                + trace +
                f"<p>Source tiers: {escape(tier_txt)}. An entry is <i>primary</i> when a cited paper or an "
                "authority confirms its key claim.</p>"
                "<p>Built with coursesmith.</p>")


class _ImageSink:
    """Adds entry images to a book on demand and returns their hrefs."""

    def __init__(self, book):
        self.book, self.added = book, {}
        self.figs = figures.Sink(book)

    def __call__(self, img):
        local = img.get("local")
        if not local:
            return None
        p = config.IMAGES_DIR / local
        if not p.exists():
            return None
        if local not in self.added:
            href = f"images/{local}"
            self.book.add(f"img{len(self.added) + 1}", href, "image/png", p.read_bytes())
            self.added[local] = href
        return self.added[local]
