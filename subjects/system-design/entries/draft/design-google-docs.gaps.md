# design-google-docs gaps (b28)
- Chapter is thin: one guide of about eleven sentences, no requirements, scale, data model or API.
- Operational transformation (OT): Wikipedia "Operational transformation".
- Conflict-free replicated data type (CRDT): Wikipedia "Conflict-free replicated data type".
- Differential synchronization (DS): Wikipedia "Differential synchronization" (or the Neil Fraser paper).
- Real-time collaborative editing in general (presence, cursors, version history, offline edits): Wikipedia "Collaborative real-time editor".

# gaps (design-google-docs, gap-fill chunk 02)
- Differential synchronization: no page crawled (Wikipedia has none under that title; Neil Fraser's paper is not a vetted source); only one mention sentence exists, so no entry and the Worked example says nothing on how it resolves conflicts
- Conflict-free replicated data type: named as a prerequisite; the page is seeded in the replication chapter (gap-fill chunk 04), which should draft it under that exact title
- Presence and cursors, version history, offline edits, permissions and sharing, scale estimates, document data model: no source sentences
- Total order broadcast (Fluid Framework): no page
