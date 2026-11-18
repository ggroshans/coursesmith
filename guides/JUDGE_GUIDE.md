# Scope judge guide

You decide which Wikipedia pages belong in a coursesmith subject: a course built from Wikipedia, ordered from
foundational to advanced, meant to cover the whole subject (major and minor material) without the very niche. You
read page metadata, never write course text, and never use a page you have not been shown.

## Input
`subjects/<subject>/work/scope/judge-packet-NN.md`. It opens with the subject, its description and its chapters
(key: title). Then one line per page:

```
<title> | <short description> | cats: <categories> | linked from N entries | lead: <first sentences, if crawled>
```

"linked from N entries" counts the course's entry articles that link to the page: a hint that the course leans on
it, not proof that it belongs.

## Verdicts
- **in**: a course on this subject should teach this page's concept: it is part of the subject, a branch or method
  of it, a process, material, classification, practice or event the subject studies. Include advanced and
  quantitative material (equations, models, methods named for their inventor or technique) when the subject uses
  it: Kriging and Variogram are in for a soil course with a soil mapping chapter; Richards equation is in.
- **support**: a concept from a neighboring field that a reader must understand to follow this course and that a
  good textbook on the subject explains in its own right (a box, a section, a glossary entry): Adsorption,
  Capillary action, Colloid, Darcy's law for soil science. Not general knowledge an adult reader already has.
- **out**: everything else:
  - general knowledge and very broad topics (Water, Iron, Agriculture, Climate, Plant, Earth);
  - chemical elements and compounds, organisms and taxa, unless the page is about their role in the subject
    (Nitrogen fixation is in; Nitrogen is out; Rhizobium can be in for soil biology, a single bacterial species
    is out);
  - places, countries, regions, single sites, single events (one landslide, one superfund site);
  - people other than the subject's founders, organizations, institutes, journals, companies, products, books,
    films, lists, local programs;
  - very niche material: single named soil series, local soil types of one region, single test devices or brand
    methods, one-off national projects;
  - pages whose topic only overlaps the subject by a word (Clay tablet, Desire path).

When unsure between in and out, ask: would a two-semester university course plus a graduate reading list on this
subject mention this concept by name? Yes: in. Only in passing as an example: out.

## Chapter
For **in** and **support**, give the chapter key where the concept fits best (`ch`). If it fits none, write a new
short chapter title as `new: <title>` (a branch the frame is missing: "new: Soil mapping and geostatistics"). Use
new chapters sparingly and consistently: reuse the same title for every page of that branch.

## Output
Write `subjects/<subject>/scope/judge/batch-NN.json` (NN = your packet number), one key per page, every page in
your packet:

```json
{"Kriging": {"v": "in", "ch": "new: Soil mapping and geostatistics", "why": "interpolation method of soil mapping"},
 "Nitrogen": {"v": "out", "why": "chemical element; its soil roles are separate entries"},
 "Capillary action": {"v": "support", "ch": "water-in-soil", "why": "explains water rise in pores"}}
```

`why`: at most 12 words. Write the file every 150 pages so nothing is lost. Make no network calls; edit only your
own batch file. Reply in at most 80 words: counts of in, support and out, and any new chapters you proposed.
