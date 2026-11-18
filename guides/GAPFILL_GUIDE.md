# Gap-fill guide

Read `CONSOLIDATION_GUIDE.md` first: its rules all apply. This addendum covers the second pass over a subject once
the first consolidation is done and `coursesmith report gaps <subject>` shows what the course could not teach.

**Gap-fill is a standing step, not an option.** It sits between the first full `finalize` and `select`. `status`
shows the open counts and `select` warns while any are left. Run it once for every subject, and a second time only
if the first round's new entries name concepts that still resolve to nothing. It ends when `reports/gaps.md` lists
nothing but gaps the owner has accepted.

## Where gaps come from
`coursesmith report gaps <subject> [--probe]` writes `reports/gaps.md` from the drafts in `entries/draft/`:

1. **Unresolved names.** A prerequisite or related title that no entry has: the course leans on a concept and never
   explains it. `--probe` asks Wikipedia whether each name is a page, and under which title.
2. **Thin entries.** An entry whose `notes` start with `thin:` (a consolidation pass sets it when the sources hold too
   little: a worked answer that is only a diagram caption, a checklist that names points without explaining them).
3. **Gaps files.** Each pass's `<chapter>.gaps.md`: pages it expected and did not find. Read the ones with many bullets.

`reports/coverage.md` (hub articles not crawled, thin chapters) is the fourth input; read it too.

## The loop
1. **Triage each gap.**
   - The name is an entry under other words ("Database indexing" for "Database index"): fix the prerequisite in the
     draft instead of crawling anything.
   - A real concept the course should teach: seed a page for it (step 2).
   - A thin entry: add pages that can fill what its note says is missing (step 2). If a better source exists but is
     not in `subject.yaml`, find it first: `coursesmith sources discover <subject> --query "<topic>"`, or a
     `guides/SOURCES_GUIDE.md` session, then `sources check`. A source with no findable license, or one only a book
     summarizes, is not a source. Standards (RFCs), original papers, official documentation and the subject's
     Wikipedia concept pages are the usual fill for a worked example whose guide is too short.
   - Not worth teaching, or no vetted source explains it: accept it under `gaps: accepted:` in `subject.yaml`, with
     the reason. A thin entry is better than a padded one.
2. **Seed.** `coursesmith frame add <subject> <chapter> "<page>" ...` (Wikipedia titles or source keys such as
   `rfc>9110`, `doc>host/path`, `paper>10.x/...`; `--also` for context pages). It writes `frame.yaml` and, for a
   subject with a hand-written `frame:`, `subject.yaml` too, and skips a page another chapter already lists. A page
   belongs to the chapter whose reader needs it first; a question chapter takes the concept pages its answer rests on.
   A source key must be inside a source's allowlist (`sources check` after widening one: that is the owner's call).
3. **Crawl and index.** `coursesmith crawl <subject> --depth 0` (add `--max-pages N` when more than 300 are new),
   then `extract`, `graph build`, and `dossier <subject> --new`. `--new` writes chunks only for pages the chapter's
   earlier chunks do not cover, numbered on from the old ones, so the first consolidation's files stay valid.
4. **Consolidate the new chunks.** Same passes as the first round, the same brief, one part file per chunk
   (`entries/draft/<chapter>.partNN.jsonl`), the gaps file `<chapter>.gaps.partNN.md`. The chapter's draft
   `entries/draft/<chapter>.jsonl` already exists: do not edit it. In each chunk:
   - **a new concept**: draft it as usual, only if no entry in `entries/draft/*.jsonl` has it (search the titles);
   - **more on an existing entry**: write the entry under the same title with only the new facts; `finalize --merge`
     adds them (the fact cap still applies);
   - **an entry the new sources change, or a thin one**: write it again in full under the same title with
     `"replaces": true`, citing everything it should rest on, old sentences and new, in the order of the answer. It
     takes the old entry's place, so a Worked example keeps one entry, and the `thin:` note goes with the old
     version. Set a new `thin:` note only if it is still thin;
   - **neither**: skip it.
   When you trim to a fact cap, put the dropped facts' sent_ids in `mention_sent_ids` so their sources are kept.
5. **Merge and check.** `finalize --check` each part file, then `finalize <subject> <chapter> --merge` per chapter,
   then `finalize <subject>` until it reports 0 problems, then `report gaps` again.

Never pad to reach a target. A chapter that stays short or thin after a gap-fill is reported, and its entry is
accepted as it is; the fix is a wider source list, not thinner entries.

## Reply
At most 150 words: new entries by kind and weight, entries extended or replaced, gaps still open, anything odd.
