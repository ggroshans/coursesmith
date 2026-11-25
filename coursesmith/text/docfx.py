"""DocFX / Microsoft Learn Markdown -> plain CommonMark, for a github source with `markup: docfx`.

Microsoft's documentation repositories (dotnet/docs and its kin) are Markdown with extensions that CommonMark
would read as stray text. Cleaned here, before the generic Markdown path:

  :::code ...:::, :::image ...:::, :::video ...:::   dropped (code is not prose; the engine drops code blocks too)
  :::zone pivot="x" / :::zone-end, :::row::: ...        the markers go, the content stays
  [!INCLUDE [..](..)], [!code-csharp[..](..)], [!VIDEO ..]   dropped (an include's text is not in this file)
  > [!NOTE] / [!TIP] / [!IMPORTANT] / [!WARNING] / [!CAUTION]   becomes "Note:", "Tip:", ... at the callout's start
  <xref:System.Collections.Generic.List`1.Add*>          becomes `Add` in code font; displayProperty=nameWithType
                                                         keeps the type: `List.Add`
  [text](xref:uid)                                       becomes plain text
  # [Windows](#tab/windows)                              becomes the heading "Windows"; the `---` that closes a tab
                                                         group goes
  ## Heading {#custom-id}                                loses the id
  ## See also / Next steps / Related content             sections of links only, dropped to the next `## `

The shared text cleaner closes the gap before a full stop ("word ." -> "word."), which would turn "in .NET" into
"in.NET" and "the .dll file" into "the.dll file". `clean` therefore puts an invisible U+200B before such a dot and
`restore` takes it out of the finished text; text/emit.py itself stays as it is, since Wikipedia's sent_ids
depend on it.
"""
import hashlib
import posixpath
import re
import textwrap

DROP_SECTIONS = {"see also", "next steps", "related content", "related articles", "additional resources",
                 "learn more", "related resources"}
_FENCE = re.compile(r"^\s*(```|~~~)")
_BLOCK_ONE_LINE = re.compile(r"^\s*:::(code|image|video|no-loc)\b.*?:::\s*$")
_MARKER = re.compile(r"^\s*:::(zone|zone-end|row|row-end|column|column-end|image-end|moniker|moniker-end|form)\b.*$")
_INCLUDE_LINE = re.compile(r"^\s*\[!(INCLUDE|VIDEO|code-[\w-]+|div|sample-.*?)\b[^\n]*\]\s*(\([^)]*\))?\s*$", re.I)
_INCLUDE_INLINE = re.compile(r"\[!INCLUDE\s*\[[^\]]*\]\([^)]*\)\]")
_CALLOUT = re.compile(r"^(\s*>\s*)\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*$", re.I | re.M)
_CALLOUT_LABEL = {"NOTE": "Note", "TIP": "Tip", "IMPORTANT": "Important", "WARNING": "Warning", "CAUTION": "Caution"}
_XREF = re.compile(r"<xref:([^>\s]+?)>")
_XREF_LINK = re.compile(r"\[([^\]]+)\]\(xref:[^)]*\)")
_TAB_HEADING = re.compile(r"^(#{1,6})\s+\[([^\]]+)\]\(#tab/[^)]*\)\s*$")
_HEADING_ID = re.compile(r"\s*\{#[\w\-.]+\}\s*$")
_TAB_END = re.compile(r"^\s*---\s*$")
_SHIELD = "\u200b"
_SPACE_DOT = re.compile(r"(?<=\s)\.(?=[A-Za-z0-9_])")      # " .NET", " .dll": a dot that starts a word


def _xref(m):
    uid = m.group(1)
    base, _, query = uid.partition("?")
    base = re.sub(r"\(.*$", "", base).rstrip("*")           # an overload's signature, a wildcard
    base = re.sub(r"`+\d*", "", base)                         # List`1 -> List
    parts = [p for p in base.split(".") if p]
    if not parts:
        return ""
    keep = 2 if "nameWithType" in query else 1
    return "`" + ".".join(parts[-keep:]) + "`"


