# consensus-ordering-and-distributed-trans gaps (pass b14, chunks 1-4)

Concepts expected but with no (or too few) sentences in this chapter:
- Leader election (Wikipedia "Leader election"): only fragments in Paxos, Raft and the distributed-lock guide.
- Quorum (Wikipedia "Quorum (distributed computing)"): used by Paxos, Raft and heartbeat entries as a prerequisite, never defined.
- Byzantine fault tolerance / Byzantine generals problem (Wikipedia "Byzantine fault"; "Practical Byzantine fault tolerance").
- Write-ahead logging (Wikipedia "Write-ahead logging"): two-phase commit relies on it.
- Compensating transaction (Wikipedia "Compensating transaction") and the saga pattern in more depth.
- Distributed lock details: fencing tokens, lock leases, Redlock, Apache ZooKeeper, etcd, Chubby paper (Burrows 2006).
- Failure detectors (phi accrual, gossip-based detection): the heartbeat guide is the only source.
- Happened-before / logical clock as its own page (Wikipedia "Happened-before", "Logical clock").
- Atomic broadcast (named as a consensus application; no page crawled).
- Two Generals' problem; CAP-style trade-offs between consensus and availability (belongs with the consistency chapters).

Pages with nothing usable:
- gh>ByteByteGoHq/.../top-7-most-used-distributed-system-patterns.md has only a bullet list of pattern names (Ambassador, Circuit Breaker, Event Sourcing, Leader Election, Publisher/Subscriber) and no explanatory sentences, so no entry.

Left out on purpose (not system-design material for this course):
- Consensus page: Consensus number / Herlihy's hierarchy (shared-memory objects), the Equivalency of agreement problems section, Phase King algorithm, the protocol comparison table, lockstep consensus in games.
- Lamport timestamp page: the "Alternatives to potential causality" (information protocols) section.
- Paxos page: Generalized Paxos, Byzantine Paxos message flows, RDMA adaptation, optimisations list.
- Raft page: production-use list beyond etcd, CockroachDB and MongoDB.

Odd things for verification:
- Consensus page S:535feb8e8bd4 calls Paxos and Raft "typically synchronous"; not used, since Paxos is described elsewhere as safe in asynchronous systems.
- Message-delay counts differ by measuring point: Multi-Paxos "4 delays to 2" proposal-to-learning (S:a9d37aae4cda) versus Basic Paxos 3 delays client-to-learner (S:fcf452f70cca). Both kept as stated.
- "Lamport timestamp" and "Paxos" are drafted twice on purpose (chunks 2/4 and 3/4) so the paper abstracts merge into them at fold time.
