# Gaps: indexes-normalization-and-storage-engine (pass b9)

Concepts the chapter uses or names but no crawled page explains in its own right:
- Hash index / Hash table (named in the index-structures list and as a cluster key)
- Skip list (in-memory index type, LSM memtable)
- Sorted string table (SSTable) and memtable
- Write-ahead log
- Bloom filter (used by LSM lookups; only described inside the LSM page)
- Inverted index (Wikipedia page; only one sentence in Database index)
- R-tree (spatial or multi-dimensional index) and Suffix tree
- B+ tree (own Wikipedia page; only the B-tree Variants section was available)
- Index selectivity and cardinality, and how a query planner chooses an index
- Materialized view (named under Denormalization)
- Star schema and snowflake schema
- Relational database, Database transaction, ACID (prerequisites named by several entries)
- Columnar database / column-oriented storage (only the 6NF paragraph)
- Compaction strategies and write amplification (leveled vs tiered, named but thin)
- MVCC as an alternative to locking (pessimistic vs optimistic locking guide is only a few sentences)
- Storage engine (no page of its own; the entry uses Database#Storage)

Skipped on purpose:
- The multi-table "cluster" of Database index (an Oracle-style construct unrelated to clustered indexes).
- ByteByteGo "Satisfying 5NF/ETNF/DKNF" worked tables: kept only the rules, not the sample data.

# indexes-normalization-and-storage-engine gaps (gap-fill gf08, chunks 04-06)
- Hash function: prerequisite of Hash table; owned by another chapter (Wikipedia "Hash function").
- Distributed hash table: only a short section on the Hash table page here; Wikipedia "Distributed hash table" is in sharding-and-partitioning.
- ARIES recovery: the paper has only an abstract with two usable sentences (no redo/undo, checkpoint or recovery-pass detail); suggest Wikipedia "Algorithms for Recovery and Isolation Exploiting Semantics".
- PostgreSQL docs for GiST, GIN, BRIN internals (indexes pages 65.x) would deepen "PostgreSQL index types".
