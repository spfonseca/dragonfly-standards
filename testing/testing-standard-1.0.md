---
shortName: TESTS
description: >-
  Which failure conditions a workload must be tested under deliberately — duplicate execution,
  termination mid-commit, retry exhaustion, downstream timeouts and throttling, concurrent races,
  shutdown, removal by a reconciler and resource exhaustion — rather than only the path it was
  designed for.
adoptionMetrics:
  - Share of workloads with automated duplicate-execution and commit-boundary termination tests
  - Share of Kubernetes workloads verified against Pod deletion and forced termination in a real cluster
impactMetrics:
  - Production incidents caused by a failure condition no test exercised
tags: [testing, verification, failure-testing, idempotency, concurrency, load-testing]
softwareLifecycle: [VERIFICATION_AND_TESTING, IMPLEMENTATION, RELEASE]
solutionScope: [QUALITY_AND_TESTING, RUNTIME_AND_EXECUTION, DEPENDENCIES_AND_EXTERNAL_SERVICES]
architectureQualities: [TESTABILITY, RELIABILITY, RESILIENCE]
---
# Testing and Verification Standard

| Field | Value |
|---|---|
| **Short Name** | TESTS |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-27 |

## Purpose

This standard governs how a system is proven to behave correctly under the conditions it will
actually meet — duplicate delivery, termination mid-commit, retry exhaustion, downstream timeouts,
concurrent races and resource exhaustion — rather than only on the path it was designed for.

## Value Proposition

- **Failure paths are proven, not assumed** — duplicate delivery, crashes at commit boundaries and
  retry exhaustion are exercised before production meets them.
- **Races surface in tests** — concurrent attempts against the same work expose what sequential
  tests cannot.
- **Reconcilers are shown to remove** — a removal test tells a working reconciler from one that
  quietly leaves withdrawn access in place.
- **Platform behaviour is verified where it happens** — termination, retry and resource limits are
  tested in a real cluster rather than inferred from local runs.

## Scope

Applies to every workload the platform runs.

It does not cover unit-testing practice, coverage targets, or the test frameworks a language
community settles for itself. What it governs is which failure conditions must be exercised
deliberately, because they are the ones that are never met until production.

## Status

**This is a holding place, not a finished standard.** Its guidelines were moved verbatim from the
Backend Job Design Standard (BJOBS v1.0 §18.1–§18.6, §18.9, §22.21 and §22.22, as numbered before
that standard's renumbering), where they had been written as job requirements although almost none
of them is specific to a job — any workload that can be killed mid-write, retried, or run twice owes
the same proofs. Two requirements that name a job pattern directly, checkpoint restart for batch
work and workflow replay compatibility, stayed behind with the pattern they belong to. They are
renumbered here; further sections and additions are later work.

One guideline, the reconciler removal test (BJOBS v1.0 §8.4 before the move), was not moved but
extracted: it had been a clause inside a reconciliation requirement rather than a requirement of its
own.

## 1. Duplicate and Concurrent Execution

### 1.1 Test duplicate execution as a normal path.

[REQUIRED] Automated tests shall execute representative work more than
once and verify that resulting state and external side effects remain
correct. *Rationale:* Duplicate safety is a required execution property,
not an exceptional failure case.

### 1.2 Test concurrency and duplicate races.

[REQUIRED] Work with externally visible side effects shall be tested
for concurrent attempts against the same logical work identity where
duplicate claims are possible. *Rationale:* Sequential tests do not
expose the race conditions idempotency controls exist to prevent.

## 2. Failure, Retry and Shutdown

### 2.1 Test process termination at commit boundaries.

[REQUIRED] Durable job patterns shall be tested with process
termination before and after significant state commits,
acknowledgements, checkpoints, and side effects. *Rationale:*
Crash-window testing verifies that the ordering of persistence and
acknowledgement does not lose or corrupt work.

### 2.2 Test retry exhaustion and terminal failure handling.

[REQUIRED] Automated tests shall verify that transient failures retry
according to policy, permanent failures do not retry indefinitely, and
exhausted work reaches the expected failed or dead-letter state.
*Rationale:* Retry policy is incomplete until its terminal path is
proven.

### 2.3 Test downstream timeout and throttling behavior.

[REQUIRED] Tests shall verify behavior when dependencies time out,
return throttling responses, become unavailable, and recover.
*Rationale:* Dependency failure is one of the dominant operating
conditions of background work.

### 2.4 Test graceful and forced shutdown.

[REQUIRED] Worker-based implementations shall verify that graceful
shutdown drains in-flight work correctly and that forced termination
leaves unfinished work recoverable. *Rationale:* Deployment and
infrastructure termination must be proven safe before production.

## 3. Reconciliation

### 3.1 Test that a reconciling job removes what its source no longer holds.

[REQUIRED] Where a job's purpose is to make one system agree with
another, a test shall run it against a source that no longer holds a
fact the target does, and shall assert the target no longer holds it
afterwards. *Rationale:* An additive reconciler passes every other test
there is — it adds what is missing, changes nothing that already agrees,
and reports success. Removal is the only direction a test can distinguish
a working reconciler from one that quietly leaves withdrawn access in
place.

## 4. Platform and Capacity

### 4.1 Test Kubernetes termination and retry behavior in a real cluster environment.

[REQUIRED] Pre-production verification shall include representative
Pod deletion, Job failure/retry, worker rollout, and forced termination
scenarios in Kubernetes rather than relying solely on local process
tests. *Rationale:* Controller reconciliation, signals, leases,
scheduling, and termination timing are platform behaviors that unit
tests cannot reproduce.

### 4.2 Load-test the configured concurrency envelope.

[RECOMMENDED] Jobs using significant concurrency should be tested at
and above the intended concurrency limit against realistic dependency
constraints and work-item cost. *Rationale:* Safe concurrency is an
empirical capacity property, not just a configuration value.

### 4.3 Test resource exhaustion behavior.

[RECOMMENDED] Pre-production testing should include memory pressure,
CPU saturation, and dependency-constrained concurrency sufficient to
validate requests, limits, OOM recovery, retry behavior, and autoscaling
boundaries. *Rationale:* Kubernetes resource policy is only robust when
the application remains correct under the limits the platform will
enforce.
