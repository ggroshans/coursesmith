# gaps (monoliths-microservices-and-service-disc, from chunk 01)
- Database per service (named as best practice; owned by a data chapter) -> suggest Singh or microservices.io page
- Bounded context / Domain-driven design -> suggest Wikipedia "Domain-driven design"
- Circuit breaker pattern, bulkhead, graceful degradation: only named in lists here; the resilience chapter should own them
- Saga pattern for transactions across orchestrated services: other chapter (distributed transactions)
- Service discovery tools (Consul, Eureka, Zookeeper, Kubernetes Services): only named in lists, no sentences on how they work -> suggest "Apache ZooKeeper", "Consul (software)"
- API gateway: appears only as a bullet in the typical architecture guide -> suggest a dedicated page in the API chapter
- Strangler fig pattern / migrating a monolith to microservices: no sentences found -> suggest Wikipedia "Strangler fig pattern"
- Singh's "Examples" under Service discovery and Event-Driven Architecture are bare tool lists, not drafted as entries

# gaps added after chunks 02-03
- Microservices history (Rodgers, 2005 talk) and Fowler/Lewis definition: deliberately not drafted (history, personalities)
- Enterprise service bus: the SOA backbone; no sentences in the dossier -> suggest Wikipedia "Enterprise service bus"
- Sidecar pattern: only inside Service mesh sentences -> suggest Wikipedia "Sidecar pattern" or microservices.io
- Consumer-driven contract testing and distributed tracing: one sentence each -> suggest "Distributed tracing", "Contract testing"
- Strangler fig pattern (incremental migration): see above
- API gateway and Backend for frontend: not in these sources beyond a bullet
- Service-oriented architectures for interactive applications, Web 2.0 vs SOA, SOA applications (caBIG, Virtual Observatory, Language Grid): skipped as niche
