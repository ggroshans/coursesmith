# http-https-and-tls gaps (pass b4)

- HTTP/2 own page or RFC 9113 (only a guide and Wikipedia HTTP sentences): suggested "HTTP/2" or rfc>9113
- HTTP/3 and QUIC pages (RFC 9114, RFC 9000): suggested "HTTP/3", "QUIC"
- HPACK header compression (only named in guides): suggested rfc>7541 or "HPACK"
- HTTP cookie (sessions are only mentioned in one sentence): suggested "HTTP cookie"
- Head-of-line blocking and HTTP pipelining as concepts: suggested "Head-of-line blocking", "HTTP pipelining"
- Individual status codes (301/302, 304, 401/403, 404, 429, 500/502/503): the ByteByteGo status guide lists only the five classes
- Public-key cryptography, symmetric-key algorithm, Diffie-Hellman key exchange (used as prerequisites, no page crawled): suggested "Public-key cryptography", "Diffie-Hellman key exchange"
- Public key certificate and Certificate authority as their own pages: suggested "Public key certificate", "Certificate authority", "X.509"
- Man-in-the-middle attack (HTTPS and TLS both turn on it; no page crawled): suggested "Man-in-the-middle attack"
- HTTP Strict Transport Security and SSL stripping (one paragraph in HTTPS): suggested "HTTP Strict Transport Security"
- TLS termination at a load balancer or reverse proxy (not in any sentence): suggested a Singh or ByteByteGo page on TLS termination
- Online Certificate Status Protocol: suggested "Online Certificate Status Protocol"
- Status 429 Too Many Requests, 101 Switching Protocols details, 100-continue/Expect: 429 is not in RFC 9110; suggested rfc>6585
- HTTP Upgrade header and the WebSocket handshake (RFC 9110 section 7.8 is cut here): covered by the WebSocket chapter, suggested rfc>6455
- Content codings (gzip, deflate, compress) and compression: suggested "HTTP compression"
- Cookies and state management: suggested rfc>6265
- Idempotency keys for POST (practice used by payment APIs): not in any sentence; suggested a payment-system guide
- Host header and name-based virtual hosting (one sentence in RFC 9110 section 7.2): suggested "Virtual hosting"
- Cache-Control directives stale-while-revalidate and stale-if-error, immutable (RFC 5861, RFC 8246): not in RFC 9111; suggested rfc>5861
- CDN edge caching and cache purging as practice (RFC 9111 describes only the protocol rules): suggested a CDN chapter page

# http-https-and-tls gaps (gap-fill gf04, chunks 05-09)

- QUIC as its own page or rfc>9000: HTTP/3 and QUIC is anchored on the Wikipedia HTTP/3 page; QUIC internals (streams, 0-RTT, connection IDs) have no sentences
- HPACK and QPACK header compression: only named, no explanation; suggested rfc>7541, rfc>9204
- HTTP Strict Transport Security and SSL stripping defense: suggested rfc>6797
- Certificate Transparency: only two sentences on the Man-in-the-middle attack page; suggested "Certificate Transparency" or rfc>6962
- Online Certificate Status Protocol and OCSP stapling: suggested "OCSP stapling"
- Cross-site request forgery and Cross-site scripting as their own concepts (cookie entry names them): suggested "Cross-site request forgery", "Cross-site scripting"
- Cookie standard rfc>6265 (Set-Cookie attributes, SameSite): the Wikipedia page is the only source
- RSA and digital signature algorithms (Public-key cryptography names them only): suggested "RSA (cryptosystem)", "Digital signature"
- TLS termination at a load balancer or reverse proxy: not in any sentence
- Symmetric-key algorithm / Hybrid cryptosystem as own pages: suggested "Symmetric-key algorithm", "Hybrid cryptosystem"
- Entries skipped: List of HTTP status codes vendor sections (IIS, Shopify, ArcGIS, cPanel and similar) are product trivia; HTTP cookie history, EU cookie directive and supercookie/zombie cookie parts are privacy law and history; CA industry organizations and named CA incidents are history

- RFC 6797 (HSTS): rfc>6797 (HSTS entry rests on the Wikipedia page only)
- RFC 7541 (HPACK header compression): rfc>7541
- RFC 7301 (ALPN): rfc>7301
- RFC 9114 (HTTP/3) and RFC 9000 (QUIC): rfc>9114, rfc>9000 (HTTP/3 and QUIC entry still rests on Wikipedia HTTP and a guide)
- RFC 9218 (HTTP extensible priorities, replaces the deprecated HTTP/2 priority scheme): rfc>9218
- RFC 5246 / TLS 1.2 handshake: rfc>5246
- OCSP stapling: Wikipedia "OCSP stapling" (named by nginx page and RFC 8446)
- Authenticated encryption (AEAD): Wikipedia "Authenticated encryption"
- Message authentication code: Wikipedia "Message authentication code"
- Stream cipher / Block cipher: Wikipedia "Stream cipher", "Block cipher" (folded into Symmetric-key encryption only as one fact)
- Hash function: still has no entry in these chunks (resolver name)
