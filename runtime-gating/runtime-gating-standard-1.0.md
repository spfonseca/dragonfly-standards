---
shortName: RGATE
description: >-
  How a service decides, when a user acts, whether the action proceeds: one decision facade and
  call contract, the order checks run in, the fixed reasons a refusal carries, what each check does
  when it cannot answer, caching, latency, audit records, and how a new check is added.
adoptionMetrics:
  - Share of gated actions decided through the decision facade
  - Share of gated actions with a declaration naming their capability and applicable check types
  - Share of check types with a complete declaration
  - Share of refusals returned to clients that carry a reason from the fixed set
  - Share of check types whose failure posture is exercised by a test
impactMetrics:
  - Incidents of an action proceeding that a check would have refused
  - Incidents of users refused because a check system was unreachable
  - Support contacts in which the user could not tell why an action was refused
  - Quota consumed by requests that were then refused
tags: [gating, decision-facade, feature-flags, entitlements, authorization, kill-switch, quota, denial-reasons, fail-closed, audit]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, IMPLEMENTATION, VERIFICATION_AND_TESTING, OPERATE_AND_SUPPORT]
solutionScope: [SOFTWARE_ARCHITECTURE, APIS_AND_INTEGRATIONS, IDENTITY_AND_ACCESS, SECURITY_CONTROLS, USER_INTERFACES]
architectureQualities: [SECURITY, RELIABILITY, RESILIENCE, PERFORMANCE, USABILITY, OBSERVABILITY, EXTENSIBILITY, TESTABILITY]
---

# Runtime Gating Standard

| Field | Value |
|---|---|
| **Short Name** | RGATE |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-11-19 |

## Purpose

This standard governs the decision a service makes at the moment a user acts: whether the action
proceeds. Feature flags, entitlements and authorization are separate systems with separate owners,
and each answers one part of that question. This standard fixes how their answers are obtained
through one decision facade, the order in which they are asked, the reason a refusal carries, what
happens when a system cannot answer, and how a further check joins them.

## Value Proposition

- **One place decides** — every gated action is decided by the same component, so the same
  situation produces the same decision in every service and on every screen.
- **A refusal says why** — each refusal carries one reason from a fixed set, and each reason has one
  HTTP status and one user-interface treatment, so the user is shown the step that resolves it.
- **An outage has a planned outcome** — each check type declares what the facade does when its
  system cannot answer, so an unreachable system produces the declared behavior.
- **Quota is spent only on work that proceeds** — quota is consumed after every other check has
  allowed the action, so a refused request uses none.
- **New checks join without rewrites** — a check type is added to the facade through one process,
  and the services that call the facade stay as they are.

## Scope

Applies to every service and user interface that decides whether a user or machine account may take
an action on the platform, and to the decision facade itself.

A gating decision is the decision whether an action proceeds. A flag read that selects between two
implementations of a capability the subject already has, or that supplies a configuration value, is
a behavior choice and is made by reading the flag directly.

The internal rules of each check system — how a flag is targeted, how a grant is issued, how a
permission is modeled — belong to that system's owner. This standard states what the facade
requires of each system's answer.

## 1. The Decision Facade

### 1.1 Decide every gated action through one decision facade.

[REQUIRED] A service shall obtain the decision for every gated action from the platform's decision
facade. The facade shall be the only component that asks the feature flag, entitlement,
authorization and other check systems for the answers that make up a gating decision.
*Rationale:* One component that composes the checks applies the same order, reasons and failure
behavior to every action. Call sites that compose their own checks drift apart one at a time.
*Example:* The export handler asks the facade whether the user may take `diagram.export` on
diagram D, and acts on the answer. The handler contains no flag read, entitlement lookup or
permission query for that decision.

### 1.2 Use one call contract for every decision.

