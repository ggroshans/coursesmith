# Verification guide

Verification gives two things: the context Wikipedia itself provides, drilled link by link, and
confirmation or added context from verified external sources. The rule never changes: **no fact from general
knowledge.** Design: `docs/DESIGN.md`, section 2.

## The four tiers
| Tier | What | Command | Your part |
|---|---|---|---|
| A | Wikipedia in depth: every page linked from each selected entry's lead | `wikicourse crawl <subject> --context`, then `extract`, `graph build`, `dossier` | Use the new sentences when you extend entries (see `GAPFILL_GUIDE.md`) |
| B | Cited works: the DOIs behind each entry's sentences, title and abstract via OpenAlex (Crossref fallback) | `wikicourse verify <subject>` | Read every `differs` |
| C | Authorities registered in `subject.yaml` (`verification.authorities`) | same | Add fetchers one at a time; read every `differs` |
| D | Added context: a fact an authority or a peer-reviewed abstract has and Wikipedia lacks | `verify/external.json` | Write it, cite it |

`verify` writes each entry's `verification` list and its `source_tier`: **primary** when a cited paper or an
authority supports its key claim (`supports`, or `refines` = inside a stated range, or a hand-reviewed
`supports`); otherwise **wikipedia**. Verdicts: `supports`, `refines`, `differs`, `no comparable claim`,
`no abstract`, `not found`. The comparison reads numbers with units, pH values, dates, and, for Classification
entries checked against an authority, whether the authority lists the class.

## Reading the worklist
`verify` lists every entry with a `differs` and nothing supporting it in `subjects/<subject>/verify/worklist.md`.
For each one:
1. Look at the entry's facts and the sentences they cite (`wikicourse sent <subject> <id>`).
2. Read the abstract or authority text the verdict came from (the work's JSON is in `cache/works/`).
3. Decide what the difference is, and record it in `verify/reviews.json`:

```json
{"soil-phys-012": {"10.2136/sssaj1990.03615995005400030045x":
    {"reviewed_verdict": "different object", "note": "the paper gives the clay fraction of a single field soil"}}}
```

`reviewed_verdict` is one of `supports`, `different object`, `older estimate`, `different method`,
`genuine conflict`. Reviews are re-applied on every run.

4. A **genuine conflict** is mentioned in the prose in one plain sentence. The writer packet marks it as MUST
   MENTION.

## Adding an authority (tier C)
An authority is worth a fetcher only where entries make checkable claims. Add one at a time:

```yaml
verification:
  authorities:
    - name: USDA NRCS Soil Survey Manual
      kind: classification          # or numeric
      fetcher: text_reference       # fetch the pages once, cache them, compare
      urls: [https://...]           # stable pages of the authority itself
      kinds: [Classification, Concept]   # optional: which entry kinds it can judge
```

Authorities without `fetcher` and `urls` stay listed as pending in `reports/verification.md`. Use only the
authority's own pages, never a summary of it.

## Added context (tier D)
Where an authority page or a peer-reviewed abstract carries a fact the entry needs and Wikipedia lacks, add it to
`verify/external.json`:

```json
{"soil-phys-004": [{"source": "USDA NRCS", "url": "https://...", "retrieved": "2026-11-15",
                    "text": "Clay particles are smaller than 0.002 mm in diameter."}]}
```

- Authorities and peer-reviewed abstracts only. No blogs; no textbooks unless open access and citable by URL.
- The text paraphrases what the source says, at most 40 words, with no new interpretation.
- The tag line shows it as `+ USDA NRCS`, and the attribution page lists the URL.

## Finishing
Run `wikicourse verify <subject>` until the worklist holds only entries you have reviewed. Reply in at most 120
words: entries checked, tier counts, conflicts found, authorities still pending.
