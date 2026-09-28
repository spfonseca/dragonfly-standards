---
shortName: KCOMP
description: >-
  How any workload runs on Kubernetes, whatever it does: the image it is pinned to, how its Pod is
  composed, the identity it runs as, the privileges it holds, what it may reach on the network, and
  how its manifests are delivered, validated and labelled.
adoptionMetrics:
  - Share of production manifests referencing an immutable image version
  - Share of workloads running as non-root with a dedicated ServiceAccount
  - Share of Kubernetes manifests validated against policy in the delivery pipeline
impactMetrics:
  - Policy violations found at admission or in production rather than in the pipeline
  - Security findings on workload privilege, identity or network reach
tags: [kubernetes, workload-security, container-images, service-accounts, network-policy, manifests]
softwareLifecycle: [IMPLEMENTATION, BUILD_AND_INTEGRATION, DEPLOYMENT]
solutionScope: [INFRASTRUCTURE, RUNTIME_AND_EXECUTION, SECURITY_CONTROLS, IDENTITY_AND_ACCESS, DELIVERY_AND_AUTOMATION]
architectureQualities: [SECURITY, DEPLOYABILITY, OPERABILITY]
---
# Compute Best Practices in Kubernetes

| Field | Value |
|---|---|
| **Short Name** | KCOMP |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-27 |

## Purpose

This standard governs how any workload runs on Kubernetes, whatever it does — a service serving
requests, a backend job, a worker draining a queue. It covers the properties every workload carries
regardless of purpose: the identity it runs as, the privileges it holds, what it may reach, how its
image is named, and how its manifests are delivered.

## Value Proposition

- **The code that runs is the code declared** — immutable image versions stop retries and new Pods
  from silently running different code.
- **Least privilege by default** — dedicated identities, no unused API tokens, non-root containers
  and no host access limit the impact of a compromise.
- **Network reach matches real dependencies** — network policy restricts each workload to what it
  needs, limiting lateral movement and accidental coupling.
- **Manifests are governed like code** — reviewed, validated and promoted through the delivery
  pipeline, so policy is enforced before admission rather than found in an incident.
- **Workloads are identifiable** — consistent labels let policy, cost, telemetry and operations find
  every workload the same way.

## Scope

Applies to every workload the platform runs on Kubernetes.

It does not cover what a workload does or how its work is decomposed. A backend job's execution
pattern, its correctness rules and its job-specific Kubernetes mechanics — `restartPolicy`,
`backoffLimit`, `activeDeadlineSeconds`, `concurrencyPolicy` and the rest — are the Backend Job
Design Standard's, and have no analogue in a workload that serves requests.

## Status

