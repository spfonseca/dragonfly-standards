---
shortName: TRIGS
description: >-
  How backend work is started — on a schedule, by an event, a message, an API request, a data
  change or an operator — what each trigger guarantees about delivery, duplication, ordering and
  timeliness, and the durable queues and dead-letter handling a queued worker's work arrives through.
adoptionMetrics:
  - Share of queued workers whose accepted work is held on a durable queue
  - Share of work queues with a dead-letter destination and a selective, authorized redrive
impactMetrics:
  - Accepted work lost to worker or service failure
  - Duplicate executions caused by a lease or visibility timeout expiring during processing
tags: [triggers, queues, messaging, dead-letter, redrive, leases]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, IMPLEMENTATION, OPERATE_AND_SUPPORT]
solutionScope: [RUNTIME_AND_EXECUTION, APIS_AND_INTEGRATIONS, DATA_AND_PERSISTENCE]
architectureQualities: [RELIABILITY, RECOVERABILITY, OPERABILITY]
---
# Execution Triggers Standard

| Field | Value |
|---|---|
| **Short Name** | TRIGS |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-27 |

## Purpose

This standard governs how backend work is started: on a schedule, by an event, by a message
arriving, by an API request, by a data change, or by an operator. It covers what each trigger
guarantees about delivery, duplication, ordering and timeliness, and what the work it starts may
therefore assume.

## Value Proposition

- **Accepted work survives failure** — a durable queue keeps work a service has accepted when the
  worker or service that would process it fails.
- **Retry and isolation follow the message** — one independently retryable unit per message keeps a
  single bad item from failing unrelated work.
- **No duplicate processing from expired leases** — leases and visibility timeouts sized to
  processing time stop a second worker from picking up work still in progress.
- **Poison work is contained and recoverable** — dead-lettering removes it from healthy capacity
  while keeping its identity and history for diagnosis and a controlled redrive.

## Scope

Applies to the mechanism that causes processing to begin.

It stops where the processing does. How that work is decomposed, coordinated, retried and recovered
is the Backend Job Design Standard's, and is selected independently of how the work arrived — a
schedule and a queued message can start the same job.

## Status

**A holding place, not a finished standard.** This exists because the two concerns were entangled: a
standard describing a pattern whose front door is a queue drifts into specifying the queue, and
then two documents define delivery semantics. A pattern may name what starts it; what that thing
guarantees belongs here.

Its guidelines specify the queue a worker pulls from rather than the worker. They were moved
verbatim from the Queued Worker section of the Backend Job Design Standard, where seven of its nine
requirements turned out to describe the front door; they carried the numbers §11.1–§11.4 and
§11.6–§11.8 before the move, and that standard's section has since been renumbered, so those numbers
there now mean something else. They are renumbered here; the other triggers — schedules, events,
API calls, data conditions and manual initiation — and further additions are later work.

Whether they belong here or in the Eventing Standard is the first thing to settle. A durable work
queue a service owns and a platform event stream are not obviously the same thing, and the answer
decides whether this standard covers transports or only what starts execution.

## 1. Work Queues

### 1.1 Use a durable queue when accepted work must survive worker or service failure.

[REQUIRED] A Queued Worker shall use durable messaging when loss of
accepted work is unacceptable; an in-memory queue is permitted only for
explicitly best-effort work. *Rationale:* Worker decoupling provides
reliability only when the buffer itself survives failure.

### 1.2 Keep each message scoped to one independently retryable unit of work.

[REQUIRED] A queue message shall identify one independently retryable
work unit or an immutable reference to it and shall not contain an
unbounded batch of unrelated work. *Rationale:* Message granularity
defines retry and failure isolation.

### 1.3 Keep queue messages small and treat authoritative data as externally owned.

[RECOMMENDED] Queue messages should carry identifiers and immutable
processing facts rather than large mutable domain snapshots when
authoritative data can be retrieved safely by reference. *Rationale:*
Small contracts reduce coupling, transport cost, and stale duplicated
state.

### 1.4 Set the message lease or visibility timeout longer than normal processing time.

[REQUIRED] The queue lease, acknowledgement deadline, or visibility
timeout shall exceed the expected processing duration with margin, or
the worker shall renew it while healthy processing continues.
*Rationale:* A lease expiring during normal processing causes concurrent
duplicate execution.

## 2. Dead-Lettering and Redrive

### 2.1 Dead-letter poison work after bounded delivery attempts.

[REQUIRED] A queued work item that repeatedly fails beyond the
configured delivery policy shall move to a dead-letter or equivalent
durable failed-work destination when the work must not be lost.
*Rationale:* Poison work must stop consuming healthy-worker capacity
while remaining available for diagnosis.

### 2.2 Preserve original identity and failure history during dead-lettering and redrive.

[REQUIRED] Dead-letter records and redriven messages shall preserve
the original work identity, original enqueue time, and sufficient
attempt/failure context to correlate the replay with prior processing.
*Rationale:* Redrive without lineage makes repeated failure
indistinguishable from new work.

### 2.3 Make dead-letter redrive selective and authorized.

[REQUIRED] Operators shall be able to redrive selected failed work
after remediation; bulk redrive shall be rate-limited and protected by
authorization appropriate to the side effects being repeated.
*Rationale:* Releasing an entire failed backlog at once can recreate the
original incident or overload recovered dependencies.
