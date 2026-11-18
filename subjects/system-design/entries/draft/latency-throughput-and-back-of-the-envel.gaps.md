# latency-throughput-and-back-of-the-envel: gaps (pass b1)

Expected but no (or thin) sentences:
- Back-of-the-envelope calculation (Wikipedia) and the primer's "Latency numbers every programmer should know" (the primer solutions only link to it, no numbers): estimation numbers come from the primer conversion guide and one Pastebin example only
- A powers-of-two / data size table with per-item sizes (characters, images, video) for storage estimates
- Percentile (p50, p95, p99) and Service level objective (Wikipedia): tail latency cites only the Latency page
- Little's law; Queries per second / requests per second as a unit; Utilization / headroom and peak-to-average traffic
- Throughput (general, requests per second at a server): only network throughput is crawled
- Fiber, memory, disk and datacenter round-trip latency figures beyond the ByteByteGo list

Thin: "Reducing latency" (ByteByteGo guide names five strategies and explains none; facts borrowed from the CDN and cache pages).

Skipped on purpose:
- Latency (engineering): gaming, audio, video, capital markets, simulation and workflow (air travel) examples; used only the air-travel point that latency is independent of throughput
- Network throughput: analog limitations (Shannon-Hartley), IETF standardized metrics (RFC 5136, 3148, 6349), integrated circuits, wireless spectral efficiency
- Bandwidth (computing): Edholm's law and MOSFET history (trivia), multimedia compression (DCT)
- Orders of magnitude (data): the long list of historical device capacities, entropy section
- ByteByteGo trade-off guides: read-through vs write-through cache pair left to the caching chapter

# latency-throughput-and-back-of-the-envel: gaps (gap-fill gf01, chunk 03)

Still missing: the primer's "Latency numbers every programmer should know" figures; a data-size table with per-item sizes for storage estimates; requests per second as a unit; utilization/headroom and peak-to-average traffic; Throughput (general, per server).

Skipped on purpose:
- Back-of-the-envelope calculation: history (Fermi, Wilkins radar, Weisskopf) and the napkin-design examples (BGP, UTF-8, Laffer curve, Bailey bridge)
- Percentile: normal-distribution table, finance/medicine/road-speed uses, the CDF and linear-interpolation formulas, weighted percentile
- Little's law: proof history, demography application, distributional form
- Round-trip delay: TCP RTT smoothing formula and Jacobson/Karels, Wi-Fi positioning (mentions only)
