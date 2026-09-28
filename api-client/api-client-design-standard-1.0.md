# API Client Design Standard

| Field | Value |
|---|---|
| **Short Name** | APICL |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-27 |

## Purpose

This standard defines how software calls HTTP APIs: the design and implementation practices a
caller follows when it depends on an interface it does not control. Its objective is outbound API
communication that is predictable, secure, observable, resilient and safe under failure.

The principle it exists to hold: **nothing another system returns is trusted until the caller has
checked it against its own expectations, and nothing about a call is left to a library's defaults.**
A caller that uses a response as it arrives, or lets an HTTP library decide its timeouts, retries and
redirects, turns every change, outage or quirk of the API it calls into a defect of its own.

## Value Proposition

-   **Contained failure** --- a slow, failing or throttling dependency degrades one capability in a
    bounded way instead of exhausting the caller's threads, connections and memory.
-   **Safe retries** --- retries are explicit, bounded and duplicate-safe, so recovering from a
    transient failure never changes a business outcome.
-   **Trustworthy data** --- every response is checked against what the caller depends on before it
    is used, so an upstream format change becomes a detected failure instead of bad data.
-   **Operable dependencies** --- operators can see which dependency was called, how long it took,
    whether it was retried and why it failed, without secrets or payloads reaching telemetry.
-   **AI-ready guidance** --- explicit defaults, a per-client decision list and a checklist let
    AI-assisted engineering tools generate conforming clients without guessing.

## Scope

Applies to every component that calls an HTTP or HTTPS API it does not own: synchronous
service-to-service calls, calls from background work, calls to third-party APIs such as an AI model
provider's, backend-for-frontend calls, and integration clients. A published file fetched over HTTP
is an API response for the purposes of this standard.

It does not cover:

- **The APIs a service offers.** How an API is designed, versioned and documented is the provider's
  concern; this standard governs only the calling side.
- **What a workload does with a failure once it has stopped retrying.** Recording the outcome,
  preserving the unit of work and reporting it belong to the calling workload.
- **Dependencies that are not HTTP APIs** — a database driver, a message broker's client. Their
  resilience is governed where those dependencies are.

Any requirement may be waived only through an explicit, documented, approved waiver recorded in the
product's implementation guidance.

## Requirement Language

-   **[REQUIRED]** --- mandatory for conformance unless an approved waiver exists; stated with
    *shall* or *shall not*.
-   **[RECOMMENDED]** --- the expected default; a deviation requires a documented reason; stated
    with *should*.
-   **[OPTIONAL]** --- permitted and context-dependent; stated with *may*.

## Design Principles

1.  **Bound every call.** Every network operation has an explicit bound in time and resources.
2.  **Assume failure.** Remote systems, networks, DNS, identity providers and intermediaries fail
    independently.
3.  **Trust nothing unchecked.** A response is used only after it has been checked against what the
    caller depends on.
4.  **Preserve semantics.** Retries, redirects and duplicate requests never change the intended
    business outcome.
5.  **Own resilience deliberately.** Timeouts, retries, circuit breaking and concurrency are explicit
    and coordinated, never inherited by accident.
6.  **Separate transport from business logic.** HTTP mechanics do not leak into application code.
7.  **Make calls observable.** An operator can tell what was called, how long it took, whether it was
    retried and why it failed.
8.  **Protect credentials and data.** Authentication material and sensitive payloads never reach
    logs, traces, metrics, URLs or exceptions, and data goes only where it is permitted to go.
9.  **Prefer bounded degradation to cascading failure.** A failing dependency is never allowed to
    exhaust the caller's resources or fail unrelated work.

------------------------------------------------------------------------

## 1. Client Architecture

### 1.1 Make every call to an API through a dedicated client component.

[REQUIRED] Calls to a given API shall be made through a defined client component, never by
constructing HTTP requests throughout business logic. *Rationale:* One place per API is what makes
authentication, serialization, resilience, telemetry and contract behaviour consistent, and what a
reviewer can check.

### 1.2 Expose domain-oriented operations.

[REQUIRED] Application code shall invoke client operations that represent the API's capabilities,
and shall not manipulate URLs, headers, status codes or raw HTTP request objects directly.
*Rationale:* Application code that speaks HTTP must change whenever the transport does.

### 1.3 Implement transport behaviour apart from business logic.

[REQUIRED] Authentication, retry, timeout, serialization, tracing and connection management shall be
implemented independently of business decision logic. *Rationale:* Transport policy mixed into
decisions cannot be tuned or tested without touching the decisions.

### 1.4 Do not expose the HTTP library to application code.

[REQUIRED] A client interface consumed by application code shall not require its callers to know the
HTTP library it uses, unless the component is intentionally a low-level infrastructure client.
*Rationale:* A library that leaks through the interface cannot be replaced or upgraded without
changing every caller.

### 1.5 Provide shared client infrastructure for cross-cutting behaviour.

[RECOMMENDED] An organization should provide shared client infrastructure for cross-cutting behaviour
— credentials, tracing, retry and timeout mechanics, error translation — while each API-specific
client defines its own contract and policy. *Rationale:* Every team re-implementing retries and token
caching produces as many variants as teams, most of them wrong in a different way.

### 1.6 Distinguish a logical call from its physical attempts.

[REQUIRED] A logical API operation may consist of one or more physical HTTP attempts; deadlines, retry
limits, telemetry and the final error shall preserve that distinction. *Rationale:* A deadline or
retry limit counted per attempt instead of per call is not a bound at all.

### 1.7 Bound the total work of a logical call.

[REQUIRED] The total duration and the number of physical attempts of a logical call shall both be
bounded. *Rationale:* Either one unbounded makes the call unbounded.

### 1.8 Keep one call context across all attempts.

[REQUIRED] Correlation identifiers, trace context, operation identity and any idempotency identifier
shall stay associated with every attempt of the same logical call. *Rationale:* Attempts that cannot
be tied to their call cannot be diagnosed, and a retry that loses its idempotency identifier is a
duplicate.

