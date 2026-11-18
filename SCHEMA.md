# Data schema

Everything a subject owns lives under `subjects/<slug>/`; the page cache under `cache/` is shared by all subjects
and gitignored; `build/` (EPUBs) is gitignored and rebuildable.

## Page keys
Every page in the store, the sentence index and every subject file is named by a **key**. A Wikipedia page keeps its
bare title (so every id made before other sources existed is still valid). Any other source's page is
`<prefix>><id>`: `rfc>9110`, `gh>owner/repo/path/to/file.md`, `doc>redis.io/docs/latest/develop/foo`,
`pdf>source-name/file.pdf`, `paper>10.1145/1773912.1773922` (or `paper>arxiv:1706.03762`),
`wiki>en.wikibooks.org/Computer_Networks` (a MediaWiki other than the default). `>` cannot occur in a MediaWiki
title, so a key never collides with an article, and none of the characters the pipeline gives a meaning to
(`# | [ ] { }`) appear raw in an id: they are percent-encoded. An entry's `article` is a key, optionally with
`#Section`. See `coursesmith/sources/keys.py`.

## Shared cache (`cache/`, gitignored)
- `raw/<slug>__<revid or version>.json`, one per page version. Wikipedia: `title`, `url`, `revid`, `pageid`,
  `fetched_at`, `html`, `links` (API link list), `body_links` (article links in body order), `lead_links` (article
  links in the lead), `categories`, `hidden_categories`, `sections` (`level`, `line`, `anchor`), `templates`,
  `citations`, `requested_title`. Another source's record has the same link, category and citation fields plus
  `name` (the human title), `source` (its name in subject.yaml), `adapter`, `source_id`, `version` (a commit sha,
  a publication date, a content hash), `license` (`{name, url, class}`), `tier`, `retrieved`, `anchors` (anchor
  text -> key, for sentence links) and `meta` (`description`, `code_blocks`, `dates`, adapter details); `html` is
  null and `revid` is null. Citations: `{"n", "note_id", "kind": "citation|note|empty", "text", "works": [{doi,
  title, container, year, first_author, genre, pmid, bibcode, url, via}]}`; an RFC's or paper's bracketed
  references become the same shape.
- `text/<slug>__<revid or version>.txt`: cleaned text. Headings as `## ` lines, table rows pipe-separated,
  footnote markers `[^n]` in place, references/navboxes/See also dropped; code blocks are dropped and a literal
  pipe in prose becomes U+2223, so no sentence is read as a table row. `coursesmith/text/emit.py` writes it for
  every source; `crawl/clean.py` is the Wikipedia front end and its output must not change (every `sent_id`
  depends on it).
- `pages.json`: key -> `{revid, stem}` of the current version, plus `source` and `version` for another source's
  page. A refresh writes the new version next to the old one and repoints this index.
- `aliases.json` (requested -> canonical title), `link_meta.json` (title -> `categories`, `description`,
  `disambig`, `missing`, `qid`), `hubs/` (navbox, index, Vital, WikiProject and category-tree reads).
- `sentences.sqlite`: `pages(title, url, revid, qid, definition_id, n_sentences, source, version, license, name)`,
  `sentences(sent_id, title, revid, section, idx, sentence, is_row, is_lead, cites, dois, tags, links, cite_years,
  dates)`, `subject_pages(subject, title)`; `title` is the page key. The last four `pages` columns are added to an
  older database on first use. **`sent_id` = sha1(key + "\n" + sentence)[:12]**, the chronicle's formula (a
  Wikipedia key is its title), so unchanged sentences keep their ids across refreshes and subjects. Dates are
  only parsed for Wikipedia and for a source that sets `dates: true`; a page with no encyclopedia lead takes its
  first prose sentence as its definition.
- `works/<doi>.json` (metadata and abstract only), `http/` (authority pages), `images/` (dithered entry images),
  `contact.txt` (User-Agent contact).

