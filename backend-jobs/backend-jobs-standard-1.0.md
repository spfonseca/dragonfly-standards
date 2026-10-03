---
shortName: BJOBS
description: 'Approved execution patterns for backend work outside the request path (Simple Job, Queued
  Worker, Batch / Parallel Job, Orchestrated Workflow) and the requirements for implementing them on Kubernetes:
  state, idempotency, retries, concurrency, reconciliation, cancellation and shutdown.'
adoptionMetrics:
- Share of backend jobs with a documented, approved execution pattern and the requirements that drove
  its selection
- Share of backend jobs recording executions, attempts and lifecycle states under the common execution
  contract
impactMetrics:
- Production incidents per quarter caused by duplicate execution, lost work or jobs stuck in a non-terminal
  state
- Median time to diagnose a failed job execution from its recorded state and failure category
- Share of backend jobs using a pattern more complex than their workload requirements justify
tags:
- backend-jobs
- batch
- workflow
- kubernetes
- reliability
softwareLifecycle:
- ARCHITECTURE_AND_DESIGN
- IMPLEMENTATION
- DEPLOYMENT
- OPERATE_AND_SUPPORT
solutionScope:
- SOFTWARE_ARCHITECTURE
- APPLICATION_COMPONENTS
- RUNTIME_AND_EXECUTION
architectureQualities:
- RELIABILITY
- RECOVERABILITY
- SCALABILITY
- OPERABILITY
---

# Backend Job Design Standard

| Field | Value |
|---|---|
| **Short Name** | BJOBS |
| **Version** | 1.0 |
| **Status** | Published |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-27 |

## Purpose

This standard establishes the approved architecture patterns and
implementation requirements for backend jobs. It gives engineers and
AI-assisted development tools enough prescriptive guidance to select an
execution architecture and implement it consistently, reliably,
observably, recoverably, scalably, and safely.

## Value Proposition

-   **Consistent architecture decisions** --- engineers choose from a
    small set of approved execution patterns instead of inventing a new
    job architecture for each workload.
-   **Simpler solutions** --- selection begins with the simplest viable
    pattern and introduces queues, parallelism, or orchestration only
    when workload requirements justify them.
-   **Reliable execution** --- common expectations for idempotency,
    retries, failure isolation, recovery, and state management prevent
    recurring classes of production failure.
-   **Operational consistency** --- every job exposes enough execution
    state, telemetry, and context to be operated and supported
    predictably.
-   **AI-ready guidance** --- explicit pattern characteristics and
    selection rules allow AI-assisted engineering tools to make
    architecture choices using the same reasoning expected of engineers.

## Scope

This standard applies to backend processing that executes outside the
normal synchronous request-response path, including scheduled,
event-triggered, message-triggered, API-initiated, data-triggered, and
manually initiated work. Trigger mechanisms are intentionally outside
the execution-pattern taxonomy; a trigger determines **when work
begins**, while this standard's execution patterns determine **how the
work executes**.

Backend jobs governed by this standard are deployed on **Kubernetes**.
Sections 18--20 define the Kubernetes workload mapping, runtime
requirements, and operational controls that implementations shall apply
in addition to the technology-independent requirements in Sections
1--17. Kubernetes-specific requirements are intentionally concentrated
in those sections so the execution patterns and correctness rules remain
understandable independently of platform mechanics.

This standard does not define the REST contract used to expose or
monitor asynchronous operations. Where a backend job is initiated or
observed through an API, the shape of that interface is an API design
concern and is not addressed here.

Five further concerns are deliberately outside it, because none is
particular to a backend job and each is identical for a workload that
serves requests:

- **Observability** — what a job emits, measures, traces and alerts on.
  A job owes the material an alert would be built from, which is a
  reporting obligation and appears here as such (8.8, 8.12, 19.11), but
  this standard levies no alerting requirement: a requirement to alert
  is only meaningful where there is something for it to bind to.
- **Testing** — how a workload is proven against duplicate delivery,
  termination mid-commit, retry exhaustion, downstream timeouts,
  concurrent races and resource exhaustion. Section 16 keeps only the
  two proofs that name a job pattern directly.
- **Workload security on Kubernetes** — the identity a Pod runs as, the
  privileges it holds, what it may reach, how its image is named and how
  its manifests are delivered. Section 14 covers the identity and
  credentials a job needs to do its own work, which is a different
  question.
- **Transport** — what a queue guarantees about delivery, ordering and
  duplication. A pattern may name what feeds it; what that thing
  guarantees is not defined here.
- **Data retention** — how long execution history, dead-lettered work,
  checkpoints and idempotency records may be kept. A job's retry and
  replay window is an input to that period; the period itself is settled
  by classification and audit policy and is not set here.

------------------------------------------------------------------------

## 1. Architecture Selection

### 1.1 Select an approved execution pattern for every backend job.

[REQUIRED] Every backend job shall use one of the four approved
execution patterns defined by this standard: **Simple Job**, **Queued
Worker**, **Batch / Parallel Job**, or **Orchestrated Workflow**.
*Rationale:* A deliberately small pattern catalog concentrates
engineering knowledge, makes architecture decisions comparable, and
prevents unnecessary one-off execution models.

The four are distinguished by **how execution ends**, which is what
determines how work is deployed, scaled, stopped and recovered:

| Pattern | Ends |
|---|---|
| Simple Job | when the work is done |
| Batch / Parallel Job | when the work is done, having been decomposed to get there |
| Orchestrated Workflow | when the work is done, across time and process restarts |
| Queued Worker | it does not — it is stopped |

The queue in a Queued Worker, and the schedule on a Simple Job, are how
each is fed. They are not what either one is.

### 1.2 Select the simplest pattern that satisfies the workload requirements.

[REQUIRED] Architecture shall begin with the least complex approved
pattern capable of satisfying the workload's reliability, scale,
concurrency, state, and recovery requirements; additional coordination
mechanisms shall be introduced only when a requirement justifies them.
*Rationale:* Queues, distributed workers, parallel coordination, and
durable workflows create real operational cost and should solve a
demonstrated problem rather than anticipate one.

### 1.3 Base pattern selection on execution requirements rather than trigger mechanism.

[RECOMMENDED] A job's execution pattern should be selected independently
of whether it is started by a schedule, event, message, API request,
data change, or operator action. *Rationale:* The mechanism that starts
work does not determine how that work must be decomposed, coordinated,
retried, or recovered.

### 1.4 Evaluate the differentiating workload requirements before selecting a pattern.

[REQUIRED] Pattern selection shall consider, at minimum, work volume,
execution duration, concurrency, decomposition into independent work
items, workflow dependencies, durable-state needs, failure isolation,
retry requirements, recovery granularity, ordering constraints, latency
expectations, and resource variability. *Rationale:* These
characteristics materially change the execution architecture and provide
a repeatable basis for selecting one pattern over another.

### 1.5 Document the selected pattern and the requirements that drove the decision.

[RECOMMENDED] The job's architecture documentation should identify its
execution pattern and briefly record the workload characteristics that
caused that pattern to be selected. *Rationale:* Recording the decision
makes later complexity explainable and allows engineers and AI tools to
reassess the architecture when workload characteristics change.

### 1.6 Select a pattern for a reconciling job the same way, and apply Section 8 in addition.

[REQUIRED] A job whose purpose is to make one system agree with another shall select its execution
pattern from the same four, on the same grounds, and shall additionally satisfy Section 8.
*Rationale:* Reconciliation determines what a job decides to do, not how its work is decomposed, so
it is orthogonal to the pattern rather than a fifth one — the same reconciler commonly runs as a
Simple Job at small scale and as a Batch / Parallel Job or Queued Worker as its input grows, without
becoming a different kind of job.

## 2. Approved Execution Patterns

### 2.1 Use a Simple Job for one bounded execution.

[REQUIRED] Work that can be treated as one bounded execution, running
from start to completion without durable coordination, decomposition
into independently managed work items, or persistent workflow state, shall use the **Simple Job** pattern. *Rationale:* A
single execution with no work items has the smallest implementation and
operational footprint, and 1.2 requires beginning from the least complex pattern that
satisfies the workload — so where this one does satisfy it, reaching past
it is the complexity that rule exists to prevent.

**Typical fit:** bounded work; modest volume; limited concurrency needs;
restart of the whole execution is acceptable; no durable multi-step
state.

### 2.2 Use a Queued Worker for processing that does not end.

