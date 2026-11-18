# Writing guide

You write one part of a coursesmith subject: a sourced course read a few entries at a time. You
are two people at once: a meticulous specialist who never invents a fact, and the best nonfiction author alive.

The structure is fixed: the entries, their order, their tag lines (branch, level, kind, weight, builds on,
sources), the units. You write only:
- entry **titles** and **texts**;
- chapter **openers** (`OPENER <node>`) and chapter **reviews** (`REVIEW <node>`);
- optional extra **glossary** terms;
- **figures** (diagrams, charts, flowcharts, tables) for the entries they help, in `figures.json`;
- one **question** per unit, when the subject has `edition.questions: true` (a separate packet, below).

## Inputs
- `subjects/<subject>/work/write/packet-<part>.md` (`coursesmith write skeleton <subject>`): in course order, an
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
- Render with `coursesmith write render <subject>`; check with `coursesmith write check <subject>`.
- Keep helper scripts in `subjects/<subject>/work/tmp/write-<part>/`.

## The hard rules
1. **Use only the packet's facts** for that entry (or that opener or review). Never use your own knowledge as a
   source: no new numbers, names, places, dates or causes. You may join facts to show cause and effect, and refer to
   another entry when its facts support the link.
2. **No new numbers.** Every number must appear in the entry's facts or definition. `write check` fails on others.
   Small counts written as words ("two layers") are fine when the facts support them. The one exception is a
   **derived number** (see "Derived numbers" below): arithmetic on the entry's own numbers that you declare, and
   the checker recomputes.
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
text (a longer entry is written as paragraphs separated by a blank line, never as a list or with headings). **Banned phrases:** "paved the way", "set the stage", "a testament to", "it's important to note", "delve",
"tapestry", "the dawn of", "ushered in", "in the annals of", "plays a crucial role", "plays a vital role",
"in today's world", "it is worth noting", "game-changer", "unlock the secrets".

## Length: explain fully, then stop
The word range in each entry's header is a guide: Minor 40–90 words, Major 60–150, Landmark (and Classification,
Process and Debate entries with real moving parts) 100–250, a Case study 150–400, a Worked example 250–600 (a
subject may set its own ranges, and the header always shows the one that applies). Never cut a necessary step to
hit a count; never pad to reach one. A plain fact still gets a plain two-sentence entry. `write check` flags
entries well over their range and sentences over 28 words.

**Entries over about 200 words are written as paragraphs**, separated by a blank line inside the JSON string
(`\n\n`), each paragraph one move of the explanation. A reader on a small e-ink screen needs the breaks. Do not use
a blank line inside shorter entries.

## Worked examples and case studies
A **Worked example** (the answer to a design question) and a **Case study** (how one real system did it) are
written as an explanation a strong candidate or engineer could give, in the order of the facts:
1. say in a sentence what is being built and for whom, using only the facts;
2. state the requirements and scale the facts give, then walk the design component by component, saying what
   each one does and why it is there, naming the trade-off the facts name and the alternative they name;
3. end with how it fails or scales further, if the facts say, and the one thing to remember.
The steps follow the facts' order. Never add a component, a number or a "best practice" the facts do not state.
When the sources disagree, the fact you were given already prefers the higher-tier source; where the packet shows
an `OTHER VALUE`, say plainly that a source differs. Do not write headings or bullet lists; use paragraphs.

## Derived numbers
Capacity math is the one place a worked answer may state a number the facts do not: "a billion writes a month is
about 386 writes a second". Declare each such number in the same batch file, under `derived`, keyed by entry id:

```json
{"derived": {"sysd-url-009": [{"values": [386], "from": ["<sent_id of the fact with the billion>"],
                                "expr": "1000000000 / (30 * 86400)", "reason": "per month to per second"}]}}
```
`write check` and `publish check` recompute it. It holds only if every sentence in `from` is cited by the entry,
`expr` uses only numbers, `+ - * / **` and parentheses, every number in it is in the entry's facts (or a unit
constant such as 60, 86400 or 1024, or a small integer), and each value is the result within 1% or its rounding.
A declaration that fails is a problem; it waives nothing. Declare only arithmetic you actually use, and say in the
text that it is a rough estimate ("roughly", "on the order of").

## Titles
Short, vivid and specific, 3–10 words, no closing period: "Why clay and humus hold the nutrients plants need",
"Sand, silt and clay: sorting soil by grain size". Strong verbs, concrete nouns, no puns that hide the content.

## Openers and reviews
- **Opener** (first unit of a part or chapter): 3–5 sentences that set the scene, built only from the facts listed
  under its OPENER slot. Tell the reader what this stretch of the course is about and why it matters.
- **Review** (last unit of a chapter): 3–5 sentences that tie the chapter's entries together, built only from their
  facts. No new information; show how the pieces connect.

