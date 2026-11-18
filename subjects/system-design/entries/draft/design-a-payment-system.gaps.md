# design-a-payment-system gaps (b28)
- Chapter is thin: two short guides, no requirements, volumes or estimates, data model or API.
- Double-entry bookkeeping: Wikipedia "Double-entry bookkeeping".
- Payment service provider (PSP) and card payment flow (authorization, capture, settlement): Wikipedia "Payment service provider", "Payment processor".
- Avoiding double payment, retries and idempotency keys in payments: guide how-to-avoid-double-payment.md (owned by resilience-circuit-breakers-rate-limitin).
- Wallet and ledger design (append-only ledger, balance consistency), failure handling when the PSP call fails: no sentences.
- Apache Flink: Wikipedia "Apache Flink" (stream processing chapter).