## 2. Request Construction

### 2.1 Build URLs with URI facilities, never by concatenation.

[REQUIRED] Paths and query strings shall be built with URI construction facilities, and path segments
and query values encoded for their URI context. *Rationale:* Concatenation produces malformed and
injectable requests the first time a value contains a reserved character.

### 2.2 Send explicit media types.

[REQUIRED] A request with a body shall send the correct `Content-Type`, and a request whose response
representation matters shall send `Accept`. *Rationale:* A server left to guess a representation may
guess differently tomorrow.

### 2.3 Use the contract's field names and formats exactly.

[REQUIRED] A client shall not infer or transform wire field names, date formats, enumeration values
or null semantics beyond what the API contract defines. *Rationale:* A client-side reinterpretation
is an undocumented second contract that the provider does not know it has.

### 2.4 Consider generated models where a trustworthy contract exists.

[RECOMMENDED] Where the API publishes a trustworthy OpenAPI contract, generated request and response
models should be considered; generated transport behaviour shall still conform to this standard.
*Rationale:* Generated models remove hand-typed field names, but generators ship their own timeout
and retry defaults.

### 2.5 Send only the headers the call needs.

[REQUIRED] A client shall not forward inbound request headers wholesale to a downstream API, and
security-sensitive headers — identity, forwarding and tenancy headers — shall be created or sanitized
at a trusted boundary rather than copied. *Rationale:* Copied headers carry a caller's claims to a
system that may trust them.

### 2.6 Identify the calling application where the API supports it.

[RECOMMENDED] For internal and partner APIs, a stable application identifier should be sent through
the agreed mechanism. *Rationale:* The provider can then attribute load, apply policy and answer a
support case about a specific caller.

## 3. Validating Responses

### 3.1 Use only structured data.

[REQUIRED] A client shall use only structured data from the APIs it calls, never scraped or free-form
content. *Rationale:* Only structured data can be checked against a schema, and every guideline in
this section depends on that check.

### 3.2 Validate every response against a schema the caller owns, before using it.

[REQUIRED] Every response from an API the caller does not own shall be validated against a JSON Schema
the **caller** owns and keeps in its own repository, before any part of it is used. The schema covers
the fields the caller maps and the envelope around them, not the whole response. *Rationale:* Most
APIs publish no schema, and a published one can change without notice. The caller's own schema is the
only statement of what it actually depends on, and validating against it turns an upstream format
change into a detected failure instead of bad data.

### 3.3 Tolerate additive change.

[REQUIRED] Unknown additional response properties shall be tolerated — the owned schema allows them —
unless the contract explicitly requires strict validation. *Rationale:* Providers add fields without a
new version; a client that fails on them fails on routine evolution.

### 3.4 Treat missing required data as a contract failure.

[REQUIRED] A response missing data the client depends on, or carrying an invalid value or format for
it, shall fail as a contract error rather than have a default substituted. *Rationale:* A substituted
value is indistinguishable downstream from a real one.

### 3.5 Leave everything unchanged when a response fails validation.

[REQUIRED] A response that fails validation shall change nothing the caller holds: the last good data
stays in place, and the failure is recorded where an operator will see it. *Rationale:* Applying part
of an invalid response leaves state that matches neither the old data nor the new.

### 3.6 Check the status before reading the body as a success.

[REQUIRED] A response shall not be deserialized as a success payload merely because it has a body; its
status shall be classified first (Section 7). *Rationale:* Many APIs return a body on failure, and a
client that parses it as success reads an error as data.

### 3.7 Verify the content type where safety depends on the representation.

[REQUIRED] A client shall reject or safely handle an unexpected media type rather than deserialize it
blindly. *Rationale:* An HTML error page from a proxy is not the JSON the client expected, and parsing
it as such produces nonsense or a crash.

### 3.8 Handle responses with no body.

[REQUIRED] A client shall not assume that every response, successful or not, carries a body or carries
JSON. *Rationale:* `204`, `304` and many intermediary errors have no body, and a client that assumes
one fails on normal traffic.

### 3.9 Parse problem details where the API returns them.

[REQUIRED] A client of an API that returns `application/problem+json` (RFC 9457) shall parse the
standard problem members and preserve the API-defined extension members the application needs.
*Rationale:* The problem type is the provider's stable, machine-readable statement of what went wrong;
discarding it leaves only a status code to branch on.

### 3.10 Bound response size, and stream large payloads.

[REQUIRED] A client consuming large or untrusted responses shall enforce a maximum response size or
stream the body, and large uploads and downloads shall be streamed rather than buffered whole when the
runtime and API support it. *Rationale:* An unbounded response is an unbounded allocation, and one
oversized reply can exhaust a process serving everyone else.

## 4. Versions and Change

### 4.1 Pin the API version where the API offers one.

[REQUIRED] Where an API is versioned by a header, a path or a date parameter, the client shall state
the version it was built against rather than accept the provider's current default. *Rationale:* An
unpinned client changes behaviour the day the provider moves its default.

### 4.2 Isolate version-specific models.

[REQUIRED] Request and response models specific to one API version shall be isolated, so migrating to
another version does not force uncontrolled changes across business code. *Rationale:* Version
changes arrive on the provider's schedule; isolation keeps them a contained piece of work.

### 4.3 Watch for deprecation and sunset signals.

[REQUIRED] A client shall detect the `Deprecation` and `Sunset` response headers, and equivalent
contract-defined signals, and surface them to operators — as a metric or a log event, once per
dependency and version rather than per call. *Rationale:* A provider announcing retirement in a header
is giving notice exactly once a caller can act on; ignored, it becomes an outage on the retirement
date.

### 4.4 Ignore session state on stateless calls.

[REQUIRED] A client of a stateless API shall not store or return cookies or other session state the
API sets, unless the contract requires it. *Rationale:* Carried session state couples calls that were
meant to be independent, and can route them differently from what the caller intends.

## 5. Connections and Transport

### 5.1 Reuse HTTP clients and connection pools.