[REQUIRED] A request to the facade shall carry the action's key, the resource's type and id when
the action targets a resource, the amount when the action consumes quota, and the mode
(`ADVISE` or `ENFORCE`). The response shall carry `allowed`, one `reason`, `retryAfter` when the
refusal has a known end, and `reservationId` when quota was reserved. The response has the same
shape whichever check types ran. *Rationale:* A caller written against one contract needs no change
when a check type is added, removed or reordered.
*Example:* Request: `{"action": "diagram.export", "resource": {"type": "diagram", "id": "7f3a…"}, "mode": "ENFORCE"}`.
Response: `{"allowed": false, "reason": "NOT_ENTITLED"}`.

### 1.3 Take the subject from the authenticated identity.

[REQUIRED] The facade shall take the user or machine account, and the organization it acts in, from
the request's verified token. *Rationale:* A subject named in a request body or header is whatever
the caller typed; the token is what the identity provider verified.

### 1.4 Separate advisory decisions from enforcing decisions.

[REQUIRED] The facade shall offer two modes. An `ADVISE` decision tells a user interface what to
render; it consumes no quota and reserves nothing. An `ENFORCE` decision is requested by the service
that performs the action, immediately before it performs it; it reserves quota and is recorded.
*Rationale:* A screen asks about many actions the user never takes. Only the decision made when the
action runs may spend quota or stand as the record of what was allowed.

### 1.5 Enforce in the service that performs the action.

[REQUIRED] The service that performs a gated action shall request an `ENFORCE` decision for every
request, including a request for a file or download reached by a link. *Rationale:* A user
interface can be bypassed and a link can be shared; the service performing the action is the last
point that sees every request.
*Example:* The download endpoint for an exported file requests an `ENFORCE` decision on each fetch,
then returns a short-lived signed address for the file.

### 1.6 Answer many advisory decisions in one call.

[RECOMMENDED] The facade should accept a list of actions in one `ADVISE` request and return one
decision for each. *Rationale:* A screen holds many gated controls, and one round trip for all of
them keeps the screen's load time independent of their number.

### 1.7 Return the decision and its reason only.

[REQUIRED] A response that reaches a client shall carry the decision fields of 1.2 and nothing
else: role assignments, grant records, plan details and flag rules stay on the server.
*Rationale:* The client needs to know what to render; the facts behind the decision describe the
organization's commercial and access arrangements and are held where they are protected.

## 2. Check Types

### 2.1 Keep each check type in its own system under its own owner.

[REQUIRED] The feature flag system, the entitlement system, the authorization system and each
further check system shall hold their own data and rules, each under one owning team. The facade
shall hold the evaluation order and the declarations of section 2, and shall keep check answers only
as cache entries. *Rationale:* Each question changes for different causes — a rollout, a purchase, a
role assignment — and a team that owns one question can change its answer without touching the
others.

### 2.2 Declare every check type.

[REQUIRED] Each check type shall have a declaration held with the facade that states: its name, its
owning team, the question it answers, what the answer is about (the organization, the user, the
resource or the session), its position in the evaluation order, the reasons it returns, its failure
posture, its cache lifetime, its latency budget and the fields it adds to an audit record.
*Rationale:* The declaration is what the facade is built and tested against, and what a reviewer
reads to learn how a check behaves.

### 2.3 Declare every gated action.

[REQUIRED] Each gated action shall have a declaration that states its key, the capability it
belongs to, the check types that apply to it, the quota it consumes and whether it is sensitive.
The facade shall refuse an action that has no declaration, with the reason `NOT_AUTHORIZED`, and
record the request as a defect. *Rationale:* An action without a declaration has no agreed checks,
and refusing it makes the omission visible the first time the action is exercised.

### 2.4 Apply account standing and authorization to every gated action.

[REQUIRED] The account standing check and the authorization check shall apply to every gated
action. The kill switch check shall apply to every action of a capability that has a kill switch.
The remaining check types apply to the actions whose declarations name them. *Rationale:* Whether
the organization may use the platform and whether the user may do this are questions every action
has; the others depend on how the capability is sold and governed.

## 3. Evaluation Order

### 3.1 Evaluate the check types in one fixed order.

[REQUIRED] The facade shall evaluate the check types that apply to an action in this order:

