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

## Scope

Applies to the mechanism that causes processing to begin.

It stops where the processing does. How that work is decomposed, coordinated, retried and recovered
is the Backend Job Design Standard's, and is selected independently of how the work arrived — a
schedule and a queued message can start the same job.

## Status: skeleton

**A holding place, not a finished standard.** This exists because the two concerns were entangled: a standard describing a pattern whose front
door is a queue drifts into specifying the queue, and then two documents define delivery semantics.
A pattern may name what starts it; what that thing guarantees belongs here.

---

## Requirements moved from the Backend Job Design Standard

These specify the queue a worker pulls from rather than the worker. They were written in that
standard's Queued Worker section, where seven of its nine requirements turned out to describe the
front door. They keep the numbering they carried BEFORE the move; that standard's §11 has since been
renumbered, so `11.1` there now means something else. The numbering is wrong here too — sections and
ordering are later work.

Whether they belong here or in the Eventing Standard is the first thing to settle. A durable work
queue a service owns and a platform event stream are not obviously the same thing, and the answer
decides whether this standard covers transports or only what starts execution.

### 11.1 Use a durable queue when accepted work must survive worker or service failure.

[REQUIRED] A Queued Worker shall use durable messaging when loss of
accepted work is unacceptable; an in-memory queue is permitted only for
explicitly best-effort work. *Rationale:* Worker decoupling provides
reliability only when the buffer itself survives failure.

### 11.2 Keep each message scoped to one independently retryable unit of work.

[REQUIRED] A queue message shall identify one independently retryable
work unit or an immutable reference to it and shall not contain an
unbounded batch of unrelated work. *Rationale:* Message granularity
defines retry and failure isolation.

### 11.3 Keep queue messages small and treat authoritative data as externally owned.

[RECOMMENDED] Queue messages should carry identifiers and immutable
processing facts rather than large mutable domain snapshots when
authoritative data can be retrieved safely by reference. *Rationale:*
Small contracts reduce coupling, transport cost, and stale duplicated
state.

### 11.4 Set the message lease or visibility timeout longer than normal processing time.

[REQUIRED] The queue lease, acknowledgement deadline, or visibility
timeout shall exceed the expected processing duration with margin, or
the worker shall renew it while healthy processing continues.
*Rationale:* A lease expiring during normal processing causes concurrent
duplicate execution.

### 11.6 Dead-letter poison work after bounded delivery attempts.

[REQUIRED] A queued work item that repeatedly fails beyond the
configured delivery policy shall move to a dead-letter or equivalent
durable failed-work destination when the work must not be lost.
*Rationale:* Poison work must stop consuming healthy-worker capacity
while remaining available for diagnosis.

### 11.7 Preserve original identity and failure history during dead-lettering and redrive.

[REQUIRED] Dead-letter records and redriven messages shall preserve
the original work identity, original enqueue time, and sufficient
attempt/failure context to correlate the replay with prior processing.
*Rationale:* Redrive without lineage makes repeated failure
indistinguishable from new work.

### 11.8 Make dead-letter redrive selective and authorized.

[REQUIRED] Operators shall be able to redrive selected failed work
after remediation; bulk redrive shall be rate-limited and protected by
authorization appropriate to the side effects being repeated.
*Rationale:* Releasing an entire failed backlog at once can recreate the
original incident or overload recovered dependencies.
