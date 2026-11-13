---
shortName: EVENT
description: >-
  How services publish and consume events: when to publish, the type name and subject grammar,
  public and private topics, payload content, versioning, required access, the facade and outbox,
  delivery, failure and dead-lettering, and how events are logged and tested.
adoptionMetrics:
  - Share of event types whose names follow the five-token grammar
  - Share of services publishing alongside a database write that use a transactional outbox
  - Share of consumers with non-idempotent side effects that record consumed message identities
  - Share of event types whose payload schema describes every property
  - Share of subscribing services with handler tests that run without the bus
impactMetrics:
  - Incidents of lost or duplicated events caused by a crash between a write and its message
  - Incidents of an event reaching an organization not entitled to it
  - Dead-letterings left unhandled by the subscription's owner
tags: [eventing, messaging, event-types, topics, subjects, transactional-outbox, inbox, deduplication, dead-letter, payload, contract-testing]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, IMPLEMENTATION, VERIFICATION_AND_TESTING, OPERATE_AND_SUPPORT]
solutionScope: [APIS_AND_INTEGRATIONS, DATA_AND_PERSISTENCE, SOFTWARE_ARCHITECTURE]
architectureQualities: [RELIABILITY, INTEROPERABILITY, RECOVERABILITY, SECURITY, PRIVACY, OBSERVABILITY, TESTABILITY]
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

This standard governs when a service publishes an event, how it names and documents the event's
type, what the payload carries, which topic the type flows on, how a type changes over time, how an
event is published, what a subscriber may assume about the events it receives, what a subscriber
does when it cannot handle one, and how publishers and subscribers log and test their events.

## Value Proposition

- **Database writes and events stay together** — a transactional outbox closes the crash window in
  which a state change commits but the event announcing it is lost.
- **Redelivery does not repeat side effects** — an inbox records what a consumer has already
  processed, so a redelivered message is recognised rather than processed twice.
- **Two topics per service domain** — a subscriber finds any event type's topic from the type's
  name, and what customers may receive is approved apart from what only the platform may.
- **Failures reach an owner** — every event a subscriber cannot handle ends in its subscription's
  dead-letter stream, and the platform announces it, so the subscription's owner acts on it.
- **Contracts are tested before deploy** — a publisher tests its events against the type's payload
  schema and a subscriber tests its handler without the bus, so a broken contract fails a build.
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

### 1.4 Publish an event to report a fact; call an API to have something done.

[REQUIRED] A service shall publish an event to report something that has already happened to a
record it owns, for any service to react to. A service that needs another service to act, or needs
an answer, shall call that service's API. *Rationale:* An event's publisher does not know who
subscribes, so it cannot rely on any one of them acting; an API call names the service that acts
and returns its answer.

*Example:* Expense management publishes `expmgt.public.expense.approved.1` when an expense is
approved, and the payment service and the Notification Service each react to it. To learn an
employee's cost centre before approving, expense management calls the organization service's API.


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
An event that reports a fact rather than a state change is processed every time it is new.
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

### 2.6 Answer every event as handled, to be retried, or never to be handled.

[REQUIRED] A subscriber shall answer each event it receives in one of three ways. It answers
*handled* when it has done the work the event causes or deliberately skipped it. It answers *retry* when the
event can succeed later, such as when a service it calls is unavailable; the platform then
redelivers the event at the next attempt of its delivery schedule. The schedule is a fixed number
of attempts at set times after the first delivery, and after the last attempt the event is
dead-lettered (2.7). It answers *never* when the event can never succeed, such as when its body
cannot be read; the platform then delivers it no more. An unexpected error in the handler counts as
*retry*, and so does an event the subscriber has not answered within 30 seconds. *Rationale:* Each
answer tells the platform whether to deliver the event again, so a subscriber that answers
accurately is retried exactly when a retry can help.

*Example:* With the platform's service SDK, a handler returns `Handled.DONE`, `Handled.LATER` or
`Handled.NEVER`, which the SDK sends to the bus as an acknowledgement, a negative acknowledgement
or a termination.

*Example:* The platform's default schedule makes six attempts, at 0, 10 seconds, 1 minute,
5 minutes, 15 minutes and 35 minutes after the first delivery.

### 2.7 Act on every dead-lettering of the subscription.

[REQUIRED] The owner of an event subscription shall act on every event dead-lettered from it. An
event is dead-lettered when it has been retried for the whole delivery schedule; it is then kept,
with its body and headers intact, in the subscription's own dead-letter stream, and the platform
publishes an event naming the subscription, the dead-lettered event's `eventId` and `type`, and
the number of attempts. The owner finds the cause, fixes it, and has the event replayed by the
Notification Service's operators. *Rationale:* A dead-lettered event is one whose work the
subscriber has not done, and the owner is the one party that knows what that work requires.

### 2.8 Expect a subscription to start with the first event published after its approval.

[REQUIRED] A subscriber shall treat the first event its subscription delivers as the first event
published after the subscription was approved. *Rationale:* Approval is the subscriber's permission
to receive the topic's events, and it covers the events published from then on.

