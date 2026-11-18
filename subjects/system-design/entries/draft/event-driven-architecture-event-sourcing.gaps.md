# gaps (chunk 01 of event-driven-architecture-event-sourcing)
- Schema registry (event schema control; named by Singh and McDonald's but no sentences about how it works) -> suggest a Confluent/Apache Avro docs page or Wikipedia "Apache Avro"
- Change data capture (own Wikipedia page exists; only two Event sourcing facts drafted here, the owning chapter should draft it)
- Event sourcing vs CRUD comparison: differences-in-event-sourcing-system-design.md is only questions and a pointer to a diagram, no entry drafted
- Event sourcing "replay" / snapshots / projections: no sentences found -> suggest Martin Fowler "Event Sourcing" article or Microsoft Azure Architecture Center page
- Command-query separation (CQS): Wikipedia page linked from CQRS but not in dossier
- Publish-subscribe pattern, message broker, eventual consistency: owned by other chapters, named as prerequisites

# gaps added after chunk 02
- Complex event processing and Event stream processing: Wikipedia pages not crawled (only the EDA sections cover them) -> suggest "Complex event processing", "Event stream processing"
- Domain-driven design / bounded context: named as prerequisite of Domain events and integration events -> suggest "Domain-driven design"
- Fallacies of distributed computing: linked from EDA Challenges -> suggest "Fallacies of distributed computing"
- Event-driven architecture vs SOA: only one sentence (d7f7dd56e82b) in the dossier, not drafted
- Event delivery guarantees (at-least-once, exactly-once, ordering): only named as challenges -> suggest a messaging chapter page

# gaps (event-driven-architecture-event-sourcing, gap-fill chunk 03)
- Aggregate, repository and Event storming as entries of their own: only a few sentences each, folded into Domain-driven design
- DDD context mapping patterns (partnership, conformist, open-host service, published language): six sentences cut from the dossier, only three named in Domain-driven design
- Schema registry: Avro page does not describe one; the name stays unresolved; suggest Confluent Schema Registry docs
- Avro Object Container File layout, language APIs and code samples skipped
- DDD notable tools (Actifsource, Context Mapper, CubicWeb) skipped
