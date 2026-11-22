---
shortName: WHREC
description: >-
  How the platform receives webhooks from third-party providers: the one receiving service per
  provider, the gateway route, signature checks, replay and duplicate deliveries, answering fast,
  tenancy, broadcasting, recovering missed deliveries, secrets, logging and testing.
adoptionMetrics:
  - Share of webhook endpoints that check every delivery's signature before any other work
  - Share of webhook endpoints served through a declared webhook route at the gateway
  - Share of providers whose deliveries reach other services only as broadcast events
  - Share of providers with a reconciliation for missed deliveries
impactMetrics:
  - Deliveries acted on without a valid signature
  - Deliveries lost without being recovered by reconciliation
  - Incidents of a delivery reaching an organization other than the one holding its integration
tags: [webhooks, integrations, signatures, hmac, replay, idempotency, gateway, secrets]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, IMPLEMENTATION, VERIFICATION_AND_TESTING, OPERATE_AND_SUPPORT]
solutionScope: [APIS_AND_INTEGRATIONS, IDENTITY_AND_ACCESS, DEPENDENCIES_AND_EXTERNAL_SERVICES]
architectureQualities: [SECURITY, RELIABILITY, INTEROPERABILITY, OBSERVABILITY, TESTABILITY]
industryReferences:
  - {title: "GitHub Docs: Validating webhook deliveries", url: "https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries"}
  - {title: "GitHub Docs: Best practices for using webhooks", url: "https://docs.github.com/en/webhooks/using-webhooks/best-practices-for-using-webhooks"}
  - {title: "Standard Webhooks specification", url: "https://www.standardwebhooks.com/"}
---

# Webhook Receiving Standard

| Field | Value |
|---|---|
| **Short Name** | WHREC |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-11-21 |

## Purpose

This standard governs how the platform receives webhooks: HTTP requests a third-party provider,
such as GitHub or Slack, sends to the platform when something happens in the provider. It sets
which service receives them, how the gateway admits them, how a delivery is proven to come from
the provider, how a delivery is answered and processed, how its organization is found, how other
services learn of it, how missed deliveries are recovered, and how receiving is logged and tested.

## Value Proposition

- **Only the provider is heard** — every delivery is checked against a secret only the provider
  and the platform hold, before anything acts on it, so a forged request changes nothing.
- **One place per provider** — a provider's deliveries arrive at the one service that holds the
  platform's integration with it, so its secret, its signature scheme and its quirks live once.
- **Other services use the platform's events** — a service that reacts to a provider's activity
  subscribes to a broadcast, with the platform's delivery guarantees, and never handles the
  provider's format.
- **Nothing is acted on twice or lost** — repeats are recognised by the provider's delivery id,
  and deliveries the provider failed to make are recovered by reconciliation.
- **Each organization sees only its own** — a delivery's organization comes from the platform's
  own record of the integration, never from the payload.

## Scope

Applies to every endpoint that receives a request a third-party provider initiates to report
something that happened in the provider. Delivering the platform's own events to a customer's
endpoint is the other direction, and is governed by the platform's eventing rules.

## 1. Receiving service and route

### 1.1 Receive a provider's webhooks in the service that holds the platform's integration with it.

[REQUIRED] A provider's webhooks shall be received by the one service that holds the platform's
integration records for that provider, at an endpoint under that integration's resource. *Rationale:*
That service already holds the provider's credentials and the records that say which organization
each delivery belongs to, so checking and routing a delivery needs nothing from anywhere else.

*Example:* GitHub's deliveries for the platform's GitHub App arrive at the App Integrations
Service's `POST /v1/github-app-integrations/webhook`.

### 1.2 Admit a webhook endpoint at the gateway as a declared webhook route.

[REQUIRED] A webhook endpoint shall be declared as a webhook route in the service's gateway
configuration, and the gateway shall admit requests on it without a token, limited to `POST`, to a
body size the provider documents as its maximum, and to a request rate. Every other route keeps
token validation. *Rationale:* A provider cannot obtain a platform token, so its endpoint is the
one place the gateway lets an unauthenticated request through, and declaring it keeps that place
visible, narrow and reviewed.

*Example:* GitHub caps a delivery's payload at 25 MB, so the GitHub webhook route admits bodies up
to that size and refuses larger ones at the gateway.

### 1.3 Give each provider app its own endpoint and secret in each environment.

[REQUIRED] Each environment shall register its own provider app, with its own webhook URL and its
own webhook secret. *Rationale:* A provider sends an app's deliveries to one URL, so an app shared
between environments would send one environment's activity to another.

## 2. Authenticity

### 2.1 Check every delivery's signature before any other work.

[REQUIRED] The receiving service shall verify the provider's signature over the delivery's raw
request body, using the provider's documented algorithm and the webhook secret, and compare the
result in constant time, before parsing the body or acting on any header. *Rationale:* The
signature is the only proof the delivery came from the provider; parsing first exposes the parser
to anyone, and comparing in variable time leaks the expected signature byte by byte.

*Example:* GitHub signs each delivery with HMAC-SHA256 of the body under the webhook secret and
sends it as `X-Hub-Signature-256: sha256=<hex>`; the service computes the same and compares the two
with a constant-time comparison.

### 2.2 Refuse a delivery whose signature is missing or wrong.

