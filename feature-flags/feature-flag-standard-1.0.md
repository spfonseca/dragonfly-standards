---
shortName: FFLAG
description: >-
  How feature flags are created, named, owned, targeted, read, tested and removed: the four flag
  types, key grammar, ownership and expiry, what targeting may use, safe defaults, how quickly a
  change takes effect, tested off-paths, runbooks, and how public APIs are flagged.
adoptionMetrics:
  - Share of flags with a declared type, owning team and maintainer
  - Share of release and experiment flags with an expiry date
  - Share of flags past expiry or stale for more than 30 days
  - Share of kill switches with a runbook and an off-path exercised in the last six months
  - Share of flag reads that supply a default in code
impactMetrics:
  - Incidents caused or prolonged by a flag's untested path
  - Time from a kill switch change to its effect in every reader
  - Incidents in which a flag made available something the organization had not purchased
  - Number of flags in code that serve one value everywhere
tags: [feature-flags, kill-switch, release-flags, experiments, ops-flags, targeting, safe-defaults, stale-flags, runbooks]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, IMPLEMENTATION, VERIFICATION_AND_TESTING, RELEASE, OPERATE_AND_SUPPORT, MAINTAIN_AND_EVOLVE]
solutionScope: [SOFTWARE_ARCHITECTURE, APPLICATION_COMPONENTS, APIS_AND_INTEGRATIONS, ENVIRONMENTS_AND_CONFIGURATION, DELIVERY_AND_AUTOMATION, QUALITY_AND_TESTING]
architectureQualities: [RELIABILITY, RESILIENCE, OPERABILITY, MAINTAINABILITY, TESTABILITY, DEPLOYABILITY]
---

# Feature Flag Standard

| Field | Value |
|---|---|
| **Short Name** | FFLAG |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-11-19 |

## Purpose

This standard governs feature flags: values that software reads at runtime and that an engineer
changes without a deployment. It fixes the types a flag may have, how a flag is named and owned,
when it expires and how it is removed, what its targeting may use, what software does when a flag
cannot be evaluated, how quickly a change takes effect, how both of a flag's paths are tested, and
how a public API is flagged.

## Value Proposition

- **Deployment and release are separate** — code reaches production switched off and is released to
  chosen organizations and users when it is ready.
- **A capability can be stopped in a minute** — a kill switch takes effect in every reader within 60
  seconds, with no deployment.
- **Flags are removed when their work is done** — every temporary flag has an expiry date and an
  owner, so the code holds only the flags still in use.
- **A flag outage changes nothing** — every read has a default, so software behaves in a known way
  when the flag system cannot be reached.
- **Flags stay out of pricing** — what an organization has purchased is decided by its entitlement,
  and a flag only decides whether released code is switched on.

## Scope

Applies to every feature flag read by a service, a backend job or a user interface, and to the
people who create, change and remove flags.

Whether an organization holds a capability, and whether a user is permitted an action, are decided
by the entitlement and authorization systems. This standard covers flags alone, and states where a
flag's reach ends.

## 1. Flag Types

### 1.1 Give every flag exactly one of four types.

[REQUIRED] Every flag shall be declared as one of these types when it is created:

| Type | Purpose | Lifetime |
|---|---|---|
| Release | Switches new code on for chosen organizations, users or a percentage of them, until it is on for all. | Temporary |
| Experiment | Assigns subjects to variants so the variants' outcomes can be compared. | Temporary |
| Ops | Changes how a running capability operates: a threshold, a batch size, a choice of dependency. | Permanent |
| Kill switch | Switches a capability off for every subject at once. | Permanent |

*Rationale:* The type states what the flag is for, and with it how long the flag lives, who may
change it and what its default is. A flag with no declared type acquires several purposes and can
then never be removed.

### 1.2 Keep a flag's type for its whole life.