[REQUIRED] Production code shall reuse long-lived HTTP client instances or managed connection pools; a
new client or transport shall not be created per request. *Rationale:* A client per request pays for
a TCP and TLS handshake on every call and exhausts sockets under load.

### 5.2 Bound the connection pool and waiting for it.

[REQUIRED] Pool size, idle-connection behaviour and waiting for a connection from the pool shall each
be bounded and configurable for the workload. *Rationale:* An unbounded wait for a pooled connection
is an unbounded call that no timeout on the request itself will catch.

### 5.3 Release every response.

[REQUIRED] Response bodies and transport resources shall always be consumed, closed or cancelled as
the HTTP library requires, so connections return to the pool. *Rationale:* A leaked response is a
leaked connection, and the pool drains one call at a time.

### 5.4 Support HTTP/2 where both sides do.

[RECOMMENDED] A client should use HTTP/2 when the runtime and the API support it, keeping correct
fallback. *Rationale:* Multiplexing reduces connection count and head-of-line waiting on busy
dependencies.

### 5.5 Never disable TLS verification.

[REQUIRED] Certificate and hostname verification shall not be disabled in production. *Rationale:*
Disabled verification makes every call interceptable, and it is the fix most often reached for when
connectivity fails.

### 5.6 Make proxy behaviour intentional.

[REQUIRED] Use of outbound proxies, service meshes or environment-derived proxy configuration shall be
explicit and understood for the deployment environment. *Rationale:* A proxy picked up from an
environment variable routes production traffic somewhere nobody chose.

### 5.7 Let endpoint changes take effect.

[REQUIRED] A long-lived client shall use connection and DNS behaviour that lets endpoint changes take
effect within an operationally acceptable period, and shall not hard-code resolved IP addresses unless
an infrastructure design requires it. *Rationale:* A client pinned to an address keeps calling a
failed or retired endpoint after the provider has moved.

### 5.8 Treat a discovery failure as a dependency failure.

[REQUIRED] DNS and service-discovery errors shall take part in timeout, retry, circuit-breaking and
telemetry policy like any other failure of the dependency. *Rationale:* Resolution is part of the
call; a failure there is the dependency being unavailable.

## 6. Timeouts and Deadlines

### 6.1 Give every logical call a deadline.

[REQUIRED] Every API call shall have an explicit maximum duration, derived from the caller's latency
budget or an approved default for its dependency class; infinite or effectively unbounded network
timeouts are prohibited. *Rationale:* A call without a deadline holds its thread, connection and
caller for as long as the remote side chooses.

### 6.2 Bound each phase where the library supports it.

[REQUIRED] Where the HTTP library supports it, connection establishment, pool acquisition, waiting for
response headers and reading the body shall each have their own bound, beneath the logical-call
deadline. *Rationale:* One overall timeout cannot tell a dead host from a slow response, and each
needs a different reaction.

### 6.3 Start a retry only if the remaining deadline can hold it.

[REQUIRED] A retry shall not begin when the time remaining on the logical call cannot reasonably
accommodate another attempt. *Rationale:* An attempt certain to be cut off is load on the dependency
with no possible benefit.

### 6.4 Propagate the remaining budget.

[REQUIRED] Where the ecosystem defines a deadline-propagation mechanism, a client shall pass on the
budget that remains rather than start a fresh one at each hop. *Rationale:* Fresh budgets at every hop
let a chain of calls outlive the request that started it.

### 6.5 Set timeout defaults per dependency class.

[RECOMMENDED] Timeout defaults should be configured per dependency or operation class, not as one
value for every external call. *Rationale:* A millisecond lookup and a multi-second partner call
cannot share a timeout that is right for both.

## 7. Outcomes and the Client Error Model

### 7.1 Classify every outcome explicitly.

[REQUIRED] A client shall distinguish successful responses, expected domain outcomes, authentication
and authorization failures, validation failures, throttling, server failures, contract failures,
timeouts, cancellation and transport failures. *Rationale:* Retry, fallback and reporting decisions
each depend on which of these happened; a client that cannot tell them apart makes all of them
wrongly.

### 7.2 Translate library exceptions into a stable client error model.

[REQUIRED] An application-facing client shall translate HTTP-library exceptions and responses into a
small, stable error model independent of the library, keeping the original cause available for
diagnostics without business code depending on it. *Rationale:* Business code that catches a
library's exception types is coupled to that library forever.

The recommended categories:

| Category | Meaning |
|---|---|
| `ClientValidationError` | The caller supplied an invalid request, detected before transmission |
| `AuthenticationError` | Authentication failed, or usable credentials could not be obtained |
| `AuthorizationError` | The identity is authenticated but not permitted |
| `NotFoundError` | The contract defines absence as an exceptional outcome |
| `ConflictError` | The request conflicts with the remote state |
| `RateLimitError` | The dependency refused work because of throttling or quota |
| `RemoteValidationError` | The remote API rejected the request's content |
| `RemoteServiceError` | The remote service returned a server failure |
| `TimeoutError` | The logical call or one of its phases exceeded its bound |
| `TransportError` | DNS, connection, TLS, reset or an equivalent transport failure |
| `ContractError` | The response violated the caller's owned schema or could not be safely interpreted (Section 3) |
| `CancelledError` | The caller or its execution context cancelled the operation |
| `AmbiguousOutcomeError` | A mutation may have executed, but no definitive result was received (Section 9) |

### 7.3 Represent expected domain outcomes as outcomes.

[REQUIRED] A non-2xx response that the contract defines as an expected domain outcome — a lookup that
finds nothing, a conflict the caller handles — shall be represented as the client contract defines it,
not as an undifferentiated exception. *Rationale:* A caller that must catch an exception to learn that
a record does not exist writes control flow around errors.

### 7.4 Preserve actionable remote error information.

[REQUIRED] A client error shall carry the remote status, the stable problem type or error code, the
callee's request identifier (Section 13) and safe diagnostic context. *Rationale:* These are what a
support case with the provider is resolved from.

