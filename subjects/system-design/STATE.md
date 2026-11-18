# System design interview questions, beginner to advanced — state

_Update after every step. `coursesmith status system-design` prints the live numbers._

## Where it stands
- **Sources vetted and checked** (`reports/sources.md`, stamp in `scope/sources.ok`): Wikipedia, three openly licensed
  guides (System Design Primer, CC BY 4.0; Singh's System Design and ByteByteGo System Design 101, both CC BY-NC-ND 4.0,
  so this course is `distribution: personal`), four RFCs (9110, 9111, 6455, 1034) and eleven foundational papers
  (abstracts only). Licenses were read from each repository's LICENSE file; commits are pinned in `subject.yaml`.
- **Frame written by hand** (`subject.yaml` `frame:`, built into `frame.yaml`): 6 parts and 48 chapters. Foundations,
  Building blocks, Scaling and consistency, Messaging/APIs/architecture, Reliability/security/operations, and
  **Design interview questions** (19 chapters, each one question: the primer's eight solutions, Singh's five case
  studies, and ByteByteGo's Gmail, Google Maps, stock exchange, Google Docs, payment and notification designs).
- **Crawled** the frame's pages only (`crawl --depth 0`): 347 pages, 27,922 sentences. Wikipedia 126 pages
  (16,785 sentences), Singh's guide 57 sections (2,983; its one file is split into 61 section pages, see
  `coursesmith sources parts system-design`), ByteByteGo 141 guides (2,033), the primer's 8 solutions (1,270), 4 RFCs
  (4,802) and 11 paper abstracts (49).
- **Extracted, graphed, dossiers built**: every page is in a chapter; 98 dossier chunks across the 48 chapters. A
  question chapter's dossier opens with `QUESTION: ...` and the instruction to write one Worked example.
- **Consolidated** (28 batches of passes, merged per chapter, full `finalize`): 701 entries in 48 chapters, 0 validation
  problems, 0 possible duplicates. 62 Landmark, 306 Major, 333 Minor; 110 Foundational, 491 Intermediate, 100 Advanced.
  Kinds: 373 Concept, 103 Method, 103 Classification, 43 Process, 43 Practice, 19 Worked example (exactly one in each
  of the 19 question chapters, none elsewhere), 11 Case study, 5 Debate, 1 Event. Prerequisite/related names that only
  differed in wording were aliased to existing titles.

## Next steps
1. **Gap-fill** (`guides/GAPFILL_GUIDE.md`): 32 prerequisite/related names resolve to no entry (`finalize` lists them).
   The real concept gaps are: Hash function, Hash table, Quorum, Public-key cryptography, Inverted index, Data
   warehouse, Canary release, Schema registry, Database per service, Write-ahead log, ACID, Serialization, Connection
   pooling, Client-server model, Distributed hash table, Distributed tracing, Domain-driven design, Feature toggle,
   Rolling update, DDoS, Edge computing, Peer-to-peer, Zero trust security model, TCP three-way handshake. Add seeds
   to `subject.yaml`, `crawl --chapter <key> --depth 0`, `extract`, `graph build`, `dossier`, consolidate the new chunk.
   The per-chapter `entries/draft/<chapter>.gaps.md` files list smaller omissions.
2. `select` (weights skew Major; trim to the per-unit target and drop the thin tech-stack Case studies), an ordering
   pass (`order packet`, ordering agents, `order build`, `order lock`), `verify`.
3. Writing passes (`guides/WRITING_GUIDE.md`: worked examples are 300-700 words in paragraphs; declare capacity math
   under `derived`), `write render`, `units build`, a question pass, `write render`, `units build` again, `publish check`,
   `export`, `publish build`.

## Known limits of the sources
- Wikipedia superscripts and root signs are lost in extraction, so formulas such as HyperLogLog's and UUID's are
  thin; the consolidation avoided stating them.
- The GFS paper page holds only publisher chrome, so the GFS entry cites Wikipedia alone.
- Singh's key-generation estimate contradicts itself (300 GB against about 390 GB); the entry leaves it out.
- ByteByteGo guides are often a diagram caption plus a few sentences. Thirteen entries are marked `thin:` in their
  notes: Resilience patterns, Map tiles, Secure system design checklist, API security practices, Reducing latency,
  Choosing a message queue and the Worked examples for Gmail, Google Maps, Google Docs, stock exchange, notification
  system, payment system and permission system.

## Notes
- Chapters whose answer is built from a concept page (a rate limiter, a key-value store, an ID generator) were left
  out: the sources have the concepts but no worked solution to cite. Add one as a question chapter with `also:` pages
  if a source with a worked answer turns up (`coursesmith sources discover system-design --query "..."`).
- Not included yet: official documentation sites (Redis, PostgreSQL, Kafka) and the Google SRE books. Both need their
  licenses read first (`sources check` does it) and an `html` source with an allowlist; the SRE books are CC BY-NC-ND.
- A ByteByteGo guide is often a diagram plus a paragraph, so its entries will be short.