## Subject files
| File | Written by | What |
|---|---|---|
| `subject.yaml` | hand | seeds, `sources:`, `distribution`, `course_type`, hubs, categories, scope rules, targets (units, word ranges, fact caps), ordering strategy, edition flags, verification registry and units, frame hints |
| `sources/registry.yaml` (repo root, shared) | hand | domains and GitHub repos vetted once: default tier and license (with where it was read and when) for each, and the license classes |
| `scope/sources.candidates.yaml` | `sources discover`, `sources merge`, hand | candidate sources with evidence, score and a ready `subject_yaml` snippet; set `status: accept` or `reject` |
| `scope/sources.ok` | `sources check` | stamp of the `sources:` block that last passed; `crawl` and `finalize` refuse to run without a current one |
| `reports/sources.md` | `sources check` | each source's declared license against the license read from the source, problems and notes |
| `work/sources/packet.md`, `work/sources/found.yaml` | `sources packet`, a web-search session | the brief and the session's findings (guides/SOURCES_GUIDE.md) |
| `frame.yaml` | `frame build`, then hand | the reviewed TOC: parts -> chapters (`key`, `title`, `seeds`, `also`, `candidates`, `share`, and `target` only when `targets.entries` is set). Chronological subjects carry an `outline:` tree instead |
| `scope/hubs.json` | `frame build` | category distances, navbox/index/Vital lists, WikiProject importance, forced titles |
| `scope/calibration.csv` | `frame build`, hand | borderline titles: `title, score, reasons, description, suggested, label` (`label` = your in/out) |
| `scope/tuned.json` | `scope tune` | threshold fitted to the labels (F1, precision, recall) |
| `ledger.csv` | `crawl` | every page visit: `title, url, revid, depth, linked_from, in_scope_reason, score, status` (`title` is the key; `revid` holds another source's version string) |
| `scope/frontier_review.csv`, `scope/frontier_rejected.csv` | `crawl` | borderline and rejected links |
| `work/graph.json` | `graph build` (gitignored, regenerable) | nodes (importance, difficulty, chapter, lead links, QID), weighted edges, RefD pairs |
| `work/dossiers/<chapter>/chunk_NN.md` | `dossier` (gitignored, regenerable) | consolidation input |
| `entries/draft/<chapter>.jsonl` | consolidation passes | draft entries |
| `entries/<chapter>.jsonl` | `finalize`, then `select`, `order`, `verify`, `units build` | final entries |
| `work/order/prereqs.NN.json` | ordering pass | `{"entries": {id: [{"id", "reason"}]}}` |
| `order.json` | `order build`, `order lock` | `{strategy, locked, locked_at, order: [ids]}` |
| `output/curriculum.md` | `order build` | full TOC with every entry; reordered by hand before `order lock` |
| `verify/reviews.json`, `verify/external.json` | verification pass | hand verdicts; tier D facts |
| `work/write/packet-<part>.md`, `questions-packet.md` | `write skeleton`, `write questions` (gitignored) | writer input |
| `work/write/fill.*.json` | writing passes | prose batches (see below) |
| `output/prose.json`, `output/course.md` | `write render` | merged prose; the whole course as Markdown. `course.md` is a reading draft: headings, openers, entry text and figures only. The tag line, chapter reviews, questions and glossary appear in the EPUBs and in `course.json`. Re-run `write render` after `figures` changes to refresh it |
| `units.json`, `glossary.json` | `units build` | units and the cumulative glossary |
| `output/course.json` | `export` | the whole course in one file for any renderer (see `docs/OUTPUT.md`) |
| `sentences.jsonl` | port | optional frozen copy of the cited sentences, for a subject not crawled by this engine (`export` falls back to it) |
| `scope/judge.json`, `scope/judge/batch-NN.json` | judge passes, `scope judge-merge` | in/support/out verdicts on borderline pages |
| `scope/syllabus.json`, `scope/syllabus_resolved.json` | planner pass, `frame resolve` | the planned branches and concepts, and what each resolved to |
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
 "sources": [{"title": "...", "url": "...", "revid": 0, "sent_ids": ["..."], "key": "...", "source": "wikipedia",
              "version": "0", "license": {"name": "CC BY 4.0", "class": "cc-by"}}],
 "events": [{"date_text": "1975", "date_ma": null, "sent_ids": ["..."]}],
 "contested": false, "contested_note": null, "conflicts": [], "flags": [], "curriculum": ["own article"],
 "score": 0, "score_parts": {}, "selected": true, "unit": 118, "position": 3,
 "verification": [], "external": [], "source_tier": "wikipedia", "image": null}
