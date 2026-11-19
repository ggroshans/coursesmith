# coursesmith

Build a complete course on any subject from Wikipedia and other vetted sources: every branch and subtopic,
ordered from foundational to advanced, with every fact traced to the source sentence it came from.

Give it a whole field (soil science, world history), a medium topic (plate tectonics), or a narrow question
(how full-range, flat-response speakers work). It finds the pages a course on that subject needs, extracts and
consolidates their facts into entries, orders the entries so each one builds on what came before, writes them
up, and splits the result into short units. What you do with it is up to you: a web app, flashcards, daily
lessons, a book. EPUB is built in; `course.json` carries everything for anything else.

One rule is never relaxed: **every fact comes from a cited source sentence (Wikipedia by default, or a
source you approved). Nothing comes from a model's general knowledge.** Language models help find pages, judge scope,
order prerequisites and write prose, but only from the cited facts they are handed.

## Examples

| Subject | Ordering | Size |
|---|---|---|
| [`soil-science`](subjects/soil-science) | foundational to advanced | 2,629 entries in 584 units, 12 parts, 50 chapters, from 7,072 pages and four open textbooks and the WRB |
| [`nature-economy`](subjects/nature-economy) | foundational to advanced | 3,932 entries in 874 units, 14 parts, 76 chapters, from 3,857 pages, the Dasgupta Review and an open economics chapter |
| [`earth-history`](subjects/earth-history) | chronological | 1,672 entries in 365 units, from the Hadean to the present (ported from an earlier project) |

