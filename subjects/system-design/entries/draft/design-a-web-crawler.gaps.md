# design-a-web-crawler gaps
- Inverted index / search engine indexing (Wikipedia "Search engine indexing"): the answer builds a reverse index but no crawled page explains it
- PageRank (Wikipedia): the selection policy leans on it
- Document similarity for duplicate-content detection (Jaccard index, Cosine similarity, shingling)
- Sitemaps (Wikipedia "Sitemaps")
- Spider trap (crawler trap)
- Bloom filter as a seen-URL check (not in the sources)

# design-a-web-crawler gaps (gf22, chunks 02-04)
- Bloom filter as a seen-URL check: the course has a Bloom filter entry in another chapter; no crawled sentence ties it to the crawler.
- Duplicate-page detection (shingling plus Jaccard, or MinHash): the pages teach each piece but no sentence says a crawler uses them; the entries claim none. Wikipedia "MinHash" or "Near-duplicate detection" would join them.
- Locality-sensitive hashing and MinHash: only two sentences inside the Jaccard index page, no entry.
- Crawl frontier and URL-seen test, DNS resolution caching: not covered by these pages.
- PageRank page: history, Toolbar, spoofing, patents and non-web uses skipped as trivia.
- Robots.txt page: history, legal cases, archive-site and AI-bot compliance skipped as trivia.
