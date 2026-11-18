# design-a-payment-system gaps (b28)
- Chapter is thin: two short guides, no requirements, volumes or estimates, data model or API.
- Double-entry bookkeeping: Wikipedia "Double-entry bookkeeping".
- Payment service provider (PSP) and card payment flow (authorization, capture, settlement): Wikipedia "Payment service provider", "Payment processor".
- Avoiding double payment, retries and idempotency keys in payments: guide how-to-avoid-double-payment.md (owned by resilience-circuit-breakers-rate-limitin).
- Wallet and ledger design (append-only ledger, balance consistency), failure handling when the PSP call fails: no sentences.
- Apache Flink: Wikipedia "Apache Flink" (stream processing chapter).

# design-a-payment-system gaps (gf26)
- Worked example is still thin: no sentences on payment volumes or estimates, ledger/wallet table schema, a payment API, or consistency between wallet and ledger updates.
- Payment processor, acquiring bank and issuing bank as separate concepts: Wikipedia "Payment processor", "Acquiring bank" (only described inside the gateway process).
- ISO 8583 and EFT switch message formats: Wikipedia "ISO 8583".
- PCI DSS: Wikipedia "Payment Card Industry Data Security Standard" (only four compliance levels are in the PSP page).
- Append-only ledger / event sourcing for money movement: no source sentence ties them to payments.
