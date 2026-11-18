# Gaps: how-the-big-distributed-data-systems-wor (pass b15)

- paper>10.1145/945445.945450 (GFS paper): the crawled abstract is only ACM page chrome (S:6006faa8ccf2), so the GFS entry rests on Wikipedia alone. Re-fetch the abstract text.
- Dynamo (storage system): Wikipedia page not crawled, and the Dynamo paper abstract has three sentences with no design content. Missing: consistent hashing ring, sloppy quorums, vector clocks, hinted handoff and anti-entropy as Dynamo uses them.
- Spanner: TrueTime and external consistency have only one Wikipedia sentence and the abstract; suggest the full Spanner paper or a "TrueTime" source, and Wikipedia "Spanner (database)" sections on transactions.
- Bigtable and Cassandra papers: abstracts only; no sentences on Chubby, tablet servers, SSTable/memtable design or Cassandra's token ring and partitioner. Suggest the full papers or Wikipedia "Chubby (lock service)".
- HBase (Apache HBase) and ScyllaDB: named as Bigtable/Cassandra relatives; no pages crawled.
- Concepts with no page here: Gossip protocol, Hinted handoff, Bloom filter (as a standalone page), Quorum reads and writes, Data locality.
- No entry for Hadoop's release history, Cassandra's Facebook origin, DynamoDB's October 2025 outage (S:b1fc65278d2f), or Discord company facts: business history or incident trivia under the brief's scope rule.
- Wikipedia's Bigtable lead and Spanner "History" sections describe the cloud products (Cloud Bigtable, Cloud Spanner), left out as product history.
- Overlap to review at merge: "HDFS architecture" (Wikipedia Hadoop article) versus the storage-systems chapter's "Hadoop Distributed File System" (Singh); "Cassandra write and read path" versus the indexes chapter's "LSM-tree writes and compaction".