[RECOMMENDED] Use the **Queued Worker** pattern when processing runs
continuously, taking independent items as they arrive and stopping only
when it is told to. *Rationale:* This is the one pattern that does not
end by finishing its work, and everything that distinguishes it follows
from that: it deploys as a long-running workload rather than a Job, it
scales by replica count rather than by schedule, it is stopped by a
signal rather than by completion, and its shutdown is a drain rather than
an exit. Whether the items arrive on a queue is how it is fed, not what
it is.

**Typical fit:** work arrives continuously or in bursts; the processing
should absorb demand variation rather than be scheduled against it; items
are independent and retried individually; there is no point at which the
work is finished.

**Not this pattern:** a bounded set of items known in advance, even if
they arrive through a queue — that ends, and ending is Simple Job or
Batch / Parallel.

### 2.3 Use a Batch / Parallel Job for a bounded collection of work.

[RECOMMENDED] Use the **Batch / Parallel Job** pattern when a known or
discoverable bounded collection must be processed as one logical
execution and throughput can benefit from partitioning or concurrent
processing. The pattern may use serial batches, partitions,
fan-out/fan-in, or other bounded parallel-processing techniques while
retaining one logical job boundary. *Rationale:* Explicit partitioning
and parallelism allow large finite workloads to complete efficiently
without converting every item into an independently managed long-lived
workflow.

**Typical fit:** large finite datasets; throughput matters more than
individual-item latency; partitionable work; aggregate completion
matters; checkpointing may be useful.

### 2.4 Use an Orchestrated Workflow for dependent, durable activities.

[RECOMMENDED] Use the **Orchestrated Workflow** pattern when
successful completion requires multiple dependent activities whose
sequencing, branching, retries, waiting, compensation, or state must
survive process failure or long periods of time. *Rationale:* Durable
orchestration makes coordination explicit and recoverable instead of
embedding a distributed state machine in application code and transient
process memory.

**Typical fit:** multiple dependent steps; long-running execution;
durable waits; branching; compensation; human or external-system
dependencies; step-level recovery.

### 2.5 Treat fan-out/fan-in as a processing technique rather than a top-level execution pattern.

[RECOMMENDED] Fan-out/fan-in should be implemented within a Batch /
Parallel Job or Orchestrated Workflow according to whether the parallel
work is a bounded data-processing operation or part of a durable
multi-step process. *Rationale:* Treating every coordination technique
as a separate architecture pattern expands the catalog without creating
a meaningfully different top-level execution model.

Work is fanned out for one of two reasons, and they route differently:

- **The same processing, repeated over many items.** The work is
  homogeneous, the gain is throughput, and the items are independent of
  each other. This is what the Batch / Parallel Job pattern is for, and
  it is the more common case by a wide margin. The signal to look for is
  a job that iterates a collection applying the same logic to each
  element — that is a partitionable workload whether or not it was
  written as one.

- **Different processing, run concurrently.** The work is heterogeneous,
  the gain is elapsed time rather than throughput, and the branches
  rejoin. Where the branches are independent and short, this belongs in
  whichever pattern already owns the execution. Where they must survive
  process failure, have their own retry policies, or wait on something,
  it is a durable multi-step process and belongs in an Orchestrated
  Workflow.

Distinguishing them matters because the first scales by adding
partitions and the second does not: concurrency across three different
branches is bounded at three however much capacity is available.

## 3. Common Execution Contract

### 3.1 Model every job as executions, work items and attempts.

[REQUIRED] A job shall identify its work using this model, and the terms
shall mean the following throughout its design, telemetry and state:

- An **execution** is one logical run of a job: the thing that starts,
  does work, and reaches a terminal state. It is what an operator means
  by "the run that failed at 03:00".
- A **work item** is an independently retryable subdivision of an
  execution — a partition, an activity, one message. It exists where a
  failure should be recoverable without redoing the whole execution.
- An **attempt** is one try at either. The same execution or work item
  may be attempted several times and remains the same execution or work
  item.

A job shall distinguish the *thing* from the *try*: an execution retried
three times is one execution with three attempts, not three executions.
Not every pattern carries all three, and a job with no independently
retryable parts has executions and attempts and no work items, which is
not a gap to fill.

A Queued Worker's execution shall be one message processed to a terminal
outcome, not the worker process.

| Pattern | One execution is | Work items are |
|---|---|---|
| Simple Job | one run of the job | usually none — the execution is the unit |
| Batch / Parallel Job | one run over the whole collection | its partitions |
| Orchestrated Workflow | one workflow instance | its activities |
| Queued Worker | processing one message to a terminal outcome | usually none |

*Rationale:* Three identifiers appear in the requirements below and mean
nothing without the relationship between them. Conflating the thing with
the try makes it impossible to ask how many times something was tried,
which is the first question asked of a job that produced a duplicate. And
a Queued Worker runs indefinitely and is stopped rather than completed,
so treating its process as the execution produces one identifier covering
millions of unrelated pieces of work — which is the same as having none.

### 3.2 Give every logical execution a globally unique execution identifier.

[REQUIRED] Every logical job execution shall have a globally unique
`executionId` that remains stable across retries of that execution and
is propagated through logs, metrics, traces, child work, and externally
visible job state. *Rationale:* One stable identity is the join key that
lets operators and software reconstruct an execution across processes
and attempts.

### 3.3 Identify each independently retryable unit of work, where one exists.

[RECOMMENDED] Where an execution is subdivided into independently
retryable units of work, each should have a stable `workItemId`,
partition identifier, activity identifier, or equivalent identity within
its parent execution. *Rationale:* Retry, deduplication, recovery, and
item-level observability require an identity more precise than the
parent execution. An identifier the execution platform already supplies
— a partition index, a message identifier, an activity identifier —
satisfies this, so a job that has work items need not mint a new one.

### 3.4 Number execution attempts explicitly.

[RECOMMENDED] Every attempt of an execution or work item should expose an
`attemptNumber` beginning at one and increasing monotonically for
subsequent attempts of that execution or work item. *Rationale:* Attempt identity makes
retry behavior observable and allows logs and failure records to
distinguish repeated execution from duplicate telemetry.

### 3.5 Propagate correlation and trace context across asynchronous boundaries.

[REQUIRED] A job shall propagate the initiating correlation identifier
and distributed-trace context across queue, partition, workflow, and
service boundaries when the underlying mechanism supports propagation.
*Rationale:* Asynchronous boundaries otherwise break the causal chain
needed to diagnose how an initiating action became background work.

### 3.6 Persist input or an immutable reference to input before acknowledging initiation.

[REQUIRED] When accepted work must survive process loss, the system
shall durably persist the job input or an immutable reference sufficient
to reconstruct it before acknowledging that initiation succeeded.
*Rationale:* An acknowledgement creates an obligation to execute;
accepting work that exists only in process memory can lose that
obligation on failure.

### 3.7 Define a bounded execution deadline.

[REQUIRED] Every execution, and every work item where one exists, shall
run under a finite timeout or deadline appropriate to its work;
unbounded execution is prohibited. *Rationale:* A hung execution
otherwise consumes capacity indefinitely and prevents retry, recovery,
and operational escalation.

### 3.8 Distinguish execution deadline from downstream-operation timeout.

[REQUIRED] Calls to downstream systems shall use timeouts shorter than
the remaining execution deadline, leaving sufficient time for the job to
handle failure, persist state, and terminate cleanly. *Rationale:* A
dependency must not consume the entire job deadline and prevent
controlled recovery.

### 3.9 Treat configuration as immutable for an attempt.

[RECOMMENDED] Configuration should be resolved at attempt start and
treated as immutable for that attempt, except for controls the job
declares as dynamic, such as cancellation or throttling. *Rationale:* Mid-attempt configuration drift makes execution
non-repeatable and complicates diagnosis.

## 4. State and Lifecycle

### 4.1 Define one standard lifecycle for a job's executions.

[REQUIRED] A job whose executions are observable after initiation
shall define a single lifecycle that every one of its executions
follows, exposing at least `PENDING`, `RUNNING`, `SUCCEEDED`, `FAILED`,
and `CANCELLED` semantics, whether or not the underlying implementation
uses those exact storage values. *Rationale:* An administrative
interface presents jobs at its top level and each job's executions
beneath, so the states it renders are a property of the job rather than
of a run. A lifecycle that varies between runs of the same job leaves
that interface with nothing to display at the level an operator works
at, and one that varies between jobs makes every job a separate thing
to learn.

### 4.2 Treat success, failure, and cancellation as terminal states.

