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

## Scope

Applies to every system that stores data, including data it holds incidentally — operational state,
queues, logs, caches and recovery stores, not only the records a product is built around.

It does not decide what a given system needs its data for. Retry windows, recovery windows and
audit obligations are stated by whoever owns the system or the obligation; this standard governs
how those inputs become a declared period and how the period is enforced.

## Status: skeleton

**This is a holding place, not a finished standard.** The requirement below was moved verbatim from
the Backend Job Design Standard, where it had been written as a job requirement although the
obligation is not a job's: how long data may be kept is settled by classification and audit
policy, and a job merely inherits the answer. It keeps the numbering it had there, which is wrong
here; sections, ordering and any additions are later work.

What this standard needs before it is usable is the part the moved requirement assumes and does not
supply: a data classification scheme, and the rule that turns a classification into a retention
period. Without those, "derived from data-classification policy" points at nothing.

---

## Requirements moved from the Backend Job Design Standard

### 16.8 Apply retention to job state and failed-work stores.

[RECOMMENDED] Execution history, idempotency records, dead-letter data,
checkpoints, and workflow history should have retention periods derived
from retry/replay needs, audit requirements, and data-classification
policy. *Rationale:* Retaining operational state forever increases
privacy, security, and storage cost without improving recovery after its
useful window.

------------------------------------------------------------------------
