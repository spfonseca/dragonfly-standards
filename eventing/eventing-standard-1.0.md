---
shortName: EVENT
description: >-
  How services publish and consume events: the envelope, type versioning, what a subscriber may
  assume about delivery and ordering, what it does with a message it cannot process, and the
  transactional outbox and inbox that keep a database write and a message together.
adoptionMetrics:
  - Share of services publishing alongside a database write that use a transactional outbox
  - Share of consumers with non-idempotent side effects that record consumed message identities
impactMetrics:
  - Incidents of lost or duplicated events caused by a crash between a write and its message
tags: [eventing, messaging, transactional-outbox, inbox, deduplication]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, IMPLEMENTATION]
solutionScope: [APIS_AND_INTEGRATIONS, DATA_AND_PERSISTENCE, SOFTWARE_ARCHITECTURE]
architectureQualities: [RELIABILITY, INTEROPERABILITY, RECOVERABILITY]
---
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

## Value Proposition

- **Database writes and events stay together** — a transactional outbox closes the crash window in
  which a state change commits but the event announcing it is lost.
- **Redelivery does not repeat side effects** — an inbox records what a consumer has already
  processed, so a redelivered message is recognised rather than applied twice.
- **One contract between publishers and subscribers** — services agree on what an event is, how it
  travels and what a subscriber may assume about it, instead of each pair negotiating its own.

## Scope

Applies to any service that publishes a fact other services react to, or subscribes to one.

It does not govern what a subscriber then does with the message. Work started by an event is
executed under the Backend Job Design Standard, which is chosen on how that work decomposes rather
than on how it arrived.

## Status

**This is a holding place, not a finished standard.** The platform's own eventing infrastructure —
the transport, the facade, topic provisioning and dead-letter policy — is specified separately in
the core platform's eventing requirements. This standard is what a service owes that
infrastructure, and is written after it settles.

Its two guidelines were moved verbatim from the Backend Job Design Standard (BJOBS v1.0 §7.2 and
§7.3), where they had been written as job requirements although neither is specific to a job: the
first binds any service that publishes a message alongside a database write, the second any service
that consumes one. They are renumbered here; the envelope, type versioning, delivery and ordering
assumptions and further additions are later work.

## 1. Publishing

### 1.1 Use a transactional outbox when database state and message publication form one logical outcome.

[REQUIRED] When correctness requires a local database change and
publication of a message or event to either both occur eventually or
neither be lost, the job shall use a transactional outbox or an
equivalent atomic persistence mechanism. *Rationale:* Writing the
database and publishing separately creates a crash window in which one
succeeds and the other is permanently lost.

## 2. Consuming

### 2.1 Use inbox or deduplication controls when message side effects are not naturally idempotent.

[RECOMMENDED] A message consumer whose side effects cannot be made
naturally idempotent should record consumed message or operation
identities transactionally with those side effects. *Rationale:* An
inbox closes the redelivery window between committing business state and
acknowledging the message.