[REQUIRED] A job's lifecycle shall classify `SUCCEEDED`, `FAILED`, and
`CANCELLED` as terminal for a logical execution, and `PENDING` and
`RUNNING` as non-terminal; retrying terminal work shall create a new
execution or an explicitly recorded replay linked to the original.
*Rationale:* Mutating terminal history destroys the audit trail and
makes the meaning of completion unstable.

### 4.3 Recover to a known good state after losing the executing process.

[REQUIRED] A job shall be able to recover from the loss of its executing
process without losing the record of work that has already reached a
terminal outcome, and without repeating work that is not safe to repeat.
*Rationale:* State that exists only in the executing process disappears
with it, and a job that has committed partial results cannot recover
unless it can still determine what it had done.

### 4.4 Record lifecycle timestamps.

[REQUIRED] Every execution shall record, at minimum, `createdAt`,
`startedAt`, and either `completedAt` or `failedAt` as applicable;
timestamps shall use the organization's standard UTC timestamp
representation. *Rationale:* These timestamps make queue
delay, execution duration, stalls, and service objectives measurable.

### 4.5 Classify a terminal failure against a fixed set of categories.

[REQUIRED] A failed execution shall record one of the following
categories, together with a diagnostic summary carrying no secret or
personal data:

| Category | Meaning |
|---|---|
| `INVALID_INPUT` | the work could not succeed as given, and retrying it unchanged will not help |
| `NOT_AUTHORIZED` | the job's identity lacked a right the work required |
| `DEPENDENCY_FAILURE` | a system the job called failed, refused, or was unreachable |
| `TIMEOUT` | the execution or one of its calls exceeded its deadline |
| `RETRY_EXHAUSTED` | a retryable failure recurred until the retry budget was spent |
| `RESOURCE_EXHAUSTED` | capacity the execution needed was denied or reclaimed |
| `DEFECT` | the job itself is wrong — an unhandled error or a violated invariant |

Every failure shall map to one of these, and a failure the job cannot
otherwise classify is a `DEFECT`.

*Rationale:* Operators and automation need to know why work stopped
without parsing arbitrary log text, and a category each job words for
itself cannot be queried across jobs or acted on by a common runbook.
The categories divide by the response they call for: `INVALID_INPUT`
needs the input changed, `DEPENDENCY_FAILURE` and `TIMEOUT` need the run
repeated, `RESOURCE_EXHAUSTED` needs capacity, and `DEFECT` needs a code
change.

### 4.6 Use atomic state transitions.

[REQUIRED] Competing executors shall not be able to transition the
same logical work into `RUNNING` or a terminal state concurrently;
ownership and state transitions shall use an atomic claim, conditional
update, lease, or equivalent concurrency control. *Rationale:* State
transitions are coordination points and must not permit two workers to
believe they exclusively own the same work.

## 5. Idempotency and Duplicate Execution

### 5.1 Assume at-least-once execution.

[REQUIRED] Job implementations shall assume that any execution or work
item may execute more than once and shall preserve correctness under
duplicate execution. *Rationale:* Redelivery, ambiguous acknowledgement,
process termination, and operator replay make exactly-once execution an
unsafe distributed-system assumption.

### 5.2 Define the idempotency scope.

[REQUIRED] Every operation with externally visible side effects shall
define the identity that makes two attempts the same logical operation,
normally the `executionId`, a work item's identity, a domain operation
identifier, or a deterministic composite key. *Rationale:* Idempotency cannot be
enforced without a precise definition of what constitutes a duplicate.

### 5.3 Persist idempotency decisions durably.

[REQUIRED] Where a duplicate would produce an effect the job has not
declared acceptable, the deduplication or idempotency record shall be
persisted in a durable store whose lifetime covers the maximum retry and
replay window. *Rationale:* In-memory duplicate detection disappears
exactly when process recovery causes duplicate execution. A job that can
absorb duplicates needs no record at all; one that cannot needs a record
that outlives the process.

### 5.4 Claim non-idempotent work atomically.

[REQUIRED] A check for prior completion and the claim to perform a
non-idempotent operation shall be atomic or protected by an equivalent
uniqueness or concurrency constraint. *Rationale:* A read-then-write
race allows two workers to observe "not processed" and both perform the
side effect.

### 5.5 Return or reuse the prior result when a completed duplicate is encountered.

[OPTIONAL] When practical, a duplicate of already completed logical
work should resolve to the recorded prior outcome rather than repeat
downstream processing. *Rationale:* Reusing the completed result reduces
load and gives duplicates deterministic behavior.

### 5.6 Make replay explicit rather than bypassing idempotency silently.

[REQUIRED] Operational replay that intentionally repeats a completed
business action shall use a new logical operation identity or an
explicit override recorded in the audit trail; operators shall not
disable duplicate protection informally. *Rationale:* Replay and
accidental duplication are different intents and must remain
distinguishable.

## 6. Retry, Timeout, and Failure Policy

### 6.1 Classify every failure before deciding whether to retry.

[REQUIRED] Every failure boundary shall classify the failure using the
categories of 4.5, and shall retry automatically only
`DEPENDENCY_FAILURE`, `TIMEOUT`, and `RESOURCE_EXHAUSTED`.
`INVALID_INPUT`, `NOT_AUTHORIZED`, and `DEFECT` shall not be retried
automatically. `RETRY_EXHAUSTED` is the outcome of a retry policy rather
than an input to one, and shall not be produced at a failure boundary.

*Rationale:* Retry policy follows failure semantics rather than treating
every exception identically, and one vocabulary for the retry decision
and the recorded outcome means a failed execution's category already
says whether it was retried. Retrying a failure the job itself caused,
or one that only a grant change can fix, spends the retry budget with no
prospect of success and delays the failure becoming visible.

### 6.2 Bound retry attempts and retry duration.

[REQUIRED] Every automatic retry policy shall define a maximum attempt
count, maximum elapsed retry duration, or both; infinite retries are
prohibited. *Rationale:* Permanent failures otherwise consume capacity
indefinitely and can prevent failed work from becoming visible to
operators.

### 6.3 Preserve the final failed unit after retry exhaustion when loss is unacceptable.

[REQUIRED] Work that must not be lost shall enter a durable failed
state, dead-letter destination, or equivalent recovery store after
automated retries are exhausted. *Rationale:* Terminal failure must
become inspectable and recoverable rather than disappear.

## 7. Concurrency and Backpressure

### 7.1 Define a maximum concurrency for every horizontally scalable worker.

[REQUIRED] Every worker or parallel executor shall have an explicit
maximum number of concurrent work items per instance and, where required
to protect shared dependencies, an aggregate limit across instances.
*Rationale:* Autoscaling without concurrency bounds can exhaust
databases, APIs, memory, sockets, or rate limits faster than
infrastructure can react.

### 7.2 Derive concurrency from the tightest downstream constraint.

[RECOMMENDED] Concurrency should be sized from measured work cost and
the most restrictive downstream capacity or rate limit, then validated
under representative load. *Rationale:* The safe concurrency of a job is
determined by the bottleneck it consumes, not by how many workers the
compute platform can create.

### 7.3 Use a distributed concurrency control when the limit is global.

[REQUIRED] Where correctness or dependency protection requires a limit
across multiple worker instances, that limit shall be enforced through a
shared semaphore, queue dispatch control, partition ownership, platform
concurrency control, or equivalent distributed mechanism rather than
per-process counters. Whether such a mechanism is supplied to a job is a
platform concern, not addressed here. *Rationale:* Per-instance limits do
not enforce a global constraint after horizontal scaling — a limit of
four per instance across five instances is a limit of twenty, and the
dependency the limit exists to protect sees the twenty.

### 7.4 Provide backpressure when arrival can exceed sustainable processing rate.

[RECOMMENDED] Workloads whose arrival rate can exceed safe processing
capacity should use durable buffering, admission control, producer
throttling, or another explicit backpressure mechanism. *Rationale:*
Without backpressure, a burst becomes resource exhaustion or lost work.

### 7.5 Bound queue or backlog growth operationally.

[RECOMMENDED] Buffered workloads should define a maximum acceptable
backlog age or depth and an operational response when that threshold is
exceeded. *Rationale:* A durable queue prevents immediate failure but
can hide an accumulating timeliness failure unless backlog has an
objective.

### 7.6 Order work only within the scope that requires ordering.

[RECOMMENDED] Where some work must be processed in order, a job should
apply that ordering only within the scope the business rule names — one
customer, one account, one partition key — and should process different
scopes concurrently. *Rationale:* Two updates to the same account must
not be applied out of order; two updates to different accounts have no
relationship to each other. Serializing the whole workload to protect
the first case makes the job as slow as its single slowest item and buys
nothing for the second.

