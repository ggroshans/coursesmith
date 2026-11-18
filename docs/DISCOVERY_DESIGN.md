# Discovery design: covering a whole subject, at any size

(Pages of sources other than Wikipedia are not discovered by hubs and categories: a source's allowlist and the
subject's seeds decide what is in scope; see `docs/DESIGN.md`, section 2b, and `coursesmith sources discover`.)

How the engine finds every page a course on a subject needs, from a broad field (soil science, world history) down
to a niche (mycorrhizal fungi, kriging), and organizes it beginner to advanced. Steps 1–3 of the pipeline (frame,
scope, crawl) change; everything from `dossier` on stays as it is. The sourcing rule is untouched: an LLM may name
pages, branches and structure, never facts. Every fact still comes from a cited Wikipedia sentence.

## What the soil science build showed (2026-11-16)

Measured on the finished course (1,735 entries, 4,278 pages):

- **Hub lists were gathered but not crawled.** The frame step collected 1,711 candidates (navbox, index, Vital, the
  WikiProject table, the category tree) with their metadata, but only the 462 frame seeds were forced into the
  crawl. 823 were never fetched; 209 of those pass the scope threshold on metadata alone (Plant–soil feedback,
  Slickenside, Biogeology, Bound water, Clay cutan, Constructed soil, Nonlimiting water range...).
- **Link-following saturated quickly.** Depth 1 added 393 pages, depth 2 added 111. The frame did the discovery.
  Wikipedia's soil category tree is shallow (Soil physics has no subcategories), so a fixed deeper depth adds little.
- **The borderline band was unreviewable.** `frontier_review.csv` had 18,733 rows; 3,977 rejected titles scored
  just under the threshold. The keyword score drops method pages named for the method, not the subject (Kriging,
  Variogram, Munsell color system all scored 0–1).
- **Some branches have no article.** Urban soil, Soil mineralogy, Soil geography, Soil micromorphology, Soil
  spectroscopy, Soil hydrology, Land evaluation, Paddy soil and Epipedon have no Wikipedia page, but their material
  exists as sentences on pages already crawled (urban soils: 14 sentences; epipedons: 27; spectroscopy: 40).
  Dossiers are built per page, so scattered material is never assembled.
- **Prerequisites are already mostly LLM-judged.** 3,434 of 3,964 prerequisite edges came from the ordering pass.
  Extending LLM judgment upstream to discovery is consistent with the engine, not a new dependency.
- **Levels are the consolidation pass's judgment.** Prerequisite-chain depth does not separate them (nearly every
  entry sits at the end of a 6+ step chain through "Soil"), so levels are not derived from the graph.

## The design

### 1. Crawl every hub candidate
Every page in a hub list (navboxes, index, Vital sections, the WikiProject table, the category tree) that passes
the scope threshold on its metadata is fetched, not only the frame seeds. `coursesmith crawl <subject> --hubs`
queues them; links from them are followed one hop. Cheapest and largest single gain.

### 2. Learned scope score, then an LLM judge on the uncertain band
- **Learned score.** A per-subject classifier (logistic regression on title, description and category tokens)
  trained with the forced frame pages as positives and far-rejected pages (keyword score <= 0) as negatives,
  evaluated on the hand-labeled `scope/calibration.csv`. It replaces the hand-tuned points, needs no per-subject
  term lists, and catches pages that do not carry the subject's words.
- **Judge.** Titles in the uncertain band go to a judge pass (a subagent reading a packet, like consolidation):
  title, description, categories and the first lead sentences in; in/out, branch, kind and a reason out. Verdicts
  are cached by title and revision. The calibration set measures whether judge plus score beats the keyword score
  (soil: F1 0.59, recall 0.91).