### 7.5 Never put raw response bodies in errors.

[REQUIRED] Exceptions and logs shall not include whole remote response bodies. *Rationale:* Error
bodies echo request data, and a raw body in an exception reaches every log and error tracker it passes
through.

## 8. Retries and Backoff

### 8.1 Give one layer ownership of retries.

[REQUIRED] Exactly one layer shall own automatic retries for a logical call. Retries in HTTP libraries,
SDKs, service meshes, gateways and the calling workload's own retry of a failed unit of work shall be
counted when the effective policy is designed, and layers shall not independently multiply attempts
unless the combined worst-case attempts and duration are explicitly designed and bounded.
*Rationale:* Three layers retrying three times each is twenty-seven attempts against a dependency
already failing.

### 8.2 Retry only transient failures.

[REQUIRED] Automatic retries shall be limited to failures reasonably expected to succeed without
changing the request: selected connection failures, timeouts, throttling and temporary unavailability.
*Rationale:* Repeating a request that cannot succeed delays the real failure and adds load.

### 8.3 Do not retry client errors by default.

[REQUIRED] `4xx` responses shall not be retried automatically, except `408`, `429` and API-specific
transient responses under an explicit policy; deterministic failures — invalid input, violated
business rules, unsupported state — shall not be retried without a change in the request or the
state. *Rationale:* An identical request that the server has deterministically refused will be refused
again.

### 8.4 Bound retry attempts.

[REQUIRED] Every retry policy shall define a maximum attempt count and remain within the logical-call
deadline. *Rationale:* Attempts bounded only by time, or only by count, are not bounded under every
failure.

### 8.5 Back off exponentially, with jitter.

[REQUIRED] Retries of transient failures shall use exponential backoff with jitter, or an equivalent
strategy that avoids synchronized retry, and immediate retries are prohibited unless explicitly
justified. *Rationale:* Backoff relieves a failing dependency, and jitter stops many clients that
failed together from retrying together.

### 8.6 Honour `Retry-After`.

[REQUIRED] When a retryable response carries a valid `Retry-After`, the client shall wait at least
that long, unless waiting would exceed the logical-call deadline or a configured maximum delay — in
which case it shall fail the call rather than retry sooner. *Rationale:* The provider has stated when
it can take the request; retrying earlier is refused and prolongs the throttling.

### 8.7 Never retry an unsafe operation without duplicate protection.

[REQUIRED] A non-idempotent operation shall not be retried automatically unless the contract provides
an idempotency mechanism (Section 9) or the client can otherwise prove a duplicate is harmless.
*Rationale:* A retried payment is two payments.

### 8.8 Judge retry eligibility by the operation, not only the method.

[RECOMMENDED] `GET`, `HEAD`, `OPTIONS`, `PUT` and `DELETE` may be eligible for retry, but the HTTP
method shall not override the API's documented side effects. *Rationale:* A `GET` that sends an email
and a `DELETE` that fires a webhook are not safe to repeat because of their verbs.

### 8.9 Record why an attempt was retried.

[REQUIRED] Telemetry shall record the attempt number and the reason for each additional attempt,
without unbounded metric cardinality. *Rationale:* Retries hide failures; recording them is how a
dependency degrading behind a retry policy becomes visible.

## 9. Idempotency and Ambiguous Outcomes

### 9.1 Use the API's idempotency keys for retryable mutations.

[REQUIRED] When an API provides an idempotency-key mechanism, a client shall use it for every mutation
it may retry. *Rationale:* It is the only way the server can recognize a retry as the same request.

### 9.2 Keep one key per logical operation.

[REQUIRED] Every attempt of one logical operation shall carry the same idempotency key, and a new
logical operation shall use a new one. *Rationale:* A key regenerated per attempt protects nothing; a
key reused across operations suppresses a real request.

### 9.3 Do not treat a transport failure as an operation failure.

[REQUIRED] When a connection fails after the request may have reached the server, the client shall
treat the outcome as unknown unless idempotency or a status lookup establishes it. *Rationale:* The
server may have completed the work and only the response was lost.

### 9.4 Reconcile an ambiguous outcome before repeating a mutation.

[RECOMMENDED] For consequential mutations, a client should resolve an ambiguous outcome — through an
operation lookup, the idempotency result or a domain query — before issuing a request that could
duplicate it. *Rationale:* Reconciling first is the difference between one order and two.

## 10. Rate Limits, Concurrency and Backpressure

### 10.1 Bound concurrent calls to each dependency.

[REQUIRED] Every application shall have a mechanism that prevents unbounded concurrent calls to a
dependency. *Rationale:* Unbounded concurrency turns a slow dependency into exhausted threads,
connections and memory in the caller.

### 10.2 Respect the API's rate limits.

[REQUIRED] Published quotas and runtime throttling responses shall shape client behaviour, and a
`429 Too Many Requests` or an equivalent contract-defined throttling response shall never cause an
immediate repeated request. *Rationale:* A client that ignores throttling is throttled harder, and
may be blocked.

### 10.3 Regulate the request rate for known quotas.

[RECOMMENDED] Where a dependency has a known quota, the client should regulate its own request rate
rather than rely on the server's refusals. *Rationale:* Staying under a quota costs nothing; being
refused costs a failed call and a backoff each time.

### 10.4 Bound the work queued behind a client.

[REQUIRED] Local queues, pending tasks and pool waiters created by calling an API shall be bounded, and
the client shall define what happens when that bound is reached — fail fast or shed load — rather
than let waiting work accumulate. *Rationale:* An unbounded queue in front of a slow dependency is
latency that grows until the process fails.

### 10.5 Separate limits for materially different operations.

[RECOMMENDED] Expensive or latency-sensitive operations should have their own concurrency limits when a
shared limit would let one starve another. *Rationale:* Bulk exports sharing a limit with interactive
lookups make the lookups wait behind the exports.

## 11. Circuit Breaking and Failure Isolation

### 11.1 Break the circuit on a failing dependency.

