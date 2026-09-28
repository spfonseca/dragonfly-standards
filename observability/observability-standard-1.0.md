---
shortName: OBSRV
description: >-
  What a running workload must make visible about itself — structured logs, outcome and latency
  metrics, distributed traces, correlation with its Kubernetes runtime, and the conditions it alerts
  on — so an operator can tell whether it is working and what went wrong without reading the code.
adoptionMetrics:
  - Share of workloads emitting structured logs with the standard execution context fields
  - Share of scheduled workloads alerting on the age of their last successful completion
impactMetrics:
  - Time to detect a stalled or silently stopped workload
  - Time to diagnose a production failure
  - Share of alerts that required operator action
tags: [observability, logging, metrics, tracing, alerting, monitoring]
softwareLifecycle: [IMPLEMENTATION, OPERATE_AND_SUPPORT]
solutionScope: [OBSERVABILITY, RUNTIME_AND_EXECUTION, INFRASTRUCTURE]
architectureQualities: [OBSERVABILITY, OPERABILITY, SUPPORTABILITY]
---
# Observability Standard

| Field | Value |
|---|---|
| **Short Name** | OBSRV |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-27 |

## Purpose

This standard governs what a running system must make visible about itself: the logs it emits,
the metrics it measures, the traces it propagates, and the conditions it alerts on. It covers what
an operator needs to answer "is this working" and "what went wrong" without reading the code.

## Value Proposition

- **Failures are answerable without the code** — structured logs and traces carry the identity
  and context an operator needs to find what went wrong.
- **Degradation shows before users report it** — outcome rates, stage latencies and backlog age
  reveal reliability and timeliness problems that individual logs cannot summarise.
- **Telemetry stays affordable and usable** — unbounded identifiers stay in logs and traces rather
  than becoming metric dimensions.
- **Alerts mean action** — alerts target sustained, actionable conditions, including a workload that
  has silently stopped, rather than every expected transient failure.
- **Runtime and business failures are told apart** — Kubernetes failure modes are monitored
  separately from application failures, so each reaches the remedy it needs.

## Scope

Applies to every workload the platform runs, whatever its purpose.

It does not define the telemetry backend, the alert routing, or the dashboards. Those are platform
infrastructure decisions; this standard is what a workload owes them.

## Status

**This is a holding place, not a finished standard.** Its guidelines were moved verbatim from the
Backend Job Design Standard (BJOBS v1.0 §15.1–§15.8 and §22.15–§22.17, as numbered before that
standard's renumbering), where they had been written as job requirements although almost none of
them is specific to a job — a service serving requests owes the same structured context, the same
outcome metrics, the same trace propagation and the same restraint about high-cardinality
dimensions. They are renumbered here; further sections and additions are later work.

## 1. Logs and Traces

### 1.1 Emit structured logs with standard job context.

[REQUIRED] Job logs shall be structured and shall include, where
applicable, `executionId`, `workItemId` or partition/activity identity,
`attemptNumber`, execution pattern, lifecycle state, correlation
identifier, and trace identifiers. *Rationale:* Consistent fields make
background execution searchable and machine-correlatable across
implementations.

### 1.2 Trace downstream calls from the job execution.

[RECOMMENDED] Jobs should create or continue distributed traces for
significant processing and downstream calls, preserving links when
strict parent-child trace structure cannot cross asynchronous fan-out.
*Rationale:* Tracing reveals where execution time and failures occur
across distributed dependencies.

### 1.3 Export Kubernetes and application execution identity together.

[REQUIRED] Telemetry shall correlate application `executionId` and
unit-of-work identity with Kubernetes namespace, workload name, Pod
name, container, and immutable application version. *Rationale:*
Production diagnosis requires joining business execution state to the
concrete Kubernetes runtime that processed it.

## 2. Metrics

### 2.1 Emit execution outcome metrics.

[REQUIRED] Jobs shall emit metrics for executions or work units
started, succeeded, failed, cancelled, retried, and terminally exhausted
as applicable. *Rationale:* Outcome rates reveal reliability degradation
that individual logs cannot summarize.

### 2.2 Measure latency at distinct stages.

[REQUIRED] Where applicable, telemetry shall distinguish waiting or
queue latency from active processing duration and end-to-end completion
latency. *Rationale:* A workload can meet processing-time targets while
violating user expectations because work waits too long before starting.

### 2.3 Measure backlog age as well as backlog depth.

[REQUIRED] Buffered workloads shall expose the age of the oldest
unprocessed work in addition to item count or depth. *Rationale:* Depth
alone has no stable meaning when work-item cost or arrival rate varies.

### 2.4 Avoid high-cardinality identifiers as unrestricted metric dimensions.

[REQUIRED] Execution IDs, work-item IDs, user IDs, and similarly
unbounded values shall not be used as unrestricted metric labels or
dimensions; they belong in logs and traces. *Rationale:*
High-cardinality metrics can become prohibitively expensive and
operationally unusable.

## 3. Alerting and Monitoring

### 3.1 Alert on conditions requiring action.

[RECOMMENDED] Alerts should target sustained failure rate, retry
exhaustion, oldest-work age, missed completion objectives, stalled
executions, dead-letter growth, and dependency saturation rather than
individual transient failures. *Rationale:* Operators need actionable
signals, not a notification for every expected retry.

### 3.2 Alert on the age of a scheduled workload's last success, not only on its failures.

[REQUIRED] A workload that runs on a schedule shall be monitored by the
time since its last successful completion, and shall alert when that
exceeds its expected interval. *Rationale:* A schedule can stop without
anything failing. A Kubernetes `Job` whose Pod never starts a container
does not advance `backoffLimit`, stays active, and with
`concurrencyPolicy: Forbid` causes every subsequent start to be skipped —
so there is no failed run to alert on, and an alert watching for errors
sees none. Found live: a platform reconciler did not run for five hours
and the symptom was the absence of an event rather than the presence of
one. This is what notices when a scheduled job cannot start its next run.

### 3.3 Monitor Kubernetes failure modes separately from business failures.

[REQUIRED] Operational monitoring shall distinguish application/job
failures from Kubernetes scheduling failures, image-pull failures, OOM
kills, evictions, repeated container restarts, unschedulable Pods, and
Job-controller retry exhaustion. *Rationale:* Infrastructure and
business failures require different remediation and should not collapse
into one generic failed-job signal.

### 3.4 Alert on unschedulable or capacity-starved job work.

[REQUIRED] Production monitoring shall detect when Jobs or worker Pods
remain Pending because of insufficient cluster capacity, resource
constraints, affinity rules, quota, or other scheduling failures.
*Rationale:* A perfectly healthy application still fails its timeliness
objective if Kubernetes cannot place its Pods.
