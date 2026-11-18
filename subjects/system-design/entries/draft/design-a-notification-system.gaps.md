# design-a-notification-system gaps (b28)
- Chapter is thin: one guide covering only push through Firebase Cloud Messaging; no requirements, scale, data model or API.
- Other channels (SMS, email) and third-party providers; Apple Push Notification service (APNs): no page crawled.
- Notification service design: queueing per channel, retries, deduplication, rate limiting, templates, user preferences and opt-out: no sentences (the typical push-notification guide is owned by real-time-communication).
- Firebase Cloud Messaging as its own page: no Wikipedia article crawled; Wikipedia "Firebase".

# gaps (design-a-notification-system, gap-fill chunk 02)
- Email as a notification channel (SMTP, deliverability, bounces): no page crawled; suggest Wikipedia "Email" and "Bounce message"
- Notification gateway, templates, channel preferences, routers, tracking: only in the real-time-communication guide (entry Notification system architecture); not cited here because it is not a source of this chapter
- Deduplication, rate limiting per user, opt-out and preferences, retries on the sender side, scale estimates: no source sentences; Worked example stays thin
- Web Push protocol (RFC 8030) is a seed of real-time-communication chunk 06, whose pass should draft the protocol entries; here its sentences are cited only in the Worked example
- Firebase page: company history and funding skipped; only the Cloud Messaging lineage was used
- Short Message Service page: history, premium-rate and silent-SMS sections skipped
