# choosing-a-database gaps (pass b8, chunks 01-04)

Expected concepts with no or one-sentence coverage (suggested page or source key):
- NewSQL: one sentence only (Database page, History > 2000s); used as a fact in NoSQL. Wikipedia "NewSQL".
- Polyglot persistence: one lead sentence on the NoSQL page. Wikipedia "Polyglot persistence".
- Two-phase locking, Serializability, Snapshot isolation, Multiversion concurrency control, Write skew: known only through sentences on the Isolation and ACID pages. Wikipedia pages of those names.
- Online analytical processing, Online transaction processing, Data warehouse, Star schema: no page crawled; covered from the Database page and ByteByteGo guides. Wikipedia pages of those names.
- Document-oriented database, Key-value database, Graph database, Wide-column store, Time series database, Multi-model database: only the NoSQL page and Singh's sections crawled. Wikipedia pages of those names; Time series and Multi-model are folded into the NoSQL entry as one fact each.
- Vector (embedding) database, Full-text search engine (Elasticsearch), Geospatial database: one bullet each in ByteByteGo how-to-choose-the-right-database. Suggest Wikipedia "Vector database", "Elasticsearch", "Spatial database".
- Eventual consistency, CAP theorem, Distributed transaction, Two-phase commit: used as related or prerequisite titles only; other chapters own them.
- Database index, Database normalization: prerequisite or related titles only; owned by indexes-normalization-and-storage-engine.

Skipped on purpose:
- ByteByteGo types-of-databases: chatty prose over a diagram; its facts are folded into the NoSQL type entries and OLTP and OLAP.
- Singh "Challenges" list in databases-and-dbms: a generic list of operating pains, no concept.
- History sections (Database, Relational database, SQL), Codd's 12 rules beyond one sentence, SQL trademark and pronunciation, DRDA, DB-Engines and Gartner rankings, SQL data types list: business history or trivia.
- NoSQL "ACID and join support" and "Performance" tables: table rows lost their column headers in extraction, so the cells cannot be read reliably.

Notes for the merge and verification passes:
- Weights lean heavy: 18 of 34 entries are Major and 2 Landmark; the chapter is core, so the ordering pass may demote some.
- Singh's NoSQL page lists "Schemaless" under both advantages and disadvantages of document databases; stated as the source gives it.
- The ByteByteGo isolation-levels guide expands MVCC as "Multi-Version Consistency Control"; Wikipedia calls it multiversion concurrency control (noted on that entry).
- Singh's SQL-vs-NoSQL "for SQL" and "for NoSQL" reason lists lost their group labels in the dossier; grouping is taken from the page's list order (noted on that entry).
