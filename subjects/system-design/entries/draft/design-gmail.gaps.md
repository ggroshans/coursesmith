# design-gmail gaps
- THIN worked example: no requirements, scale estimates, mailbox storage or data model, search, spam filtering, attachments, API or scaling discussion in any crawled source
- Suggested pages: Simple Mail Transfer Protocol, Internet Message Access Protocol, Post Office Protocol, Email (Wikipedia); rfc>5321 (SMTP); MX record
- Email search / inverted index over mailboxes; spam filtering; message threading: no source

# design-gmail gap-fill gaps (batch gf24)
- STILL THIN worked example "Designing Gmail": no source gives Gmail's scale or traffic estimates, mailbox storage layout (how a provider stores billions of mailboxes), search index design, or a client/API design (JMAP). Suggested: rfc>8620 (JMAP core), rfc>8621 (JMAP for Mail), Inverted index (Wikipedia), Bigtable paper abstract.
- Spam and authentication concepts the entries lean on but no page covers: Sender Policy Framework, DomainKeys Identified Mail, DMARC, Greylisting, DNSBL, Bayesian spam filtering (Wikipedia titles); rfc>7208 (SPF), rfc>6376 (DKIM), rfc>7489 (DMARC).
- MIME as its own page: Multipurpose Internet Mail Extensions; rfc>2045 (MIME part one); Base64 is crawled under another chapter.
- Mail submission and storage: rfc>6409 (message submission), rfc>8314 (TLS for submission and access), Local Mail Transfer Protocol, Maildir, Mbox, Webmail.
- No entry for the SMTP size limits or VRFY/EXPN (RFC 5321 4.5.3, 3.5): low interview value; the numbers are cited in the worked example only.
