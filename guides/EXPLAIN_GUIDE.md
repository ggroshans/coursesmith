# Explain guide: the scout pass

Only for a subject whose `subject.yaml` has an `explain:` block. You read the course's entries and name the
background each one **assumes the reader already has**, so the course can teach it in place. You write nothing a
reader sees. The writers later explain from the pages you name, never from memory.

## Inputs
- `subjects/<subject>/work/explain/packet-NNN.md` (`coursesmith explain packet <subject>`): 60 entries each, with the
  reader (`Reader:` line, and `Reader especially wants:` if the subject sets a focus) and per entry its definition
  and first facts.

## Output
`subjects/<subject>/work/explain/assumes.NNN.json`, one per packet:

```json
{"assumes": {"dotnet-core-0123": ["Dependency injection", "Inversion of control"],
             "dotnet-core-0124": ["Garbage collection (computer science)"]}}
```

Each phrase is a **Wikipedia article title or a short search phrase** (2 to 5 words) that finds one. At most the
number the packet says per entry. Leave an entry out when it assumes nothing.

## What to name
Ask of each entry: *what would a reader like the one in the `Reader:` line need to already know to follow this, and
not yet know?* Good picks:
- a concept or mechanism the entry leans on without explaining ("garbage collection", "public-key cryptography");
- a protocol, standard, algorithm or technology it takes for granted ("HTTP", "JSON", "OAuth");
- a piece of history, an organization or a person the entry's point depends on.

Choose the ones that most deepen understanding, not trivia. Prefer the **general concept** over the product's own
name: "Dependency injection", not "Microsoft.Extensions.DependencyInjection".

## What to skip
- The entry's own subject (its title) and anything the entry itself defines in its facts.
- Household words and anything the `Reader:` line says the reader already knows.
- Version numbers, product names with no encyclopedia article, code identifiers (class and method names).
- Anything you are unsure exists on Wikipedia. A wrong page is worse than none.
- Topics that are plainly other entries of this course. The engine drops a phrase that resolves to a course
  entry's article and tells the writer to link to that entry instead, so naming it costs nothing but wastes a slot.

## After you
`coursesmith explain resolve <subject>` looks each phrase up, skips disambiguation pages, fetches the pages and
writes `explain/background.json` and `reports/explain.md`. **Read the report**: it shows which page each phrase
became. Fix a wrong hit in `work/explain/pages.json` (`{"phrase": "Page title"}`) and run `resolve` again.

Reply in at most 60 words: packets read, phrases named, anything odd.
