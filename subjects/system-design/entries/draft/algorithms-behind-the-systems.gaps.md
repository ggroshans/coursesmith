# algorithms-behind-the-systems: gaps (pass b24)

No entry, and why:
- gh>ByteByteGoHq/.../algorithms-you-should-know-before-taking-system-design-interviews.md: its sentences only introduce a star-rated list that lives in a diagram; the one usable idea (knowing how algorithms are used in real systems matters more than implementation details) is advice, too thin for an entry.
- gh>ByteByteGoHq/.../unique-id-generator.md: three requirement bullets and a note that implementation details are online; folded into Distributed unique ID generation.
- Geohash precision table, base-32 alphabet and decoding worked example (Wikipedia), Snowflake worked example, UUID filesystem/partition/COM uses and byte ordering: skipped as detail or trivia.

Expected but absent from the dossier (suggested pages):
- Count-min sketch, Merkle tree, Skip list, Trie, Z-order curve, Hilbert curve, S2 / H3 geospatial indexing (Wikipedia: "Z-order curve", "Hilbert curve", "Trie", "Merkle tree", "Count–min sketch", "Skip list")
- Ticket-server (Flickr) ID generation and ULID / KSUID time-ordered IDs (no source crawled)
- k-d tree and R-tree as other spatial indexes (Wikipedia: "K-d tree", "R-tree")
- Bloom filter use as an interview building block is only shown through Wikipedia and two ByteByteGo cache guides; no worked system-design discussion of sizing a filter from the 9.6 bits-per-element figure.

Odd source text for the verifier:
- HyperLogLog sentences 3b2afba93ab5 and 2a2ea27bca02 / f2dad12afbbe lose superscripts and a square root in extraction ("2n", "1.04/m"); the estimate formula and relative error are deliberately not stated as facts.
- UUID sentence 17d6658255c5 prints "2122" for 2^122; the fact uses the 122 bits and 5.3×10^36 only.

# gaps (gf19, algorithms-behind-the-systems chunks 04-08)
Skipped on purpose: Hash function integer hashing variants (mid-squares, Fibonacci, Zobrist, algebraic coding), Z-order BIGMIN code and quadtree-building code, Hilbert L-system and 3D-printing uses, K-d tree open-source library list, MD5 pseudocode and history of attacks, Base64 variant tables (PEM, UTF-7, OpenPGP), RFC 9562 test vectors, IANA registries, namespace IDs.
Dropped to mention_sent_ids: universal and perfect hashing (cd9ad6be7870, 6121a39a21af), Nil and Max UUID (334f8ba55124, 9eb4583c9529).
Odd source text: K-d tree sentence b3fca07139d3 prints "n≫2k" for n much greater than 2^k, so the rule of thumb for points versus dimensions is not stated; HyperLogLog Wikipedia sentences 2a2ea27bca02 and f2dad12afbbe lose superscripts and the square root (the paper abstract 954c43f2e0e8 is used instead); MD5 page's Definition line is a stray attack sentence (8b3259b60b5d used).
Expected but absent (suggested pages):
- Skip list, R-tree, S2 geometry and H3 hexagonal indexing (Wikipedia "Skip list", "R-tree", "S2 Geometry", "H3 (geospatial indexing)")
- Locality-sensitive hashing (Wikipedia "Locality-sensitive hashing") for near-duplicate detection; Similarity hashing rests on only a few sentences.
- Cryptographic hash function / SHA-2 (Wikipedia "Cryptographic hash function", "SHA-2"), cited here only through MD5 and Hash collision.
- ULID and KSUID time-ordered ids; Flickr ticket servers (no source crawled).
- Linear probing and Perfect hash function pages for a fuller Hash collision / Hash table treatment (Hash table itself is in the indexes chapter).
