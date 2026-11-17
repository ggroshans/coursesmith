# Design

How wikicourse turns a subject into a course, and why. The pipeline and commands are in `README.md`, every file
in `SCHEMA.md`, discovery (covering a whole subject) in `docs/DISCOVERY_DESIGN.md`. The engine grew out of the
Deep Time Chronicle, an earlier Wikipedia-sourced history of Earth; "the chronicle" below means that project.

## 1. Entry schema

```json
{"id": "soil-chem-014", "title": "Cation exchange capacity",
 "kind": "Concept", "weight": "Major", "level": "Intermediate",
 "part": "Soil chemistry", "chapter": "Charge and nutrient holding",
 "article": "Cation-exchange capacity",
 "definition": {"text": "...", "sent_ids": ["..."]},
 "facts": [{"text": "...", "sent_ids": ["..."]}],
 "prerequisites": ["soil-phys-003", "soil-chem-006"],
 "related": ["soil-fert-002"],
 "sources": [{"title": "...", "url": "...", "revid": 0, "sent_ids": ["..."]}],
 "events": [{"date_text": "1975", "date_ma": null, "sent_ids": ["..."]}],
 "contested": false, "conflicts": [], "flags": [],
 "score": 0, "selected": true, "unit": 118, "position": 3,
 "verification": [], "external": [], "source_tier": "wikipedia"}
```

Rendered form (illustrative; the facts here are not sourced and must not be reused):

```
- **Cation exchange capacity** — **Why clay and humus hold the nutrients plants need**

  Clay particles and humus carry negative charges on their surfaces. Those charges hold
  positively charged nutrients, cations such as calcium, magnesium and potassium, and
  release them into soil water as plants take them up. The total a soil can hold is its
  cation exchange capacity. Sandy soils have little; clay-rich and organic soils have a lot,
  which is one reason they stay fertile longer.

  `Soil chemistry · Intermediate · Concept · Major` · `Builds on: Clay minerals (Unit 41); Soil pH (Unit 58)` ·
  `Sources: Cation-exchange capacity; Soil; Clay minerals` · `+ USDA NRCS`
  <!-- soil-chem-014 -->
```

- **id:** `<subject>-<chapter slug>-<nnn>`, assigned at consolidation and **never changed after `order lock`**, even if the entry later moves chapters; the `part`/`chapter` fields carry the truth, the id is just a stable handle. Prose, prerequisites and `glossary.json` all refer to ids.
- **kind:** Concept, Process, Classification, Method, Material, Practice, Event, Person/Institution, Debate.
- **weight:** Landmark / Major / Minor, roughly 10 / 35 / 55 % as in the Deep Time Chronicle. Minor entries make a subject feel lived-in.
- **level:** Foundational / Intermediate / Advanced, from the graph plus the consolidation pass's judgment.
- **Curriculum test** (an entry needs one): its own article, or its own section on a hub page; listed in the navbox, index or Vital Articles; rated Top or High importance; prerequisite of two or more selected entries; mentioned on two or more in-scope pages.
- **Exclude** unless they also pass the first test: individual scientists other than founders (one summary entry per founder), journals and societies (one summary entry each), country-specific pages without global significance, companies, products.
- "Never pad" holds: if a subject supports fewer good entries than expected, the fix is a wider frame, not thinner entries.


## 2. Deep verification (every subject)

Verification aims at two things: context from drilling Wikipedia's own hierarchy, and verification or added context from verified external sources. The rule stays: no fact from general knowledge.

**Tier A — Wikipedia, in depth.** Follow every link in an entry's lead and its own article's sections (depth 1 from the entry), so each dossier carries the context Wikipedia itself provides. These are facts with sent_ids as now.

**Tier B — cited works.** For every entry, resolve the DOIs behind its facts' footnotes through OpenAlex (Crossref fallback), read title and abstract only, and compare: `supports / refines / contradicts / no comparable claim`. Already built in `extsrc.py` and `verify.py`. Extend to numbers and classifications, not just dates.

**Tier C — authorities per subject.** A registry in `subject.yaml` of machine-readable or stable reference sources, each with a fetcher and a comparison rule. For soil science, start with the two classification systems, USDA NRCS Soil Taxonomy (orders, suborders, definitions) and the FAO World Reference Base for Soil Resources, plus the USDA soil survey glossary; add ISRIC SoilGrids for numbers once the classification checks work. Each fetcher is real work, so add authorities one at a time and only where entries actually make checkable claims. An entry whose key claim an authority confirms becomes `source_tier: primary`.

