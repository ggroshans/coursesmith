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
import re

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


def clean(md):
    """The Markdown with DocFX's extensions removed (front matter is left for the Markdown path to strip)."""
    lines, out, fence, skipping = md.replace("\r\n", "\n").split("\n"), [], False, False
    front = False
    for n, line in enumerate(lines):
        if n == 0 and line.strip() == "---":
            front = True
            out.append(line)
            continue
        if front:
            out.append(line)
            front = line.strip() != "---"
            continue
        if _FENCE.match(line):
            fence = not fence
            out.append(line)
            continue
        if fence:
            out.append(line)
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
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out))
    return _SPACE_DOT.sub(_SHIELD + ".", text)


def restore(text):
    """Take the shield back out of text cleaned from `clean`'s output."""
    return (text or "").replace(_SHIELD, "")