| Position | Check type | Question |
|---|---|---|
| 1 | Kill switch | Is the capability switched on for everyone? |
| 2 | Account standing | Is the organization in good standing? |
| 3 | Entitlement | Does the organization hold the capability? |
| 4 | Organization admin policy | Has the organization's administrator left the capability on for this user? |
| 5 | Seat assignment | Does the user hold a seat for the capability? |
| 6 | Authorization | May the user take this action on this resource? |
| 7 | Consent and compliance | Have the required terms been accepted, and do the compliance conditions hold? |
| 8 | Risk and step-up | Is the session's authentication strong and recent enough for this action? |
| 9 | Approval gate | Has the approval this action needs been given? |
| 10 | Release and experiment flags | Is the capability released to this subject? |
| 11 | Quota | Is there quota left for this amount? |

*Rationale:* A fixed order gives every user in the same situation the same reason. The order runs
from questions about the capability and the organization, through questions about the user and the
resource, to questions about this one request.

### 3.2 Stop at the first refusal and report its reason.

[REQUIRED] The facade shall stop at the first check that refuses and return that check's reason.
*Rationale:* The first refusal in the order is the one the user must resolve first, and later checks
would spend time on a request that is already refused.
*Example:* A user without permission, in an organization that has not purchased the capability,
acts while the capability's kill switch is off. The facade returns `SWITCHED_OFF`.

### 3.3 Allow an action only when every applicable check allows it.

[REQUIRED] The facade shall return `allowed: true` only when every check type that applies to the
action has allowed it. One check's allowance carries no weight in another check: a flag that is on
leaves the entitlement check's refusal in force, and an entitlement that is held leaves the
authorization check's refusal in force. *Rationale:* Each system answers one question and has no
knowledge of the others; an action is safe to perform when all of them agree.

### 3.4 Let the kill switch decide before every other check.

[REQUIRED] When a capability's kill switch is off, the facade shall refuse every action of that
capability for every subject, including subjects holding an override grant and platform staff.
*Rationale:* A kill switch is used to stop a capability during an incident, and it does that only
when no other check can let a request through.

### 3.5 Keep the checks before authorization independent of the resource.

[REQUIRED] The checks at positions 1 to 5 shall decide from the capability, the organization and
the user alone, and shall read nothing about the resource. The authorization check shall return
`NOT_FOUND` when the subject may not see the resource. *Rationale:* A refusal that depends on the
resource confirms the resource exists. With the earlier checks independent of the resource, a hidden
resource and a missing one receive the same answer.

### 3.6 Consume quota last, and only when enforcing.

[REQUIRED] The facade shall reserve quota only in an `ENFORCE` decision and only after every other
applicable check has allowed the action. An `ADVISE` decision reads the remaining quota and reserves
nothing. *Rationale:* Quota spent on a request that is then refused is quota the customer paid for
and did not receive.

### 3.7 Settle or release every reservation.

[REQUIRED] A service that receives a `reservationId` shall report the outcome of the action: it
settles the reservation with the amount actually used when the action succeeds, and releases it
when the action fails. A reservation with no reported outcome is released when its declared lifetime
ends. *Rationale:* The reservation holds quota for work in progress; reporting the outcome is what
turns the held amount into the used amount or returns it.

### 3.8 Evaluate checks concurrently only where the reported reason is unchanged.

[OPTIONAL] The facade may evaluate several checks at the same time, provided it returns the reason
of the refusing check that stands earliest in the order and reserves quota only after every other
check has allowed the action. *Rationale:* Concurrent evaluation shortens the decision; the order
remains what determines the reason and when quota is spent.

## 4. Reasons

### 4.1 Return exactly one reason from the fixed set.

[REQUIRED] Every decision shall carry exactly one of these reasons:

