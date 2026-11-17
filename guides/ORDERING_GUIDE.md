# Ordering guide

You name the **prerequisites** of every selected entry in a wikicourse subject, so the course can run from
foundational to advanced the way a good textbook does. The script does the sorting; your judgment supplies the
edges it sorts by.

## Why this pass exists
Three signals feed the order (`docs/DESIGN.md`, section 3):
- **RefD** (Liang et al., EMNLP 2015): B is a prerequisite of A when A's linked articles refer to B more than B's
  refer to A. Cheap, unsupervised, about 60–75% accurate.
- **Lead links**: articles linked from an entry's lead section.
- **This pass**: you read each entry's definition and pick its prerequisites from the entry list.

Where you have covered an entry, your choice is authoritative. Where you have not, the script falls back to lead
links that RefD also supports.

## Input
`subjects/<subject>/work/order/packet.md` (`wikicourse order packet <subject>`):
- the **entry list**: `id | title | part › chapter | level`;
- one block per entry: definition, what the consolidation pass suggested, lead links, RefD, and the script's
  current choice.

## Output
`subjects/<subject>/work/order/prereqs.NN.json`, one or more batch files, merged in name order (later files win per
entry):

```json
{"entries": {"soil-chem-014": [{"id": "soil-chem-006", "reason": "CEC is defined by the charge on clay minerals"},
                               {"id": "soil-found-007", "reason": "exchange depends on soil pH"}]}}
```

Write a batch every 50–80 entries. Make the JSON with Python (`json.dump`, `ensure_ascii=False`) or the Write tool.

## Rules
1. **3–5 prerequisites per entry**; fewer for Foundational entries (often none), never more than 5. **List every
   entry you have judged**, with `[]` when it needs nothing: an entry missing from your batches falls back to the
   automatic suggestions, which can create cycles.
2. **A prerequisite is something the reader must understand first to follow this entry's definition and facts.**
   Not merely related, not an example, not a later application. "Clay" is a prerequisite of "Cation exchange
   capacity"; "Fertilizer" is not.
3. **Pick only from the entry list**, by id. Never invent concepts.
4. **Point backward or sideways in the frame.** Prefer prerequisites in the same chapter, an earlier chapter, or the
   Foundations part. An edge to a later chapter or part is dropped by the script (it moves to `related` and is
   listed in `reports/order.md`), so name one only when it is genuinely needed; the curriculum review then decides
   whether to move an entry.
5. **No cycles.** If A needs B and B seems to need A, choose the one that is truly more basic.
6. **One line of reason each**, from the definitions and facts in the packet, never from outside knowledge.
7. Use the suggestions as hints, not answers: RefD and lead links are often right about direction and often wrong
   about relevance.

## Finishing
1. Run `wikicourse order build <subject>`; read `reports/order.md` (dropped edges, broken cycles) and
   `output/curriculum.md` (the full table of contents).
2. Fix what reads wrong by editing your batch files and re-running, or leave a note for the owner's curriculum
   review. **Do not run `order lock`**: the owner locks the order after reading `curriculum.md`.
3. Reply in at most 120 words: entries covered, edges written, dropped edges and cycles, anything the curriculum
   review should look at first.
