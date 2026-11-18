# design-a-stock-exchange gaps (b28)
- Chapter is thin: two short guides, no requirements, volumes, data model or API.
- Order book; Matching engine / matching algorithm; Order types (limit, market): Wikipedia "Order book", "Matching engine", "Order (exchange)".
- The 14 steps of the trading flow (client gateway, order manager, risk checks, sequencer, matching engine, market data publisher, reporting): spelled out only in the diagram, not in the text.
- Pre-trade risk checks, sequencer / event sourcing for recovery and failover of a single-server design.
- Market data feed (publishing prices to subscribers): Wikipedia "Market data" or a primer guide.
- CPU pinning / context switch / lock-free design: Wikipedia "Processor affinity", "Context switch", "Lock-free".

# design-a-stock-exchange gaps (gf26)
- Order matching system / matching algorithms (price-time priority, pro-rata, auctions): Wikipedia "Order matching system" was not crawled; the Matching engine entry is thin.
- Sequencer, event sourcing and failover for a single-server exchange design; pre-trade risk checks: no sentences (maybe "Event sourcing" or a primer/vendor page).
- Volumes and estimates for an exchange (orders per second, symbols): no source sentence.
- Context switch / "Lock-free" as separate pages: covered inside "Processor affinity" and "Non-blocking algorithm"; "Memory barrier" and "Compare-and-swap" could be seed pages.
- Bid-ask spread, Dark pool, Iceberg order, High-frequency trading: only mentioned; add Wikipedia pages if the owner wants market microstructure detail.