[RECOMMENDED] A long-lived service calling a failure-prone dependency should use circuit breaking, or
adaptive concurrency, where continued calls during a failure would consume meaningful resources or
amplify it. *Rationale:* A breaker stops a fleet of callers from continuously attacking an unhealthy
dependency and gives it room to recover.

### 11.2 Make a breaker bounded and recoverable.

[REQUIRED] A circuit breaker shall define its failure criteria, open duration, half-open probing and
recovery. *Rationale:* A breaker without a recovery path turns a transient outage into a permanent
one.

### 11.3 Do not count expected outcomes as failures.

[REQUIRED] An expected response — a valid `404` for a lookup — shall not trip a breaker merely because
its status is not 2xx. *Rationale:* Counting domain outcomes as failures opens circuits on healthy
dependencies.

### 11.4 Isolate one dependency's failure from unrelated work.

[REQUIRED] The failure of one dependency shall not fail work that does not need it: connection pools,
concurrency limits and resilience state shall be separated where one dependency's exhaustion would
otherwise consume what another needs, and work that calls several dependencies shall record each
dependency's outcome on its own. *Rationale:* One provider's outage should leave every other
provider's results intact.

### 11.5 Use a fallback only where the semantics permit it.

[REQUIRED] Stale, partial, cached or substituted results shall be used as a fallback only where the
business semantics explicitly permit them, and shall be distinguishable as such. *Rationale:* A
fallback nobody can tell from a real answer is silent data corruption.

## 12. Authentication and Credentials

### 12.1 Use the API's approved identity mechanism, with least privilege.

[REQUIRED] A client shall authenticate with the API's approved mechanism — OAuth 2.0 access tokens,
workload identity, mTLS or an approved API-key scheme — using credentials that grant only what the
calling workload needs. *Rationale:* An over-privileged credential turns a compromised client into a
compromised dependency.

### 12.2 Obtain credentials from the platform's secret or identity mechanism.

[REQUIRED] API keys, client secrets, private keys and long-lived tokens shall come from the approved
secret-management or workload-identity mechanism, never from source code or checked-in configuration.
*Rationale:* A credential in code is shared with everyone who can read the repository and cannot be
rotated without a release.

### 12.3 Cache tokens, and refresh them once.

[REQUIRED] Access tokens shall be reused until close to expiry rather than fetched per call, and
concurrent callers shall not cause a refresh storm when a cached token expires. *Rationale:* A token
per call doubles the calls and loads the identity provider; unsynchronized refresh does the same all
at once.

### 12.4 Bound credential acquisition.

[REQUIRED] Obtaining or refreshing a credential shall have its own bounded timeout and retry policy,
and shall count against the caller's overall budget. *Rationale:* An identity provider that hangs is a
dependency that hangs.

### 12.5 Do not blindly retry authentication and authorization failures.

[REQUIRED] A `401` may trigger at most the supported credential refresh or re-authentication flow,
once; a `403` shall not be treated as retryable unless the contract says otherwise. *Rationale:* A
refused credential refused again is still refused, and repeated refusals can lock an account.

### 12.6 Never put a credential in a URL.

[REQUIRED] Secrets and bearer tokens shall not be placed in query strings or URL paths. *Rationale:*
URLs are logged by every proxy, gateway and server they pass through.

### 12.7 Never log, trace or report a credential.

[REQUIRED] Authorization headers, cookies, tokens, API keys, client secrets and private keys shall not
appear in logs, traces, metrics, exceptions or error bodies. *Rationale:* Every place a credential is
written is a place it can be read from.

## 13. Correlation and Tracing

### 13.1 Propagate trace context.

[REQUIRED] A client taking part in distributed tracing shall inject the organization's trace context
into every outbound request, in its approved propagation format. *Rationale:* Without it, the trace
ends at the caller and the dependency's share of the latency is invisible.

### 13.2 Propagate the correlation identifier.

[RECOMMENDED] Where the ecosystem uses a correlation identifier beside tracing, a client should
propagate it on every call. *Rationale:* It ties a caller's log lines to the dependency's.

### 13.3 Record the callee's request identifier.

[REQUIRED] Where the API returns a request identifier (`Request-Id`, `X-Request-Id` or a
contract-defined equivalent), the client shall record it with the call's telemetry and carry it in the
client error (Section 7.4). *Rationale:* It is the one value a provider's support needs to find the
call in its own logs.

## 14. Pagination and Collections

### 14.1 Follow the API's pagination mechanism.

[REQUIRED] A client shall use the API's continuation token, cursor, next link or page mechanism, and
shall not reconstruct undocumented pagination state. *Rationale:* Hand-built page offsets break when
the provider changes page size or ordering.

### 14.2 Treat cursors as opaque.

[RECOMMENDED] A server-provided continuation value should be treated as opaque and passed back
unchanged. *Rationale:* Its format is the provider's to change.

### 14.3 Bound automatic pagination.

[REQUIRED] A helper that traverses pages automatically shall support limits on pages, records, bytes
or duration, and cancellation, suited to its use. *Rationale:* A collection that grows without bound
turns an unbounded loop into an outage.

### 14.4 Never load an unbounded collection into memory.

[REQUIRED] Large result sets shall be exposed through iteration, streaming or paging, never
materialized whole. *Rationale:* Memory is the bound nobody configured.

### 14.5 Respect the collection's consistency rules.

[REQUIRED] A client shall respect documented snapshot, ordering, cursor-expiry and continuation
semantics. *Rationale:* Pages read across an expired cursor, or re-sorted between pages, silently skip
or repeat records.

## 15. Caching and Conditional Requests

### 15.1 Cache a response only where its semantics permit.

[REQUIRED] Application-level response caching shall be used only where it is explicitly permitted for
the operation and the sensitivity of the data. *Rationale:* A cached answer is a claim about the
dependency's current state that may no longer be true.

### 15.2 Give every cache a freshness bound.

[REQUIRED] Every cache shall have explicit freshness and expiry; indefinite caching is prohibited
unless the data is immutable by contract. *Rationale:* A cache without expiry serves the first answer
forever.

