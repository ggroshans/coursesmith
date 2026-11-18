# design-a-permission-system gaps (b28)
- Chapter is thin: one guide listing five models with pros and cons; no requirements, scale, data model, API or advice on choosing a model.
- Wikipedia "Access-control list", "Discretionary access control", "Mandatory access control", "Attribute-based access control", "Role-based access control": not crawled.
- Policy engine / policy decision point (XACML, OPA) and where the check runs in a service: no sentences here.
- Relationship-based access control and Google Zanzibar: no sentences.
- Caching permission checks, permission inheritance and groups, audit logging: no sentences.

# design-a-permission-system gaps (gf26)
- Worked example still thin: no sentences on scale, requirements, a table-level schema, a REST API, caching of permission checks, permission inheritance across resources or audit logging.
- Google Zanzibar and relationship-based access control at scale: no crawled page beyond the RBAC section on ReBAC (Wikipedia "Relationship-based access control" or the Zanzibar paper).
- Open Policy Agent / Rego as a policy engine: only a few sentences inside the XACML page (Wikipedia "Open Policy Agent" or doc>www.openpolicyagent.org).
- Capability-based security and Principle of least privilege: mentioned only; Wikipedia "Capability-based security", "Principle of least privilege".
- Kubernetes RBAC objects (Role, RoleBinding): kubernetes.io docs page "Using RBAC Authorization" would fill a concrete data model.
