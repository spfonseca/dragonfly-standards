---
shortName: ENTTL
description: >-
  How the platform records what each organization holds: the entitlement system as the runtime
  source of truth, synchronization from billing, capabilities in place of plan names, the five
  grant types, upgrade, downgrade, grace and expiry, and metering with reservations and
  reconciliation.
adoptionMetrics:
  - Share of commercial checks in code that name a capability
  - Share of plans defined as data in the plan catalog
  - Share of billing events applied to grants through the idempotent synchronization path
  - Share of metered capabilities that reserve before work and settle after it
  - Share of override grants with an issuer and an end time
impactMetrics:
  - Incidents of an organization refused a capability it had paid for
  - Incidents of an organization using a capability it had not paid for
  - Time from a purchase to the capability being usable
  - Differences found between billing and grants, and between the usage ledger and its counters
  - Deployments needed to change what a plan includes
tags: [entitlements, capabilities, grants, billing-sync, plans, trials, overrides, grace-period, metering, quota, reconciliation]
softwareLifecycle: [REQUIREMENTS_ANALYSIS, ARCHITECTURE_AND_DESIGN, IMPLEMENTATION, VERIFICATION_AND_TESTING, OPERATE_AND_SUPPORT]
solutionScope: [SOFTWARE_ARCHITECTURE, APPLICATION_COMPONENTS, APIS_AND_INTEGRATIONS, DATA_AND_PERSISTENCE, DEPENDENCIES_AND_EXTERNAL_SERVICES]
architectureQualities: [RELIABILITY, RECOVERABILITY, MODIFIABILITY, SECURITY, COMPLIANCE, OBSERVABILITY, TESTABILITY]
---

# Entitlements Standard

| Field | Value |
|---|---|
| **Short Name** | ENTTL |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-11-19 |

## Purpose

This standard governs entitlements: the platform's record of what each organization holds. It fixes
where that record lives and how it follows billing, how product function is modeled as
capabilities, the types of grant an organization can hold, what happens to grants on upgrade,
downgrade, late payment and expiry, and how metered use is counted, reserved, settled and
reconciled.

## Value Proposition

- **One answer to "has it been paid for"** — every service reads the same entitlement record, so an
  organization holds a capability everywhere or nowhere.
- **Packaging changes without code changes** — code names capabilities and plans are data, so a
  capability moves between plans without a deployment.
- **Billing can be down while customers work** — decisions read the entitlement system's own
  record, and billing is consulted only when a commercial fact changes.
- **Usage is counted once** — each usage event carries an identity and is applied once, and work in
  progress reserves quota before it starts.
- **Every exception has an owner and an end** — a grant made by staff outside a purchase is an
  override with an issuer and an end time.

## Scope

Applies to the entitlement system, to the synchronization between billing and it, and to every
service that sells, meters or checks a capability.

Whether a user is permitted an action, and whether released code is switched on, are decided by the
authorization and feature flag systems. An entitlement is a fact about an organization; which of
the organization's users may use what it holds is decided elsewhere.

## 1. Source of Truth

### 1.1 Hold what every organization holds in one entitlement system.

[REQUIRED] The entitlement system shall be the only source, at runtime, of what an organization
holds. Every service that needs that answer obtains it from the entitlement system's record.
*Rationale:* Two sources give two answers, and the customer meets the disagreement as a capability
that works on one screen and is refused on another.

### 1.2 Treat billing as the origin of commercial facts.

[REQUIRED] A purchase, renewal, cancellation or payment failure shall originate in the billing
system, and the entitlement system shall derive grants from it. The entitlement system originates
only trial and override grants. *Rationale:* The commercial arrangement is made once, in the system
that charges for it; the grants are that arrangement expressed in the terms the product checks.

### 1.3 Decide from the entitlement system's own record.

[REQUIRED] The entitlement system shall answer what an organization holds from its own stored
grants, with no call to the billing system while answering. *Rationale:* A decision is made on
every gated request, and a billing system reached on every request would add its latency and its
outages to all of them.

### 1.4 Carry facts one way, from billing to entitlements.

[REQUIRED] Synchronization shall flow from the billing system to the entitlement system. A grant
derived from billing is changed only by a further billing event; an adjustment made by staff is a
separate override grant. *Rationale:* A synchronized grant edited by hand is overwritten by the
next synchronization, and until then billing and the product disagree with no record of why.

## 2. Synchronization from Billing

### 2.1 Apply each billing event exactly once.

[REQUIRED] The entitlement system shall record the identity of every billing event it applies, and
shall apply an event whose identity it has already recorded as no change. *Rationale:* Billing
systems deliver an event more than once, and a renewal applied twice extends a grant twice.

