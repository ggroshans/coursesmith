# design-a-stock-exchange gaps (b28)
- Chapter is thin: two short guides, no requirements, volumes, data model or API.
- Order book; Matching engine / matching algorithm; Order types (limit, market): Wikipedia "Order book", "Matching engine", "Order (exchange)".
- The 14 steps of the trading flow (client gateway, order manager, risk checks, sequencer, matching engine, market data publisher, reporting): spelled out only in the diagram, not in the text.
- Pre-trade risk checks, sequencer / event sourcing for recovery and failover of a single-server design.
- Market data feed (publishing prices to subscribers): Wikipedia "Market data" or a primer guide.
- CPU pinning / context switch / lock-free design: Wikipedia "Processor affinity", "Context switch", "Lock-free".