```
- **id**: `<short>-<part key>-<nnn>`, assigned by `finalize`, kept by title (or article + chapter) across runs,
  and **never changed after `order lock`**. Prose, prerequisites and the glossary refer to ids.
- **kind**: Concept, Process, Classification, Method, Material, Practice, Event, Person/Institution, Debate, and
  for question chapters Worked example (a question's answer; up to 16 facts, 250-600 words, paragraphs, never a
  glossary term, ordered last in its chapter) and Case study (150-400 words). `targets.fact_caps` and
  `targets.word_ranges` in subject.yaml change the limits.
- **sources**: one item per cited page. `title` is the page's human name (the article title for Wikipedia),
  `key` what the store and index know it by, `source` its name in subject.yaml, `version` a commit, date or hash,
  `license` as read from the source (omitted for Wikipedia). Items written before other sources existed lack the
  new fields; readers fill them in as Wikipedia.
- **weight**: Landmark / Major / Minor, roughly 10 / 35 / 55 %. **level**: Foundational / Intermediate / Advanced.
- **curriculum**: tests passed (own article, own section, hub list, Top/High importance, mentioned on 2+ pages,
  prerequisite of 2+, vetted source, question entry).
- **flags**: `citation_needed`, `contested`, `conflict`. Flagged entries are verified even when not selected.
- **verification**: `{doi | source, title, year, venue, verdict, matched, reviewed_verdict, note}`; verdict one of
  `supports`, `refines`, `differs`, `no comparable claim`, `no abstract`, `not found`.
- **external** (tier D): `{source, url, retrieved, text}`, shown as `+ <source>` in the tag line.
- **source_tier**: `primary` (a cited paper or an authority supports the key claim), `wikipedia` (cites only
  Wikipedia), else the best trust tier among the cited sources: `official`, `standard`, `reference`, `curated` or
  `commentary`. Tiers rank `official` > `standard` > `primary` > `reference` > `curated` > `commentary`; when
  sources disagree the higher tier's value is the fact and the other goes to `conflicts`
  (guides/CONSOLIDATION_GUIDE.md).
- **image**: `{file, license, license_url, artist, page_url, local, caption}`; only CC BY(-SA), CC0 or public domain.
- **figures** (in `subjects/<s>/figures.json`, keyed by entry id, not in the entry record; `course.json` carries
  them on each entry): a list of `{type, caption, sent_ids, ...}` with type `flow` (Mermaid flowchart subset),
  `cycle`, `layers`, `scale`, `bar`, `tree` or `table`; see the WRITING_GUIDE for each type's fields. Drawn at
  build time as grayscale PNG (tables as XHTML); every number in one must be in its entry's facts.
- Chronological subjects add `date_display`, `date_ma`, `date_young_ma`, `uncertainty_ma`, `date_unit`,
  `date_qualifier`, a `path` of outline node ids, `branch` (the chronicle's type) and `origin`.

## Prose batches (`work/write/fill.*.json`)
```json
{"entries":   {"<id>": {"title": "...", "text": "..."}},
 "openers":   {"<outline node id>": "..."},
 "reviews":   {"<outline node id>": "..."},
 "glossary":  {"<id>": [{"term": "...", "text": "...", "sent_ids": ["..."]}]},
 "questions": {"<first entry id of the unit>": {"q": "...", "a": "...", "sent_ids": ["..."]}},
 "derived":   {"<id>": [{"values": [386], "from": ["<sent_id>"], "expr": "1000000000 / (30 * 86400)", "reason": "..."}]},
 "closing":   "..."}
```
Merged in file-name order, later files win. `{{ref:<id>}}` in a text renders as that entry's title and unit number.
A text is one paragraph unless it is a Worked example or Case study, or the subject sets `edition.paragraphs: true`;
then a blank line (`\n\n`) in the text starts a new paragraph. `derived` declares arithmetic on an entry's own
numbers (a back-of-the-envelope figure); `publish/derived.py` recomputes it and a failing declaration waives
nothing. `waivers.json` takes the same under `derived`.

## Units (`units.json`)
`{subject, built, n_units, n_entries, sizes, units: [{n, entries, path, leaf, openers, reviews, terms, question,
last_time, answer_prev, next}]}`. `glossary.json`: `{subject, terms: {term: {term, text, sent_ids, entry, unit}}}`.