| Reason | Returned by | Meaning |
|---|---|---|
| `ALLOWED` | The facade | Every applicable check allowed the action. |
| `UNAUTHENTICATED` | The facade | The request carries no verified identity. |
| `SWITCHED_OFF` | Kill switch | The capability is switched off for everyone. |
| `ACCOUNT_SUSPENDED` | Account standing | The organization is suspended or closed. |
| `NOT_ENTITLED` | Entitlement | The organization does not hold the capability. |
| `DISABLED_BY_ORGANIZATION` | Organization admin policy | The organization's administrator has turned the capability off for this user. |
| `NO_SEAT` | Seat assignment | The user holds no seat for the capability. |
| `NOT_AUTHORIZED` | Authorization | The user may see the resource and may not take this action on it. |
| `NOT_FOUND` | Authorization | The resource does not exist, or the user may not see it. |
| `CONSENT_REQUIRED` | Consent and compliance | Required terms are unaccepted, or a compliance condition is unmet. |
| `STEP_UP_REQUIRED` | Risk and step-up | The action needs stronger or more recent authentication. |
| `APPROVAL_REQUIRED` | Approval gate | The action needs an approval that has not been given. |
| `NOT_RELEASED` | Release and experiment flags | The capability is not released to this subject. |
| `LIMIT_REACHED` | Quota | The organization holds as many of the counted thing as its limit allows. |
| `QUOTA_EXHAUSTED` | Quota | The organization has used its allowance for the current period. |
| `CHECK_UNAVAILABLE` | The facade | A check that refuses when it cannot answer could not answer. |

*Rationale:* A fixed set lets every client map a refusal to a treatment once, and lets support and
audit count refusals by cause.

### 4.2 Map each reason to one HTTP status.

[REQUIRED] A service that refuses a request on the facade's decision shall answer with the status
below and carry the reason in the error body:

| Reason | HTTP status |
|---|---|
| `UNAUTHENTICATED`, `STEP_UP_REQUIRED` | 401 |
| `ACCOUNT_SUSPENDED`, `NOT_ENTITLED`, `DISABLED_BY_ORGANIZATION`, `NO_SEAT`, `NOT_AUTHORIZED`, `CONSENT_REQUIRED`, `APPROVAL_REQUIRED`, `LIMIT_REACHED` | 403 |
| `NOT_FOUND`, `NOT_RELEASED` | 404 |
| `QUOTA_EXHAUSTED` | 429 |
| `SWITCHED_OFF`, `CHECK_UNAVAILABLE` | 503 |

*Rationale:* The status tells a generic client the class of failure — authenticate, give up, or try
again later — and the reason tells a client written for the platform which treatment to show.

### 4.3 Give each reason one user-interface treatment.

[REQUIRED] A user interface shall treat each reason as follows:

| Reason | Treatment |
|---|---|
| `ALLOWED` | The control is shown and enabled. |
| `UNAUTHENTICATED` | The user is taken to sign in, and returned to the action afterwards. |
| `SWITCHED_OFF` | The control is shown disabled with a notice that the feature is temporarily unavailable. |
| `ACCOUNT_SUSPENDED` | A notice names the suspension; a billing administrator is given the path to resolve it. |
| `NOT_ENTITLED` | The control is shown disabled; a user who may purchase is offered the purchase, and any other user is told to ask an administrator. |
| `DISABLED_BY_ORGANIZATION` | The control is shown disabled with a notice that the organization's administrator has turned the feature off. |
| `NO_SEAT` | The control is shown disabled with the path to request a seat. |
| `NOT_AUTHORIZED` | The control is shown disabled with a notice that the user's role does not include the action. |
| `NOT_FOUND` | The user interface behaves as it does for a missing resource. |
| `CONSENT_REQUIRED` | The terms are presented for acceptance, and the action is retried once they are accepted. |
| `STEP_UP_REQUIRED` | The user is asked to authenticate again, and the action is retried afterwards. |
| `APPROVAL_REQUIRED` | The user is offered a request for approval, or shown that one is pending. |
| `NOT_RELEASED` | The control is absent. |
| `LIMIT_REACHED` | The limit and the current count are shown, with the path to raise the limit. |
| `QUOTA_EXHAUSTED` | The usage and the time the allowance renews are shown, with the path to add more. |
| `CHECK_UNAVAILABLE` | The user is told the action cannot be completed at the moment and may be retried. |

