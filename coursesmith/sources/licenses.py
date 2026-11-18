"""License classes: what a source's license lets a course do with its content.

Facts are not copies, but a course paraphrases its sources and ships attribution, so the class decides whether
a subject meant for the public (`distribution: public`) may cite a source at all. A subject for personal use
(the default) may cite anything it can attribute.
"""
import re

# class -> may a publicly distributed course cite it
PUBLIC = {
    "cc-by-sa": True,
    "cc-by": True,
    "public-domain": True,
    "permissive": True,
    "copyleft": True,
    "ietf-trust": True,
    "cc-by-nc": False,
    "cc-by-nc-sa": False,
    "cc-by-nd": False,
    "cc-by-nc-nd": False,
    "all-rights-reserved": False,
    "unknown": False,
}

# longest patterns first: "ccbyncnd" must win over "ccbync" and "ccby"
_PATTERNS = [
    ("ccbyncnd", "cc-by-nc-nd"),
    ("ccbyncsa", "cc-by-nc-sa"),
    ("ccbync", "cc-by-nc"),
    ("ccbynd", "cc-by-nd"),
    ("ccbysa", "cc-by-sa"),
    ("ccby", "cc-by"),
    ("cc0", "public-domain"),
    ("publicdomain", "public-domain"),
    ("unlicense", "public-domain"),
    ("ietftrust", "ietf-trust"),
    ("ietf", "ietf-trust"),
    ("lgpl", "copyleft"),
    ("agpl", "copyleft"),
    ("gpl", "copyleft"),
    ("allrightsreserved", "all-rights-reserved"),
    ("mit", "permissive"),
    ("apache", "permissive"),
    ("bsd", "permissive"),
    ("isc", "permissive"),
    ("mpl", "permissive"),
    ("psf", "permissive"),
    ("zlib", "permissive"),
]


def classify(name):
    """License class for an SPDX id or a human license name ("CC BY-SA 4.0", "CC-BY-NC-ND-4.0", "MIT")."""
    s = re.sub(r"[^a-z0-9]", "", str(name or "").lower())
    if s in ("pd", "pd0"):
        return "public-domain"
    for pat, cls in _PATTERNS:
        if pat in s:
            return cls
    return "unknown"


# (phrase in a license text, class), most specific first
_TEXT_PATTERNS = [
    ("attribution-noncommercial-noderivatives", "cc-by-nc-nd"),
    ("attribution-noncommercial-sharealike", "cc-by-nc-sa"),
    ("attribution-noncommercial", "cc-by-nc"),
    ("attribution-noderivatives", "cc-by-nd"),
    ("attribution-sharealike", "cc-by-sa"),
    ("creative commons attribution", "cc-by"),
    ("cc0", "public-domain"),
    ("public domain dedication", "public-domain"),
    ("this is free and unencumbered software released into the public domain", "public-domain"),
    ("gnu lesser general public license", "copyleft"),
    ("gnu general public license", "copyleft"),
    ("gnu affero general public license", "copyleft"),
    ("apache license", "permissive"),
    ("permission is hereby granted, free of charge", "permissive"),
    ("redistribution and use in source and binary forms", "permissive"),
    ("all rights reserved", "all-rights-reserved"),
]


def detect_from_text(text):
    """License class from the text of a LICENSE file, for repositories GitHub cannot match to an SPDX id."""
    s = re.sub(r"\s+", " ", str(text or "").lower())
    for phrase, cls in _TEXT_PATTERNS:
        if phrase in s:
            return cls
    return "unknown"


def is_public(cls, overrides=None):
    table = {**PUBLIC, **(overrides or {})}
    v = table.get(cls, False)
    return bool(v.get("public")) if isinstance(v, dict) else bool(v)


def normalize(raw, fallback=None):
    """A license as {name, url, class, ...}. Accepts a string, a dict with name/spdx/url/class, or None."""
    if not raw:
        return dict(fallback) if fallback else None
    if isinstance(raw, str):
        raw = {"name": raw}
    out = dict(raw)
    out.setdefault("name", out.get("spdx") or "")
    if not out.get("class"):
        out["class"] = classify(out.get("spdx") or out.get("name"))
    return out