*Example:* A reporting service whose subscription to `ordmgt.public` is approved on a Wednesday at
10:00 receives each order placed from 10:00 on, and none placed before.

### 2.9 Read the state that predates a subscription from the publisher's API.

[RECOMMENDED] A subscriber that needs records as they stood before its subscription was approved
should read them from the publishing service's API, keep each record's `lastUpdatedAt`, and then
process delivered events with the same checks (2.2, 2.3). *Rationale:* The publisher's API checks
the subscriber's access to each record, so the subscriber starts from exactly the records it may
read, and the kept `lastUpdatedAt` discards any event that reports a change the read already
included.

*Example:* The reporting service reads its organization's open orders from the order service's
`GET /v1/orders`, then processes `ordmgt.public.order.*` events as they arrive.

## 3. Event types

### 3.1 Name an event type `<domain>.<class>.<resource>.<event>.<major>`.

[REQUIRED] An event type's name shall have five tokens, each lowercase letters, digits and dashes:

| Token | What it is |
|---|---|
| `domain` | The short code of the service domain that owns the fact |
| `class` | `public` when a customer organization may receive the type; `private` when only the platform organization may |
| `resource` | The `metadata.resourceType` of the record the fact is about, or of the record closest to it |
| `event` | What happened to that record, in the past tense, as words joined by dashes |
| `major` | The major version, a positive integer |

*Rationale:* The name tells a subscriber whose fact it is, who may receive it, which kind of record
it is about and what happened, and it is the key every publisher, subscriber and filter matches on.
Because the class is part of the name, making a private type public creates a new type.

*Example:* `ordmgt.public.order.placed.1` is the type an order's placement is published as: domain
`ordmgt`, class `public`, resource `order`, event `placed`, major `1`.

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
shall declare `requiredAccess`: each permission a person must hold, on an object in the platform's
authorization model, to read about the event. Every entry must hold.

- Name the permission that grants reading the record the event is about, so reading about an event
  never needs more or less than reading the record.
- Name the object by `objectIdPath` when each event names it, pointing at a field the payload
  schema requires. Name it by `objectId` when the type is always about one fixed object.
- Declare no entry when the event is a fact about the whole organization that every person in its
  audience may read.

*Rationale:* Access is checked when a person reads, which can be long after the event, and the
event type is the one place that knows which record the event is about. A permission rather than a
role relation keeps the declaration valid when roles change.

*Example:* For `expmgt.public.expense.approved.1`, the one entry is `can_view` on the `expense` at
`payload.expenseId`.

### 3.5 Name the one record an event is about.

[REQUIRED] An event type whose events are each about one record shall say where in the payload the
record's id is, and that field shall be a required UUID. An event type whose events are not about
one record names none. *Rationale:* The record's id becomes the last token of the event's subject
(4.3), so a subscriber can receive one record's events alone.

### 3.6 Name the event for the business fact that happened.

[REQUIRED] An event type's `event` token shall name the business fact in the domain's own words,
in the past tense: what a person in that domain would say happened to the record. *Rationale:* A
subscriber chooses types by what happened, and a name that states the fact lets it choose without
reading the payload.

*Example:* `expmgt.public.expense.submitted.1`, `expmgt.public.expense.approved.1` and
`expmgt.public.expense.reimbursed.1` each name one step of an expense's life.

### 3.7 Design event types around the workflows that subscribe to them.

[REQUIRED] An event type shall let a subscriber decide whether to act from the one event it
receives, without combining it with other events or reading the publisher's state back. A fact that
holds once several conditions are true is one event type when a subscriber acts on that fact.
*Rationale:* A subscriber that has to combine events or read state back to decide rebuilds the
publisher's logic, and two subscribers rebuilding it disagree.

*Example:* Accounts payable pays an expense report once every expense on it is approved. Expense
management publishes `expmgt.public.expense-report.approved.1` when the last expense is approved,
and accounts payable acts on that one event, without tracking each expense's approval.

### 3.8 Choose the class by who may receive the fact.

[REQUIRED] An event type's class shall be `public` when a customer organization's service
consumers may receive the fact about that organization's records, and `private` when the fact concerns how
the platform itself runs. The class is chosen when the type is first registered. *Rationale:* The
class decides which organizations may ever subscribe, and it is part of the type's name, so moving
a type to the other class creates a new type.

*Example:* `ordmgt.public.order.placed.1` is public, because a customer's service consumer acts on
its orders. `notify.private.event-subscription.dead-lettered.1` is private, because it reports how
the platform's delivery is running.

### 3.9 Carry no secret, and only the personal data a subscriber acts on.

[REQUIRED] An event's payload shall carry no credential, token or other secret, and shall carry
personal data only where a subscriber of the type acts on it. *Rationale:* Every event is kept in
the platform's event log and delivered to every subscriber of its topic, so whatever a payload
holds is stored and copied beyond the record it came from.

### 3.10 Keep each event within the publication limit of 1 MiB.