**Tier D — added context.** Where an authority or abstract carries a fact Wikipedia lacks and the entry needs it, the fact may be added, cited to that source (`external: [{source, url, retrieved, text}]`) and marked in the tag line as `+ USDA NRCS`. Authorities and peer-reviewed abstracts only; no blogs, no textbooks unless open-access and citable by URL.

Verification scope is every selected entry plus every flagged one. Every `contradicts` with no supporting source is read by a human and resolved in `verify/reviews.json`, re-applied on each run, as in the chronicle. Genuine conflicts are mentioned in the prose in one plain sentence.


## 3. Ordering: foundational to advanced

No existing tool does this (checked 2026-11-14: Wikipedia's Book namespace was deleted in 2021; wikipedia2book, wiki2book and wikipedia-to-epub take hand-made lists; WikiToLearn and Metacademy are dead). Build it from three signals:

1. **Hierarchy** from `frame.yaml`: parts and chapters. For soil science the navbox `Template:Soil science topics` (203 articles in 8 groups) suggests: Foundations → Soil formation and the pedosphere → Soil physics → Soil chemistry → Soil biology → Classification and taxonomy → Fertility and plant nutrition → Water, erosion and landscape → Agriculture and management → Environmental soil science and climate → History, people and frontiers.
2. **Prerequisites** between entries:
   - RefD (Liang et al., EMNLP 2015, https://aclanthology.org/D15-1193/): represent each concept by the articles it links to; B is a prerequisite of A when A's neighborhood references B more than B's references A. Unsupervised, cheap, ~60–75 % accurate on benchmarks. Threshold θ ≈ 0.05.
   - Lead-link rule: articles linked from an entry's lead section are its prerequisites.
   - An LLM pass (`ORDERING_GUIDE.md`) that reads each entry's definition and names 3–5 prerequisites from the entry list, with a one-line reason.
   - Cycles broken by importance; prerequisites must land in an earlier unit.
3. **Importance and difficulty** as tie-breakers: WikiProject importance, in-scope inlinks, pageviews (`wikimedia.org/api/rest_v1/metrics/pageviews/per-article/...`), Vital level; lexical complexity of the lead; depth in the frame.

Order = for each part in frame order, topological sort of its entries by prerequisites, ties by importance descending then difficulty ascending. Two structural moves a textbook makes: a **Foundations** part holding the ~5 % of concepts most branches depend on (for soil: soil, mineral, weathering, clay, pH, organic matter, soil horizon, texture), and a **History and frontiers** part closing the course with the dated events and live debates. Chronological ordering (`dates.py`, boundary handling) is the second strategy, for earth history.

Expect the automatic order to be a draft. The `curriculum.md` review is where it becomes a course; budget an afternoon per subject.

Evaluation datasets if the prerequisite scorer needs tuning: AL-CPL (https://github.com/harrylclc/AL-CPL-dataset), LectureBank (https://github.com/Yale-LILY/LectureBank). A recent LLM-plus-graph method to borrow from: LECDPR, IJCAI 2026 (https://github.com/lecdpr/LECDPR).


## 4. Voice

The writing rules (`guides/WRITING_GUIDE.md`): facts only from the packet, no new numbers, plain definitions on first use, contested items read as contested, banned phrases, 12–22-word sentences with subject and verb up front, American spelling, metric units.

**Write like the best modern nonfiction authors.** The models are Bill Bryson, Yuval Noah Harari, Malcolm Gladwell and Erik Larson. What they have in common, and what every entry should do:

- **Open with a hook, not a definition.** A striking number, a consequence, a small concrete scene, a question the entry answers. The definition comes in sentence two or three, in plain words.
- **One idea per sentence, and the reader never rereads.** A sentence can be grammatically correct and still wrong for this project. If the subject and verb are not in the first few words, rewrite it. No stacked clauses, no nested parentheses, no noun strings.
- **Make scale felt** with the facts' own sizes, speeds and temperatures, and with comparisons that are obviously true ("a teaspoon of soil holds more organisms than there are people on Earth" only if a sourced sentence says so).
- **Show cause and effect.** History and science are chains; connect each entry to what it builds on and what it leads to, using the "builds on" entries when the facts support the link.
- **Surprise where the facts allow.** The counterintuitive fact, the overlooked connection, the thing the reader assumed wrong. Never manufacture surprise; find it in the sources.
- **People when the sources have them.** Who noticed this first, what they were trying to do, what went wrong. Names and years from the packet only.
- **Vary the rhythm.** Most sentences 12–22 words; an occasional five-word punch. Vary openings across entries: the actor, the place, the consequence, the number.
- **Confident and warm, never breathless.** No exclamation marks, no rhetorical stacking, no "imagine" more than once per edition. Honest about uncertainty in plain language.
- **What the models do that this project cannot:** invent an anecdote, import a fact from memory, speculate about motives. Every colorful detail must sit in the packet. When the facts are plain, write plainly and briefly rather than decorate.

**Length: explain fully, then stop.** The chronicle's entries averaged 56 words (2–4 sentences for Landmark and Major, 1–2 for Minor). For new subjects that is a floor, not a cap. An entry runs as long as a clear explanation needs: typically 60–150 words, up to ~250 when a concept has real moving parts (a classification system, a multi-step process, a debate with two sides). Never cut a necessary step to hit a count, and never pad to reach one. A plain fact still gets a plain two-sentence entry. Units stay at 4–5 entries regardless (`targets.per_unit`), so an edition may run 400–1,200 words.

`write check` should flag: entries over 300 words (review, not reject), sentences over 28 words, any number not in the entry's facts, banned phrases, a definition missing on a term's first use in the part, and more than one "imagine"/"picture" per edition.


## 5. What Wikipedia offers for mapping a subject (verified 2026-11-14, soil science)

- No `Outline of soil science`, `Glossary of soil science` or `Portal:Soil` exists. Nearest: `Outline of Earth science`, `Outline of agriculture`, `Glossary of geology`. Do not assume an outline page for any subject; `frame build` must work without one.
- `Index of soil-related articles`: 332 links, alphabetical, flat.
- `Template:Soil science topics`: 203 article links in 8 groups, transcluded by 103 articles (`list=embeddedin&einamespace=0`). The best free hierarchy; check every subject for its navbox templates (`prop=templates` on the main article).
- WikiProject Soil assessments (`User:WP_1.0_bot/Tables/Project/Soil`): Top 29 / High 67 / Mid 262 / Low 759 / NA 241 / unknown 158 = 1,516 articles. Quality: GA 4, B 96, C 230, Start 595, Stub 292. Expect many stubs: the frame must lean on the B/C/Top/High core.
- `Category:Soil science`: 19 subcategories, 111 direct pages, ~1,190 pages at depth 1. Drift starts at depth 2 (Fictional characters with earth or stone abilities, Sample return missions, Geophagia) and dominates by depth 3 (Hourglasses, Sandboarding, Fort Curtis, Superfund sites, Fertilizer companies). Use depth 1, filter depth 2, never depth 3.
- `prop=pageassessments&redirects=1` returns every WikiProject's quality and importance for a title. `prop=pageprops&ppprop=wikibase_item` gives the Wikidata QID. `page/related` is gone (403, absent from the spec); use `list=search&srsearch=morelike:<Title>`.
- Vital Articles: `Wikipedia:Vital articles/Level 4/Physical sciences` has 10 soil entries under "Pedology"; `.../Level 5/Physical sciences/Earth science` has 34 under "Soil science". Parse with `action=parse&prop=links`.
- Wikidata is good at the discipline level (Soil science Q9161265: P527 has-part pedology; 20 items P279 subclass of soil science; Soil Q36133: P2579 studied-by soil science, soil chemistry, soil physics) and noisy at leaf concepts (CEC Q898477 subclass of "capacity of a set"). Use it for the frame's top two levels only.


## 6. Cost and scale reference (from the chronicle)

- 2,288 pages crawled; ~202,000 sentences indexed; 2,057 events consolidated; 1,672 selected (working tree).
- Consolidation input: ~8.3 MB of dossiers (~2 million tokens read across passes). Writing: ~1.0 MB packets in, ~1.0 MB prose out.
- `raw/` 398 MB, `text/` 32 MB, `cache/` 102 MB, `.git` 34 MB.
- Soil science at depth 1–2 is ~1,200–2,000 pages: the same order of magnitude. Crawl at 0.5 req/s: 1–2 hours.