*Rationale:* One treatment per reason means a user who meets the same refusal on two screens is
shown the same next step.

### 4.4 Send `retryAfter` where the refusal has a known end.

[REQUIRED] A decision with the reason `QUOTA_EXHAUSTED` shall carry `retryAfter` set to the time
the allowance renews, and a decision with the reason `CHECK_UNAVAILABLE` shall carry `retryAfter`
set to the time the facade will next attempt the check. The service shall send the same value in the
response's `Retry-After` header. *Rationale:* A client that knows when the refusal ends waits that
long and retries once.

### 4.5 Treat an unrecognized reason as a refusal.

[REQUIRED] A client that receives a reason it does not recognize shall treat the decision as a
refusal and show the treatment for `CHECK_UNAVAILABLE` without the offer to retry. *Rationale:* The
set grows when a check type is added, and a client released before the addition must still refuse.

## 5. Failure Posture

### 5.1 Declare what the facade does when each check type cannot answer.

[REQUIRED] Each check type shall have one of the failure postures below, and the facade shall apply
it when the check's system is unreachable, times out or returns an error:

| Check type | When the check cannot answer |
|---|---|
| Kill switch | The facade uses the last value it received. When it has never received one, the capability is treated as switched on. |
| Account standing | The facade uses the last standing it received, for up to 24 hours, and refuses after that. |
| Entitlement | The facade uses the last entitlement it received, for up to 24 hours, and refuses after that. |
| Organization admin policy | The facade uses the last policy it received, for up to 1 hour, and refuses after that. |
| Seat assignment | The facade uses the last assignment it received, for up to 1 hour, and refuses after that. |
| Authorization | The facade refuses. |
| Consent and compliance | The facade refuses. |
| Risk and step-up | The facade requires step-up. |
| Approval gate | The facade refuses. |
| Release and experiment flags | The facade uses the last value it received. When it has never received one, it uses the flag's safe default. |
| Quota, limit grant | The facade refuses. |
| Quota, metered grant | The facade allows the action and records the amount durably, and the amount is settled when the metering system answers again. |

*Rationale:* Checks that protect data and consent refuse, because an action wrongly allowed there
cannot be taken back. Checks that reflect a commercial arrangement continue on the last known
answer for a bounded time, because a paying customer stopped by an outage is the larger harm, and
the bound ensures a lapse is enforced once it ends.

### 5.2 Bound every check with a timeout.

[REQUIRED] The facade shall give each check a timeout of at most twice the check type's latency
budget, and shall apply the check type's failure posture when the timeout passes. *Rationale:* A
check that never answers holds the user's request open; the timeout converts a slow system into the
declared posture.

### 5.3 Report `CHECK_UNAVAILABLE` when a refusing posture applies.

[REQUIRED] When the facade refuses because a check could not answer, it shall return
`CHECK_UNAVAILABLE`. The check's own refusal reason is returned only when the check answered and
refused. *Rationale:* A user told "not authorized" during an outage asks an administrator for access
they already have; `CHECK_UNAVAILABLE` tells them to try again.

### 5.4 Record and alert on every decision made under a failure posture.

[REQUIRED] The facade shall record each decision made under a failure posture, naming the check
type, and shall raise an alert to the check type's owning team when such decisions continue for
longer than one minute. *Rationale:* A decision made on a last known answer may be wrong, and the
record is what lets the owner find and review those decisions afterwards.

### 5.5 Test each check type's failure posture.

[REQUIRED] The facade's tests shall make each check system unreachable in turn and assert the
decision, the reason and the record that section 5 requires. *Rationale:* The posture is used only
during an outage, and an untested posture is discovered to be wrong during one.

## 6. Caching

### 6.1 Cache a check's answer no longer than its declared lifetime.

[REQUIRED] The facade shall keep a check's answer for at most the lifetime below:

