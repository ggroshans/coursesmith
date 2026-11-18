# System design interview questions, beginner to advanced: curriculum

_Reorder by moving entry lines (keep each `<!-- id -->`), then run `coursesmith order lock`. Prerequisites must stay above the entries that build on them._


## Foundations


### What system design is and how interviews work

1. **System design** — Foundational · Concept · Landmark <!-- sysd-found-130 -->
2. **System design interview** — Foundational · Concept · Major · builds on: System design (1) <!-- sysd-found-131 -->
3. **System design building blocks** — Foundational · Classification · Major · builds on: System design (1) <!-- sysd-found-136 -->
4. **Functional requirements** — Foundational · Concept · Minor · builds on: System design (1) <!-- sysd-found-207 -->
5. **Non-functional requirements** — Foundational · Concept · Major · builds on: System design (1), Functional requirements (4) <!-- sysd-found-139 -->
6. **Software architecture** — Foundational · Concept · Major · builds on: System design (1), Non-functional requirements (5) <!-- sysd-found-138 -->
7. **Common scaling problems and fixes** — Intermediate · Practice · Major · builds on: System design building blocks (3), Non-functional requirements (5) <!-- sysd-found-137 -->
8. **Architecture decision records** — Intermediate · Practice · Minor · builds on: Software architecture (6), Non-functional requirements (5) <!-- sysd-found-142 -->
9. **Software architecture activities** — Intermediate · Process · Minor · builds on: Software architecture (6), Non-functional requirements (5) <!-- sysd-found-141 -->
10. **Software architecture erosion** — Intermediate · Concept · Minor · builds on: Software architecture (6), Software architecture activities (9) <!-- sysd-found-143 -->
11. **Requirements engineering** — Intermediate · Concept · Minor · builds on: System design (1), Functional requirements (4), Non-functional requirements (5) <!-- sysd-found-144 -->
12. **Software design pattern** — Intermediate · Concept · Minor · builds on: Software architecture (6) <!-- sysd-found-208 -->
13. **Architectural patterns and styles** — Intermediate · Concept · Minor · builds on: Software architecture (6), Software design pattern (12) <!-- sysd-found-140 -->
14. **Requirements clarification** — Foundational · Practice · Major · builds on: Functional requirements (4), Non-functional requirements (5), System design interview (2) <!-- sysd-found-133 -->
15. **System design interview framework** — Foundational · Process · Landmark · builds on: System design interview (2), Requirements clarification (14), System design building blocks (3) <!-- sysd-found-132 -->
16. **Machine learning systems design** — Intermediate · Concept · Minor · builds on: System design (1), Non-functional requirements (5) <!-- sysd-found-135 -->
17. **Conway's law** — Intermediate · Concept · Minor · builds on: Software architecture (6) <!-- sysd-found-209 -->
18. **Discussing trade-offs in interviews** — Foundational · Practice · Minor · builds on: System design interview framework (15) <!-- sysd-found-134 -->

### Latency, throughput and back-of-the-envelope numbers

19. **Latency** — Foundational · Concept · Landmark <!-- sysd-found-087 -->
20. **Bandwidth** — Foundational · Concept · Major <!-- sysd-found-099 -->
21. **Network latency** — Intermediate · Concept · Major · builds on: Latency (19) <!-- sysd-found-088 -->
22. **Percentile** — Foundational · Concept · Major <!-- sysd-found-192 -->
23. **Tail latency** — Intermediate · Concept · Major · builds on: Latency (19), Percentile (22) <!-- sysd-found-089 -->
24. **Latency numbers to know** — Intermediate · Concept · Major · builds on: Latency (19), Network latency (21) <!-- sysd-found-097 -->
25. **Design trade-offs** — Foundational · Concept · Major · builds on: System design (1) <!-- sysd-found-094 -->
26. **Reducing latency** — Intermediate · Practice · Major · builds on: Latency (19), Network latency (21), Latency numbers to know (24) <!-- sysd-found-095 -->
27. **Round-trip time** — Intermediate · Concept · Minor · builds on: Network latency (21) <!-- sysd-found-194 -->
28. **Website performance metrics** — Intermediate · Classification · Major · builds on: Latency (19), Round-trip time (27) <!-- sysd-found-098 -->
29. **Data size units** — Foundational · Concept · Minor <!-- sysd-found-100 -->
30. **Network throughput** — Intermediate · Concept · Major · builds on: Bandwidth (20), Data size units (29), Latency (19) <!-- sysd-found-090 -->
31. **Goodput** — Intermediate · Concept · Minor · builds on: Network throughput (30) <!-- sysd-found-092 -->
32. **Maximum throughput measures** — Intermediate · Classification · Minor · builds on: Network throughput (30), Bandwidth (20) <!-- sysd-found-091 -->
33. **Latency vs throughput** — Foundational · Concept · Major · builds on: Latency (19), Network throughput (30) <!-- sysd-found-093 -->
34. **Back-of-the-envelope estimation** — Advanced · Method · Major · builds on: Data size units (29), Latency numbers to know (24), Network throughput (30), Latency vs throughput (33) <!-- sysd-found-096 -->
35. **Little's law** — Advanced · Concept · Major · builds on: Latency (19), Network throughput (30), Latency vs throughput (33) <!-- sysd-found-193 -->

### How computers talk: IP, TCP and UDP

36. **OSI model** — Foundational · Concept · Major <!-- sysd-found-024 -->
37. **TCP/IP model** — Foundational · Concept · Major · builds on: OSI model (36) <!-- sysd-found-029 -->
38. **Client-server model** — Foundational · Concept · Major <!-- sysd-found-154 -->
39. **OSI model layers** — Foundational · Classification · Major · builds on: OSI model (36) <!-- sysd-found-025 -->
40. **Transport layer** — Foundational · Concept · Major · builds on: TCP/IP model (37), OSI model layers (39), OSI model (36) <!-- sysd-found-030 -->
41. **Encapsulation and de-encapsulation** — Foundational · Process · Major · builds on: TCP/IP model (37) <!-- sysd-found-019 -->
42. **Transmission Control Protocol** — Foundational · Concept · Landmark · builds on: Transport layer (40) <!-- sysd-found-005 -->
43. **TCP connection setup and teardown** — Intermediate · Process · Major · builds on: Transmission Control Protocol (42), Client-server model (38) <!-- sysd-found-006 -->
44. **Application-layer protocols** — Foundational · Classification · Minor · builds on: TCP/IP model (37), Client-server model (38), Transmission Control Protocol (42) <!-- sysd-found-020 -->
45. **Internet Protocol** — Foundational · Concept · Landmark · builds on: TCP/IP model (37) <!-- sysd-found-001 -->
46. **IP address** — Foundational · Concept · Major · builds on: Internet Protocol (45) <!-- sysd-found-021 -->
47. **User Datagram Protocol** — Foundational · Concept · Major · builds on: Internet Protocol (45), Transport layer (40) <!-- sysd-found-015 -->
48. **Port numbers** — Intermediate · Concept · Major · builds on: IP address (46), Transport layer (40), Client-server model (38), Internet Protocol (45) <!-- sysd-found-011 -->
49. **Network socket** — Intermediate · Concept · Major · builds on: IP address (46), Port numbers (48), Transport layer (40), Transmission Control Protocol (42), User Datagram Protocol (47) <!-- sysd-found-152 -->
50. **IPv4 versus IPv6** — Intermediate · Concept · Major · builds on: IP address (46), Internet Protocol (45) <!-- sysd-found-018 -->
51. **TCP versus UDP** — Foundational · Concept · Major · builds on: Transmission Control Protocol (42), User Datagram Protocol (47) <!-- sysd-found-016 -->
52. **UDP use cases** — Foundational · Concept · Major · builds on: User Datagram Protocol (47), TCP versus UDP (51) <!-- sysd-found-017 -->
53. **Best-effort delivery** — Intermediate · Concept · Major · builds on: Internet Protocol (45), Transport layer (40) <!-- sysd-found-002 -->
54. **TCP reliable delivery** — Intermediate · Concept · Major · builds on: Transmission Control Protocol (42), Best-effort delivery (53) <!-- sysd-found-007 -->
55. **TCP flow control** — Intermediate · Concept · Major · builds on: Transmission Control Protocol (42), TCP reliable delivery (54) <!-- sysd-found-009 -->
56. **IP addressing methods** — Foundational · Classification · Major · builds on: IP address (46), Internet Protocol (45) <!-- sysd-found-003 -->
57. **MTU and IP fragmentation** — Intermediate · Concept · Major · builds on: Internet Protocol (45), Encapsulation and de-encapsulation (41) <!-- sysd-found-004 -->
58. **TCP congestion control** — Intermediate · Concept · Major · builds on: TCP reliable delivery (54), TCP flow control (55), Bandwidth (20), Transmission Control Protocol (42) <!-- sysd-found-010 -->
59. **Address Resolution Protocol** — Intermediate · Concept · Major · builds on: IP address (46), TCP/IP model (37), OSI model layers (39), Internet Protocol (45) <!-- sysd-found-148 -->
60. **Head-of-line blocking** — Intermediate · Concept · Minor · builds on: Transmission Control Protocol (42), TCP reliable delivery (54) <!-- sysd-found-012 -->
61. **QUIC** — Advanced · Concept · Major · builds on: User Datagram Protocol (47), Transmission Control Protocol (42), Head-of-line blocking (60), TCP congestion control (58) <!-- sysd-found-149 -->
62. **Public and private IP addresses** — Foundational · Classification · Minor · builds on: IP address (46) <!-- sysd-found-022 -->
63. **Network address translation** — Intermediate · Concept · Major · builds on: Public and private IP addresses (62), Port numbers (48), IP address (46) <!-- sysd-found-028 -->
64. **Static and dynamic IP addresses** — Foundational · Classification · Minor · builds on: IP address (46) <!-- sysd-found-023 -->
65. **Dynamic Host Configuration Protocol** — Intermediate · Concept · Major · builds on: Static and dynamic IP addresses (64), Client-server model (38), User Datagram Protocol (47), Internet Protocol (45), IP address (46) <!-- sysd-found-146 -->
66. **DHCP lease process** — Intermediate · Process · Major · builds on: Dynamic Host Configuration Protocol (65), IP addressing methods (56) <!-- sysd-found-147 -->
67. **Subnets and CIDR notation** — Intermediate · Concept · Minor · builds on: IP address (46), Internet Protocol (45) <!-- sysd-found-027 -->
68. **TCP retransmission timeout** — Advanced · Method · Major · builds on: TCP reliable delivery (54), Round-trip time (27) <!-- sysd-found-162 -->
69. **TCP segmentation and MSS** — Intermediate · Concept · Major · builds on: Transmission Control Protocol (42), MTU and IP fragmentation (57) <!-- sysd-found-161 -->
70. **Nagle's algorithm** — Intermediate · Method · Minor · builds on: TCP segmentation and MSS (69), TCP reliable delivery (54), Transmission Control Protocol (42) <!-- sysd-found-014 -->
71. **TCP sequence numbers** — Intermediate · Concept · Major · builds on: Transmission Control Protocol (42), TCP reliable delivery (54) <!-- sysd-found-156 -->
72. **Selective acknowledgment** — Intermediate · Method · Minor · builds on: TCP reliable delivery (54), TCP sequence numbers (71) <!-- sysd-found-008 -->
73. **TCP three-way handshake** — Intermediate · Process · Major · builds on: TCP connection setup and teardown (43), TCP sequence numbers (71), Transmission Control Protocol (42) <!-- sysd-found-155 -->
74. **TCP connection states** — Intermediate · Concept · Major · builds on: TCP connection setup and teardown (43), TCP three-way handshake (73), Transmission Control Protocol (42) <!-- sysd-found-157 -->
75. **SYN flood and other TCP attacks** — Intermediate · Concept · Minor · builds on: TCP three-way handshake (73), TCP sequence numbers (71), TCP connection states (74), TCP connection setup and teardown (43) <!-- sysd-found-013 -->
76. **Network layer** — Foundational · Concept · Minor · builds on: TCP/IP model (37), OSI model layers (39), OSI model (36), Internet Protocol (45) <!-- sysd-found-031 -->
77. **Internet Control Message Protocol** — Intermediate · Concept · Major · builds on: Internet Protocol (45), Network layer (76), IP address (46) <!-- sysd-found-153 -->
78. **Choosing between TCP and UDP** — Foundational · Practice · Major · builds on: TCP versus UDP (51), UDP use cases (52), Transmission Control Protocol (42), User Datagram Protocol (47) <!-- sysd-found-026 -->
79. **NAT traversal** — Advanced · Method · Minor · builds on: Network address translation (63), Port numbers (48), Transmission Control Protocol (42), Public and private IP addresses (62) <!-- sysd-found-145 -->
80. **Delayed acknowledgment** — Intermediate · Method · Minor · builds on: TCP reliable delivery (54) <!-- sysd-found-164 -->
81. **Silly window syndrome** — Advanced · Concept · Minor · builds on: TCP flow control (55), TCP segmentation and MSS (69) <!-- sysd-found-165 -->
82. **TCP half-close** — Intermediate · Concept · Minor · builds on: TCP connection setup and teardown (43), TCP connection states (74) <!-- sysd-found-160 -->
83. **TCP keep-alive** — Intermediate · Method · Minor · builds on: Transmission Control Protocol (42), TCP connection states (74) <!-- sysd-found-163 -->
84. **TCP reset** — Intermediate · Concept · Minor · builds on: TCP connection states (74), TCP sequence numbers (71) <!-- sysd-found-159 -->
85. **TCP segment header** — Intermediate · Concept · Minor · builds on: Port numbers (48), TCP sequence numbers (71), TCP flow control (55), TCP connection setup and teardown (43), Transmission Control Protocol (42) <!-- sysd-found-167 -->
86. **TIME-WAIT state** — Intermediate · Concept · Minor · builds on: TCP connection states (74), TCP connection setup and teardown (43) <!-- sysd-found-158 -->
87. **Zero-window probing** — Advanced · Method · Minor · builds on: TCP flow control (55), TCP reliable delivery (54) <!-- sysd-found-166 -->
88. **Path MTU Discovery** — Intermediate · Method · Minor · builds on: MTU and IP fragmentation (57), Internet Control Message Protocol (77) <!-- sysd-found-150 -->
89. **TCP congestion control algorithms** — Advanced · Classification · Minor · builds on: TCP congestion control (58), TCP reliable delivery (54) <!-- sysd-found-151 -->

### The Domain Name System

90. **Domain Name System** — Foundational · Concept · Landmark · builds on: IP address (46), Client-server model (38) <!-- sysd-found-101 -->
91. **Anycast** — Intermediate · Concept · Major · builds on: IP address (46), Network layer (76), Internet Protocol (45), Domain Name System (90) <!-- sysd-found-201 -->
92. **DNS transport protocols** — Intermediate · Classification · Major · builds on: Domain Name System (90), User Datagram Protocol (47), Transmission Control Protocol (42), Port numbers (48) <!-- sysd-found-114 -->
93. **Domain name hierarchy** — Foundational · Concept · Major · builds on: Domain Name System (90) <!-- sysd-found-102 -->
94. **Top-level domain** — Foundational · Concept · Major · builds on: Domain name hierarchy (93), Domain Name System (90) <!-- sysd-found-202 -->
95. **Time to live and hop limit** — Foundational · Concept · Minor · builds on: Internet Protocol (45) <!-- sysd-found-203 -->
96. **DNS resource records** — Intermediate · Concept · Minor · builds on: Domain Name System (90), Domain name hierarchy (93), Time to live and hop limit (95) <!-- sysd-found-109 -->
97. **Domain name registration** — Foundational · Concept · Minor · builds on: Domain name hierarchy (93), Top-level domain (94) <!-- sysd-found-117 -->
98. **HOSTS.TXT and DNS origins** — Foundational · Event · Minor · builds on: Domain Name System (90) <!-- sysd-found-118 -->
99. **DNS record types** — Foundational · Classification · Major · builds on: DNS resource records (96), IP address (46), IPv4 versus IPv6 (50) <!-- sysd-found-110 -->
100. **Reverse DNS lookup** — Intermediate · Method · Minor · builds on: DNS record types (99), IP address (46) <!-- sysd-found-111 -->
101. **CNAME records and aliases** — Intermediate · Concept · Minor · builds on: DNS record types (99), DNS resource records (96) <!-- sysd-found-126 -->
102. **Specialized DNS record types** — Intermediate · Classification · Major · builds on: DNS record types (99), DNS resource records (96), CNAME records and aliases (101) <!-- sysd-found-204 -->
103. **DNS components** — Intermediate · Concept · Minor · builds on: Domain Name System (90), Domain name hierarchy (93), DNS resource records (96) <!-- sysd-found-121 -->
104. **DNS design goals** — Intermediate · Concept · Minor · builds on: Domain Name System (90), HOSTS.TXT and DNS origins (98), Domain name hierarchy (93) <!-- sysd-found-119 -->
105. **Domain name registrar** — Foundational · Concept · Minor · builds on: Domain name registration (97), Top-level domain (94) <!-- sysd-found-206 -->
106. **Subdomain** — Foundational · Concept · Minor · builds on: Domain name hierarchy (93) <!-- sysd-found-129 -->
107. **DNS lookup process** — Foundational · Process · Landmark · builds on: Domain Name System (90), Domain name hierarchy (93), Top-level domain (94) <!-- sysd-found-105 -->
108. **DNS resolver** — Intermediate · Concept · Major · builds on: DNS lookup process (107), DNS components (103), Client-server model (38) <!-- sysd-found-106 -->
109. **DNS caching and TTL** — Intermediate · Method · Major · builds on: DNS lookup process (107), DNS resolver (108), DNS resource records (96), Time to live and hop limit (95) <!-- sysd-found-108 -->
110. **DNS load distribution** — Intermediate · Method · Major · builds on: DNS record types (99), IP address (46), DNS resolver (108), DNS resource records (96) <!-- sysd-found-112 -->
111. **DNS security issues** — Intermediate · Concept · Major · builds on: Domain Name System (90), DNS resolver (108), DNS caching and TTL (109), DNS transport protocols (92) <!-- sysd-found-115 -->
112. **Recursive and iterative queries** — Intermediate · Classification · Major · builds on: DNS lookup process (107), DNS resolver (108) <!-- sysd-found-107 -->
113. **DNSSEC** — Intermediate · Concept · Major · builds on: DNS security issues (111), DNS resource records (96), DNS resolver (108), Domain Name System (90) <!-- sysd-found-195 -->
114. **Round-robin DNS** — Intermediate · Method · Major · builds on: DNS load distribution (110), DNS record types (99), IP address (46), DNS resource records (96), DNS caching and TTL (109) <!-- sysd-found-200 -->
115. **DNS cache poisoning** — Intermediate · Method · Major · builds on: DNS caching and TTL (109), DNS resolver (108), DNS security issues (111) <!-- sysd-found-199 -->
116. **DNS privacy** — Intermediate · Debate · Minor · builds on: DNS transport protocols (92), DNS resolver (108), DNS security issues (111) <!-- sysd-found-116 -->
117. **Root and TLD name servers** — Foundational · Concept · Major · builds on: DNS lookup process (107), Top-level domain (94) <!-- sysd-found-128 -->
118. **Stub resolver** — Intermediate · Concept · Minor · builds on: DNS resolver (108), Recursive and iterative queries (112) <!-- sysd-found-124 -->
119. **Authoritative name server** — Intermediate · Concept · Major · builds on: DNS lookup process (107), DNS components (103), Domain Name System (90) <!-- sysd-found-104 -->
120. **DNS delegation** — Intermediate · Method · Major · builds on: Domain name hierarchy (93), Authoritative name server (119) <!-- sysd-found-103 -->
121. **DNS zone** — Intermediate · Concept · Major · builds on: DNS delegation (120), Authoritative name server (119), Domain name hierarchy (93) <!-- sysd-found-122 -->
122. **DNS zone transfer** — Intermediate · Process · Major · builds on: DNS zone (121), Authoritative name server (119) <!-- sysd-found-123 -->
123. **DNS availability over consistency** — Intermediate · Concept · Major · builds on: DNS caching and TTL (109), DNS zone transfer (122), DNS design goals (104) <!-- sysd-found-120 -->
124. **DNSSEC chain of trust** — Advanced · Method · Major · builds on: DNSSEC (113), DNS delegation (120), Root and TLD name servers (117), Specialized DNS record types (102) <!-- sysd-found-196 -->
125. **DNSSEC denial of existence** — Advanced · Method · Minor · builds on: DNSSEC (113), Specialized DNS record types (102), DNS zone (121), DNS resource records (96) <!-- sysd-found-198 -->
126. **DNSSEC key management** — Advanced · Method · Minor · builds on: DNSSEC (113), DNSSEC chain of trust (124), DNS caching and TTL (109) <!-- sysd-found-197 -->
127. **Split-horizon DNS** — Intermediate · Method · Minor · builds on: Authoritative name server (119), DNS resolver (108), Public and private IP addresses (62), Domain Name System (90) <!-- sysd-found-205 -->
128. **DNS message format** — Intermediate · Concept · Minor · builds on: DNS resource records (96), Authoritative name server (119) <!-- sysd-found-113 -->
129. **DNS standard queries** — Intermediate · Concept · Minor · builds on: DNS resource records (96), DNS record types (99), DNS components (103), DNS message format (128) <!-- sysd-found-127 -->
130. **DNS resolver algorithm** — Advanced · Process · Minor · builds on: DNS lookup process (107), DNS resolver (108), Recursive and iterative queries (112), DNS caching and TTL (109), DNS standard queries (129) <!-- sysd-found-125 -->

### HTTP, HTTPS and TLS

