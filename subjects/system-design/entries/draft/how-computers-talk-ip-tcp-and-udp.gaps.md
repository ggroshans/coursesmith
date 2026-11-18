# how-computers-talk-ip-tcp-and-udp: gaps (pass b2)

- Internet protocol suite (Wikipedia page, the TCP/IP model as a whole; only the OSI "Comparison with TCP/IP model" section was available)
- Network address translation (Wikipedia page; only the IP address "Address translation" section was available)
- Dynamic Host Configuration Protocol (Wikipedia page; DHCP is covered only inside IP address assignment)
- Address Resolution Protocol and MAC address (data link addressing; only mentioned in passing)
- QUIC (Wikipedia page or RFC 9000; needed for HTTP/3, only touched in a UDP fact)
- Maximum transmission unit and Path MTU Discovery (Wikipedia pages; only IP's "Link capacity" section)
- TCP congestion control algorithms: slow start, congestion avoidance, fast retransmit, fast recovery (Wikipedia "TCP congestion control"; the TCP page only names them)
- Sockets (Wikipedia "Network socket" or Berkeley sockets; used as an idea in TCP/UDP facts but has no page)
- ICMP and traceroute/ping (Wikipedia "Internet Control Message Protocol"; named in IP facts only)
- Round-trip time as a latency measure (Wikipedia "Round-trip delay"; RTT appears in TCP facts without a definition)

Not drafted on purpose: IP version history and IEN documents, IPv4 subnetting history and classful networks, IP address
law (Canada, EU, California), link-local addressing and address conflicts, TCP checksum and UDP pseudo-header
computation, TCP timestamps, TCP offload engines and accelerators, TCP veto and other vulnerabilities beyond the
SYN flood and hijacking summary, OSI cross-layer functions and OSI layers 1, 2, 5, 6 and 7 as separate entries
(summarised inside "OSI model layers"), OSI TP0-TP4 transport classes.
The ByteByteGo "explaining 8 network protocols" guide only lists protocols; HTTP, HTTPS and WebSocket belong to their own chapters.

# how-computers-talk-ip-tcp-and-udp: gaps (gap-fill batch gf02, chunks 05-09)

- End-to-end principle (Wikipedia page; only a few sentences on the Internet protocol suite page)
- Robustness principle (Wikipedia page; only two sentences, not drafted)
- Peer-to-peer (Wikipedia page; the Client-server model page only gives a comparison section)
- STUN and hole punching in WebRTC (Wikipedia "STUN", "TCP hole punching"; the NAT page only names them)
- Neighbor Discovery Protocol and ICMPv6 (Wikipedia pages; named in ARP and ICMP facts only)
- Berkeley sockets / socket programming (Wikipedia "Berkeley sockets"; used in Network socket facts)

Not drafted on purpose: Internet protocol suite and NAT history, DHCP options and message-type tables, ARP packet layout details, ARP stuffing, ICMP control-message tables (source quench, timestamp, address mask), QUIC adoption statistics and source-code table, TCP congestion control niche algorithms (Hybla, Agile-SD, C2TCP, Elastic-TCP, NATCP), Client-server early history and WebAssembly section.

# how-computers-talk-ip-tcp-and-udp gaps (gap-fill gf03, chunk 10)

Skipped on purpose from RFC 9293: user/TCP interface calls (OPEN, SEND, RECEIVE, CLOSE, ABORT, STATUS) and event
processing tables, urgent mechanism (new applications SHOULD NOT use it), IP security compartment and precedence,
TCP options catalogue, glossary, IANA and change-history sections, low watermark settings.
Still wanted: QUIC (rfc>9000 or Wikipedia "QUIC"); TCP congestion control algorithms (Wikipedia "TCP congestion control");
Explicit Congestion Notification; TCP Fast Open; SYN cookies.