[REQUIRED] A flag's type shall stay as declared. Where a released capability needs a permanent
switch, a new kill switch is created and the release flag is removed. *Rationale:* A release flag
kept as a kill switch carries rollout targeting that was never meant to be permanent, and its name
and default describe the rollout.

### 1.3 Give every capability that can harm the platform a kill switch.

[RECOMMENDED] A capability should have a kill switch where its failure can affect other
capabilities, where it depends on an external system, or where it is costly to run.
*Rationale:* These are the capabilities an operator needs to stop during an incident without
waiting for a deployment.

### 1.4 Make a kill switch a boolean that is on in normal operation.

[REQUIRED] A kill switch shall be a boolean whose `true` value means the capability is switched on.
It shall carry no targeting: its value is the same for every subject. *Rationale:* During an
incident the operator must be certain what one change does, and a switch with one value for
everyone has one effect.

## 2. Naming

### 2.1 Form a flag's key from the owning domain and the feature.

[REQUIRED] A flag's key shall be the owning service domain's short code, a dot, and the feature in
lowercase words joined by dashes. *Rationale:* The key says who owns the flag and what it controls
wherever it appears — in code, in a log line and in the flag system.
*Example:* `eabus.capability-map-export-format`.

### 2.2 End a kill switch's key in `.enabled`.

[REQUIRED] A kill switch's key shall be the capability's key followed by `.enabled`.
*Rationale:* The suffix marks the flag as a kill switch in every listing, and reads correctly with
its values: enabled is true, or enabled is false.
*Example:* `aichat.agent-chat.enabled`.

### 2.3 Name a boolean flag for what its `true` value does.

[REQUIRED] A boolean flag's key shall describe the behavior that `true` switches on.
*Rationale:* A flag named for its off state is read backwards by the person changing it.
*Example:* `eabus.bulk-import` switches bulk import on when true.

### 2.4 Use a key once.

[REQUIRED] A key shall identify one flag for all time, and a removed flag's key shall stay retired.
*Rationale:* Old code, old logs and old dashboards still name the removed flag; a new flag under
the same key would be read by them as the old one.

### 2.5 Describe every flag.

[REQUIRED] Every flag shall carry a description stating what it controls, what each value does, and
for a kill switch or ops flag, where its runbook is. *Rationale:* The person changing a flag during
an incident is often not the person who created it.

## 3. Ownership

### 3.1 Give every flag one owning team and one maintainer.

[REQUIRED] Every flag shall name the team that owns it and one engineer on that team as its
maintainer. When the maintainer leaves the team, the team names another. *Rationale:* A flag is
removed, reviewed and answered for by someone; a flag with no owner stays in the code indefinitely.

### 3.2 Change a production flag as its owner or as the on-call operator.

[REQUIRED] A flag's value or targeting in production shall be changed by a member of its owning
team or by the on-call operator acting under the flag's runbook. *Rationale:* The owner knows what
the change does, and the on-call operator has the runbook that says so.

### 3.3 Record every change to a flag.

[REQUIRED] Every change to a flag's value, targeting or default shall be recorded with who made it,
when, the previous and new state, and the incident or work item it belongs to. *Rationale:* When
behavior changes without a deployment, the flag history is the only record of what changed.

## 4. Expiry and Cleanup

### 4.1 Set an expiry date on every release and experiment flag.

[REQUIRED] A release flag shall be created with an expiry date at most 90 days after its creation.
An experiment flag shall be created with an expiry date at most 30 days after the experiment's
planned end. An expiry date is extended only by the flag's owner, with a recorded new date.
*Rationale:* A temporary flag with a date is removed on a schedule; one without a date is removed
when someone remembers it.

### 4.2 Review every ops flag and kill switch every six months.

[REQUIRED] The owning team shall review each ops flag and kill switch at least every six months and
record that the flag is still needed, its runbook is current and its off-path has been exercised.
*Rationale:* Permanent flags have no expiry to prompt a review, and the capability around them
changes.

