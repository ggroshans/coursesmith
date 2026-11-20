# Output: using a built course

A finished subject can be used three ways:

- **`output/course.json`** (`coursesmith export <subject>`): the whole course in one file, for any renderer.
  This is the file to build on.
- **EPUBs** (`coursesmith publish build <subject>`): one per unit plus the complete course, in `build/epubs/<slug>/`.
- **The subject's own files** (`entries/*.jsonl`, `order.json`, `units.json`, `glossary.json`,
  `output/prose.json`), documented in `SCHEMA.md`. Read these if you are changing the course, not just showing it.

The finished courses in [coursesmith-courses](https://github.com/ggroshans/coursesmith-courses) ship with `course.json` already exported.

## `course.json`

```jsonc
{
  "format": "wikicourse-course", "version": 2, "built": "2026-11-17T15:24Z", "wikicourse": "0.2.0",
  "subject": {"slug": "soil-science", "title": "Soil Science", "description": "...",
              "ordering": "pedagogical", "per_unit": [4, 5],
              "distribution": "personal", "course_type": "survey", "kinds": ["Concept", "Process", "..."]},
  "license": {"name": "CC BY-SA 4.0", "url": "...", "text": "...",
              "pages":  {"Soil": {"url": "...", "revid": 1234, "permalink": "...&oldid=1234",
                                   "name": "Soil", "source": "wikipedia", "version": "1234",
                                   "version_label": "revision 1234", "license": "CC BY-SA 4.0",
                                   "license_class": "cc-by-sa", "tier": "reference"}},
              "sources": [{"key": "Soil", "name": "Soil", "source": "wikipedia", "url": "...", "revid": 1234,
                           "permalink": "...", "version": "1234", "version_label": "revision 1234",
                           "license": "CC BY-SA 4.0", "license_class": "cc-by-sa", "tier": "reference",
                           "n_sentences": 14, "retrieved": null}],
              "images": {"soil-fert-099": {"file", "license", "license_url", "artist", "page_url"}}},
  "outline": [{"id": "found", "title": "Foundations", "level": 1, "parent": null},
              {"id": "what-soil-is", "title": "What soil is", "level": 2, "parent": "found"}],
  "openers": {"<outline id>": "a few sentences opening a part or chapter"},
  "reviews": {"<outline id>": "a few sentences closing a chapter"},
  "closing": null,
  "entries": [ /* every selected entry, in reading order (below) */ ],
  "units":   [{"n": 1, "entries": ["soil-found-077", "..."], "path": ["found", "what-soil-is"],
               "openers": ["found", "what-soil-is"], "reviews": [], "terms": ["soil", "pedology"],
               "question": {"q": "...", "a": "...", "sent_ids": ["..."]},
               "last_time": "...", "answer_prev": "...", "next": "..."}],
  "glossary":  {"pedology": {"term": "Pedology", "text": "...", "sent_ids": ["..."], "entry": "soil-found-090", "unit": 1}},
  "questions": {"<first entry id of a unit>": {"q": "...", "a": "...", "sent_ids": ["..."]}},
  "sentences": {"03e8d020acfc": {"title": "Soil science", "url": "...", "revid": 1234,
                                  "section": "Fields of study", "sentence": "the cited sentence",
                                  "key": "Soil science", "source": "wikipedia", "version": "1234"}},
  "missing_sentences": []
}
```

### Entries

`entries` is the course in reading order, foundational to advanced (or by time for a chronological subject).

| Field | Meaning |
|---|---|
| `id` | stable handle, never changes once the order is locked; `{{ref:id}}` in any text points here |
| `title`, `text` | the written entry; `text` keeps `{{ref:id}}` markers for linking |
| `text_plain` | the same text with each marker replaced by the entry's title |
| `path` | outline ids from part to chapter (or eon to age) |
| `part`, `chapter`, `level`, `kind`, `weight` | Foundational / Intermediate / Advanced; Concept, Process, Method...; Landmark / Major / Minor |
| `definition`, `facts` | `{text, sent_ids}`: what the prose was written from, each fact citing sentences |
| `prerequisites`, `related` | entry ids: what this builds on (always earlier), and see-also links |
| `sources` | the pages the entry cites: `title` (human name), `key`, `url`, `revid`, `version`, `source`, `license`, `sent_ids` |
| `unit`, `position` | which unit it falls in, and where |
| `source_tier`, `verification`, `external` | `primary` when an outside source confirms the key claim, `wikipedia` for an entry citing only Wikipedia, else the best tier among its sources (`official`, `standard`, `reference`, `curated`, `commentary`); the checks; facts added from authorities |
| `image` | Commons image record (`file`, `license`, `artist`, `caption`, `local`), when the subject uses images |
| `events`, `date_display` | dated events (chronological subjects) |

Every `sent_ids` value is a key of `sentences`, so any fact can show the exact sentence it came from and a
permalink to the revision it was read in.

## Recipes

- **Web app or static site.** Walk `outline` for the table of contents; render `entries` in order, grouped by
  `path`. Replace `{{ref:id}}` in `text` with a link to `#id`. Show each fact's sentences on demand from
  `sentences`. Put `license.text` and the `license.pages` list on a sources page.
- **Daily lessons.** Use `units`: each holds 4–5 entry ids, the openers and reviews to show with them, the
  terms it defines, a question, and ready-made "last time" and "next" lines.
- **Flashcards.** One card per `glossary` term (front: `term`, back: `text`), one per entry (front: `title`,
  back: `definition.text`), and one per unit `question` (`q` / `a`). Each card can cite its `sent_ids`.
- **Search or retrieval.** Index `text_plain` per entry with `path` and `level` as filters; `sentences` gives
  the source passages behind every answer.
- **Your own EPUB or print layout.** `coursesmith publish build` already makes one; `coursesmith/publish/edition.py`
  shows how units, openers, reviews and attribution are laid out.

## License duty

The code is MIT; the content is not. A course built only from Wikipedia is **CC BY-SA 4.0**: anything you
publish from it must credit Wikipedia (the `license.pages` list is that credit), link the license, and be shared
under the same terms. A course that cites other sources says so in `license.name`, and `license.sources` lists
every page with its source, version and license; keep that credit and respect each license. If any cited source
forbids redistribution or derivatives (a NonCommercial or NoDerivatives license), `license.name` reads "Personal
use only (mixed sources)" and the course is for your own reading: set `distribution: public` in subject.yaml to
make `publish check` refuse such a source in the first place. Images carry their own Commons licenses in
`license.images`. See `NOTICE.md`.
