"""Page keys. A key names one page in the store, the sentence index and every subject file.

Wikipedia pages keep their bare title, so every id and file made before other sources existed stays valid.
Every other source uses `<prefix>><id>`:

    rfc>9110                                      an IETF RFC
    gh>owner/repo/path/to/file.md                 a file in a GitHub repository
    doc>redis.io/docs/latest/develop/foo/         a page on an allowlisted docs site
    pdf>source-name/file.pdf                      a PDF listed in subject.yaml
    paper>10.1145/1773912.1773922                 a paper, by DOI (or arxiv:ID)
    wiki>en.wikibooks.org/Computer_Networks       a page on a MediaWiki other than the default

`>` cannot appear in a MediaWiki title, so a qualified key never collides with a real article ("RFC 9110" is
one). It never starts a line, so it cannot be read as a blockquote, and it is none of `#` (the article#section
separator), `|` (dossier and table rows) or `[]{}` (footnote, reference and diagram syntax).
"""
import re

SEP = ">"

# characters the rest of the pipeline gives a meaning to; they are percent-encoded inside a source id
_UNSAFE = {"#": "%23", "|": "%7C", "[": "%5B", "]": "%5D", "{": "%7B", "}": "%7D", "<": "%3C", ">": "%3E"}


def is_qualified(key):
    return SEP in (key or "")


def clean_id(source_id):
    s = str(source_id).strip()
    for ch, enc in _UNSAFE.items():
        s = s.replace(ch, enc)
    return re.sub(r"\s+", "_", s)


def make_key(prefix, source_id):
    return f"{prefix}{SEP}{clean_id(source_id)}"


def split_key(key):
    """(prefix, source_id). A bare title is ("", title)."""
    if SEP not in key:
        return "", key
    prefix, rest = key.split(SEP, 1)
    return prefix, rest


def page_part(article):
    """The key of an entry's `article` field, which may carry a #Section."""
    return (article or "").split("#")[0]


def display(key):
    """A short human label for a key when no page record is at hand."""
    prefix, rest = split_key(key)
    if not prefix:
        return key
    if prefix == "rfc":
        return f"RFC {rest}"
    if prefix in ("gh", "doc", "pdf", "wiki"):
        return rest.rstrip("/").rsplit("/", 1)[-1].replace("_", " ") or rest
    return rest
