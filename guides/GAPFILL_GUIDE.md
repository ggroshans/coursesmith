# Gap-fill guide

Read `CONSOLIDATION_GUIDE.md` first: its rules all apply. This addendum covers a second pass over a chapter after
`report coverage` (or a consolidation pass's gaps file) showed missing concepts.

## The loop
1. **Pick the gaps.** From `reports/coverage.md` (hub articles not crawled, crawled but in no entry, thin
   chapters) and `entries/draft/<chapter key>.gaps.md`.
2. **Crawl them.** Add the page titles (or, for another source, its keys such as `gh>owner/repo/path.md`) to the
   chapter's `seeds` in `frame.yaml` (or `candidates` if they are only context). A key must be inside a source's
   allowlist in `subject.yaml`; if it is not, the crawl skips it and says so, and widening the allowlist is the
   owner's decision after `coursesmith sources check`. Then run `coursesmith crawl <subject> --chapter <key> --depth 0` to fetch just those pages, followed by
   `extract`, `graph build` and `dossier <subject> <key>`.
3. **Consolidate the new material** into the chapter's existing draft, `entries/draft/<chapter key>.jsonl`:
   - **a new entry**: append it, in the usual schema;
   - **more on an existing entry**: edit that entry in place (add facts, a better definition, sources), keeping
     its `title` unchanged. `finalize` matches entries by title (or by article and chapter), so the entry keeps
     its id;
   - **neither**: skip it.
4. Respect the fact limits (8 for Landmark and Major, 4 for Minor). When you trim, move the dropped facts'
   sent_ids into `mention_sent_ids` so their sources are kept.
5. Run `coursesmith finalize <subject> <chapter key>` until it reports 0 problems, then `report coverage` again.

Never pad to reach a target. A chapter that stays short after a gap-fill is reported in the reply; the fix is a
wider frame, not thinner entries.

## Reply
At most 150 words: new entries by kind and weight, entries extended, gaps still open, anything odd.
