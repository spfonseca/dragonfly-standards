# Dragonfly Engineering Standards

The single index of the organization's engineering standards. Every repo that builds against a
standard references it from here — one source of truth, no drifting copies.

| Standard | Covers | Status |
|---|---|---|
| [RESTful API Design Standard for Enterprise Reuse v1.0](rest-api-design/RESTful-API-Design-Standard-v1.0.md) | Design and governance of reusable enterprise REST APIs — products, DDD boundaries, architecture, resilience, versioning, resources, URLs, verbs, headers, parameters, status codes, security, async operations, collections, data formats, caching, expansion, links, events, documentation, observability. | Released |
| [RESTful API Design Standard v1.1 (draft)](rest-api-design/RESTful-API-Design-Standard-v1.1.md) | Working draft of the above — holds guidelines still under elaboration (the shared batch idiom §14.7; server-assigned tenancy/ownership §13.7 with owning-org and creator provenance metadata §7.9). Do not build against. | Draft |
| [Relational DB Design Standard](relational-db-design/relational-db-design-standard.md) | Physical schema and database-runtime conventions — naming, keys, typing, common columns, normalization, integrity, indexing, API alignment, resilience, observability, security, backup and recovery, schema migration. | Draft |
