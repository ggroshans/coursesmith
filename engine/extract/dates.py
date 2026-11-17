"""Dated-expression detection and normalisation to Ma (millions of years before present).

Used during the crawl for branch-saturation tracking, and in Phase 3 for
extraction. Conventions: BP = before 1950; b2k = before 2000 (so b2k - 50 = BP);
BCE/CE years are converted to BP via 1950.
"""
import re

NUM = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"
APPROX = r"(?:(?:c\.|ca\.|circa|about|around|approximately|roughly|~|≈)\s*)?"
RANGE = rf"(?P<n1>{NUM})(?:\s*(?:–|—|-|to|and)\s*{APPROX}(?P<n2>{NUM}))?"
UNC = rf"(?:\s*(?:±|\+/-|\+/−)\s*(?P<unc>{NUM})(?:\s*/\s*(?:{NUM}))?|\s*\+\s*(?P<uncp>{NUM})(?:\s*[−–-]\s*(?:{NUM}))?)?"

# (regex unit alternatives, multiplier to Ma, kind)
_UNITS = [
    (r"Ga|Gya|bya|b\.y\.a\.|Gyr ago|billion years ago|billion years before present", 1000.0, "geo"),
    (r"Ma|Mya|mya|m\.y\.a\.|Myr ago|million years ago|million years before present", 1.0, "geo"),
    (r"ka|kya|kyr BP|kyr ago|ka BP|thousand years ago|thousand years [Bb]efore [Pp]resent|thousand years BP", 1e-3, "geo"),
    (r"cal(?:ibrated)? ?(?:yr )?BP|years? BP|years? [Bb]efore [Pp]resent|BP", 1e-6, "bp"),
    # Plain "N years ago" counts back from today, not from 1950 ("326 years ago" = 1700 CE, written in 2026).
    (r"years? ago", 1e-6, "ago"),
    (r"b2k", 1e-6, "b2k"),
    (r"BCE|BC", 1e-6, "bce"),
    (r"CE|AD", 1e-6, "ce"),
]
DATE_RE = re.compile(
    rf"(?<![\w./+])(?<!±)(?<!± )(?<!\+ )(?<![−–]){APPROX}{RANGE}{UNC}\s*(?:\(\s*)?(?P<unit>"
    + "|".join(f"(?:{u})" for u, _, _ in _UNITS)
    + r")(?![\w])"
)
_UNIT_LOOKUP = [(re.compile(rf"^(?:{u})$"), mult, kind) for u, mult, kind in _UNITS]

# Ranges the main pattern misses (Hadean pilot, Phase 3):
# "between about 4.4 billion and 4.0 billion years ago" (a magnitude word on both ends)
RANGE_MAG_RE = re.compile(
    rf"(?<![\w.]){APPROX}(?P<n1>{NUM})\s*(?P<m1>billion|million|thousand)(?:\s+years)?\s*(?:–|—|-|to|and)\s*"
    rf"{APPROX}(?P<n2>{NUM})\s*(?P<m2>billion|million|thousand)\s+years\s+(?:ago|before present)")
# "2.023 billion (± 4 million) years ago" (the uncertainty between the magnitude and "years ago")
MAG_UNC_RE = re.compile(
    rf"(?<![\w.]){APPROX}(?P<n1>{NUM})\s*(?P<m1>billion|million|thousand)\s*\(\s*(?:±|\+/-|\+/−|plus or minus)\s*"
    rf"(?P<u>{NUM})\s*(?P<mu>billion|million|thousand)?(?:\s+years)?\s*\)\s*years\s+(?:ago|before present|old)")
# "4567.3 ± 0.16 – 4031 ± 3 Ma" (an uncertainty on both ends)
RANGE_UNC_RE = re.compile(
    rf"(?<![\w.]){APPROX}(?P<n1>{NUM})\s*(?:±|\+/-|\+/−)\s*(?P<u1>{NUM})\s*(?:–|—|-|to)\s*{APPROX}(?P<n2>{NUM})"
    rf"(?:\s*(?:±|\+/-|\+/−)\s*(?P<u2>{NUM}))?\s*(?P<unit>Ga|Ma|ka)(?![\w])")

# Ages stated as "X billion years old", "a 3.5-billion-year-old ...", "an age of 2.023 billion years",
# "dated to 1.8 billion years" (kind 'age_old').
_MAG = {"billion": 1000.0, "million": 1.0, "thousand": 1e-3}
AGE_OLD_RE = re.compile(
    rf"(?<![\w.]){APPROX}(?P<n1>{NUM})(?:\s*(?:–|—|-|to|and)\s*{APPROX}(?P<n2>{NUM}))?{UNC}"
    r"\s*[- ](?P<mag>billion|million|thousand)[- ]years?[- ](?:old\b|in age\b|of age\b)")
