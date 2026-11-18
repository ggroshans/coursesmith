# sharding-and-partitioning gaps (pass b12)

- Rendezvous hashing (Wikipedia page; only 4 sentences of it are reachable through Consistent hashing, so the entry is anchored to that section)
- Hash function (Wikipedia; every hashing entry here needs it as a prerequisite, no entry exists in the course yet)
- Distributed hash table (Wikipedia; consistent hashing is its cornerstone)
- Shared-nothing architecture (Wikipedia; sharding relies on it)
- Resharding and rebalancing strategies (fixed number of partitions, dynamic splitting, moving a shard): sources only call it a challenge
- Secondary indexes on partitioned data, and request routing to the right shard (a router or service-discovery step): not covered by any crawled source
- Cross-shard transactions and joins in practice (two-phase commit, denormalization): only named as a challenge
- Hot-key mitigation (key salting, splitting a hot key): only the generic "hot spot" remedies appear
- Replication factor and quorum placement on the ring (Dynamo-style preference lists): only one Singh paragraph
- ByteByteGo "key-concepts-to-understand-database-sharding" guide: analogies only (bookshelf, playing cards, phone book), no entry drafted; "Shard etymology", the sharding implementations list and blockchain sharding were skipped as trivia, product lists or out of scope

- Hash table (Wikipedia: Hash table) is a prerequisite of Distributed hash table and has no entry.
- Hash function (Wikipedia: Hash function) is a prerequisite of Rendezvous hashing and has no entry.
- Peer-to-peer (Wikipedia: Peer-to-peer) is cited as related by Distributed hash table and Chord and has no entry.
- Kademlia (Wikipedia: Kademlia) is named as the most popular optimized DHT; not crawled.
