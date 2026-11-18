"""Which sources a course cites, under which licenses, and what that means for sharing it.

One place computes this for the export (`license` in course.json), the EPUB's Sources and license page and the
`publish check` distribution gate, so they never disagree. An entry's `sources[]` items written before other
sources existed have no `key`, `source` or `license`; `norm_source` fills them in as Wikipedia.
"""
from collections import defaultdict

from ..sources import licenses
from ..sources.keys import is_qualified
from ..sources.registry import Registry

CC_BY_SA = {"name": "CC BY-SA 4.0", "url": "https://creativecommons.org/licenses/by-sa/4.0/", "class": "cc-by-sa"}
WIKIPEDIA_TEXT = ("Adapted from Wikipedia articles available under the Creative Commons Attribution-ShareAlike 4.0 "
                  "License. Facts were extracted from the revisions listed in `pages`; the full list of authors of "
                  "each article is in its page history. Anything built from this file must keep this attribution "
                  "and be shared under the same license.")
PERSONAL = "Personal use only (mixed sources)"


def norm_source(s):
    """An entry's `sources[]` item with every field a reader may rely on."""
    out = dict(s)
    out["key"] = s.get("key") or s["title"]
    out["source"] = s.get("source") or "wikipedia"
    out["version"] = s.get("version") or (str(s["revid"]) if s.get("revid") is not None else None)
    return out


def source_rows(entries, registry, store=None):
    """One row per cited page across `entries`: name, url, version, license, tier, cited sentence count."""
    rows = {}
    for e in entries:
        for raw in e.get("sources") or []:
            s = norm_source(raw)
            key = s["key"]
            r = rows.get(key)
            if r is None:
                ad = registry.maybe_for_key(key)
                lic = s.get("license") or (ad.license if ad else None) or CC_BY_SA
                lic = licenses.normalize(lic)
                r = rows[key] = {
                    "key": key, "name": s["title"], "source": s["source"], "adapter": ad.adapter if ad else "wikipedia",
                    "source_label": ad.label if ad else s["source"], "url": s.get("url"), "revid": s.get("revid"),
                    "version": s["version"], "tier": ad.tier if ad else "reference", "license": lic,
                    "license_class": lic.get("class") or "unknown", "retrieved": None, "_sids": set(),
                    "permalink": ad.permalink(s) if ad else s.get("url"),
                    "version_label": ad.version_label(s["version"]) if ad else (f"revision {s['revid']}" if s.get("revid") else "")}
                if store is not None and is_qualified(key):
                    try:
                        r["retrieved"] = (store.load_page(key) or {}).get("retrieved")
                    except (KeyError, OSError, ValueError):
                        pass
            r["_sids"] |= set(s.get("sent_ids") or [])
    out = []
    for r in rows.values():
        r["n_sentences"] = len(r.pop("_sids"))
        out.append(r)
    return sorted(out, key=lambda r: (r["source_label"], r["name"].lower()))


def is_wikipedia_only(rows):
    return all(r["adapter"] == "wikipedia" and r["license_class"] == "cc-by-sa" for r in rows)


def summarize(rows, registry, distribution="personal"):
    """The course's license: {name, url, text, restricted, classes, by_license}. Wikipedia-only courses keep the
    exact wording they always had."""
    by_license = defaultdict(list)
    for r in rows:
        by_license[(r["license"].get("name") or r["license_class"], r["license_class"])].append(r["source_label"])
    classes = {r["license_class"] for r in rows}
    restricted = sorted(c for c in classes if not registry.is_public(c))
    if is_wikipedia_only(rows):
        return {"name": CC_BY_SA["name"], "url": CC_BY_SA["url"], "text": WIKIPEDIA_TEXT, "restricted": [],
                "classes": sorted(classes), "by_license": {}, "wikipedia_only": True}
    if restricted:
        name, url = PERSONAL, ""
    elif classes & {"cc-by-sa", "copyleft"}:
        name, url = "Mixed open licenses, share-alike (see sources)", CC_BY_SA["url"]
    else:
        name, url = "Mixed open licenses (see sources)", ""
    lines = []
    for (lname, _), labels in sorted(by_license.items()):
        lines.append(f"{lname}: {', '.join(sorted(set(labels)))}.")
    text = "Adapted from the sources listed in `license.sources`, under these licenses. " + " ".join(lines)
    if "cc-by-sa" in classes or "copyleft" in classes:
        text += " Share-alike sources require anything built from this file to be shared under the same license."
    if restricted:
        text += (" Some sources do not allow redistribution or derivatives ("
                 + ", ".join(restricted) + "): this course is for personal reading only.")
    return {"name": name, "url": url, "text": text, "restricted": restricted, "classes": sorted(classes),
            "by_license": {f"{k[0]}": sorted(set(v)) for k, v in by_license.items()}, "wikipedia_only": False}


def distribution_problems(entries, registry, distribution):
    """With `distribution: public`, every cited source's license must allow it."""
    if distribution != "public":
        return []
    out = []
    for e in entries:
        for raw in e.get("sources") or []:
            s = norm_source(raw)
            ad = registry.maybe_for_key(s["key"])
            lic = licenses.normalize(s.get("license") or (ad.license if ad else None) or CC_BY_SA)
            if not registry.is_public(lic.get("class") or "unknown"):
                out.append(f"{e['id']}: cites {s['title']} ({lic.get('name') or 'unknown license'}, "
                           f"{lic.get('class')}), which does not allow public distribution; "
                           f"set `distribution: personal` or drop the source")
    return out


def course_registry(subject):
    return Registry.from_subject(subject)