### 2.2 Apply an organization's billing events in their order.

[REQUIRED] The entitlement system shall apply billing events for one organization in the order
billing produced them, and shall set aside an event older than the state already applied.
*Rationale:* Events arrive out of order after a retry, and a cancellation followed by a late-arriving
earlier renewal would otherwise restore what was cancelled.

### 2.3 Reflect a purchase within 60 seconds.

[REQUIRED] A grant shall be readable from the entitlement system within 60 seconds of the billing
event that causes it. *Rationale:* A customer who has just paid tries the capability at once.

### 2.4 Tell the customer when a purchase is still being applied.

[REQUIRED] A purchase flow shall confirm that the grant exists before it tells the customer the
capability is ready, and shall show that the purchase is being applied until then.
*Rationale:* A success message followed by a refusal reads as a failed purchase.

### 2.5 Reconcile grants with billing every day.

[REQUIRED] The entitlement system shall compare every organization's billing-derived grants with
the billing system's current state at least once a day, record each difference, correct the grants
to match billing, and alert the entitlement system's owner when differences are found.
*Rationale:* An event can be lost in spite of 2.1 and 2.2; the daily comparison bounds how long a
lost event leaves a customer with the wrong grants.

### 2.6 Hold an event that cannot be applied, and alert.

[REQUIRED] A billing event that cannot be applied shall be kept, with the cause, where the
entitlement system's owner can inspect and re-apply it, and shall raise an alert. The events that
follow it for the same organization wait for it. *Rationale:* A dropped event is a customer charged
for something they do not have; a kept event can be repaired and applied.

## 3. Capabilities

### 3.1 Model product function as capabilities.

[REQUIRED] Everything an organization can hold shall be a capability with a stable key, declared in
the capability catalog with its description, its owning team and the grant types it may be granted
under. *Rationale:* A capability is the unit that is sold, granted and checked; declaring it once
gives sales, billing and code the same thing to refer to.
*Example:* `bulk-import`, `diagram-export`, `ai-requests`.

### 3.2 Name capabilities in code.

[REQUIRED] Code that depends on what an organization holds shall ask whether the organization holds
a named capability. Plan names, tier names and prices appear only in the plan catalog and the
billing system. *Rationale:* Code that asks "is this the Team plan" must change every time a plan is
renamed, split or repriced; code that asks for a capability changes only when the product does.
*Example:* The import handler asks whether the organization holds `bulk-import`. The Team plan's
entry in the plan catalog lists `bulk-import` among its grants.

### 3.3 Define each plan as data.

[REQUIRED] A plan shall be an entry in the plan catalog that lists the grants an organization
receives when it buys the plan. Changing what a plan includes is a change to that entry and takes
effect without a deployment. *Rationale:* Packaging changes far more often than the product, and it
is changed by people who do not deploy code.

### 3.4 Size a capability to what can be sold on its own.

[RECOMMENDED] A capability should cover one function that could be sold, withheld or limited
independently of the others. *Rationale:* A capability that bundles two functions has to be split,
with every check on it revisited, the first time packaging separates them.

### 3.5 Form a capability's key from lowercase words joined by dashes.

[REQUIRED] A capability's key shall be lowercase words joined by dashes, shall describe the
function, and shall identify one capability for all time. *Rationale:* The key appears in code, in
the plan catalog and in audit records; a stable, descriptive key reads the same in all three.

## 4. Grant Types

### 4.1 Issue every grant as one of five types.

[REQUIRED] Every grant shall be one of these types:

| Type | What it gives | Example |
|---|---|---|
| Boolean | The capability, with no amount. | Bulk import is included. |
| Limit | The largest number of a counted thing the organization may hold at one time. | Up to 25 seats; up to 10 projects. |
| Metered | An allowance of use within a period, which renews when the period does. | 1,000 AI requests each month. |
| Trial | A capability, limit or allowance for a fixed time, at no charge. | Bulk import for 14 days. |
| Override | A capability, limit or allowance issued by staff outside a purchase. | 50 seats for a pilot, until 31 March. |

*Rationale:* These five cover how capabilities are sold and granted, and each is checked and ended
differently; a grant of a known type is handled by rules written once.

### 4.2 Record the same facts on every grant.

[REQUIRED] A grant shall record: the organization, the capability, the type, the amount and period
for a limit or metered grant, when it starts, when it ends where it has an end, and its source — the
billing reference it derives from, or the staff member who issued it. *Rationale:* These facts
answer what the organization holds, until when, and why, which is what a decision, a support case
and an audit each need.

### 4.3 Give every trial an end.