### 15.3 Scope cache keys to everything that changes the answer.

[REQUIRED] Cache keys and scope shall account for organization, identity, authorization context,
locale and every other dimension that changes a response. *Rationale:* A key missing the identity
serves one caller's data to another.

### 15.4 Use conditional requests where the API supports them.

[RECOMMENDED] A client should use `ETag`/`If-None-Match`, `Last-Modified`/`If-Modified-Since` or the
contract's conditional mechanism where it materially reduces transfer. *Rationale:* A `304` costs the
provider and the network almost nothing.

## 16. Optimistic Concurrency

### 16.1 Use the API's concurrency controls when it provides them.

[REQUIRED] An update to a mutable resource shall use the API's ETags, versions or other preconditions
wherever a lost update is possible. *Rationale:* Without a precondition, the last writer silently
discards the others' changes.

### 16.2 Never overwrite a conflict silently.

[REQUIRED] A failed precondition shall be surfaced, or reconciled by explicit domain logic; it shall
not be retried automatically against the newest version. *Rationale:* Retrying with the latest ETag is
exactly the lost update the precondition exists to prevent.

## 17. Redirects

### 17.1 Follow redirects only by intent, and boundedly.

[REQUIRED] Automatic redirect following shall be explicitly configured or knowingly accepted from the
library, with a maximum hop count. *Rationale:* A library's default can follow redirects without limit
and anywhere.

### 17.2 Never carry credentials across origins on a redirect.

[REQUIRED] Authorization headers and other credentials shall not be forwarded to a different or
untrusted origin because a redirect was received. *Rationale:* A redirect is an instruction from a
response; following it with credentials hands them to whoever wrote it.

### 17.3 Call canonical URLs directly.

[RECOMMENDED] Service-to-service calls should use canonical endpoint URLs rather than rely on
redirects during normal operation. *Rationale:* Every redirect is an extra round trip and an extra
place for the credential rule to fail.

## 18. Security and Data Sent

### 18.1 Use TLS across every trust boundary.

[REQUIRED] API traffic crossing a process or trust boundary in production shall use TLS, unless an
approved infrastructure layer provides equivalent protected transport, and the client shall verify the
remote endpoint's identity. *Rationale:* Unencrypted or unverified calls expose credentials and data
to anyone on the path.

### 18.2 Prevent server-side request forgery.

[REQUIRED] Where any part of a destination can be influenced by untrusted input, the client shall
enforce a destination allowlist or an equivalent control. *Rationale:* A user-controlled URL fetched
from inside the network reaches whatever the network can.

### 18.3 Restrict egress for sensitive workloads.

[RECOMMENDED] A workload handling sensitive data should run under network egress controls, so
compromised logic cannot call arbitrary endpoints. *Rationale:* Egress limits bound the damage of a
defect or compromise that no code review caught.

### 18.4 Send only what the call needs, where it is permitted to go.

[REQUIRED] A request shall carry only the data the operation needs; sensitive data shall be sent only
to dependencies approved for its classification; a customer's data shall go only to a dependency, host
or region the customer authorized, honouring any data-residency choice they made. *Rationale:* Data
sent is data the caller no longer controls.

## 19. Cancellation

### 19.1 Propagate the caller's cancellation.

[REQUIRED] Where the execution model supports cancellation, an API call shall accept and propagate
cancellation from its caller, and a cancelled logical call shall start no further attempts.
*Rationale:* Work nobody is waiting for is load with no beneficiary.

### 19.2 Cancellation does not undo a remote mutation.

[REQUIRED] Cancelling the local wait for a mutation shall not be treated as proof that the remote
operation did not execute; the outcome is ambiguous (Section 9). *Rationale:* The server may already
have done the work.

## 20. Configuration

### 20.1 Make endpoints configuration.

[REQUIRED] API base URLs and environment-specific routing shall be configuration, not compiled
business logic. *Rationale:* An endpoint in code cannot differ between environments without a
separate build.

### 20.2 Keep resilience policy in one discoverable place.

[REQUIRED] Timeout, retry, concurrency and circuit-breaker settings shall be defined in discoverable
per-client or per-dependency configuration, not scattered among call sites. *Rationale:* A policy
nobody can find cannot be reviewed or changed safely.

### 20.3 Validate configuration at startup, with safe bounds.

[REQUIRED] An invalid required endpoint, timeout, credential reference or resilience setting shall fail
startup rather than fail a later call, and runtime-configurable values shall be validated against
minimum and maximum bounds so configuration cannot create infinite retries, extreme timeouts or
unbounded concurrency. *Rationale:* A misconfiguration found at startup is a failed deploy; found at
runtime it is an incident.

## 21. Observability

### 21.1 Trace every outbound call, with its attempts.

[REQUIRED] A production client shall emit a trace span for each outbound HTTP operation under the
organization's telemetry conventions (OpenTelemetry HTTP client conventions or equivalent), and where
individual attempts are instrumented, retries shall be distinguishable while correlated to the logical
call. *Rationale:* A span per call with no attempt detail hides the retries that explain its latency.

### 21.2 Measure latency and outcomes per dependency.

[REQUIRED] A client shall record request duration, volume, failures, timeouts, throttling, retries,
validation failures and circuit-breaker state, by low-cardinality dependency and operation
dimensions, so a degrading dependency is visible before its callers fail. *Rationale:* Per-dependency
measurement is what points an operator at the right dependency.

### 21.3 Keep telemetry dimensions low-cardinality.

[REQUIRED] Raw URLs containing identifiers, request identifiers, user identifiers, arbitrary query
values, exception messages and payload values shall not be metric dimensions; operations shall be
identified by route or URL templates. *Rationale:* High-cardinality labels break the metrics system
before they help anyone.

### 21.4 Identify the dependency.

[REQUIRED] Telemetry shall identify the remote service or server address well enough for
dependency-level troubleshooting, without exposing secrets. *Rationale:* "An API call failed" names no
one to call.

### 21.5 Alert on repeated validation failures.