[REQUIRED] A delivery without a signature, or with one that does not verify, shall be answered 401
with a problem response that names only the failure, and shall be logged with its source address
and delivery id. *Rationale:* The provider never sends an unsigned delivery, so one is a forgery
or a misconfiguration, and either is worth seeing in the logs.

### 2.3 Refuse a delivery outside the replay window when the provider signs a timestamp.

[REQUIRED] When a provider includes a timestamp in what it signs, the receiving service shall
refuse a delivery whose timestamp is more than five minutes from the service's clock. *Rationale:*
A captured delivery replayed later carries a valid signature, and a signed timestamp is what lets
the service tell it from a fresh one.

*Example:* Slack signs `v0:<timestamp>:<body>`, so a Slack delivery stamped six minutes ago is
refused. GitHub signs no timestamp, so GitHub deliveries rely on 3.2 instead.

### 2.4 Keep each webhook secret in the secret store, and accept two during a rotation.

[REQUIRED] A webhook secret shall be held in the platform's secret store, in a container the
environment's infrastructure code creates and the secret's value added to it apart from that
code, and read by the receiving service at run time. During a rotation the service shall accept a
signature made with either the current or the previous secret. *Rationale:* The provider issues the
secret, so infrastructure code reserves its place without holding its value, and accepting both
secrets lets the provider switch without a window of refused deliveries.

## 3. Organization

### 3.1 Find a delivery's organization from the platform's own record.

[REQUIRED] The receiving service shall find the organization a delivery belongs to by matching the
provider's identifier in the delivery, such as an installation id or a workspace id, to the
integration record that holds it. A delivery that no integration record holds shall be acknowledged
and dropped. *Rationale:* Any provider account can send activity to the platform's app, so only the
platform's record of who connected what decides which organization may see it.

*Example:* A GitHub `push` delivery carries `installation.id` 60377125; the integration holding
installation 60377125 belongs to Northwind Trading, so the delivery is Northwind Trading's.

## 4. Answering and processing

### 4.1 Answer within the provider's timeout, and process afterwards.

[REQUIRED] The receiving service shall answer a verified delivery with 2xx once it has recorded the
delivery, and do the delivery's work after answering. *Rationale:* A provider waits a few seconds
before counting a delivery as failed, and work done before answering turns a slow dependency into
lost deliveries.

*Example:* GitHub counts a delivery as failed when the answer takes more than 10 seconds.

### 4.2 Recognise a repeated delivery by the provider's delivery id.

[REQUIRED] The receiving service shall record each delivery's provider delivery id, and answer 2xx
without acting again on a delivery it has already recorded. *Rationale:* Providers redeliver, and
an operator redelivers by hand, so the same delivery arrives more than once.

*Example:* GitHub's delivery id is the `X-GitHub-Delivery` header.

### 4.3 Expect deliveries in any order.

[REQUIRED] The receiving service shall act correctly whatever order deliveries arrive in, by
comparing the provider's timestamps or by reading the current state from the provider's API before
changing a record from a delivery. *Rationale:* Providers send deliveries concurrently and retry
them separately, so a later fact can arrive before an earlier one.

### 4.4 Acknowledge a delivery the service does not handle.

[REQUIRED] A verified delivery of an event type the service does not handle shall be answered 2xx
and dropped. *Rationale:* A provider that receives errors for a type it was told to send retries
it, and may disable the webhook.

### 4.5 Broadcast a delivery for other services, and keep the provider's format inside the receiver.

[REQUIRED] A delivery other services react to shall be broadcast by the receiving service as a
platform event of the delivery's organization, naming the integration it came through. Other
services shall subscribe to that event and never receive the provider's deliveries themselves.
*Rationale:* Subscribers get the platform's delivery guarantees, tenancy and contracts, and a
change in the provider's format is absorbed in one place.

*Example:* A GitHub `pull_request` delivery for Northwind Trading's integration is broadcast as
Northwind Trading's event, and the Code service, which subscribes, records the pull request.

## 5. Recovery

### 5.1 Reconcile the deliveries a provider failed to make.

[REQUIRED] For every provider that does not redeliver failed deliveries on its own, the receiving
service shall run a reconciliation on a schedule that finds failed deliveries through the
provider's API and asks for them again, within the period the provider keeps them. *Rationale:* A
delivery that failed while the service was down or deploying is otherwise lost, and its fact never
reaches the records that depend on it.

*Example:* GitHub does not redeliver failed deliveries automatically, and keeps them for three
days; an hourly job lists the app's failed deliveries and asks GitHub to redeliver each one.

## 6. Logging and testing

### 6.1 Log each delivery's identity and outcome, and leave out its payload and signature.

[REQUIRED] The receiving service shall log each delivery's provider, delivery id, event type,
organization, outcome and processing time, and shall leave the body, the signature and the secret
out of every log. *Rationale:* The identity and outcome are what tracing a delivery needs; the body
may carry a customer's code or personal data, and the signature helps a forger.

### 6.2 Test signature checks, repeats, ordering and unhandled types.

[REQUIRED] A receiving service's tests shall cover a delivery with a valid signature, a missing
one, a wrong one and one made with the previous secret during a rotation; the same delivery twice;
two deliveries out of order; an event type the service does not handle; and a delivery no
integration holds. *Rationale:* These are the cases a receiver meets in production and the path
written first never exercises.