[REQUIRED] A trial grant shall carry an end time set when it is issued, and one organization shall
receive a trial of a given capability once. At its end a trial is replaced by a purchased grant or
it expires. *Rationale:* A trial is an offer of limited duration; without an end and a single use
it is a free plan.

### 4.4 Give every override an issuer and an end.

[REQUIRED] An override grant shall record the staff member who issued it and the category of the
cause — a pilot, a commercial concession, a support remedy or a correction — and shall carry an end
time. Issuing an override is an action recorded in the entitlement system's audit history.
*Rationale:* An override is an exception to what was purchased; the issuer and the end time are
what keep exceptions reviewable and temporary.

### 4.5 Resolve an organization's grants into one entitlement per capability.

[REQUIRED] The entitlement system shall compute what an organization holds for a capability from
its active grants as follows:

| Capability granted as | Entitlement |
|---|---|
| Boolean | Held when any active grant gives the capability. |
| Limit | The amount of the active override grant where one exists; otherwise the largest amount among the active grants. |
| Metered | Every active grant's remaining allowance, consumed in the order of 7.4. |

*Rationale:* An organization often holds several grants for one capability — a plan, a trial and an
override together — and a stated rule gives one answer whichever service asks.

## 5. Lifecycle

### 5.1 Decide a grant's state from its times.

[REQUIRED] A grant shall be in one of the states `SCHEDULED`, `ACTIVE`, `GRACE` or `EXPIRED`, and
the entitlement system shall determine the state from the grant's start, end and grace times at the
moment it answers. *Rationale:* A state computed from times is correct at every instant; a state
changed by a scheduled process is wrong from the moment the time passes until the process runs.

### 5.2 Apply an upgrade at once.

[REQUIRED] When an organization upgrades, the new grants shall become active as soon as the billing
event is applied, and the grants they replace shall end at the same moment. *Rationale:* The
customer has paid for more and expects it immediately.

### 5.3 Apply a downgrade at the end of the paid period.

[REQUIRED] When an organization downgrades or cancels, its current grants shall remain active until
the end of the period already paid for, and the new grants shall be scheduled to start then.
*Rationale:* The customer has paid for the current period, and the change they asked for is to the
next one.

### 5.4 Keep what an organization has when its limit falls.

[REQUIRED] When a downgrade leaves an organization holding more of a counted thing than its new
limit allows, everything it holds shall be kept and remain readable, and creating more shall be
refused until the count is within the limit. *Rationale:* Deleting a customer's data to fit a plan
is irreversible, and refusing additions enforces the limit without it.
*Example:* An organization with 14 projects moves to a plan with a limit of 10. All 14 projects
remain and can be read. Creating another project is refused until the organization holds fewer
than 10.

### 5.5 Continue grants through a grace period after a failed payment.

[REQUIRED] When a renewal payment fails, the grants it would have renewed shall enter `GRACE` and
continue to be honored for the grace period the plan catalog states. A successful payment during
grace returns them to `ACTIVE`; at the end of grace they become `EXPIRED`. *Rationale:* Most failed
payments are a card that needs replacing; grace gives the customer time to fix it while they keep
working.

### 5.6 Tell the organization before a grant ends.

[REQUIRED] The organization's billing administrators shall be told before a trial ends, when a
payment fails, and before a grace period ends. *Rationale:* A capability that stops without warning
is a support case; a warning turns most of them into a payment.

### 5.7 Keep every change to a grant as history.

[REQUIRED] The entitlement system shall keep every creation of and change to a grant as an
append-only history entry, with the time and the billing event or staff member that caused it.
*Rationale:* "What did this organization hold on that date, and why" is asked in every billing
dispute, and only a history answers it.

## 6. Answering Entitlement Questions

### 6.1 Answer what an organization holds within 5 milliseconds.

[REQUIRED] The entitlement system shall answer whether an organization holds a capability, and with
what limit or remaining allowance, within 5 milliseconds at the 99th percentile. *Rationale:* The
question is asked on every gated request.

### 6.2 Announce every change to what an organization holds.

[REQUIRED] The entitlement system shall announce each change to an organization's entitlement, so
that components holding a copy of the earlier answer can discard it. *Rationale:* An upgrade takes
effect for the customer only when every holder of the old answer has let it go.

### 6.3 Let an organization read what it holds and what it has used.

[REQUIRED] The entitlement system shall let an organization's administrators read the
organization's grants, limits, current counts, and usage against each metered allowance with the
time the allowance renews. *Rationale:* A customer who can see their usage plans around a limit; one
who cannot learns of it when they are refused.

## 7. Metering

### 7.1 Record usage in an append-only ledger.

