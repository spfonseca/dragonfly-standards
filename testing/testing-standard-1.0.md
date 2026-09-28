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

## Scope

Applies to every workload the platform runs.

It does not cover unit-testing practice, coverage targets, or the test frameworks a language
community settles for itself. What it governs is which failure conditions must be exercised
deliberately, because they are the ones that are never met until production.

## Status: skeleton

**This is a holding place, not a finished standard.** The requirements below were moved verbatim
from the Backend Job Design Standard, where they had been written as job requirements although
almost none of them is specific to a job — any workload that can be killed mid-write, retried,
or run twice owes the same proofs. Two requirements that name a job pattern directly, checkpoint
restart for batch work and workflow replay compatibility, stayed behind with the pattern they
belong to. They keep the numbering they had there, which is wrong here; sections, ordering and any
additions are later work.

One requirement below, the reconciler removal test, was not moved but extracted: it had been a
clause inside a reconciliation requirement rather than a requirement of its own.

---

## Requirements moved from the Backend Job Design Standard

### 8.4 Test that a reconciling job removes what its source no longer holds.

[REQUIRED] Where a job's purpose is to make one system agree with
another, a test shall run it against a source that no longer holds a
fact the target does, and shall assert the target no longer holds it
afterwards. *Rationale:* An additive reconciler passes every other test
there is — it adds what is missing, changes nothing that already agrees,
and reports success. Removal is the only direction a test can distinguish
a working reconciler from one that quietly leaves withdrawn access in
place.

### 18.1 Test duplicate execution as a normal path.

[REQUIRED] Automated tests shall execute representative work more than
once and verify that resulting state and external side effects remain
correct. *Rationale:* Duplicate safety is a required execution property,
not an exceptional failure case.

### 18.2 Test process termination at commit boundaries.

[REQUIRED] Durable job patterns shall be tested with process
termination before and after significant state commits,
acknowledgements, checkpoints, and side effects. *Rationale:*
Crash-window testing verifies that the ordering of persistence and
acknowledgement does not lose or corrupt work.

### 18.3 Test retry exhaustion and terminal failure handling.

[REQUIRED] Automated tests shall verify that transient failures retry
according to policy, permanent failures do not retry indefinitely, and
exhausted work reaches the expected failed or dead-letter state.
*Rationale:* Retry policy is incomplete until its terminal path is
proven.

### 18.4 Test downstream timeout and throttling behavior.

[REQUIRED] Tests shall verify behavior when dependencies time out,
return throttling responses, become unavailable, and recover.
*Rationale:* Dependency failure is one of the dominant operating
conditions of background work.

### 18.5 Test concurrency and duplicate races.

[REQUIRED] Work with externally visible side effects shall be tested
for concurrent attempts against the same logical work identity where
duplicate claims are possible. *Rationale:* Sequential tests do not
expose the race conditions idempotency controls exist to prevent.

### 18.6 Test graceful and forced shutdown.

[REQUIRED] Worker-based implementations shall verify that graceful
shutdown drains in-flight work correctly and that forced termination
leaves unfinished work recoverable. *Rationale:* Deployment and
infrastructure termination must be proven safe before production.

### 18.9 Load-test the configured concurrency envelope.

[RECOMMENDED] Jobs using significant concurrency should be tested at
and above the intended concurrency limit against realistic dependency
constraints and work-item cost. *Rationale:* Safe concurrency is an
empirical capacity property, not just a configuration value.

### 22.21 Test Kubernetes termination and retry behavior in a real cluster environment.

[REQUIRED] Pre-production verification shall include representative
Pod deletion, Job failure/retry, worker rollout, and forced termination
scenarios in Kubernetes rather than relying solely on local process
tests. *Rationale:* Controller reconciliation, signals, leases,
scheduling, and termination timing are platform behaviors that unit
tests cannot reproduce.

### 22.22 Test resource exhaustion behavior.

[RECOMMENDED] Pre-production testing should include memory pressure,
CPU saturation, and dependency-constrained concurrency sufficient to
validate requests, limits, OOM recovery, retry behavior, and autoscaling
boundaries. *Rationale:* Kubernetes resource policy is only robust when
the application remains correct under the limits the platform will
enforce.

------------------------------------------------------------------------
