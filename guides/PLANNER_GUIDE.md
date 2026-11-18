# Syllabus planner guide

You plan the full syllabus of a coursesmith subject: every branch, topic and concept a complete course should teach,
from the first idea a beginner needs to the methods and models of advanced study, including minor material but not
the very niche. You name things; you never write course text or facts. Every fact in the course comes later from
sentences of the subject's sources (Wikipedia, plus any other source `subject.yaml` lists), so naming a concept no
source covers costs nothing: the resolver reports it honestly. In a subject whose chapters are questions, name the
concepts a strong answer to each question depends on, not the question itself.

## Input
`subjects/<subject>/work/scope/plan-packet.md`: the subject's description and boundary, the current frame (parts
and chapters) with every entry title already in the course, the gap lists the consolidation passes wrote, and the
new chapters the scope judge proposed.

## What to produce
`subjects/<subject>/scope/syllabus.json`:

```json
{"branches": [{"name": "Soil mapping and geostatistics", "chapter": "new: Soil mapping and geostatistics",
               "why": "pedometrics is a recognized branch; the course has no home for it"}],
 "concepts": [{"name": "Kriging", "branch": "Soil mapping and geostatistics", "level": "Advanced",
               "pages": ["Kriging", "Regression-kriging"], "phrases": ["kriging"]},
              {"name": "Urban soils", "branch": "Human-made and urban soils", "level": "Intermediate",
               "pages": ["Urban soil"], "phrases": ["urban soil", "urban soils"]}]}
```

- **Branches**: the subject's recognized branches and subfields, as the field organizes itself (its scientific
  societies' divisions and commissions, the chapters of standard textbooks, university course sequences). Give each
  the existing chapter key that holds it, or `new: <title>` when the frame has no home for it.
- **Concepts**: everything a complete course on each branch teaches that the course does **not** already have.
  Check the entry titles in the packet first; never list a concept that is already an entry under any name.
  Prioritize: (1) whole branches and subfields missing; (2) core concepts of a branch missing; (3) the advanced end
  of each branch (methods, models, equations, measurement techniques); (4) minor concepts that make a branch feel
  complete. Skip the very niche: single soil series, local soil types, brands, single sites, people other than
  founders, organizations.
- `level`: Foundational, Intermediate or Advanced.
- `pages`: the page titles you expect: Wikipedia article titles (exact where you know them, likely ones otherwise;
  the resolver follows redirects), or keys of another source when the packet lists that source's pages
  (`gh>owner/repo/path.md`, `rfc>9110`). Never invent a key.
- `phrases`: 1–3 short phrases a sentence in the sources would use for the concept, for when no page exists.

Aim for completeness, not a count: a broad subject may need several hundred concepts, a narrow one a few dozen.
Also list each gap-list item from the packet that a complete course needs, under its branch.

Write the file in pieces as you go (rewrite the whole file each time) so nothing is lost. Validate with
`.venv/bin/python -c "import json;d=json.load(open('subjects/<subject>/scope/syllabus.json'));print(len(d['branches']),len(d['concepts']))"`.
No network; edit only that file; do not commit. Reply in at most 120 words: branches added, concepts by level, and
the branches you think are thinnest.
