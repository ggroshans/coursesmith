# Notice: code and content licenses

**Code.** Everything under `coursesmith/`, `tests/` and the guides in `guides/` is MIT-licensed (see `LICENSE`).

**Course content.** Everything under `subjects/` and every export the engine writes (`output/course.json`,
`output/course.md`, EPUBs) is derived from Wikipedia and is licensed under the
[Creative Commons Attribution-ShareAlike 4.0 License](https://creativecommons.org/licenses/by-sa/4.0/):

- `scope/*.csv`, `entries/draft/*.gaps.md`, `reports/*.md` and the exported `sentences` quote Wikipedia
  sentences verbatim;
- entry definitions and facts are close paraphrases of cited Wikipedia sentences, and the prose is written from
  those facts.

Attribution is by revision: every entry lists the Wikipedia pages and revision ids it draws on (`sources`), each
EPUB ends with a "Sources and license" page, and `course.json` carries a `license` block with every page, URL and
revision. If you publish anything built from this content, keep that attribution and share it under the same
license.

**Images.** Entry images come from Wikimedia Commons; each carries its own license (CC BY, CC BY-SA, CC0 or
public domain) and author in the entry's `image` record. Image files are not stored in this repository.

**External sources.** Facts marked as external (`external`, `+ USDA NRCS` in a tag line) are short quotations from
the named authority or a paper's abstract, cited by URL.

**Other sources.** A subject may cite sources besides Wikipedia (a GitHub repository, an RFC, a documentation
site, a PDF, a paper), listed under `sources:` in its `subject.yaml` after `coursesmith sources check` has read
each one's license from the source itself. Content derived from such a subject carries those sources' licenses,
not only CC BY-SA: its `course.json` `license.sources` and each EPUB's "Sources and license" page name every
page, version and license. Some sources (those under NonCommercial or NoDerivatives licenses, such as several
system-design guides and the Google SRE books) allow personal reading but not redistribution; a subject that cites
one is for personal use, and `distribution: public` in `subject.yaml` makes `publish check` refuse it.
`sources/registry.yaml` records, with the date and what was read, the licenses of the sources vetted so far.
