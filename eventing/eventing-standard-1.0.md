# Eventing Standard

| Field | Value |
|---|---|
| **Short Name** | EVENT |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-27 |

## Purpose

This standard governs how services publish and consume events: what an event is, the envelope it
travels in, how a type is versioned, what a subscriber may assume about delivery and ordering, and
what it must do with a message it cannot process.

## Scope

Applies to any service that publishes a fact other services react to, or subscribes to one.

It does not govern what a subscriber then does with the message. Work started by an event is
executed under the Backend Job Design Standard, which is chosen on how that work decomposes rather
than on how it arrived.

## Status: skeleton

**This is a holding place, not a finished standard.** The platform's own eventing infrastructure —
the transport, the facade, topic provisioning and dead-letter policy — is specified separately in
the core platform's eventing requirements. This standard is what a service owes that
infrastructure, and is written after it settles.

The two requirements below were moved verbatim from the Backend Job Design Standard, where they had
been written as job requirements although neither is specific to a job: the first binds any service
that publishes a message alongside a database write, the second any service that consumes one. They
keep the numbering they had there, which is wrong here; sections, ordering and any additions are
later work.

---

## Requirements moved from the Backend Job Design Standard

### 7.2 Use a transactional outbox when database state and message publication form one logical outcome.

[REQUIRED] When correctness requires a local database change and
publication of a message or event to either both occur eventually or
neither be lost, the job shall use a transactional outbox or an
equivalent atomic persistence mechanism. *Rationale:* Writing the
database and publishing separately creates a crash window in which one
succeeds and the other is permanently lost.

### 7.3 Use inbox or deduplication controls when message side effects are not naturally idempotent.

[RECOMMENDED] A message consumer whose side effects cannot be made
naturally idempotent should record consumed message or operation
identities transactionally with those side effects. *Rationale:* An
inbox closes the redelivery window between committing business state and
acknowledging the message.

------------------------------------------------------------------------
