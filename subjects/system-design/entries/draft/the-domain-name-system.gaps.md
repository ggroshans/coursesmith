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

# the-domain-name-system gaps (gap-fill gf03, chunks 03-05)

Skipped on purpose: DNSSEC adoption statistics, rollout history by country and the U.S. government deployment
programs, DNSSEC algorithm and digest tables, DNSSEC Lookaside Validation (historical), tool lists; Anycast history,
6to4 and multicast rendezvous-point uses; TLD proposals, historical and pseudo-domains and example tables; root server
operator table; domain registrar history, prices, transfer scams, rankings and accreditation fees; the obsolete record
type table beyond three examples.
Overlaps for the coordinator: "Round-robin DNS" (drafted here, article Round-robin DNS) covers ground that "DNS load
balancing" (load-balancing chapter) and "DNS load distribution" also touch; each has distinct_from set.
"Time to live and hop limit" is the network/DNS side of TTL; the caching chapter's "Time to live" is cache eviction.
Still wanted: EDNS client subnet / GeoDNS routing (RFC 7871); DANE (DNS-based Authentication of Named Entities);
DNS over HTTPS and DNS over TLS (Wikipedia pages); BGP (Border Gateway Protocol) as a prerequisite of Anycast.