131. **HTTP** — Foundational · Concept · Landmark · builds on: Client-server model (38), Application-layer protocols (44), Transmission Control Protocol (42) <!-- sysd-found-032 -->
132. **Public-key cryptography** — Intermediate · Concept · Major <!-- sysd-found-173 -->
133. **HTTP request and response messages** — Foundational · Concept · Major · builds on: HTTP (131) <!-- sysd-found-033 -->
134. **HTTP persistent connections** — Intermediate · Concept · Major · builds on: HTTP request and response messages (133), Transmission Control Protocol (42), TCP connection setup and teardown (43), HTTP (131) <!-- sysd-found-038 -->
135. **HTTP request methods** — Foundational · Classification · Major · builds on: HTTP request and response messages (133) <!-- sysd-found-034 -->
136. **HTTP statelessness and sessions** — Foundational · Concept · Major · builds on: HTTP (131), HTTP request and response messages (133) <!-- sysd-found-042 -->
137. **HTTP cookie** — Intermediate · Concept · Major · builds on: HTTP statelessness and sessions (136), HTTP request and response messages (133), HTTP (131) <!-- sysd-found-168 -->
138. **HTTP status codes** — Foundational · Classification · Major · builds on: HTTP request and response messages (133) <!-- sysd-found-037 -->
139. **Idempotent HTTP methods** — Intermediate · Concept · Major · builds on: HTTP request methods (135) <!-- sysd-found-036 -->
140. **Safe HTTP methods** — Intermediate · Concept · Major · builds on: HTTP request methods (135) <!-- sysd-found-035 -->
141. **Digital certificates and certificate authorities** — Intermediate · Concept · Major · builds on: Public-key cryptography (132) <!-- sysd-found-053 -->
142. **Symmetric-key encryption** — Intermediate · Concept · Major <!-- sysd-found-181 -->
143. **Diffie-Hellman key exchange** — Advanced · Method · Major · builds on: Public-key cryptography (132), Symmetric-key encryption (142) <!-- sysd-found-174 -->
144. **Certificate chain of trust** — Intermediate · Concept · Major · builds on: Digital certificates and certificate authorities (141), Public-key cryptography (132) <!-- sysd-found-175 -->
145. **Certificate authority trust risks** — Intermediate · Concept · Major · builds on: Digital certificates and certificate authorities (141), Certificate chain of trust (144) <!-- sysd-found-178 -->
146. **RSA cryptosystem** — Intermediate · Concept · Major · builds on: Public-key cryptography (132) <!-- sysd-found-191 -->
147. **HTTP authentication** — Intermediate · Concept · Minor · builds on: HTTP request and response messages (133), HTTP status codes (138), HTTP statelessness and sessions (136) <!-- sysd-found-043 -->
148. **HTTP client error status codes** — Foundational · Classification · Major · builds on: HTTP status codes (138) <!-- sysd-found-072 -->
149. **HTTP intermediaries** — Intermediate · Concept · Major · builds on: HTTP (131), HTTP request and response messages (133) <!-- sysd-found-062 -->
150. **HTTP redirection status codes** — Intermediate · Classification · Major · builds on: HTTP status codes (138) <!-- sysd-found-071 -->
151. **HTTP server error status codes** — Intermediate · Classification · Major · builds on: HTTP status codes (138) <!-- sysd-found-073 -->
152. **Additional HTTP status codes** — Intermediate · Classification · Minor · builds on: HTTP status codes (138), HTTP client error status codes (148), HTTP server error status codes (151) <!-- sysd-found-190 -->
153. **HTTP caching** — Intermediate · Concept · Major · builds on: HTTP request and response messages (133), HTTP request methods (135), HTTP intermediaries (149) <!-- sysd-found-077 -->
154. **HTTP cache freshness** — Intermediate · Concept · Major · builds on: HTTP caching (153) <!-- sysd-found-079 -->
155. **Certificate revocation** — Advanced · Concept · Minor · builds on: Digital certificates and certificate authorities (141), Public-key cryptography (132) <!-- sysd-found-054 -->
156. **What happens when you type a URL** — Foundational · Process · Major · builds on: DNS lookup process (107), IP address (46), Transmission Control Protocol (42), HTTP (131), HTTP request and response messages (133), Domain Name System (90) <!-- sysd-found-044 -->
157. **HTTP versions** — Intermediate · Classification · Major · builds on: HTTP (131), HTTP persistent connections (134), Transmission Control Protocol (42), User Datagram Protocol (47) <!-- sysd-found-039 -->
158. **HTTP/2** — Intermediate · Concept · Major · builds on: HTTP versions (157), HTTP persistent connections (134), HTTP request and response messages (133), Head-of-line blocking (60) <!-- sysd-found-040 -->
159. **HTTP/3 and QUIC** — Intermediate · Concept · Major · builds on: HTTP/2 (158), User Datagram Protocol (47), QUIC (61), Head-of-line blocking (60) <!-- sysd-found-041 -->
160. **HTTP/2 streams and multiplexing** — Intermediate · Concept · Major · builds on: HTTP/2 (158), HTTP persistent connections (134) <!-- sysd-found-182 -->
161. **HTTP pipelining** — Intermediate · Concept · Minor · builds on: HTTP persistent connections (134), HTTP request and response messages (133), Head-of-line blocking (60) <!-- sysd-found-170 -->
162. **Certificate validation levels** — Intermediate · Classification · Minor · builds on: Digital certificates and certificate authorities (141), Domain Name System (90), Certificate chain of trust (144) <!-- sysd-found-177 -->
163. **Non-standard HTTP status codes** — Intermediate · Classification · Minor · builds on: HTTP status codes (138), HTTP client error status codes (148), HTTP server error status codes (151) <!-- sysd-found-172 -->
164. **HTTP extensibility** — Intermediate · Concept · Minor · builds on: HTTP request and response messages (133), HTTP request methods (135), HTTP status codes (138), HTTP authentication (147), HTTP (131) <!-- sysd-found-076 -->
165. **HTTP informational status codes** — Intermediate · Classification · Minor · builds on: HTTP status codes (138) <!-- sysd-found-171 -->
166. **HTTP resources and representations** — Intermediate · Concept · Minor · builds on: HTTP (131) <!-- sysd-found-061 -->
167. **HTTP content type, encoding and length** — Intermediate · Concept · Minor · builds on: HTTP request and response messages (133), HTTP resources and representations (166) <!-- sysd-found-066 -->
168. **HTTP content negotiation** — Intermediate · Concept · Major · builds on: HTTP resources and representations (166), HTTP content type, encoding and length (167) <!-- sysd-found-064 -->
169. **HTTP success status codes** — Foundational · Classification · Minor · builds on: HTTP status codes (138) <!-- sysd-found-070 -->
170. **HTTP/2 connection management** — Advanced · Concept · Minor · builds on: HTTP/2 (158), HTTP persistent connections (134), HTTP/2 streams and multiplexing (160) <!-- sysd-found-187 -->
171. **HTTP/2 flow control** — Advanced · Concept · Minor · builds on: HTTP/2 streams and multiplexing (160), TCP flow control (55) <!-- sysd-found-183 -->
172. **HTTP/2 header compression** — Intermediate · Concept · Minor · builds on: HTTP request and response messages (133), HTTP/2 (158) <!-- sysd-found-184 -->
173. **HTTP/2 server push** — Intermediate · Concept · Minor · builds on: HTTP/2 (158), HTTP/2 streams and multiplexing (160), Safe HTTP methods (140) <!-- sysd-found-185 -->
174. **Keeping sensitive data out of URLs** — Foundational · Practice · Minor · builds on: HTTP request methods (135), HTTP request and response messages (133) <!-- sysd-found-075 -->
175. **POST versus PUT** — Intermediate · Concept · Minor · builds on: HTTP request methods (135), Idempotent HTTP methods (139), HTTP resources and representations (166) <!-- sysd-found-063 -->
176. **Vary header** — Intermediate · Concept · Minor · builds on: HTTP content negotiation (168), HTTP request and response messages (133) <!-- sysd-found-065 -->
177. **Cache-Control header** — Intermediate · Concept · Minor · builds on: HTTP caching (153), HTTP request and response messages (133) <!-- sysd-found-082 -->
178. **Cache-Control request directives** — Intermediate · Classification · Minor · builds on: Cache-Control header (177), HTTP cache freshness (154) <!-- sysd-found-084 -->
179. **Shared and private HTTP caches** — Intermediate · Concept · Minor · builds on: HTTP caching (153), HTTP intermediaries (149) <!-- sysd-found-085 -->
180. **HTTP cache security risks** — Advanced · Concept · Minor · builds on: HTTP caching (153), Shared and private HTTP caches (179) <!-- sysd-found-086 -->
181. **Transport Layer Security** — Intermediate · Concept · Landmark · builds on: Public-key cryptography (132), Symmetric-key encryption (142), Transmission Control Protocol (42) <!-- sysd-found-049 -->
182. **HTTPS** — Foundational · Concept · Landmark · builds on: HTTP (131), Symmetric-key encryption (142), Public-key cryptography (132), Transport Layer Security (181) <!-- sysd-found-048 -->
183. **Man-in-the-middle attack** — Intermediate · Concept · Major · builds on: Client-server model (38), HTTP (131), Public-key cryptography (132), Transport Layer Security (181) <!-- sysd-found-179 -->
184. **Securing cookies** — Intermediate · Practice · Major · builds on: HTTP cookie (137), HTTPS (182), Man-in-the-middle attack (183), Transport Layer Security (181) <!-- sysd-found-169 -->
185. **Datagram Transport Layer Security** — Advanced · Concept · Minor · builds on: Transport Layer Security (181), User Datagram Protocol (47) <!-- sysd-found-060 -->
186. **HTTP Strict Transport Security** — Intermediate · Concept · Major · builds on: HTTPS (182), Man-in-the-middle attack (183), HTTP redirection status codes (150), Transport Layer Security (181) <!-- sysd-found-180 -->
187. **HTTP origins and certificate verification** — Intermediate · Concept · Minor · builds on: HTTPS (182), Digital certificates and certificate authorities (141), Port numbers (48) <!-- sysd-found-074 -->
188. **Secure Sockets Layer** — Foundational · Concept · Minor · builds on: HTTPS (182), Transport Layer Security (181) <!-- sysd-found-046 -->
189. **Forward secrecy** — Advanced · Concept · Major · builds on: Public-key cryptography (132) <!-- sysd-found-052 -->
190. **TLS versions** — Advanced · Classification · Minor · builds on: Transport Layer Security (181), Secure Sockets Layer (188), Forward secrecy (189) <!-- sysd-found-055 -->
191. **TLS handshake** — Intermediate · Process · Major · builds on: Transport Layer Security (181), Digital certificates and certificate authorities (141), Public-key cryptography (132) <!-- sysd-found-050 -->
192. **Server Name Indication** — Advanced · Concept · Minor · builds on: TLS handshake (191), Digital certificates and certificate authorities (141) <!-- sysd-found-057 -->
193. **TLS cipher suites and key exchange** — Advanced · Classification · Minor · builds on: TLS handshake (191), Symmetric-key encryption (142), Public-key cryptography (132), Diffie-Hellman key exchange (143), RSA cryptosystem (146) <!-- sysd-found-056 -->
194. **TLS 1.3** — Advanced · Concept · Major · builds on: TLS handshake (191), TLS versions (190), Forward secrecy (189), TLS cipher suites and key exchange (193) <!-- sysd-found-188 -->
195. **TLS interception** — Advanced · Concept · Minor · builds on: TLS handshake (191), Man-in-the-middle attack (183), HTTP intermediaries (149), Digital certificates and certificate authorities (141) <!-- sysd-found-059 -->
196. **Limits of HTTPS protection** — Intermediate · Concept · Minor · builds on: HTTPS (182), TLS handshake (191), Man-in-the-middle attack (183) <!-- sysd-found-058 -->
197. **Starting an HTTP/2 connection** — Intermediate · Process · Minor · builds on: HTTP/2 (158), TLS handshake (191), Server Name Indication (192) <!-- sysd-found-186 -->
198. **Mutual TLS** — Intermediate · Concept · Minor · builds on: TLS handshake (191), Digital certificates and certificate authorities (141), Public-key cryptography (132), Transport Layer Security (181) <!-- sysd-found-047 -->
199. **Types of TLS certificate** — Intermediate · Classification · Minor · builds on: Digital certificates and certificate authorities (141), Subdomain (106), Mutual TLS (198), Certificate chain of trust (144) <!-- sysd-found-176 -->
200. **Symmetric session keys in HTTPS** — Intermediate · Concept · Minor · builds on: HTTPS (182), Public-key cryptography (132), Symmetric-key encryption (142), TLS handshake (191) <!-- sysd-found-045 -->
201. **TLS session resumption** — Advanced · Method · Major · builds on: TLS handshake (191), Symmetric session keys in HTTPS (200) <!-- sysd-found-051 -->
202. **TLS 0-RTT early data** — Advanced · Method · Major · builds on: TLS 1.3 (194), TLS session resumption (201), Round-trip time (27), Idempotent HTTP methods (139) <!-- sysd-found-189 -->
203. **HTTP conditional requests** — Intermediate · Concept · Major · builds on: HTTP request methods (135), HTTP request and response messages (133), HTTP resources and representations (166) <!-- sysd-found-067 -->
204. **HTTP range requests** — Intermediate · Concept · Minor · builds on: HTTP request methods (135), HTTP content type, encoding and length (167), HTTP conditional requests (203) <!-- sysd-found-069 -->
205. **HTTP validators and entity tags** — Intermediate · Concept · Minor · builds on: HTTP resources and representations (166), HTTP conditional requests (203) <!-- sysd-found-068 -->
206. **HTTP cache validation** — Intermediate · Process · Major · builds on: HTTP caching (153), HTTP conditional requests (203), HTTP validators and entity tags (205) <!-- sysd-found-080 -->
207. **Cache-Control response directives** — Intermediate · Classification · Major · builds on: Cache-Control header (177), HTTP cache freshness (154), HTTP cache validation (206), Shared and private HTTP caches (179) <!-- sysd-found-083 -->
208. **HTTP cache invalidation** — Intermediate · Concept · Minor · builds on: HTTP caching (153), HTTP cache validation (206), Safe HTTP methods (140) <!-- sysd-found-081 -->
209. **Storing and reusing HTTP cached responses** — Intermediate · Process · Minor · builds on: HTTP caching (153), HTTP cache freshness (154), HTTP cache validation (206), Vary header (176) <!-- sysd-found-078 -->

## Building blocks


### Algorithms behind the systems

210. **Hash function** — Intermediate · Concept · Major <!-- sysd-reliab-106 -->
211. **Base64** — Foundational · Concept · Major <!-- sysd-reliab-117 -->
212. **Hash collision** — Intermediate · Concept · Major · builds on: Hash function (210) <!-- sysd-reliab-107 -->
213. **Bloom filter** — Intermediate · Concept · Major · builds on: Hash function (210), Hash collision (212) <!-- sysd-reliab-001 -->
214. **Quadtree** — Intermediate · Concept · Major <!-- sysd-reliab-006 -->
215. **MD5** — Intermediate · Concept · Minor · builds on: Hash function (210), Hash collision (212) <!-- sysd-reliab-110 -->
216. **K-d tree** — Advanced · Method · Major · builds on: Quadtree (214) <!-- sysd-reliab-116 -->
217. **Trie** — Intermediate · Concept · Major <!-- sysd-reliab-113 -->
218. **Z-order curve** — Advanced · Method · Major · builds on: Quadtree (214) <!-- sysd-reliab-114 -->
219. **Geohash** — Intermediate · Method · Major <!-- sysd-reliab-005 -->
220. **Hilbert curve** — Advanced · Method · Minor · builds on: Z-order curve (218) <!-- sysd-reliab-115 -->
221. **Similarity hashing** — Advanced · Concept · Minor · builds on: Hash function (210) <!-- sysd-reliab-109 -->
222. **String hashing** — Intermediate · Method · Minor · builds on: Hash function (210) <!-- sysd-reliab-108 -->
223. **Distributed unique ID generation** — Intermediate · Classification · Major <!-- sysd-reliab-008 -->
224. **Universally unique identifier** — Intermediate · Concept · Major · builds on: Distributed unique ID generation (223) <!-- sysd-reliab-013 -->
225. **Snowflake ID** — Intermediate · Method · Major · builds on: Distributed unique ID generation (223) <!-- sysd-reliab-012 -->
226. **UUID versions** — Advanced · Classification · Major · builds on: Universally unique identifier (224), Hash function (210), Snowflake ID (225) <!-- sysd-reliab-014 -->
227. **UUID best practices** — Advanced · Practice · Major · builds on: Universally unique identifier (224), UUID versions (226) <!-- sysd-reliab-118 -->
228. **Count-min sketch** — Advanced · Method · Major · builds on: Hash function (210), Hash collision (212), Bloom filter (213) <!-- sysd-reliab-111 -->
229. **Merkle tree** — Intermediate · Method · Major · builds on: Hash function (210) <!-- sysd-reliab-112 -->
230. **HyperLogLog** — Advanced · Concept · Major · builds on: Hash function (210) <!-- sysd-reliab-010 -->
231. **Cache filtering with a Bloom filter** — Intermediate · Method · Minor · builds on: Bloom filter (213) <!-- sysd-reliab-004 -->
232. **Counting Bloom filter** — Advanced · Method · Minor · builds on: Bloom filter (213) <!-- sysd-reliab-002 -->
233. **Bloom filter alternatives** — Advanced · Concept · Minor · builds on: Bloom filter (213), Counting Bloom filter (232), Hash function (210) <!-- sysd-reliab-003 -->
234. **Quadtree types** — Advanced · Classification · Minor · builds on: Quadtree (214) <!-- sysd-reliab-011 -->
235. **Limits of geohash proximity search** — Advanced · Concept · Minor · builds on: Geohash (219), Z-order curve (218) <!-- sysd-reliab-009 -->
236. **Nearby search with a quadtree** — Intermediate · Method · Minor · builds on: Quadtree (214) <!-- sysd-reliab-007 -->

### Load balancing

237. **Load balancing** — Foundational · Concept · Landmark · builds on: Client-server model (38) <!-- sysd-blocks-112 -->
238. **DNS load balancing** — Intermediate · Method · Major · builds on: Load balancing (237), DNS load distribution (110), Round-robin DNS (114), Domain Name System (90) <!-- sysd-blocks-118 -->
239. **Load balancing algorithms** — Intermediate · Classification · Major · builds on: Load balancing (237) <!-- sysd-blocks-114 -->
240. **Session persistence** — Intermediate · Method · Major · builds on: Load balancing (237), HTTP statelessness and sessions (136) <!-- sysd-blocks-120 -->
241. **Static and dynamic load balancing** — Intermediate · Classification · Major · builds on: Load balancing (237), Load balancing algorithms (239) <!-- sysd-blocks-113 -->
242. **Client-side load balancing** — Intermediate · Method · Minor · builds on: Load balancing (237), Load balancing algorithms (239), IP address (46) <!-- sysd-blocks-119 -->
243. **Master-worker load balancing** — Advanced · Method · Minor · builds on: Static and dynamic load balancing (241), Load balancing (237) <!-- sysd-blocks-127 -->
244. **Round robin load balancing** — Foundational · Method · Minor · builds on: Load balancing (237) <!-- sysd-blocks-115 -->
245. **Session state storage** — Intermediate · Classification · Minor · builds on: Session persistence (240), HTTP statelessness and sessions (136), HTTP cookie (137), Load balancing (237) <!-- sysd-blocks-121 -->
246. **Work stealing** — Advanced · Method · Minor · builds on: Static and dynamic load balancing (241), Load balancing (237) <!-- sysd-blocks-128 -->
247. **Layer 4 and layer 7 load balancing** — Intermediate · Classification · Major · builds on: Load balancing (237), OSI model layers (39), Port numbers (48), HTTP request and response messages (133), OSI model (36) <!-- sysd-blocks-116 -->
248. **Hardware, software and cloud load balancers** — Foundational · Classification · Minor · builds on: Load balancing (237) <!-- sysd-blocks-117 -->
249. **Global server load balancing** — Intermediate · Method · Minor · builds on: Load balancing (237), DNS load balancing (238), Anycast (91), Domain Name System (90) <!-- sysd-blocks-126 -->
250. **Health checks** — Intermediate · Practice · Minor · builds on: Load balancing (237) <!-- sysd-blocks-122 -->
251. **Load balancer failover** — Intermediate · Practice · Major · builds on: Load balancing (237), Health checks (250) <!-- sysd-blocks-123 -->
252. **TLS termination** — Intermediate · Method · Minor · builds on: Load balancing (237), Transport Layer Security (181), TLS handshake (191), HTTPS (182) <!-- sysd-blocks-124 -->
253. **Load balancer features** — Intermediate · Classification · Major · builds on: Load balancing (237), Layer 4 and layer 7 load balancing (247), TLS termination (252) <!-- sysd-blocks-125 -->

### Proxies and API gateways

254. **Proxy server** — Foundational · Concept · Major · builds on: Client-server model (38), HTTP intermediaries (149), HTTP (131), IP address (46) <!-- sysd-blocks-129 -->
255. **Forward proxy** — Foundational · Concept · Major · builds on: Proxy server (254) <!-- sysd-blocks-130 -->
256. **Reverse proxy** — Intermediate · Concept · Major · builds on: Proxy server (254), Forward proxy (255), HTTP (131), Load balancing (237) <!-- sysd-blocks-137 -->
257. **HAProxy** — Intermediate · Concept · Minor · builds on: Load balancing (237), Layer 4 and layer 7 load balancing (247), Reverse proxy (256), Load balancer failover (251) <!-- sysd-blocks-191 -->
258. **API gateway** — Intermediate · Concept · Major · builds on: Reverse proxy (256), Load balancing (237) <!-- sysd-blocks-133 -->
259. **Caching proxy** — Intermediate · Concept · Minor · builds on: Proxy server (254), Shared and private HTTP caches (179) <!-- sysd-blocks-132 -->
260. **Nginx** — Intermediate · Concept · Major · builds on: Reverse proxy (256), Load balancing (237), Caching proxy (259) <!-- sysd-blocks-190 -->
261. **Transparent proxy** — Intermediate · Concept · Minor · builds on: Proxy server (254), Forward proxy (255) <!-- sysd-blocks-131 -->
262. **Reverse proxy trade-offs** — Intermediate · Concept · Minor · builds on: Reverse proxy (256) <!-- sysd-blocks-138 -->
263. **API gateway request flow** — Intermediate · Process · Minor · builds on: API gateway (258) <!-- sysd-blocks-134 -->
264. **Reverse proxy vs API gateway vs load balancer** — Intermediate · Classification · Minor · builds on: Reverse proxy (256), API gateway (258), Load balancing (237) <!-- sysd-blocks-136 -->
265. **Backend for frontend pattern** — Intermediate · Method · Minor · builds on: API gateway (258) <!-- sysd-blocks-135 -->
266. **API management** — Intermediate · Concept · Minor · builds on: API gateway (258) <!-- sysd-blocks-189 -->

### Caching

