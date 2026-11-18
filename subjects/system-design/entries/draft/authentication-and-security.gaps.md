# authentication-and-security gaps (pass b23)

Concepts expected in this chapter with no (or too few) sentences in the dossier; suggested page or source:
- Role-based access control; Attribute-based access control; Access control list (Wikipedia; only one sentence each on the Authorization page)
- Security Assertion Markup Language (Wikipedia; SAML has only Singh's 3 sentences and a 7-sentence section of Single sign-on)
- Multi-factor authentication (Wikipedia page; covered only by the Authentication page's subsection)
- Salt (cryptography); Rainbow table; bcrypt / Argon2 password hashing (Wikipedia; the ByteByteGo password guide stops at salted hashes)
- HTTP cookie; Session ID / session management (Wikipedia; cookie-based sessions are only described in one ByteByteGo guide)
- Refresh token; OAuth 2.0 grant types (authorization code, client credentials, PKCE: RFC 6749, RFC 7636); the Wikipedia OAuth Types section lists only ROPC
- WebAuthn / FIDO2 (named in the API-security tips, no explanation)
- API keys and "leveled" API keys; OWASP API Security Top 10; input validation (the API-security guide is a bare list of 12 tips)
- Kerberos (only the SSO page's configuration bullets); Principle of least privilege (one sentence)
- Encryption in transit and at rest, TLS/HTTPS, public key certificate (the secure-design cheat sheet only names "Encryption")
- Cross-site scripting, CSRF, Zero trust architecture (mentioned only in passing)

Sources with no or thin entries:
- how-do-we-design-a-secure-system.md: a cheat sheet; its sentences only name 12 design points. One thin Minor entry ("Secure system design checklist") lists them; the content is in a diagram.
- top-12-tips-for-api-security.md: a bare list of tips. One thin Minor entry ("API security practices"); no tip is explained.
- Wikipedia Authentication: art, antiques, commercial products, packaging and literature sections are about authenticating objects, not computing; not drafted.
- Wikipedia OAuth History, Uses, Criticisms and resignations; OpenID Foundation, adoption, history and legal sections; JSON Web Token implementations list: company and people history or product lists; not drafted. The Gmail phishing incident (2017) and the 2012/2020 social-login and breach incidents are not drafted.

# gaps (gf18, authentication-and-security chunks 04-08)
- Secure system design checklist stays thin: no source explains audit and compliance, emergency responses, third-party vendor management, disaster recovery, terminal security, container security or encryption at rest (OWASP Cheat Sheet Series, NIST Cybersecurity Framework).
- API security practices stays thin: leveled API keys, whitelisting, API gateway use, error handling, API versioning and the OWASP API Security Top 10 have no explanatory page (OWASP API Security Top 10).
- Public-key cryptography and Hash function are cited as prerequisites (WebAuthn, Cryptographic salt, Rainbow table) and have no entry here.
- HTTP cookie / session management (Wikipedia "HTTP cookie") still has no entry in this chapter; XSS and CSRF defenses lean on cookie flags.
- PBKDF2 and scrypt as password hashing functions (Wikipedia "PBKDF2", "Scrypt"); key stretching has no page of its own.
- Content Security Policy (Wikipedia) for XSS defense; Same-origin policy (Wikipedia) for the XSS and CSRF background.
- Attribute-based access control is cited by Zero trust security model; it exists as an entry in design-a-permission-system.
- bcrypt vs Argon2: the bcrypt article argues bcrypt is stronger for run times under about one second; not stated as fact because the Argon2 side (RFC 9106) was not crawled.

# gaps (gf19, authentication-and-security chunk 09)
- Secure system design checklist and API security practices stay thin: neither RFC explains the checklist or the API tips; a source such as the OWASP API Security Top 10 or Cheat Sheet Series would be needed.
- JSON Web Signature / JSON Web Encryption (RFC 7515, RFC 7516) for how a JWS signature and a JWE are built; RFC 7519 only points to them.
- Public-key cryptography and Hash function are cited by these entries as prerequisites and have no entry here.
