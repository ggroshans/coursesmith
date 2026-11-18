# Consolidation guide

You turn one chapter's **dossier** into **draft entries** for a coursesmith subject. A subject is a course built
from Wikipedia and, when `subject.yaml` lists them, other vetted sources (a repository, a standard, a docs site,
a paper), ordered from foundational to advanced and read 4–5 entries at a time. The schema is in
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
## gh>owner/repo/README.md [seed] "URL shortener (repo)" importance 4.0 · repo · curated · commit ae9bbd7 · CC BY 4.0 · in-scope inlinks 3
Suggested prerequisites: lead links: Clay; Soil pH | RefD: Clay mineral (0.21)
Definition: S:<id> | <first lead sentence>
S:<sent_id> | § <section> | <sentence> | links: <articles it links to> | cites: <years> | <flags>
also on: S:<sent_id> | <other page> § <section> | <sentence> | ...
```

- `seed` pages are the chapter's own; `also` pages belong to another chapter but this one draws on them for detail
  (Soil texture's classes, say); `assigned` pages were attached to the chapter by the concept graph.
- The first header is a Wikipedia article (its title). The second is a page of another source: its **key**
  (`gh>…` a repository file, `rfc>…` an RFC, `doc>…` a docs page, `pdf>…`, `paper>…`), the human name in quotes,
  then its source, **trust tier**, version (a commit, a publication date, a snapshot hash) and license. Use the key
  exactly as written when you cite a page in `article`.
- A chunk that opens with `QUESTION: …` belongs to a chapter that answers one question. See "Question chapters".
- Flags: `CITATION NEEDED` and other maintenance tags; `DATED` (a date the history part may use); `CONTESTED`
  (words such as debated or disputed: check whether the sources really disagree).
- `frame.yaml` shows where the chapter sits and its `target` (a guide, not a quota).

## What makes an entry
An entry is one concept, process, classification, method, material, practice, event, person or debate that a
course on the subject should teach. It needs at least one **curriculum test**:
1. its own article, or its own section on a hub page (`"article": "Soil texture#Classification"`);
2. listed in the subject's navbox, index or Vital Articles (Wikipedia subjects);
3. rated Top or High importance by the WikiProject (Wikipedia subjects);
4. a prerequisite of two or more other entries;
5. mentioned on two or more in-scope pages (count `also on` lines);
6. taught by an `official`, `standard` or `primary` source (a page whose header says so): a vendor's or standard's
   own page is a reason to include the concept;
7. the entry is the worked answer of a question chapter (kind Worked example).

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
  Debate, Worked example, Case study. Worked example and Case study are for question chapters (below); every other
  kind is as before.
- `weight`: **Landmark** (a concept the whole subject turns on: soil, weathering, cation exchange; about 10% of a
  chapter), **Major** (a core concept of its chapter; about 35%), **Minor** (narrower, but it makes the subject
  feel lived-in; about 55%).
- `level`: **Foundational** (needs nothing beyond everyday words and the Foundations part), **Intermediate**
  (builds on one or two other entries), **Advanced** (needs several entries first, or quantitative detail). Use the
  suggested prerequisites and your judgment.
- `article`: the entry's own page, exactly as the dossier titles it (a Wikipedia article title, or another source's
  key such as `gh>owner/repo/README.md`), or `"Page#Section"` (the section's own heading, the deepest one for a
  nested section: `Clay#Agriculture`), or null for a concept with no page or section of its own that still passes
  another curriculum test (mentioned on two or more pages, say).
- `definition`: the concept in one plain sentence, paraphrased from the page's definition line (or another
  sentence that defines it), with its `sent_ids`. It becomes the glossary line, so it must stand alone.
