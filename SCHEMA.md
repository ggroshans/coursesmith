# Data schema

Everything a subject owns lives under `subjects/<slug>/`; the page cache under `cache/` is shared by all subjects
and gitignored; `build/` (EPUBs) is gitignored and rebuildable.

## Shared cache (`cache/`, gitignored)
- `raw/<slug>__<revid>.json`, one per page revision: `title`, `url`, `revid`, `pageid`, `fetched_at`, `html`,
  `links` (API link list), `body_links` (article links in body order), `lead_links` (article links in the lead),
  `categories`, `hidden_categories`, `sections` (`level`, `line`, `anchor`), `templates`, `citations`,
  `requested_title`. Citations: `{"n", "note_id", "kind": "citation|note|empty", "text", "works": [{doi, title,
  container, year, first_author, genre, pmid, bibcode, url, via}]}`.
- `text/<slug>__<revid>.txt`: cleaned text. Headings as `## ` lines, table rows pipe-separated, footnote markers
  `[^n]` in place, references/navboxes/See also dropped.
- `pages.json`: canonical title -> `{revid, stem}` of the current revision. A refresh writes the new revision next
  to the old one and repoints this index.
- `aliases.json` (requested -> canonical title), `link_meta.json` (title -> `categories`, `description`,
  `disambig`, `missing`, `qid`), `hubs/` (navbox, index, Vital, WikiProject and category-tree reads).
- `sentences.sqlite`: `pages(title, url, revid, qid, definition_id, n_sentences)`,
  `sentences(sent_id, title, revid, section, idx, sentence, is_row, is_lead, cites, dois, tags, links, cite_years,
  dates)`, `subject_pages(subject, title)`. **`sent_id` = sha1(title + "\n" + sentence)[:12]**, the chronicle's
  formula, so unchanged sentences keep their ids across refreshes and subjects.
- `works/<doi>.json` (metadata and abstract only), `http/` (authority pages), `images/` (dithered entry images),
  `contact.txt` (User-Agent contact).

