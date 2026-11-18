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