## 8. Reconciliation

### 8.1 Recognise when a job is reconciling, and apply this section to it.

[REQUIRED] A job whose purpose is to make one system agree with another
shall be treated as reconciling and shall satisfy this section, whatever
execution pattern it uses. A projection, a synchronisation, a mirror and
a backfill that runs more than once are all reconciling. *Rationale:*
Most scheduled jobs on a platform reconcile whether or not they were
designed as such, and the rules below are the ones that keep a job from
deleting what it was meant to protect. A job that is reconciling in
substance and not recognised as such is exactly the job that fails that
way — the recognition is what pulls the rest of this section onto it.

Reconciliation is not an execution pattern: it determines what a job
decides to do, where the patterns determine how work is decomposed and
coordinated. The two compose, and the same reconciler may run as a
Simple Job at small scale and as a Batch / Parallel Job or Queued Worker
as its input grows without becoming a different kind of job.

### 8.2 Rederive desired state from its source on every run.

[REQUIRED] A reconciling job shall compute desired state afresh from its source of truth each run,
and shall not treat a cached view, a previous run's output, or an incremental change feed as
authoritative. *Rationale:* State derived once and carried forward drifts silently, and a job that
trusts its own history cannot repair the error it made last time — which is the one failure
reconciliation exists to prevent.

### 8.3 Apply the difference, not the desired state.

[REQUIRED] A reconciling job shall compare desired state against actual state and apply only the
differences. *Rationale:* Writing everything each run makes the cost proportional to the estate
rather than to the change, hides what actually moved in a log of unchanged writes, and turns a
routine run into a large write burst against whatever it is reconciling
into. This is an obligation rather than advice: the objection to
requiring it is that a job unable to read its whole source cannot diff,
and 8.6 and 8.7 remove that case by making such a job abort rather than
reconcile — so there is no state in which the rule cannot be followed.

### 8.4 Converge on removal as deliberately as on addition.

[REQUIRED] Where the source no longer holds a fact that the target does, the job shall remove it
from the target. *Rationale:* Removal is the direction that
is reliably wrong: additive reconciliation looks correct in every test and in normal operation,
while access that should have been withdrawn quietly persists. A grant that arrives late is an
inconvenience; one that never leaves is an incident.

### 8.5 Define which facts the job owns before it removes anything.

[REQUIRED] A reconciling job shall define the subset of the target it manages, and shall remove only
facts within that subset. *Rationale:* A target is rarely written by one writer. A job that removes
everything it did not put there will delete another writer's work on its first run, and the blast
radius is the whole target rather than the job's own scope.

### 8.6 Fail closed when the source cannot be read.

[REQUIRED] A reconciling job shall distinguish a source that reports nothing from a source it could
not read, and shall abort the run rather than reconcile toward an empty or partial desired state.
*Rationale:* This is the failure that destroys an estate. An unreadable source read as an empty one
makes every managed fact a difference to be removed, and a job that is correct in every other
respect will faithfully delete everything it manages.

### 8.7 Treat an incomplete read as unreadable.

[REQUIRED] Where desired state is assembled from several reads, or from a paginated one, a job shall
treat the failure of any part as a failure of the whole. *Rationale:* A partial read is
indistinguishable from a shrunken source, and 8.5's protection is lost if a job applies it only to
the first page.

### 8.8 Report counts of facts examined, added, removed and left unchanged.

[REQUIRED] Each run shall report the counts of facts examined, added, removed and left unchanged,
and shall report a run in which nothing changed as a successful run. *Rationale:* A reconciler with
no output is indistinguishable from one that is not running, and the second run of a correct
reconciler reporting zero changes is the cheapest available proof that it converges.

### 8.9 Make a second run a no-op.

[REQUIRED] Running a reconciling job twice against an unchanged source shall produce no writes on
the second run. *Rationale:* Convergence is the property being claimed, and a second run that still
writes is comparing the wrong thing — usually a representation difference mistaken for a
difference in fact.

### 8.10 Pair a periodic full reconciliation with any incremental path.

[RECOMMENDED] Where a job consumes an event or change feed so that it can react sooner than its
schedule alone would allow, it should keep running a full reconciliation on a schedule — less
often than before, but not stop running one. *Rationale:* An
incremental path is an optimisation and not a correctness mechanism: events are missed, dropped and
delivered out of order, and the periodic full pass is what repairs the resulting drift. A system
with only the incremental half has no way to discover what it missed.

### 8.11 Keep a run shorter than the interval between runs.

[RECOMMENDED] A reconciling job's full run should complete well within the interval at which it is
scheduled, and a job whose run time has grown to approach that interval should be changed rather
than scheduled less often. *Rationale:* A run that does not finish before the next is due either
overlaps it or blocks it, and scheduling less often to hide that leaves the target stale for
longer. How to shorten the run — examining only what may have changed, partitioning, reducing what
is reconciled — is a design choice; noticing that it must be shortened is not.

### 8.12 Record when the job last reconciled successfully.

[RECOMMENDED] A reconciling job should publish the time of its last successful full reconciliation.
*Rationale:* The question asked of a reconciler in an incident is how stale the target may be, and
that is answerable from the last successful run rather than from the last run attempted.

## 9. Simple Job Implementation

### 9.1 Keep a Simple Job within one recoverable execution boundary.

[RECOMMENDED] A Simple Job should execute as one bounded unit whose
failure can be handled by retrying or restarting the whole job without
requiring durable coordination among internal steps. *Rationale:* If
partial progress must be independently recovered, the workload has
exceeded the defining simplicity of this pattern.

### 9.2 Persist externally visible side effects before reporting success.

[REQUIRED] A Simple Job shall not transition to `SUCCEEDED` until all
required side effects are durably committed. *Rationale:* Success must
mean the work survived executor termination rather than merely that the
code reached its final line.

### 9.3 Prefer whole-job retry over custom checkpointing for small bounded work.

[RECOMMENDED] A Simple Job should retry from its beginning rather than
introduce checkpoints unless repeating successful work has become
materially expensive or unsafe. *Rationale:* Checkpoint state is
coordination complexity and should be introduced only when restart cost
justifies it.

### 9.4 Promote a Simple Job when its recovery requirements outgrow the pattern.

[RECOMMENDED] A Simple Job that requires independently retryable items,
durable partition progress, or durable multi-step state should be
redesigned using Queued Worker, Batch / Parallel Job, or Orchestrated
Workflow rather than accumulating custom coordination code. *Rationale:*
Pattern boundaries prevent a nominally simple job from becoming an
unrecognized workflow engine.

## 10. Queued Worker Implementation

### 10.1 Design a Queued Worker to run indefinitely and to stop only on request.

[REQUIRED] A Queued Worker shall have no completion condition of its own,
shall remain available while work may arrive, and shall exit only in
response to a shutdown signal. *Rationale:* This is what separates the
pattern from a Simple Job, and the separation is not academic: a worker
that exits when its queue is momentarily empty turns an idle period into
a restart loop, and one treated as a Job by its deployment gets
completion semantics, backoff and retry limits that have no meaning for
work that never finishes. The requirements below are consequences of
running indefinitely, not of there being a queue.

### 10.2 Take the queue's guarantees as given rather than specifying them.

[RECOMMENDED] A Queued Worker should be designed against the delivery,
ordering, duplication and dead-letter behaviour its queue already
provides, and should not restate them. *Rationale:* The queue is the front
door, not the processing. What a queue guarantees about delivery,
ordering and duplication is a transport concern and is not addressed
here; a pattern that specifies its own transport ends up defining
delivery semantics twice, in two places that will disagree. What belongs
here is what the worker does with what arrives.

### 10.3 Size a lease longer than the work normally takes.

[RECOMMENDED] Where a queue grants time-bounded ownership of a work
item, that period should exceed the time processing the item normally
takes, and a worker still making progress should renew it. *Rationale:*
A lease that expires while its owner is still working hands the same
item to a second worker, so the work is done twice and correctness falls
back on idempotency. A lease far longer than the work has the opposite
cost: when a worker dies, nothing may touch the item until the lease
expires, so recovery waits out a period sized for a failure that did not
happen.

### 10.4 Stop lease renewal when the worker can no longer guarantee completion.

[REQUIRED] A worker shall cease extending ownership when it has lost
the ability to complete or safely commit the work, allowing another
worker to recover it after the lease expires. *Rationale:* Indefinitely
extending failed work prevents recovery.

### 10.5 Acknowledge queued work only after durable success.