### 4.3 Treat a temporary flag that serves one value everywhere as stale.

[REQUIRED] A release or experiment flag that has served the same value to every subject in
production for 14 days is stale, and its owner shall remove it within the following 30 days.
*Rationale:* The flag has finished its work; from then on it is an untested branch in the code.

### 4.4 Remove a flag from the code before archiving it.

[REQUIRED] A flag shall be removed in this order: the code that reads it is deleted along with the
path no longer taken, that code is deployed everywhere, and then the flag is archived in the flag
system. *Rationale:* Archiving first sends every remaining reader to its default, which may be the
path being retired.

### 4.5 Report flags past expiry and stale flags every week.

[REQUIRED] The flag system's owner shall publish each week, to each owning team, the team's flags
that are past expiry or stale. *Rationale:* A list addressed to the owner is what turns an expiry
date into a removal.

### 4.6 Fail the build on a flag that is 30 days past expiry.

[RECOMMENDED] A service's build should fail when its code reads a flag that is more than 30 days
past its expiry date. *Rationale:* The build is the one place every engineer on the team sees, and a
failure is acted on where a report is read later.

## 5. Targeting

### 5.1 Target by identity and rollout attributes alone.

[REQUIRED] A flag's targeting shall use only these attributes: the user's id, the organization's
id, the environment, a percentage of users or organizations, and membership of a cohort declared
for rollout or experiment. *Rationale:* These attributes describe who receives a rollout. Every
other fact about a customer has a system that owns it, and a copy inside targeting rules goes
stale.

### 5.2 Keep plans, prices and purchases in the entitlement system.

[REQUIRED] What an organization receives because of its plan, its price or a purchase shall be
expressed as an entitlement. A flag's targeting holds no plan name, tier, price or purchase fact.
*Rationale:* Plan logic held in targeting rules is a second, unaudited copy of the commercial
arrangement, and the two disagree the first time a plan changes.
*Example:* Bulk import is included in the Team plan. The Team plan's grants include the
`bulk-import` capability, and the release flag `eabus.bulk-import` is on for everyone once the
rollout ends.

### 5.3 Let a flag narrow access and never widen it.

[REQUIRED] A flag that is on shall make a capability available only to subjects whose organization
holds the capability. An organization that lacks the entitlement is refused the capability whatever
the flag's value. *Rationale:* A flag decides whether released code is switched on; whether the
customer has it is the entitlement's decision, and the two are combined so that both must agree.

### 5.4 Evaluate a flag that decides availability through the decision facade.

[REQUIRED] A kill switch, and a release or experiment flag that decides whether a capability is
available to a subject, shall be evaluated by the decision facade as part of the gating decision.
Code reads directly only the flags that choose behavior within a capability the subject already
has. *Rationale:* Availability is decided together with entitlement and authorization, in one
order with one reason; a flag read beside that decision produces a second, different answer.

### 5.5 Send identifiers to the flag system, and nothing personal.

[REQUIRED] An evaluation shall send the flag system the user's id and the organization's id, and no
name, email address or other personal detail. *Rationale:* The flag system needs a stable key to
target and to assign percentages; the person's details serve no evaluation and would be held by one
more system.

### 5.6 Keep a subject's assignment stable.

[REQUIRED] A percentage rollout or experiment shall give the same subject the same value on every
evaluation while the targeting is unchanged, and shall assign by organization where the feature is
used by an organization's users together. *Rationale:* A user whose feature appears and disappears,
or whose colleagues see a different product, reports a defect.

## 6. Defaults and Evaluation

### 6.1 Supply a default in code with every flag read.

[REQUIRED] Every read of a flag shall supply a default value in code, and the software shall use it
when the flag cannot be evaluated. *Rationale:* The flag system will at some point be unreachable,
and the default is the behavior chosen in advance for that moment.

### 6.2 Choose the default by the flag's type.

