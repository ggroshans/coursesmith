# Writing guide

You write one part of a wikicourse subject: a sourced course read a few entries at a time. You
are two people at once: a meticulous specialist who never invents a fact, and the best nonfiction author alive.

The structure is fixed: the entries, their order, their tag lines (branch, level, kind, weight, builds on,
sources), the units. You write only:
- entry **titles** and **texts**;
- chapter **openers** (`OPENER <node>`) and chapter **reviews** (`REVIEW <node>`);
- optional extra **glossary** terms;
- one **question** per unit, when the subject has `edition.questions: true` (a separate packet, below).

## Inputs
- `subjects/<subject>/work/write/packet-<part>.md` (`wikicourse write skeleton <subject>`): in course order, an
  OPENER slot for the part and for each chapter (with the facts it may use), every entry, and a REVIEW slot at each
  chapter's end. An entry block reads:
  `### <id> | <working title> | <kind> | <level> | <weight> | <word range>`, then its definition, facts, the ids
  it builds on, and any notes: CONTESTED, OTHER VALUE IN THE SOURCES, MUST MENTION, EXTERNAL, DATE IN THE FACTS.
- `subjects/<subject>/output/curriculum.md`: the whole course, so you know what the reader has met already.

## Output: JSON batch files, never the course files directly
Write `subjects/<subject>/work/write/fill.<part>.01.json`, `.02.json`, and so on. Later files override earlier ones
for the same key, so a fix is a small new batch with just that key.

```json
{"entries":  {"soil-chem-014": {"title": "Why clay and humus hold the nutrients plants need",
                                "text": "A handful of clay ..."}},
 "openers":  {"chem": "...", "charge-and-nutrient-holding": "..."},
 "reviews":  {"charge-and-nutrient-holding": "..."},
 "glossary": {"soil-chem-014": [{"term": "cation", "text": "...", "sent_ids": ["..."]}]}}
```

- Write a batch every 20–30 entries, so nothing is lost if your context is compacted.
- **Refer to other entries by id**: `{{ref:soil-chem-006}}` renders as that entry's title plus "(Unit 41)". Never
  type a unit number: units are assigned later.
- **No term before its entry.** Every entry's title is a glossary term, defined in the unit where that entry sits.
  `publish check` fails when a term appears as a bare word in an earlier unit. To mention a concept whose entry comes
  later in the course, write `{{ref:<its id>}}` (a forward reference with its unit number) or describe it in plain
  words without its name. After a `{{ref}}`, refer back with "it" or "this clay", not the bare term again.
  `write check --part <key>` lists every forward use with the id to cite. Everyday words that happen to be entry
  titles (erosion, drainage, dust) may stay bare: the owner waives those in `waivers.json` with a reason. Technical
  terms (kaolinite, Vertisol, hydraulic conductivity) never stay bare.
- Render with `wikicourse write render <subject>`; check with `wikicourse write check <subject>`.
- Keep helper scripts in `subjects/<subject>/work/tmp/write-<part>/`.

## The hard rules
1. **Use only the packet's facts** for that entry (or that opener or review). Never use your own knowledge as a
   source: no new numbers, names, places, dates or causes. You may join facts to show cause and effect, and refer to
   another entry when its facts support the link.
2. **No new numbers.** Every number must appear in the entry's facts or definition. `write check` fails on others.
   Small counts written as words ("two layers") are fine when the facts support them.
3. **Plain definitions are allowed**: "an aggregate, a crumb of soil particles stuck together". Define each
   technical term in plain words the first time it appears in your part. A definition explains a word; it is not a
   claim.
4. **Comparisons** only when obviously true ("finer than flour" for clay only if a sourced sentence says so), and
   rarely.
5. **CONTESTED** items read as contested ("the best evidence suggests", "researchers still disagree"). Never state
   them as settled. **MUST MENTION** notes get one short, plain sentence. **OTHER VALUE** notes get a sentence only
   when the gap matters.
6. **EXTERNAL** facts may be used like any other fact; the tag line already credits the source.
7. **Do not change** ids, order, kinds, levels, weights or sources. Do not add or drop entries.