267. **Caching** — Foundational · Concept · Landmark · builds on: Latency (19) <!-- sysd-blocks-001 -->
268. **Locality of reference** — Foundational · Concept · Major · builds on: Caching (267) <!-- sysd-blocks-002 -->
269. **CPU cache** — Intermediate · Concept · Minor · builds on: Caching (267), Locality of reference (268) <!-- sysd-blocks-159 -->
270. **Cache hit ratio** — Intermediate · Concept · Major · builds on: Caching (267) <!-- sysd-blocks-003 -->
271. **Cache eviction policies** — Intermediate · Concept · Major · builds on: Caching (267), Locality of reference (268), Cache hit ratio (270) <!-- sysd-blocks-005 -->
272. **Cache write policies** — Intermediate · Classification · Major · builds on: Caching (267), Cache hit ratio (270) <!-- sysd-blocks-004 -->
273. **Least frequently used** — Intermediate · Method · Major · builds on: Cache eviction policies (271), Locality of reference (268) <!-- sysd-blocks-008 -->
274. **Least recently used** — Intermediate · Method · Major · builds on: Cache eviction policies (271), Locality of reference (268) <!-- sysd-blocks-007 -->
275. **Cache coherence** — Intermediate · Concept · Minor · builds on: Caching (267), CPU cache (269) <!-- sysd-blocks-158 -->
276. **Page cache** — Intermediate · Concept · Minor · builds on: Caching (267), Locality of reference (268) <!-- sysd-blocks-160 -->
277. **Buffer versus cache** — Intermediate · Concept · Minor · builds on: Caching (267), Locality of reference (268) <!-- sysd-blocks-015 -->
278. **Cache prefetching** — Intermediate · Method · Minor · builds on: Caching (267), Locality of reference (268) <!-- sysd-blocks-013 -->
279. **Caching strategies** — Intermediate · Classification · Major · builds on: Caching (267), Cache write policies (272) <!-- sysd-blocks-022 -->
280. **Distributed cache** — Intermediate · Concept · Major · builds on: Caching (267), Client-server model (38) <!-- sysd-blocks-025 -->
281. **Redis** — Intermediate · Concept · Major · builds on: Caching (267), Distributed cache (280) <!-- sysd-blocks-029 -->
282. **Memcached** — Intermediate · Concept · Major · builds on: Caching (267), Distributed cache (280) <!-- sysd-blocks-030 -->
283. **Redis replication and clustering** — Intermediate · Method · Minor · builds on: Redis (281), Distributed cache (280) <!-- sysd-blocks-032 -->
284. **Memoization** — Foundational · Method · Minor · builds on: Caching (267) <!-- sysd-blocks-014 -->
285. **Belady's optimal algorithm** — Advanced · Concept · Minor · builds on: Cache eviction policies (271), Cache hit ratio (270) <!-- sysd-blocks-006 -->
286. **FIFO and random eviction** — Intermediate · Method · Minor · builds on: Cache eviction policies (271), Least recently used (274), Least frequently used (273) <!-- sysd-blocks-011 -->
287. **Most recently used** — Intermediate · Method · Minor · builds on: Least recently used (274), Cache eviction policies (271) <!-- sysd-blocks-009 -->
288. **SIEVE and S3-FIFO** — Advanced · Method · Minor · builds on: FIFO and random eviction (286), Least recently used (274), Cache eviction policies (271) <!-- sysd-blocks-012 -->
289. **Segmented LRU** — Advanced · Method · Minor · builds on: Least recently used (274), Cache eviction policies (271) <!-- sysd-blocks-010 -->
290. **Adaptive replacement cache** — Advanced · Method · Minor · builds on: Least recently used (274), Least frequently used (273), Cache eviction policies (271) <!-- sysd-blocks-161 -->
291. **Caching layers** — Foundational · Classification · Minor · builds on: Caching (267) <!-- sysd-blocks-021 -->
292. **Time to live** — Foundational · Method · Minor · builds on: Caching (267) <!-- sysd-blocks-028 -->
293. **Cache invalidation** — Intermediate · Concept · Major · builds on: Caching (267), Time to live (292), Cache coherence (275) <!-- sysd-blocks-024 -->
294. **Cache-aside** — Intermediate · Method · Major · builds on: Caching (267), Cache hit ratio (270), Caching strategies (279), Time to live (292) <!-- sysd-blocks-023 -->
295. **Cache stampede** — Intermediate · Concept · Major · builds on: Caching (267), Time to live (292), Cache-aside (294) <!-- sysd-blocks-017 -->
296. **Cache stampede mitigation** — Intermediate · Method · Major · builds on: Cache stampede (295), Time to live (292) <!-- sysd-blocks-018 -->
297. **Cache penetration** — Intermediate · Concept · Minor · builds on: Caching (267), Cache-aside (294), Cache hit ratio (270), Bloom filter (213) <!-- sysd-blocks-019 -->
298. **Cache failure modes** — Intermediate · Classification · Minor · builds on: Cache stampede (295), Cache penetration (297), Time to live (292), Caching (267) <!-- sysd-blocks-020 -->
299. **Multi-level caching** — Intermediate · Concept · Minor · builds on: Caching (267), Caching layers (291), CPU cache (269) <!-- sysd-blocks-026 -->
300. **When to use a cache** — Foundational · Practice · Minor · builds on: Caching (267), Locality of reference (268) <!-- sysd-blocks-027 -->
301. **Redis persistence** — Intermediate · Method · Minor · builds on: Redis (281), When to use a cache (300) <!-- sysd-blocks-031 -->
302. **Choosing between Memcached and Redis** — Intermediate · Practice · Major · builds on: Redis (281), Memcached (282), Redis persistence (301), Redis replication and clustering (283), Caching (267), Distributed cache (280) <!-- sysd-blocks-033 -->
303. **Cache purge, refresh and ban** — Intermediate · Method · Minor · builds on: Cache invalidation (293), HTTP cache invalidation (208), Shared and private HTTP caches (179), Caching proxy (259) <!-- sysd-blocks-157 -->
304. **Thundering herd problem** — Intermediate · Concept · Minor · builds on: Cache stampede (295), Caching (267) <!-- sysd-blocks-162 -->
305. **Caching weather forecasts** — Intermediate · Case study · Minor · builds on: Caching (267), Cache hit ratio (270), Locality of reference (268) <!-- sysd-blocks-016 -->

### Content delivery networks

306. **Content delivery network** — Foundational · Concept · Landmark · builds on: Proxy server (254), Caching (267), Network latency (21), Domain Name System (90) <!-- sysd-blocks-069 -->
307. **Peer-to-peer** — Intermediate · Concept · Major · builds on: Client-server model (38), IP address (46) <!-- sysd-blocks-181 -->
308. **DDoS** — Intermediate · Concept · Major · builds on: Client-server model (38), IP address (46), TCP three-way handshake (73), Bandwidth (20) <!-- sysd-blocks-180 -->
309. **CDN origin and edge servers** — Foundational · Concept · Major · builds on: Content delivery network (306), Caching (267) <!-- sysd-blocks-070 -->
310. **Image CDN** — Intermediate · Concept · Minor · builds on: Content delivery network (306), HTTP content negotiation (168), HTTP request and response messages (133) <!-- sysd-blocks-083 -->
311. **Peer-to-peer CDN** — Intermediate · Concept · Minor · builds on: Peer-to-peer (307), Content delivery network (306), CDN origin and edge servers (309) <!-- sysd-blocks-076 -->
312. **Private CDN** — Intermediate · Concept · Minor · builds on: Content delivery network (306), CDN origin and edge servers (309), Reverse proxy (256), Caching proxy (259) <!-- sysd-blocks-077 -->
313. **Telco CDN** — Intermediate · Concept · Minor · builds on: Content delivery network (306), CDN origin and edge servers (309), Bandwidth (20) <!-- sysd-blocks-079 -->
314. **Virtual CDN** — Advanced · Concept · Minor · builds on: Content delivery network (306), CDN origin and edge servers (309) <!-- sysd-blocks-080 -->
315. **CDN request flow** — Intermediate · Process · Major · builds on: CDN origin and edge servers (309), Caching (267), DNS lookup process (107), Content delivery network (306), Domain Name System (90) <!-- sysd-blocks-071 -->
316. **Push and pull CDNs** — Intermediate · Classification · Major · builds on: CDN origin and edge servers (309), CDN request flow (315), Time to live (292), Content delivery network (306), Caching (267) <!-- sysd-blocks-072 -->
317. **CDN request routing** — Intermediate · Method · Major · builds on: Content delivery network (306), CDN origin and edge servers (309), DNS lookup process (107), Global server load balancing (249), Anycast (91), Domain Name System (90), Load balancing (237), IP address (46) <!-- sysd-blocks-073 -->
318. **Content networking techniques** — Intermediate · Concept · Minor · builds on: Content delivery network (306), Caching (267), Load balancing (237), CDN request routing (317) <!-- sysd-blocks-074 -->
319. **Edge content service protocols** — Advanced · Concept · Minor · builds on: CDN origin and edge servers (309), Content networking techniques (318), Application-layer protocols (44), Caching (267), Content delivery network (306) <!-- sysd-blocks-081 -->
320. **End-user mapping with EDNS client subnet** — Advanced · Method · Minor · builds on: CDN request routing (317), DNS resolver (108), Subnets and CIDR notation (67), DNS caching and TTL (109), Domain Name System (90) <!-- sysd-blocks-075 -->
321. **Multi-CDN** — Intermediate · Concept · Minor · builds on: Content delivery network (306), CDN request routing (317) <!-- sysd-blocks-078 -->
322. **Edge computing** — Intermediate · Concept · Major · builds on: Content delivery network (306), CDN origin and edge servers (309), Latency (19), Bandwidth (20) <!-- sysd-blocks-178 -->
323. **Subresource Integrity** — Intermediate · Concept · Minor · builds on: Content delivery network (306), HTTP (131), HTTP origins and certificate verification (187), Hash function (210) <!-- sysd-blocks-179 -->
324. **CDN security and privacy** — Intermediate · Concept · Minor · builds on: Content delivery network (306), DDoS (308), Subresource Integrity (323) <!-- sysd-blocks-082 -->

### Choosing a database

325. **Database** — Foundational · Concept · Major <!-- sysd-blocks-035 -->
326. **Relational database** — Foundational · Concept · Major · builds on: Database (325) <!-- sysd-blocks-044 -->
327. **NoSQL** — Foundational · Concept · Major · builds on: Relational database (326) <!-- sysd-blocks-058 -->
328. **Graph database** — Intermediate · Concept · Major · builds on: NoSQL (327), Relational database (326) <!-- sysd-blocks-061 -->
329. **Document database** — Intermediate · Concept · Major · builds on: NoSQL (327) <!-- sysd-blocks-059 -->
330. **Elasticsearch** — Intermediate · Concept · Major · builds on: Document database (329), HTTP (131) <!-- sysd-q-025 -->
331. **Key-value store** — Foundational · Concept · Major · builds on: NoSQL (327) <!-- sysd-blocks-060 -->
332. **Database management system** — Foundational · Concept · Major · builds on: Database (325) <!-- sysd-blocks-036 -->
333. **Database transaction** — Intermediate · Concept · Major · builds on: Database (325), Database management system (332) <!-- sysd-blocks-039 -->
334. **ACID properties** — Foundational · Concept · Landmark · builds on: Database transaction (333) <!-- sysd-blocks-055 -->
335. **Database models** — Intermediate · Classification · Major · builds on: Database (325), Database management system (332) <!-- sysd-blocks-037 -->
336. **Isolation** — Intermediate · Concept · Major · builds on: Database transaction (333), ACID properties (334) <!-- sysd-blocks-040 -->
337. **Primary and foreign keys** — Foundational · Concept · Major · builds on: Relational database (326) <!-- sysd-blocks-045 -->
338. **Wide-column store** — Intermediate · Concept · Major · builds on: NoSQL (327), Relational database (326), Key-value store (331) <!-- sysd-blocks-062 -->
339. **OLTP and OLAP** — Intermediate · Concept · Major · builds on: Database transaction (333), Relational database (326) <!-- sysd-blocks-051 -->
340. **Data warehouse** — Intermediate · Concept · Major · builds on: OLTP and OLAP (339), Relational database (326) <!-- sysd-blocks-170 -->
341. **Star and snowflake schemas** — Intermediate · Concept · Major · builds on: Data warehouse (340), OLTP and OLAP (339), Relational database (326) <!-- sysd-blocks-052 -->
342. **Online analytical processing** — Advanced · Concept · Major · builds on: OLTP and OLAP (339), Data warehouse (340), Star and snowflake schemas (341), Relational database (326) <!-- sysd-blocks-168 -->
343. **Connection pooling** — Intermediate · Concept · Major · builds on: Database (325), TCP connection setup and teardown (43), Caching (267) <!-- sysd-blocks-176 -->
344. **Database languages** — Foundational · Classification · Minor · builds on: Database management system (332) <!-- sysd-blocks-038 -->
345. **SQL** — Foundational · Concept · Major · builds on: Relational database (326), Database languages (344) <!-- sysd-blocks-066 -->
346. **SQL vs NoSQL databases** — Intermediate · Debate · Landmark · builds on: Relational database (326), NoSQL (327), SQL (345), ACID properties (334) <!-- sysd-blocks-064 -->
347. **Spatial database** — Intermediate · Concept · Major · builds on: Relational database (326), SQL (345) <!-- sysd-blocks-175 -->
348. **MOLAP, ROLAP and HOLAP** — Advanced · Classification · Major · builds on: Online analytical processing (342), Relational database (326) <!-- sysd-blocks-169 -->
349. **Querying and indexing in NoSQL** — Intermediate · Concept · Minor · builds on: NoSQL (327), Document database (329) <!-- sysd-blocks-068 -->
350. **Database constraints** — Intermediate · Concept · Minor · builds on: Relational database (326), Primary and foreign keys (337) <!-- sysd-blocks-046 -->
351. **Relational operations** — Intermediate · Concept · Minor · builds on: Relational database (326), Primary and foreign keys (337), SQL (345) <!-- sysd-blocks-048 -->
352. **Handling relational data in NoSQL** — Advanced · Method · Major · builds on: NoSQL (327), Relational operations (351), Primary and foreign keys (337), Document database (329), Relational database (326) <!-- sysd-blocks-067 -->
353. **Stored procedure** — Intermediate · Concept · Minor · builds on: Database management system (332), SQL (345), Relational database (326) <!-- sysd-blocks-047 -->
354. **Views and materialized views** — Intermediate · Concept · Minor · builds on: Relational database (326), Relational operations (351), SQL (345) <!-- sysd-blocks-050 -->
355. **Vector database** — Intermediate · Concept · Minor · builds on: Database (325) <!-- sysd-blocks-174 -->
356. **Choosing a database by workload** — Intermediate · Practice · Major · builds on: OLTP and OLAP (339), Document database (329), Graph database (328), Vector database (355), Spatial database (347), Relational database (326), NoSQL (327) <!-- sysd-blocks-053 -->
357. **Polyglot persistence** — Intermediate · Practice · Major · builds on: Relational database (326), NoSQL (327), Choosing a database by workload (356) <!-- sysd-blocks-164 -->
358. **BASE consistency model** — Intermediate · Concept · Major · builds on: ACID properties (334), NoSQL (327) <!-- sysd-blocks-056 -->
359. **ACID vs BASE** — Intermediate · Debate · Major · builds on: ACID properties (334), BASE consistency model (358) <!-- sysd-blocks-057 -->
360. **Time series database** — Intermediate · Concept · Minor · builds on: Database (325), NoSQL (327) <!-- sysd-blocks-172 -->
361. **Concurrency control** — Advanced · Concept · Minor · builds on: Database transaction (333), Isolation (336) <!-- sysd-blocks-043 -->
362. **ETL and ELT** — Intermediate · Method · Minor · builds on: Data warehouse (340) <!-- sysd-blocks-171 -->
363. **Multi-model database** — Intermediate · Concept · Minor · builds on: Database models (335), Polyglot persistence (357), Document database (329), Graph database (328), NoSQL (327), Relational database (326) <!-- sysd-blocks-173 -->
364. **NewSQL** — Intermediate · Concept · Minor · builds on: Relational database (326), NoSQL (327), ACID properties (334), OLTP and OLAP (339) <!-- sysd-blocks-163 -->
365. **N+1 query problem** — Intermediate · Concept · Minor · builds on: SQL (345), Relational operations (351), Relational database (326) <!-- sysd-blocks-063 -->
366. **Transaction states** — Intermediate · Process · Minor · builds on: Database transaction (333) <!-- sysd-blocks-065 -->
367. **Database schema** — Foundational · Concept · Minor · builds on: Database (325) <!-- sysd-blocks-049 -->
368. **Multiversion concurrency control** — Advanced · Method · Major · builds on: Concurrency control (361), Isolation (336) <!-- sysd-blocks-054 -->
369. **Two-phase locking** — Advanced · Method · Major · builds on: Concurrency control (361), Database transaction (333) <!-- sysd-blocks-165 -->
370. **PostgreSQL isolation levels** — Advanced · Concept · Major · builds on: Multiversion concurrency control (368) <!-- sysd-blocks-177 -->
371. **Snapshot isolation** — Advanced · Concept · Major · builds on: Multiversion concurrency control (368), Database transaction (333) <!-- sysd-blocks-166 -->
372. **Isolation levels** — Advanced · Classification · Major · builds on: Isolation (336) <!-- sysd-blocks-041 -->
373. **Read phenomena in transactions** — Intermediate · Classification · Major · builds on: Isolation (336), Database transaction (333), Isolation levels (372) <!-- sysd-blocks-042 -->
374. **Write skew** — Advanced · Concept · Major · builds on: Snapshot isolation (371), Read phenomena in transactions (373), Database transaction (333) <!-- sysd-blocks-167 -->

### Indexes, normalization and storage engines

375. **Database normalization** — Intermediate · Process · Landmark · builds on: Relational database (326), Database schema (367), Primary and foreign keys (337) <!-- sysd-blocks-093 -->
376. **Database index** — Intermediate · Concept · Landmark · builds on: Relational database (326), Database (325) <!-- sysd-blocks-084 -->
377. **Hash table** — Intermediate · Concept · Major · builds on: Hash function (210), Key-value store (331) <!-- sysd-blocks-182 -->
378. **B-tree** — Intermediate · Concept · Major · builds on: Database index (376) <!-- sysd-blocks-103 -->
379. **Write-ahead log** — Intermediate · Concept · Major · builds on: ACID properties (334), Database transaction (333) <!-- sysd-blocks-185 -->
380. **Storage engine** — Intermediate · Concept · Major · builds on: Database management system (332), Database index (376) <!-- sysd-blocks-111 -->
381. **Inverted index** — Intermediate · Concept · Major · builds on: Database index (376), Hash table (377) <!-- sysd-blocks-186 -->
382. **R-tree** — Intermediate · Concept · Major · builds on: B-tree (378), Spatial database (347), Database index (376) <!-- sysd-blocks-187 -->
383. **Insertion, update and deletion anomalies** — Intermediate · Concept · Major · builds on: Database normalization (375), Relational database (326) <!-- sysd-blocks-094 -->
384. **B-trees and disk reads** — Intermediate · Concept · Major · builds on: B-tree (378), Database index (376), Latency numbers to know (24) <!-- sysd-blocks-104 -->
385. **B+ tree and B* tree** — Advanced · Concept · Major · builds on: B-tree (378), B-trees and disk reads (384) <!-- sysd-blocks-105 -->
386. **Clustered and non-clustered indexes** — Intermediate · Concept · Major · builds on: Database index (376), Relational database (326) <!-- sysd-blocks-085 -->
387. **Log-structured merge-tree** — Intermediate · Concept · Major · builds on: Database index (376), B-tree (378) <!-- sysd-blocks-108 -->
388. **Denormalization** — Intermediate · Method · Major · builds on: Database normalization (375), Insertion, update and deletion anomalies (383), Relational operations (351) <!-- sysd-blocks-107 -->
389. **Hash collision resolution** — Intermediate · Method · Minor · builds on: Hash table (377), Hash collision (212) <!-- sysd-blocks-183 -->
390. **B-tree versus LSM-tree** — Intermediate · Concept · Major · builds on: B-tree (378), Log-structured merge-tree (387), Database index (376) <!-- sysd-blocks-099 -->
391. **Index data structures** — Intermediate · Classification · Major · builds on: Database index (376) <!-- sysd-blocks-090 -->
392. **PostgreSQL index types** — Intermediate · Classification · Minor · builds on: Index data structures (391), B-tree (378), Hash table (377), Inverted index (381), R-tree (382), Database index (376) <!-- sysd-blocks-188 -->
393. **Skip list** — Intermediate · Concept · Minor <!-- sysd-blocks-184 -->
394. **LSM-tree writes and compaction** — Intermediate · Process · Major · builds on: Log-structured merge-tree (387) <!-- sysd-blocks-109 -->
395. **B-tree insertion and deletion** — Advanced · Process · Minor · builds on: B-tree (378), B-trees and disk reads (384) <!-- sysd-blocks-106 -->
396. **Bitmap index** — Intermediate · Concept · Minor · builds on: Database index (376), Index data structures (391) <!-- sysd-blocks-091 -->
397. **Covering index** — Intermediate · Concept · Minor · builds on: Database index (376), Clustered and non-clustered indexes (386) <!-- sysd-blocks-087 -->
398. **Dense and sparse indexes** — Intermediate · Concept · Minor · builds on: Database index (376), Clustered and non-clustered indexes (386) <!-- sysd-blocks-100 -->
399. **Indexes and database constraints** — Intermediate · Concept · Minor · builds on: Database index (376), Database constraints (350), Primary and foreign keys (337) <!-- sysd-blocks-089 -->
400. **Types of database indexes** — Intermediate · Classification · Minor · builds on: Index data structures (391), Database index (376) <!-- sysd-blocks-092 -->
401. **Pessimistic and optimistic locking** — Intermediate · Concept · Minor · builds on: Database transaction (333), Isolation (336), Concurrency control (361) <!-- sysd-blocks-098 -->
402. **LSM-tree lookups and range queries** — Advanced · Process · Minor · builds on: LSM-tree writes and compaction (394), Bloom filter (213), Log-structured merge-tree (387) <!-- sysd-blocks-110 -->
403. **Database keys** — Intermediate · Classification · Minor · builds on: Relational database (326), Primary and foreign keys (337) <!-- sysd-blocks-101 -->
404. **Composite index column order** — Intermediate · Concept · Minor · builds on: Database index (376), Database keys (403), B-tree (378) <!-- sysd-blocks-086 -->
405. **Full table scans and index limits** — Intermediate · Concept · Minor · builds on: Database index (376), SQL (345), Composite index column order (404) <!-- sysd-blocks-088 -->
406. **Functional dependencies** — Intermediate · Concept · Minor · builds on: Database keys (403), Relational database (326) <!-- sysd-blocks-102 -->
407. **Normal forms** — Intermediate · Classification · Major · builds on: Database normalization (375), Functional dependencies (406), Database keys (403), Insertion, update and deletion anomalies (383) <!-- sysd-blocks-095 -->
408. **Normalizing a table to 3NF** — Intermediate · Method · Major · builds on: Normal forms (407), Functional dependencies (406), Insertion, update and deletion anomalies (383), Primary and foreign keys (337), Database normalization (375) <!-- sysd-blocks-096 -->
409. **Sixth normal form and columnar stores** — Advanced · Concept · Minor · builds on: Normal forms (407), Primary and foreign keys (337), Functional dependencies (406), Data warehouse (340) <!-- sysd-blocks-097 -->

### Storage systems