## Subject files
| File | Written by | What |
|---|---|---|
| `subject.yaml` | hand | seeds, hubs, categories, scope rules, targets, ordering strategy, edition flags, verification registry, frame hints |
| `frame.yaml` | `frame build`, then hand | the reviewed TOC: parts -> chapters (`key`, `title`, `seeds`, `also`, `candidates`, `share`, and `target` only when `targets.entries` is set). Chronological subjects carry an `outline:` tree instead |
| `scope/hubs.json` | `frame build` | category distances, navbox/index/Vital lists, WikiProject importance, forced titles |
| `scope/calibration.csv` | `frame build`, hand | borderline titles: `title, score, reasons, description, suggested, label` (`label` = owner's in/out) |
| `scope/tuned.json` | `scope tune` | threshold fitted to the labels (F1, precision, recall) |
| `ledger.csv` | `crawl` | every page visit: `title, url, revid, depth, linked_from, in_scope_reason, score, status` |
| `scope/frontier_review.csv`, `scope/frontier_rejected.csv` | `crawl` | borderline and rejected links |
| `work/graph.json` | `graph build` | nodes (importance, difficulty, chapter, lead links, QID), weighted edges, RefD pairs |
| `work/dossiers/<chapter>/chunk_NN.md` | `dossier` | consolidation input |
| `entries/draft/<chapter>.jsonl` | consolidation passes | draft entries |
| `entries/<chapter>.jsonl` | `finalize`, then `select`, `order`, `verify`, `units build` | final entries |
| `work/order/prereqs.NN.json` | ordering pass | `{"entries": {id: [{"id", "reason"}]}}` |
| `order.json` | `order build`, `order lock` | `{strategy, locked, locked_at, order: [ids]}` |
| `output/curriculum.md` | `order build` | full TOC with every entry; reordered by hand before `order lock` |
| `verify/reviews.json`, `verify/external.json` | verification pass | hand verdicts; tier D facts |
| `work/write/packet-<part>.md`, `questions-packet.md` | `write skeleton`, `write questions` | writer input |
| `work/write/fill.*.json` | writing passes | prose batches (see below) |
| `output/prose.json`, `output/course.md` | `write render` | merged prose; the whole course as Markdown |
| `units.json`, `glossary.json` | `units build` | units and the cumulative glossary |
| `reports/*.md` | most stages | frame, coverage, duplicates, selection, order, verification |
| `waivers.json` | hand | checked false alarms for `publish check`, each with a reason |
| `STATE.md` | every session | where the subject stands and the next step |

## Entry (`entries/<chapter>.jsonl`)
```json
{"id": "soil-chem-014", "title": "Cation exchange capacity",
 "kind": "Concept", "weight": "Major", "level": "Intermediate",
 "part": "Soil chemistry", "chapter": "Charge and nutrient holding",
 "article": "Cation-exchange capacity", "qid": "Q898477",
 "definition": {"text": "...", "sent_ids": ["..."]},
 "facts": [{"text": "...", "sent_ids": ["..."]}],
 "prerequisites": ["soil-phys-003", "soil-chem-006"], "prerequisite_sources": {"soil-chem-006": "ordering pass"},
 "related": ["soil-fert-002"],
 "sources": [{"title": "...", "url": "...", "revid": 0, "sent_ids": ["..."]}],
 "events": [{"date_text": "1975", "date_ma": null, "sent_ids": ["..."]}],
 "contested": false, "contested_note": null, "conflicts": [], "flags": [], "curriculum": ["own article"],
 "score": 0, "score_parts": {}, "selected": true, "unit": 118, "position": 3,
 "verification": [], "external": [], "source_tier": "wikipedia", "image": null}
```
- **id**: `<short>-<part key>-<nnn>`, assigned by `finalize`, kept by title (or article + chapter) across runs,
  and **never changed after `order lock`**. Prose, prerequisites and the glossary refer to ids.
- **kind**: Concept, Process, Classification, Method, Material, Practice, Event, Person/Institution, Debate.
- **weight**: Landmark / Major / Minor, roughly 10 / 35 / 55 %. **level**: Foundational / Intermediate / Advanced.
- **curriculum**: tests passed (own article, own section, hub list, Top/High importance, mentioned on 2+ pages,
  prerequisite of 2+).
- **flags**: `citation_needed`, `contested`, `conflict`. Flagged entries are verified even when not selected.
- **verification**: `{doi | source, title, year, venue, verdict, matched, reviewed_verdict, note}`; verdict one of
  `supports`, `refines`, `differs`, `no comparable claim`, `no abstract`, `not found`.
- **external** (tier D): `{source, url, retrieved, text}`, shown as `+ <source>` in the tag line.
- **source_tier**: `primary` (a cited paper or an authority supports the key claim), `wikipedia`.
- **image**: `{file, license, license_url, artist, page_url, local, caption}`; only CC BY(-SA), CC0 or public domain.
- Chronological subjects add `date_display`, `date_ma`, `date_young_ma`, `uncertainty_ma`, `date_unit`,
  `date_qualifier`, a `path` of outline node ids, `branch` (the chronicle's type) and `origin`.

## Prose batches (`work/write/fill.*.json`)
```json
{"entries":   {"<id>": {"title": "...", "text": "..."}},
 "openers":   {"<outline node id>": "..."},
 "reviews":   {"<outline node id>": "..."},
 "glossary":  {"<id>": [{"term": "...", "text": "...", "sent_ids": ["..."]}]},
 "questions": {"<first entry id of the unit>": {"q": "...", "a": "...", "sent_ids": ["..."]}},
 "closing":   "..."}
```
Merged in file-name order, later files win. `{{ref:<id>}}` in a text renders as that entry's title and unit number.

## Units (`units.json`)
`{subject, built, n_units, n_entries, sizes, units: [{n, entries, path, leaf, openers, reviews, terms, question,
last_time, answer_prev, next}]}`. `glossary.json`: `{subject, terms: {term: {term, text, sent_ids, entry, unit}}}`.
