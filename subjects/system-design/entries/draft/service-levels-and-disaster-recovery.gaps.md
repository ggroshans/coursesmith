# service-levels-and-disaster-recovery gaps (pass b21)

Concepts expected but with no sentences (or only a bullet) in the dossier:
- Error budget (one bullet only, in Site reliability engineering § Principles and practices) - suggest a page or Google SRE source
- Business continuity planning (Wikipedia: "Business continuity planning")
- Business impact analysis (Wikipedia: "Business impact analysis")
- Mean time between failures / Mean time to repair (Wikipedia pages, only named in lists)
- Incident management (Wikipedia: "Incident management"); postmortems
- Chaos engineering / failover testing (Wikipedia: "Chaos engineering")
- Multi-region and cross-region failover design (cloud provider DR guides)
- Backup strategies and the 3-2-1 rule (Wikipedia: "Backup")
- Alerting and on-call practice (Wikipedia: "Website monitoring" or a docs page)
- Percentile latency SLIs (p99) as service levels (cf. "Tail latency" in the latency chapter)

Not drafted on purpose:
- Service-level agreement § History/Specific examples: telecom history, Telecommunications Act of 1996, 5G, WSLA, EU research projects (SLA@SOI, VISION Cloud, IRMOS): trivia or niche, no entry.
- Site reliability engineering § History/Industry (Google's 2003 start, team sizes, survey percentages, SREcon, company list): company history, excluded.
- IT disaster recovery § History (Sungard 1978, mainframe era), Change Healthcare cyberattack, HIPAA 2024 NPRM details: business history/trivia, excluded.
- Sentences flagged CITATION NEEDED or FAILED VERIFICATION were not used as facts.
- Availability and the nines, redundancy and clusters are owned by the scalability-and-availability chapter; only named as related here.

# service-levels-and-disaster-recovery gaps (gap-fill gf15, chunks 3-7)

Concepts expected but not covered by any page crawled so far:
- Blameless postmortems and incident response roles (suggest doc>sre.google/sre-book/postmortem-culture, doc>sre.google/sre-book/managing-incidents)
- Toil and on-call practice (suggest doc>sre.google/sre-book/eliminating-toil, doc>sre.google/sre-book/being-on-call)
- Time-series alerting rules, Borgmon/Prometheus style (suggest doc>sre.google/sre-book/practical-alerting)
- Mean time between failures / mean time to repair (Wikipedia pages, only named in lists)
- Chubby and lock services in depth, Google's D/Colossus storage layering (suggest doc>sre.google/sre-book/managing-critical-state; the production-environment chapter gives only a few sentences each)

Not drafted on purpose:
- Business continuity planning: lists of ISO, BSI, Australian and US standards, resilience theory, inventory bullets: standards catalogue, no explanation.
- Incident management: physical incident management, critical infrastructure and ITIL/ISO 20000 detail beyond the generic lifecycle: not system-design material.
- Chaos engineering: history (Macintosh Monkey, ABAL2 La Matraque), tool lists (Steadybit, Gremlin, Proofdock, Voyages-sncf): trivia and products.
- Backup: storage media (tape, hard disk, optical, SSD) one-liners, filesystem dump and metadata handling, refactoring, multiplexing, staging: low interview value.
- Embracing Risk: Google-specific Ads and Web Search latency anecdotes and the frontend infrastructure example; production environment hardware, Jupiter/B4 networking, development environment, Stubby/protobuf: company stack detail.
- Data integrity chapter: "beginner's mind", "trust but verify" principle bullets and the cloud-environment challenge list are folded into other entries, not drafted separately.
- Load balancing chapters: the code listing of deterministic subsetting and the pagination discussion of query cost.
- No entry was marked thin.