410. **Computer data storage** — Foundational · Concept · Major <!-- sysd-blocks-139 -->
411. **Hard disk drive** — Foundational · Concept · Major · builds on: Computer data storage (410) <!-- sysd-blocks-199 -->
412. **Volatile memory** — Foundational · Concept · Major · builds on: Computer data storage (410) <!-- sysd-blocks-192 -->
413. **Non-volatile memory** — Foundational · Classification · Major · builds on: Volatile memory (412), Computer data storage (410) <!-- sysd-blocks-193 -->
414. **Durability** — Intermediate · Concept · Major · builds on: ACID properties (334), Database transaction (333), Non-volatile memory (413), Volatile memory (412) <!-- sysd-blocks-210 -->
415. **Storage hierarchy** — Foundational · Classification · Major · builds on: Computer data storage (410) <!-- sysd-blocks-140 -->
416. **Flash memory** — Intermediate · Concept · Major · builds on: Non-volatile memory (413) <!-- sysd-blocks-194 -->
417. **Solid-state drive** — Foundational · Concept · Major · builds on: Flash memory (416), Non-volatile memory (413), Hard disk drive (411) <!-- sysd-blocks-195 -->
418. **Disk failure and error handling** — Intermediate · Concept · Minor · builds on: Hard disk drive (411) <!-- sysd-blocks-200 -->
419. **Drive interfaces** — Intermediate · Classification · Minor · builds on: Hard disk drive (411), Solid-state drive (417) <!-- sysd-blocks-201 -->
420. **Storage device characteristics** — Foundational · Classification · Minor · builds on: Computer data storage (410) <!-- sysd-blocks-141 -->
421. **Block storage** — Foundational · Concept · Major · builds on: Computer data storage (410) <!-- sysd-blocks-143 -->
422. **RAID** — Intermediate · Concept · Major · builds on: Hard disk drive (411), Solid-state drive (417), Disk failure and error handling (418), Block storage (421) <!-- sysd-blocks-149 -->
423. **iSCSI** — Intermediate · Concept · Major · builds on: Block storage (421), Drive interfaces (419), Transmission Control Protocol (42), Internet Protocol (45) <!-- sysd-blocks-206 -->
424. **Data scrubbing** — Intermediate · Method · Minor · builds on: RAID (422), Disk failure and error handling (418) <!-- sysd-blocks-155 -->
425. **RAID implementations** — Intermediate · Classification · Minor · builds on: RAID (422), Drive interfaces (419) <!-- sysd-blocks-156 -->
426. **File storage** — Foundational · Concept · Major · builds on: Block storage (421), Computer data storage (410) <!-- sysd-blocks-144 -->
427. **Object storage** — Intermediate · Concept · Landmark · builds on: Block storage (421), File storage (426) <!-- sysd-blocks-145 -->
428. **Cloud storage** — Intermediate · Concept · Minor · builds on: Object storage (427), Block storage (421), File storage (426) <!-- sysd-blocks-147 -->
429. **Amazon S3** — Intermediate · Concept · Major · builds on: Object storage (427), Cloud storage (428) <!-- sysd-blocks-208 -->
430. **DAS, NAS and SAN** — Intermediate · Classification · Minor · builds on: Computer data storage (410), Block storage (421), File storage (426) <!-- sysd-blocks-142 -->
431. **Fibre Channel** — Intermediate · Concept · Major · builds on: Block storage (421), DAS, NAS and SAN (430), Drive interfaces (419) <!-- sysd-blocks-207 -->
432. **Network File System** — Intermediate · Concept · Major · builds on: File storage (426), DAS, NAS and SAN (430), Client-server model (38), Transmission Control Protocol (42) <!-- sysd-blocks-202 -->
433. **Server Message Block** — Intermediate · Concept · Major · builds on: File storage (426), DAS, NAS and SAN (430), Client-server model (38), Transmission Control Protocol (42) <!-- sysd-blocks-204 -->
434. **SSD as a cache layer** — Intermediate · Practice · Minor · builds on: Solid-state drive (417), Hard disk drive (411), Caching (267) <!-- sysd-blocks-198 -->
435. **SSD endurance** — Intermediate · Concept · Minor · builds on: Solid-state drive (417), Flash memory (416) <!-- sysd-blocks-197 -->
436. **Wear leveling and TRIM** — Intermediate · Method · Minor · builds on: Solid-state drive (417), Flash memory (416) <!-- sysd-blocks-196 -->
437. **Parallel NFS** — Advanced · Method · Minor · builds on: Network File System (432), File storage (426) <!-- sysd-blocks-203 -->
438. **Opportunistic locking** — Intermediate · Concept · Minor · builds on: Server Message Block (433), Caching (267), Pessimistic and optimistic locking (401) <!-- sysd-blocks-205 -->
439. **Object stores versus key-value stores** — Intermediate · Concept · Minor · builds on: Object storage (427), Key-value store (331) <!-- sysd-blocks-152 -->
440. **Object storage use cases** — Intermediate · Classification · Minor · builds on: Object storage (427) <!-- sysd-blocks-146 -->
441. **Hadoop Distributed File System** — Intermediate · Concept · Minor · builds on: File storage (426), DAS, NAS and SAN (430) <!-- sysd-blocks-148 -->
442. **Reed-Solomon codes** — Advanced · Method · Major <!-- sysd-blocks-209 -->
443. **RAID levels** — Intermediate · Classification · Major · builds on: RAID (422) <!-- sysd-blocks-150 -->
444. **Erasure coding** — Intermediate · Method · Major · builds on: RAID levels (443), Object storage (427) <!-- sysd-blocks-151 -->
445. **Parity check** — Intermediate · Concept · Minor · builds on: Erasure coding (444) <!-- sysd-blocks-153 -->
446. **Weaknesses of RAID** — Intermediate · Concept · Minor · builds on: RAID levels (443), Parity check (445), Disk failure and error handling (418) <!-- sysd-blocks-154 -->

## Scaling and consistency


### Scalability and availability

447. **Scalability** — Foundational · Concept · Landmark <!-- sysd-scale-059 -->
448. **High availability** — Foundational · Concept · Landmark · builds on: Scalability (447) <!-- sysd-scale-068 -->
449. **Redundancy** — Intermediate · Method · Major · builds on: High availability (448) <!-- sysd-scale-073 -->
450. **Mean time between failures** — Intermediate · Concept · Major · builds on: High availability (448) <!-- sysd-scale-133 -->
451. **Horizontal and vertical scaling** — Foundational · Classification · Major · builds on: Scalability (447) <!-- sysd-scale-061 -->
452. **Stateless and stateful services** — Intermediate · Concept · Major · builds on: Client-server model (38), HTTP statelessness and sessions (136) <!-- sysd-scale-138 -->
453. **Amdahl's law** — Advanced · Concept · Major · builds on: Scalability (447), Horizontal and vertical scaling (451) <!-- sysd-scale-136 -->
454. **Autoscaling** — Intermediate · Practice · Major · builds on: Horizontal and vertical scaling (451), Load balancing (237) <!-- sysd-q-067 -->
455. **Dimensions of scalability** — Intermediate · Classification · Minor · builds on: Scalability (447) <!-- sysd-scale-060 -->
456. **Diminishing returns of adding hardware** — Advanced · Concept · Minor · builds on: Horizontal and vertical scaling (451), Amdahl's law (453) <!-- sysd-scale-065 -->
457. **Universal Scalability Law** — Advanced · Method · Minor · builds on: Scalability (447), Amdahl's law (453), Diminishing returns of adding hardware (456) <!-- sysd-scale-066 -->
458. **Scalability strategies** — Intermediate · Practice · Major · builds on: Horizontal and vertical scaling (451), Stateless and stateful services (452), Load balancing (237), Caching (267), Autoscaling (454) <!-- sysd-scale-062 -->
459. **Database scaling strategies** — Intermediate · Practice · Major · builds on: Horizontal and vertical scaling (451), Scalability strategies (458), Database (325), Database index (376), Caching (267), Views and materialized views (354) <!-- sysd-scale-064 -->
460. **Computer cluster** — Intermediate · Concept · Major · builds on: Horizontal and vertical scaling (451) <!-- sysd-scale-075 -->
461. **Scale-out storage consistency** — Advanced · Concept · Minor · builds on: Scalability (447), Horizontal and vertical scaling (451), Computer cluster (460) <!-- sysd-scale-067 -->
462. **Scheduled and unscheduled downtime** — Intermediate · Concept · Minor · builds on: High availability (448) <!-- sysd-scale-071 -->
463. **Availability and the nines** — Intermediate · Concept · Major · builds on: High availability (448), Scheduled and unscheduled downtime (462) <!-- sysd-scale-069 -->
464. **Mean time to repair** — Intermediate · Concept · Minor · builds on: Mean time between failures (450), Scheduled and unscheduled downtime (462) <!-- sysd-scale-134 -->
465. **Measuring availability** — Intermediate · Concept · Minor · builds on: Availability and the nines (463), Scheduled and unscheduled downtime (462) <!-- sysd-scale-070 -->
466. **Recovery time and recovery point objectives** — Intermediate · Concept · Minor · builds on: High availability (448), Availability and the nines (463), Scheduled and unscheduled downtime (462) <!-- sysd-scale-072 -->
467. **Active-active and active-passive clusters** — Intermediate · Classification · Major · builds on: Computer cluster (460), High availability (448), Redundancy (449), Load balancing (237) <!-- sysd-scale-076 -->
468. **Availability in sequence and in parallel** — Intermediate · Method · Major · builds on: Availability and the nines (463), Redundancy (449) <!-- sysd-scale-074 -->
469. **Forms of redundancy** — Intermediate · Classification · Minor · builds on: Redundancy (449) <!-- sysd-scale-135 -->
470. **Capacity planning** — Intermediate · Concept · Minor · builds on: Scalability (447), Back-of-the-envelope estimation (34) <!-- sysd-scale-137 -->
471. **Scalability bottlenecks** — Intermediate · Concept · Minor · builds on: Scalability (447) <!-- sysd-scale-063 -->
472. **Clustering versus load balancing** — Intermediate · Concept · Minor · builds on: Computer cluster (460), Load balancing (237) <!-- sysd-scale-077 -->

### Replication

473. **Replication** — Foundational · Concept · Landmark · builds on: Redundancy (449), High availability (448) <!-- sysd-scale-043 -->
474. **Single point of failure** — Foundational · Concept · Major · builds on: High availability (448) <!-- sysd-scale-056 -->
475. **Failover** — Intermediate · Process · Major · builds on: Replication (473), Single point of failure (474), Redundancy (449), High availability (448) <!-- sysd-scale-058 -->
476. **Gossip protocol** — Intermediate · Concept · Major · builds on: Peer-to-peer (307), Replication (473) <!-- sysd-scale-128 -->
477. **Single-leader replication** — Intermediate · Method · Major · builds on: Replication (473), Database (325) <!-- sysd-scale-044 -->
478. **Log-shipping standby servers** — Intermediate · Method · Major · builds on: Single-leader replication (477), Write-ahead log (379), Failover (475), Replication (473) <!-- sysd-scale-131 -->
479. **Leader election** — Intermediate · Concept · Major · builds on: Single-leader replication (477), Failover (475) <!-- sysd-scale-124 -->
480. **Multi-master replication** — Intermediate · Method · Major · builds on: Single-leader replication (477), Replication (473) <!-- sysd-scale-045 -->
481. **Replication conflict resolution** — Intermediate · Method · Major · builds on: Multi-master replication (480), Database transaction (333) <!-- sysd-scale-046 -->
482. **Conflict-free replicated data type** — Advanced · Concept · Major · builds on: Replication (473), Multi-master replication (480), Replication conflict resolution (481) <!-- sysd-scale-125 -->
483. **Synchronous and asynchronous replication** — Intermediate · Classification · Major · builds on: Replication (473), Latency (19) <!-- sysd-scale-047 -->
484. **Quorum** — Intermediate · Concept · Major · builds on: Replication (473), Synchronous and asynchronous replication (483) <!-- sysd-scale-122 -->
485. **Leaderless replication** — Advanced · Method · Major · builds on: Multi-master replication (480), Replication conflict resolution (481), Quorum (484), Gossip protocol (476), Replication (473) <!-- sysd-scale-129 -->
486. **Read replica pattern** — Intermediate · Practice · Major · builds on: Single-leader replication (477), Load balancing (237) <!-- sysd-scale-049 -->
487. **Performance bottleneck** — Intermediate · Concept · Minor · builds on: Latency (19), Latency vs throughput (33), Scalability (447) <!-- sysd-scale-057 -->
488. **Replication lag and read-after-write consistency** — Intermediate · Concept · Major · builds on: Single-leader replication (477), Synchronous and asynchronous replication (483) <!-- sysd-scale-048 -->
489. **Active and passive replication** — Intermediate · Classification · Minor · builds on: Replication (473), Single-leader replication (477) <!-- sysd-scale-050 -->
490. **Chain replication** — Advanced · Method · Minor · builds on: Single-leader replication (477), Synchronous and asynchronous replication (483), Multi-master replication (480) <!-- sysd-scale-052 -->
491. **Replication change propagation methods** — Advanced · Classification · Minor · builds on: Single-leader replication (477), Write-ahead log (379), SQL (345) <!-- sysd-scale-053 -->
492. **Logical replication** — Intermediate · Method · Major · builds on: Single-leader replication (477), Replication change propagation methods (491), Primary and foreign keys (337), Replication (473) <!-- sysd-scale-132 -->
493. **Replication models** — Advanced · Classification · Minor · builds on: Replication (473), Active and passive replication (489), Database transaction (333) <!-- sysd-scale-051 -->
494. **Storage replication** — Intermediate · Concept · Minor · builds on: Replication (473), Block storage (421) <!-- sysd-scale-054 -->
495. **Choosing a replication solution** — Intermediate · Practice · Minor · builds on: Storage replication (494), Log-shipping standby servers (478), Logical replication (492), Synchronous and asynchronous replication (483), Failover (475), Replication (473) <!-- sysd-scale-130 -->
496. **File-based replication** — Intermediate · Concept · Minor · builds on: Storage replication (494), File storage (426) <!-- sysd-scale-055 -->
497. **Split-brain** — Intermediate · Concept · Major · builds on: Replication (473), Single-leader replication (477), Failover (475) <!-- sysd-scale-123 -->
498. **State-based and operation-based CRDTs** — Advanced · Classification · Minor · builds on: Conflict-free replicated data type (482), Multi-master replication (480) <!-- sysd-scale-126 -->
499. **Common CRDT data types** — Advanced · Classification · Minor · builds on: Conflict-free replicated data type (482), State-based and operation-based CRDTs (498) <!-- sysd-scale-127 -->

### Sharding and partitioning

500. **Database partitioning** — Intermediate · Concept · Major · builds on: Database (325), Relational database (326) <!-- sysd-scale-080 -->
501. **Partitioning criteria** — Intermediate · Classification · Major · builds on: Database partitioning (500) <!-- sysd-scale-082 -->
502. **Range partitioning** — Intermediate · Method · Major · builds on: Partitioning criteria (501), Database partitioning (500) <!-- sysd-scale-083 -->
503. **Horizontal partitioning** — Intermediate · Method · Minor · builds on: Database partitioning (500), Relational database (326) <!-- sysd-scale-085 -->
504. **Database sharding** — Intermediate · Method · Landmark · builds on: Database partitioning (500), Horizontal partitioning (503), Partitioning criteria (501) <!-- sysd-scale-087 -->
505. **Shared-nothing architecture** — Intermediate · Concept · Major · builds on: Computer cluster (460), Database sharding (504), Single point of failure (474) <!-- sysd-scale-141 -->
506. **Hot spots and data skew** — Intermediate · Concept · Minor · builds on: Database partitioning (500), Partitioning criteria (501) <!-- sysd-scale-081 -->
507. **Challenges of sharding** — Intermediate · Concept · Major · builds on: Database sharding (504), Relational operations (351), Failover (475), Hot spots and data skew (506) <!-- sysd-scale-088 -->
508. **Hash partitioning** — Intermediate · Method · Major · builds on: Partitioning criteria (501), Hot spots and data skew (506), Hash table (377), Database partitioning (500) <!-- sysd-scale-084 -->
509. **Consistent hashing** — Intermediate · Method · Landmark · builds on: Hash table (377), Hash partitioning (508), Database sharding (504) <!-- sysd-scale-078 -->
510. **Distributed hash table** — Intermediate · Concept · Major · builds on: Hash table (377), Consistent hashing (509), Peer-to-peer (307) <!-- sysd-scale-139 -->
511. **Rendezvous hashing** — Advanced · Method · Major · builds on: Consistent hashing (509), Hash table (377) <!-- sysd-scale-079 -->
512. **Virtual nodes** — Intermediate · Method · Minor · builds on: Consistent hashing (509), Hot spots and data skew (506) <!-- sysd-scale-089 -->
513. **Chord** — Advanced · Method · Minor · builds on: Distributed hash table (510), Consistent hashing (509) <!-- sysd-scale-140 -->
514. **Vertical partitioning** — Intermediate · Method · Minor · builds on: Database partitioning (500), Relational database (326), Horizontal partitioning (503) <!-- sysd-scale-086 -->
515. **Database federation** — Intermediate · Method · Major · builds on: Database partitioning (500), Vertical partitioning (514), Database sharding (504) <!-- sysd-scale-091 -->
516. **When to use sharding** — Intermediate · Practice · Minor · builds on: Database sharding (504), Challenges of sharding (507), Horizontal and vertical scaling (451), Database scaling strategies (459) <!-- sysd-scale-090 -->

### The CAP theorem and consistency

517. **Consistency model** — Intermediate · Concept · Major · builds on: Replication (473), Synchronous and asynchronous replication (483), Replication lag and read-after-write consistency (488) <!-- sysd-scale-092 -->
518. **Eventual consistency** — Intermediate · Concept · Major · builds on: Consistency model (517), Synchronous and asynchronous replication (483), Replication lag and read-after-write consistency (488), BASE consistency model (358), Replication (473) <!-- sysd-scale-097 -->
519. **Network partition** — Intermediate · Concept · Major · builds on: Computer cluster (460), Best-effort delivery (53), Network latency (21), Replication (473) <!-- sysd-scale-142 -->
520. **CAP theorem** — Intermediate · Concept · Landmark · builds on: Consistency model (517), Network partition (519), Replication (473), High availability (448) <!-- sysd-scale-107 -->
521. **Replica conflict resolution** — Intermediate · Method · Major · builds on: Eventual consistency (518), Replication conflict resolution (481), Multi-master replication (480) <!-- sysd-scale-098 -->
522. **PACELC** — Intermediate · Concept · Major · builds on: CAP theorem (520), Consistency model (517), Latency (19), Synchronous and asynchronous replication (483) <!-- sysd-scale-101 -->
523. **Strong eventual consistency** — Advanced · Concept · Minor · builds on: Eventual consistency (518), Replica conflict resolution (521) <!-- sysd-scale-099 -->
524. **CP, AP and CA systems** — Intermediate · Classification · Major · builds on: CAP theorem (520), Network partition (519), ACID properties (334), BASE consistency model (358), Eventual consistency (518) <!-- sysd-scale-108 -->
525. **Common misreadings of CAP** — Intermediate · Concept · Major · builds on: CAP theorem (520), CP, AP and CA systems (524), PACELC (522), ACID properties (334), High availability (448) <!-- sysd-scale-103 -->
526. **Primary-backup replication** — Intermediate · Method · Minor · builds on: Replication (473), Single-leader replication (477), Synchronous and asynchronous replication (483) <!-- sysd-scale-104 -->
527. **Active replication** — Advanced · Method · Minor · builds on: Replication (473), Active and passive replication (489), Primary-backup replication (526) <!-- sysd-scale-106 -->
528. **Quorum-based replication** — Intermediate · Method · Minor · builds on: Replication (473), Quorum (484), Primary-backup replication (526) <!-- sysd-scale-105 -->
529. **Sequential consistency** — Advanced · Concept · Minor · builds on: Consistency model (517), Replication lag and read-after-write consistency (488) <!-- sysd-scale-093 -->
530. **Linearizability** — Advanced · Concept · Major · builds on: Sequential consistency (529), Consistency model (517), Isolation (336) <!-- sysd-scale-094 -->
531. **Causal consistency** — Advanced · Concept · Minor · builds on: Sequential consistency (529), Consistency model (517) <!-- sysd-scale-095 -->
532. **Session guarantees** — Intermediate · Classification · Minor · builds on: Consistency model (517), Eventual consistency (518), Replication lag and read-after-write consistency (488) <!-- sysd-scale-096 -->
533. **PACELC database classifications** — Intermediate · Classification · Minor · builds on: PACELC (522), CP, AP and CA systems (524), ACID properties (334), NoSQL (327) <!-- sysd-scale-102 -->
534. **Eventual consistency patterns** — Intermediate · Classification · Minor · builds on: Eventual consistency (518), Replica conflict resolution (521) <!-- sysd-scale-100 -->

### Consensus, ordering and distributed transactions

535. **Distributed transaction** — Intermediate · Concept · Major · builds on: Database transaction (333), ACID properties (334), Isolation (336) <!-- sysd-scale-001 -->
536. **Two-phase commit** — Intermediate · Process · Major · builds on: Distributed transaction (535), Write-ahead log (379), ACID properties (334) <!-- sysd-scale-002 -->
537. **Lamport timestamp** — Intermediate · Method · Major · builds on: Network latency (21) <!-- sysd-scale-014 -->
538. **Heartbeat failure detection** — Intermediate · Method · Major · builds on: Computer cluster (460), Failover (475), Network latency (21) <!-- sysd-scale-006 -->
539. **Happened-before relation** — Advanced · Concept · Minor · builds on: Lamport timestamp (537) <!-- sysd-scale-112 -->
540. **Vector clock** — Advanced · Method · Major · builds on: Lamport timestamp (537), Happened-before relation (539) <!-- sysd-scale-024 -->
541. **Two-phase commit variants** — Advanced · Method · Minor · builds on: Two-phase commit (536), Write-ahead log (379) <!-- sysd-scale-003 -->
542. **Consensus** — Advanced · Concept · Landmark · builds on: Distributed transaction (535), Replication (473), Quorum (484), Network partition (519) <!-- sysd-scale-008 -->
543. **Distributed lock** — Intermediate · Concept · Major · builds on: Pessimistic and optimistic locking (401), Computer cluster (460), Time to live (292), Consensus (542) <!-- sysd-scale-007 -->
544. **State machine replication** — Advanced · Concept · Major · builds on: Consensus (542), Replication (473), Active and passive replication (489) <!-- sysd-scale-020 -->
545. **Single-value and multi-valued consensus** — Advanced · Classification · Minor · builds on: Consensus (542), State machine replication (544) <!-- sysd-scale-012 -->
546. **Synchronous and asynchronous systems** — Advanced · Classification · Minor · builds on: Consensus (542), Network latency (21) <!-- sysd-scale-011 -->
547. **Three-phase commit** — Advanced · Process · Major · builds on: Two-phase commit (536), Synchronous and asynchronous systems (546), Quorum (484) <!-- sysd-scale-004 -->
548. **Two Generals' Problem** — Intermediate · Concept · Major · builds on: Transmission Control Protocol (42), TCP reliable delivery (54), Network partition (519), Consensus (542) <!-- sysd-scale-114 -->
549. **Crash and Byzantine failures** — Advanced · Classification · Major · builds on: Consensus (542), Heartbeat failure detection (538), Two Generals' Problem (548) <!-- sysd-scale-009 -->
550. **Atomic broadcast** — Advanced · Concept · Major · builds on: Consensus (542), Crash and Byzantine failures (549), Lamport timestamp (537) <!-- sysd-scale-113 -->
551. **Apache ZooKeeper** — Intermediate · Concept · Major · builds on: Consensus (542), Distributed lock (543), Leader election (479), Atomic broadcast (550), Key-value store (331) <!-- sysd-scale-111 -->
552. **FLP impossibility result** — Advanced · Concept · Major · builds on: Consensus (542), Synchronous and asynchronous systems (546), Crash and Byzantine failures (549) <!-- sysd-scale-010 -->
553. **Paxos** — Advanced · Method · Major · builds on: Consensus (542), Quorum (484), Crash and Byzantine failures (549), FLP impossibility result (552) <!-- sysd-scale-015 -->
554. **Byzantine fault tolerance** — Advanced · Concept · Major · builds on: Consensus (542), Crash and Byzantine failures (549), Quorum (484) <!-- sysd-scale-109 -->
555. **Raft** — Advanced · Method · Major · builds on: Consensus (542), Paxos (553), State machine replication (544), Quorum (484), Leader election (479) <!-- sysd-scale-021 -->
556. **Consensus-based system patterns** — Advanced · Classification · Major · builds on: Consensus (542), State machine replication (544), Distributed lock (543), Leader election (479), Atomic broadcast (550) <!-- sysd-scale-115 -->
557. **Sizing a consensus group** — Advanced · Practice · Major · builds on: Consensus (542), Quorum (484), Crash and Byzantine failures (549), Database sharding (504), Quorum-based replication (528) <!-- sysd-scale-117 -->
558. **Placing consensus replicas** — Advanced · Practice · Major · builds on: Consensus (542), Sizing a consensus group (557), Network latency (21), Leader election (479) <!-- sysd-scale-118 -->
559. **Basic Paxos** — Advanced · Process · Major · builds on: Paxos (553), Quorum (484), Single-value and multi-valued consensus (545) <!-- sysd-scale-016 -->
560. **Multi-Paxos** — Advanced · Method · Major · builds on: Basic Paxos (559), State machine replication (544), Single-value and multi-valued consensus (545), Leader election (479) <!-- sysd-scale-017 -->
561. **Permissioned and permissionless consensus** — Advanced · Classification · Minor · builds on: Consensus (542), Crash and Byzantine failures (549), Byzantine fault tolerance (554) <!-- sysd-scale-013 -->
562. **Monitoring consensus systems** — Advanced · Practice · Minor · builds on: Consensus (542), Leader election (479), Heartbeat failure detection (538), Sizing a consensus group (557) <!-- sysd-scale-119 -->
563. **Cheap Paxos** — Advanced · Method · Minor · builds on: Basic Paxos (559), Quorum (484), Crash and Byzantine failures (549) <!-- sysd-scale-019 -->
564. **Fast Paxos** — Advanced · Method · Minor · builds on: Basic Paxos (559), Quorum (484), Network latency (21) <!-- sysd-scale-018 -->
565. **Consensus performance** — Advanced · Concept · Major · builds on: Consensus (542), Multi-Paxos (560), Fast Paxos (564), Latency vs throughput (33), Network latency (21) <!-- sysd-scale-116 -->
566. **Raft leader election** — Advanced · Process · Minor · builds on: Raft (555), Heartbeat failure detection (538), Leader election (479), Quorum (484) <!-- sysd-scale-022 -->
567. **Raft log replication** — Advanced · Process · Minor · builds on: Raft (555), Raft leader election (566), State machine replication (544) <!-- sysd-scale-023 -->
568. **Saga pattern** — Intermediate · Method · Major · builds on: Distributed transaction (535), Two-phase commit (536) <!-- sysd-scale-005 -->
569. **Compensating transaction** — Intermediate · Concept · Minor · builds on: Database transaction (333), Distributed transaction (535), ACID properties (334), Saga pattern (568) <!-- sysd-scale-110 -->

