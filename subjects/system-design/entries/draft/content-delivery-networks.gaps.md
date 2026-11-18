# content-delivery-networks gaps (pass b7)

Concepts expected here with no (or only a sentence of) source text:
- Edge computing (suggest Wikipedia "Edge computing"; the ByteByteGo beginner's guide only has three loose sentences)
- Cache invalidation / content purging and TTL on CDNs (suggest Wikipedia "Cache invalidation" or an RFC 9111 section; no CDN-specific text crawled)
- Origin shield / tiered caching (one defining line in the Wikipedia Technology section, folded into "CDN origin and edge servers")
- Anycast routing (crawled as IP address#Routing > Anycast addressing; the chapter that owns IP/DNS should draft it; here only the ByteByteGo line is cited)
- Global server load balancing (suggest Wikipedia "Global Server Load Balancing")
- Subresource Integrity and DDoS (concept pages exist as links; suggest Wikipedia "Subresource Integrity", "Denial-of-service attack")
- Content negotiation (HTTP Accept headers / Client-Hints used by Image CDNs; RFC 9110 content negotiation)
- Non-HTTP delivery (WebRTC, WebSockets): one sentence only (S:29b8e72fc9f7), not drafted

Not drafted on purpose:
- ByteByteGo "a-beginner's-guide-to-cdn" is a pointer to an external article; its text is about edge computing and cloud gaming, no CDN concept beyond what the other guides say.
- ByteByteGo "why-are-content-delivery-networks-cdn-so-popular": the market-size line is business trivia; "Best Practices" is a single pointer sentence.
- Wikipedia provider lists (Commercial-as-a-Service, Telco CDNs, Commercial using P2P, free software vendors): lists of companies and products, no concept.
- Singh "Examples" (CloudFront, Google Cloud CDN, Cloudflare): a list of products.

# content-delivery-networks gap-fill gaps (chunks 02-03, gf06)

- Content negotiation (Wikipedia page, chunk 03): not drafted. The http-https-and-tls chapter already has "HTTP content negotiation" from RFC 9110, which covers server-driven (proactive) and agent-driven (reactive) negotiation, Accept headers and q-values; the Wikipedia page adds only the Accept-Datetime and Accept-Profile extensions.
- DDoS: the page is long (about 30 attack-technique sections); only the concept, main attack families, SYN flood, reflection/amplification, layer 7, yo-yo and the upstream-filtering defence were taught. Rate limiting, anycast and CDN absorption of attacks have no sentences here (see Rate limiting; Anycast is still an open gap).
- Edge computing: the fog-computing contrast, IoT and edge-AI sections and the Akamai history were skipped as trivia or off-topic. No source for serverless at the edge (edge functions) beyond one ESI-era sentence.
- Peer-to-peer: copyright law, network neutrality and cryptocurrency sections were skipped as non-engineering. "Distributed hash table" and "Client-server model" are named as prerequisites/related but no chunk of this pass teaches them.
