# the-domain-name-system gaps (pass b3)

Concepts a strong DNS chapter wants but this dossier has only passing sentences for (suggested pages):
- DNSSEC: "Domain Name System Security Extensions" (only one-line mentions here)
- DNS cache poisoning: "DNS spoofing" or "DNS cache poisoning" (a security fact only)
- GeoDNS / latency-based DNS routing and round-robin DNS: "Round-robin DNS", "Geo-DNS" (folded into DNS load distribution as a few facts)
- Anycast routing: "Anycast" (root-server copies mention it)
- Content delivery network: "Content delivery network" (DNS steering of users to nearby servers)
- Top-level domain: "Top-level domain" (only TLD-type bullets here)
- Root name server: "Root name server" (drafted as part of "Root and TLD name servers" from Singh and Wikipedia)
- Time to live: "Time to live" (covered inside DNS caching and TTL)
- List of DNS record types: "List of DNS record types" (not crawled; record types come from ByteByteGo, Singh and the DNS article)
- Split-horizon DNS, DNS load balancing at scale, EDNS client subnet (RFC 7871 is only named once)
- Domain name registrar / WHOIS: "Domain name registrar", "WHOIS" (one folded entry, Domain name registration)

Skipped on purpose:
- Singh "Examples" section is only a list of managed DNS products (Cloudflare DNS, Google Cloud DNS, and so on): no entry.
- Wikipedia History details on BIND developers and ISC: people and organization history, no entry.
- DNS blocklists (Operation > Other applications) and DNSMessenger: one-off uses, folded into DNS security issues and DNS load distribution at most.
- Wikipedia wildcard-record example zone lines and the DNS message header bit table: not stated as plain sentences.