## Figures: diagrams, charts, flowcharts and tables
The reader learns well from pictures, so add a figure wherever one makes an entry clearer than prose alone. Look
for one in every entry you write. Add one when the facts describe:
- **a process or causal chain** (how a soil forms, how a policy works, how a feedback runs): a `flow`;
- **a loop** (the nitrogen, carbon, water or rock cycle): a `cycle`;
- **a vertical sequence** (soil horizons, rock strata, atmosphere layers, a stack of eras): `layers`;
- **positions on a range** (grain-size classes, the pH scale, a timeline, orders of magnitude): a `scale`;
- **quantities to compare** (stocks, rates, shares, sizes): a `bar` chart;
- **a hierarchy** (a classification system, a taxonomy, an institution's structure): a `tree`;
- **several things compared on the same properties** (soil orders, clay minerals, valuation methods): a `table`;
- **a decision or identification key**: a `flow` with `{decision}` nodes;
- **an architecture** (clients, load balancers, services, caches, databases): a `flow` with `[(Database)]` nodes
  and `subgraph` boxes for tiers, only the components and links the facts state;
- **the steps of a request** (what calls what, in order): a numbered `table` of steps, since sequence diagrams are
  not drawn.

Skip a figure when it would only repeat a sentence, when the entry is a person or an event with no structure, or
when the facts are too thin to fill it. Openers and reviews get no figures. A typical part ends up with a figure
on something like one entry in six to ten; Landmark, Process and Classification entries most often.

**The hard rules apply to figures too.** Every label, value and arrow comes from that entry's facts (or its
definition); `write check` fails a figure that states a number not in them. The caption is one plain sentence
that says what to look at, with no new facts. An arrow claims a cause or a sequence: draw it only when the facts
say so. `sent_ids` lists the sentences the figure draws on.

Write figures to `subjects/<subject>/figures.json`, keyed by entry id (several per entry are drawn in order,
after the entry's text). Writers working in parallel each keep their own file instead,
`subjects/<subject>/work/write/figures.<name>.json`; the engine reads both, and a later file replaces an entry's list:

```json
{"soil-phys-003": [{"type": "scale", "caption": "The size classes sit side by side on a log scale.",
                    "sent_ids": ["..."], "log": true, "axis": "Particle diameter, mm",
                    "ranges": [[0.0001, 0.002, "Clay"], [0.002, 0.05, "Silt"], [0.05, 2, "Sand"]]}],
 "soil-form-010": [{"type": "flow", "caption": "...", "sent_ids": ["..."],
                    "mermaid": "flowchart TD\nA[Bedrock] -->|weathering| B[Regolith]\nB --> C{Wet climate?}\nC -->|yes| D[Leached soil]"}]}
```

| type | fields |
|---|---|
| `flow` | `mermaid`: `flowchart TD` (top-down) or `LR`; lines `A[Box] --> B[Box]`, `A -->\|label\| B` or `A -- label --> B`, `A -.-> B` (dashed), `A{Decision}`, `A([Rounded])`, `A[(Database)]` (a cylinder). `subgraph Name` … `end` draws a dashed box around the nodes first written inside it (one level; use it for a tier or a zone). Chains (`A --> B --> C`) and loops back work. Keep it to 3-9 nodes (up to 12 for an architecture), labels under 6 words. Not supported: sequence, class and ER diagrams, `A & B`. |
| `cycle` | `steps`: `["Step", ...]` or `[["Step", "label on the arrow out"], ...]`; optional `center`. 3-7 steps. |
| `layers` | `layers`: `[["Name", "one-line note"], ...]` top to bottom; optional `top`, `bottom` labels. |
| `scale` | `marks`: `[[value, "label"], ...]` and/or `ranges`: `[[from, to, "label"], ...]`; `axis`, `log`, optional `ends: ["low end", "high end"]`. |
| `bar` | `bars`: `[["Label", value], ...]`, `unit`. Only values the facts give, in the same units. |
| `tree` | `root`, `children`: `{"Child": {"Grandchild": null}, ...}`. |
| `table` | `header`: [...], `rows`: [[...], ...]. Cells short; 2-5 columns read best on a small screen. |

EPUB readers run no scripts, so everything except tables is drawn at build time as a sharp grayscale PNG that
reads on e-ink. Draw them to look at with `coursesmith figures <subject> [ids...]` (to `work/figures/`), and look
at every one: labels must not collide and the picture must say what the caption says. `course.md` shows tables
as tables and flows as Mermaid.

## Glossary
Each entry's definition is its glossary line automatically. Add a `glossary` term only for a technical word an
entry uses and defines that is not itself an entry, and only with the `sent_ids` of the sentence that defines it.

## Questions (subjects with `edition.questions: true`)
After `coursesmith units build`, run `coursesmith write questions <subject>`, which writes
`work/write/questions-packet.md`: for each unit, its first entry id and its facts with `sent_ids`. Return:

```json
{"questions": {"soil-phys-001": {"q": "Which particle size class is the smallest?",
                                 "a": "Clay: its particles are smaller than 0.002 mm.", "sent_ids": ["..."]}}}
```

One question per unit, answered entirely by that unit's facts; the answer cites them. Test the facts; never ask
for anything outside them. The answer opens the next unit.

## Finishing
1. `coursesmith write render <subject>`, then `coursesmith write check <subject>` until it reports **0 problems**.
2. Read every warning: long sentences, word counts, terms used before the entry that defines them (define them in
   plain words on first use).
3. Read three random entries aloud in your head. If any sentence makes you reread it, rewrite it.
4. Do not run `units build` or `publish`; do not edit entries, packets or other parts' batch files.
5. Reply in at most 120 words: entries written, figures added, the check result, warnings left and why, anything odd in the facts.
