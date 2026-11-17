# wikicourse

Wikipedia subjects as sourced courses, ordered foundational to advanced.

A subject is crawled from Wikipedia, consolidated into sourced entries, ordered from foundational to advanced
(or by time), written up, and split into as many units of 4–5 entries as the subject needs, with EPUBs as one output.

One rule is never relaxed: every fact traces to a Wikipedia revision or a verified external source. Nothing
comes from general knowledge.

## Subjects

| Subject | Ordering | State |
|---|---|---|
| `earth-history` | chronological | 1,672 entries in 365 units, published (ported from the Deep Time Chronicle) |
| `soil-science` | pedagogical | 2,274 entries in 505 units, 50 chapters, published (no length cap: as long as the material runs) |

`wikicourse status` prints where each one stands; each subject's `STATE.md` says what to do next.

## Setup

```sh
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/python -m unittest discover -s tests -t .
```

Python 3.9+ is enough; the EPUB writer is built in, so neither pandoc nor EbookLib is needed.

Wikimedia's User-Agent policy asks crawlers for a contact. Set `WIKICOURSE_CONTACT` to an email address or URL,
or put it in `cache/contact.txt` (gitignored). Nothing else personal leaves the machine. Requests stay at or
under 0.5 per second, 50 titles per metadata call, honoring `retry-after`.

## Building a subject

| Stage | Command | Human review |
|---|---|---|
| Frame | `frame build` | **Yes**: edit `frame.yaml`; label `scope/calibration.csv`, then `scope tune` |
| Crawl | `crawl [--chapter KEY] [--depth N]`, then `crawl --hubs` (every hub-list page) | |
| Judge | `scope judge-packets`, judge passes (`guides/JUDGE_GUIDE.md`), `scope judge-merge`, `crawl --judged` | spot-check `scope/judge.json` |
| Syllabus | `frame plan-packet`, the planner pass (`guides/PLANNER_GUIDE.md`), `frame resolve`, `crawl --judged`, `dossier --phrases` | **Yes**: new chapters into `frame.yaml`; read `reports/syllabus.md` |
| Extract | `extract` | |
| Graph | `graph build [--pageviews]` | |
| Coverage | `report coverage` | **Yes**: decide gap-fill crawls (`guides/GAPFILL_GUIDE.md`) |
| Dossiers | `dossier [CHAPTER]` | |
| Consolidate | Claude Code passes per `guides/CONSOLIDATION_GUIDE.md`, then `finalize` | resolve `reports/duplicates.md` |
| Select | `select` | |
| Order | `order packet`, the ordering pass (`guides/ORDERING_GUIDE.md`), `order build` | **Yes**: reorder `output/curriculum.md`, then `order lock` |
| Verify | `crawl --context` (tier A), `verify` (tiers B–D, `guides/VERIFICATION_GUIDE.md`) | read every genuine conflict |
| Write | `write skeleton`, writing passes (`guides/WRITING_GUIDE.md`), `write render`, `write check` | spot-read |
| Units | `units build`, then `write questions` and a question pass if the subject has questions | |
| Images | `images` (subjects with `edition.images: true`) | |
| Publish | `publish build`, `publish check` | |

Every command is `wikicourse <command> <subject> [args]`; `wikicourse <command> -h` explains one. After any entry
change, re-run: `finalize → select → order build → verify → write skeleton → write render → units build →
(question pass) → publish build`. Entry ids never change after `order lock`.

Discovery (hub crawl, scope judge, syllabus plan) is described with its measured results in
`docs/DISCOVERY_DESIGN.md`. After a cleaner fix, `reclean` re-cleans cached pages and carries every citation over to
the new sentence ids.

Refreshing sources later: re-crawl (new revisions are stored next to the old ones in `cache/`), `extract`, then
`finalize` lists every entry whose cited sentences changed or vanished; only those need another pass. Sentence
ids are a hash of title and text, so unchanged sentences keep their ids.

## Layout

```
engine/      python package behind the `wikicourse` command
  crawl/       API client, page store, cleaning, citations, scope, crawl      (from the chronicle's crawler/)
  extract/     sentence splitting, sentence index, mentions, dates            (from the chronicle's crawler/)
  frame/       hub readers, frame builder, coverage report
  graph/       concept graph, importance, difficulty, RefD prerequisites
  consolidate/ dossiers, finalize
  order/       selection, pedagogical and chronological ordering
  verify/      OpenAlex/Crossref lookups, authorities, reviews
  write/       writer packets, render, checks
  publish/     units, EPUB, covers, images, checks
  port/        reclean (re-clean cached pages, carry citations over)
guides/      instructions for the Claude Code passes
subjects/    one folder per subject (subject.yaml, frame.yaml, entries, order, units, STATE.md)
docs/        design notes
tests/       unit tests
cache/       gitignored, shared page cache keyed by title + revid
build/       gitignored, EPUBs
```

`SCHEMA.md` documents every file.

## License

Course text is adapted from Wikipedia under CC BY-SA 4.0; every edition carries an attribution page with page
titles, URLs and revision ids.