AGE_AT_RE = re.compile(
    rf"\b(?:ages?|aged|dated|dating)(?:\s+(?:of|at|to|is|was|estimated at|back))?\s+(?:to\s+)?{APPROX}"
    rf"(?P<n1>{NUM})(?:\s*(?:–|—|-|to|and)\s*{APPROX}(?P<n2>{NUM}))?{UNC}"
    r"\s*(?P<mag>billion|million|thousand)\s+years\b(?!\s+(?:ago|before|BP|old|later|earlier|after))")
ALT_AFTER_RE = re.compile(
    rf"^(?:\s*\(?\s*(?:±|\+/-|plus or minus)[^)]{{0,40}}\)?)?(?:\[\^\d+\])*\s*(?:or|versus|vs\.?)\s+{APPROX}(?P<n1>{NUM})"
    r"\s*(?P<mag>billion|million|thousand)\s+years\b(?!\s+(?:ago|before|BP|later|earlier|after))")
# Uncertainty stated after the date: "(± 4 million years)", "+13/–17 Ma".
PM_AFTER_RE = re.compile(
    rf"^\s*\(?\s*(?:±|\+/-|\+/−|plus or minus)\s*(?P<u>{NUM})\s*(?P<mag>billion|million|thousand|Ga|Ma|ka|Myr|kyr)?")
ASYM_AFTER_RE = re.compile(rf"^\s*\+\s*(?P<up>{NUM})\s*/\s*[-–−]\s*(?P<dn>{NUM})")
_MAG_UNIT = {"billion": 1000.0, "Ga": 1000.0, "million": 1.0, "Ma": 1.0, "Myr": 1.0, "thousand": 1e-3, "ka": 1e-3,
             "kyr": 1e-3}

# Calendar years in running text: "In 1815", "since 1950", "by 2023" (marked kind='calendar').
CAL_RE = re.compile(r"\b(?:[Ii]n|[Bb]y|[Ss]ince|[Uu]ntil|[Dd]uring|[Ff]rom|[Bb]etween)\s+(?P<y>1[0-9]{3}|20[0-2][0-9])\b")


def _num(s):
    return float(s.replace(",", ""))


PRESENT_YEAR = 2026


def _to_ma(v, mult, kind):
    if kind == "ago":
        return (v - (PRESENT_YEAR - 1950)) * mult
    if kind == "b2k":
        return (v - 50) * mult
    if kind == "bce":
        return (v + 1950) * mult
    if kind == "ce":
        return (1950 - v) * mult
    return v * mult


