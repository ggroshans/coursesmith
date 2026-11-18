# Consolidation guide

You turn one chapter's **dossier** into **draft entries** for a coursesmith subject. A subject is a course built
from Wikipedia, ordered from foundational to advanced and read 4–5 entries at a time. The schema is in
`SCHEMA.md`; the design is in `docs/DESIGN.md`.

## Ground rules
- **Every fact comes from dossier sentences, cited by `sent_id`.** Never use your own knowledge as a source. Never
  invent, round or combine numbers into a new value. If an important concept is missing, list it in the gaps file
  (below) instead of writing it.
- Paraphrase; don't copy sentences. Keep facts short and plain.
- Work from the dossier files, never whole pages:
  - a line cut off with "...": `.venv/bin/coursesmith sent <subject> <id>`;
  - context around a sentence: `.venv/bin/coursesmith ctx <subject> "<Page title>" "<phrase>" -n 4`;
  - a phrase across the subject: `.venv/bin/coursesmith search <subject> "<phrase>"`;
  - a page's sections and sentence counts: `.venv/bin/coursesmith sections <subject> "<Page title>"`;
  - one section in full: `.venv/bin/coursesmith page <subject> "<Page title>" --section "<Section>"`.
  The dossier keeps at most 80 sentences per seed page (25 per assigned page), spread across its sections; a line
  `(§ <Section>: N more sentences; ...)` marks each cut and gives the command that prints the rest.
  - **Facts may cite any sentence of any crawled page** by those ids, not only dossier lines.
- Make no network calls. Edit only your own output files.
- **Other passes may run at the same time.** Keep helper scripts and temp files in
  `subjects/<subject>/work/tmp/<chapter key>/`, with the chapter key in each file name. Never share scratch files.

## Input
`subjects/<subject>/work/dossiers/<chapter key>/chunk_NN.md`. Pages are grouped as concept blocks, most important
first:

```
## <Page title> [seed, vital, navbox | also | assigned] importance 9.4 · High · Q123 · in-scope inlinks 12
Suggested prerequisites: lead links: Clay; Soil pH | RefD: Clay mineral (0.21)
Definition: S:<id> | <first lead sentence>
S:<sent_id> | § <section> | <sentence> | links: <articles it links to> | cites: <years> | <flags>
also on: S:<sent_id> | <other page> § <section> | <sentence> | ...
```

- `seed` pages are the chapter's own; `also` pages belong to another chapter but this one draws on them for detail
  (Soil texture's classes, say); `assigned` pages were attached to the chapter by the concept graph.
- Flags: `CITATION NEEDED` and other maintenance tags; `DATED` (a date the history part may use); `CONTESTED`
  (words such as debated or disputed: check whether the sources really disagree).
- `frame.yaml` shows where the chapter sits and its `target` (a guide, not a quota).

## What makes an entry
An entry is one concept, process, classification, method, material, practice, event, person or debate that a
course on the subject should teach. It needs at least one **curriculum test**:
1. its own article, or its own section on a hub page (`"article": "Soil texture#Classification"`);
2. listed in the subject's navbox, index or Vital Articles;
3. rated Top or High importance by the WikiProject;
4. a prerequisite of two or more other entries;
5. mentioned on two or more in-scope pages (count `also on` lines).

**Exclude**, unless they also pass test 1 or 2: individual scientists other than founders (write one summary entry
per founder, with `"founder": true`); journals and societies (one summary entry each); country-specific pages
without global significance; companies; products. If you write such an entry anyway, set `"exclude": true` and say
why in `notes`.

**Granularity.** One canonical article (or section anchor) per concept. A material and its property can be two
entries when the sources treat them separately (Expansive clay, a Material; Shrink–swell capacity, a Concept);
two pages that describe the same thing are one entry. A hub article with real moving parts (a
classification system, a multi-step method) may yield several entries, one per section, each with its own
`article` anchor. Two pages about the same thing are one entry citing both. Draft **every** qualifying entry, not
just the best: selection comes later. **Never pad**: a thin chapter is reported, not filled.

## Output: one JSON object per line
Work **one chunk at a time**. After each chunk, before reading the next:
1. write that chunk's entries to `entries/draft/<chapter key>.partNN.jsonl` (NN = the chunk number);
2. update `entries/draft/<chapter key>.progress.md`: chunks done, titles drafted so far.

Use the progress note to extend an entry you already drafted rather than duplicating it. At the end, if you own the
whole chapter, concatenate the parts into `entries/draft/<chapter key>.jsonl` and delete the part files.

```json
{"title": "Cation exchange capacity", "kind": "Concept", "weight": "Major", "level": "Intermediate",
 "article": "Cation-exchange capacity",
 "definition": {"text": "The amount of positively charged ions a soil can hold on its particle surfaces.",
                "sent_ids": ["ab12cd34ef56"]},
 "facts": [{"text": "Clay particles and humus carry negative surface charges that hold cations.",
            "sent_ids": ["0f1e2d3c4b5a"]}],
 "prerequisites": ["Clay mineral", "Soil pH"], "related": ["Base saturation"],
 "contested": false, "contested_note": null, "conflicts": [], "distinct_from": [],
 "wants_image": false, "notes": null}
```

**Fields**
- `title`: the concept's plain name, 1–6 words ("Cation exchange capacity", "USDA soil texture classes"). The
  writer adds vivid wording later.
- `kind`: exactly one of Concept, Process, Classification, Method, Material, Practice, Event, Person/Institution,
  Debate.
- `weight`: **Landmark** (a concept the whole subject turns on: soil, weathering, cation exchange; about 10% of a
  chapter), **Major** (a core concept of its chapter; about 35%), **Minor** (narrower, but it makes the subject
  feel lived-in; about 55%).
- `level`: **Foundational** (needs nothing beyond everyday words and the Foundations part), **Intermediate**
  (builds on one or two other entries), **Advanced** (needs several entries first, or quantitative detail). Use the
  suggested prerequisites and your judgment.
- `article`: the entry's own Wikipedia article, exactly as the dossier titles it, or `"Page#Section"` (the
  section's own heading, the deepest one for a nested section: `Clay#Agriculture`), or null for a concept with no
  page or section of its own that still passes another curriculum test (mentioned on two or more pages, say).
- `definition`: the concept in one plain sentence, paraphrased from the page's definition line (or another
  sentence that defines it), with its `sent_ids`. It becomes the glossary line, so it must stand alone.