| Check type | Longest cache lifetime |
|---|---|
| Kill switch | 30 seconds |
| Account standing | 60 seconds |
| Entitlement | 60 seconds |
| Organization admin policy | 60 seconds |
| Seat assignment | 60 seconds |
| Authorization | The lifetime the authorization system's owner declares |
| Consent and compliance | 60 seconds |
| Risk and step-up | Evaluated on every decision |
| Approval gate | Evaluated on every decision |
| Release and experiment flags | 60 seconds |
| Quota | Evaluated on every decision |

*Rationale:* The lifetime is how long a change in the owning system can go unseen. It is short where
a change must take effect quickly and zero where the answer belongs to one request.

### 6.2 Keep a composed decision no longer than its shortest-lived input.

[REQUIRED] Where the facade caches a whole decision, it shall keep it no longer than the shortest
cache lifetime among the check types that produced it. *Rationale:* A cached decision is as stale as
its stalest input.

### 6.3 Key every cached answer by organization and subject.

[REQUIRED] A cached answer shall be keyed by the organization, the user where the answer is about
the user, the action, and the resource where the answer is about the resource. *Rationale:* An
answer returned for a different organization or user is an access defect.

### 6.4 Drop cached answers when the owning system announces a change.

[RECOMMENDED] The facade should remove a cached answer when the check's system announces that the
underlying fact changed. *Rationale:* An announced change takes effect at once, and the cache
lifetime becomes the bound for the case where the announcement is lost.

### 6.5 Limit a client's cache of advisory decisions to 60 seconds.

[REQUIRED] A client shall keep an `ADVISE` decision for at most 60 seconds, and shall discard every
cached decision when the user signs out or changes the organization they act in. *Rationale:*
Advisory decisions drive what is rendered; a short lifetime keeps the screen close to what the
server will enforce.

## 7. Latency Budgets

### 7.1 Hold an enforcing decision to 100 milliseconds.

[REQUIRED] The facade shall return an `ENFORCE` decision within 100 milliseconds at the 99th
percentile and 25 milliseconds at the median, measured at the facade. *Rationale:* The decision is
added to every gated request, so its latency is part of every such request's latency.

### 7.2 Give every check type a budget inside the total.

[REQUIRED] Each check type shall answer within its budget at the 99th percentile:

| Check type | Budget |
|---|---|
| Kill switch, release and experiment flags | 1 millisecond each |
| Account standing | 5 milliseconds |
| Entitlement | 5 milliseconds |
| Organization admin policy | 5 milliseconds |
| Seat assignment | 5 milliseconds |
| Authorization | 20 milliseconds |
| Consent and compliance | 5 milliseconds |
| Risk and step-up | 10 milliseconds |
| Approval gate | 5 milliseconds |
| Quota reservation | 15 milliseconds |

*Rationale:* A total budget is met only when each part has its own, and a part's budget is what its
owner designs and measures against.

### 7.3 Measure and publish each check type's latency.

[REQUIRED] The facade shall measure each check type's latency and each decision's total latency,
and publish both against their budgets. A check type that exceeds its budget is a defect for its
owning team. *Rationale:* The measurement names the check that is slow, so the team that can fix it
is the team that is told.

### 7.4 Answer a batch of advisory decisions within 150 milliseconds.

[RECOMMENDED] The facade should return an `ADVISE` request of up to 50 actions within 150
milliseconds at the 99th percentile. *Rationale:* The batch is requested while a screen loads, and
its latency delays everything the screen gates.

## 8. Audit Logging

### 8.1 Record every enforcing refusal and every enforcing decision on a sensitive action.

[REQUIRED] The facade shall write an audit record for every `ENFORCE` decision that refuses, and
for every `ENFORCE` decision, allowed or refused, on an action whose declaration marks it
sensitive. Allowed decisions on other actions are counted in metrics. *Rationale:* Refusals and
sensitive actions are what an investigation asks about; counting the rest keeps the log's volume in
proportion to its use.

### 8.2 Record the same fields for every decision.