[REQUIRED] A worker shall acknowledge or delete a queued work item
only after all required side effects for that work item have
completed successfully or have been durably committed such that recovery
can finish them. *Rationale:* Early acknowledgement converts a worker
crash into silent work loss.

## 11. Batch / Parallel Job Implementation

### 11.1 Define a finite input boundary for each batch execution.

[REQUIRED] A Batch / Parallel Job shall define the dataset, query
boundary, manifest, time window, or key range that constitutes one
logical execution. *Rationale:* A batch cannot be reasoned about,
completed, or replayed if its membership changes implicitly while it
runs.

### 11.2 Make partition assignment deterministic or persist the partition manifest.

[REQUIRED] Work shall be partitioned using deterministic boundaries or
a durably persisted manifest so that restart does not silently change
which items belong to which partition. *Rationale:* Stable membership is
required for reliable checkpointing, retry, and completeness.

### 11.3 Track each partition's outcome separately.

[REQUIRED] Each independently executed partition shall carry its own
attempt count and terminal status, distinct from the batch execution's.
*Rationale:* A batch recording only its own outcome cannot say which
partitions succeeded, so retry repeats all of them and partial failure
looks total.

### 11.4 Choose partition size to balance overhead and recovery cost.

[RECOMMENDED] Partitions should be large enough that scheduling
overhead is small relative to useful work but small enough that retrying
one failed partition does not repeat an unacceptable amount of completed
work. *Rationale:* Partition granularity is the tradeoff between
throughput efficiency and recovery precision.

### 11.5 Checkpoint only at stable commit boundaries.

[REQUIRED] A checkpoint shall be written only after all side effects
represented by that checkpoint are durably committed; a checkpoint shall
never claim progress that could be lost on immediate process
termination. *Rationale:* An optimistic checkpoint converts a crash into
skipped work.

### 11.6 Make checkpoint writes monotonic.

[REQUIRED] Checkpoint state shall advance monotonically or use
conditional versioning so that a delayed or retried worker cannot
overwrite newer progress with older progress. *Rationale:* Concurrent or
delayed attempts must not move durable progress backward.

### 11.7 Make partitions independent of one another.

[REQUIRED] Partition boundaries shall be chosen so that a partition can
be retried on its own, without rerunning another partition and without
depending on another's outcome or ordering. Work that cannot be divided
this way shall not be partitioned. *Rationale:* Independent retry is the
reason to partition at all. Partitions that share side effects or depend
on each other's order carry the full cost of fan-out while still forcing
the whole batch to be rerun when one part fails.

### 11.8 Define aggregate completion explicitly.

[REQUIRED] The batch shall define whether overall success requires all
partitions to succeed, permits a documented partial-success threshold,
or produces another explicit aggregate outcome. *Rationale:* Fan-out has
no meaningful completion semantics until fan-in defines what the
collection result means.

### 11.9 Bound fan-out concurrency.

[REQUIRED] Fan-out shall create work subject to an explicit
concurrency or dispatch limit rather than materializing unbounded
parallel work against downstream systems. *Rationale:* Partitioning
improves throughput only when parallelism remains within safe capacity.

## 12. Orchestrated Workflow Implementation

### 12.1 Persist workflow state in a durable workflow store or engine.

[REQUIRED] Orchestrated Workflow state, timers, decisions, and
completed-step history required for recovery shall be durably persisted
outside transient application memory. *Rationale:* Durable coordination
is the defining reason to use this pattern.

### 12.2 Make workflow activities independently retryable.

[REQUIRED] External side effects and remote calls shall occur inside
explicit workflow activities or equivalent units with defined timeout,
retry, and idempotency behavior rather than inside unrecoverable
orchestration logic. *Rationale:* Durable workflow replay requires side
effects to have controlled execution boundaries.

### 12.3 Keep replayed orchestration code deterministic.

[REQUIRED] Where the workflow engine executes orchestration code by
replaying it against recorded history, that code shall follow the
engine's determinism rules and shall not
directly perform nondeterministic I/O, read wall-clock time, generate
uncontrolled random values, or invoke external side effects outside
approved activity mechanisms. *Rationale:* Replay must reconstruct the
same decisions from history or workflow state becomes corrupt or
unrecoverable.

### 12.4 Define timeout and retry policy per activity.

[RECOMMENDED] Each remote or failure-prone workflow activity should define
its own execution timeout and retry policy rather than inheriting one
undifferentiated policy for the entire workflow. *Rationale:* Different
dependencies and business steps have different failure semantics.

### 12.5 Model durable waits without holding compute resources.

[RECOMMENDED] Waiting for timers, external events, approvals, or
long-running dependencies should be represented as durable workflow state
rather than a sleeping process, open thread, or open network connection.
*Rationale:* Durable waits allow long-running workflows to survive
deployment and infrastructure failure without consuming compute.

### 12.6 Define compensation for committed steps that must be undone.

[RECOMMENDED] A workflow whose later failure requires reversal of earlier
committed business effects should define the compensating action, the
conditions that invoke it, and the behavior when compensation itself
fails. *Rationale:* A saga is incomplete if its rollback path exists
only as an assumption.

### 12.7 Version workflows for in-flight compatibility.

[REQUIRED] Changes to workflow logic shall preserve correct execution
of workflows started by prior deployed versions through workflow
versioning, compatible branching, worker pinning, or an equivalent
migration strategy. *Rationale:* Long-running workflows can outlive
multiple deployments and must not reinterpret their history under
incompatible code.

### 12.8 Do not use orchestration for ordinary in-process sequencing.

[RECOMMENDED] A workflow engine should not be introduced solely to
call a few short local functions in sequence when no durable wait,
independent retry, compensation, recoverable state, or substantial
conditional branching is required. *Rationale:* Durable orchestration
has meaningful operational cost and should solve a durable-coordination
problem. Branching is one: a process whose path through many conditions
must survive a restart is coordinating state, not merely sequencing
calls.

## 13. Cancellation and Control

### 13.1 Implement cancellation cooperatively.

[REQUIRED] Cancellation shall be represented as durable intent and
observed by running work at safe interruption boundaries; forceful
process termination alone shall not be considered a complete
cancellation mechanism. *Rationale:* Killing compute does not undo
committed side effects or reliably describe the business outcome.

### 13.2 Stop accepting new child work after cancellation is accepted.

[RECOMMENDED] Once cancellation is accepted, the execution should not
create new partitions, queue items, workflow activities, or other child
work except work required to reach a safe cancelled state or perform
defined compensation. *Rationale:* Cancellation must converge toward
termination rather than continue expanding the workload.

### 13.3 Define cancellation behavior for in-flight side effects.

[RECOMMENDED] A job should define whether an in-flight operation
completes, is abandoned for retry, or is compensated when cancellation
arrives. *Rationale:* Cancellation racing with side effects is
unavoidable and requires deterministic semantics.

### 13.4 Authorize and audit every operational control.

[REQUIRED] The following are the operational controls a job may expose.
Each shall require authorization, and each use shall record the actor,
the time, the target job or execution, the parameters given, and the
outcome:

| Control | Effect |
|---|---|
| `TRIGGER` | start an execution outside its normal schedule or trigger |
| `CANCEL` | stop an execution before it reaches a terminal state |
| `RETRY` | run a failed execution again |
| `REPLAY` | run a completed execution again |
| `PAUSE` / `RESUME` | stop and restart the job taking new work |
| `DISABLE` / `ENABLE` | stop and restart the job being scheduled at all |
| `REDRIVE` | return dead-lettered work items for processing |
| `DISCARD` | delete dead-lettered work items without processing them |

No other control shall alter a job's execution or its work in a running
environment.

*Rationale:* Each of these repeats, prevents or destroys business
effect, and each is reached for by a person under pressure during an
incident — when the record of who did what is least likely to be written
and most needed. A closed list is what makes the audit checkable: an open
one leaves "equivalent controls" to be judged after the fact by whoever
built the control.

## 14. Security and Data Handling

### 14.1 Run each deployed job component with a dedicated workload identity.

[REQUIRED] Backend job components shall use non-human workload
identities, and shall not use a developer's credentials or a credential
embedded in an image, manifest or configuration file. *Rationale:*
Workload identity makes access attributable and independently revocable.

A credential read at runtime from a secret store is not embedded, and is
not forbidden here: a job that authenticates to a backend needs one, and
14.3 to 14.5 govern it. What is forbidden is a credential that travels
with the code, because it cannot be rotated without a deployment and
cannot be revoked without one either.

### 14.2 Grant least privilege to job identities.