### How the big distributed data systems work

570. **Spanner** — Advanced · Concept · Major · builds on: Distributed transaction (535), Paxos (553), Linearizability (530), Synchronous and asynchronous replication (483), Database sharding (504), Consensus (542), Consistency model (517) <!-- sysd-scale-026 -->
571. **Amazon Dynamo** — Intermediate · Concept · Major · builds on: Key-value store (331), NoSQL (327), High availability (448), Replication (473), Eventual consistency (518) <!-- sysd-scale-042 -->
572. **Amazon DynamoDB** — Intermediate · Concept · Major · builds on: Amazon Dynamo (571), Key-value store (331), Document database (329), Database sharding (504), Eventual consistency (518), NoSQL (327) <!-- sysd-scale-027 -->
573. **DynamoDB partition and sort keys** — Intermediate · Concept · Minor · builds on: Amazon DynamoDB (572), Hash partitioning (508), Range partitioning (502), Primary and foreign keys (337), Database index (376), Database sharding (504) <!-- sysd-scale-028 -->
574. **DynamoDB data modeling patterns** — Intermediate · Classification · Minor · builds on: DynamoDB partition and sort keys (573), Handling relational data in NoSQL (352), Denormalization (388), Views and materialized views (354), Time series database (360), Amazon DynamoDB (572) <!-- sysd-scale-029 -->
575. **Google File System** — Intermediate · Case study · Major · builds on: File storage (426), Replication (473), Heartbeat failure detection (538), Primary-backup replication (526), Database sharding (504) <!-- sysd-scale-025 -->
576. **Bigtable** — Intermediate · Concept · Major · builds on: Wide-column store (338), Google File System (575), Database sharding (504), Log-structured merge-tree (387), Distributed lock (543), NoSQL (327) <!-- sysd-scale-038 -->
577. **Apache Cassandra** — Intermediate · Concept · Major · builds on: Wide-column store (338), Amazon Dynamo (571), Bigtable (576), Leaderless replication (485), CP, AP and CA systems (524), NoSQL (327), Replication (473), Eventual consistency (518) <!-- sysd-scale-031 -->
578. **MapReduce** — Intermediate · Concept · Major · builds on: Computer cluster (460), Google File System (575), Hash partitioning (508), Heartbeat failure detection (538), Replication (473), Database sharding (504) <!-- sysd-scale-040 -->
579. **Apache Hadoop** — Intermediate · Concept · Major · builds on: MapReduce (578), Hadoop Distributed File System (441), Google File System (575), Replication (473) <!-- sysd-scale-035 -->
580. **HDFS architecture** — Intermediate · Concept · Major · builds on: Hadoop Distributed File System (441), Apache Hadoop (579), Replication (473), Heartbeat failure detection (538), Single point of failure (474) <!-- sysd-scale-036 -->
581. **Apache HBase** — Intermediate · Concept · Minor · builds on: Bigtable (576), HDFS architecture (580), Wide-column store (338), CP, AP and CA systems (524), PACELC database classifications (533), Apache Hadoop (579) <!-- sysd-scale-120 -->
582. **Cassandra data model** — Intermediate · Concept · Minor · builds on: Apache Cassandra (577), Wide-column store (338), Hash partitioning (508), Denormalization (388), Replica conflict resolution (521) <!-- sysd-scale-032 -->
583. **Cassandra gossip and failure handling** — Advanced · Process · Minor · builds on: Apache Cassandra (577), Gossip protocol (476), Heartbeat failure detection (538), Leaderless replication (485) <!-- sysd-scale-034 -->
584. **Cassandra write and read path** — Intermediate · Process · Minor · builds on: Apache Cassandra (577), Log-structured merge-tree (387), LSM-tree writes and compaction (394), Write-ahead log (379), LSM-tree lookups and range queries (402) <!-- sysd-scale-033 -->
585. **ScyllaDB** — Intermediate · Concept · Minor · builds on: Apache Cassandra (577), Cassandra write and read path (584), Amazon DynamoDB (572), Shared-nothing architecture (505), CP, AP and CA systems (524), Database sharding (504) <!-- sysd-scale-121 -->
586. **Bigtable data model** — Intermediate · Concept · Minor · builds on: Bigtable (576), Wide-column store (338), Key-value store (331) <!-- sysd-scale-039 -->
587. **Hadoop job scheduling and YARN** — Advanced · Method · Minor · builds on: Apache Hadoop (579), MapReduce (578), HDFS architecture (580), Computer cluster (460) <!-- sysd-scale-037 -->
588. **MapReduce dataflow and shuffle** — Intermediate · Process · Minor · builds on: MapReduce (578), Hash partitioning (508), Hot spots and data skew (506) <!-- sysd-scale-041 -->
589. **Discord message storage** — Intermediate · Case study · Minor · builds on: Apache Cassandra (577), Cassandra write and read path (584), ScyllaDB (585), Hot spots and data skew (506), Tail latency (23), Log-structured merge-tree (387), NoSQL (327) <!-- sysd-scale-030 -->

## Messaging, APIs and architecture


### Message queues and brokers

590. **Synchronous and asynchronous communication** — Foundational · Concept · Major · builds on: Client-server model (38), HTTP request and response messages (133) <!-- sysd-msg-047 -->
591. **Types of queues** — Foundational · Classification · Minor <!-- sysd-msg-056 -->
592. **Message queue** — Intermediate · Concept · Landmark · builds on: Synchronous and asynchronous communication (590), Types of queues (591) <!-- sysd-msg-046 -->
593. **Message-oriented middleware** — Intermediate · Concept · Major · builds on: Message queue (592), Synchronous and asynchronous communication (590) <!-- sysd-msg-138 -->
594. **Message delivery semantics** — Intermediate · Classification · Major · builds on: Message queue (592), Synchronous and asynchronous communication (590) <!-- sysd-msg-050 -->
595. **Benefits of message queues** — Intermediate · Concept · Major · builds on: Message queue (592), Synchronous and asynchronous communication (590), Scalability (447) <!-- sysd-msg-067 -->
596. **Message queue protocols** — Intermediate · Classification · Minor · builds on: Message queue (592), Message-oriented middleware (593), Application-layer protocols (44) <!-- sysd-msg-049 -->
597. **Message broker** — Intermediate · Concept · Major · builds on: Message queue (592), Message queue protocols (596), Message-oriented middleware (593) <!-- sysd-msg-051 -->
598. **Advanced Message Queuing Protocol** — Advanced · Concept · Major · builds on: Message queue protocols (596), Message-oriented middleware (593), Application-layer protocols (44), Message queue (592), Message broker (597) <!-- sysd-msg-136 -->
599. **RabbitMQ** — Intermediate · Concept · Major · builds on: Message broker (597), Advanced Message Queuing Protocol (598), Message queue protocols (596), Message queue (592) <!-- sysd-msg-072 -->
600. **Apache ActiveMQ** — Intermediate · Concept · Minor · builds on: Message broker (597), Message-oriented middleware (593), Message queue protocols (596) <!-- sysd-msg-139 -->
601. **Message queue semantics options** — Intermediate · Classification · Minor · builds on: Message queue (592), Message delivery semantics (594), Time to live (292) <!-- sysd-msg-048 -->
602. **Operating-system message queues** — Intermediate · Concept · Minor · builds on: Message queue (592), Types of queues (591) <!-- sysd-msg-058 -->
603. **Amazon Simple Queue Service** — Intermediate · Concept · Minor · builds on: Message queue (592), Message broker (597) <!-- sysd-msg-135 -->
604. **Dead letter queue** — Intermediate · Concept · Major · builds on: Message queue (592), Message delivery semantics (594) <!-- sysd-msg-134 -->
605. **Message queue features** — Intermediate · Classification · Major · builds on: Message queue (592), Message delivery semantics (594), Dead letter queue (604), Types of queues (591) <!-- sysd-msg-069 -->
606. **Choosing a message queue** — Intermediate · Practice · Major · builds on: Message queue (592), Message broker (597), Message queue protocols (596), Message delivery semantics (594), Message queue features (605) <!-- sysd-msg-059 -->
607. **Enterprise service bus** — Intermediate · Concept · Minor · builds on: Message broker (597), Message-oriented middleware (593) <!-- sysd-msg-053 -->
608. **Blocking and non-blocking queues** — Advanced · Concept · Minor · builds on: Types of queues (591), Synchronous and asynchronous communication (590) <!-- sysd-msg-057 -->
609. **How a message queue processes jobs** — Intermediate · Process · Minor · builds on: Message queue (592), Types of queues (591) <!-- sysd-msg-068 -->
610. **Backpressure** — Intermediate · Concept · Minor · builds on: Message queue (592), How a message queue processes jobs (609), Latency (19) <!-- sysd-msg-071 -->
611. **Push and pull delivery** — Intermediate · Concept · Minor · builds on: Message queue (592), Synchronous and asynchronous communication (590) <!-- sysd-msg-070 -->
612. **Competing consumers** — Intermediate · Method · Minor · builds on: Message queue (592), How a message queue processes jobs (609) <!-- sysd-msg-055 -->
613. **Cloud messaging patterns** — Intermediate · Classification · Major · builds on: Message queue (592), Competing consumers (612), Saga pattern (568), Synchronous and asynchronous communication (590) <!-- sysd-msg-054 -->
614. **Publish–subscribe pattern** — Intermediate · Concept · Landmark · builds on: Synchronous and asynchronous communication (590), Message queue (592), Message broker (597) <!-- sysd-msg-060 -->
615. **MQTT** — Intermediate · Concept · Major · builds on: Publish–subscribe pattern (614), Message queue protocols (596), Application-layer protocols (44), Message broker (597) <!-- sysd-msg-137 -->
616. **Advantages of publish–subscribe** — Intermediate · Concept · Major · builds on: Publish–subscribe pattern (614), Synchronous and asynchronous communication (590), Push and pull delivery (611) <!-- sysd-msg-064 -->
617. **Observer pattern** — Intermediate · Concept · Minor · builds on: Software design pattern (12), Publish–subscribe pattern (614) <!-- sysd-msg-141 -->
618. **NATS** — Intermediate · Concept · Minor · builds on: Publish–subscribe pattern (614), Message broker (597), Message-oriented middleware (593) <!-- sysd-msg-140 -->
619. **Drawbacks of publish–subscribe** — Advanced · Concept · Minor · builds on: Publish–subscribe pattern (614), Advantages of publish–subscribe (616), Message delivery semantics (594) <!-- sysd-msg-065 -->
620. **Publish–subscribe message filtering** — Intermediate · Classification · Minor · builds on: Publish–subscribe pattern (614), Message broker (597) <!-- sysd-msg-062 -->
621. **Publish–subscribe topologies** — Advanced · Classification · Minor · builds on: Publish–subscribe pattern (614), Message broker (597) <!-- sysd-msg-063 -->
622. **Message broker versus event streaming platform** — Intermediate · Concept · Minor · builds on: Message broker (597), Publish–subscribe pattern (614), Message queue (592) <!-- sysd-msg-052 -->
623. **Publish–subscribe features** — Intermediate · Classification · Minor · builds on: Publish–subscribe pattern (614), Message queue semantics options (601) <!-- sysd-msg-066 -->
624. **Message queue versus publish–subscribe** — Intermediate · Concept · Minor · builds on: Message queue (592), Publish–subscribe pattern (614) <!-- sysd-msg-061 -->

### Event streaming and Kafka

625. **Apache Kafka** — Intermediate · Concept · Landmark · builds on: Message queue (592), Publish–subscribe pattern (614), Message broker versus event streaming platform (622) <!-- sysd-msg-036 -->
626. **Batch processing** — Foundational · Concept · Major <!-- sysd-msg-133 -->
627. **Stream processing** — Intermediate · Concept · Major · builds on: Batch processing (626), Message queue (592), Message broker versus event streaming platform (622) <!-- sysd-msg-043 -->
628. **Apache Spark** — Intermediate · Concept · Major · builds on: Batch processing (626), MapReduce (578), Stream processing (627) <!-- sysd-msg-132 -->
629. **Kafka architecture** — Intermediate · Concept · Major · builds on: Apache Kafka (625), Message broker (597), Competing consumers (612), Database partitioning (500) <!-- sysd-msg-037 -->
630. **Preventing message loss in Kafka** — Advanced · Practice · Major · builds on: Kafka architecture (629), Message delivery semantics (594), Replication (473), Synchronous and asynchronous replication (483), Apache Kafka (625) <!-- sysd-msg-038 -->
631. **Kafka Streams** — Intermediate · Concept · Minor · builds on: Apache Kafka (625), Kafka architecture (629), Stream processing (627) <!-- sysd-msg-040 -->
632. **Complex event processing** — Advanced · Concept · Minor · builds on: Stream processing (627) <!-- sysd-msg-045 -->
633. **Change data capture** — Intermediate · Concept · Major · builds on: Database (325), Replication (473), Message queue (592) <!-- sysd-msg-041 -->
634. **Change data capture methods** — Intermediate · Classification · Major · builds on: Change data capture (633), Write-ahead log (379), Message queue (592) <!-- sysd-msg-042 -->
635. **Stream processing engines** — Advanced · Classification · Minor · builds on: Stream processing (627), Batch processing (626), Apache Kafka (625) <!-- sysd-msg-044 -->
636. **Apache Flink** — Advanced · Concept · Major · builds on: Stream processing (627), Batch processing (626), Stream processing engines (635), Apache Kafka (625) <!-- sysd-msg-131 -->
637. **Why Kafka is fast** — Advanced · Concept · Minor · builds on: Kafka architecture (629), Hard disk drive (411), Page cache (276), Apache Kafka (625) <!-- sysd-msg-039 -->

### Event-driven architecture, event sourcing and CQRS

638. **Event-driven architecture** — Intermediate · Concept · Landmark · builds on: Synchronous and asynchronous communication (590), Message broker (597), Publish–subscribe pattern (614), Message queue (592) <!-- sysd-msg-020 -->
639. **Domain-driven design** — Intermediate · Concept · Major · builds on: Software architecture (6) <!-- sysd-msg-127 -->
640. **Event store** — Intermediate · Concept · Major · builds on: Database (325), Event-driven architecture (638) <!-- sysd-msg-022 -->
641. **Event sourcing** — Intermediate · Method · Landmark · builds on: Event-driven architecture (638), Event store (640) <!-- sysd-msg-021 -->
642. **Fallacies of distributed computing** — Intermediate · Concept · Major · builds on: Latency (19), Bandwidth (20), Client-server model (38) <!-- sysd-msg-128 -->
643. **Broker and mediator topologies** — Intermediate · Classification · Major · builds on: Event-driven architecture (638), Message broker (597), Publish–subscribe pattern (614), Message queue (592) <!-- sysd-msg-026 -->
644. **Error handling and data loss in event-driven systems** — Intermediate · Practice · Major · builds on: Event-driven architecture (638), Dead letter queue (604), Message delivery semantics (594), Message queue (592) <!-- sysd-msg-030 -->
645. **Event processing styles** — Intermediate · Classification · Major · builds on: Event-driven architecture (638), Stream processing (627), Complex event processing (632) <!-- sysd-msg-029 -->
646. **Event structure and payload design** — Intermediate · Practice · Major · builds on: Event-driven architecture (638), Message queue (592) <!-- sysd-msg-028 -->
647. **Command–query separation** — Intermediate · Concept · Minor <!-- sysd-msg-129 -->
648. **Command Query Responsibility Segregation** — Intermediate · Method · Major · builds on: Command–query separation (647), Event-driven architecture (638), Eventual consistency (518), Denormalization (388) <!-- sysd-msg-024 -->
649. **Domain events and integration events** — Advanced · Classification · Minor · builds on: Event-driven architecture (638), Domain-driven design (639) <!-- sysd-msg-027 -->
650. **Event flow layers** — Intermediate · Process · Minor · builds on: Event-driven architecture (638), Message broker (597), Stream processing (627), Message queue (592) <!-- sysd-msg-033 -->
651. **Event granularity** — Intermediate · Practice · Minor · builds on: Event-driven architecture (638), Event structure and payload design (646) <!-- sysd-msg-031 -->
652. **Synchronous request-response over events** — Advanced · Method · Minor · builds on: Event-driven architecture (638), Synchronous and asynchronous communication (590), Cloud messaging patterns (613), Message queue (592) <!-- sysd-msg-034 -->
653. **Timeout antipattern** — Intermediate · Concept · Minor · builds on: Fallacies of distributed computing (642), Network latency (21), Two Generals' Problem (548), Synchronous and asynchronous communication (590) <!-- sysd-msg-035 -->
654. **Event correction with a double timeline** — Advanced · Method · Minor · builds on: Event sourcing (641), Event store (640) <!-- sysd-msg-023 -->
655. **Apache Avro** — Intermediate · Concept · Minor <!-- sysd-msg-130 -->
656. **Event schema evolution** — Advanced · Practice · Minor · builds on: Event structure and payload design (646), Apache Avro (655), Event-driven architecture (638) <!-- sysd-msg-032 -->
657. **McDonald's event-driven platform** — Intermediate · Case study · Minor · builds on: Event-driven architecture (638), Event structure and payload design (646), Event schema evolution (656), Error handling and data loss in event-driven systems (644), Apache Kafka (625), Database sharding (504) <!-- sysd-msg-025 -->

### Monoliths, microservices and service discovery

658. **Loose coupling** — Intermediate · Concept · Major · builds on: Software architecture (6) <!-- sysd-msg-143 -->
659. **Monolithic application** — Foundational · Concept · Major · builds on: Software architecture (6) <!-- sysd-msg-091 -->
660. **Microservices** — Intermediate · Concept · Landmark · builds on: Monolithic application (659), Loose coupling (658), Scalability (447), Network latency (21), Load balancing (237), Message queue (592) <!-- sysd-msg-083 -->
661. **Service-oriented architecture** — Intermediate · Concept · Major · builds on: Monolithic application (659) <!-- sysd-msg-094 -->
662. **Service discovery** — Intermediate · Concept · Major · builds on: Microservices (660), IP address (46), Domain Name System (90) <!-- sysd-msg-092 -->
663. **Service mesh** — Advanced · Concept · Major · builds on: Microservices (660), Service discovery (662), Reverse proxy (256) <!-- sysd-msg-093 -->
664. **Distributed tracing** — Intermediate · Concept · Major · builds on: Microservices (660) <!-- sysd-msg-145 -->
665. **N-tier architecture** — Foundational · Classification · Major · builds on: Software architecture (6), Client-server model (38) <!-- sysd-msg-080 -->
666. **Orchestration versus choreography** — Intermediate · Classification · Major · builds on: Microservices (660), Synchronous and asynchronous communication (590), Saga pattern (568) <!-- sysd-msg-078 -->
667. **Microservices versus SOA** — Intermediate · Concept · Minor · builds on: Service-oriented architecture (661), Microservices (660) <!-- sysd-msg-097 -->
668. **Service provider, broker and consumer** — Intermediate · Concept · Minor · builds on: Service-oriented architecture (661), Service discovery (662) <!-- sysd-msg-096 -->
669. **Service-oriented design principles** — Advanced · Practice · Minor · builds on: Service-oriented architecture (661), Loose coupling (658) <!-- sysd-msg-095 -->
670. **Service registry and registration** — Intermediate · Concept · Major · builds on: Service discovery (662), High availability (448) <!-- sysd-msg-082 -->
671. **Components of a microservice architecture** — Intermediate · Concept · Major · builds on: Microservices (660), Load balancing (237), API gateway (258), Service registry and registration (670), Content delivery network (306), Service discovery (662) <!-- sysd-msg-079 -->
672. **Client-side and server-side discovery** — Intermediate · Classification · Major · builds on: Service discovery (662), Service registry and registration (670), Load balancing (237) <!-- sysd-msg-081 -->
673. **Microservices best practices** — Intermediate · Practice · Major · builds on: Microservices (660), Domain-driven design (639), Loose coupling (658) <!-- sysd-msg-074 -->
674. **Monolith versus microservices** — Intermediate · Debate · Major · builds on: Monolithic application (659), Microservices (660), Network latency (21) <!-- sysd-msg-073 -->
675. **Bounded context** — Advanced · Concept · Minor · builds on: Domain-driven design (639) <!-- sysd-msg-085 -->
676. **Cell-based architecture** — Advanced · Concept · Minor · builds on: Microservices (660), Single point of failure (474) <!-- sysd-msg-086 -->
677. **Code sharing between microservices** — Advanced · Practice · Minor · builds on: Microservices (660), Loose coupling (658) <!-- sysd-msg-089 -->
678. **Microservice granularity** — Advanced · Concept · Minor · builds on: Microservices (660), Network latency (21) <!-- sysd-msg-084 -->
679. **Reach-in reporting antipattern** — Advanced · Concept · Minor · builds on: Microservices (660), Bounded context (675), Database (325) <!-- sysd-msg-088 -->
680. **Testing and observing microservices** — Advanced · Practice · Minor · builds on: Microservices (660), Distributed tracing (664) <!-- sysd-msg-090 -->
681. **Consul** — Intermediate · Concept · Minor · builds on: Service discovery (662), Service registry and registration (670), Key-value store (331) <!-- sysd-msg-144 -->
682. **Distributed monolith** — Intermediate · Concept · Minor · builds on: Microservices (660), Monolithic application (659), Loose coupling (658) <!-- sysd-msg-076 -->
683. **Microservices pitfalls** — Intermediate · Practice · Minor · builds on: Microservices (660), Distributed monolith (682) <!-- sysd-msg-075 -->
684. **Modular monolith** — Intermediate · Concept · Minor · builds on: Monolithic application (659), Loose coupling (658) <!-- sysd-msg-077 -->
685. **Strangler fig pattern** — Intermediate · Method · Minor · builds on: Monolithic application (659), Microservices (660) <!-- sysd-msg-142 -->
686. **Incremental migration to microservices** — Advanced · Method · Minor · builds on: Monolithic application (659), Microservices (660), Strangler fig pattern (685) <!-- sysd-msg-087 -->

### APIs: REST, GraphQL and gRPC

