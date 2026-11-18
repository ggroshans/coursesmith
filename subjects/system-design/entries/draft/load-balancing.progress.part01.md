# load-balancing progress (pass p2)

Chunks done: 01 of 1 (chunk_01.md) -> load-balancing.part01.jsonl, 28 entries, `finalize --check` 0 problems.

Titles drafted (kind, weight, level):
- Load balancing (Concept, Landmark, Foundational)
- Load balancer (Concept, Major, Foundational)
- Load balancing algorithms (Classification, Major, Intermediate)
- Round robin (Method, Major, Foundational)
- Weighted round robin (Method, Minor, Intermediate)
- Least connections (Method, Minor, Intermediate)
- Least response time (Method, Minor, Intermediate)
- Hash-based load balancing (Method, Minor, Intermediate)
- Random load balancing (Method, Minor, Foundational)
- Static load balancing (Concept, Major, Intermediate)
- Dynamic load balancing (Concept, Major, Intermediate)
- Master-worker scheme (Method, Minor, Intermediate)
- Work stealing (Method, Minor, Advanced)
- Client-side load balancing (Method, Minor, Intermediate)
- DNS load balancing (Method, Minor, Intermediate)
- Load balancing by DNS delegation (Method, Minor, Advanced)
- Sticky sessions (Concept, Major, Intermediate)
- Externalized session state (Practice, Minor, Intermediate)
- Health checks (Process, Major, Intermediate)
- Failover (Concept, Major, Intermediate)
- Redundant load balancers (Practice, Minor, Intermediate)
- TLS termination (Method, Minor, Intermediate)
- Layer 4 and layer 7 load balancing (Classification, Major, Intermediate)
- Content-based routing (Classification, Minor, Intermediate)
- Types of load balancers (Classification, Major, Intermediate)
- Global server load balancing (Concept, Minor, Intermediate)
- Load balancer features (Concept, Minor, Intermediate)
- Data center network load balancing (Concept, Minor, Advanced)

Notes for the merge and verification passes:
- Article anchors (`Page#Section`) are not validated by `finalize --check`; each was matched by hand to a heading printed by `sections`.
- Entries with `article: null` (no own page or section, but on 2+ pages): Weighted round robin, Least connections,
  Least response time, Hash-based load balancing, Health checks, TLS termination, Global server load balancing.
- Sticky sessions and Externalized session state share the Wikipedia "Persistence" section; each lists the other in distinct_from.
- Conflict/odd: Wikipedia lists least connections under "Static load distribution" (24eb2aca1aae) against its own definition
  of static (c08acfe98f76); ByteByteGo files it as dynamic (8340a6800efe). Recorded in conflicts and notes on
  "Load balancing algorithms" and "Least connections".
- No entry is contested.