[REQUIRED] A job identity shall receive only the resource and
operation permissions required by that job component, with write and
administrative permissions separated where practical. *Rationale:*
Background jobs can process large volumes unattended, magnifying the
impact of excessive privilege.

### 14.3 Give every job its own credential for the backends it authenticates to.

[REQUIRED] Where a job authenticates to a backend service, it shall hold
a credential issued to that job alone, distinct from and additional to
its workload identity, and shall not share one with another job or with
an application service. *Rationale:* A job normally carries two
identities — one to run as, one to call with — and only the first is
covered by 14.1. A credential shared between two jobs makes them
indistinguishable in the backend's audit log, means revoking one revokes
the other, and means rotating it for either breaks whichever was not
expecting it.

### 14.4 Keep one system of record for a credential's secret.

[REQUIRED] A credential's secret shall have exactly one authoritative
store, and any other system holding a copy shall be converged onto it
rather than written independently. The job shall read the secret at
runtime from that store. *Rationale:* A secret written in two places
diverges, and the divergence is silent until something fails to
authenticate — by which time the two writers have long since disagreed.

### 14.5 Manage a job's credential through the platform's own credential API.

[REQUIRED] A job's credential shall be created, listed, rotated and
revoked through the same interface as every other credential the platform
issues, and shall appear in the same inventory. *Rationale:* A credential
provisioned by a mechanism of its own appears in no inventory, so nobody
can answer what is able to authenticate as this platform — and the answer
is the first thing wanted in an incident. It also means a job's
credential is revocable by an operator without a deployment, which is
what makes 14.2's least privilege enforceable rather than aspirational.

### 14.6 Keep secrets out of job inputs and telemetry.

[REQUIRED] Reusable credentials, tokens, and secrets shall not be
embedded in queue messages, batch manifests, workflow state, job
definitions, logs, traces, or failure records; jobs shall resolve
secrets through the approved secret-management mechanism. *Rationale:*
Background-job artifacts are commonly persisted and replayed and
therefore are unsafe secret stores.

### 14.7 Minimize sensitive data in durable coordination state.

[REQUIRED] Queue payloads, checkpoints, workflow history, and
failed-work stores shall contain identifiers or references instead of
sensitive domain data where processing can retrieve the authoritative
data at execution time. *Rationale:* Durable coordination systems often
have broad retention and operational access and should not become
unnecessary copies of sensitive data.

## 15. Deployment and Graceful Shutdown

### 15.1 Drain a worker before terminating it.

[REQUIRED] During planned shutdown or deployment, a worker shall stop
polling, leasing, or otherwise accepting new work, and shall then be
given a finite grace period in which in-flight work can finish and
commit or relinquish ownership. *Rationale:* Draining is what separates
a normal deployment from a failure. Too short a grace period turns every
deployment into unnecessary retries; an unbounded one lets one stuck
item block the rollout indefinitely.

### 15.2 Do not record unfinished work as done.

[REQUIRED] A worker terminated before it finishes shall not acknowledge,
delete, or mark complete work it was doing but did not complete durably.
*Rationale:* Infrastructure eventually kills processes, so correctness
cannot depend on graceful shutdown always completing. Abandoning work
does not lose it — a broker holds an item until it is acknowledged, and
an unacknowledged item is redelivered. What loses work is claiming it
finished on the way out.

### 15.3 Handle work enqueued by a different code version.

[REQUIRED] A worker shall determine which version of a work item it has
been given, shall process the versions it declares support for, and
shall return a work item of any other version to the queue unprocessed
rather than interpret it under a version it was not written for.
*Rationale:* Durable work outlives the deployment that created it, and
during a rolling release two code versions consume the same queue at
once. A producer and a consumer cannot be held in step by coordination —
often neither knows the other exists — so the work item has to say what
it is. An item a worker cannot process is not bad work, it is work for a
different worker, and returning it lets one that supports the version
take it. An item no deployed worker supports stops being redelivered
when its retry budget is spent. How the version travels is a contract
and transport concern, not addressed here.

## 16. Testing and Verification

### 16.1 Test checkpoint restart for batch work.

[RECOMMENDED] Batch / Parallel Jobs using checkpoints should be tested by
terminating execution after a checkpoint and verifying that restart
neither skips uncommitted work nor repeats work outside the documented
idempotency guarantees. *Rationale:* Checkpoint correctness is defined
by restart behavior.

### 16.2 Test workflow replay and version compatibility.

[RECOMMENDED] Orchestrated Workflows should be tested for replay
determinism and for continued execution of representative in-flight
histories across workflow-code upgrades. *Rationale:* Durable workflows
fail in production when history and newly deployed code disagree.

## 17. Pattern Selection Guide

### 17.1 Select a pattern against the differentiating characteristics.

[REQUIRED] Pattern selection shall be made against the characteristics
below, and a selection that a characteristic argues against shall be
justified rather than left implicit. *Rationale:* 1.2 requires beginning
from the least complex pattern that satisfies the workload and 1.4
requires evaluating what distinguishes them; this is the comparison that
makes both answerable rather than a matter of taste, and it is what an
engineer or an AI tool reasons over when choosing.

| Requirement characteristic | Simple Job | Queued Worker | Batch / Parallel Job | Orchestrated Workflow |
|---|---|---|---|---|
| Single bounded operation | **Strong fit** | Possible | Possible | Usually excessive |
| Independent work items | Limited | **Strong fit** | Strong fit when bounded as one collection | Possible |
| Bursty / unpredictable arrival | Limited | **Strong fit** | Limited | Possible |
| Large finite dataset | Possible at small scale | Possible | **Strong fit** | Possible |
| High parallelism | Limited | Strong fit | **Strong fit** | Strong fit when workflow-driven |
| Item-level retry / isolation | Limited | **Strong fit** | Strong fit by partition/item | Strong fit by activity |
| Multi-step dependencies | Limited | Poor fit by itself | Limited | **Strong fit** |
| Durable waits / long-running state | Poor fit | Limited | Limited | **Strong fit** |
| Branching / compensation | Poor fit | Poor fit by itself | Limited | **Strong fit** |
| Whole-execution restart acceptable | **Strong fit** | Not usually relevant | Possible | Possible |
| Checkpoint / partial resume | Usually unnecessary | Per-item durability | **Strong fit** | **Strong fit** |
| Lowest operational complexity | **Strong fit** | Moderate | Moderate | Highest |

### 17.2 Prefer Simple Job until a specific requirement eliminates it.

[RECOMMENDED] A new backend job should begin as a Simple Job unless
independent buffering, substantial bounded parallelism, or durable
multi-step coordination is required. *Rationale:* Making complexity earn
its place keeps the common case inexpensive while leaving clear
escalation paths when requirements demand them.

### 17.3 Choose Queued Worker when independent work needs buffering or isolated processing.

[RECOMMENDED] Prefer Queued Worker when independent work items arrive
separately or unpredictably and require durable buffering, controlled
consumption, independent retry, or failure isolation. *Rationale:* A
durable queue is most valuable when it decouples the rate and
availability of producers from those of processors.

### 17.4 Choose Batch / Parallel Job when one bounded workload must be processed efficiently.

[RECOMMENDED] Prefer Batch / Parallel Job when the workload is finite,
aggregate completion matters, and partitioning or concurrency materially
improves throughput or recovery. *Rationale:* Batch coordination
preserves the identity of one logical workload while allowing its
data-processing work to scale horizontally.

### 17.5 Choose Orchestrated Workflow only when durable coordination is itself a requirement.

[RECOMMENDED] Prefer Orchestrated Workflow when the process contains
dependent steps, durable waits, substantial conditional branching,
compensation, or step-level recovery that must survive executor failure;
do not introduce orchestration merely to sequence a few short in-process
function calls.
*Rationale:* Workflow engines solve durable coordination exceptionally
well but impose state, operational, and conceptual overhead that simple
execution does not need.

------------------------------------------------------------------------

## 18. Kubernetes Workload Mapping

### 18.1 Use Kubernetes Job for bounded run-to-completion execution.

[REQUIRED] A Simple Job or bounded Batch / Parallel Job that starts,
performs finite work, and terminates shall normally be deployed as a
Kubernetes `Job` rather than a continuously running `Deployment`.
*Rationale:* The Kubernetes Job controller natively models
run-to-completion execution, completion status, pod replacement, bounded
retries, and parallel completions.

### 18.2 Use Kubernetes CronJob only as the scheduled trigger for bounded work.

