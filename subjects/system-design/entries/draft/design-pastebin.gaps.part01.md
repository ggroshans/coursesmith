# design-pastebin gaps (part01)

Concepts the answer relies on, with no explaining sentences in this chapter (named as prerequisites or left to other chapters):
- Hash function / MD5 (used for the url; only one bullet here) - suggested page: Hash function, MD5
- Object storage (named only as "Amazon S3") - page: Object storage (storage-systems chapter)
- Database index (primary key and created_at index) - page: Database index
- MapReduce (analytics from web server logs) - page: MapReduce; paper>10.1145/1327452.1327492
- Data warehouse (Amazon Redshift, Google BigQuery for the analytics database) - page: Data warehouse
- Remote procedure call and REST (internal and public APIs) - pages: Remote procedure call, REST
- Master-slave replication, read replicas, SQL federation, denormalization - replication / sharding chapters
- Expiring data (time-to-live or periodic cleanup of expired pastes) - page: Time to live
- Back-of-the-envelope estimation: no source defines it (only the primer's conversion guide) - suggest Singh "Estimation and constraints" sections or a gap-fill
- Pastebin API detail (request and response of create and get paste) and the table schema are code blocks in the primer, dropped from the text, so the data-model and API facts name only fields and sizes

Not drafted on purpose: the primer's "Additional talking points" bullets (caching, NoSQL, asynchronism; topic names only, no sentences that teach).