[REQUIRED] An audit record shall carry: the time, the request id, the user or machine account id,
the organization id, the action, the resource's type and id, the mode, whether the action was
allowed, the reason, the check type that decided, the identifier or version of the fact it decided
on (the flag's version, the grant's id, the authorization model's version), and whether a failure
posture applied. *Rationale:* These fields answer who was refused what, when, by which check, and on
which version of the facts, which is what reproducing a decision requires.

### 8.3 Identify people by id only.

[REQUIRED] An audit record shall identify users and organizations by id, and shall carry no name,
email address or request payload. *Rationale:* The record is kept for a long time and read by
operators; ids let an authorized reader look the person up while the log itself holds no personal
detail.

### 8.4 Keep audit records append-only.

[REQUIRED] Audit records shall be written once and never changed, and shall be kept for at least
one year. *Rationale:* A record that can be edited cannot settle a dispute about what was decided.

### 8.5 Sample advisory decisions for diagnosis.

[OPTIONAL] The facade may record a sample of `ADVISE` decisions in its diagnostic logs.
*Rationale:* A sample is enough to diagnose a screen that renders the wrong controls, and advisory
decisions are too numerous to record in full.

## 9. Further Check Types

### 9.1 Check account standing for the organization as a whole.

[REQUIRED] The account standing check shall answer from the organization's standing, which is one
of `ACTIVE`, `SUSPENDED` or `CLOSED`, and shall refuse with `ACCOUNT_SUSPENDED` for the last two.
Actions an administrator needs in order to restore standing or to leave — viewing and paying
invoices, exporting the organization's data — shall be declared exempt from this check. A late
payment alone leaves standing `ACTIVE`; the entitlement system's grace period governs it.
*Rationale:* Standing is a decision about the whole organization, taken for non-payment past grace,
abuse or a legal hold. The exempt actions are the ones that resolve it.

### 9.2 Let an organization's administrator narrow what the organization holds.

[REQUIRED] The organization admin policy check shall answer from the policy the organization's
administrator has set, which turns a capability off for the whole organization or for named groups
of its users, and shall refuse with `DISABLED_BY_ORGANIZATION`. A policy narrows what the
organization's entitlement provides and adds nothing to it. *Rationale:* An organization governs
its own users' use of what it has bought; what it has bought is the entitlement system's fact.

### 9.3 Check that the user holds a seat for a capability sold by seat.

[REQUIRED] For a capability sold by seat, the seat assignment check shall answer whether the user
holds an assigned seat, and shall refuse with `NO_SEAT`. The number of seats is the organization's
limit for that capability, and the action that assigns a seat is itself a gated action that consumes
that limit through the quota check. *Rationale:* The organization buys a number of seats and its
administrator decides who holds them; the two facts change separately and are checked separately.

### 9.4 Check consent and compliance against current versions.

[REQUIRED] The consent and compliance check shall answer whether the user, or the organization
where the terms bind the organization, has accepted the current version of each set of terms the
action's declaration names, and whether each compliance condition it names holds. It shall refuse
with `CONSENT_REQUIRED`. A new version of the terms makes earlier acceptances insufficient for the
actions that name them. *Rationale:* Consent is given to a specific text; when the text changes, the
earlier consent covers the earlier text.

### 9.5 Compare the session's authentication with what the action requires.

[REQUIRED] An action's declaration shall state the authentication strength and the recency it
requires, where it requires more than a signed-in session. The risk and step-up check shall compare
these with the authentication facts in the request's token, and refuse with `STEP_UP_REQUIRED`. The
client authenticates the user again and repeats the same request. *Rationale:* A session established
hours ago by password alone is weaker evidence of who is acting than the action may need, and
re-authentication supplies that evidence at the moment it matters.

### 9.6 Bind an approval to one subject, action and resource.

[REQUIRED] For an action whose declaration requires approval, the approval gate check shall answer
whether an approval record exists that names this subject, this action and this resource, has not
expired and has not been used, and shall refuse with `APPROVAL_REQUIRED`. An `ENFORCE` decision
that passes marks the approval used. The approver is a different user from the requester.
*Rationale:* An approval is consent to one specific act by one specific person; binding and
single use keep it from covering any other.

## 10. Adding a Check Type

### 10.1 Propose a new check type with a complete declaration.

[REQUIRED] A proposal for a new check type shall contain the declaration of 2.2 in full, the reason
for its position in the evaluation order, and one scenario in which the check refuses an action
every existing check allows. *Rationale:* The scenario shows the check answers a question nothing
else answers, and the declaration is what the facade's owner needs to build and test it.

### 10.2 Obtain approval from the facade's owner and the check's owner.

[REQUIRED] A new check type shall be added only after the facade's owning team and the check
system's owning team have both approved the proposal. *Rationale:* The facade's owner answers for
the order, latency and reasons of every decision, and the check's owner answers for the fact; each
commits to its part.

### 10.3 Place the check by what its answer is about.

[RECOMMENDED] A new check type should take a position among the checks whose answers are about the
same thing: the capability or organization at positions 1 to 3, the user at positions 4 and 5, the
resource at position 6, the request at positions 7 to 10. Quota stays last. *Rationale:* Keeping the
order's shape keeps 3.5 and 3.6 true as check types are added.

### 10.4 Reuse an existing reason where one fits.

[RECOMMENDED] A new check type should return a reason from the existing set. Where a new reason is
needed, the proposal shall give its HTTP status and user-interface treatment, and clients shall be
released with the treatment before the facade first returns it. *Rationale:* Each new reason is a
new treatment in every client; reuse keeps the set small enough to learn.

### 10.5 Run a new check in observe mode before it enforces.

[REQUIRED] A new check type shall first run in observe mode: the facade evaluates it and records
what it would have decided, while the decision returned is unaffected. The check begins to enforce
once its recorded decisions over a period stated in the proposal have been reviewed.
*Rationale:* A new check with a mistaken rule refuses real users; observe mode shows what it would
refuse before it refuses anyone.

### 10.6 Extend the facade's tests with the new check.

[REQUIRED] The addition shall include tests of the new check's position, its reasons, its failure
posture, its cache lifetime and its audit fields. *Rationale:* The facade's tests are what keep the
declared behavior true as later check types are added around this one.

## Glossary

| Term | Definition |
|---|---|
| **Action** | Something a subject asks the platform to do, identified by a stable key such as `diagram.export`. |
| **Advisory decision** | A decision requested in `ADVISE` mode to tell a user interface what to render. It consumes and reserves nothing. |
| **Capability** | A named unit of product function that an organization can hold and a user can exercise, identified by a stable key that carries no plan name or price. |
| **Check type** | One kind of question asked before an action proceeds, answered by one system: kill switch, entitlement, authorization and the others of section 3. |
| **Decision** | The decision facade's answer for one action: allowed or refused, with exactly one reason. |
| **Decision facade** | The one server-side component that a service asks whether a subject may take an action. It asks each check system and returns one decision. |
| **Enforcing decision** | A decision requested in `ENFORCE` mode by the service that performs the action, immediately before it performs it. |
| **Entitlement** | The record of what an organization holds for a capability, made up of the organization's active grants. |
| **Fail closed** | To refuse the action when a check cannot answer. |
| **Fail open** | To allow the action when a check cannot answer. |
| **Failure posture** | What the decision facade does for a check type when that check's system cannot answer. |
| **Feature flag** | A named value that software reads at runtime and that changes without a deployment. |
| **Grant** | One issued right of an organization to a capability. |
| **Kill switch** | A feature flag that switches a capability off for every subject at once. |
| **Limit** | The largest number of a counted thing an organization may hold at one time. |
| **Organization** | The customer account that users belong to and that grants are issued to. |
| **Quota** | The amount a limit or a metered allowance leaves available to an organization. |
| **Reason** | The single value from the fixed set that says why a decision allowed or refused. |
| **Reservation** | Quota held for an action that is in progress, later settled with the amount used or released. |
| **Safe default** | The value software uses for a feature flag when the flag cannot be evaluated. |
| **Seat** | One user's assigned place in a capability sold by number of users. |
| **Step-up** | Authenticating the user again, more strongly or more recently, for one action. |
| **Subject** | The user or machine account a decision is made for, together with the organization it acts in. |
