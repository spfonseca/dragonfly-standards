# Authorization Tuple Management Standard

| Field | Value |
|---|---|
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

## Scope

Applies to every service that writes to a relationship-based authorization store (OpenFGA, in
practice), and to the reconciliation tooling that repairs it. Does not cover model composition, the
relation vocabulary, or how a service decides which check to make — those belong to the platform's
authorization design.

Any requirement may be waived only through an explicit, documented, approved waiver recorded in the
product's implementation guidance.

---

## 1. Authority and Direction

> Which store is authoritative, which is derived, and therefore which way repair runs.

- Whether the domain database or the tuple store is the record of truth.
- That checks are answered by the tuple store and never by the application's own tables.
- That reconciliation is one-directional, and which direction.
- Whether a tuple with no corresponding domain state is deleted or reported.

## 2. Write Path

> How a tuple write is bound to the domain write it accompanies.

- The transactional guarantee required between a domain write and its tuple write.
- Whether tuple writes may be issued inline in a request.
- Idempotency requirements, including the delete-of-a-missing-tuple case.
- What the API answers when the domain write commits and the tuple write does not.

## 3. Revocation

> The asymmetry: a lost grant is an inconvenience, a lost revocation is an incident.

- Whether revocations may be eventual, and the requirement if they may not.
- What the API answers when a revocation cannot be completed.
- Ordering requirements when a single operation both grants and revokes.
- Handling of cascading revocation (deleting a subject that appears in many tuples).

## 4. Reconciliation

> The audit that catches what the write path never knew about.

- What must be reconciled, how often, and by what.
- Whether drift is repaired automatically or reported for a human decision.
- What a reconciliation run must record.
- The requirement that persistent drift is treated as a defect in a write path.

## 5. Read Consistency

> Replication lag is exactly the window in which a revoked subject still passes.

- When a stronger consistency setting is required on a check.
- The default for ordinary checks.
- Requirements on caching a check result.

## 6. Availability and Failure Posture

> What happens when the authorization store cannot be reached.

- Fail-closed requirements.
- Whether any operation may proceed without an authorization answer.
- What must be logged, and what must not be (tuple contents are access data).

## 7. Observability

> A tuple store fails quietly; this is what makes it audible.

- Required signals: write failures, outbox depth or lag, drift per reconciliation run.
- What must be alertable.
- Audit-trail requirements for grants and revocations.

## 8. Migration and Backfill

> Tuples for state that predates tuple writing, and for restores.

- Requirements on a backfill: determinism, idempotency, and what it may infer.
- The rule against inferring a grant from a coincidence of current state.
- Requirements after a database restore.

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