Each has `output/course.json` (the whole course), `output/course.md` (readable in one file) and
`output/curriculum.md` (the table of contents with every entry's level, kind and prerequisites).

[`system-design`](subjects/system-design) is the first course built from more than Wikipedia: system design
interview questions, beginner to advanced, from Wikipedia, three openly licensed guides, fourteen RFCs, twenty-two
paper abstracts, the Google SRE book and the Kubernetes and PostgreSQL documentation. It has 48 chapters (19 of them
design questions with worked answers), 1,091 entries and 312 daily units, built and published (see its `STATE.md`).
It is `distribution: personal`, because two of its guides and the SRE book are NonCommercial.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -t .
```

Python 3.9+. No other services: the page cache and the sentence index are local files under `cache/`.

**Crawling politely.** Wikimedia's User-Agent policy asks crawlers to give a contact. Set `COURSESMITH_CONTACT`
to an email address or URL, or write it to `cache/contact.txt`; `crawl` refuses to run without one. Requests
stay at or under 0.5 per second, 50 titles per metadata call, honoring `retry-after`. A large subject takes a
few hours to crawl; a small one, minutes.

## Start a subject

```sh
coursesmith init frfr-speakers --title "How FRFR speakers work" \
    --seed "Full-range speaker" --seed "Loudspeaker" --category Loudspeakers
```

This writes `subjects/frfr-speakers/subject.yaml`, with every setting commented. Edit it, then follow the
pipeline below. `coursesmith status` shows where each subject stands at any time.

## The pipeline

| Stage | Command | You review |
|---|---|---|
| Frame | `frame build` | **yes**: edit `frame.yaml` (parts, chapters, seeds); label `scope/calibration.csv`, then `scope tune` |
| Crawl | `crawl [--depth N]`, then `crawl --hubs` | |
| Judge | `scope judge-packets`, judge passes, `scope judge-merge`, `crawl --judged` | spot-check `scope/judge.json` |
| Syllabus | `frame plan-packet`, planner pass, `frame resolve`, `crawl --judged`, `dossier --phrases` | **yes**: add new branches to `frame.yaml`; read `reports/syllabus.md` |
| Extract | `extract` | |
| Graph | `graph build [--pageviews]` | |
| Coverage | `report coverage` | **yes**: decide gap-fill crawls |
| Dossiers | `dossier` | |
| Consolidate | consolidation passes, then `finalize` | resolve `reports/duplicates.md` |
| Gap-fill | `report gaps [--probe]`; `frame add`, `crawl`, `extract`, `graph build`, `dossier --new`, passes, `finalize --merge`, `finalize` | **yes**: choose the pages; accept the gaps you cannot fill (`gaps: accepted:`) |
| Select | `select` | |
| Order | `order packet`, ordering pass, `order build` | **yes**: read `output/curriculum.md`, then `order lock` |
| Verify | `crawl --context`, `verify`, verification pass | read every genuine conflict |
| Write | `write skeleton`, writing passes (prose and figures), `write render`, `write check` | spot-read |
| Figures | `figures` draws `figures.json` (flowcharts in Mermaid, cycles, layers, scales, bar charts, trees, tables) to look at | look at every one |
| Units | `units build`; if the subject has questions: `write questions`, a question pass, `write render`, then `units build` again (units copy their question only when built) | |
| Images | `images` (subjects with `edition.images: true`) | |
| Output | `export`; `publish build`, `publish check` for EPUBs | |

Every command is `coursesmith <command> <subject> [args]`; `coursesmith <command> -h` explains one. After
changing entries, re-run `finalize → (report gaps → gap-fill → finalize) → select → order build → verify → write skeleton → write render →
units build → (question pass → write render → units build) → export / publish build`. Entry ids never change
after `order lock`.

Lookup commands for a pass or for you: `sections` and `page` (a page's sentences with ids), `search`
(sentences containing a phrase across the subject), `sent` (sentences by id), `ctx` (sentences around a
phrase).

### The passes

The judgment steps (judge, planner, consolidation, ordering, verification, writing, questions, gap-fill) are
**passes**: the engine writes a packet (`work/.../*.md`), an agent reads it with the matching guide in
`guides/` and writes its answer as JSON, and the engine merges and validates it. Each guide is a self-contained
brief: what to read, what to write, the rules, and the checks the output must pass.

Any capable coding agent can run a pass, and passes over separate packets can run in parallel, one agent per
packet. Point the agent at the repo, the guide and its packet; give each parallel pass its own scratch folder
(`subjects/<slug>/work/tmp/<pass>/`). The engine never trusts a pass: `finalize`, `order build`, `write check`
and `publish check` reject anything that breaks the rules, and every fact must cite sentence ids that exist.

| Guide | Reads | Writes |
|---|---|---|
| `SOURCES_GUIDE.md` | `work/sources/packet.md` | `work/sources/found.yaml` |
| `JUDGE_GUIDE.md` | `work/scope/judge-packet-NN.md` | `scope/judge/batch-NN.json` |
| `PLANNER_GUIDE.md` | `work/scope/plan-packet.md` | `scope/syllabus.json` |
| `CONSOLIDATION_GUIDE.md` | `work/dossiers/<chapter>/chunk_NN.md` | `entries/draft/<chapter>.partNN.jsonl` |
| `GAPFILL_GUIDE.md` | `reports/gaps.md`, `reports/coverage.md`, gaps files | `frame.yaml` seeds, more draft entries |
| `ORDERING_GUIDE.md` | `work/order/packet*.md` | `work/order/prereqs.NN.json` |
| `VERIFICATION_GUIDE.md` | `verify/worklist.md` | `verify/reviews.json` |
| `WRITING_GUIDE.md` | `work/write/packet-<part>.md`, `questions-packet*.md` | `work/write/fill.<part>.NN.json` |

## Beyond Wikipedia

Wikipedia is the default and needs no setup. A subject can also read other **vetted** sources: a GitHub
repository, an IETF RFC, an official docs site, a PDF, a paper, another MediaWiki. "Vetted" means a person
approved the list and the license was read from the source itself; the crawl never leaves it.

```sh
coursesmith init system-design --title "System design interview questions" --questions
coursesmith sources discover system-design     # candidates + evidence -> scope/sources.candidates.yaml
coursesmith sources packet system-design       # optional: a brief for a web-search session (guides/SOURCES_GUIDE.md)
coursesmith sources merge system-design        #           ... and fold its found.yaml back in
# accept candidates by copying them under `sources:` in subject.yaml, then:
coursesmith sources check system-design --fix-refs   # reads each LICENSE, pins commits, checks allowlists
```

A page of another source is named by a **key** (`rfc>9110`, `gh>owner/repo/path.md`, `doc>host/path`,
`paper>10.1145/...`); Wikipedia keeps bare titles, so nothing made before changed. List keys under `seeds:` or in
`frame.yaml` like any page. Each source carries a **trust tier** (official, standard, primary, reference, curated,
commentary): when sources disagree the higher tier's value is the fact and the other is recorded as a conflict.
Every entry's tag line, every EPUB's "Sources and license" page and `course.json` name the pages, versions and
licenses used. `distribution: public` makes `publish check` refuse any source whose license forbids
redistribution (NonCommercial, NoDerivatives); the default, `personal`, allows them and says so.

**A course of questions.** `course_type: questions`, with parts flagged `question: true`: each chapter is one
interview-style question, answered by a **Worked example** entry (longer, in paragraphs, ordered last in its
chapter) plus the concepts a good answer relies on. Capacity math ("about 4 writes a second") is declared as a
derived number and recomputed by the checks, so it never slips past the sourced-numbers rule. Architecture
diagrams use `flow` figures with database cylinders and tier boxes. Everything else about the course, the
daily-unit layout and the `course.json` the e-reader reads, is the same.

## Subjects of every size

**A whole field.** Fill in `hubs` in `subject.yaml` (the subject's navbox, index page, Vital Articles
sections, WikiProject) and sketch the parts with hints; `frame build` assigns every hub page to a chapter.
Then the judge pass sorts the borderline pages, and the planner pass lays out the field's full syllabus,
branch by branch, and names what the frame missed. Concepts with no article of their own are assembled from
sentences scattered across pages (`dossier --phrases`). `docs/DISCOVERY_DESIGN.md` covers how this works and
what it measured on soil science.

**A medium topic.** A few seeds and one or two category roots; `frame build` with no parts makes one part
whose chapters come from Wikipedia's categories. The planner pass then proposes the branches.

**A niche topic or a question.** Seeds are the main lever: the two or three articles that answer it.

- Leave `hubs` empty (niche topics rarely have any).
- Lower `scope.threshold` to 3–4, and crawl a little deeper (`crawl --depth 3`).
- Lean on the planner and judge passes to find the pages the topic needs from neighboring fields. A
  question about speakers needs acoustics and electronics pages that never mention speakers in their titles.

Some floors are tuned for larger subjects and may need lowering for a very small one: `SEED_MIN` and the
three-page category cluster in `coursesmith/frame/build.py`, `MIN_PHRASE_SENTENCES` in `coursesmith/frame/syllabus.py`,
and `MIN_LINKS` in `coursesmith/crawl/judge.py`. Units adapt on their own: a course of 7 entries gets two units.

## Output

- **`output/course.json`** (`coursesmith export`): the outline, every entry in order with its prose, facts and
  citations, units, glossary, questions, and the text of every cited sentence with its page and revision.
  The format, with recipes for a web app, flashcards and search, is in [`docs/OUTPUT.md`](docs/OUTPUT.md).
- **EPUBs** (`coursesmith publish build`): one per unit and one for the whole course, in `build/epubs/<slug>/`,
  each with a sources and license page.
- **The subject's files**: every file is documented in [`SCHEMA.md`](SCHEMA.md).

Refreshing a course later: re-crawl (new revisions are stored beside the old), `extract`, then `finalize`
lists every entry whose cited sentences changed or vanished; only those need another pass. Sentence ids are a
hash of page title and text, so unchanged sentences keep their ids. After a fix to the page cleaner,
`reclean` re-cleans cached pages and carries every citation over to the new sentence ids.

## Layout

```
coursesmith/  the `coursesmith` command
  sources/      source adapters (wikipedia, github, html, rfc, pdf, paper), registry, keys, licenses, discover, check
  text/         DOM, Markdown, PDF and bracketed-reference text for every source
  crawl/        API client, page store, cleaning, citations, scope, judge, crawl
  extract/      sentence splitting, the sentence index, mentions, dates
  frame/        hub readers, frame builder, syllabus planner and resolver, coverage
  graph/        concept graph, importance, difficulty, RefD prerequisites
  consolidate/  dossiers, finalize
  order/        selection, pedagogical and chronological ordering
  verify/       OpenAlex/Crossref lookups, authorities, reviews
  write/        writer packets, render, checks
  publish/      units, EPUB, covers, images, checks, export
  port/         reclean
guides/       briefs for the passes
sources/      registry.yaml: domains and repos vetted once, with the license read and when
subjects/     one folder per subject
docs/         design (DESIGN.md), discovery (DISCOVERY_DESIGN.md), output format (OUTPUT.md)
tests/        unit tests
cache/        gitignored: shared page cache keyed by page key and version, sentence index, images
build/        gitignored: EPUBs
```

`docs/DESIGN.md` explains the entry schema, verification, ordering and voice.

## License

The code is MIT (`LICENSE`). Course content (everything under `subjects/` and everything the engine exports)
is derived from Wikipedia (CC BY-SA 4.0) and, for a subject that lists them, other sources under their own
licenses, attributed through the cited revisions and versions; see `NOTICE.md`.

## Renamed from wikicourse

The package and command were `wikicourse` before 0.2. `COURSESMITH_ROOT`, `COURSESMITH_CONTACT` and
`COURSESMITH_MIN_INTERVAL` replace the `WIKICOURSE_*` variables, which are still read as a fallback. The
`course.json` format id stays `wikicourse-course` because readers match on it. If you rename the repo folder,
update the `course` path in the xteink-daily config, which points at `../wikicourse/subjects/<slug>/output/course.json`.
