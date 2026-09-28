---
shortName: CMPLY
description: >-
  How long a system keeps the data it holds, on what basis that period was chosen, and what happens
  when it ends — classification, retention, deletion, and the record that survives it — including
  data held incidentally, such as operational state, queues, logs, caches and recovery stores.
adoptionMetrics:
  - Share of job state and failed-work stores with a declared retention period
impactMetrics:
  - Volume of operational state held beyond its declared retention period
tags: [compliance, data-retention, data-classification, deletion, privacy]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, OPERATE_AND_SUPPORT, RETIRE]
solutionScope: [DATA_AND_PERSISTENCE, SECURITY_CONTROLS]
architectureQualities: [COMPLIANCE, PRIVACY, COST_EFFICIENCY]
---
# Compliance and Data Retention Standard

| Field | Value |
|---|---|
| **Short Name** | CMPLY |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-27 |

## Purpose

This standard governs how long a system keeps the data it holds, on what basis that period was
chosen, and what happens when the period ends: what is classified, what is retained, what is
deleted, and what record survives the deletion.

## Value Proposition

- **Every store has a declared period** — data a system holds, including incidental operational
  state, is kept for a stated reason and no longer.
- **Periods rest on stated inputs** — retry and recovery windows, audit obligations and
  classification determine how long data is kept, rather than habit or default.
- **Less exposure and cost** — data past its useful window is not left behind to add privacy,
  security and storage cost.

## Scope

Applies to every system that stores data, including data it holds incidentally — operational state,
queues, logs, caches and recovery stores, not only the records a product is built around.

It does not decide what a given system needs its data for. Retry windows, recovery windows and
audit obligations are stated by whoever owns the system or the obligation; this standard governs
how those inputs become a declared period and how the period is enforced.

## Status

**This is a holding place, not a finished standard.** Its one guideline was moved verbatim from the
Backend Job Design Standard (BJOBS v1.0 §16.8, as numbered before that standard's renumbering), where
it had been written as a job requirement although the obligation is not a job's: how long data may
be kept is settled by classification and audit policy, and a job merely inherits the answer. It is
renumbered here; further sections and additions are later work.

What this standard needs before it is usable is the part the moved guideline assumes and does not
supply: a data classification scheme, and the rule that turns a classification into a retention
period. Without those, "derived from data-classification policy" points at nothing.

## 1. Retention

### 1.1 Apply retention to job state and failed-work stores.

[RECOMMENDED] Execution history, idempotency records, dead-letter data,
checkpoints, and workflow history should have retention periods derived
from retry/replay needs, audit requirements, and data-classification
policy. *Rationale:* Retaining operational state forever increases
privacy, security, and storage cost without improving recovery after its
useful window.
