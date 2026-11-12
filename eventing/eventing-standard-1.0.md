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
| **Last Updated** | 2026-11-12 |

## Purpose

This standard governs how services publish and consume events: what an event is, the envelope it
travels in, how a type is versioned, what a subscriber may assume about delivery and ordering, and
what it must do with a message it cannot process.

## Value Proposition

- **Database writes and events stay together** — a transactional outbox closes the crash window in
  which a state change commits but the event announcing it is lost.
- **Redelivery does not repeat side effects** — an inbox records what a consumer has already
  processed, so a redelivered message is recognised rather than applied twice.
- **One topic per service domain** — a subscriber finds any event type's topic from the type's name,
  and approval to receive a domain's events is one decision.
- **One contract between publishers and subscribers** — services agree on what an event is, how it
  travels and what a subscriber may assume about it, instead of each pair negotiating its own.

## Scope

Applies to any service that publishes a fact other services react to, or subscribes to one.

It does not govern what a subscriber then does with the message. Work started by an event is
executed under the Backend Job Design Standard, which is chosen on how that work decomposes rather
than on how it arrived.

## Status

This standard holds the rules the platform's eventing has settled, and gains a rule as each one
settles. Sections 1.1 and 2.1 were moved verbatim from the Backend Job Design Standard (BJOBS v1.0
§7.2 and §7.3). The rest were settled while the platform's event transport was built, in 2026-10
and 2026-11.

## 1. Publishing

### 1.1 Use a transactional outbox when database state and message publication form one logical outcome.

[REQUIRED] When correctness requires a local database change and
publication of a message or event to either both occur eventually or
neither be lost, the backend job shall use a transactional outbox or an
equivalent atomic persistence mechanism. *Rationale:* Writing the
database and publishing separately creates a crash window in which one
succeeds and the other is permanently lost.

### 1.2 Publish through the platform's event facade, as the service's own machine account.

[REQUIRED] A service shall publish an event by calling the platform's event facade
(`POST /v1/events`) with its own machine account's token, and shall never connect to the event
transport to publish. *Rationale:* The facade validates each event against its type's contract,
checks the caller is one of the type's publishers and records the event before it reaches the
transport, so every event on the bus is valid, attributable and archived.

### 1.3 Leave the event's organization to the platform.

[REQUIRED] A publisher shall not supply the organization an event belongs to. The facade sets it
from the publisher's machine account, which belongs to exactly one organization. A payload field
that names an organization describes the fact; it never decides which organization the event
belongs to. *Rationale:* A subscriber trusts an event's organization only because no publisher can
choose it.


## 2. Consuming

### 2.1 Use inbox or deduplication controls when message side effects are not naturally idempotent.

[RECOMMENDED] A message consumer whose side effects cannot be made
naturally idempotent should record consumed message or operation
identities transactionally with those side effects. *Rationale:* An
inbox closes the redelivery window between committing business state and
acknowledging the message.

### 2.2 Expect every event at least once, and recognise a repeat by its `eventId`.

[REQUIRED] A subscriber shall treat each event as possibly delivered more than once, and shall
recognise a repeat by the event's `eventId`. *Rationale:* The transport redelivers any event whose
acknowledgement it did not receive, and a publisher's outbox may place one event twice.

### 2.3 Expect events in any order, and discard a record's out-of-date change.

[REQUIRED] A subscriber that applies changes to a record shall keep the `lastUpdatedAt` of the last
change it applied for that record, and shall discard an event whose `lastUpdatedAt` is not later.
An event that reports a fact rather than a state change is applied every time it is new.
*Rationale:* Redelivery, parallel pulls, outbox retries and several publishing pods each reorder
events; the record's own `lastUpdatedAt`, written by one database, is the one order that holds.

### 2.4 Act within each event's organization.

[REQUIRED] A subscriber shall carry out the work an event causes within the organization the event
belongs to, and shall read and write that organization's records only. *Rationale:* Every
organization's events travel on the same topics, so the event's organization is the only boundary
between tenants in a subscriber's work.

### 2.5 Filter a subscription to the event types the subscriber handles.

[RECOMMENDED] A subscriber should set its subscription's filters to the event types it handles,
rather than receive the whole topic and discard the rest. *Rationale:* Filters are applied by the
transport without opening the event, so a subscriber neither pays for nor holds events it has no
use for.

## 3. Event types

### 3.1 Name an event type `<namespace>.<eventName>.<major>`.

[REQUIRED] An event type's `namespace` shall be the short code of the service domain that owns the
fact, and its `eventName` shall say what happened, in the past tense, as lowercase words joined by
dashes: `ident.organization-suspended.1`. *Rationale:* A subscriber reads from the name whose fact
it is and what happened, and the name is the key every publisher, subscriber and filter matches on.

### 3.2 Change a type only by adding, and make a breaking change a new major.

[REQUIRED] A new minor version of an event type shall only add to its payload schema, and shall not
remove a field from the schema's required fields. A change that a current subscriber cannot read is
a new major version, which is a new event type. *Rationale:* Events are validated against the
type's current minor, so every subscriber written against an earlier minor of the same major must
still read every event.

### 3.3 Carry the record's `lastUpdatedAt` in an event that reports a change to its state.

[REQUIRED] An event type whose events report a change to a record's state shall carry, in its
payload, the record's `lastUpdatedAt` from that change. *Rationale:* It is what lets a subscriber
discard an out-of-date change (2.3).

### 3.4 Declare the access a person needs to read about an event.

[REQUIRED] An event type whose events can reach people, as notifications or on any other screen,
shall declare `requiredAccess`: each relation a person must hold, on an object in the platform's
authorization model, to read about the event. An entry that names its object by `objectIdPath`
shall point at a field the payload schema requires. For `exp.expense-approved.1`, the entry is
`viewer` on the `expense` at `payload.expenseId`. *Rationale:* Access is checked when a person
reads, which can be long after the event; the event type is the one place that knows which record
the event is about.

## 4. Topics

### 4.1 Give each service domain one topic, named with the domain's short code.

[REQUIRED] A service domain shall have exactly one topic, named with its short code, and every
event type whose `namespace` is that short code shall flow on it: the Order Management
domain's topic is `ordmgt`, and carries `ordmgt.order-placed.1` and every other type whose
namespace is `ordmgt`. Approval to receive events is granted per topic, so approval is granted for a whole
domain's events; a subscriber's filters then select the types it handles (2.5). *Rationale:* A
subscriber finds any type's topic from the type's name alone, and the domain, which already bounds
a service's resources and ownership, is the one boundary for its events as well.

### 4.2 Serve every organization from one topic.

[REQUIRED] A topic shall carry every organization's events, and shall never be created per
organization. Each event's organization is the last token of its subject, and a subscriber
receives only the organizations its subscription is entitled to. *Rationale:* A topic per tenant
does not scale, and the transport separates tenants already.