# -- code listings ---------------------------------------------------------------
# With a `Listings` collector, `clean` keeps the code instead of dropping it: a fenced block, a `:::code` block and
# a `[!code-csharp[..](..)]` reference each become a line `⟦L<n>⟧` of their own in the text, and the code goes to
# the collector. The text layer anchors each marker to the sentence before it (extract/sentences.py).
MARK_RE = re.compile(r"⟦L(\d+)⟧")
_CODE_ATTR = re.compile(r'(\w+)="([^"]*)"')
_CODE_BLOCK = re.compile(r"^\s*:::code\b(.*?):::\s*$")
_CODE_REF = re.compile(r"^\s*\[!code-([\w-]+)\[[^\]]*\]\(([^)]+)\)\]\s*$", re.I)
_MARKER_LINE = re.compile(r"^\s*(?://|'|#|--|<!--|/\*|\*|;)\s*</?[\w.\-]+>\s*(?:-->|\*/)?\s*$")
_REGION_LINE = re.compile(r"^\s*#\s*(end)?region\b", re.I)
LANG_ALIASES = {"cs": "csharp", "c#": "csharp", "fs": "fsharp", "f#": "fsharp", "vbnet": "vb", "vbscript": "vb",
                "ps": "powershell", "pwsh": "powershell", "sh": "bash", "shell": "bash", "js": "javascript",
                "ts": "typescript", "yml": "yaml", "c++": "cpp"}


def lang_of(info):
    word = (info or "").strip().split(" ")[0].split("{")[0].split("-interactive")[0].lower()
    return LANG_ALIASES.get(word, word)


def code_id(title_hint, lang, code):
    return hashlib.sha1(f"{title_hint}\n{lang}\n{code}".encode()).hexdigest()[:12]


class Listings:
    """The code a page carries: [{"n", "lang", "code", "source"}] in page order. `drop` lists languages to leave
    out (a course with no Visual Basic), `max_lines` skips blocks longer than that."""

    def __init__(self, drop=(), max_lines=80, read=None):
        self.items, self.skipped = [], {"language": 0, "long": 0, "missing": 0, "empty": 0}
        self.drop = {LANG_ALIASES.get(str(d).lower(), str(d).lower()) for d in drop}
        self.max_lines = int(max_lines)
        self.read = read           # read(path as written in the Markdown) -> file text or None

    def add(self, lang, code, source=None, indent=""):
        code = textwrap.dedent(code).strip("\n")
        code = "\n".join(l.rstrip() for l in code.split("\n")).strip("\n")
        if not code.strip():
            self.skipped["empty"] += 1
            return []
        if lang in self.drop:
            self.skipped["language"] += 1
            return []
        if code.count("\n") + 1 > self.max_lines:
            self.skipped["long"] += 1
            return []
        self.items.append({"n": len(self.items), "lang": lang, "code": code, "source": source})
        return ["", f"{indent}⟦L{len(self.items) - 1}⟧", ""]


def _ranges(spec, n):
    """1-based line ranges "1-5,9,12-" -> sorted line indexes."""
    out = []
    for part in str(spec).replace("L", "").split(","):
        m = re.fullmatch(r"\s*(\d+)?\s*(-\s*(\d+)?)?\s*", part)
        if not m or not (m.group(1) or m.group(3)):
            continue
        a = int(m.group(1) or 1)
        b = int(m.group(3) or n) if m.group(2) else a
        out += range(max(1, a) - 1, min(n, b))
    return sorted(set(out))


def snippet(text, ident=None, rng=None):
    """The part of a source file a DocFX reference names: a named region (`// <name>` ... `// </name>` or
    `#region name`), or line ranges. Region marker lines never reach the output."""
    lines = text.replace("\r\n", "\n").split("\n")
    if ident:
        name = re.escape(ident)
        start = next((i for i, l in enumerate(lines)
                      if re.match(rf"^\s*(?://|'|#|--|<!--|/\*|\*|;)\s*<{name}>\s*(?:-->|\*/)?\s*$", l, re.I)), None)
        if start is not None:
            end = next((i for i in range(start + 1, len(lines))
                        if re.match(rf"^\s*(?://|'|#|--|<!--|/\*|\*|;)\s*</{name}>", lines[i], re.I)), len(lines))
            lines = lines[start + 1:end]
        else:
            start = next((i for i, l in enumerate(lines) if re.match(rf"^\s*#\s*region\s+{name}\s*$", l, re.I)), None)
            if start is None:
                return None
            depth, end = 1, len(lines)
            for i in range(start + 1, len(lines)):
                if re.match(r"^\s*#\s*region\b", lines[i], re.I):
                    depth += 1
                elif re.match(r"^\s*#\s*endregion\b", lines[i], re.I):
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            lines = lines[start + 1:end]
    elif rng:
        lines = [lines[i] for i in _ranges(rng, len(lines))]
    lines = [l for l in lines if not _MARKER_LINE.match(l) and not _REGION_LINE.match(l)]
    return "\n".join(lines)