[RECOMMENDED] Repeated response-validation failures from one dependency should raise an alert rather
than wait to be noticed in a dashboard. *Rationale:* They are the signal that a provider changed its
format, and nothing downstream will fail loudly while the last good data stays in place (Section 3.5).

## 22. Logging

### 22.1 Log API calls as structured events.

[REQUIRED] API-client logs shall use structured fields suitable for correlation and querying: the
dependency and client name, the logical operation, method, route template, status, elapsed time,
attempt number, retry reason, trace or correlation identifier, the callee's request identifier and the
error category. *Rationale:* Structured fields are queryable; prose log lines are not.

### 22.2 Log a failure once, where the context is.

[RECOMMENDED] A logical failure should be logged once, by the layer with enough operational context,
not at every abstraction layer it passes through. *Rationale:* One failure logged five times reads as
five failures.

### 22.3 Keep payloads out of logs by default.

[REQUIRED] Request and response body logging shall be disabled by default and enabled only under an
approved redaction and data-classification policy. *Rationale:* Payloads carry the data every other
rule in this standard protects.

### 22.4 Sanitize URLs before logging them.

[REQUIRED] A full URL shall not be logged where its query parameters may carry sensitive or
high-cardinality values. *Rationale:* A query string is where tokens and identifiers end up.

## 23. Testing

### 23.1 Test request construction.

[REQUIRED] Tests shall verify each client operation's method, path, query parameters, headers,
serialization and API-specific contract behaviour. *Rationale:* A request built wrong is refused, or
worse, accepted and misread.

### 23.2 Test response classification and validation.

[REQUIRED] Tests shall cover expected successes, domain outcomes, representative `4xx`, `429` and
`5xx` responses, empty responses, and responses that fail the owned schema — missing required fields,
unknown additive fields, invalid values, unexpected content types, malformed payloads — including that
a failed validation changes nothing. *Rationale:* Classification and validation are where a client is
wrong without anyone noticing.

### 23.3 Test retry boundaries.

[REQUIRED] Tests shall verify which failures are retried and which are not, the maximum attempts,
backoff, `Retry-After` handling and the total deadline. *Rationale:* A retry policy that has never been
exercised has an unknown effective policy.

### 23.4 Test duplicate safety.

[REQUIRED] Every automatically retried mutation shall have tests proving idempotency-key reuse or an
equivalent duplicate protection. *Rationale:* Duplicate charges are found by customers otherwise.

### 23.5 Test timeouts and cancellation.

[REQUIRED] Tests shall cover connection timeout, response timeout and the overall deadline where
supported, and that cancellation stops waiting and retries and releases local resources. *Rationale:*
Bounds that are only configured are assumed, not known.

### 23.6 Test credentials and redaction.

[REQUIRED] Tests shall cover token refresh, refresh concurrency, expired credentials and authorization
failures, and shall confirm that credentials and protected payload fields are absent from traces,
metrics and logs. *Rationale:* A leaked credential is found only by looking for it.

### 23.7 Test under resource exhaustion.

[REQUIRED] Important clients shall be tested under pool saturation, concurrency limits, slow
dependencies and large responses. *Rationale:* Those are the conditions under which a client takes its
caller down with it.

### 23.8 Test against a representative implementation.

[RECOMMENDED] A client should be tested against a representative implementation of the API — a mock
generated from its contract, a sandbox or the provider's test environment — as well as with unit tests,
and critical clients should be exercised in pre-production with injected latency, connection failures,
throttling, malformed responses and unavailability. *Rationale:* Unit tests prove the client matches
its author's idea of the API; these prove it matches the API.

## 24. Per-Client Decisions

[REQUIRED] Every production API client shall document, configure or inherit an explicit value for
each of the following. *Rationale:* Each is a decision a library will otherwise make silently.

| Concern | Decision |
|---|---|
| Base endpoint | The environment-specific endpoint |
| Authentication | Identity mechanism, scopes or audience, credential source |
| API version | The version pinned (Section 4.1) |
| Response schema | The owned schema the response is validated against (Section 3.2) |
| Connect timeout | Maximum connection-establishment time |
| Pool acquisition timeout | Maximum wait for local connection capacity |
| Operation deadline | Maximum logical-call duration |
| Retryable operations | Which operations and methods are eligible |
| Retryable failures | Which statuses and exceptions are classified transient |
| Maximum attempts | Physical attempts per logical call |
| Backoff | Initial delay, growth, jitter, maximum delay |
| `Retry-After` | Handling, and the maximum accepted delay |
| Concurrency | Maximum in-flight calls, or the limiter used |
| Rate limit | The provider's quota, and the client-side policy |
| Circuit breaker | Whether used, and its thresholds |
| Response size | Maximum buffered size, or the streaming policy |
| Pagination | Page, record and duration bounds |
| Error mapping | Remote errors onto the client error model |
| Idempotency | The mutation duplicate-protection mechanism |
| Telemetry | Dependency name, operation naming, redaction |
| Data classification | What data may leave the calling service for this dependency |

## 25. Implementation Defaults

[REQUIRED] Where an API-specific requirement or a measured service level gives no better value, a
client shall use these defaults. *Rationale:* A stated default is reviewable; an inherited library
default is not.

| Setting | Default |
|---|---|
| HTTP client lifetime | Long-lived or framework-managed; never per request |
| Connection pooling | Enabled and bounded |
| TLS verification | Enabled |
| Logical-call deadline | Required, chosen from the dependency's latency budget |
| Maximum attempts | 3 in total, for eligible operations |
| Backoff | Exponential, with jitter |
| Immediate retry | Prohibited unless explicitly justified |
| `Retry-After` | Honoured within the remaining deadline and the configured maximum |
| Mutation retry | Disabled unless duplicate-protected |
| Automatic redirects | Disabled for service clients unless required; otherwise at most 3 hops |
| Response buffering | Bounded; large responses streamed |
| Response validation | Against the owned schema, before use |
| Unknown response properties | Tolerated |
| Missing required properties | Contract failure |
| Caller cancellation | Propagated |
| Trace propagation | Enabled |
| Payload logging | Disabled |
| Credential logging | Prohibited |
| Retry ownership | One layer |
| Concurrency and pending work | Explicitly bounded |

