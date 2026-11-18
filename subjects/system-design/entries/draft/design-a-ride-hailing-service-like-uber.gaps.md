# design-a-ride-hailing-service-like-uber gaps (b26)
- Geohash and Quadtree Wikipedia pages are crawled but belong to algorithms-behind-the-systems; the Worked example names them as prerequisites.
- Not crawled: Hilbert curve, Google S2 and H3 (geospatial indexing), "Surge pricing" / "Dynamic pricing" (Singh gives three sentences, 21f403aa0539 23bdf920fd36 e70196540d9e), "Proximity search".
- ETA calculation and routing: Singh only says the ride service computes the ETA; suggest the design-google-maps sources.
- proximity-service.md is framed around Yelp and restaurants and ends with an offer of more detail: one Concept entry only; the geohash walk-through there is summarized, not duplicated as a Geohash entry.
- uber-tech-stack.md is a list of products: drafted only as a low-priority Case study.
- Cut from the Worked example for the 16-fact cap: Hilbert-curve range queries (814b4cf90f36), metrics and analytics with Spark (89b8dad3991c).

# design-a-ride-hailing-service-like-uber gaps (gf22, chunk 02)
- k-d tree and R-tree (Wikipedia "K-d tree", "R-tree"): only 'also on' lines here; nearest-neighbor search folds them into one fact. Pages would give each its own entry.
- Locality-sensitive hashing (Wikipedia): two sentences inside the nearest-neighbor page, no entry.
- Dynamic pricing page: per-industry, controversy and regulation sections skipped as business trivia; no source explains how a ride-hailing surge multiplier is computed from supply and demand per area.
