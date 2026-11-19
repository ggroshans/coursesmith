# Soil Science — state

_Update after every step. `coursesmith status soil-science` prints the live numbers._

## Where it stands (2026-11-16)
- **Build order:** steps 1–9 run, then a discovery round (`docs/DISCOVERY_DESIGN.md`) that widened the course to
  every branch of the field. The course runs as long as its material does: no unit cap, no entry target.
- **Frame:** 12 parts, 50 chapters. Reviewed 2026-11-16 by the build session standing in for the owner. The
  discovery round added a part (Studying soil: methods and mapping: lab methods, micromorphology, pedometrics) and
  ten chapters elsewhere: soil geography, solute transport, soil mineralogy, soil solution chemistry and sorption,
  soil biochemistry, urban and human-made soils, soils and human health, paleopedology and soil dating, forensic and
  archaeological soil science. A forest and rangeland chapter was tried and dissolved (four entries). Re-review
  freely.
- **Scope:** keyword score (threshold 4, F1 0.59 on the calibration set) plus the scope judge (`scope/judge.json`:
  5,923 borderline pages, 160 in, 191 support; F1 0.75 on the calibration set). Ten pages the judge ruled out were
  kept as core pages of new chapters.
- **Syllabus:** `scope/syllabus.json`, 50 branches and 749 concepts from the planner pass; `reports/syllabus.md`
  shows which are covered, which became entries, and the 144 Wikipedia has no page or sentences for.
- **Crawl:** about 6,000 pages: the frame crawl, every hub-list page, the judged and syllabus pages, two gap-fill
  rounds and tier A context. 443 pages were re-cleaned after the powers-of-ten fix (`reclean`).
- **Entries:** 2,314 final, 2,274 selected (Landmark 102, Major 758, Minor 1,414).
- **Order:** locked, 2,274 entries; ordering passes cover every entry; 298 forward edges became `related`.
- **Verification:** OpenAlex/Crossref on 4,855 DOIs, four live authorities. Worklist reviewed (`verify/reviews.json`);
  90 entries primary; no genuine conflicts.
- **Units:** 505 units of 4–5 entries, one question each.

## Next steps
1. Read the first units (`build/epubs/soil-science/`, or `coursesmith export soil-science`).
2. Decide the unit size (`targets.per_unit`), then `units build`, `write questions` + a question pass,
   `publish build`.
3. Re-review the frame and the curriculum (`output/curriculum.md`), especially the new chapters; ids are frozen, so
   moves only change part/chapter and order.

## Notes
- `waivers.json` waives about 120 everyday words, plain phrases and personal names that are also entry titles
  (erosion, rock, groundwater, tropical soils, Charles Darwin...); technical terms always carry a forward reference.
- Possible misreadings flagged for review: soil-env-110 (20–40% of soil carbon lasting over 100 years vs Trumbore
  1997's "centuries or less"); soil-hist-113 (the Dokuchaev–Sibirtsev school "from 1870", when Sibirtsev was ten);
  the NBPT dose (0.5% on its own page, 0.05% on Controlled-release fertiliser), recorded as a conflict.
- Several entries carry event dates (from their `events`) that no fact states; writers left them out of the prose.
- Charles E. Kellogg (US soil survey chief) has no Wikipedia article; "Charles Kellogg (naturalist)" is a vaudeville
  performer and is excluded.
- Concepts with no Wikipedia page or sentences (Land evaluation, Soil association, Epipedon as a whole, soil fabric
  and others) are listed in `reports/syllabus.md` and `entries/draft/*.gaps.md`.

## Upgrade pass (2026-11-19)
Rebuilt on the current process, in place: vetted outside sources (WRB 2022 PDF; four CC BY / CC BY-NC LibreTexts books: two
lab manuals, Building Soils for Better Crops, Digging into Canadian Soils), a gap-fill round (27 unresolved concepts
seeded, 187 pages crawled), and consolidation of every page no entry rested on yet. Entries 2,314 -> 2,760 (2,629 selected);
units 505 -> 584; ids unchanged, order re-built stable (old entries keep their relative order). 393 entries written
(354 new, 39 with new facts), 12 figures, 259 new questions, `write check` 0 problems, `publish check` 0 problems.
- `distribution: personal` (two NonCommercial books).
- Not used: Soils4Africa DSM manual (page would not fetch), Predictive Soil Mapping (.Rmd not read by the github adapter),
  USDA NRCS Keys/Survey Manual (no license readable).
- Many new Wikipedia-only entries from the earlier crawl are generic supporting topics (physics, statistics); selection
  kept them. Open duplicate warnings (38) are same-page section entries, left as distinct.
