# design-a-url-shortener gaps (b25)
- Unique ID generator / Key generation service (counter ranges, KGS): owned by algorithms-behind-the-systems; Worked example covers the URL-shortener use only.
- Base62 / Base64 encoding: no crawled page (suggest Wikipedia "Base62" or "Base64").
- Hash collisions / MD5: Wikipedia "Hash collision", "MD5" not in this dossier.
- Source inconsistency: Singh's KGS storage estimate gives 300 GB in prose and ~390 GB in the formula (sents 77c6363ffeed, 1eb3de12ed3a); left out of the Worked example.
- Cut for the 16-fact cap: private URLs and HTTP 401 security, API gateway (sents 643f918e54ca, dde009a031b3, 5ad747c47dcf, fb55dbdf8c56), per-URL analytics metadata (6ead351b6f53).