[REQUIRED] A publisher shall keep each event it publishes through the event facade
(`POST /v1/events`), its payload and headers together, within 1 MiB (1,048,576 bytes). The facade
refuses a larger event with `400` `payload-too-large` and records nothing. *Rationale:* The limit
is checked when the event is published, so every event the facade accepts reaches each subscriber
whole.

### 3.11 Document a type for the subscriber deciding whether to subscribe.

[REQUIRED] An event type shall carry a display name, a description that states what has happened
when the event is published, in the domain's own terms, and a steward, the person who answers for
the type. Its payload schema shall describe every property. *Rationale:* A subscriber decides from
the type's entry alone whether the type reports the fact it needs and what each field means.

*Example:* `expmgt.public.expense.approved.1` has the display name "Expense approved", the
description "An approver has approved an expense, and it is ready for reimbursement", and the
payload property `approvedById` described as "The user who approved the expense".

## 4. Topics

### 4.1 Give each service domain a public topic and a private topic.

[REQUIRED] A service domain shall have one topic for each class, named `<domain>.<class>`, and
every event type shall flow on the topic its domain and class name. A customer organization's machine account may subscribe to a public topic
once approved; only the platform organization's machine accounts may subscribe to a private topic.
*Rationale:* Approval to receive events is granted per topic, so a domain's events that customers
may see and those they may not are approved separately, and the transport refuses a private subject
to a customer's connection outright.

*Example:* `ordmgt.public.order.placed.1` flows on `ordmgt.public`, and
`ordmgt.private.order.fraud-flagged.1` flows on `ordmgt.private`.

### 4.2 Serve every organization from one topic.

[REQUIRED] A topic shall carry every organization's events, and shall never be created per
organization. Each event's organization is the sixth token of its subject (4.3), and a subscriber
receives only the organizations its subscription is entitled to. *Rationale:* A topic per tenant
does not scale, and the transport separates tenants already.

### 4.3 Read an event's subject as `<event type>.<organizationId>.<entityId>`.

[REQUIRED] Every event is placed on a subject of exactly seven tokens: the five of its type (3.1),
then the id of the organization the event belongs to, then the id of the record it is about, or `_`
when its type names no record (3.5). A subscriber's filters select on any of the seven tokens.
*Rationale:* A fixed number of tokens keeps every filter and permission a plain pattern, and the
record's id lets a subscriber follow one record.

*Example:* An order placed in one organization is placed on
`ordmgt.public.order.placed.1.3f9a2c71-8b4e-4d1a-9c6f-2e7b5a0d4c18.8d1e4b2a-5c3f-4a6e-9b7d-0f2c1e3a5b48`.

*Example:* The filter `ordmgt.public.order.>` selects every order event, and
`ordmgt.public.order.*.*.*.8d1e4b2a-5c3f-4a6e-9b7d-0f2c1e3a5b48` selects one order's.

## 5. Observability

### 5.1 Log every event's handling with its `eventId` and type.

[REQUIRED] A subscriber shall write the event's `eventId` and type on every log line about handling
that event, including how it answered (2.6). A publisher shall log the `eventId` the facade returns
for each event it publishes. *Rationale:* The `eventId` is the one value the facade, the bus, the
dead-letter stream and every subscriber share, so it is what an investigation follows from one log
to the next.

*Example:* `eventing: event 5d2c8e1a-7b4f-4a3e-9c6d-1f8b2e4a7c90 (ordmgt.public.order.placed.1) DONE`.

### 5.2 Watch the subscription's oldest unacknowledged event.

[REQUIRED] The owner of an event subscription shall watch its oldest unacknowledged event's age,
which the platform measures for every subscription. *Rationale:* A subscriber that falls behind
delays the work of every event it has yet to process, and the age of its oldest waiting event
shows that before anything is dead-lettered.

## 6. Testing

### 6.1 Test that every event a publisher builds meets its type's payload schema.

[REQUIRED] A publisher shall test, in its own test suite, that each event it builds validates
against the payload schema of its type's current version. *Rationale:* The facade refuses an event
that does not validate, so a test that validates it first moves the failure from a running service
to the build.

### 6.2 Test a handler by calling it with events, without the bus.

[REQUIRED] A subscriber shall test its handler by calling it directly with events built in the
test, and checking its answer (2.6) and the records it wrote. *Rationale:* The handler holds the
subscriber's logic, and calling it directly tests that logic without a running bus.

*Example:* A test of the Notification Service's engine calls its handler with an
`expmgt.public.expense.approved.1` event and checks that it answers `Handled.DONE` and wrote one
notification.

### 6.3 Test a handler with only the payload's required fields.

[REQUIRED] A subscriber shall test its handler with an event whose payload carries only the fields
its type's schema requires. *Rationale:* A type gains optional fields in later minor versions
(3.2), so a handler that works on the required fields alone works on every event of its major.

### 6.4 Test a handler with a repeated event and an out-of-date change.

[REQUIRED] A subscriber shall test that its handler, given the same event twice, does its work once
(2.2), and that, given a change older than one it has already applied to the record, discards it
(2.3). *Rationale:* The
bus redelivers and reorders events in normal running, so these two cases occur in production.
