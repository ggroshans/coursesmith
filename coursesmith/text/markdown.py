"""Markdown -> cleaned text: CommonMark through markdown-it-py, then the generic HTML path.

A README is not an encyclopedia article. Badges and logos are dropped (they are images), code blocks are
dropped and counted (shell prompts and comments would read as headings and tables), the first H1 becomes the
page name, a pipe or leading `#` in prose is neutralized, and a heading nested in raw HTML is still found.
"""
import re

from .html import Doc, html_to_doc

_FRONT = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.S)


def _renderer():
    from markdown_it import MarkdownIt
    return MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])


def strip_front_matter(md):
    return _FRONT.sub("", md, count=1)


def markdown_to_doc(md, name="", resolve_link=None, drop=()):
    html = _renderer().render(strip_front_matter(md))
    return html_to_doc(f"<div>{html}</div>", name=name, resolve_link=resolve_link, drop=drop)


def markdown_to_text(md, name="", resolve_link=None):
    return markdown_to_doc(md, name, resolve_link).text


__all__ = ["Doc", "markdown_to_doc", "markdown_to_text", "strip_front_matter"]