687. **API** — Foundational · Concept · Major <!-- sysd-msg-001 -->
688. **REST** — Intermediate · Concept · Landmark · builds on: API (687), HTTP (131), Client-server model (38), HTTP resources and representations (166) <!-- sysd-msg-002 -->
689. **Remote procedure call** — Intermediate · Concept · Major · builds on: API (687), Client-server model (38) <!-- sysd-msg-018 -->
690. **GraphQL** — Intermediate · Concept · Major · builds on: API (687), REST (688) <!-- sysd-msg-004 -->
691. **Serialization** — Intermediate · Concept · Major <!-- sysd-msg-125 -->
692. **REST architectural constraints** — Intermediate · Classification · Major · builds on: REST (688), Client-server model (38), HTTP statelessness and sessions (136), HTTP caching (153) <!-- sysd-msg-003 -->
693. **REST uniform interface** — Intermediate · Concept · Major · builds on: REST architectural constraints (692), HTTP resources and representations (166), HTTP request methods (135) <!-- sysd-msg-017 -->
694. **HATEOAS** — Intermediate · Concept · Major · builds on: REST uniform interface (693), REST (688) <!-- sysd-msg-123 -->
695. **Serialization formats** — Intermediate · Classification · Major · builds on: Serialization (691) <!-- sysd-msg-126 -->
696. **Protocol buffers** — Intermediate · Concept · Major · builds on: Serialization (691), Serialization formats (695) <!-- sysd-msg-006 -->
697. **gRPC** — Intermediate · Concept · Major · builds on: Remote procedure call (689), Protocol buffers (696) <!-- sysd-msg-005 -->
698. **SOAP** — Intermediate · Concept · Major · builds on: HTTP (131), Remote procedure call (689), Serialization formats (695) <!-- sysd-msg-122 -->
699. **API documentation** — Foundational · Concept · Minor · builds on: API (687) <!-- sysd-msg-014 -->
700. **API release policies** — Intermediate · Classification · Minor · builds on: API (687) <!-- sysd-msg-012 -->
701. **Web API** — Foundational · Concept · Minor · builds on: API (687), HTTP request and response messages (133) <!-- sysd-msg-011 -->
702. **API versioning and deprecation** — Intermediate · Practice · Minor · builds on: API release policies (700), Web API (701), API (687) <!-- sysd-msg-013 -->
703. **API pagination** — Intermediate · Method · Major · builds on: Web API (701), REST (688) <!-- sysd-msg-009 -->
704. **API design best practices** — Intermediate · Practice · Major · builds on: REST (688), HTTP resources and representations (166), HTTP request and response messages (133), API gateway (258) <!-- sysd-msg-008 -->
705. **RPC call sequence** — Intermediate · Process · Minor · builds on: Remote procedure call (689), Serialization (691) <!-- sysd-msg-019 -->
706. **Choosing between REST, GraphQL and gRPC** — Intermediate · Debate · Major · builds on: REST (688), GraphQL (690), gRPC (697), HTTP caching (153) <!-- sysd-msg-007 -->
707. **GraphQL schema and type system** — Intermediate · Concept · Minor · builds on: GraphQL (690) <!-- sysd-msg-015 -->
708. **GraphQL operations** — Intermediate · Concept · Minor · builds on: GraphQL schema and type system (707), GraphQL (690) <!-- sysd-msg-016 -->
709. **OpenAPI Specification** — Intermediate · Concept · Minor · builds on: Web API (701), API documentation (699), API (687) <!-- sysd-msg-124 -->
710. **API performance optimization** — Intermediate · Practice · Minor · builds on: API pagination (703), Reducing latency (26), Caching (267) <!-- sysd-msg-010 -->

### Real-time communication

711. **Polling** — Foundational · Method · Major · builds on: Client-server model (38), Synchronous and asynchronous communication (590), HTTP (131) <!-- sysd-msg-101 -->
712. **Push technology** — Foundational · Concept · Landmark · builds on: Client-server model (38), Polling (711), HTTP (131), Publish–subscribe pattern (614) <!-- sysd-msg-098 -->
713. **Long polling** — Intermediate · Method · Major · builds on: Polling (711), HTTP (131) <!-- sysd-msg-100 -->
714. **Push notification** — Intermediate · Concept · Major · builds on: Push technology (712) <!-- sysd-msg-105 -->
715. **Web push** — Intermediate · Concept · Major · builds on: Push notification (714), HTTP/2 (158) <!-- sysd-msg-107 -->
716. **Techniques for real-time updates** — Intermediate · Classification · Major · builds on: HTTP (131), Push technology (712), Polling (711) <!-- sysd-msg-099 -->
717. **WebSocket** — Intermediate · Concept · Landmark · builds on: Transmission Control Protocol (42), HTTP (131), Techniques for real-time updates (716), TCP connection setup and teardown (43) <!-- sysd-msg-108 -->
718. **WebSocket opening handshake** — Intermediate · Process · Major · builds on: WebSocket (717), HTTP request and response messages (133), HTTP informational status codes (165), HTTP (131), HTTP/2 (158) <!-- sysd-msg-109 -->
719. **WebSocket frames and messages** — Intermediate · Concept · Major · builds on: WebSocket (717), WebSocket opening handshake (718) <!-- sysd-msg-110 -->
720. **WebSocket proxies and load balancers** — Intermediate · Concept · Major · builds on: WebSocket opening handshake (718), Reverse proxy (256), Load balancing (237) <!-- sysd-msg-115 -->
721. **WebSocket closing handshake** — Intermediate · Process · Major · builds on: WebSocket frames and messages (719), TCP connection setup and teardown (43) <!-- sysd-msg-113 -->
722. **Notification system architecture** — Intermediate · Process · Major · builds on: Push notification (714), Message queue (592) <!-- sysd-msg-106 -->
723. **Webhooks** — Intermediate · Method · Major · builds on: HTTP (131), Polling (711), Push technology (712) <!-- sysd-msg-102 -->
724. **WebSocket API** — Intermediate · Concept · Minor · builds on: WebSocket (717), WebSocket frames and messages (719) <!-- sysd-msg-116 -->
725. **HTTP streaming** — Intermediate · Method · Minor · builds on: Push technology (712), HTTP (131), HTTP persistent connections (134) <!-- sysd-msg-104 -->
726. **Server-sent events** — Intermediate · Concept · Major · builds on: Push technology (712), HTTP (131), HTTP streaming (725) <!-- sysd-msg-103 -->
727. **Presence information** — Intermediate · Concept · Minor <!-- sysd-msg-149 -->
728. **XMPP** — Intermediate · Concept · Major · builds on: Presence information (727), Serialization formats (695), Application-layer protocols (44) <!-- sysd-msg-148 -->
729. **Push message delivery controls** — Intermediate · Method · Minor · builds on: Web push (715), HTTP request and response messages (133) <!-- sysd-msg-150 -->
730. **Reconnect with backoff** — Intermediate · Practice · Minor · builds on: WebSocket closing handshake (721), WebSocket (717) <!-- sysd-msg-119 -->
731. **WebSocket URIs** — Foundational · Concept · Minor · builds on: WebSocket (717), HTTPS (182) <!-- sysd-msg-121 -->
732. **WebSocket security** — Intermediate · Concept · Major · builds on: WebSocket opening handshake (718), WebSocket URIs (731), HTTP origins and certificate verification (187), HTTPS (182) <!-- sysd-msg-114 -->
733. **WebSocket extensions** — Intermediate · Concept · Minor · builds on: WebSocket opening handshake (718), WebSocket frames and messages (719) <!-- sysd-msg-118 -->
734. **WebSocket masking** — Intermediate · Method · Minor · builds on: WebSocket frames and messages (719) <!-- sysd-msg-111 -->
735. **WebSocket ping and pong** — Intermediate · Concept · Minor · builds on: WebSocket frames and messages (719), TCP keep-alive (83), Heartbeat failure detection (538) <!-- sysd-msg-112 -->
736. **WebSocket subprotocols** — Intermediate · Concept · Minor · builds on: WebSocket opening handshake (718), WebSocket frames and messages (719), Application-layer protocols (44) <!-- sysd-msg-117 -->
737. **WebSocket version negotiation** — Intermediate · Process · Minor · builds on: WebSocket opening handshake (718) <!-- sysd-msg-120 -->
738. **Comet** — Intermediate · Concept · Minor · builds on: Push technology (712), Long polling (713), HTTPS (182), Polling (711) <!-- sysd-msg-146 -->
739. **C10k problem** — Intermediate · Concept · Minor · builds on: Network socket (49), Client-server model (38) <!-- sysd-msg-147 -->
740. **Push service operations and security** — Intermediate · Practice · Minor · builds on: Web push (715), C10k problem (739), Transport Layer Security (181) <!-- sysd-msg-151 -->

## Reliability, security and operations


### Resilience: circuit breakers, rate limiting and idempotency

741. **Rate limiting** — Intermediate · Concept · Landmark · builds on: DDoS (308), Latency vs throughput (33) <!-- sysd-reliab-075 -->
742. **Fault tolerance** — Foundational · Concept · Major · builds on: Single point of failure (474) <!-- sysd-reliab-082 -->
743. **Fault tolerance techniques** — Intermediate · Classification · Major · builds on: Fault tolerance (742), Replication (473), Failover (475), Load balancing (237), Redundancy (449) <!-- sysd-reliab-083 -->
744. **Cascading failure** — Intermediate · Concept · Major · builds on: Fault tolerance (742), Single point of failure (474), Performance bottleneck (487) <!-- sysd-reliab-168 -->
745. **Deadline propagation** — Intermediate · Method · Major · builds on: Remote procedure call (689), Timeout antipattern (653), Cascading failure (744) <!-- sysd-reliab-176 -->
746. **Resource exhaustion** — Intermediate · Concept · Major · builds on: Cascading failure (744), Performance bottleneck (487) <!-- sysd-reliab-178 -->
747. **Load shedding** — Intermediate · Method · Major · builds on: Cascading failure (744), Rate limiting (741), Resource exhaustion (746) <!-- sysd-reliab-170 -->
748. **Client-side throttling** — Advanced · Method · Major · builds on: Rate limiting (741), Load shedding (747) <!-- sysd-reliab-171 -->
749. **Bandwidth throttling** — Intermediate · Concept · Minor · builds on: Rate limiting (741), Bandwidth (20), Network throughput (30) <!-- sysd-reliab-169 -->
750. **Token bucket** — Intermediate · Method · Major · builds on: Rate limiting (741), Bandwidth (20) <!-- sysd-reliab-088 -->
751. **Leaky bucket** — Intermediate · Method · Major · builds on: Rate limiting (741), Bandwidth (20) <!-- sysd-reliab-086 -->
752. **Resilience patterns** — Intermediate · Concept · Major · builds on: Fault tolerance (742), Cascading failure (744) <!-- sysd-reliab-078 -->
753. **Fail-fast and fail-safe design** — Intermediate · Practice · Minor · builds on: Fault tolerance (742) <!-- sysd-reliab-085 -->
754. **Graceful degradation** — Foundational · Concept · Minor · builds on: Fault tolerance (742) <!-- sysd-reliab-084 -->
755. **Recovering from a cascading failure** — Intermediate · Practice · Major · builds on: Cascading failure (744), Load shedding (747), Graceful degradation (754), Resource exhaustion (746) <!-- sysd-reliab-181 -->
756. **Rate limiting algorithms** — Intermediate · Classification · Major · builds on: Rate limiting (741) <!-- sysd-reliab-076 -->
757. **Rate limiting in distributed systems** — Advanced · Concept · Major · builds on: Rate limiting algorithms (756), Load balancing (237), Consistency model (517), Rate limiting (741) <!-- sysd-reliab-077 -->
758. **Measuring capacity beyond QPS** — Intermediate · Concept · Minor · builds on: Capacity planning (470), Latency vs throughput (33) <!-- sysd-reliab-173 -->
759. **Per-customer quotas** — Intermediate · Method · Minor · builds on: Rate limiting (741), Measuring capacity beyond QPS (758), Load shedding (747) <!-- sysd-reliab-172 -->
760. **Request criticality** — Advanced · Method · Minor · builds on: Load shedding (747), Graceful degradation (754) <!-- sysd-reliab-174 -->
761. **Cascading failure triggers** — Intermediate · Classification · Minor · builds on: Cascading failure (744), Resource exhaustion (746) <!-- sysd-reliab-179 -->
762. **Cold cache and slow startup** — Intermediate · Concept · Minor · builds on: Caching (267), Cache hit ratio (270), Cascading failure (744) <!-- sysd-reliab-180 -->
763. **Load testing to failure** — Intermediate · Practice · Minor · builds on: Cascading failure (744), Resource exhaustion (746), Capacity planning (470) <!-- sysd-reliab-183 -->
764. **Queue management for overload** — Intermediate · Method · Minor · builds on: Backpressure (610), Load shedding (747), Resource exhaustion (746) <!-- sysd-reliab-177 -->
765. **Preventing server overload** — Intermediate · Practice · Major · builds on: Load testing to failure (763), Load shedding (747), Graceful degradation (754), Capacity planning (470), Queue management for overload (764), Cascading failure (744) <!-- sysd-reliab-182 -->
766. **Retry strategies** — Intermediate · Classification · Minor · builds on: Fault tolerance (742), Fallacies of distributed computing (642), Timeout antipattern (653) <!-- sysd-reliab-069 -->
767. **Circuit breaker** — Intermediate · Method · Major · builds on: Cascading failure (744), Fault tolerance (742), Retry strategies (766), Remote procedure call (689) <!-- sysd-reliab-067 -->
768. **Idempotency** — Intermediate · Concept · Landmark · builds on: Idempotent HTTP methods (139), Retry strategies (766) <!-- sysd-reliab-071 -->
769. **Exponential backoff** — Intermediate · Method · Major · builds on: Retry strategies (766) <!-- sysd-reliab-079 -->
770. **Retry budgets** — Intermediate · Method · Major · builds on: Retry strategies (766), Cascading failure (744), Rate limiting (741) <!-- sysd-reliab-175 -->
771. **Exactly-once execution** — Intermediate · Concept · Major · builds on: Idempotency (768), Retry strategies (766), Message delivery semantics (594) <!-- sysd-reliab-070 -->
772. **Idempotency keys** — Intermediate · Method · Major · builds on: Idempotency (768), POST versus PUT (175), Retry strategies (766) <!-- sysd-reliab-073 -->
773. **Circuit breaker states** — Intermediate · Process · Minor · builds on: Circuit breaker (767) <!-- sysd-reliab-068 -->
774. **Backoff jitter** — Intermediate · Method · Minor · builds on: Exponential backoff (769), Thundering herd problem (304) <!-- sysd-reliab-081 -->
775. **Truncated exponential backoff** — Intermediate · Method · Minor · builds on: Exponential backoff (769) <!-- sysd-reliab-080 -->
776. **Idempotency use cases** — Intermediate · Concept · Minor · builds on: Idempotency (768), Retry strategies (766), Message delivery semantics (594) <!-- sysd-reliab-072 -->
777. **Hierarchical token bucket** — Advanced · Method · Minor · builds on: Token bucket (750), Bandwidth (20) <!-- sysd-reliab-089 -->
778. **Idempotent consumers** — Intermediate · Method · Minor · builds on: Idempotency (768), Message delivery semantics (594), Message queue (592) <!-- sysd-reliab-074 -->
779. **Traffic shaping and policing** — Intermediate · Concept · Minor · builds on: Rate limiting (741), Bandwidth (20), Bandwidth throttling (749) <!-- sysd-reliab-087 -->
780. **Token bucket versus leaky bucket** — Intermediate · Concept · Minor · builds on: Token bucket (750), Leaky bucket (751), Traffic shaping and policing (779) <!-- sysd-reliab-090 -->

### Service levels and disaster recovery

781. **Disaster recovery** — Intermediate · Process · Landmark · builds on: High availability (448), Redundancy (449), Replication (473) <!-- sysd-reliab-091 -->
782. **Backup** — Foundational · Concept · Major · builds on: Computer data storage (410) <!-- sysd-reliab-189 -->
783. **Data integrity** — Intermediate · Concept · Major · builds on: Durability (414), Replication (473), Backup (782) <!-- sysd-reliab-205 -->
784. **Monitoring** — Foundational · Concept · Major <!-- sysd-reliab-201 -->
785. **Service level indicator** — Intermediate · Concept · Major · builds on: Latency (19), Availability and the nines (463), Monitoring (784), Network throughput (30) <!-- sysd-reliab-099 -->
786. **Service level objective** — Intermediate · Concept · Landmark · builds on: Service level indicator (785), Availability and the nines (463) <!-- sysd-reliab-103 -->
787. **Service-level agreement** — Intermediate · Concept · Major · builds on: Service level objective (786), Service level indicator (785), Availability and the nines (463) <!-- sysd-reliab-100 -->
788. **Recovery point objective** — Intermediate · Concept · Major · builds on: Disaster recovery (781), Backup (782), Recovery time and recovery point objectives (466) <!-- sysd-reliab-093 -->
789. **Backup methods** — Intermediate · Classification · Major · builds on: Backup (782), Recovery point objective (788) <!-- sysd-reliab-190 -->
790. **Recovery time objective** — Intermediate · Concept · Major · builds on: Disaster recovery (781), Recovery time and recovery point objectives (466) <!-- sysd-reliab-092 -->
791. **Hot, warm and cold sites** — Intermediate · Classification · Major · builds on: Disaster recovery (781), Recovery time objective (790), Active-active and active-passive clusters (467), Recovery point objective (788) <!-- sysd-reliab-095 -->
792. **Defense in depth for data integrity** — Intermediate · Method · Major · builds on: Data integrity (783), Backup (782), Replication (473) <!-- sysd-reliab-206 -->
793. **Replication is not backup** — Intermediate · Concept · Major · builds on: Replication (473), Backup (782), Data integrity (783) <!-- sysd-reliab-210 -->
794. **Soft deletion** — Intermediate · Method · Major · builds on: Data integrity (783), Defense in depth for data integrity (792), Database (325), Backup (782) <!-- sysd-reliab-207 -->
795. **Backend subsetting** — Advanced · Method · Major · builds on: Load balancing (237), Client-side load balancing (242), Connection pooling (343) <!-- sysd-reliab-223 -->
796. **Lame duck state** — Advanced · Method · Major · builds on: Health checks (250), Client-side load balancing (242), Load balancing (237) <!-- sysd-reliab-222 -->
797. **Limits of simple round robin** — Advanced · Concept · Major · builds on: Round robin load balancing (244), Lame duck state (796), Backend subsetting (795), Client-side load balancing (242) <!-- sysd-reliab-224 -->
798. **Virtual IP load balancing** — Intermediate · Method · Major · builds on: IP address (46), Load balancing (237), Layer 4 and layer 7 load balancing (247), Consistent hashing (509) <!-- sysd-reliab-220 -->
799. **Error budget** — Intermediate · Method · Major · builds on: Service level objective (786), Service level indicator (785), Availability and the nines (463) <!-- sysd-reliab-196 -->
800. **Reliability versus cost** — Intermediate · Concept · Major · builds on: Availability and the nines (463), Service level objective (786), Redundancy (449) <!-- sysd-reliab-197 -->
801. **Four golden signals** — Intermediate · Method · Major · builds on: Monitoring (784), Latency (19), Network throughput (30), Resource exhaustion (746) <!-- sysd-reliab-202 -->
802. **Choosing service level indicators** — Intermediate · Practice · Major · builds on: Service level indicator (785), Monitoring (784), Four golden signals (801) <!-- sysd-reliab-193 -->
803. **Choosing SLO targets** — Intermediate · Practice · Major · builds on: Service level objective (786), Choosing service level indicators (802), Reliability versus cost (800) <!-- sysd-reliab-194 -->
804. **Chaos engineering** — Intermediate · Practice · Major · builds on: Fault tolerance (742), Redundancy (449), Monitoring (784) <!-- sysd-reliab-188 -->
805. **Business continuity planning** — Intermediate · Concept · Major · builds on: Disaster recovery (781) <!-- sysd-reliab-184 -->
806. **High availability architectures** — Intermediate · Classification · Major · builds on: High availability (448), Active-active and active-passive clusters (467), Failover (475), Redundancy (449), Replication (473) <!-- sysd-reliab-097 -->
807. **Observability** — Intermediate · Concept · Major · builds on: Monitoring (784), Distributed tracing (664), Latency (19) <!-- sysd-reliab-098 -->
808. **Site reliability engineering** — Intermediate · Practice · Major · builds on: Monitoring (784), High availability (448), Service level objective (786), Observability (807) <!-- sysd-reliab-104 -->
809. **3-2-1 backup rule** — Foundational · Practice · Minor · builds on: Backup (782), Storage device characteristics (420) <!-- sysd-reliab-191 -->
810. **Tiered backup strategy** — Advanced · Method · Major · builds on: Backup (782), Backup methods (789), 3-2-1 backup rule (809), Recovery point objective (788) <!-- sysd-reliab-209 -->
811. **Backing up live data** — Intermediate · Method · Minor · builds on: Backup (782), Backup methods (789) <!-- sysd-reliab-192 -->
812. **Disaster recovery strategies** — Intermediate · Classification · Minor · builds on: Disaster recovery (781), Business continuity planning (805), Recovery time objective (790), Recovery point objective (788) <!-- sysd-reliab-094 -->
813. **Disaster recovery practices** — Intermediate · Practice · Minor · builds on: Disaster recovery (781), Business continuity planning (805), Disaster recovery strategies (812) <!-- sysd-reliab-096 -->
814. **Testing data recovery** — Intermediate · Practice · Major · builds on: Backup (782), Data integrity (783), Disaster recovery practices (813) <!-- sysd-reliab-214 -->
815. **Backups versus archives** — Intermediate · Concept · Minor · builds on: Backup (782), Data integrity (783) <!-- sysd-reliab-208 -->
816. **Data loss failure modes** — Advanced · Classification · Minor · builds on: Data integrity (783), Defense in depth for data integrity (792), Backup (782) <!-- sysd-reliab-212 -->
817. **Out-of-band data validation** — Advanced · Method · Major · builds on: Data integrity (783), Defense in depth for data integrity (792), Data loss failure modes (816), Backup (782) <!-- sysd-reliab-213 -->
818. **Point-in-time recovery** — Advanced · Concept · Minor · builds on: Backup (782), Backup methods (789), Recovery point objective (788) <!-- sysd-reliab-211 -->
819. **Least-loaded round robin** — Advanced · Method · Minor · builds on: Limits of simple round robin (797), Backend subsetting (795), Round robin load balancing (244) <!-- sysd-reliab-225 -->
820. **Weighted round robin with backend feedback** — Advanced · Method · Minor · builds on: Limits of simple round robin (797), Backend subsetting (795), Round robin load balancing (244) <!-- sysd-reliab-226 -->
821. **Packet forwarding in network load balancers** — Advanced · Classification · Minor · builds on: Virtual IP load balancing (798), Network address translation (63), Encapsulation and de-encapsulation (41), OSI model layers (39), Load balancing (237) <!-- sysd-reliab-221 -->
822. **Managing expectations with SLOs** — Intermediate · Practice · Minor · builds on: Service level objective (786), Service level indicator (785) <!-- sysd-reliab-195 -->
823. **Request-based availability** — Intermediate · Concept · Minor · builds on: Availability and the nines (463), Measuring availability (465), Service level indicator (785) <!-- sysd-reliab-198 -->
824. **Setting an availability target** — Intermediate · Practice · Minor · builds on: Availability and the nines (463), Reliability versus cost (800), Service level objective (786) <!-- sysd-reliab-199 -->
825. **Multiple service levels for infrastructure** — Advanced · Method · Minor · builds on: Service level objective (786), Reliability versus cost (800), Setting an availability target (824), Redundancy (449) <!-- sysd-reliab-200 -->
826. **Borg** — Intermediate · Concept · Minor · builds on: Computer cluster (460) <!-- sysd-reliab-217 -->
827. **Life of a request** — Intermediate · Process · Minor · builds on: DNS lookup process (107), Global server load balancing (249), Reverse proxy (256), Bigtable (576), Load balancing (237), DNS load balancing (238) <!-- sysd-reliab-219 -->
828. **N+2 capacity planning** — Intermediate · Method · Minor · builds on: Capacity planning (470), Redundancy (449), Measuring capacity beyond QPS (758), Borg (826) <!-- sysd-reliab-218 -->
829. **SLA components** — Intermediate · Classification · Minor · builds on: Service-level agreement (787), Service level objective (786), Monitoring (784) <!-- sysd-reliab-101 -->
830. **Cloud service level agreements** — Intermediate · Concept · Minor · builds on: Service-level agreement (787), SLA components (829), Availability and the nines (463) <!-- sysd-reliab-102 -->
831. **Black-box and white-box monitoring** — Intermediate · Classification · Minor · builds on: Monitoring (784), Observability (807) <!-- sysd-reliab-203 -->
832. **Alerting and paging practice** — Intermediate · Practice · Major · builds on: Monitoring (784), Black-box and white-box monitoring (831), Four golden signals (801) <!-- sysd-reliab-204 -->
833. **Incident management** — Intermediate · Process · Major · builds on: Monitoring (784), Alerting and paging practice (832), Mean time to repair (464), Service-level agreement (787) <!-- sysd-reliab-187 -->
834. **SRE team models** — Advanced · Classification · Minor · builds on: Site reliability engineering (808) <!-- sysd-reliab-105 -->
835. **Business impact analysis** — Intermediate · Method · Minor · builds on: Business continuity planning (805), Recovery time objective (790), Recovery point objective (788) <!-- sysd-reliab-185 -->
836. **Disaster recovery tiers** — Intermediate · Classification · Minor · builds on: Disaster recovery (781), Backup (782), Recovery time objective (790), Hot, warm and cold sites (791) <!-- sysd-reliab-186 -->
837. **Gmail restore from GTape** — Advanced · Case study · Minor · builds on: Backup (782), Data integrity (783), Defense in depth for data integrity (792), Replication is not backup (793), Disaster recovery (781) <!-- sysd-reliab-215 -->
838. **Runaway deletion at Google Music** — Advanced · Case study · Minor · builds on: Soft deletion (794), Data integrity (783), Out-of-band data validation (817), Backup (782) <!-- sysd-reliab-216 -->

