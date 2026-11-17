# Pilot: Soil physics › Soil texture and structure

Step 4 of the build order: one mid-size chapter through every stage, to calibrate the guides against real dossiers
before scaling to the whole subject. Run on 2026-11-15.

## What ran

| Stage | Command | Result |
|---|---|---|
| Frame | `frame build`, then a hand review of this chapter | 22 forced pages (19 seeds + Soil texture, Clay, Soil physics as `also`) |
| Crawl | `crawl --chapter soil-texture-and-structure --depth 1 --max-pages 150` | 150 pages, 123 requests at 0.5 req/s |
| Extract, graph | `extract`, `graph build` | 15,876 sentences; 150 nodes, 2,939 edges, 1,170 RefD pairs |
| Dossier | `dossier soil-science soil-texture-and-structure` | 32 pages, 8 chunks |
| Consolidate | three parallel passes (`guides/CONSOLIDATION_GUIDE.md`), merge, `finalize` | 58 entries, 0 problems, 0 duplicates |
| Select | `select --chapter soil-texture-and-structure` | 57 selected (Mud excluded: it belongs to a sediment chapter) |
| Order | `order packet`, ordering pass, `order build`, hand review, `order lock` | 57 entries, 0 dropped edges, 0 cycles |
| Verify | `crawl --context` (tier A, 120 pages), `verify`, hand reviews | 110 DOIs, 2 NRCS authorities; 7 entries primary; 1 tier D fact |
| Write | two parallel passes (`guides/WRITING_GUIDE.md`), `write check` | 57 entries, 2 openers, 1 review; 0 problems, 0 warnings |
| Units | `units build`, question pass | 13 units (8 of 4, 5 of 5), 13 questions, 57 glossary terms |
| Images | `images` | 1 image (the USDA texture triangle, public domain) |
| Publish | `publish build`, `publish check` | 13 EPUBs of 13–55 KB, complete edition 81 KB; 0 problems |

Coverage of the chapter's hub articles: navbox 91%, index 92%, Vital 67%, Top/High 100%. The one article in no
entry is the Soil physics overview, which belongs to the part opener and the Foundations part.

## What the pilot changed

**Dossiers and the sentence index**
- The dossier kept only the first 45 sentences of each page, silently. It now keeps up to 80 per seed page (25 per
  assigned page), spread across sections, and marks every cut with the command that prints the rest. New commands:
  `sections` (a page's sections and sentence counts) and `page --section` (one section in full).
- Definitions were sometimes an infobox title ("Granulometry"). A definition is now the first lead sentence of six
  or more words that is not a table row.

**Consolidation**
- `finalize` now validates conflict sentence ids, and no longer gives section entries their page's Wikidata QID
  (they triggered false duplicates).
- The guide now covers split chapters (per-pass progress and gaps files), section anchors (the deepest heading),
  values that differ between standards (facts, not conflicts), apparent source errors (notes), entries without an
  article, and a material versus its property (two entries when the sources treat them separately).

**Ordering**
- An entry the ordering pass judged to need nothing must still be listed (`[]`); otherwise it falls back to
  automatic suggestions, which created false cycles.
- `order build` wrote its computed prerequisites back into the entries, and the next run read them as the
  consolidation's: a feedback loop. The consolidation's list now lives in `prerequisites_draft`.
- Section entries no longer stand for their whole page in the lead-link and RefD mapping, and count half their
  page's importance when breaking ties; weight breaks ties too.

**Writing**
- Every entry title is a glossary term, and `publish check` fails when a term appears before its unit. The guide
  now says to use `{{ref:id}}` for any forward mention (it renders with the unit number). Writers found forward
  references read best at the end of a sentence.

**Verification**
- Number matching near a key term produced false `supports` (a "40 %" from another texture class) and false
  `differs`. Each verdict now carries the authority sentence it came from, `reports/verification.md` lists
  automatic supports for spot-checking, and the pilot's 17 checks are recorded by hand in `verify/reviews.json`.
- PDF authorities are read with pypdf; the NRCS Soil Survey Manual (chapter 3) and the soil survey glossary are
  live. Soil Taxonomy, the WRB and SoilGrids are registered but have no fetcher yet.

**Images**
- A section entry took its page's lead image (the Leaning Tower of Pisa for a USCS section of Soil mechanics). It
  now takes the first image inside its own section, or none.

## Source oddities the passes noticed
- The USCS table on Wikipedia has the W/P meanings reversed in one place; the writer ignored it.
- One Expansive clay sentence groups kaolinite with the clays that swell most, against the page's other facts; left
  out.
- Coarse-grained USCS limits appear as `Cu ≥ 4, 1 ≤ Cc ≤ 3` in one place and with strict inequalities in another;
  the writer followed the USCS groups entry.

## Open points for the owner
- **Weight mix**: Landmark 2%, Major 46%, Minor 53%. The chapter's landmark concepts (Soil texture, Clay) sit in
  Foundations, so this chapter skews Major. Decide whether that is right before the full run.
- **Same-unit prerequisites**: 18 entries share a unit with a prerequisite that comes just before them (Atterberg
  limits, then each limit). `publish check` treats that as a warning, not a failure.
- **Length and voice**: entries run 40–290 words; read the 13 units on the devices and say whether the length and
  the voice are right. That is the cheapest moment to change the writing guide.