- `facts`: 2–8 for Landmark and Major entries, 1–4 for Minor ones. Each at most 40 words, with its `sent_ids`.
  Cover what it is, how it works, its size or scale, why it matters and what it leads to, as far as the sentences
  say. Numbers keep their units and their exact values.
- `prerequisites`: 0–5 titles (or articles) of other entries a reader must meet first. Name concepts, not
  examples. The ordering pass refines these.
- `related`: other entries worth a cross-reference that are not prerequisites.
- `events`: optional, for the history part: `[{"date_text": "1883", "sent_ids": ["..."]}]`.
- `contested` / `contested_note`: true when the sources call the matter debated or disputed; the note is one plain
  sentence. A hedge word alone is not a debate.
- `conflicts`: other values the sources give for the **same quantity under the same definition**:
  `{"text": "...", "sent_id": "...", "note": "..."}`. Values that differ because standards differ (USDA, ISO and
  the Unified system put the sand–silt limit in different places) are not conflicts: state them as facts, naming
  each standard. An apparent error in a source (a table with two labels swapped) goes in `notes`, with the
  sentence id, so the verification pass can look at it.
- `distinct_from`: titles of entries that share this entry's article but are genuinely separate (two sections of
  one page). It silences the duplicate warning. Never null an `article` to silence it.
- `wants_image`: true when one picture teaches what words cannot (the texture triangle, a horizon profile). The
  image step only uses freely licensed images.
- `founder`, `exclude`, `notes`: see above.

## Split chapters (when your task names a chunk range)
A long chapter is shared among passes by chunk range. Each pass writes only its own files: one
`entries/draft/<chapter key>.partNN.jsonl` per chunk it processes, and `<chapter key>.progress.partNN.md` and
`<chapter key>.gaps.partNN.md` with NN = its first chunk. Check part files with `finalize --check`. Once every pass is
done, `coursesmith finalize <subject> <chapter key> --merge` joins them into `<chapter key>.jsonl` and folds an entry
drafted twice (same title, or same whole-page article) into one, so an entry that straddles two ranges is fine to
draft twice. The full `finalize` runs after the merge.

## Gaps
Write `entries/draft/<chapter key>.gaps.md` (`.gaps.partNN.md` in a split chapter): important concepts of this chapter you expected but found no
sentences for, one line each with a suggested Wikipedia page title. It drives gap-fill crawls; name things only.

## Checking and finishing
1. Check each part file: `.venv/bin/coursesmith finalize <subject> --check entries/draft/<key>.partNN.jsonl`.
2. When the chapter is merged: `.venv/bin/coursesmith finalize <subject> <chapter key>` until it reports 0 problems.
   Typical problems: an unknown `sent_id` (conflict sentence ids are checked too), a bad kind/weight/level, too
   many or too few facts, an `article` that was not crawled.
3. Read `reports/duplicates.md`: merge each real duplicate, or list the pair in `distinct_from`. Section entries of
   one page always share its article, so give them `distinct_from` each other.
4. Reply in at most 200 words: entries by kind, weight and level; contested and conflict counts; gaps listed;
   anything odd about the dossier.