### Containers, orchestration and deployment

839. **Chroot** — Intermediate · Concept · Minor <!-- sysd-reliab-146 -->
840. **Kubernetes** — Intermediate · Concept · Landmark · builds on: Computer cluster (460), Horizontal and vertical scaling (451), Load balancing (237) <!-- sysd-reliab-050 -->
841. **Containers** — Intermediate · Concept · Landmark <!-- sysd-reliab-063 -->
842. **Cgroups** — Advanced · Concept · Major · builds on: Containers (841) <!-- sysd-reliab-145 -->
843. **Linux namespaces and cgroups** — Advanced · Concept · Major · builds on: Containers (841), Cgroups (842), Chroot (839) <!-- sysd-reliab-064 -->
844. **Pod lifecycle** — Intermediate · Process · Major <!-- sysd-reliab-227 -->
845. **Container probes** — Intermediate · Concept · Major · builds on: Health checks (250), Containers (841) <!-- sysd-reliab-161 -->
846. **Docker** — Intermediate · Concept · Major · builds on: Containers (841) <!-- sysd-reliab-045 -->
847. **Container images and registries** — Intermediate · Concept · Major · builds on: Docker (846), Containers (841) <!-- sysd-reliab-046 -->
848. **Container orchestration** — Intermediate · Concept · Major · builds on: Containers (841), Container images and registries (847), Horizontal and vertical scaling (451), High availability (448) <!-- sysd-reliab-148 -->
849. **Container runtime** — Intermediate · Concept · Minor · builds on: Containers (841), Docker (846), Container images and registries (847) <!-- sysd-reliab-049 -->
850. **Kubernetes nodes** — Intermediate · Concept · Major · builds on: Kubernetes (840), Container runtime (849), Containers (841) <!-- sysd-reliab-054 -->
851. **Kubernetes pods** — Intermediate · Concept · Major · builds on: Containers (841), Kubernetes nodes (850), IP address (46), Port numbers (48) <!-- sysd-reliab-055 -->
852. **Pod restart policy** — Intermediate · Concept · Major · builds on: Kubernetes pods (851), Pod lifecycle (844) <!-- sysd-reliab-228 -->
853. **CrashLoopBackOff** — Intermediate · Concept · Minor · builds on: Pod restart policy (852), Exponential backoff (769), Kubernetes pods (851) <!-- sysd-reliab-229 -->
854. **Graceful pod termination** — Intermediate · Process · Minor · builds on: Pod lifecycle (844), Kubernetes nodes (850), Container runtime (849), Kubernetes pods (851) <!-- sysd-reliab-230 -->
855. **Container persistent storage** — Intermediate · Concept · Minor · builds on: Containers (841), Kubernetes pods (851), Stateless and stateful services (452), Computer data storage (410) <!-- sysd-reliab-061 -->
856. **Sidecar and init containers** — Intermediate · Concept · Minor · builds on: Kubernetes pods (851), Containers (841), Container persistent storage (855) <!-- sysd-reliab-159 -->
857. **Labels and selectors** — Intermediate · Concept · Minor · builds on: Kubernetes pods (851), Kubernetes nodes (850) <!-- sysd-reliab-060 -->
858. **Kubernetes services** — Intermediate · Concept · Major · builds on: Kubernetes pods (851), Labels and selectors (857), Service discovery (662), Load balancing (237) <!-- sysd-reliab-058 -->
859. **Kubernetes Service types** — Intermediate · Classification · Major · builds on: Kubernetes services (858), Kubernetes nodes (850), Load balancing (237), Port numbers (48) <!-- sysd-reliab-151 -->
860. **Kubernetes Ingress** — Intermediate · Concept · Major · builds on: Kubernetes services (858), Kubernetes Service types (859), Reverse proxy (256), TLS termination (252), Load balancing (237) <!-- sysd-reliab-152 -->
861. **Ingress path and host matching** — Intermediate · Concept · Minor · builds on: Kubernetes Ingress (860), HTTP request and response messages (133), Domain name hierarchy (93) <!-- sysd-reliab-153 -->
862. **Docker run workflow** — Intermediate · Process · Minor · builds on: Docker (846), Container images and registries (847), Client-server model (38), Containers (841) <!-- sysd-reliab-042 -->
863. **Docker Compose** — Intermediate · Concept · Minor · builds on: Docker (846), Container images and registries (847), Docker run workflow (862) <!-- sysd-reliab-047 -->
864. **Docker Swarm** — Advanced · Concept · Minor · builds on: Docker (846), Docker Compose (863), Container orchestration (848), Computer cluster (460), Raft (555) <!-- sysd-reliab-048 -->
865. **Virtual machine** — Intermediate · Concept · Major <!-- sysd-reliab-065 -->
866. **Hypervisor** — Intermediate · Concept · Major · builds on: Virtual machine (865) <!-- sysd-reliab-044 -->
867. **Virtualization versus containerization** — Intermediate · Concept · Major · builds on: Virtual machine (865), Containers (841), Hypervisor (866) <!-- sysd-reliab-043 -->
868. **Virtual machine snapshots and migration** — Advanced · Method · Minor · builds on: Virtual machine (865), Hypervisor (866), Backup (782), Failover (475) <!-- sysd-reliab-066 -->
869. **Physical, virtual and container deployment** — Foundational · Concept · Minor · builds on: Virtual machine (865) <!-- sysd-reliab-149 -->
870. **Continuous delivery** — Intermediate · Practice · Major <!-- sysd-reliab-143 -->
871. **CI/CD pipeline** — Intermediate · Practice · Major · builds on: Continuous delivery (870) <!-- sysd-reliab-144 -->
872. **Release engineering** — Intermediate · Practice · Major · builds on: Continuous delivery (870), CI/CD pipeline (871) <!-- sysd-reliab-162 -->
873. **Infrastructure as code** — Intermediate · Practice · Major · builds on: Virtual machine (865), Continuous delivery (870) <!-- sysd-reliab-147 -->
874. **Twelve-factor app** — Intermediate · Practice · Major · builds on: Stateless and stateful services (452), Horizontal and vertical scaling (451), Continuous delivery (870), Containers (841) <!-- sysd-reliab-041 -->
875. **ConfigMaps and Secrets** — Intermediate · Concept · Minor · builds on: Kubernetes pods (851), Twelve-factor app (874), Container persistent storage (855) <!-- sysd-reliab-059 -->
876. **Hermetic builds** — Intermediate · Practice · Minor · builds on: Release engineering (872), CI/CD pipeline (871) <!-- sysd-reliab-165 -->
877. **Release branching and cherry-picking** — Intermediate · Method · Minor · builds on: Release engineering (872), CI/CD pipeline (871) <!-- sysd-reliab-164 -->
878. **Release pipeline** — Intermediate · Process · Major · builds on: Release engineering (872), Release branching and cherry-picking (877), Hermetic builds (876), CI/CD pipeline (871) <!-- sysd-reliab-163 -->
879. **Horizontal Pod Autoscaler** — Intermediate · Concept · Major · builds on: Autoscaling (454) <!-- sysd-reliab-155 -->
880. **Autoscaler flapping controls** — Advanced · Method · Minor · builds on: Horizontal Pod Autoscaler (879), Autoscaling (454) <!-- sysd-reliab-156 -->
881. **Scaling to zero** — Advanced · Concept · Minor · builds on: Horizontal Pod Autoscaler (879), Autoscaling (454) <!-- sysd-reliab-157 -->
882. **Pod resource requests and limits** — Intermediate · Concept · Major · builds on: Kubernetes pods (851), Kubernetes nodes (850), Cgroups (842) <!-- sysd-reliab-160 -->
883. **Rolling update** — Intermediate · Method · Major <!-- sysd-reliab-150 -->
884. **Deployments and ReplicaSets** — Intermediate · Concept · Major · builds on: Kubernetes pods (851), Labels and selectors (857) <!-- sysd-reliab-056 -->
885. **StatefulSets** — Advanced · Concept · Minor · builds on: Deployments and ReplicaSets (884), Stateless and stateful services (452), Container persistent storage (855) <!-- sysd-reliab-057 -->
886. **Kubernetes control plane** — Intermediate · Concept · Major · builds on: Kubernetes (840), Kubernetes nodes (850), REST (688), High availability (448) <!-- sysd-reliab-051 -->
887. **Kubernetes controllers** — Intermediate · Concept · Major · builds on: Kubernetes (840), Kubernetes control plane (886), Kubernetes pods (851) <!-- sysd-reliab-053 -->
888. **Pod templates** — Intermediate · Concept · Minor · builds on: Kubernetes pods (851), Deployments and ReplicaSets (884), Kubernetes controllers (887) <!-- sysd-reliab-158 -->
889. **Kubernetes operators** — Advanced · Concept · Minor · builds on: Kubernetes controllers (887), Kubernetes control plane (886), StatefulSets (885) <!-- sysd-reliab-062 -->
890. **etcd** — Advanced · Concept · Minor · builds on: Kubernetes control plane (886), Key-value store (331), CAP theorem (520), Replication (473) <!-- sysd-reliab-052 -->
891. **Ingress controllers and classes** — Intermediate · Concept · Minor · builds on: Kubernetes Ingress (860), Kubernetes controllers (887), Reverse proxy (256) <!-- sysd-reliab-154 -->
892. **Feature toggle** — Intermediate · Method · Major · builds on: Continuous delivery (870) <!-- sysd-reliab-141 -->
893. **Configuration distribution models** — Intermediate · Classification · Major · builds on: Release engineering (872), Release pipeline (878), Feature toggle (892), Twelve-factor app (874) <!-- sysd-reliab-166 -->
894. **Blue-green deployment** — Intermediate · Method · Major · builds on: Load balancing (237), Domain Name System (90) <!-- sysd-reliab-039 -->
895. **Deployment strategies** — Intermediate · Classification · Major · builds on: High availability (448), Load balancing (237), Blue-green deployment (894), Kubernetes (840) <!-- sysd-reliab-040 -->
896. **Canary release** — Intermediate · Method · Major · builds on: Deployment strategies (895), Load balancing (237), Feature toggle (892) <!-- sysd-reliab-142 -->
897. **Risk-based rollouts** — Intermediate · Method · Minor · builds on: Release engineering (872), Release pipeline (878), Deployment strategies (895), Canary release (896) <!-- sysd-reliab-167 -->

### Authentication and security

898. **Authentication** — Foundational · Concept · Landmark <!-- sysd-reliab-015 -->
899. **Cross-site scripting** — Intermediate · Concept · Major · builds on: What happens when you type a URL (156), HTTP origins and certificate verification (187), HTTP statelessness and sessions (136) <!-- sysd-reliab-127 -->
900. **Authentication factors** — Foundational · Classification · Major · builds on: Authentication (898) <!-- sysd-reliab-016 -->
901. **Cryptographic salt** — Intermediate · Concept · Major · builds on: Hash function (210) <!-- sysd-reliab-120 -->
902. **Authorization** — Foundational · Concept · Major · builds on: Authentication (898) <!-- sysd-reliab-030 -->
903. **OAuth 2.0** — Intermediate · Concept · Landmark · builds on: Authentication (898), Authorization (902) <!-- sysd-reliab-022 -->
904. **Principle of least privilege** — Intermediate · Concept · Major · builds on: Authorization (902) <!-- sysd-reliab-126 -->
905. **Multi-factor authentication** — Foundational · Concept · Major · builds on: Authentication (898), Authentication factors (900) <!-- sysd-reliab-017 -->
906. **OAuth pseudo-authentication** — Intermediate · Concept · Major · builds on: Authentication (898), OAuth 2.0 (903), Authorization (902) <!-- sysd-reliab-034 -->
907. **Continuous authentication** — Intermediate · Concept · Minor · builds on: Authentication (898), Authentication factors (900) <!-- sysd-reliab-018 -->
908. **Digital authentication** — Intermediate · Process · Minor · builds on: Authentication (898) <!-- sysd-reliab-019 -->
909. **Access control models** — Intermediate · Classification · Major · builds on: Authorization (902) <!-- sysd-reliab-031 -->
910. **Secure system design checklist** — Foundational · Practice · Major · builds on: Authentication (898), Authorization (902), HTTPS (182) <!-- sysd-reliab-028 -->
911. **Session and token authentication** — Foundational · Classification · Major · builds on: Authentication (898), HTTP statelessness and sessions (136), HTTP cookie (137) <!-- sysd-reliab-021 -->
912. **Cross-site request forgery** — Intermediate · Concept · Major · builds on: HTTP statelessness and sessions (136), HTTP cookie (137), Session and token authentication (911), HTTP origins and certificate verification (187) <!-- sysd-reliab-129 -->
913. **Access token** — Intermediate · Concept · Major · builds on: OAuth 2.0 (903), Session and token authentication (911) <!-- sysd-reliab-134 -->
914. **Refresh token** — Intermediate · Concept · Major · builds on: Access token (913) <!-- sysd-reliab-135 -->
915. **JSON Web Token** — Intermediate · Concept · Major · builds on: Session and token authentication (911), Public-key cryptography (132), Symmetric-key encryption (142), Authentication (898) <!-- sysd-reliab-032 -->
916. **OpenID Connect** — Intermediate · Concept · Major · builds on: OAuth 2.0 (903), OAuth pseudo-authentication (906), Authentication (898), JSON Web Token (915) <!-- sysd-reliab-024 -->
917. **JWT claims** — Intermediate · Concept · Major · builds on: JSON Web Token (915) <!-- sysd-reliab-138 -->
918. **Creating and validating a JWT** — Intermediate · Process · Major · builds on: JSON Web Token (915), JWT claims (917), Public-key cryptography (132) <!-- sysd-reliab-139 -->
919. **CSRF prevention** — Intermediate · Method · Major · builds on: Cross-site request forgery (912), Session and token authentication (911) <!-- sysd-reliab-130 -->
920. **Rainbow table** — Intermediate · Concept · Minor · builds on: Hash function (210), Cryptographic salt (901) <!-- sysd-reliab-121 -->
921. **Salted password hashing** — Intermediate · Practice · Major · builds on: Authentication (898), Hash function (210), Cryptographic salt (901), Rainbow table (920) <!-- sysd-reliab-020 -->
922. **OAuth 2.0 clients and endpoints** — Intermediate · Concept · Minor · builds on: OAuth 2.0 (903), HTTP redirection status codes (150) <!-- sysd-reliab-136 -->
923. **OAuth 2.0 authorization flow** — Intermediate · Process · Major · builds on: OAuth 2.0 (903), Access token (913), OAuth 2.0 clients and endpoints (922) <!-- sysd-reliab-023 -->
924. **OAuth 2.0 grant types** — Intermediate · Classification · Major · builds on: OAuth 2.0 (903), OAuth 2.0 authorization flow (923), Access token (913) <!-- sysd-reliab-132 -->
925. **Authorization code grant** — Intermediate · Process · Major · builds on: OAuth 2.0 grant types (924), Access token (913), Refresh token (914), OAuth 2.0 clients and endpoints (922), OAuth 2.0 (903) <!-- sysd-reliab-133 -->
926. **OAuth 2.0 security threats** — Intermediate · Concept · Major · builds on: OAuth 2.0 authorization flow (923), Authorization code grant (925), OAuth 2.0 clients and endpoints (922) <!-- sysd-reliab-035 -->
927. **Proof Key for Code Exchange** — Intermediate · Method · Major · builds on: Authorization code grant (925), OAuth 2.0 security threats (926), OAuth 2.0 clients and endpoints (922), Hash function (210), OAuth 2.0 (903), OAuth 2.0 authorization flow (923) <!-- sysd-reliab-137 -->
928. **XSS prevention** — Intermediate · Method · Minor · builds on: Cross-site scripting (899) <!-- sysd-reliab-128 -->
929. **WebAuthn** — Intermediate · Concept · Major · builds on: Authentication (898), Multi-factor authentication (905), Public-key cryptography (132), API (687) <!-- sysd-reliab-124 -->
930. **API security practices** — Intermediate · Practice · Major · builds on: API (687), OAuth 2.0 (903), Authorization (902), WebAuthn (929), API gateway (258) <!-- sysd-reliab-029 -->
931. **Zero trust security model** — Intermediate · Concept · Major · builds on: Authentication (898), Authorization (902), Principle of least privilege (904) <!-- sysd-reliab-131 -->
932. **Signed, encrypted and nested JWTs** — Advanced · Concept · Minor · builds on: JSON Web Token (915), Creating and validating a JWT (918), Public-key cryptography (132) <!-- sysd-reliab-140 -->
933. **JWT security pitfalls** — Intermediate · Practice · Major · builds on: JSON Web Token (915), Creating and validating a JWT (918), Signed, encrypted and nested JWTs (932) <!-- sysd-reliab-033 -->
934. **Argon2** — Intermediate · Method · Minor · builds on: Salted password hashing (921), Hash function (210) <!-- sysd-reliab-123 -->
935. **bcrypt** — Intermediate · Method · Minor · builds on: Salted password hashing (921), Hash function (210), Cryptographic salt (901) <!-- sysd-reliab-122 -->
936. **MFA bypass attacks** — Intermediate · Concept · Minor · builds on: Authentication factors (900), Multi-factor authentication (905) <!-- sysd-reliab-119 -->
937. **Identity provider** — Intermediate · Concept · Minor · builds on: Authentication (898) <!-- sysd-reliab-026 -->
938. **Single sign-on** — Intermediate · Concept · Major · builds on: Authentication (898), Session and token authentication (911), Identity provider (937) <!-- sysd-reliab-025 -->
939. **Kerberos** — Intermediate · Concept · Major · builds on: Authentication (898), Public-key cryptography (132), Single sign-on (938) <!-- sysd-reliab-125 -->
940. **OpenID** — Intermediate · Concept · Minor · builds on: Authentication (898), Identity provider (937) <!-- sysd-reliab-036 -->
941. **Single sign-on risks** — Intermediate · Concept · Major · builds on: Single sign-on (938), Authentication factors (900), Multi-factor authentication (905) <!-- sysd-reliab-037 -->
942. **SAML** — Intermediate · Concept · Minor · builds on: Single sign-on (938), Identity provider (937), Authorization (902) <!-- sysd-reliab-027 -->
943. **Single sign-on configurations** — Intermediate · Classification · Minor · builds on: Single sign-on (938), Kerberos (939), Identity provider (937) <!-- sysd-reliab-038 -->

## Design interview questions


### Design a URL shortener

944. **URL shortening** — Foundational · Concept · Major · builds on: HTTP redirection status codes (150) <!-- sysd-q-030 -->
945. **Drawbacks of URL shortening** — Intermediate · Concept · Minor · builds on: URL shortening (944) <!-- sysd-q-032 -->
946. **Short link expiration** — Intermediate · Practice · Minor · builds on: URL shortening (944), Time to live (292) <!-- sysd-q-033 -->
947. **Base62 encoding** — Foundational · Concept · Minor · builds on: Base64 (211) <!-- sysd-q-034 -->
948. **Short URL key generation** — Intermediate · Method · Minor · builds on: URL shortening (944), Base62 encoding (947), Hash function (210), Distributed unique ID generation (223) <!-- sysd-q-031 -->
949. **Designing a URL shortener** — Intermediate · Worked example · Landmark · builds on: Short URL key generation (948), HTTP redirection status codes (150), Caching (267), Database sharding (504), Back-of-the-envelope estimation (34), Consistent hashing (509) <!-- sysd-q-029 -->

### Design Pastebin

950. **Pastebin** — Foundational · Concept · Major · builds on: Short URL key generation (948) <!-- sysd-q-063 -->
951. **Designing Pastebin** — Intermediate · Worked example · Landmark · builds on: Short URL key generation (948), Object storage (427), Caching (267), Read replica pattern (486), Short link expiration (946), Database index (376) <!-- sysd-q-062 -->

### Design a chat service like WhatsApp

952. **Instant messaging** — Foundational · Concept · Major · builds on: Client-server model (38), Synchronous and asynchronous communication (590) <!-- sysd-q-003 -->
953. **End-to-end encryption** — Intermediate · Concept · Major · builds on: Public-key cryptography (132), Symmetric-key encryption (142), Man-in-the-middle attack (183), Instant messaging (952), Transport Layer Security (181) <!-- sysd-q-070 -->
954. **Store and forward** — Foundational · Concept · Major · builds on: Synchronous and asynchronous communication (590), Message queue (592) <!-- sysd-q-069 -->
955. **Signal Protocol** — Advanced · Concept · Major · builds on: End-to-end encryption (953), Public-key cryptography (132), Forward secrecy (189), Instant messaging (952) <!-- sysd-q-072 -->
956. **End-to-end encryption versus provider access** — Intermediate · Debate · Minor · builds on: End-to-end encryption (953), Instant messaging (952) <!-- sysd-q-071 -->
957. **Messaging metadata and sealed sender** — Advanced · Concept · Minor · builds on: End-to-end encryption (953), Signal Protocol (955), Instant messaging (952) <!-- sysd-q-073 -->
958. **Chat application on Redis pub/sub** — Intermediate · Method · Minor · builds on: Publish–subscribe pattern (614), Redis (281), Instant messaging (952), WebSocket (717), Message queue versus publish–subscribe (624) <!-- sysd-q-004 -->
959. **Designing a chat service like WhatsApp** — Intermediate · Worked example · Landmark · builds on: WebSocket (717), Store and forward (954), Push notification (714), Object storage (427), Database sharding (504), Message queue (592) <!-- sysd-q-002 -->
960. **How WhatsApp delivers messages** — Intermediate · Case study · Minor · builds on: XMPP (728), Store and forward (954), Instant messaging (952) <!-- sysd-q-005 -->

