# Earth History — state

_Update after every step. `coursesmith status earth-history` prints the live numbers._

## Where it stands (2026-11-18)
- **Stage:** published.
- **Source:** the Deep Time Chronicle, an earlier Wikipedia-sourced project frozen as v1, ported into this
  layout: 1,672 selected entries (of 2,124 consolidated events), the chronicle's order, 78 headings (ICS chart
  v2026/06), 74 scene-setters as chapter openers, and the closing narrative.
- **Units:** 365 units (153 of 4 entries, 212 of 5), split chapter-aware; no unit opens with a chapter's last
  entry. Ordering is chronological; the proportional clock is on (origin 4,567 Ma, the ICS base of the Hadean).
- **Upgrade pass (2026-11-18):** prose rewritten to the current WRITING_GUIDE (batches `fill.eh1-8.*`, over the
  original `fill.chronicle.json`), 62 chapter reviews added, 365 unit questions, 33 glossary terms, 257 figures
  on 249 entries, 106 licensed Landmark images (`edition.images` and `edition.questions` on).
- **Checks:** `write check` 0 problems (23 word-count warnings on thin Minor entries); `publish check` 0 problems.

## Notes
- This subject was not crawled by this engine: its entries came over whole from the chronicle, so `ledger.csv`,
  `frame.yaml` and the discovery files are absent. It is an example of the output format, a chronological
  course, and the proportional clock.
- Entries still have no structured definitions, so the glossary holds only the writers' extra terms; 32 terms
  used before their defining unit were dropped (`fill.zz-glossary.json`).
- Glossary and figure sent_ids are entry-level (a figure cites its entry's sentences), not matched one by one.