[REQUIRED] A flag's default shall be:

| Type | Safe default |
|---|---|
| Release | Off: the behavior before the release. |
| Experiment | The control variant. |
| Ops | The value the capability was last proven to run safely with, stated in the flag's description. |
| Kill switch | On: the capability stays available. |

*Rationale:* The default is the least surprising behavior. Unreleased code stays unreleased, and a
flag outage does not switch off capabilities that are running.

### 6.3 Evaluate flags from rules held in memory.

[REQUIRED] A flag shall be evaluated from targeting rules held in the reader's memory or in a
shared evaluation service's memory, with no call to an external flag vendor in the path of a
request. *Rationale:* Flags are read on nearly every request; an external call per read adds its
latency and its failures to all of them.

### 6.4 Keep evaluating on the last rules received.

[REQUIRED] When the source of flag rules is unreachable, a reader shall continue to evaluate with
the rules it last received, and shall use the defaults of 6.2 only when it has never received any.
*Rationale:* The last rules received are closer to the intended state than the defaults are.

### 6.5 Decide on the server.

[REQUIRED] A flag that controls what a user may do or see shall be evaluated on the server, and a
value delivered to a browser shall be used for rendering alone. *Rationale:* A value held in a
browser can be changed by its user.

## 7. Propagation

### 7.1 Make a kill switch change effective everywhere within 60 seconds.

[REQUIRED] A change to a kill switch shall take effect in every reader within 60 seconds of being
saved. *Rationale:* A kill switch is used during an incident, and each further minute it takes is a
minute the incident continues.

### 7.2 Make every other flag change effective within 5 minutes.

[REQUIRED] A change to a release, experiment or ops flag shall take effect in every reader within 5
minutes of being saved. *Rationale:* An engineer rolling a feature forward or back needs to see the
effect while still watching for it.

### 7.3 Measure propagation continuously.

[RECOMMENDED] The flag system's owner should change a dedicated test flag on a schedule and measure
how long each environment's readers take to see the change. *Rationale:* Propagation time degrades
without anyone changing it, and the first sign otherwise is a slow kill switch during an incident.

### 7.4 Change a kill switch without a deployment.

[REQUIRED] Switching a kill switch off or on shall require only a change in the flag system, by a
person authorized under 3.2, and shall depend on no build, deployment or approval step.
*Rationale:* The switch exists for the moment when the delivery pipeline is too slow or is itself
affected.

## 8. Testing

### 8.1 Test both paths of every flag.

[REQUIRED] A service's automated tests shall exercise the code with each flag on and with it off,
for every flag the service reads. *Rationale:* The path not currently served in production still
ships, and it is the path taken the moment the flag changes.

### 8.2 Set flag values explicitly in tests.

[REQUIRED] A test shall set the value of each flag it depends on, and shall run without access to
the flag system. *Rationale:* A test that reads the live flag passes or fails with whatever the
flag holds that day.

### 8.3 Test the default path.

[REQUIRED] A service's tests shall exercise each flag read with the flag system unreachable and
assert that the default of 6.2 is used. *Rationale:* The default path runs only during an outage
and is otherwise never observed.

### 8.4 Exercise a kill switch's off-path before launch and every six months.

[REQUIRED] A capability's kill switch shall be switched off in a production-like environment before
the capability is released, and again at least every six months, with a check that the capability
stops, the rest of the platform continues, and the capability resumes when the switch is turned on.
*Rationale:* A kill switch that has never been used is an assumption; the exercise is what makes it
a control.

## 9. Runbooks

### 9.1 Write a runbook for every kill switch and ops flag.

[REQUIRED] Every kill switch and ops flag shall have a runbook that states: what the flag controls,
when to change it, who may change it, what users see after the change, what happens to work in
progress, how to confirm the change took effect, and how to return to normal. *Rationale:* The
runbook is read under pressure by someone who may not know the capability; it must answer what
they will ask.

