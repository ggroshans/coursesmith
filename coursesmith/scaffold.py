"""coursesmith init: start a new subject.

    coursesmith init <slug> --title "How FRFR speakers work" [--seed Loudspeaker]... [--category C]...

Writes subjects/<slug>/subject.yaml with every setting commented, and a STATE.md stub. Works for a whole field
(fill in the hubs and the parts), a medium topic, or a niche question (seeds and a category or two are enough;
the planner and judge passes find the rest).
"""
import json

from . import config
from .util import slug as _slug

TEMPLATE = """\
slug: {slug}
title: {title}
short: {short}   # prefix for entry ids: {short}-<chapter>-001
description: >-
  {description}

# Pages the crawl always fetches: the subject's main article and anything a course on it must cover.
seeds: {seeds}

# Wikipedia's own maps of the subject. A broad field usually has some of these; a niche topic often has none,
# and that is fine: seeds, categories and the planner pass carry it.
hubs: {{}}
#   navboxes: [Template:Soil science topics]     # the navbox at the foot of the main article
#   index: Index of soil-related articles
#   vital: [Wikipedia:Vital articles/Level 4/Physical sciences#Pedology]
#   wikiproject: Soil                            # WikiProject name, for Top/High/Mid/Low importance

categories:
  roots: {categories}
  depth: 1          # 1 is clean; 2 needs `exclude`; 3 drifts
  exclude: []

scope:
  include_terms: {include}   # words a relevant title or description tends to contain
  exclude_terms: []          # words that mark a page as out (company, album, fictional...)
  exclude_desc: []           # short-description phrases that mark a page as out (city in, footballer...)
  person_terms: []           # occupations that mark a person page in this field (pedologist...)
  threshold: null            # scope score a page needs; null = 5. Lower it (3-4) for a small topic.

# per_unit: entries per unit; the course runs as many units as its entries need.
targets: {{per_unit: {per_unit}}}
ordering: pedagogical       # or chronological, for a history
edition: {{images: false, questions: false, proportional_clock: false}}
verification:
  works: openalex           # cited DOIs checked against OpenAlex/Crossref abstracts
  authorities: []           # see guides/VERIFICATION_GUIDE.md

# Hints for `frame build`. With no parts, the whole subject is one part and its chapters come from Wikipedia's
# categories; the syllabus planner pass (`frame plan-packet`) then proposes the branches. For a large subject,
# name the parts and give each hints (words in titles, descriptions or categories) or pinned seeds.
frame: {{}}
#   foundations: [Loudspeaker, Sound pressure]   # the few concepts everything else builds on
#   parts:
#     - key: found
#       title: Foundations
#       foundations: true
#     - key: design
#       title: Speaker design
#       hints: [driver, enclosure, crossover, ~horn]
#       chapters:
#         - title: Drivers
#           seeds: [Loudspeaker driver, Tweeter, Woofer]
#     - key: hist
#       title: History, people and frontiers
#       history: true                            # people and organizations land here
"""

STATE = """\
# {title} — state

_Update after every step. `coursesmith status {slug}` prints the live numbers._

## Where it stands
- New subject: `subject.yaml` written, nothing crawled yet.

## Next steps
1. Fill in `subject.yaml` (seeds, categories; hubs and parts for a large subject).
2. `coursesmith frame build {slug}`, then review `frame.yaml` and `reports/frame_report.md`.
3. Follow the pipeline in README.md.
"""


class InitError(RuntimeError):
    pass


def _flow(xs):
    return json.dumps(list(xs or []), ensure_ascii=False)


def init(slug, title, seeds=(), categories=(), per_unit=(4, 5), force=False, log=print):
    if slug != _slug(slug):
        raise InitError(f"slug must be lowercase words joined by hyphens, e.g. {_slug(slug)!r}")
    d = config.SUBJECTS / slug
    if (d / "subject.yaml").exists() and not force:
        raise InitError(f"{d / 'subject.yaml'} exists (use --force to overwrite)")
    seeds = list(seeds or [])
    cats = [c if c.startswith("Category:") else f"Category:{c}" for c in categories or []]
    words = [w for w in _slug(title).split("-") if len(w) > 3 and w not in ("does", "work", "works", "what")]
    text = TEMPLATE.format(slug=slug, title=json.dumps(title, ensure_ascii=False), short=slug.split("-")[0],
                           description=f"{title}, from foundational to advanced, sourced from Wikipedia.",
                           seeds=_flow(seeds), categories=_flow(cats), include=_flow(words[:6]),
                           per_unit=_flow(per_unit))
    d.mkdir(parents=True, exist_ok=True)
    (d / "subject.yaml").write_text(text, encoding="utf-8")
    if not (d / "STATE.md").exists():
        (d / "STATE.md").write_text(STATE.format(title=title, slug=slug), encoding="utf-8")
    log(f"[init] wrote {d / 'subject.yaml'}")
    log(f"  next: edit it, then `coursesmith frame build {slug}`")
    return d
