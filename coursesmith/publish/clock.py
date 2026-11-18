"""Time lines for chronological subjects: the span a unit covers and the proportional-clock line.

The proportional calendar squeezes Earth's history into one 365-day year: the origin (the base of the Hadean
on the ICS chart, 4,567 Ma) is midnight on January 1, and the present is midnight at the end of December 31.
"""
from datetime import datetime, timedelta

YEAR_S = 365 * 86400


def fmt_age(ma):
    """'4.57 billion years ago', '539 million years ago', '11,700 years ago', '1815 CE'."""
    if ma is None:
        return ""
    if ma >= 1000:
        return f"{ma / 1000:.3g} billion years ago"
    if ma >= 1:
        return f"{ma:.3g} million years ago"
    years = ma * 1e6
    if years >= 10000:
        return f"{float(f'{years:.3g}'):,.0f} years ago"
    ce = round(1950 - years)
    return f"{ce} CE" if ce > 0 else f"{1 - ce} BCE"


def fmt_span(old_ma, young_ma):
    a, b = fmt_age(old_ma), fmt_age(young_ma)
    if not b or a == b:
        return a
    for suffix in (" billion years ago", " million years ago", " years ago", " CE", " BCE"):
        if a.endswith(suffix) and b.endswith(suffix):
            return f"{a[: -len(suffix)]} to {b[: -len(suffix)]}{suffix}"
    return f"{a} to {b}"


def _seconds_before_midnight(ma, origin_ma):
    return max(0.0, ma / origin_ma * YEAR_S)


def _moment(s):
    """(kind, text) for a moment s seconds before the year's final midnight."""
    if s < 1:
        return "last", None
    if s < 60:
        return "sec", f"{s:.1f}".rstrip("0").rstrip(".") if s < 10 else f"{s:.0f}"
    t = datetime(2001, 1, 1) + timedelta(seconds=YEAR_S - s)
    if s < 86400:
        return "time", t.strftime("%-I:%M:%S %p" if s < 3600 else "%-I:%M %p").lower()
    return "day", t.strftime("%B %-d")


def clock_line(old_ma, young_ma, origin_ma):
    a = _moment(_seconds_before_midnight(old_ma, origin_ma))
    b = _moment(_seconds_before_midnight(young_ma if young_ma is not None else old_ma, origin_ma))
    dec31 = " on December 31"
    if a == b:
        when = {"last": "in the last second before midnight" + dec31,
                "sec": f"{a[1]} seconds before midnight{dec31}",
                "time": f"at {a[1]}{dec31}", "day": f"on {a[1]}"}[a[0]]
    elif a[0] == "day" and b[0] == "day":
        when = f"between {a[1]} and {b[1]}"
    elif a[0] == "day":
        tail = {"time": f"{b[1]}{dec31}", "sec": f"{b[1]} seconds before midnight{dec31}",
                "last": "the last second of December 31"}[b[0]]
        when = f"between {a[1]} and {tail}"
    elif a[0] == "time":
        tail = {"time": b[1], "sec": f"{b[1]} seconds before midnight", "last": "the last second"}[b[0]]
        when = f"between {a[1]} and {tail}{dec31}"
    elif a[0] == "sec" and b[0] == "sec":
        when = f"between {a[1]} and {b[1]} seconds before midnight{dec31}"
    else:
        when = f"in the last {a[1]} seconds before midnight{dec31}"
    return f"On a proportional calendar these events happen {when}."
