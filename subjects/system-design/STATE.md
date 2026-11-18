# System design interview questions, beginner to advanced — state

_Update after every step. `coursesmith status system-design` prints the live numbers._

## Where it stands
**Finished and published:** 1,091 entries in 48 chapters, 312 units (3 or 4 entries each), 312 questions, 312 EPUBs plus
the complete edition (`build/epubs/system-design/`) and `output/course.json` (all 312 units render through the
xteink-daily `Course` loader). `write check` and `publish check` report 0 problems.

- **Sources** (`reports/sources.md`, stamp in `scope/sources.ok`): Wikipedia; three openly licensed guides (System
  Design Primer, CC BY 4.0; Singh's System Design and ByteByteGo System Design 101, CC BY-NC-ND 4.0); fourteen RFCs;
  twenty-two paper abstracts; the Google SRE book (CC BY-NC-ND 4.0, ten chapters); the Kubernetes documentation (CC BY
  4.0) and the PostgreSQL documentation (PostgreSQL License). Licenses were read from the sources, commits pinned.
  Two NonCommercial guides and the SRE book make the course `distribution: personal`.
- **Frame** (hand-written in `subject.yaml`, built into `frame.yaml`): 6 parts. Foundations, Building blocks (starting
  with "Algorithms behind the systems", moved up because hashing and Bloom filters are needed by the chapters after
  it), Scaling and consistency, Messaging/APIs/architecture, Reliability/security/operations, and **Design interview
  questions** (19 chapters, each one question with a worked answer).
- **Consolidation and gap-fill:** the first round gave 701 entries; the gap-fill round (332 more pages, 124 chunks)
  brought it to 1,102 (1,091 selected; 10 Gmail protocol details and one more are excluded). `reports/gaps.md` lists
  nothing open. Accepted gaps, with reasons, are under `gaps: accepted:` in `subject.yaml`.
- **Order locked** (ids frozen). 124 prerequisite edges point to a later chapter and were moved to `related`
  (`reports/order.md`); 35 cycles were broken.
- **Verification:** tier B ran (547 DOIs); tiers: 498 Wikipedia, 224 reference, 180 curated, 132 standard, 35 official,
  22 primary. No authorities are registered, so tiers C and D are empty. Tier A (`crawl --context`) was skipped.
- **Prose:** all entries written with figures (176, in `work/write/figures.*.json`) and 48 chapter reviews;
  `edition.paragraphs: true`. Term-before-definition waivers are in `waivers.json` (API, SQL and similar, with reasons).

## Known limits
- Seven worked answers are thin because no vetted source gives scale, a data model or an API: Gmail, Google Maps,
  Google Docs, a stock exchange, a payment system, a notification system and a permission system. They rest on standards,
  papers and concept pages and say what the sources say; none was padded.
- Wikipedia superscripts and root signs are lost in extraction, so formulas (UUID, k-d tree, HyperLogLog's error
  bound beyond the paper's abstract) are stated only where a sentence carries them.
- The Google File System paper page holds only publisher chrome; its entry cites Wikipedia alone.
- Wikipedia has no page for event sourcing or differential synchronization; the entries rest on the other sources.
- Not included: the Redis docs (CC BY-NC-SA) and Kafka docs (one monolithic page).

## If you change entries
`finalize` -> `report gaps` -> `select` -> `order build` (ids stay) -> `verify` -> `write render` and `check` -> `units build`
(then `write questions`, a question pass, `write render`, `units build` again) -> `publish check`, `export`, `publish build`.
