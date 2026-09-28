---
shortName: RESIL
description: >-
  How software behaves when a dependency it calls fails, slows or refuses it: retry backoff and
  jitter, which layer owns a retry boundary, honouring throttling signals, what must not be retried,
  circuit breaking, and compensation across systems.
adoptionMetrics:
  - Share of outbound dependency clients whose retry policy uses exponential backoff with jitter
  - Share of failure boundaries with one documented retry-owning layer
impactMetrics:
  - Retry traffic sent to a dependency during its outages
  - Incidents in which retries amplified a dependency failure
tags: [resilience, retry, backoff, throttling, circuit-breaker, compensation]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, IMPLEMENTATION, OPERATE_AND_SUPPORT]
solutionScope: [DEPENDENCIES_AND_EXTERNAL_SERVICES, APIS_AND_INTEGRATIONS, APPLICATION_COMPONENTS]
architectureQualities: [RESILIENCE, RELIABILITY, AVAILABILITY]
---
# Service Resilience Standard

| Field | Value |
|---|---|
| **Short Name** | RESIL |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-27 |

## Purpose

This standard governs how software behaves when something it depends on fails, slows down, or
refuses it: when to retry, how fast, how many times, which layer is allowed to decide, and when to
stop calling a dependency altogether.

## Value Proposition

- **Failing dependencies get room to recover** — backoff with jitter and honoured throttling
  signals keep callers from piling onto a dependency that is already struggling.
- **Retries do not multiply** — one layer owns each retry boundary, so a small retry policy cannot
  compound into an outage amplifier.
- **Actionable failures surface promptly** — deterministic failures are not retried, so the real
  cause is reported instead of hidden behind repeated identical attempts.
- **Sustained failure is contained** — circuit breaking or equivalent protection stops a caller
  population from continuously loading an unhealthy dependency.
- **Multi-system work ends in a known outcome** — explicit compensation undoes committed steps when
  a later one fails, without relying on rollback across systems.

## Scope

Applies to any software that calls something it does not control — a synchronous request handler
calling a service, a background job calling an API, a client calling a database.

It does not cover what a caller does with a failure once it has stopped retrying: recording the
outcome, preserving the work, or reporting it. Those are concerns of the calling workload and are
not addressed here.

## Status

**This is a holding place, not a finished standard.** Its guidelines were moved verbatim from the
Backend Job Design Standard (BJOBS v1.0 §6.2, §6.4, §6.5, §6.6, §6.8 and §7.5), where they had
been written as job requirements although none of them is specific to a job — any caller of any
dependency owes the same behaviour. They are renumbered here; further sections and additions are
later work.

Two things to settle when this is edited properly:

- Several still say "the job" or "workers". That wording is a leftover, not a scoping decision.
- Retry presumes a classification of failures into those worth retrying and those that are not.
  The standard they came from classifies against its own set of failure categories; this one will
  need to say what it classifies against, or the retry requirements rest on a term it never
  defines.

## 1. Retry

### 1.1 Retry transient failures with exponential backoff and jitter.

[REQUIRED] Automatic retries for transient dependency or
infrastructure failures shall use exponential backoff with jitter unless
the dependency provides a more specific retry schedule such as
`Retry-After`. *Rationale:* Backoff reduces pressure on a failing
dependency and jitter prevents synchronized workers from retrying
together.

### 1.2 Give one architectural layer ownership of each retry boundary.

[REQUIRED] For a given failure boundary, one layer shall own automatic
retry; nested libraries, workers, queues, workflow engines, and callers
shall not independently multiply retries unless the combined worst-case
attempts and duration are explicitly designed and documented.
*Rationale:* Layered retries multiply unexpectedly and can turn a small
retry policy into a dependency outage amplifier.

### 1.3 Honor dependency throttling signals.

[REQUIRED] When a downstream dependency communicates a retry delay or
rate-limit reset, the job shall honor that signal within its remaining
execution deadline rather than retry sooner. *Rationale:* Ignoring
explicit throttling instructions increases failure duration and may
cause further rejection.

### 1.4 Do not automatically retry deterministic validation or business-rule failures.

[REQUIRED] Failures caused by invalid input, violated business rules,
unsupported state, or another deterministic condition shall not be
automatically retried without a change in the relevant input or state.
*Rationale:* Repeating identical deterministic work cannot make it
succeed and only obscures the actionable failure.

## 2. Dependency Protection

### 2.1 Apply circuit breaking or equivalent dependency protection to repeated remote failures.

[RECOMMENDED] Jobs making sustained calls to a failing remote
dependency should use circuit breaking, adaptive concurrency, or
equivalent protection where repeated attempts would materially increase
load or latency. *Rationale:* Failure protection prevents large worker
populations from continuously attacking an unhealthy dependency.

## 3. Compensation

### 3.1 Use compensation for reversible multi-system business operations.

[RECOMMENDED] When a multi-system process must undo previously committed
steps after later failure, the design should define explicit compensating
actions rather than rely on rollback across systems. *Rationale:*
Compensation preserves independent transaction boundaries while giving
long-running work a recoverable business outcome.
