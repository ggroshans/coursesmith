# Gaps: apis-rest-graphql-and-grpc (pass b18)

- SOAP (page `SOAP` or `Simple Object Access Protocol`): the chapter title and the ByteByteGo guide soap-vs-rest-vs-graphql-vs-rpc name it, but the guide text is only a diagram caption; no sentences on its design or trade-offs.
- HATEOAS (page `HATEOAS`): only covered inside "REST uniform interface" from the REST article; no page of its own crawled.
- OpenAPI / API specification and contract-first design (page `OpenAPI Specification`).
- Protocol Buffers (page `Protocol Buffers`): drafted as a 3-fact entry from Singh and the GRPC article; a real article would fill it out.
- HTTP/2 (page `HTTP/2`) is cited by gRPC; belongs to the HTTP chapter.
- API gateway (page or Singh section on API gateway) and rate limiting at the gateway: named in the API design guide, owned by other chapters.
- Idempotency of POST and PATCH in API design (ByteByteGo tip): owned by the resilience chapter (`Idempotence`).
- N+1 problem in GraphQL (resolver/data-loader batching): only a one-line bullet in Singh; suggest a page such as `Object-relational impedance mismatch` or a GraphQL docs page.
- GraphQL query cost limiting / abusive queries: one sentence only (ByteByteGo); suggest GraphQL docs on depth and complexity limits.
- Skipped as non-concepts or business trivia: the API copyright dispute (Oracle v. Google), API history of the term, gRPC adoption and Stubby history, GraphQL conference/foundation history.

# gaps (apis-rest-graphql-and-grpc, gap-fill chunks 04-05)
- Swagger/OpenAPI history, OpenAPI Initiative, version release dates: history, skipped
- SOAP history (XML-RPC, Microsoft politics) and WS-* extensions: skipped; WSDL not in the dossier -> suggest Wikipedia "Web Services Description Language"
- Serialization: language-by-language support sections (Java, Python, Ruby, ...) are per-language detail, not drafted; pointer swizzling and differential execution only mentioned in passing
- Apache Thrift and Apache Avro as their own entries: no seed page here -> suggest "Apache Thrift", "Apache Avro"
- JSON and XML as formats: only cited inside Serialization formats -> suggest Wikipedia "JSON"
