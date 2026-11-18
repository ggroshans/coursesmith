# load-balancing gaps (pass p2, chunk 01)

Expected concepts with no sentences or no crawled page (suggested page or source key):
- Consistent hashing (belongs to its own chapter; only two "also on" sentences here)
- Reverse proxy (crawled, but another chapter)
- Power of two choices (Wikipedia "Power of two random choices"; one bullet only here)
- Equal-cost multi-path routing (Wikipedia "Equal-cost multi-path routing"; data center flow hashing)
- Anycast (Wikipedia "Anycast"; global routing of traffic)
- Global server load balancing (Wikipedia "Global Server Load Balancing")
- Session stickiness cookies (Wikipedia "Sticky session" or "Load balancing (computing)" persistence detail; no page crawled)
- Connection draining / graceful server removal (no source found)
- Autoscaling (only a Singh bullet and ByteByteGo's scalability line; suggest a scaling-chapter page)
- NGINX and HAProxy as load balancers (suggest Wikipedia "Nginx", "HAProxy"; named building blocks in interviews)
- Application delivery controller (Wikipedia "Application delivery controller")
- Linux Virtual Server / direct server return (Wikipedia "Linux Virtual Server")

Parts of the sources given no entry:
- Singh "Examples" (AWS, Azure, GCP, DigitalOcean load balancers) and ByteByteGo's named cloud products: a list of products, no concept.
- Wikipedia "Problem overview" detail judged parallel-computing specific, not system design: task size and the prefix-sum static
  distribution, task dependencies and directed acyclic graphs, shared versus distributed memory, hierarchy of control,
  scalability of algorithms, fault tolerance of parallel algorithms, tree-shaped computation.
- Wikipedia "Telecommunications" (Shortest Path Bridging, TRILL, network monitoring) and "Data ingestion for AI model
  training": network standards history and a thin, promotional section; only the redundant-link contrast was kept (in Failover).
- Singh "Advantages" is a bare bullet list (scalability, redundancy, flexibility, efficiency) with no sentences to cite.
