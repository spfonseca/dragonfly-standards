# Dragonfly Engineering Standards

The single index of the organization's engineering standards. Every repo that builds against a
standard references it from here — one source of truth, no drifting copies.

**Status vocabulary.** `Published` is the approved, active version — the one to build against.
`Draft` is not approved and must not be built against. `Retired` is superseded and kept only for
reference. Exactly one version of a standard is Published at a time, and a guideline moves into
the Published version when it is agreed *and* being built. Each standard repeats its own status
in its header table; this index and that header must agree.

| Standard | Covers | Status |
|---|---|---|
| [RESTful API Design Standard for Enterprise Reuse v1.0](rest-api-design/RESTful-API-Design-Standard-v1.0.md) | Design and governance of reusable enterprise REST APIs — products, DDD boundaries, architecture, resilience, versioning, resources, URLs, verbs, headers, parameters, status codes, security, async operations, collections, data formats, caching, expansion, links, events, documentation, observability. | Published |
| [RESTful API Design Standard v1.1 (draft)](rest-api-design/RESTful-API-Design-Standard-v1.1.md) | Working draft of the above — holds guidelines still under elaboration (the shared batch idiom §14.7; server-assigned tenancy/ownership §13.7 with owning-org and creator provenance metadata §7.9). Do not build against: a guideline moves down into v1.0 when it is agreed *and* being built, so v1.1 holds only what is agreed for later. | Draft |
| [Relational DB Design Standard](relational-db-design/relational-db-design-standard.md) | Physical schema and database-runtime conventions — naming, keys, typing, common columns, normalization, integrity, indexing, API alignment, resilience, observability, security, backup and recovery, schema migration. | Draft |
| [Web Asset Delivery Standard](web-asset-delivery/web-asset-delivery-standard.md) | Caching and edge routing of static web assets — per-content-class cache lifetimes, origin-header-driven CDN behavior, SPA deep-link routing, and post-deploy verification. Covers static delivery; API response caching is the RESTful API Design Standard §17. | Draft |