**This is a holding place, not a finished standard.** Its guidelines were moved verbatim from the
Backend Job Design Standard (BJOBS v1.0 §21.21, §21.22, §22.1–§22.7 and §22.18–§22.20, as numbered
before that standard's renumbering), where they had been written as job requirements although every
one of them is identical for a service Deployment. They are renumbered here; further sections and
additions are later work.

One question to settle before this is written properly: **how much of it should be a standard at
all.** A requirement the platform's own Terraform modules can enforce structurally — a workload
declared through a module gets a dedicated service account, a non-root user, a read-only root
filesystem and consistent labels by construction — is better as a property of the module than as a
rule each team must remember and each reviewer must check. What remains for the standard is
whatever a module cannot decide on a workload's behalf.

## 1. Images and Pod Composition

### 1.1 Pin deployable images to an immutable application version.

[REQUIRED] Production job and worker manifests shall reference an
immutable image version, preferably by digest or by an organizationally
guaranteed immutable tag; mutable tags such as `latest` are prohibited.
*Rationale:* Retries and later-created Pods must not silently execute
different code under the same declared deployment version.

### 1.2 Use one primary application container per job Pod by default.

[RECOMMENDED] A job Pod should contain one primary work-performing
container; sidecars shall be introduced only for a platform capability
that cannot be provided externally or through native Kubernetes
facilities, and their termination behavior shall be validated for Job
completion. *Rationale:* Sidecars add lifecycle coupling and can prevent
or delay run-to-completion semantics when not designed for Jobs.

## 2. Workload Identity

### 2.1 Use a dedicated Kubernetes ServiceAccount per deployed job component.

[REQUIRED] Each independently deployed job or worker component shall
use a dedicated Kubernetes `ServiceAccount` mapped to the approved
workload identity rather than the namespace default ServiceAccount.
*Rationale:* Component-specific identity enables least privilege and
isolates compromise.

### 2.2 Disable automatic ServiceAccount token mounting unless the workload calls the Kubernetes API.

[REQUIRED] Set `automountServiceAccountToken: false` for job Pods that
do not need to call the Kubernetes API; enable token mounting only when
Kubernetes API access is an explicit workload requirement. *Rationale:*
Most application jobs need cloud or application identity, not Kubernetes
API credentials, so an unused token is unnecessary attack surface.

## 3. Workload Security

### 3.1 Run containers as non-root.

[REQUIRED] Job and worker containers shall run as a non-root user and
shall set `allowPrivilegeEscalation: false` unless a reviewed platform
requirement makes that impossible. *Rationale:* Background processing
normally requires no host-level privilege, and removing it reduces the
impact of container compromise.

### 3.2 Use the runtime-default seccomp profile.

[REQUIRED] Linux job and worker Pods shall use the `RuntimeDefault`
seccomp profile unless an approved exception requires a different
profile. *Rationale:* The runtime-default syscall filter provides
baseline process isolation without requiring application-specific policy
construction.

### 3.3 Prefer a read-only root filesystem.

[RECOMMENDED] Containers should use `readOnlyRootFilesystem: true` and
mount explicit writable ephemeral or persistent volumes only where
runtime writes are required. *Rationale:* A read-only application
filesystem reduces mutation opportunities and makes writable state
intentional.

### 3.4 Do not use privileged containers or host namespaces for application jobs.

[REQUIRED] Application backend jobs shall not use privileged
containers, `hostNetwork`, `hostPID`, `hostIPC`, or host-path mounts
unless approved as a platform-level exception. *Rationale:* These
capabilities bypass important Kubernetes isolation boundaries and are
unnecessary for normal application processing.

### 3.5 Restrict network access to required dependencies.

[REQUIRED] Namespaces hosting backend jobs shall use the
organization's network-policy controls so workers can reach only
required internal services, data stores, messaging endpoints,
observability endpoints, and approved external destinations where
enforcement capability exists. *Rationale:* Least-privilege networking
limits lateral movement and accidental dependency creation.

## 4. Manifest Delivery and Governance

### 4.1 Keep Kubernetes manifests and policies in the normal delivery pipeline.

[REQUIRED] `Job`, `CronJob`, `Deployment`, autoscaling,
ServiceAccount, NetworkPolicy, disruption, and related Kubernetes
definitions shall be version-controlled, reviewed, validated, and
promoted through the same automated delivery controls as application
code. *Rationale:* Kubernetes configuration is executable production
behavior and must not be managed as ad hoc runtime state.

### 4.2 Validate Kubernetes policy before deployment.

[REQUIRED] Delivery pipelines shall validate Kubernetes manifests
against schema and organizational policy before production deployment,
including required resources, security context, identity, image
immutability, and prohibited privilege settings. *Rationale:* Platform
constraints are most reliable when mechanically enforced before
admission rather than discovered during an incident.

### 4.3 Use namespace and workload labels consistently.

[REQUIRED] Job workloads shall carry the organization's standard
ownership, application, environment, component, and observability labels
so policy, cost, telemetry, and operations can identify them
consistently. *Rationale:* Kubernetes automation depends heavily on
labels; inconsistent metadata makes governance and operations brittle.