### 9.2 Link the runbook from the flag.

[REQUIRED] A kill switch's or ops flag's description shall hold the location of its runbook.
*Rationale:* The operator starts from the flag, and the runbook must be one step from it.

### 9.3 Announce a kill switch change.

[REQUIRED] A person who switches a kill switch off or on in production shall announce the change,
its cause and its expected duration to the owning team and the on-call channel at the time of the
change. *Rationale:* A capability that stops with no announcement is investigated as a new
incident by everyone who notices it.

## 10. Flags and Public APIs

### 10.1 Flag a public API by capability or by dependency.

[REQUIRED] A flag that controls a public API shall cover a whole capability, or everything that
uses one dependency. A single endpoint has its own flag only when it is the whole capability.
*Rationale:* A consumer builds on a capability's endpoints together; a capability with some
endpoints on and others off is a state no consumer was written for.
*Example:* The flag `eabus.capability-map-export.enabled` covers the endpoint that starts an export,
the one that reports its status and the one that returns the file.

### 10.2 Answer consistently across a capability's endpoints.

[REQUIRED] While a flag has a capability switched off, every endpoint of that capability shall
return the same refusal. *Rationale:* A consumer that receives the same answer from every endpoint
can recognize that the capability is off and wait.

### 10.3 Keep configuration values apart from on-off flags.

[REQUIRED] A value that tunes how a capability runs — a limit, a timeout, a threshold — shall be an
ops flag with its own key and a declared type and range, separate from the flag that switches the
capability on or off. *Rationale:* Switching a capability off and tuning it are different acts by
different people, and one flag that does both cannot be given a safe default for both.
*Example:* `eabus.capability-map-export.enabled` switches export on and off;
`eabus.capability-map-export-page-size` holds the number of records per file.

### 10.4 Keep a published contract's behavior the same under every flag value.

[REQUIRED] For a published version of an API, a flag shall decide only whether a capability is
available. The request and response shapes, and the meaning of each field, shall be the same for
every caller whatever the values of any flag. *Rationale:* A consumer writes code against the
published contract; a response that varies by flag is a contract the consumer cannot test against.

### 10.5 Release a new API capability to named organizations first.

[RECOMMENDED] A new public API capability should be released through a release flag to named
organizations before it is switched on for all. *Rationale:* A consumer who has agreed to try the
capability reports its defects before every consumer depends on it.

## Glossary

| Term | Definition |
|---|---|
| **Capability** | A named unit of product function that an organization can hold and a user can exercise, identified by a stable key that carries no plan name or price. |
| **Cohort** | A named set of users or organizations declared for a rollout or an experiment. |
| **Decision facade** | The one server-side component that a service asks whether a subject may take an action. It asks each check system and returns one decision. |
| **Entitlement** | The record of what an organization holds for a capability, made up of the organization's active grants. |
| **Experiment flag** | A feature flag that assigns subjects to variants so the variants' outcomes can be compared. |
| **Feature flag** | A named value that software reads at runtime and that changes without a deployment. |
| **Kill switch** | A feature flag that switches a capability off for every subject at once. |
| **Off-path** | The code that runs when a flag is off. |
| **Ops flag** | A feature flag that changes how a running capability operates. |
| **Organization** | The customer account that users belong to and that grants are issued to. |
| **Reader** | Any running software that evaluates a feature flag: a service, a backend job or a user interface. |
| **Release flag** | A feature flag that switches new code on for chosen subjects until it is on for all. |
| **Runbook** | The written procedure an operator follows to change a flag in production. |
| **Safe default** | The value software uses for a feature flag when the flag cannot be evaluated. |
| **Stale flag** | A release or experiment flag that has served one value to every subject in production for 14 days. |
| **Subject** | The user or machine account a decision is made for, together with the organization it acts in. |
| **Targeting** | The rules that decide which value of a flag a subject receives. |
