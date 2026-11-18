# System design interview questions, beginner to advanced — state

_Update after every step. `coursesmith status system-design` prints the live numbers._

## Where it stands
- **Sources vetted and checked** (`reports/sources.md`, stamp in `scope/sources.ok`): Wikipedia, three openly licensed
  guides (System Design Primer, CC BY 4.0; Singh's System Design and ByteByteGo System Design 101, both CC BY-NC-ND 4.0,
  so this course is `distribution: personal`), four RFCs (9110, 9111, 6455, 1034) and eleven foundational papers
  (abstracts only). Licenses were read from each repository's LICENSE file; commits are pinned in `subject.yaml`.
- **Frame written by hand** (`subject.yaml` `frame:`, built into `frame.yaml`): 6 parts and 48 chapters. Foundations,
  Building blocks, Scaling and consistency, Messaging/APIs/architecture, Reliability/security/operations, and
  **Design interview questions** (18 chapters, each one question: the primer's eight solutions, Singh's five case
  studies, and ByteByteGo's Gmail, Google Maps, stock exchange, Google Docs, payment and notification designs).
- **Crawled** the frame's pages only (`crawl --depth 0`): 347 pages, 27,922 sentences. Wikipedia 126 pages
  (16,785 sentences), Singh's guide 57 sections (2,983; its one file is split into 61 section pages, see
  `coursesmith sources parts system-design`), ByteByteGo 141 guides (2,033), the primer's 8 solutions (1,270), 4 RFCs
  (4,802) and 11 paper abstracts (49).
- **Extracted, graphed, dossiers built**: every page is in a chapter; 98 dossier chunks across the 48 chapters. A
  question chapter's dossier opens with `QUESTION: ...` and the instruction to write one Worked example.

## Next steps (the usual coordinator workflow, as for nature-economy)
1. `report coverage`, then read `reports/frame_report.md`; decide any gap-fill crawls (`crawl --depth 1` follows in-scope
   Wikipedia links; RFC and paper sources have `depth: 0` on purpose).
2. Run consolidation passes per chapter (`guides/CONSOLIDATION_GUIDE.md`, including "When sources disagree" and
   "Question chapters": exactly one **Worked example** per question chapter). Then `finalize --merge`, `finalize`,
   `select`, an ordering pass (`order build`, `order lock`), `verify`.
3. Writing passes (`guides/WRITING_GUIDE.md`: worked examples are 300-700 words in paragraphs; declare capacity math
   under `derived`), `write render`, `units build`, a question pass, `write render`, `units build` again, `publish check`,
   `export`, `publish build`.

## Notes
- Chapters whose answer is built from a concept page (a rate limiter, a key-value store, an ID generator) were left
  out: the sources have the concepts but no worked solution to cite. Add one as a question chapter with `also:` pages
  if a source with a worked answer turns up (`coursesmith sources discover system-design --query "..."`).
- Not included yet: official documentation sites (Redis, PostgreSQL, Kafka) and the Google SRE books. Both need their
  licenses read first (`sources check` does it) and an `html` source with an allowlist; the SRE books are CC BY-NC-ND.
- A ByteByteGo guide is often a diagram plus a paragraph, so its entries will be short.