The logical-call deadline has no universal numeric default on purpose. A 500 ms internal lookup, a
5-second partner call and a multi-minute export initiation have different budgets; each client
chooses its value while keeping an explicit upper bound.

------------------------------------------------------------------------

## Appendix A — Reference Execution Flow

A conforming client behaves, conceptually, as follows:

1.  Validate the caller's input.
2.  Resolve the configured endpoint and operation.
3.  Obtain or reuse credentials.
4.  Establish the logical-call deadline and cancellation context.
5.  Acquire concurrency and rate-limit capacity.
6.  Construct the request from the API contract, pinning its version.
7.  Attach trace and correlation context, and the idempotency key where applicable.
8.  Make one physical attempt over the pooled transport.
9.  Classify the outcome.
10. If it is retryable, check duplicate safety, the remaining deadline, the retry budget and
    cancellation.
11. Wait for `Retry-After` where given; otherwise back off exponentially with jitter.
12. Repeat only within the attempt and time budgets.
13. Validate the final response against the owned schema, and use it only if it passes.
14. Translate transport and protocol details into the client's result or error model.
15. Release every response, connection, limiter and cancellation resource.
16. Emit the logical call's telemetry, without secrets or uncontrolled cardinality.

## Appendix B — Implementation Checklist

An engineer or AI generating an API client shall be able to answer **yes** to each applicable item:

-   [ ] Calls go through a dedicated client for the API.
-   [ ] The HTTP client and its pool are reused, not created per request.
-   [ ] Connection pools and pending work are bounded.
-   [ ] Connection, acquisition, response and total call time are bounded.
-   [ ] The API version is pinned where the API offers one.
-   [ ] Every response is validated against a schema the caller owns before use.
-   [ ] A response that fails validation changes nothing.
-   [ ] `Deprecation` and `Sunset` signals reach operators.
-   [ ] Retry ownership is explicit, and hidden retries are accounted for.
-   [ ] Retryable failures are explicitly classified.
-   [ ] Retries are bounded and use exponential backoff with jitter.
-   [ ] `Retry-After` is honoured.
-   [ ] Mutation retries are protected by idempotency keys or equivalent.
-   [ ] Ambiguous mutation outcomes are handled explicitly.
-   [ ] Outbound concurrency is bounded, and provider rate limits are respected.
-   [ ] Circuit breaking is considered for long-lived services.
-   [ ] One dependency's failure does not fail unrelated work.
-   [ ] Credentials are least-privilege and come from the approved mechanism.
-   [ ] Tokens are cached, and refresh is concurrency-safe.
-   [ ] Credentials never appear in URLs, logs, traces, metrics or errors.
-   [ ] Trace context is propagated, and the callee's request identifier is recorded.
-   [ ] Response status and content type are checked before the body is used.
-   [ ] Problem details are parsed where the API uses them.
-   [ ] Large responses are bounded or streamed.
-   [ ] Pagination cannot retrieve an unbounded result by accident.
-   [ ] Optimistic concurrency controls are used where the API provides them.
-   [ ] Redirects are disabled, or bounded and credential-safe.
-   [ ] Endpoint changes can take effect for long-lived clients.
-   [ ] Only permitted data is sent, to permitted destinations.
-   [ ] Client errors use a stable, library-independent model.
-   [ ] Caller cancellation propagates.
-   [ ] Traces and per-dependency metrics are emitted with low cardinality.
-   [ ] Payload logging is off by default.
-   [ ] Tests cover timeouts, retries, throttling, validation failures, credential refresh,
    cancellation and duplicate safety.

## Appendix C — Anti-Patterns

Each of these is prohibited by a requirement above:

-   Creating a new HTTP client or connection pool per request.
-   Infinite network timeouts.
-   Retrying every exception or every non-2xx response.
-   Retrying `POST` or other mutations without duplicate-safety analysis.
-   Immediate or fixed-delay retries that create retry storms.
-   Layering application, SDK, mesh and gateway retries without calculating their combined effect.
-   Treating a timeout as proof that a remote mutation did not execute.
-   Retrying `401`, `403`, validation errors or business conflicts without a contract-specific reason.
-   Using a response before validating it, or applying part of one that failed validation.
-   Accepting a provider's current API version by default.
-   Logging bearer tokens, cookies, API keys or whole sensitive payloads.
-   Using raw URLs containing identifiers as metric labels.
-   Forwarding inbound headers wholesale to a downstream API.
-   Loading an arbitrarily paginated result set into memory.
-   Disabling TLS verification to fix a connectivity problem.
-   Hard-coding production endpoints or credentials.
-   Letting untrusted input select arbitrary outbound hosts.
-   Hiding every remote failure behind one generic "API call failed" error.

## Glossary

**API client** --- A component responsible for invoking operations exposed by an API it does not own.

**Logical call** --- The application-level invocation of an API operation, including every physical
attempt needed to reach a final result.

**Physical attempt** --- One transmission of a request over the network.

**Deadline** --- The latest time by which a logical call must complete.

**Timeout** --- A bound on one wait or phase, such as connection establishment or reading a response.

**Retry budget** --- The bounded number of attempts, and time, available for retries.

**Owned schema** --- The JSON Schema a caller keeps for an API's responses, covering what it depends
on; the caller's statement of the contract as it uses it.

**Idempotency key** --- A stable identifier sent with every attempt of one logical mutation so the
server can recognize duplicates.

**Ambiguous outcome** --- A mutation whose execution the client cannot confirm or rule out.

**Backpressure** --- Mechanisms that stop work from overwhelming a dependency or the client's own
resources.

**Circuit breaker** --- A mechanism that temporarily stops calls to a dependency after defined failure
conditions are met.

**Problem details** --- The machine-readable HTTP API error representation `application/problem+json`.