[RECOMMENDED] Time-scheduled bounded execution should use a Kubernetes
`CronJob` that creates a Kubernetes `Job`; application containers should
not implement their own long-lived scheduler loop for routine calendar
scheduling. *Rationale:* Keeping schedule ownership in the platform
makes timing, missed starts, concurrency, history, and operational
control explicit.

### 18.3 Use Deployment for continuously consuming queued workers.

[REQUIRED] A Queued Worker that continuously polls or receives work
shall normally run as a Kubernetes `Deployment`, not as one Kubernetes
`Job` per queue item. *Rationale:* A long-running worker pool avoids
pod-creation overhead for each item and provides stable horizontal
scaling, rolling deployment, and graceful draining.

### 18.4 Process queue items with a worker pool rather than one Job per item.

[RECOMMENDED] Where a job consumes a queue, its items should be
processed by long-running worker Pods that pull from that queue. A
separate Kubernetes `Job` per item should be created only where an item
needs process-level isolation, resources unlike those of other items, or
a runtime long enough that start-up cost is negligible beside it.
*Rationale:* A `Job` per item pays a Pod's full cost — scheduling, image
pull, container start, teardown — for every message, and leaves an API
object behind for each. Where an item takes seconds, that overhead is
most of the work done. A worker pool pays those costs once per worker
instead of once per item.

### 18.5 Use indexed or completion-based Jobs for Kubernetes-native parallel batch work.

[OPTIONAL] A Batch / Parallel Job whose partitions can be
represented as a fixed completion set should use Kubernetes Job
completion/parallelism controls, including indexed completion when each
pod must deterministically know its partition identity. *Rationale:*
Native completion tracking removes custom pod coordination while
preserving stable partition identity and bounded parallelism.

### 18.6 Keep business workflow state outside Kubernetes workload objects.

[REQUIRED] An Orchestrated Workflow shall not use Kubernetes `Job`,
`Pod`, `Deployment`, annotations, or object status as the authoritative
store for business workflow state; durable workflow state shall remain
in the approved workflow engine or application persistence layer.
*Rationale:* Kubernetes workload state describes compute lifecycle, not
durable business-process history.

### 18.7 Run workflow workers as long-lived Kubernetes workloads when the workflow engine uses workers.

[RECOMMENDED] When the orchestration technology uses continuously
polling workers, those workers should be deployed as Kubernetes
`Deployment`s and scaled independently from individual workflow
instances. *Rationale:* Workflow instances are durable logical
executions and should not require one Kubernetes workload object per
workflow.

### 18.8 Do not use bare Pods for production backend jobs.

[REQUIRED] Production backend jobs shall be managed by an appropriate
Kubernetes controller such as `Job`, `CronJob`, or `Deployment`;
directly created unmanaged `Pod`s are prohibited. *Rationale:*
Controllers provide reconciliation, replacement, rollout, completion,
and lifecycle semantics that bare Pods do not.

### 18.9 Make the workload mapping explicit in deployment configuration.

[RECOMMENDED] The deployment definition should identify the execution
pattern and Kubernetes workload kind so reviewers and automation can
verify that the platform primitive matches the architecture.
*Rationale:* Explicit mapping prevents accidental use of a long-running
service primitive for bounded work or vice versa.

### 18.10 Use the following default mapping unless a documented requirement justifies an exception.

[RECOMMENDED] Deviations from this mapping should document the workload
characteristic that requires the alternative. *Rationale:* A default
mapping gives engineers and AI a safe implementation path while
preserving an escape hatch for real requirements. *Example:*

| Execution concern | Kubernetes default |
|---|---|
| Simple bounded execution | `Job` |
| Scheduled bounded execution | `CronJob` → `Job` |
| Continuous queued worker | `Deployment` |
| Fixed partitioned batch | `Job` with completions / parallelism; indexed completion when useful |
| Queue item requiring strong per-item isolation | `Job` created by a dispatcher/controller |
| Workflow worker | `Deployment` |
| Workflow durable state | Workflow engine / durable datastore, not Kubernetes object state |

## 19. Kubernetes Pod and Job Runtime Requirements

### 19.1 Set resource requests for every job container.

[REQUIRED] Every job and worker container shall define CPU and memory
`requests` based on measured or initially estimated normal consumption
and shall be tuned from observed production behavior. *Rationale:*
Kubernetes scheduling and cluster capacity planning depend on requests;
omitting them makes placement and resource availability unpredictable.

### 19.2 Set a memory limit for every job container.

[REQUIRED] Every job and worker container shall define a memory
`limit` above its expected working set with sufficient headroom for
normal peaks. *Rationale:* A bounded memory allocation prevents one
faulty or unexpectedly large job from consuming unbounded node memory.

### 19.3 Use a CPU limit to contain a runaway process.

[RECOMMENDED] A CPU limit should be set where a container's plausible
failure modes include consuming CPU without bound — a hot loop, a retry
storm, an unbounded thread pool — so that such a failure stays inside
that container rather than degrading everything sharing the node. The
limit should sit above the workload's legitimate peak so a normal burst
is not throttled. Where no runaway mode is plausible, the CPU request
alone carries the workload's guaranteed share. *Rationale:* CPU is
compressible: a container over its limit is throttled rather than
killed, so the limit is not node protection in the way a memory limit
is. It buys containment of one specific failure — a job that has begun
to spin — at the cost of capping throughput, which is why it is set for
that reason rather than by default.

### 19.4 Keep application concurrency within the pod resource envelope.

[RECOMMENDED] Worker concurrency per Pod should be configured so the
maximum expected concurrent work fits within the Pod's CPU, memory,
connection-pool, and downstream-capacity budgets. *Rationale:*
Kubernetes can enforce container resources but cannot make an
application-level concurrency setting safe automatically.

### 19.5 Use restartPolicy Never for Kubernetes Jobs by default.

[REQUIRED] Kubernetes `Job` pod templates shall use
`restartPolicy: Never` by default so a failed Pod is visible as a
distinct execution attempt; `OnFailure` may be used only when in-Pod
container restart semantics are explicitly desired and do not conflict
with attempt accounting or retry ownership. *Rationale:* `restartPolicy` governs the container within a Pod, not the
Job's retries: under `Never` the Job controller still creates a new Pod
for each attempt, so retry is unaffected. What changes is that each
attempt is a separate Pod with its own logs, rather than a container
restarted in place over the top of the previous attempt's output. Hidden
container restarts also obscure attempt identity and combine
unexpectedly with Job-level and application-level retries.

### 19.6 Set Job backoffLimit explicitly.

[REQUIRED] Every Kubernetes `Job` shall explicitly configure
`backoffLimit` or the applicable per-index retry limit rather than rely
on the platform default, and that value shall be counted within the
job's total retry budget rather than added to it. *Rationale:* Kubernetes Job retries are
part of the total retry budget and must not silently multiply
application or dependency retries.

### 19.7 Set activeDeadlineSeconds for bounded Kubernetes Jobs.

[REQUIRED] Every Kubernetes `Job` shall define `activeDeadlineSeconds`
consistent with the maximum useful execution duration of the logical
Kubernetes Job. *Rationale:* The controller needs a platform-level upper
bound so hung or pathologically slow Jobs cannot consume resources
indefinitely — and, for a scheduled Job, so that a stalled run releases
the schedule for its successor rather than holding it (20.11).

### 19.8 Use podFailurePolicy when Kubernetes-level failures require different treatment.

[OPTIONAL] Jobs that can distinguish retryable infrastructure or
disruption failures from deterministic container exit conditions should
define `podFailurePolicy` so Kubernetes does not consume retry budget on
failures known to be non-retryable or treats disruptions according to
the intended policy. *Rationale:* Failure-aware Job control avoids
wasting retries and makes Kubernetes behavior align with the
application's failure classification.

### 19.9 Set completion and parallelism explicitly for parallel Jobs.

[RECOMMENDED] Kubernetes Batch / Parallel Jobs should explicitly configure
the required completion semantics and a bounded `parallelism`;
parallelism should respect the global concurrency and
downstream-protection requirements of §8. *Rationale:* Kubernetes
parallelism is an execution control and must not become an unreviewed
source of load.

### 19.10 Configure CronJob concurrencyPolicy explicitly.

[REQUIRED] Every Kubernetes `CronJob` shall explicitly set
`concurrencyPolicy` to `Forbid`, `Replace`, or `Allow` according to the
workload's overlap semantics; relying on the default is prohibited.
`Forbid` shall be the default when concurrent runs of the same logical
schedule are not required. *Rationale:* Slow executions can otherwise
create overlapping work without an explicit architecture decision.

