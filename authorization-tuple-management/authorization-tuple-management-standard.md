---
shortName: AUTTM
description: >-
  How a service writes, revokes and reconciles authorization tuples in a relationship-based
  authorization store: which store is authoritative, binding a tuple write to its domain write,
  revocation, reconciliation, read consistency, failure posture, observability, and backfill.
adoptionMetrics:
  - Share of services writing tuples whose tuple writes are bound to the domain write they accompany
  - Share of authorization stores covered by a scheduled reconciliation run
impactMetrics:
  - Count of revocations found by reconciliation that the write path did not complete (target zero)
  - Count of tuples found by reconciliation with no corresponding domain state
tags: [authorization, openfga, tuples, revocation, reconciliation, consistency]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, IMPLEMENTATION, OPERATE_AND_SUPPORT]
solutionScope: [IDENTITY_AND_ACCESS, SECURITY_CONTROLS, DATA_AND_PERSISTENCE]
architectureQualities: [SECURITY, RELIABILITY, RECOVERABILITY, OBSERVABILITY]
---

# Authorization Tuple Management Standard

| Field | Value |
|---|---|
| **Short Name** | AUTTM |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-08-22 |

## Purpose

This standard governs how a service **writes, revokes and reconciles authorization tuples** in a
relationship-based authorization store, and what it must do when a tuple write fails. It covers the
write path, not the model: how a product's types and relations are shaped is a per-platform design
concern.

A relationship store is a denormalized projection of relationships the application already holds in
its own database. That duplication is inherent to the architecture, not a defect — but it means
every domain write that changes access has a second write that can fail independently, and a lost
revocation is a security failure nobody observes. This standard exists to make that failure mode
impossible to reach by accident.

## Value Proposition

- **No silent revocation loss** — a revocation that did not reach the tuple store is a security
  failure nobody observes; this standard makes that failure mode impossible to reach by accident.
- **One direction of truth** — which store is authoritative and which is derived is settled once,
  so repair always runs the same way.
- **Drift that is caught** — reconciliation audits what the write path never knew about, and
  persistent drift is traced to the write path that caused it.
- **A store that fails audibly** — write failures, lag and drift are signals, so a tuple store
  that fails quietly is still noticed.

## Scope

Applies to every service that writes to a relationship-based authorization store (OpenFGA, in
practice), and to the reconciliation tooling that repairs it. Does not cover model composition, the
relation vocabulary, or how a service decides which check to make — those belong to the platform's
authorization design.

Any requirement may be waived only through an explicit, documented, approved waiver recorded in the
product's implementation guidance.

---

## 1. Authority and Direction

### 1.1 Draft placeholder: which store is authoritative, which is derived, and therefore which way repair runs.

[OPTIONAL] To be filled before this standard leaves Draft:

- Whether the domain database or the tuple store is the record of truth.
- That checks are answered by the tuple store and never by the application's own tables.
- That reconciliation is one-directional, and which direction.
- Whether a tuple with no corresponding domain state is deleted or reported.

*Rationale:* A relationship store is a denormalized projection of relationships the application
already holds in its own database; which side is authoritative decides which way repair runs.

## 2. Write Path

### 2.1 Draft placeholder: how a tuple write is bound to the domain write it accompanies.

[OPTIONAL] To be filled before this standard leaves Draft:

- The transactional guarantee required between a domain write and its tuple write.
- Whether tuple writes may be issued inline in a request.
- Idempotency requirements, including the delete-of-a-missing-tuple case.
- What the API answers when the domain write commits and the tuple write does not.

*Rationale:* Every domain write that changes access has a second write that can fail
independently.

## 3. Revocation

### 3.1 Draft placeholder: how revocations are completed, ordered and cascaded.

[OPTIONAL] To be filled before this standard leaves Draft:

- Whether revocations may be eventual, and the requirement if they may not.
- What the API answers when a revocation cannot be completed.
- Ordering requirements when a single operation both grants and revokes.
- Handling of cascading revocation (deleting a subject that appears in many tuples).

*Rationale:* The asymmetry: a lost grant is an inconvenience, a lost revocation is an incident.

## 4. Reconciliation

### 4.1 Draft placeholder: what is reconciled, how often, by what, and what happens to drift.

[OPTIONAL] To be filled before this standard leaves Draft:

- What must be reconciled, how often, and by what.
- Whether drift is repaired automatically or reported for a human decision.
- What a reconciliation run must record.
- The requirement that persistent drift is treated as a defect in a write path.

*Rationale:* Reconciliation is the audit that catches what the write path never knew about.

## 5. Read Consistency

### 5.1 Draft placeholder: when a check requires stronger consistency, the default, and caching.

[OPTIONAL] To be filled before this standard leaves Draft:

- When a stronger consistency setting is required on a check.
- The default for ordinary checks.
- Requirements on caching a check result.

*Rationale:* Replication lag is exactly the window in which a revoked subject still passes.

## 6. Availability and Failure Posture

### 6.1 Draft placeholder: what happens when the authorization store cannot be reached.

[OPTIONAL] To be filled before this standard leaves Draft:

- Fail-closed requirements.
- Whether any operation may proceed without an authorization answer.
- What must be logged, and what must not be (tuple contents are access data).

*Rationale:* Every check depends on the authorization store, so its unavailability is an access
question, not only an outage.

## 7. Observability

### 7.1 Draft placeholder: the signals, alerts and audit trail that make the tuple store audible.

[OPTIONAL] To be filled before this standard leaves Draft:

- Required signals: write failures, outbox depth or lag, drift per reconciliation run.
- What must be alertable.
- Audit-trail requirements for grants and revocations.

*Rationale:* A tuple store fails quietly; this is what makes it audible.

## 8. Migration and Backfill

### 8.1 Draft placeholder: tuples for state that predates tuple writing, and for restores.

[OPTIONAL] To be filled before this standard leaves Draft:

- Requirements on a backfill: determinism, idempotency, and what it may infer.
- The rule against inferring a grant from a coincidence of current state.
- Requirements after a database restore.

*Rationale:* State that predates tuple writing, or that a restore brings back, has no tuple write
behind it.

---

## Open questions

To settle before this leaves Draft.

- Whether §2's transactional guarantee is stated as an outbox specifically or as an outcome any
  mechanism may satisfy.
- Whether §3's synchronous-revocation rule admits exceptions for bulk operations.
- Whether reconciliation is a per-service obligation or a platform-provided service.
- How this standard relates to the platform's authorization design document, which currently holds
  the model and some write-side rules.

## Status

- [ ] Filled out
- [ ] Reviewed
- [ ] Published