### 3. Syllabus plan, resolve, audit: top-down and bottom-up checking each other
- **`frame plan`**: a planner pass writes the subject's tree (branches, subbranches, topics, leaf concepts), each
  with a level and a line on what it covers, from the subject, a boundary statement ("out: agronomy as a whole")
  and how the field organizes itself (its societies' divisions, textbook tables of contents) as names only.
- **`frame resolve`**: every node is mapped to pages or sections through the prescreen (redirects, canonical
  titles), Wikipedia search and section headings. A node with no page but scattered sentences becomes a **phrase
  dossier** (below). A node with neither is recorded as "Wikipedia has no coverage", never written from memory.
- **`frame audit`** (planned, not built; `report coverage` is the closest command today): per branch: entries, levels, unresolved nodes, and in-scope pages no node claims. Unplaced
  pages go back to the planner ("where does this go, or which branch is missing?"). The auditor names pages an
  advanced course in the branch would also cover; they are resolved and crawled. The loop stops when a round adds
  fewer than a handful of pages per branch.

### 4. Phrase dossiers for branches without an article
When a node resolves to no page, its dossier is built from `search` across the crawl (every sentence containing its
phrase and its synonyms), so consolidation can draft `article: null` entries and the planner can open a chapter for
it ("Urban and human-made soils" gathering Technosol, Anthrosol, Soil sealing and the urban-soil sentences).

### 5. Neighbor imports as support entries
A page outside the boundary enters as a **support entry** when it is a prerequisite of two or more in-scope entries
or the planner marks it required background (Variogram for a kriging course; Darcy's law for soil physics). Support
entries are tagged with their home field and open the course or their chapter.

### 6. Adaptive probing instead of fixed depths
Each discovery signal (category level, link hop, backlinks to Landmark entries, `morelike:` search, pages embedding
the subject's navboxes, Wikidata's top two levels) runs another round only while the previous round's accepted pages
exceed a floor. Soil would stop at category depth 2 and link depth 2 on its own; a niche topic keeps going.
Backlinks and `morelike:` are noisy (3 of 17 `morelike:Pedometric mapping` results were relevant), so they only
feed the scorer and the judge.

### 7. One tree for every size
Every syllabus node is a mini-subject with its own seeds and scope. A node resolving to more than ~40 candidate
pages splits; one resolving to fewer than ~3 becomes a leaf. A broad subject gets a 4–5 level tree with shallow
crawls per branch; a niche topic gets a shallow tree whose leaves are sections of a few articles, crawled deep.
Per-branch budgets replace the global depth. `frame estimate` (planned, not built) would report entries, units and the thinnest branches
before the main crawl.

### 8. Levels and the ladder
The auditor checks each chapter for a spine (the 3–5 entries everything else in it builds on) and for entries at
each level, and names pages for a chapter with no Advanced entries. Levels stay the consolidation pass's call,
guided by quotas as weights already are.

## What the first run measured (soil science, 2026-11-16)

- **`crawl --hubs`**: 205 hub-list pages passed the threshold on metadata; with one hop of links, 228 pages. About
  half were niche (single soil series, institutes), which the judge then ruled out.
- **A learned vocabulary score did not help.** A logistic regression on title, description and category words
  (trained on 888 in, 2,783 out) scored F1 0.55 on the calibration set, 0.57 combined with the keyword score,
  against 0.59 for the keyword score alone, and ranked Kriging and Variogram low: their vocabulary is not soil's.
  The calibration labels encode a policy (no soil series, institutes or scientists), which is the judge's job.
  Not shipped.
- **Inlinks from entry articles do not separate either.** The most-linked non-entry pages are generic background
  (Agriculture 128 entries, Nitrogen 118, United States 63).
- **The judge**: 5,923 pages in 10 passes (about two minutes each): 160 in, 191 support, 5,572 out. On the 100
  calibration titles: F1 0.75, precision 0.77, recall 0.73 (keyword score: 0.59, 0.44, 0.91).
- **The planner**: 50 branches (13 new chapters) and 749 concepts. Resolved: 18 already covered, 328 pages,
  112 phrase concepts, 147 pages the judge ruled out (mostly general pages: Quartz, Granite, Biome; ten overridden
  as core pages of a new chapter), 144 with no Wikipedia coverage.
- **Lessons for the passes**: give each parallel pass its own scratch folder (judges sharing one overwrote each
  other's helper files); the judge's "out" is right for general pages a planner names (Quartz, Biome), so the
  planner names topics and the judge picks the page.

## Roles

| Pass | In | Out |
|---|---|---|
| Planner | subject, boundary, depth, field outline names | syllabus tree with levels |
| Resolver | a node + search results and redirects | its pages or sections, a phrase, or "none" |
| Judge | a borderline page's metadata and lead | in/out, branch, kind, reason |
| Auditor | one branch's entries and levels | missing pages, ladder gaps, misplaced entries |

All four run as subagent passes over packets, as consolidation and writing do; the packet format leaves room for an
API runner later.

## Build order
1. `crawl --hubs`; gap-fill the chapters that gained pages; rebuild the course.
2. Learned scope score + judge, evaluated against the calibration set.
3. `frame plan` / `resolve` / `audit`, with phrase dossiers.
4. Adaptive probing of the extra signals.
5. Recursive tree and per-branch budgets.
