# gaps: the-cap-theorem-and-consistency (pass b13)

Concepts expected but with no (or too few) sentences in the dossier:
- Linearizability (page "Linearizability"): only two sentences inside Consistency model; the entry is thin.
- Network partition (page "Network partition"): linked from CAP theorem but not crawled.
- Vector clock and Lamport timestamps: named in one Eventual consistency sentence, pages not crawled.
- Conflict-free replicated data type (CRDT): one sentence in Eventual consistency.
- Quorum read/write settings (R + W > N, Dynamo-style tunable consistency): only a majority-vote sketch (N/2 + 1) in Consistency model.
- Read-after-write consistency and strong consistency as plain terms: only list items in Consistency model.
- Serializability and one-copy serializability: list items only; page not crawled.
- Brewer's "CAP Twelve Years Later" (the 2012 clarification): cited only as a quote in the ByteByteGo guide.
- Anti-entropy, read repair, gossip: one-line bullets in Eventual consistency; no page crawled.

Sections skipped on purpose (hardware memory models, no system-design teaching value): Consistency model "Weak memory consistency models" (weak ordering, release, entry, local, general), "Relaxed memory consistency models", "Transactional memory models", processor, PRAM, cache and slow consistency, and the local-write and cache-coherence protocols. "Continuous consistency" (conits) was not drafted: sources give mostly diagram-dependent detail.
Folded, not separate: Strict consistency (a fact in Consistency model), Partition tolerance (a fact in CAP theorem), BASE (a fact in Eventual consistency; another pass owns "BASE consistency model"), Singh's PACELC chapter (cited in PACELC), the Gilbert and Lynch paper (cited in CAP theorem).
