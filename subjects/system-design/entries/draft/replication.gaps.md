# gaps: replication (pass b11)

Concepts expected but with no (or too few) sentences in the dossier:
- Leaderless replication (Dynamo-style), quorum reads and writes: only named as the third approach in "Replication (computing)#Database replication"; suggested pages: Dynamo (storage system), Quorum (distributed computing), Eventual consistency.
- Failover (Failover page not crawled); leader election; split brain.
- Replication factor and replica placement (rack or region awareness): no sentences.
- Read-your-writes, monotonic reads and other session guarantees beyond ByteByteGo's "read-after-write": suggested page Consistency model.
- Hinted handoff, anti-entropy and read repair, vector clocks, CRDTs (BDR mention only): no sentences here.
- Geo-replication and cross-region replication: only one multi-data-center sentence.
- Singh's database replication page is short; it has no sentences on replication lag mechanics beyond one bullet.

Skipped on purpose: the long implementation list in "Multi-master replication" (Active Directory, OpenDJ, CouchDB, Aurora, MySQL/MariaDB, PostgreSQL BDR, Ingres and others) is product and version detail, not teaching; no product entries were drafted from it (CouchDB's MVCC-based HTTP replication and Aurora's writer and storage nodes could feed a case study if wanted). Also skipped: "Replication within file", "Distributed shared memory replication", file-system journal replication, and the dated PostgreSQL BDR history.

# gaps: replication (gap-fill gf10, chunks 03-05)
- Operational transformation: named as the alternative to sequence CRDTs; no entry yet (suggested page: Operational transformation).
- PostgreSQL streaming replication, replication slots, cascading and synchronous replication (sections 26.2.5 to 26.2.9) and the hot standby page: only table-of-contents lines crawled; suggested pages doc>www.postgresql.org/docs/current/warm-standby.html sub-sections or hot-standby.html.
- PostgreSQL logical replication details (row filters, conflicts, failover) are only headings in the corpus.
- Hinted handoff, sloppy quorum, Merkle-tree anti-entropy: one table row each on the Dynamo page; suggested pages: Merkle tree, Hinted handoff.
- Bully algorithm, ZooKeeper-style election, lease-based leadership: no sentences.
- Skipped on purpose: ring, mesh, hypercube and radio-network leader election algorithms (kept to the symmetry idea, Chang and Roberts, consensus); split-horizon DNS; CRDT industry-use list; epidemic-paper abstract is OCR-garbled.
