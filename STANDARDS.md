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
| [RESTful API Design Standard v1.1 (draft)](rest-api-design/RESTful-API-Design-Standard-v1.1.md) | Working draft of the above — holds guidelines still under elaboration (the shared batch idiom §14.7). Do not build against: compliance is measured against v1.0 alone. A guideline is authored into both versions and stays in both — v1.1 is v1.0 plus what is agreed for later, not a separate set. | Draft |
| [Relational DB Design Standard](relational-db-design/relational-db-design-standard.md) | Physical schema and database-runtime conventions — naming, keys, typing, common columns, normalization, integrity, indexing, API alignment, resilience, observability, security, backup and recovery, schema migration. | Draft |
| [Web Asset Delivery Standard](web-asset-delivery/web-asset-delivery-standard.md) | Caching and edge routing of static web assets — per-content-class cache lifetimes, origin-header-driven CDN behavior, SPA deep-link routing, and post-deploy verification. Covers static delivery; API response caching is the RESTful API Design Standard §17. | Draft |
| [API Client Design Standard](api-client/api-client-design-standard-1.0.md) | How software calls HTTP APIs it does not own — client architecture, request construction, validating every response against a schema the caller owns, versions and change, connections, timeouts and deadlines, the client error model, retries and backoff, idempotency and ambiguous outcomes, rate limits and backpressure, circuit breaking and failure isolation, credentials, tracing, pagination, caching, optimistic concurrency, redirects, security and data sent, cancellation, configuration, observability, logging and testing. | Draft |
| [Authorization Tuple Management Standard](authorization-tuple-management/authorization-tuple-management-standard.md) | Writing, revoking and reconciling authorization tuples in a relationship-based authorization store — write-path transactionality, revocation synchrony, drift reconciliation, read consistency, failure posture, and backfill. Covers the write path; the relation model itself belongs to the platform's authorization design. | Draft |
| [Authorization Design Standard](authorization-design/authorization-design-standard.md) | How access is designed — scopes sized to experiences, facts on subjects, people and machine accounts as one kind of subject, tenancy from the token, deny by default, where checks run, platform-level facts, and the split between the platform-owned model and the shared mechanism. Skeleton. | Draft |
| [FMEA Rating Rubric Standard](fmea-rating-rubric/fmea-rating-rubric-standard.md) | The rubric a failure modes and effects analysis is rated under — the ten-point anchor tables for severity, occurrence and detection, served whole as one resource; severity dominating in place of a risk priority number, which is neither computed nor stored; re-rating after actions taken; what an experience shows beside a rating. Specific to FMEA. | Draft |
| [Backend Job Design Standard v1.0](backend-jobs/backend-jobs-standard-1.0.md) | How work that runs outside the request-response path is designed — the four approved execution patterns and when each is chosen, execution and work-item identity, state and lifecycle, idempotency under at-least-once execution, retry and failure classification, concurrency and backpressure, reconciliation, the implementation rules particular to each pattern, cancellation and operational control, job identity and credentials, deployment and drain, and the Kubernetes workload mapping. Covers how the work executes; what triggers it is not addressed. | Published |
| [Backend Job Design Standard v1.1 (draft)](backend-jobs/backend-jobs-standard-1.1.md) | Working draft of the above — v1.0 plus Section 21, the alerts that are about a job's own outcome: a terminal failure, a scheduled run that did not happen, and a reconciled target that may be stale. Do not build against: compliance is measured against v1.0 alone. | Draft |
| [Service Resilience Standard](resilience/resilience-standard-1.0.md) | How software behaves when a dependency fails, slows or refuses it — retry backoff and jitter, which layer owns a retry boundary, honouring throttling signals, what must not be retried, circuit breaking, and compensation across systems. Skeleton. | Draft |
| [Eventing Standard](eventing/eventing-standard-1.0.md) | How services publish and consume events — the envelope, type versioning, what a subscriber may assume about delivery and ordering, what happens to a message it cannot process, and the transactional outbox and inbox that keep a database write and a message from parting company. Skeleton. | Draft |
| [Execution Triggers Standard](execution-triggers/execution-triggers-standard-1.0.md) | What causes work to begin — schedules, events, messages, API calls, data conditions and manual initiation, and what each owes about duplicate starts, missed starts and late starts. Skeleton. | Draft |
| [Observability Standard](observability/observability-standard-1.0.md) | What a workload emits and what can be asked of it afterwards — logs, metrics, traces, correlation across asynchronous boundaries, and what an alert binds to. Skeleton. | Draft |
| [Testing and Verification Standard](testing/testing-standard-1.0.md) | Which failure conditions must be exercised deliberately — duplicate delivery, termination mid-commit, retry exhaustion, downstream timeouts, concurrent races, shutdown, and resource exhaustion — rather than only the path the code was designed for. Skeleton. | Draft |
| [Compute Best Practices in Kubernetes](compute-k8s/compute-k8s-standard-1.0.md) | What any workload owes the cluster it runs on — resource requests and limits, probes, termination handling, image and manifest discipline, and workload security. Skeleton. | Draft |
| [Compliance and Data Retention Standard](compliance/compliance-standard-1.0.md) | How long data is kept, on what basis, and what happens when the period ends — classification, retention, deletion, and the record that survives it. Applies to data a system holds incidentally as much as to the records a product is built around. Skeleton. | Draft |

## Authoring format

Every standard is written so it converts, unedited, into the platform's `standards` resource:
`scripts/publish-to-content.py --check` converts them all and names every line that breaks this
format; `--project <env project>` publishes them. A standard that does not convert is not published.

**Front matter** — what the prose does not carry, as YAML between `---` lines at the top of the file:

```yaml
---
shortName: APIDS                  # five capital letters; the same in every version
description: >-                   # at most 320 characters
  One or two sentences on what the standard governs.
adoptionMetrics: [...]            # how adoption is measured; at least one
impactMetrics: [...]              # how its effect is measured; at least one
tags: [...]
softwareLifecycle: [...]          # the service's values, e.g. ARCHITECTURE_AND_DESIGN
solutionScope: [...]              # e.g. APIS_AND_INTEGRATIONS
architectureQualities: [...]      # e.g. RELIABILITY
industryReferences:               # optional
  - {title: ..., url: https://...}
supportingStandards: [APIDS-v1]   # optional; each must have a Published version here
---
```

**Header** — `# <Title>`, the same in every version, then the table with **Version**
(`<major>.<minor>`), **Status** (Published, Draft, Retired) and **Author** (first and last name).
A **Short Name** row, where present, matches the front matter.

**Unnumbered sections** — `## Purpose`, `## Value Proposition` (bullets, each
`- **Label** — text`), `## Scope` and any other reading matter, before or after the numbered
sections. `## Glossary`, where present, is one table, `| Term | Definition |`.

**Numbered sections** — `## N. Name`, numbered from 1 without gaps, each holding at least one
guideline and nothing normative outside one.

**Guidelines** — `### N.M <Directive.>`, numbered from 1 within the section without gaps. The body
opens with the level, `[REQUIRED]`, `[RECOMMENDED]` or `[OPTIONAL]`, then the normative text, then
`*Rationale:* <why>`, then any `*Example:* <example>` blocks. Each marker may start a line or follow
the text inline. A guideline may carry further statements, each `[LEVEL] text *Rationale:* why`;
the guideline's level is its first statement's.

The Status maps to the resource's state: Published loads ACTIVE, Draft loads DRAFT, Retired loads
RETIRED.