- `facts`: 2–8 for Landmark and Major entries, 1–4 for Minor ones (a Worked example takes up to 16, a Case study
  up to 12; the packet's `subject.yaml` may change these caps). Each at most 40 words, with its `sent_ids`.
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

## When sources disagree
Pages in a dossier can come from sources of different trust. Tiers, best first: **official** (a vendor's or
project's own documentation), **standard** (an RFC or other standard), **primary** (a paper by the people who did
the work), **reference** (Wikipedia and other encyclopedias), **curated** (a community list or guide),
**commentary** (a named author's essays and blogs).
- When two sentences give different values for the **same** quantity or claim under the same definition, the fact
  you write is the **higher-tier** one. Put the other value in `conflicts` with its `sent_id`, as above. Never
  average, never pick the middle, never split the difference.
- A lower tier may win only when the higher one is older (`cites:` years, a version or date in the header or
  sentence) and the entry says so in a fact: "Version 7 raised the default to 100 MB; earlier versions allowed 50 MB."
  A difference between versions is not a conflict; state each with its version.
- When sources differ because they define the term differently (an RFC's "idempotent" and a blog's), they are not
  in conflict: state each, naming the source.
- Never raise a claim's standing by citing a better source for a different claim. A fact cites the sentences that
  say it.
- A `curated` or `commentary` source that is the only one for a claim is still usable; mention the source's name
  in the fact when the claim is its author's opinion ("The primer recommends …").

## Question chapters
A chapter flagged as a question (the dossier opens with `QUESTION: …`) is one interview-style question, such as
"Design a URL shortener". Write:
- the **concept entries** a strong answer relies on (hash functions, a key-value store, caching), each from its
  own pages, exactly as in any chapter; and
- **exactly one entry of kind Worked example** titled for the question ("Designing a URL shortener"): the answer
  itself, built only from dossier sentences, with `article` set to the page that works the problem. Its facts are
  the steps and the numbers of the answer in the order a good answer gives them: requirements, estimates, the
  data model, the components, the trade-offs, the failure cases. Up to 16 facts, each citing its sentences, with
  `prerequisites` naming the concept entries it uses.
A back-of-the-envelope figure that the sources do not state but that follows from numbers they do (writes per
second from writes per day) is not a fact: do not write it. The writing pass may derive it under a recorded
waiver; your job is to cite the inputs.

## Split chapters (when your task names a chunk range)
A long chapter is shared among passes by chunk range. Each pass writes only its own files: one
`entries/draft/<chapter key>.partNN.jsonl` per chunk it processes, and `<chapter key>.progress.partNN.md` and
`<chapter key>.gaps.partNN.md` with NN = its first chunk. Check part files with `finalize --check`. Once every pass is
done, `coursesmith finalize <subject> <chapter key> --merge` joins them into `<chapter key>.jsonl` and folds an entry
drafted twice (same title, or same whole-page article) into one, so an entry that straddles two ranges is fine to
draft twice. The full `finalize` runs after the merge.

## Gaps
Write `entries/draft/<chapter key>.gaps.md` (`.gaps.partNN.md` in a split chapter): important concepts of this chapter you expected but found no
sentences for, one line each with a suggested page title or source key. It drives gap-fill crawls; name things only.

Two more things feed `coursesmith report gaps` and the gap-fill round that follows (`GAPFILL_GUIDE.md`), so keep to
their conventions:
- **An entry the sources only half support** (a worked answer that is a diagram caption, a checklist that names points and
  explains none) still gets written from the sentences it has, never padded. Start its `notes` with `thin:` and say what
  is missing (`"thin: no estimates, data model or API"`), and name the pages that would fill it in the gaps file.
- **A prerequisite or related title** should be an entry that exists or a concept the course ought to have, written as
  its usual name ("Hash function"). One that has no entry is listed as an unresolved name; do not stretch a title to an
  entry that is about something else just to resolve it.

## Checking and finishing
1. Check each part file: `.venv/bin/coursesmith finalize <subject> --check entries/draft/<key>.partNN.jsonl`.
2. When the chapter is merged: `.venv/bin/coursesmith finalize <subject> <chapter key>` until it reports 0 problems.
   Typical problems: an unknown `sent_id` (conflict sentence ids are checked too), a bad kind/weight/level, too
   many or too few facts, an `article` that was not crawled.
3. Read `reports/duplicates.md`: merge each real duplicate, or list the pair in `distinct_from`. Section entries of
   one page always share its article, so give them `distinct_from` each other.
4. Reply in at most 200 words: entries by kind, weight and level; contested and conflict counts; gaps listed;
   anything odd about the dossier.
