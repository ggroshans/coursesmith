# real-time-communication gaps (pass b19)

Expected concepts with no or too little source text in the dossier (suggested page or source):
- Polling (computer science) (Wikipedia; not crawled, so Polling cites the ByteByteGo guide)
- Comet (programming) (Wikipedia; long polling and streaming predecessors of WebSocket)
- Webhook (Wikipedia; signature verification, retries, idempotent receivers)
- Scaling WebSocket and SSE servers: connection routing, sticky sessions, fan-out through publish-subscribe, the C10k problem (Wikipedia "C10k problem", "Publish-subscribe pattern")
- SSE reconnection and Last-Event-ID (doc>html.spec.whatwg.org server-sent events section)
- Web Push protocol and Push API (rfc>8030, rfc>8291; Mozilla or W3C Push API docs)
- Apple Push Notification service and Firebase Cloud Messaging delivery (official docs)
- MQTT and XMPP as push or messaging protocols over persistent connections (Wikipedia "MQTT", "XMPP")
- WebSockets over HTTP/2 and HTTP/3 (rfc>8441, rfc>9220; only one sentence each in Wikipedia)
- Heartbeats, presence and typing indicators in chat systems (no source sentence)
- WebTransport and gRPC streaming as alternatives (other chapter or new source)

Dossier content deliberately not drafted: Flash XML Socket relays, Reliable Group Data Delivery (replication, not real-time
delivery), PointCast/CDF/BlackBerry history, browser and server support tables, Cable Haunt, hixie draft history, RFC 6455
sections 6 (send/receive algorithms), 11 (IANA registries) and 12 (use by other specifications), and the one-line Singh
design mentions of WebSockets/SSE (cited inside the SSE entry).
Note: the push-notification system guide is also adjacent to the question chapter "Design a notification system"; here it is a
Concept/Process entry only (Notification system architecture), not a Worked example.