### Design a social feed like Twitter

961. **Apache Lucene** — Intermediate · Concept · Minor · builds on: Inverted index (381) <!-- sysd-q-093 -->
962. **Fan-out** — Intermediate · Concept · Minor · builds on: Message queue (592), Publish–subscribe pattern (614), Message-oriented middleware (593) <!-- sysd-q-092 -->
963. **Feed fan-out models** — Intermediate · Classification · Major · builds on: Fan-out (962), Caching (267), Message queue (592) <!-- sysd-q-021 -->
964. **Feed ranking** — Intermediate · Concept · Minor · builds on: Feed fan-out models (963) <!-- sysd-q-022 -->
965. **EdgeRank** — Intermediate · Concept · Minor · builds on: Feed ranking (964) <!-- sysd-q-091 -->
966. **Trending topics** — Intermediate · Concept · Minor · builds on: Count-min sketch (228), Stream processing (627), Caching (267), Elasticsearch (330) <!-- sysd-q-026 -->
967. **Designing a social feed like Twitter** — Intermediate · Worked example · Landmark · builds on: Feed fan-out models (963), Feed ranking (964), Caching (267), Elasticsearch (330), Content delivery network (306), Load balancing (237) <!-- sysd-q-020 -->
968. **Twitter's technology stack** — Intermediate · Case study · Minor · builds on: Caching (267), Database (325), SQL vs NoSQL databases (346) <!-- sysd-q-024 -->
969. **Twitter's tweet recommendation pipeline** — Intermediate · Case study · Minor · builds on: Feed ranking (964), Feed fan-out models (963) <!-- sysd-q-023 -->

### Design a video streaming service like Netflix

970. **Streaming media** — Intermediate · Concept · Major · builds on: Internet Protocol (45), Bandwidth (20), Choosing between TCP and UDP (78) <!-- sysd-q-045 -->
971. **Recommender system** — Intermediate · Concept · Major · builds on: Streaming media (970) <!-- sysd-q-047 -->
972. **Collaborative filtering** — Intermediate · Concept · Major · builds on: Recommender system (971) <!-- sysd-q-101 -->
973. **Video codec** — Intermediate · Concept · Major · builds on: Streaming media (970) <!-- sysd-q-102 -->
974. **Adaptive bitrate streaming** — Intermediate · Concept · Landmark · builds on: Streaming media (970), Video codec (973), Bandwidth (20), Network throughput (30), HTTP (131), Content delivery network (306) <!-- sysd-q-042 -->
975. **HTTP Live Streaming** — Intermediate · Concept · Major · builds on: HTTP (131), Adaptive bitrate streaming (974), Streaming media (970) <!-- sysd-q-043 -->
976. **Video on demand** — Foundational · Concept · Minor · builds on: Streaming media (970) <!-- sysd-q-104 -->
977. **MPEG-DASH** — Intermediate · Concept · Major · builds on: Adaptive bitrate streaming (974), HTTP (131), Streaming media (970) <!-- sysd-q-044 -->
978. **Video transcoding** — Intermediate · Concept · Major · builds on: Video codec (973), Message queue (592) <!-- sysd-q-037 -->
979. **Live streaming** — Intermediate · Process · Major · builds on: Streaming media (970), Latency (19), Adaptive bitrate streaming (974), Content delivery network (306) <!-- sysd-q-036 -->
980. **Streaming delivery methods** — Intermediate · Classification · Minor · builds on: Streaming media (970), Content delivery network (306), Peer-to-peer (307) <!-- sysd-q-046 -->
981. **Real-Time Messaging Protocol** — Intermediate · Concept · Minor · builds on: Streaming media (970), Transmission Control Protocol (42) <!-- sysd-q-103 -->
982. **H.264** — Intermediate · Concept · Minor · builds on: Video codec (973) <!-- sysd-q-105 -->
983. **HEVC** — Intermediate · Concept · Minor · builds on: H.264 (982), Video codec (973) <!-- sysd-q-106 -->
984. **AV1** — Intermediate · Concept · Minor · builds on: Video codec (973), HEVC (983), Video transcoding (978), Streaming media (970) <!-- sysd-q-107 -->
985. **Geo-blocking** — Intermediate · Concept · Minor · builds on: IP address (46), Content delivery network (306) <!-- sysd-q-038 -->
986. **Designing a video streaming service like Netflix** — Advanced · Worked example · Landmark · builds on: Adaptive bitrate streaming (974), Video transcoding (978), Content delivery network (306), Object storage (427), Message queue (592), Caching (267) <!-- sysd-q-035 -->
987. **Netflix's technology stack** — Intermediate · Case study · Minor · builds on: Database (325), SQL vs NoSQL databases (346), Stream processing (627), Content delivery network (306) <!-- sysd-q-041 -->
988. **YouTube's video transcoding unit** — Intermediate · Case study · Minor · builds on: Video transcoding (978), Video codec (973) <!-- sysd-q-039 -->
989. **Netflix Open Connect** — Intermediate · Case study · Minor · builds on: Content delivery network (306), CDN origin and edge servers (309), Private CDN (312) <!-- sysd-q-040 -->

### Design a ride-hailing service like Uber

990. **Nearest neighbor search** — Intermediate · Concept · Major <!-- sysd-q-090 -->
991. **Proximity service** — Intermediate · Concept · Major · builds on: Nearest neighbor search (990), Geohash (219), Quadtree (214), Spatial database (347) <!-- sysd-q-017 -->
992. **Dynamic pricing** — Foundational · Concept · Minor <!-- sysd-q-089 -->
993. **Designing a ride-hailing service like Uber** — Advanced · Worked example · Landmark · builds on: Proximity service (991), Geohash (219), Quadtree (214), WebSocket (717), Database sharding (504), Caching (267) <!-- sysd-q-016 -->
994. **Uber's technology stack** — Intermediate · Case study · Minor · builds on: gRPC (697), Apache Kafka (625), Database (325) <!-- sysd-q-018 -->

### Design a web crawler

995. **Web crawler** — Foundational · Concept · Major · builds on: HTTP (131) <!-- sysd-q-049 -->
996. **Robots exclusion protocol** — Foundational · Concept · Major · builds on: Web crawler (995) <!-- sysd-q-055 -->
997. **Crawl politeness policy** — Intermediate · Practice · Major · builds on: Web crawler (995), Robots exclusion protocol (996), Rate limiting (741) <!-- sysd-q-054 -->
998. **Crawl re-visit policy** — Intermediate · Method · Major · builds on: Web crawler (995), HTTP cache freshness (154) <!-- sysd-q-053 -->
999. **Crawl selection policy** — Intermediate · Method · Major · builds on: Web crawler (995) <!-- sysd-q-050 -->
1000. **How search engines work** — Foundational · Process · Major · builds on: Web crawler (995) <!-- sysd-q-056 -->
1001. **Search engine indexing** — Intermediate · Process · Major · builds on: How search engines work (1000), Inverted index (381), Database index (376), Web crawler (995) <!-- sysd-q-108 -->
1002. **PageRank** — Intermediate · Concept · Major · builds on: How search engines work (1000), Web crawler (995) <!-- sysd-q-109 -->
1003. **Cosine similarity** — Intermediate · Concept · Minor <!-- sysd-q-111 -->
1004. **Sitemaps** — Foundational · Concept · Minor · builds on: Web crawler (995), Robots exclusion protocol (996) <!-- sysd-q-112 -->
1005. **Deep web crawling** — Intermediate · Concept · Minor · builds on: Web crawler (995), Database (325) <!-- sysd-q-057 -->
1006. **Focused crawler** — Intermediate · Concept · Minor · builds on: Web crawler (995), Crawl selection policy (999) <!-- sysd-q-052 -->
1007. **URL normalization** — Foundational · Method · Minor · builds on: HTTP resources and representations (166), Web crawler (995) <!-- sysd-q-051 -->
1008. **Spider trap** — Intermediate · Concept · Minor · builds on: Web crawler (995) <!-- sysd-q-113 -->
1009. **Jaccard index** — Intermediate · Concept · Minor <!-- sysd-q-110 -->
1010. **W-shingling** — Intermediate · Method · Minor · builds on: Jaccard index (1009) <!-- sysd-q-114 -->
1011. **Designing a web crawler** — Intermediate · Worked example · Landmark · builds on: Web crawler (995), Crawl politeness policy (997), Inverted index (381), Message queue (592), Database sharding (504), Key-value store (331), Caching (267) <!-- sysd-q-048 -->

### Design a personal finance app like Mint

1012. **Heap** — Intermediate · Concept · Major <!-- sysd-q-087 -->
1013. **Open banking** — Intermediate · Concept · Minor · builds on: API (687), Authorization (902), OAuth 2.0 (903) <!-- sysd-q-088 -->
1014. **Designing a personal finance app** — Intermediate · Worked example · Landmark · builds on: Open banking (1013), Message queue (592), Relational database (326), Object storage (427), Caching (267), Replication (473) <!-- sysd-q-015 -->

### Design a cache for the most recent search queries

1015. **Doubly linked list** — Foundational · Concept · Minor <!-- sysd-q-068 -->
1016. **Designing a search query cache** — Intermediate · Worked example · Landmark · builds on: Least recently used (274), Doubly linked list (1015), Hash table (377), Distributed cache (280), Consistent hashing (509), Caching (267), Cache eviction policies (271), Database sharding (504) <!-- sysd-q-001 -->

### Design a sales rank by category

1017. **Designing a sales rank by category** — Intermediate · Worked example · Landmark · builds on: MapReduce (578), Batch processing (626), Object storage (427), Caching (267), Replication (473), Database index (376) <!-- sysd-q-019 -->

### Design the data structures for a social network

1018. **Social graph** — Foundational · Concept · Minor <!-- sysd-q-155 -->
1019. **Adjacency matrix** — Intermediate · Concept · Major · builds on: Social graph (1018) <!-- sysd-q-159 -->
1020. **Adjacency list** — Intermediate · Concept · Major · builds on: Social graph (1018) <!-- sysd-q-158 -->
1021. **Breadth-first search** — Intermediate · Concept · Major · builds on: Social graph (1018), Adjacency list (1020) <!-- sysd-q-153 -->
1022. **Shortest path problem** — Intermediate · Concept · Major · builds on: Social graph (1018), Breadth-first search (1021) <!-- sysd-q-154 -->
1023. **Bidirectional search** — Intermediate · Method · Major · builds on: Breadth-first search (1021), Shortest path problem (1022) <!-- sysd-q-157 -->
1024. **Six degrees of separation** — Foundational · Concept · Minor · builds on: Social graph (1018) <!-- sysd-q-156 -->
1025. **Designing a social network graph** — Intermediate · Worked example · Landmark · builds on: Social graph (1018), Breadth-first search (1021), Bidirectional search (1023), Database sharding (504), Graph database (328), Caching (267) <!-- sysd-q-064 -->

### Scale a system to millions of users on AWS

1026. **Scaling a website in stages** — Foundational · Process · Major · builds on: Horizontal and vertical scaling (451), Monolithic application (659), Load balancing (237), Microservices (660), Replication (473) <!-- sysd-q-066 -->
1027. **Virtual private cloud** — Intermediate · Concept · Minor · builds on: Public and private IP addresses (62), Subnets and CIDR notation (67), Network address translation (63) <!-- sysd-q-160 -->
1028. **Scaling a system to millions of users** — Intermediate · Worked example · Landmark · builds on: Horizontal and vertical scaling (451), Scalability bottlenecks (471), Load balancing (237), Replication (473), Caching (267), Message queue (592) <!-- sysd-q-065 -->

### Design Gmail

1029. **Simple Mail Transfer Protocol** — Intermediate · Concept · Major · builds on: Transmission Control Protocol (42), Application-layer protocols (44), Client-server model (38), Domain Name System (90) <!-- sysd-q-115 -->
1030. **Email message format** — Intermediate · Concept · Major · builds on: Simple Mail Transfer Protocol (1029) <!-- sysd-q-136 -->
1031. **MIME** — Intermediate · Concept · Major · builds on: Email message format (1030), Simple Mail Transfer Protocol (1029), Base64 (211) <!-- sysd-q-123 -->
1032. **Email spam** — Foundational · Concept · Major · builds on: Simple Mail Transfer Protocol (1029) <!-- sysd-q-128 -->
1033. **SMTP mail transaction** — Intermediate · Process · Major · builds on: Simple Mail Transfer Protocol (1029) <!-- sysd-q-130 -->
1034. **SMTP envelope versus message header** — Intermediate · Concept · Major · builds on: Simple Mail Transfer Protocol (1029), SMTP mail transaction (1033), Email message format (1030) <!-- sysd-q-134 -->
1035. **Email header fields** — Intermediate · Classification · Major · builds on: Email message format (1030), SMTP envelope versus message header (1034) <!-- sysd-q-137 -->
1036. **SMTP queueing and retries** — Intermediate · Method · Major · builds on: Simple Mail Transfer Protocol (1029), Retry strategies (766), Exponential backoff (769) <!-- sysd-q-132 -->
1037. **Bounce messages** — Intermediate · Concept · Major · builds on: SMTP mail transaction (1033), SMTP envelope versus message header (1034), SMTP queueing and retries (1036), Simple Mail Transfer Protocol (1029) <!-- sysd-q-133 -->
1038. **Mail agents and relays** — Intermediate · Classification · Major · builds on: Simple Mail Transfer Protocol (1029), Store and forward (954), Client-server model (38) <!-- sysd-q-116 -->
1039. **MX record** — Intermediate · Concept · Major · builds on: DNS record types (99), DNS resource records (96), Simple Mail Transfer Protocol (1029), Mail agents and relays (1038), CNAME records and aliases (101), Domain Name System (90) <!-- sysd-q-126 -->
1040. **Post Office Protocol** — Intermediate · Concept · Major · builds on: Simple Mail Transfer Protocol (1029), Mail agents and relays (1038), Transmission Control Protocol (42) <!-- sysd-q-120 -->
1041. **Email delivery** — Intermediate · Process · Major · builds on: Simple Mail Transfer Protocol (1029), Mail agents and relays (1038), MX record (1039), SMTP envelope versus message header (1034), Domain Name System (90) <!-- sysd-q-122 -->
1042. **Internet Message Access Protocol** — Intermediate · Concept · Major · builds on: Simple Mail Transfer Protocol (1029), Mail agents and relays (1038), Transmission Control Protocol (42) <!-- sysd-q-119 -->
1043. **POP versus IMAP** — Intermediate · Concept · Major · builds on: Post Office Protocol (1040), Internet Message Access Protocol (1042) <!-- sysd-q-121 -->
1044. **IMAP commands and responses** — Intermediate · Concept · Major · builds on: Internet Message Access Protocol (1042), Transmission Control Protocol (42) <!-- sysd-q-143 -->
1045. **IMAP unique identifiers** — Advanced · Concept · Major · builds on: Internet Message Access Protocol (1042), IMAP commands and responses (1044) <!-- sysd-q-140 -->
1046. **Email spoofing** — Intermediate · Concept · Minor · builds on: SMTP envelope versus message header (1034), Email header fields (1035), Simple Mail Transfer Protocol (1029) <!-- sysd-q-125 -->
1047. **SMTP security** — Advanced · Concept · Major · builds on: Simple Mail Transfer Protocol (1029), Authentication (898), Transport Layer Security (181), Email spoofing (1046), DNS record types (99), Domain Name System (90) <!-- sysd-q-118 -->
1048. **Spam filtering** — Intermediate · Classification · Major · builds on: Email spam (1032), Email spoofing (1046), SMTP queueing and retries (1036), Domain Name System (90) <!-- sysd-q-129 -->
1049. **Designing Gmail** — Intermediate · Worked example · Landmark · builds on: Simple Mail Transfer Protocol (1029), Email delivery (1041), MX record (1039), Internet Message Access Protocol (1042), Spam filtering (1048), Domain Name System (90) <!-- sysd-q-058 -->

### Design Google Maps

1050. **Dijkstra's algorithm** — Intermediate · Concept · Major · builds on: Shortest path problem (1022), Heap (1012) <!-- sysd-q-148 -->
1051. **A* search algorithm** — Intermediate · Concept · Major · builds on: Dijkstra's algorithm (1050), Shortest path problem (1022), Heap (1012) <!-- sysd-q-149 -->
1052. **Geocoding** — Intermediate · Concept · Major · builds on: Geohash (219) <!-- sysd-q-152 -->
1053. **Contraction hierarchies** — Advanced · Method · Major · builds on: Dijkstra's algorithm (1050), Shortest path problem (1022) <!-- sysd-q-150 -->
1054. **Map tiles** — Intermediate · Concept · Major · builds on: Content delivery network (306), Object storage (427) <!-- sysd-q-061 -->
1055. **Web Mercator projection** — Intermediate · Concept · Minor · builds on: Map tiles (1054) <!-- sysd-q-151 -->
1056. **Designing Google Maps** — Intermediate · Worked example · Landmark · builds on: Map tiles (1054), Geocoding (1052), Dijkstra's algorithm (1050), A* search algorithm (1051), Contraction hierarchies (1053), Content delivery network (306), Object storage (427) <!-- sysd-q-060 -->

### Design a stock exchange

1057. **Non-blocking algorithm** — Advanced · Concept · Major · builds on: Pessimistic and optimistic locking (401), Concurrency control (361) <!-- sysd-q-100 -->
1058. **Order types** — Intermediate · Classification · Major <!-- sysd-q-095 -->
1059. **FIX protocol** — Intermediate · Concept · Major · builds on: Transmission Control Protocol (42), Application-layer protocols (44), Serialization formats (695), User Datagram Protocol (47) <!-- sysd-q-098 -->
1060. **Order book** — Intermediate · Concept · Major · builds on: Order types (1058) <!-- sysd-q-094 -->
1061. **Market data** — Intermediate · Concept · Major · builds on: Order book (1060), Publish–subscribe pattern (614), User Datagram Protocol (47) <!-- sysd-q-097 -->
1062. **Matching engine** — Intermediate · Concept · Major · builds on: Order book (1060), Order types (1058) <!-- sysd-q-096 -->
1063. **Processor affinity** — Intermediate · Concept · Minor · builds on: CPU cache (269) <!-- sysd-q-099 -->
1064. **Low-latency critical path design** — Intermediate · Practice · Minor · builds on: Latency (19), Reducing latency (26), Processor affinity (1063), Non-blocking algorithm (1057) <!-- sysd-q-028 -->
1065. **Designing a stock exchange** — Advanced · Worked example · Landmark · builds on: Order book (1060), Matching engine (1062), Low-latency critical path design (1064), Market data (1061), FIX protocol (1059), Latency (19), Event-driven architecture (638) <!-- sysd-q-027 -->

### Design Google Docs

1066. **Collaborative real-time editing** — Intermediate · Concept · Major · builds on: Replication (473), Replication conflict resolution (481), Network latency (21), Pessimistic and optimistic locking (401), WebSocket (717) <!-- sysd-q-146 -->
1067. **Groupware concurrency control** — Advanced · Concept · Minor · builds on: Concurrency control (361), Pessimistic and optimistic locking (401), Collaborative real-time editing (1066) <!-- sysd-q-147 -->
1068. **Operational transformation** — Advanced · Concept · Major · builds on: Collaborative real-time editing (1066), Groupware concurrency control (1067), Replication (473), Happened-before relation (539), Replication conflict resolution (481), Lamport timestamp (537) <!-- sysd-q-145 -->
1069. **Designing Google Docs** — Intermediate · Worked example · Landmark · builds on: Operational transformation (1068), Collaborative real-time editing (1066), Conflict-free replicated data type (482), WebSocket (717), Message queue (592), Replication conflict resolution (481) <!-- sysd-q-059 -->

### Design a payment system

1070. **Double-entry bookkeeping** — Intermediate · Concept · Major <!-- sysd-q-077 -->
1071. **Payment settlement systems** — Intermediate · Concept · Minor <!-- sysd-q-081 -->
1072. **Payment service provider** — Intermediate · Concept · Major · builds on: Payment settlement systems (1071) <!-- sysd-q-078 -->
1073. **Payment gateway** — Intermediate · Concept · Major · builds on: Payment service provider (1072), Payment settlement systems (1071) <!-- sysd-q-079 -->
1074. **Card payment authorization and settlement** — Intermediate · Process · Major · builds on: Payment gateway (1073), Payment service provider (1072), Payment settlement systems (1071) <!-- sysd-q-080 -->
1075. **Payment reconciliation** — Intermediate · Process · Major · builds on: Double-entry bookkeeping (1070), Payment settlement systems (1071), Card payment authorization and settlement (1074), Batch processing (626), Stream processing (627), Exactly-once execution (771) <!-- sysd-q-008 -->
1076. **Designing a payment system** — Advanced · Worked example · Landmark · builds on: Exactly-once execution (771), Idempotency keys (772), Double-entry bookkeeping (1070), Payment service provider (1072), Payment reconciliation (1075) <!-- sysd-q-007 -->

### Design a notification system

1077. **Short Message Service** — Intermediate · Concept · Major · builds on: Push notification (714) <!-- sysd-q-076 -->
1078. **Firebase Cloud Messaging** — Intermediate · Concept · Major · builds on: Push notification (714), Store and forward (954), Message queue (592) <!-- sysd-q-074 -->
1079. **Apple Push Notification service** — Intermediate · Concept · Minor · builds on: Push notification (714), HTTP/2 (158), Polling (711) <!-- sysd-q-075 -->
1080. **Designing a notification system** — Intermediate · Worked example · Landmark · builds on: Notification system architecture (722), Web push (715), Firebase Cloud Messaging (1078), Apple Push Notification service (1079), Message queue (592), Push notification (714) <!-- sysd-q-006 -->

### Design a permission system

1081. **Access control list** — Foundational · Concept · Major · builds on: Authorization (902) <!-- sysd-q-010 -->
1082. **Role-based access control** — Intermediate · Concept · Major · builds on: Authorization (902), Access control list (1081), Access control models (909) <!-- sysd-q-014 -->
1083. **Discretionary access control** — Intermediate · Concept · Major · builds on: Authorization (902), Access control list (1081) <!-- sysd-q-011 -->
1084. **Attribute-based access control** — Intermediate · Concept · Major · builds on: Authorization (902), Role-based access control (1082), Access control models (909) <!-- sysd-q-013 -->
1085. **Policy decision and enforcement points** — Intermediate · Concept · Major · builds on: Authorization (902), Access control models (909) <!-- sysd-q-085 -->
1086. **XACML** — Intermediate · Concept · Major · builds on: Attribute-based access control (1084), Policy decision and enforcement points (1085), Role-based access control (1082) <!-- sysd-q-082 -->
1087. **AAA authorization framework** — Advanced · Concept · Minor · builds on: Authorization (902), Authentication (898), Policy decision and enforcement points (1085), Kerberos (939) <!-- sysd-q-086 -->
1088. **Mandatory access control** — Intermediate · Concept · Minor · builds on: Authorization (902), Discretionary access control (1083) <!-- sysd-q-012 -->
1089. **Relationship-based access control** — Intermediate · Concept · Minor · builds on: Role-based access control (1082), Attribute-based access control (1084), Access control models (909) <!-- sysd-q-083 -->
1090. **Separation of duties** — Intermediate · Concept · Minor · builds on: Role-based access control (1082), Principle of least privilege (904) <!-- sysd-q-084 -->
1091. **Designing a permission system** — Intermediate · Worked example · Landmark · builds on: Access control list (1081), Role-based access control (1082), Attribute-based access control (1084), Relationship-based access control (1089), Policy decision and enforcement points (1085), Authorization (902) <!-- sysd-q-009 -->
