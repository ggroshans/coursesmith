- Cache invalidation (no Wikipedia page crawled; Singh and ByteByteGo cover it)
- Cache coherence (page `Cache coherence`)
- Locality of reference (page `Locality of reference`)
- Memoization (page `Memoization`)
- CPU cache (page `CPU cache`)
- Page cache (page `Page cache`)
- Adaptive replacement cache (page `Adaptive replacement cache`)
- Distributed cache (page `Distributed cache`)
- Time to live (page `Time to live`)
- Read-through cache (only one ByteByteGo tradeoffs sentence; page `Cache (computing)` has no section on it)
- Refresh-ahead caching (primer lists the name only; main primer README `Cache` section not crawled)
- Cache-aside explanation (primer main README; only names and the Mint/query-cache steps are crawled)
- Query-level versus object-level caching (primer talking-point names only)
- Cache warming and cold-start cache (no source; Singh uses hot/warm/cold in a non-standard sense)
- Consistent hashing for cache clusters (page `Consistent hashing` is crawled but belongs to another chapter)
- Cache-control and HTTP cache validation (owned by the http chapter; rfc>9111 is crawled)

# caching gap-fill gaps (chunks 04-06, gf06)

- Cache coherence in distributed (not CPU) caches: the Wikipedia page is about CPU coherence; no source here covers coherence between application-level caches beyond the one Singh sentence.
- CPU cache: only the lead, Operation, Associativity and Multi-level sections were read; address translation, TLB and specialised caches (victim, trace, uop) were left out as hardware detail.
- Memoization: the Parsers and Automatic memoization sections (pseudocode, parsing history) are not taught; no entry for dynamic programming.
- Thundering herd problem: only OS mitigations and backoff jitter are given; no sources for request coalescing or locking in front of a cache (see Cache stampede mitigation).
- Cache stampede paper (Vattani et al.): only the abstract exists, so the optimal algorithm itself (the XFetch formula) has no sentences.
- Not drafted: Page cache side-channel attacks (2019 research, security trivia); ARC's PostgreSQL 8.0.0 patent story (business history).
