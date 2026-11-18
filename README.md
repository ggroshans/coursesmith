# wikicourse

Build a complete course on any subject from Wikipedia: every branch and subtopic, ordered from foundational to
advanced, with every fact traced to the Wikipedia sentence it came from.

Give it a whole field (soil science, world history), a medium topic (plate tectonics), or a narrow question
(how full-range, flat-response speakers work). It finds the pages a course on that subject needs, extracts and
consolidates their facts into entries, orders the entries so each one builds on what came before, writes them
up, and splits the result into short units. What you do with it is up to you: a web app, flashcards, daily
lessons, a book. EPUB is built in; `course.json` carries everything for anything else.

One rule is never relaxed: **every fact comes from a cited Wikipedia sentence (or a verified external
source). Nothing comes from a model's general knowledge.** Language models help find pages, judge scope,
order prerequisites and write prose, but only from the cited facts they are handed.

## Examples

| Subject | Ordering | Size |
|---|---|---|
| [`soil-science`](subjects/soil-science) | foundational to advanced | 2,274 entries in 505 units, 12 parts, 50 chapters, from 6,885 pages |
| [`nature-economy`](subjects/nature-economy) | foundational to advanced | 3,590 entries in 798 units, 14 parts, 76 chapters, from 3,709 pages |

Each has `output/course.json` (the whole course), `output/course.md` (readable in one file) and
`output/curriculum.md` (the table of contents with every entry's level, kind and prerequisites).

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -t .
```

Python 3.9+. No other services: the page cache and the sentence index are local files under `cache/`.

**Crawling politely.** Wikimedia's User-Agent policy asks crawlers to give a contact. Set `WIKICOURSE_CONTACT`
to an email address or URL, or write it to `cache/contact.txt`; `crawl` refuses to run without one. Requests
stay at or under 0.5 per second, 50 titles per metadata call, honoring `retry-after`. A large subject takes a
few hours to crawl; a small one, minutes.

## Start a subject

```sh
wikicourse init frfr-speakers --title "How FRFR speakers work" \
    --seed "Full-range speaker" --seed "Loudspeaker" --category Loudspeakers
```

This writes `subjects/frfr-speakers/subject.yaml`, with every setting commented. Edit it, then follow the
pipeline below. `wikicourse status` shows where each subject stands at any time.

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
| Select | `select` | |
| Order | `order packet`, ordering pass, `order build` | **yes**: read `output/curriculum.md`, then `order lock` |
| Verify | `crawl --context`, `verify`, verification pass | read every genuine conflict |
| Write | `write skeleton`, writing passes, `write render`, `write check` | spot-read |
| Units | `units build`; `write questions` and a question pass if the subject has questions | |
| Images | `images` (subjects with `edition.images: true`) | |
| Output | `export`; `publish build`, `publish check` for EPUBs | |

Every command is `wikicourse <command> <subject> [args]`; `wikicourse <command> -h` explains one. After
changing entries, re-run `finalize → select → order build → verify → write skeleton → write render →
units build → (question pass) → export / publish build`. Entry ids never change after `order lock`.

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
| `JUDGE_GUIDE.md` | `work/scope/judge-packet-NN.md` | `scope/judge/batch-NN.json` |
| `PLANNER_GUIDE.md` | `work/scope/plan-packet.md` | `scope/syllabus.json` |
| `CONSOLIDATION_GUIDE.md` | `work/dossiers/<chapter>/chunk_NN.md` | `entries/draft/<chapter>.partNN.jsonl` |
| `GAPFILL_GUIDE.md` | `reports/coverage.md`, gaps files | `frame.yaml` seeds, more draft entries |
| `ORDERING_GUIDE.md` | `work/order/packet*.md` | `work/order/prereqs.NN.json` |
| `VERIFICATION_GUIDE.md` | `verify/worklist.md` | `verify/reviews.json` |
| `WRITING_GUIDE.md` | `work/write/packet-<part>.md`, `questions-packet*.md` | `work/write/fill.<part>.NN.json` |

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
three-page category cluster in `engine/frame/build.py`, `MIN_PHRASE_SENTENCES` in `engine/frame/syllabus.py`,
and `MIN_LINKS` in `engine/crawl/judge.py`. Units adapt on their own: a course of 7 entries gets two units.

## Output

- **`output/course.json`** (`wikicourse export`): the outline, every entry in order with its prose, facts and
  citations, units, glossary, questions, and the text of every cited sentence with its page and revision.
  The format, with recipes for a web app, flashcards and search, is in [`docs/OUTPUT.md`](docs/OUTPUT.md).
- **EPUBs** (`wikicourse publish build`): one per unit and one for the whole course, in `build/epubs/<slug>/`,
  each with a sources and license page.
- **The subject's files**: every file is documented in [`SCHEMA.md`](SCHEMA.md).

Refreshing a course later: re-crawl (new revisions are stored beside the old), `extract`, then `finalize`
lists every entry whose cited sentences changed or vanished; only those need another pass. Sentence ids are a
hash of page title and text, so unchanged sentences keep their ids. After a fix to the page cleaner,
`reclean` re-cleans cached pages and carries every citation over to the new sentence ids.

## Layout

```
engine/       the `wikicourse` command
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
subjects/     one folder per subject
docs/         design (DESIGN.md), discovery (DISCOVERY_DESIGN.md), output format (OUTPUT.md)
tests/        unit tests
cache/        gitignored: shared page cache keyed by title and revision, sentence index, images
build/        gitignored: EPUBs
```

`docs/DESIGN.md` explains the entry schema, verification, ordering and voice.

## License

The code is MIT (`LICENSE`). Course content (everything under `subjects/` and everything the engine exports)
is derived from Wikipedia and is CC BY-SA 4.0, attributed through the cited revisions; see `NOTICE.md`.