def find_dates(text, calendar=True):
    """Yield dicts: date_text, date_ma (older end for ranges), young_ma, uncertainty_ma, kind."""
    out = []
    consumed = -1
    pre = []  # spans claimed by the two range patterns above
    for m in RANGE_MAG_RE.finditer(text):
        a, b = _num(m.group("n1")) * _MAG[m.group("m1")], _num(m.group("n2")) * _MAG[m.group("m2")]
        out.append({"date_text": m.group(0).strip(), "date_ma": max(a, b), "young_ma": min(a, b),
                    "uncertainty_ma": None, "kind": "geo", "span": (m.start(), m.end())})
        pre.append((m.start(), m.end()))
    for m in MAG_UNC_RE.finditer(text):
        mult = _MAG[m.group("m1")]
        umult = _MAG[m.group("mu")] if m.group("mu") else mult
        out.append({"date_text": m.group(0).strip(), "date_ma": _num(m.group("n1")) * mult, "young_ma": None,
                    "uncertainty_ma": _num(m.group("u")) * umult, "kind": "geo", "span": (m.start(), m.end())})
        pre.append((m.start(), m.end()))
    for m in RANGE_UNC_RE.finditer(text):
        if any(a <= m.start() < b for a, b in pre):
            continue
        mult = {"Ga": 1000.0, "Ma": 1.0, "ka": 1e-3}[m.group("unit")]
        a, b = _num(m.group("n1")) * mult, _num(m.group("n2")) * mult
        u = max(_num(m.group("u1")), _num(m.group("u2")) if m.group("u2") else 0) * mult
        out.append({"date_text": m.group(0).strip(), "date_ma": max(a, b), "young_ma": min(a, b),
                    "uncertainty_ma": u, "kind": "geo", "span": (m.start(), m.end())})
        pre.append((m.start(), m.end()))
    for m in DATE_RE.finditer(text):
        if m.start() < consumed or any(a <= m.start() < b for a, b in pre):
            continue  # part of a range above, or of the previous date's '+13/–17 Ma' uncertainty
        unit = m.group("unit")
        for rx, mult, kind in _UNIT_LOOKUP:
            if rx.match(unit):
                break
        else:
            continue
        n1 = _num(m.group("n1"))
        n2 = _num(m.group("n2")) if m.group("n2") else None
        # "421–395,000 years ago": the first number's thousands are implied by the second.
        if (n2 is not None and "," in m.group("n2") and "," not in m.group("n1") and n1 < 1000 <= n2
                and 0.5 <= n1 * 1000 / n2 <= 2):
            n1 *= 1000
        # 'years ago' etc. with tiny numbers are almost always durations or noise.
        if kind in ("bp", "ago") and n1 < 50:
            continue
        if kind in ("bce", "ce") and n1 > 20000:
            continue
        a = _to_ma(n1, mult, kind)
        b = _to_ma(n2, mult, kind) if n2 is not None else None
        old, young = (max(a, b), min(a, b)) if b is not None else (a, None)
        u_raw = m.group("unc") or m.group("uncp")
        unc = _to_ma(_num(u_raw), mult, "geo") if u_raw and kind not in ("bce", "ce") else None
        if unc is None and kind not in ("bce", "ce"):
            unc, consumed = _after_unc(text, m.end(), mult)
        out.append({"date_text": m.group(0).strip(), "date_ma": old, "young_ma": young,
                    "uncertainty_ma": unc, "kind": "bp" if kind == "ago" else kind, "span": (m.start(), m.end())})
    taken = [d["span"] for d in out]
    for rx in (AGE_OLD_RE, AGE_AT_RE):
        for m in rx.finditer(text):
            if any(a <= m.start("n1") < b for a, b in taken):
                continue
            mult = _MAG[m.group("mag")]
            a = _num(m.group("n1")) * mult
            b = _num(m.group("n2")) * mult if m.group("n2") else None
            old, young = (max(a, b), min(a, b)) if b is not None else (a, None)
            unc = _num(m.group("unc")) * mult if m.group("unc") else _after_unc(text, m.end(), mult)[0]
            out.append({"date_text": m.group(0).strip(), "date_ma": old, "young_ma": young,
                        "uncertainty_ma": unc, "kind": "age_old", "span": (m.start(), m.end())})
            taken.append((m.start(), m.end()))
            # "... 2.023 billion years (± 4 million years) or 2.19 billion years": the competing value.
            alt = ALT_AFTER_RE.match(text[m.end():m.end() + 120])
            if alt:
                st, en = m.end() + alt.start("n1"), m.end() + alt.end()
                out.append({"date_text": text[st:en].strip(), "date_ma": _num(alt.group("n1")) * _MAG[alt.group("mag")],
                            "young_ma": None, "uncertainty_ma": None, "kind": "age_old", "span": (st, en)})
                taken.append((st, en))
    for d in out:  # float noise from unit multipliers (2023.0000000000002)
        for k in ("date_ma", "young_ma", "uncertainty_ma"):
            if d[k] is not None:
                d[k] = round(d[k], 9)
    if calendar:
        for m in CAL_RE.finditer(text):
            y = int(m.group("y"))
            out.append({"date_text": m.group(0), "date_ma": (1950 - y) * 1e-6, "young_ma": None,
                        "uncertainty_ma": None, "kind": "calendar", "span": (m.start(), m.end())})
    return out


def _after_unc(text, end, mult):
    """Uncertainty written after a date: '(± 4 million years)' or '+13/–17 Ma' (the larger side).
    Returns (value or None, end of the consumed text)."""
    tail = text[end:end + 60]
    m = PM_AFTER_RE.match(tail)
    if m:
        return _num(m.group("u")) * (_MAG_UNIT.get(m.group("mag"), mult) if m.group("mag") else mult), end + m.end()
    m = ASYM_AFTER_RE.match(tail)
    if m:
        u = re.match(r"\s*(Ga|Ma|ka)\b", tail[m.end():])
        return max(_num(m.group("up")), _num(m.group("dn"))) * mult, end + m.end() + (u.end() if u else 0)
    return None, end


def fingerprints(text):
    """Distinct geologic-date values (3 significant figures) in a text: the
    saturation proxy for 'new events' during the crawl."""
    fps = set()
    for d in find_dates(text, calendar=False):
        v = d["date_ma"]
        if v > 0:
            fps.add(float(f"{v:.3g}"))
    return fps