### 19.11 Ensure a scheduled job cannot prevent its own next run indefinitely.

[REQUIRED] Where a `CronJob` sets `concurrencyPolicy: Forbid`, its
`activeDeadlineSeconds` shall be set so that a stalled run terminates
before the following scheduled start. *Rationale:* `backoffLimit` counts
container failures and does not advance for a Pod that never starts a
container — an image that cannot be pulled, a volume that cannot mount, a
node that cannot schedule it. The Job remains active, `Forbid` then skips
every subsequent start, and the schedule stops without failing — and the
symptom is the absence of a run rather than the presence of a failure.

### 19.12 Configure missed-start behavior explicitly for CronJobs.

[RECOMMENDED] Every Kubernetes `CronJob` should set
`startingDeadlineSeconds` according to the maximum lateness at which a
missed scheduled execution remains useful, or explicitly document why
unlimited late start is correct. *Rationale:* Cluster or controller
outages eventually delay schedules, and whether late work should run is
a business semantic rather than a scheduler accident.

### 19.13 Set CronJob timezone explicitly.

[RECOMMENDED] Every Kubernetes `CronJob` should set `.spec.timeZone`;
`Etc/UTC` should be the default unless the business schedule is
intentionally tied to a named local civil timezone. *Rationale:*
Explicit timezone prevents schedule interpretation from depending on
controller configuration and makes daylight-saving behavior intentional.

### 19.14 Configure completed Job cleanup.

[RECOMMENDED] Kubernetes Jobs should define `ttlSecondsAfterFinished`, and
CronJobs should define successful and failed Job history limits,
according to operational troubleshooting and audit needs. Durable
business execution history should not depend on retaining Kubernetes Job
objects indefinitely. *Rationale:* Kubernetes object history is useful
operationally but is not the system of record and should be bounded.

### 19.15 Handle SIGTERM and Kubernetes termination explicitly.

[REQUIRED] Job and worker processes shall handle `SIGTERM`, stop
acquiring new work, begin cooperative shutdown, and exit before
`terminationGracePeriodSeconds` expires whenever safe completion is
possible. *Rationale:* Kubernetes routinely terminates Pods during
deployments, scaling, eviction, and node maintenance.

### 19.16 Size terminationGracePeriodSeconds from real drain behavior.

[RECOMMENDED] `terminationGracePeriodSeconds` should be long enough for
the workload's normal safe-stop path, including queue acknowledgement or
lease release, checkpoint persistence, and connection cleanup, but should
remain bounded. *Rationale:* The Kubernetes default is not evidence that
the application can actually drain safely within that interval.

### 19.17 Use preStop only when the application cannot begin draining directly on SIGTERM.

[OPTIONAL] Prefer application-native `SIGTERM` handling; use a
`preStop` hook only when an additional platform action is required
before termination and account for hook execution within the same
termination grace period. *Rationale:* Duplicating shutdown logic in
lifecycle hooks and application code creates ordering ambiguity and
reduces the time available for actual draining.

### 19.18 Use liveness probes only for failures a restart can correct.

[RECOMMENDED] Long-running worker `Deployment`s should use a liveness
probe only when the probe detects a condition for which restarting the
container is the correct recovery action; liveness should not fail merely
because a downstream dependency is unavailable or the queue is empty.
*Rationale:* An incorrect liveness probe can turn a dependency incident
into a restart storm.

### 19.19 Use startup probes for workers with materially slow initialization.

[OPTIONAL] A long-running worker that can legitimately require
substantial startup time should use a `startupProbe` so liveness
checking does not kill healthy initialization. *Rationale:* Startup and
runtime health are different conditions and should have different
failure windows.

### 19.20 Do not require readiness probes for non-serving bounded Jobs.

[OPTIONAL] Kubernetes `Job` Pods that do not receive Service
traffic generally should not define readiness probes; readiness is
appropriate for worker Pods only when readiness controls actual traffic
or dispatch behavior. *Rationale:* Readiness is a routing/admission
signal, not a generic indication that background work is progressing.

## 20. Kubernetes Scaling and Operations

### 20.1 Autoscale continuous workers from work demand when possible.

[RECOMMENDED] Queued Worker `Deployment`s should scale from a
work-demand signal such as queue depth, oldest-message age, or arrival
rate when the messaging platform exposes a reliable signal; CPU or
memory may supplement but should not be the sole scaling signal when
they poorly represent backlog. *Rationale:* Queue workers exist to drain
work, so scaling should respond directly to pending work and timeliness
objectives.

### 20.2 Preserve a hard maximum replica count.

[REQUIRED] Autoscaled workers shall define a maximum replica count
derived from downstream capacity and the global concurrency budget;
autoscaling shall not be allowed to exceed the safe dependency envelope.
*Rationale:* Demand-based scaling without a ceiling can amplify an
incident into dependency exhaustion.

### 20.3 Scale-to-zero only when cold-start delay satisfies the workload objective.

[OPTIONAL] Queue workers may scale to zero only when the
trigger/scaler can reliably reactivate them and cold-start plus
scheduling latency remains within the workload's trigger-to-execution
objective. *Rationale:* Cost optimization must not silently violate
processing timeliness.

### 20.4 Use PodDisruptionBudget only where maintaining continuous worker capacity matters.

[OPTIONAL] Long-running worker pools with a required minimum
processing capacity during voluntary disruptions should define a
`PodDisruptionBudget`; bounded Kubernetes Jobs generally should rely on
Job reconciliation rather than PDBs. *Rationale:* PDBs protect
availability of continuous capacity, while Jobs are naturally recreated
to reach completion.

### 20.5 Distribute critical worker replicas across failure domains.

[RECOMMENDED] Worker pools whose availability objective requires
tolerance of node or zone disruption should use topology-spread
constraints or appropriate anti-affinity so all replicas are not
concentrated in one failure domain. *Rationale:* Replica count provides
little resilience when replicas share the same infrastructure failure
boundary.

### 20.6 Use ephemeral storage deliberately.

[RECOMMENDED] Jobs that use significant local scratch space should declare
ephemeral-storage requests and limits and should not rely on
container-local files for state required after Pod loss. *Rationale:*
Local ephemeral storage is schedulable but disposable; exhausting it can
evict Pods and losing it is normal.

### 20.7 Treat Kubernetes Pod replacement as expected duplicate-execution pressure.

[RECOMMENDED] Implementations should remain correct when Kubernetes
replaces a Pod after node failure, eviction, OOM termination, failed
liveness, deployment, or Job retry and the prior attempt's final outcome
is ambiguous. *Rationale:* Kubernetes reconciliation improves
availability by replacing compute, but replacement cannot prove whether
the prior attempt committed an external side effect.

------------------------------------------------------------------------

## Glossary

| Term | Definition |
|---|---|
| **Backend Job** | Work executed outside the normal synchronous request-response path and managed as a distinct execution concern. |
| **Execution Pattern** | The architecture governing how a backend job decomposes, coordinates, executes, and recovers its work. |
| **Trigger** | The condition or mechanism that causes processing to begin; it is independent of the execution pattern. |
| **Execution** | One logical run of a job: the thing that starts, does work, and reaches a terminal state, retaining one `executionId` across its attempts. |
| **Work Item** | An independently retryable subdivision of an execution — a partition, an activity, one message. |
| **Attempt** | One try at an execution or a work item. |
| **Simple Job** | A single bounded execution requiring no durable coordination between independently managed work items. |
| **Queued Worker** | An execution model in which durable queued work items are asynchronously processed by one or more workers. |
| **Batch / Parallel Job** | A bounded logical workload processed serially or partitioned for concurrent execution. |
| **Orchestrated Workflow** | A durable execution model coordinating dependent activities, state, waits, branching, retries, and recovery. |
| **Idempotency** | The property that repeating the same logical operation does not produce an incorrect additional effect. |
| **Lease** | Time-bounded ownership of work that becomes available for recovery if the owner does not complete or renew it. |
| **Checkpoint** | Durable progress recorded only after the work it represents has been committed, allowing restart without repeating all prior work. |
| **Backpressure** | A mechanism that prevents incoming work from exceeding the rate or capacity at which it can safely be processed. |
| **Dead Letter** | Durable storage for work that exhausted automated delivery or processing attempts and requires investigation or controlled replay. |
| **Transactional Outbox** | A pattern that records an outgoing message in the same local transaction as the state change that requires it, then publishes it asynchronously. |
| **Compensation** | A business operation that semantically reverses or mitigates an earlier committed step when a later step fails. |
