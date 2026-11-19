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
    ("postgresql", "permissive"),
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
    ("permission to use, copy, modify, and distribute this software and its documentation for any purpose, without fee", "permissive"),
    ("redistribution and use in source and binary forms", "permissive"),
    ("all rights reserved", "all-rights-reserved"),
]


# short names a LICENSE file or README states on one line, matched on word boundaries
_NAME_PATTERNS = [
    (re.compile(r"\bmit license\b", re.I), "permissive"),
    (re.compile(r"\bapache(?: license)?,? (?:version )?2\.0\b", re.I), "permissive"),
    (re.compile(r"\bbsd[- ](?:[23]-clause )?license\b", re.I), "permissive"),
    (re.compile(r"\bgnu (?:lesser |affero )?general public license\b|\b[la]?gpl[- ]?v?[23]\b", re.I), "copyleft"),
]
_CC_URL = re.compile(r"creativecommons\.org/(?:licenses/([a-z]+(?:-[a-z]+)*)|publicdomain/zero)/", re.I)
_CC_ABBREV = re.compile(r"\bcc[ -]by(?:[ -](?:nc|nd|sa))*\b|\bcc0\b", re.I)


def detect_from_text(text):
    """License class from the text of a LICENSE file, for repositories GitHub cannot match to an SPDX id.

    The license a file grants is the first one it names: a Creative Commons legal text opens with its title and
    ends with boilerplate that mentions CC0, which must not change the answer. So every sign (a Creative Commons
    link, an abbreviation like "CC BY-NC-ND 4.0", the long legal phrasing, a software license) is located and the
    earliest wins."""
    raw = str(text or "")
    found = []
    for m in _CC_URL.finditer(raw):
        found.append((m.start(), "public-domain" if m.group(1) is None else classify("cc-" + m.group(1))))
    for m in _CC_ABBREV.finditer(raw):
        found.append((m.start(), classify(m.group(0))))
    low = re.sub(r"\s+", " ", raw.lower())
    low = re.sub(r"share[- ]alike", "sharealike", low)
    for phrase, cls in _TEXT_PATTERNS:
        k = low.find(phrase)
        if k >= 0:
            if low.startswith("creative commons ", k - 17) and phrase != "creative commons attribution":
                k -= 17  # "Creative Commons Attribution-ShareAlike" opens where the generic phrase does
            found.append((k, cls))
    for rx, cls in _NAME_PATTERNS:
        m = rx.search(raw)
        if m:
            found.append((m.start(), cls))
    return min(found, key=lambda f: f[0])[1] if found else "unknown"


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
    out = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in dict(raw).items()}  # YAML dates
    out.setdefault("name", out.get("spdx") or "")
    if not out.get("class"):
        out["class"] = classify(out.get("spdx") or out.get("name"))
    return out
