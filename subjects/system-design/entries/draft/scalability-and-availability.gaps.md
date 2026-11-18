# gaps: scalability-and-availability (pass b11)

Concepts expected but with no (or too few) sentences in the dossier:
- Elasticity / autoscaling (Elasticity (cloud computing), Autoscaling): only a one-line bullet in ByteByteGo ("Auto Scaling").
- Stateless services and stateful vs stateless design: one bullet each in the ByteByteGo guides, no page of its own.
- Failover (Failover page): named in the High availability article but not crawled.
- Mean time between failures (MTBF) and mean time to recovery: one sentence each in the High availability article.
- Redundancy (engineering): not crawled; the Redundancy entry rests on the High availability section.
- Amdahl's law (page not crawled): only the worked example inside Scalability.
- Fault tolerance: owned by the resilience chapter; only Singh's comparison with high availability is used here.
- Capacity planning for scaling: no sentences.

Sections skipped on purpose (no system-design teaching value): Scalability "Examples" (Incident Command System), "Domains" beyond the P2P and OLTP facts, "Weak versus strong scaling" (HPC), "Network scalability"; High availability "Resilience" beyond one idea, "Military control systems", "Reasons for unavailability", "Costs of unavailability" (dated survey and 1996 cost). Singh's "Availability" tables beyond the formula and the sequence/parallel formulas, and the cheat-sheet pages that only list the word "Availability", got no entry.

# gaps: scalability-and-availability (gap-fill gf10, chunks 03-05)
- Autoscaling is also an entry in scale-a-system-to-millions-of-users-on-a (primer bullet): same title here, new facts from the Wikipedia page; fold at the duplicates pass.
- Capacity planning: the Wikipedia page is mostly manufacturing; IT capacity planning has only a few sentences (SRE book adds advice). Suggested: a sre.google chapter on demand forecasting if one is in the source list.
- MTBF and MTTR: no source here gives availability = MTBF / (MTBF + MTTR); suggested page: Availability (reliability theory) or Reliability engineering.
- Elasticity (cloud computing): still no page of its own.
- Sections skipped on purpose: MTBF in manufacturing (TPM), MTBF with censored data, vendor histories in Autoscaling, bridge/aircraft/power-grid examples and fire-safety distances in Redundancy (engineering), Amdahl derivations with transformed sequential parts.