def _from_file(L, lang, path, ident=None, rng=None):
    raw = L.read(path) if L.read else None
    if raw is None:
        L.skipped["missing"] += 1
        return None
    code = snippet(raw, ident, rng)
    if code is None:
        L.skipped["missing"] += 1
        return None
    return code


def _code_block(L, line):
    m = _CODE_BLOCK.match(line)
    attrs = dict(_CODE_ATTR.findall(m.group(1)))
    src = attrs.get("source")
    if not src:
        return []
    code = _from_file(L, attrs.get("language"), src, attrs.get("id"), attrs.get("range"))
    lang = lang_of(attrs.get("language") or posixpath.splitext(src)[1].lstrip("."))
    return [] if code is None else L.add(lang, code, src, indent=line[:len(line) - len(line.lstrip())])


def _code_ref(L, line):
    m = _CODE_REF.match(line)
    lang, ref = lang_of(m.group(1)), m.group(2).strip()
    ref = ref.split(" ")[0]
    path, _, query = ref.partition("?")
    path, _, frag = path.partition("#")
    rng = ident = None
    if re.fullmatch(r"L[\d\-L,]+", frag or ""):
        rng = frag
    elif frag:
        ident = frag
    for k in query.split("&"):
        if k.startswith("range="):
            rng = k[6:]
    code = _from_file(L, lang, path, ident, rng)
    return [] if code is None else L.add(lang, code, path, indent=line[:len(line) - len(line.lstrip())])


def clean(md, listings=None):
    """The Markdown with DocFX's extensions removed (front matter is left for the Markdown path to strip).
    With a `Listings` collector the code is kept: see above."""
    lines, out, fence, skipping = md.replace("\r\n", "\n").split("\n"), [], False, False
    front = False
    block, indent, fence_ch, info = [], "", "", ""
    for n, line in enumerate(lines):
        if n == 0 and line.strip() == "---":
            front = True
            out.append(line)
            continue
        if front:
            out.append(line)
            front = line.strip() != "---"
            continue
        if _FENCE.match(line) and not fence:
            fence = True
            indent = line[:len(line) - len(line.lstrip())]
            m = re.match(r"^\s*(```+|~~~+)\s*(.*)$", line)
            fence_ch, info = m.group(1)[0], m.group(2)
            block = []
            if listings is None:
                out.append(line)
            continue
        if fence:
            if re.match(rf"^\s*{re.escape(fence_ch)}{{3,}}\s*$", line):
                fence = False
                if listings is None:
                    out.append(line)
                else:
                    cut = len(indent)
                    out += listings.add(lang_of(info), "\n".join(l[cut:] if l[:cut].strip() == "" else l for l in block),
                                        indent=indent)
            elif listings is None:
                out.append(line)
            else:
                block.append(line)
            continue
        h = re.match(r"^(#{1,6})\s+(.*?)\s*$", line)
        if h:
            title = _HEADING_ID.sub("", h.group(2)).strip().casefold()
            if len(h.group(1)) == 2:
                skipping = title in DROP_SECTIONS
            elif len(h.group(1)) == 1:
                skipping = False
        if skipping:
            continue
        if listings is not None and _CODE_BLOCK.match(line):
            out += _code_block(listings, line)
            continue
        if listings is not None and _CODE_REF.match(line):
            out += _code_ref(listings, line)
            continue
        if _BLOCK_ONE_LINE.match(line) or _MARKER.match(line) or _INCLUDE_LINE.match(line):
            continue
        t = _TAB_HEADING.match(line)
        if t:
            out.append(f"{t.group(1)} {t.group(2)}")
            continue
        if _TAB_END.match(line) and out and not out[-1].strip():
            continue                                          # the `---` that closes a tab group
        line = _HEADING_ID.sub("", line) if h else line
        line = _INCLUDE_INLINE.sub("", line)
        line = _CALLOUT.sub(lambda m: f"{m.group(1)}**{_CALLOUT_LABEL[m.group(2).upper()]}:**", line)
        line = _XREF_LINK.sub(r"\1", line)
        line = _XREF.sub(_xref, line)
        out.append(line)
    if fence and listings is not None and block:       # a fence the page never closed
        out += listings.add(lang_of(info), "\n".join(block), indent=indent)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out))
    return _SPACE_DOT.sub(_SHIELD + ".", text)


def restore(text):
    """Take the shield back out of text cleaned from `clean`'s output."""
    return (text or "").replace(_SHIELD, "")