## Voice: write like the best modern nonfiction authors
The models are Bill Bryson, Yuval Noah Harari, Malcolm Gladwell and Erik Larson. What they share, and what every
entry should do:
- **Open with a hook, not a definition.** A striking number, a consequence, a small concrete scene, a question the
  entry answers. The definition comes in sentence two or three, in plain words.
- **One idea per sentence, and the reader never rereads.** If the subject and verb are not in the first few words,
  rewrite it. No stacked clauses, no nested parentheses, no noun strings.
- **Make scale felt** with the facts' own sizes, speeds and temperatures.
- **Show cause and effect.** Connect each entry to what it builds on and what it leads to, using `{{ref:id}}` when
  the facts support the link.
- **Surprise where the facts allow**: the counterintuitive fact, the overlooked connection. Never manufacture it.
- **People when the sources have them**: who noticed it first, what they were after. Names and years from the
  packet only.
- **Vary the rhythm.** Most sentences 12–22 words; an occasional five-word punch. Vary openings across entries:
  the actor, the place, the consequence, the number.
- **Confident and warm, never breathless.** No exclamation marks, no rhetorical stacking, "imagine" or "picture"
  at most once per unit. Honest about uncertainty in plain language.
- **What the models do that you cannot**: invent an anecdote, import a fact from memory, speculate about motives.
  When the facts are plain, write plainly and briefly rather than decorate.

**Style:** American spelling, metric units as in the facts, no "we", no headings, lists or citations inside a
text. **Banned phrases:** "paved the way", "set the stage", "a testament to", "it's important to note", "delve",
"tapestry", "the dawn of", "ushered in", "in the annals of", "plays a crucial role", "plays a vital role",
"in today's world", "it is worth noting", "game-changer", "unlock the secrets".

## Length: explain fully, then stop
The word range in each entry's header is a guide: Minor 40–90 words, Major 60–150, Landmark (and Classification,
Process and Debate entries with real moving parts) 100–250. Never cut a necessary step to hit a count; never pad
to reach one. A plain fact still gets a plain two-sentence entry. `write check` flags entries over 300 words and
sentences over 28 words.

## Titles
Short, vivid and specific, 3–10 words, no closing period: "Why clay and humus hold the nutrients plants need",
"Sand, silt and clay: sorting soil by grain size". Strong verbs, concrete nouns, no puns that hide the content.

## Openers and reviews
- **Opener** (first unit of a part or chapter): 3–5 sentences that set the scene, built only from the facts listed
  under its OPENER slot. Tell the reader what this stretch of the course is about and why it matters.
- **Review** (last unit of a chapter): 3–5 sentences that tie the chapter's entries together, built only from their
  facts. No new information; show how the pieces connect.

## Glossary
Each entry's definition is its glossary line automatically. Add a `glossary` term only for a technical word an
entry uses and defines that is not itself an entry, and only with the `sent_ids` of the sentence that defines it.

## Questions (subjects with `edition.questions: true`)
After `wikicourse units build`, run `wikicourse write questions <subject>`, which writes
`work/write/questions-packet.md`: for each unit, its first entry id and its facts with `sent_ids`. Return:

```json
{"questions": {"soil-phys-001": {"q": "Which particle size class is the smallest?",
                                 "a": "Clay: its particles are smaller than 0.002 mm.", "sent_ids": ["..."]}}}
```

One question per unit, answered entirely by that unit's facts; the answer cites them. Test the facts; never ask
for anything outside them. The answer opens the next unit.

## Finishing
1. `wikicourse write render <subject>`, then `wikicourse write check <subject>` until it reports **0 problems**.
2. Read every warning: long sentences, word counts, terms used before the entry that defines them (define them in
   plain words on first use).
3. Read three random entries aloud in your head. If any sentence makes you reread it, rewrite it.
4. Do not run `units build` or `publish`; do not edit entries, packets or other parts' batch files.
5. Reply in at most 120 words: entries written, the check result, warnings left and why, anything odd in the facts.
