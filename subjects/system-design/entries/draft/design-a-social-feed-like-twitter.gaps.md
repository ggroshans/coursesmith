# design-a-social-feed-like-twitter gaps (b26)
- EdgeRank: Wikipedia "EdgeRank" is linked from Singh but not crawled; Feed ranking rests on Singh's few sentences.
- Fan-out (feed generation, timeline): no Wikipedia page crawled; suggest "Fan-out (software)" or a Twitter timeline engineering post.
- Elasticsearch / Apache Lucene / inverted index: no page crawled; Elasticsearch entry rests on Singh's sentences (suggest Wikipedia "Elasticsearch", "Apache Lucene", "Inverted index").
- Social graph / mutual friends (Singh "Mutual friends", graph databases Neo4j): left to design-the-data-structures-for-a-social.
- twitter-architecture-2022-vs-2012.md has one sentence (a4ed222871aa): no entry. twitter-10-tech-stack.md is a five-bullet list of products: drafted only as a thin Case study, low priority.
- how-does-twitter-recommend-tweets.md is a terse stage list (the diagram carries the detail): Case study of four facts only; the Twitter Blue boost and the Mem credit sentences are skipped.
- Conflicts not raised: Singh's high-level table lists 100 million DAU against 200 million in its traffic derivation (b95d774fb8ad vs d76ce9f4a6a4); Singh (1 billion tweets/day) and the primer (500 million tweets/day) assume different scales and are attributed in the Worked example.
- Cut from the Worked example for the 16-fact cap: data partitioning and consistent hashing (6b62e0d7728a, 6ece367ee9c1), retweets (65b5bb6bd5da), metrics with Kafka and Spark (80c3f5e15e39).
