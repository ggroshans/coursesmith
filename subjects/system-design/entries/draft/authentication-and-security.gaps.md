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