[REQUIRED] Every use of a metered capability shall be recorded as an entry in a usage ledger that
is only ever added to. The ledger is the record of usage, and every counter and remaining balance
is derived from it. *Rationale:* A counter alone cannot show how it reached its value; the ledger
can be re-added to check a counter and to answer a dispute.

### 7.2 Give every usage event an idempotency key.

[REQUIRED] Every usage event shall carry a key that identifies the unit of work it reports, and the
metering system shall apply a second event with the same key as no change. *Rationale:* A service
that retries after a timeout reports the same work twice, and the customer must be charged for it
once.

### 7.3 Reserve before the work, and settle after it.

[REQUIRED] A service shall reserve the amount a unit of work is expected to use before it starts
the work, and shall settle the reservation with the amount actually used when the work succeeds, or
release it when the work fails. A reservation neither settled nor released is released when its
lifetime, 15 minutes unless the capability's declaration states another, has passed.
*Rationale:* Checking the balance and deducting later lets many concurrent requests each see the
same remaining allowance and together exceed it; a reservation holds each request's share from the
moment it is admitted.
*Example:* A report is expected to use 40 AI requests. The service reserves 40, the report uses 31,
and the service settles 31; the other 9 return to the allowance.

### 7.4 Consume grants in a fixed priority.

[REQUIRED] When an organization holds several metered grants for one capability, usage shall be
taken from them in this order: the grant that ends soonest first; among grants ending together,
trial and override grants before purchased ones; then the grant issued earliest.
*Rationale:* Allowance that is about to end is lost if it is not used first, and free allowance
spent before paid allowance is what the customer expects.

### 7.5 Enforce a limit atomically.

[REQUIRED] The check that a limit or allowance has room and the reservation against it shall be one
atomic operation. *Rationale:* Two requests that each check and then each reserve both pass the
check, and the limit is exceeded by one.

### 7.6 Renew allowances on the organization's billing anchor.

[REQUIRED] A metered allowance's period shall start and end at the organization's billing anchor,
held in UTC, and unused allowance ends with the period unless the grant states that it carries
over. *Rationale:* The customer's allowance renews with their invoice, and one stated time zone
gives every service the same boundary.

### 7.7 Reconcile counters with the ledger every day.

[REQUIRED] The metering system shall recompute each organization's usage from the ledger at least
once a day, compare it with the counters used for decisions, record each difference, and alert the
metering system's owner when a difference is found. *Rationale:* Counters are updated on the request
path where failures are tolerated for speed, and they drift; the ledger is what they are corrected
to.

### 7.8 Correct usage with a new ledger entry.

[REQUIRED] A correction to recorded usage shall be a new ledger entry that states the adjustment
and its cause. Existing entries stay as written. *Rationale:* The ledger supports billing; a history
that has been edited cannot show what the customer was charged for.

### 7.9 Settle usage recorded while metering was unreachable.

[REQUIRED] A service that performed metered work while the metering system could not be reached
shall keep the usage durably and report it, with its idempotency key, when the metering system
answers again. *Rationale:* The work was done and is owed to the ledger; the key ensures the late
report counts once.

## Glossary

| Term | Definition |
|---|---|
| **Allowance** | The amount of use a metered grant gives within one period. |
| **Billing anchor** | The time in each period at which an organization's billing period, and with it its allowances, renews. |
| **Capability** | A named unit of product function that an organization can hold and a user can exercise, identified by a stable key that carries no plan name or price. |
| **Capability catalog** | The list of every capability, with its key, description, owning team and grant types. |
| **Entitlement** | The record of what an organization holds for a capability, made up of the organization's active grants. |
| **Grace period** | The time after a failed payment during which the affected grants continue to be honored. |
| **Grant** | One issued right of an organization to a capability. |
| **Idempotency key** | A value that identifies one unit of work, so that a repeated report of it is applied once. |
| **Limit** | The largest number of a counted thing an organization may hold at one time. |
| **Metered grant** | A grant of an allowance of use within a period. |
| **Organization** | The customer account that users belong to and that grants are issued to. |
| **Override** | A grant issued by staff outside a purchase, with an issuer and an end time. |
| **Plan** | A named set of grants sold together, defined as an entry in the plan catalog. |
| **Plan catalog** | The data that lists, for each plan, the grants an organization receives. |
| **Quota** | The amount a limit or a metered allowance leaves available to an organization. |
| **Reconciliation** | Comparing two records of the same facts, recording the differences and correcting the derived one. |
| **Reservation** | Quota held for an action that is in progress, later settled with the amount used or released. |
| **Seat** | One user's assigned place in a capability sold by number of users. |
| **Trial** | A grant of a capability for a fixed time at no charge. |
| **Usage ledger** | The append-only record of every use of a metered capability. |
