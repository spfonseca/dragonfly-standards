# RESTful API Design Standard

**Status:** Normative. Requirements use "shall" (mandatory) and "should" (recommended). Waivers require explicit, documented, and approved rationale.

**About this draft:** This is the first fully-seeded draft. Its structure is a flat, two-level hierarchy — each top-level section is a *requirements area*, and each numbered sub-section is a single *requirement* written as a direction-setting action sentence, followed by its normative statement, rationale, obligation level, and (where useful) an example. Requirements carry an obligation tag: **[REQUIRED]** (shall), **[RECOMMENDED]** (should), or **[OPTIONAL]** (may). Content was seeded from established industry guidelines (Google, Microsoft/Azure, Zalando, PayPal) and the organization's own prior standard; the organization's specific design preferences will be layered in over subsequent revisions.

> **Open-decision markers.** Where a newly-seeded requirement would extend or contradict an existing organizational decision (most often the constrained HTTP status set in §14), it is flagged inline as **⚠ Open decision** for adjudication rather than assumed.

---

## 1. Scope & Conformance

### 1.1 Express mandatory rules with "shall" and recommendations with "should."
**[REQUIRED]** This document expresses obligations with the keywords "shall"/"shall not" (mandatory), "should"/"should not" (recommended), and "may" (optional), interpreted per RFC 2119. Each requirement additionally carries an explicit obligation tag.
*Rationale:* A single, well-known vocabulary removes ambiguity about what is enforceable at design review versus advisory.

### 1.2 Apply this standard to every RESTful API the organization produces.
**[REQUIRED]** This standard governs all HTTP APIs offered to internal or external consumers, regardless of hosting model or business domain.
*Rationale:* Consistency is only valuable when it is universal; per-team dialects reintroduce exactly the friction the standard exists to remove.

### 1.3 Grant exceptions only through an explicit, documented, approved waiver.
**[REQUIRED]** Any deviation shall be recorded with its rationale and approved by the API review committee before development proceeds; the degree of adherence for each API is set at planning time, with full adherence as the default.
*Rationale:* Undocumented deviations are indistinguishable from defects and erode consumer trust in the catalog as a whole.

### 1.4 Defer to the named governing documents wherever this standard yields.
**[RECOMMENDED]** Where this standard defers — metadata constraints, domain names, layering, information vocabularies — the API Program Framework, Application Services Architecture, Information Architecture, and Infrastructure Services Architecture govern.
*Rationale:* Keeping cross-cutting concerns in their authoritative source prevents drift between overlapping documents.

---

## 2. API Product & Governance

### 2.1 Tie every API to named, high-value customer workflows.
**[REQUIRED]** Each API shall be associated with named application workflows, each linked to a customer segment or specific customer, balancing internal and external needs per the API Adoption Strategy.
*Rationale:* APIs built without a demonstrated consumer become unused surface area that still carries lifecycle and security cost.

### 2.2 Quantify and justify return on investment before design proceeds.
**[REQUIRED]** ROI shall be quantified during roadmap planning and stored with the API product documentation; design shall not proceed until the return is deemed sufficient.
*Rationale:* Front-loading the economic decision prevents sunk-cost commitment to low-value interfaces.

### 2.3 Design each API for reuse across multiple consumers.
**[RECOMMENDED]** APIs should be understandable within minutes, appropriately granular, well abstracted, consistent, documented, and discoverable, so a single design serves many workflows.
*Rationale:* Reuse is where the standardization overhead pays back; single-purpose APIs multiply catalog size without multiplying value.

### 2.4 Size and group APIs into a small, cohesive, discoverable catalog.
**[RECOMMENDED]** Group related resources into cohesive APIs, limit the total number of APIs, and separate resources with sharply different evolution profiles — with cohesion generally taking precedence over evolvability.
*Rationale:* Consumers find and reason about a small, well-organized catalog far faster than a large, fragmented one.

### 2.5 Make the common workflows the easiest ones to code.
**[RECOMMENDED]** Provide sensible defaults, coarse-grained interactions that control call volume, simple data types over deep hierarchies, and responses that chain naturally into subsequent requests.
*Rationale:* The first developer experience is decisive for adoption; the common path must be the path of least resistance.

### 2.6 Apply the organization's shared conventions uniformly across all APIs.
**[REQUIRED]** Naming, verb semantics, parameter names and semantics, information models, standardized responses, and shared idioms shall be uniform across all APIs.
*Rationale:* Learned-once conventions let a consumer move between APIs without relearning idioms.

### 2.7 Pass an API Design Review before development begins.
**[REQUIRED]** Designs shall be assessed offline by the review committee against the API Design Checklists, then adjudicated in an API Design Review before development may proceed.
*Rationale:* Interface mistakes are cheap to fix before code exists and expensive afterward, because the interface is the client contract.

### 2.8 Capture the required API metadata by design-review time.
**[REQUIRED]** API metadata shall be captured per the Application Services Architecture and available at design review.
*Rationale:* Governance, discovery, and runtime management all depend on complete metadata being present when decisions are made.

---

## 3. Versioning

### 3.1 Increment the major version for incompatible changes and the minor for compatible ones.
**[REQUIRED]** Increment the major number for any backward-incompatible change and the minor number for changes that preserve the client contract; minimize major upgrades and verify every minor upgrade as backward compatible.
*Rationale:* A predictable version contract lets consumers upgrade minors freely and plan for majors deliberately.

### 3.2 Treat any behavior-altering syntactic or semantic difference as backward-incompatible.
**[REQUIRED]** A backward-incompatible change is any syntactic or semantic difference that can alter behavior a client was guaranteed.
*Rationale:* A shared, precise definition prevents breaking changes from being mislabeled as minor.

### 3.3 Format versions as "V{major}.{minor}", starting the major at 1.
**[REQUIRED]** Version identifiers use the syntax `"V" MajorNumber "." MinorNumber`, with the major number starting at 1.
*Rationale:* A single fixed syntax makes versions parseable by both humans and tooling.
*Example:* `V1.3`

### 3.4 Label pre-release versions sequentially as "V{n}-Alpha".
**[REQUIRED]** Alpha versions use the syntax `"V" Number "-Alpha"`, incrementing sequentially from `V1-Alpha` per alpha release.
*Rationale:* Distinct alpha labeling keeps experimental interfaces from being mistaken for production contracts.

### 3.5 Version top-level resources on the same scheme, and never version sub-resources.
**[REQUIRED]** Top-level resources use the same major.minor scheme as APIs; sub-resources are not versioned, and a backward-incompatible sub-resource change increments the parent resource version.
*Rationale:* Versioning only at the top level keeps the version surface small and unambiguous.

### 3.6 Resolve an omitted minor number in a URL to the latest minor of that major.
**[REQUIRED]** A URL that omits the minor number selects the latest minor version of that major; a URL that pins the minor selects exactly that version.
*Rationale:* Consumers get automatic compatible improvements by default while retaining the ability to pin.
*Example:* `/user/customers/V1` resolves to `V1.5` if that is latest; `/user/customers/V1.3` pins `V1.3`.

---

## 4. Compatibility & Deprecation

### 4.1 Never break existing client code.
**[REQUIRED]** The golden rule: released endpoint–verb combinations shall not change in a way that breaks conforming clients. Rate every endpoint–verb combination for design certainty (1 = high certainty … 5 = high uncertainty) at review; high-uncertainty pairings shall not ship to production, and only the minimum viable API — combinations with clear business justification — is released.
*Rationale:* Broken clients are the single most damaging outcome for an API program's reputation.

### 4.2 Batch backward-incompatible changes into a single major-version upgrade.
**[RECOMMENDED]** Accumulate breaking changes and release them together in one major version whenever practicable, rather than issuing frequent majors.
*Rationale:* Each major upgrade imposes migration cost on every consumer; batching amortizes that cost.

### 4.3 Announce deprecations with `Deprecation` and `Sunset` response headers.
**[RECOMMENDED]** Responses from a deprecated version or resource should carry the `Deprecation` header and a `Sunset` header (RFC 8594) indicating the retirement date.
*Rationale:* Machine-readable deprecation lets client tooling warn developers automatically, long before a human reads release notes.
*Example:* `Sunset: Wed, 31 Dec 2025 23:59:59 GMT`
*Note (open decision):* the `Deprecation`/`Sunset` headers are additions to the response-header set enumerated in §10; confirm before adoption.

### 4.4 Publish an end-of-life date whenever deprecating a version.
**[REQUIRED]** Deprecation shall record an end-of-life date, surfaced through the `about/versions` endpoint as part of each version's lifecycle triplet (version number, lifecycle state, end-of-life date).
*Rationale:* Consumers cannot plan migration without a firm retirement date.

### 4.5 Provide a migration plan with every major-version upgrade.
**[REQUIRED]** Every major version upgrade shall be accompanied by a migration plan presented at design review.
*Rationale:* A migration plan converts a breaking change from a surprise into a managed transition.

---

## 5. Architecture & REST Constraints

### 5.1 Give every resource a URL and a UUID instance identifier.
**[REQUIRED]** Every resource shall be addressable by URL, and instance identifiers shall be unique and conform to UUID (RFC 4122).
*Rationale:* Global, opaque identifiers keep references stable and prevent collisions across distributed systems.

### 5.2 Honor HTTP content negotiation and represent resources as JSON.
**[REQUIRED]** APIs shall honor `Accept`/`Content-Type` semantics, shall accept `application/json` request bodies, and shall be able to return `application/json` representations.
*Rationale:* A single mandatory representation guarantees any client can interoperate without bespoke encoding.

### 5.3 Expose only the approved uniform verb set.
**[REQUIRED]** Only GET, PUT, POST, DELETE, and HEAD shall be used, each with its defined semantics (§9).
*Rationale:* A constrained, uniform interface is what makes REST resources predictable across the whole catalog.

### 5.4 Keep every interaction stateless.
**[REQUIRED]** APIs shall hold no in-memory client state between interactions; each request carries everything needed to process it.
*Rationale:* Statelessness is what allows horizontal scaling and transparent failover.

### 5.5 Assign each resource to its architectural layer.
**[REQUIRED]** Resources shall be typed and assigned to layers per the Application Services Architecture — Business Resources in the Business Resource Layer, Core Resources in the Core Resource Layer.
*Rationale:* Explicit layering keeps dependencies flowing in one direction and preserves architectural integrity.

### 5.6 Hide implementation details behind the interface.
**[REQUIRED]** APIs shall conceal implementation details — especially persistence mechanisms and technologies likely to be replaced — exposing only functionality common to viable alternative implementations where a change is anticipated.
*Rationale:* Leaking implementation into the contract couples consumers to decisions the provider needs to keep free to change.

### 5.7 Omit HATEOAS unless a future reassessment adopts it.
**[OPTIONAL]** Hypermedia controls are not currently supported; the computation, bandwidth, and representation-complexity cost is judged to outweigh present client value. This position is reassessed periodically.
*Rationale:* Recording the decision and its basis prevents relitigating it ad hoc and signals it is deliberate, not an oversight.

---

## 6. Resource Modeling

### 6.1 Model each resource around its essential attributes and relationships.
**[REQUIRED]** Resource design shall capture the essence of the resource — its fundamental attributes and relationships — informed by how customers actually use it.
*Rationale:* Modeling from real usage produces resources that fit workflows instead of mirroring internal storage.

### 6.2 Choose resource granularity from real customer usage.
**[RECOMMENDED]** Deliberately manage resource size, complexity, and the choice between referenced and embedded information based on consumer access patterns.
*Rationale:* Right-sized resources minimize both over-fetching and chatty multi-call sequences.

### 6.3 Define resource structure in the Information Architecture.
**[REQUIRED]** Resource structure and semantics shall be defined in, and adhere to, the organization's Information Architecture.
*Rationale:* A shared information model is what lets the same concept mean the same thing across every API.

### 6.4 Assign each resource to exactly one owning domain.
**[REQUIRED]** Every resource belongs to exactly one approved domain (per the Application Services Architecture), which namespaces it and sets development-ownership boundaries; resource code lives in a package named for the resource, nested in its domain package.
*Rationale:* Single ownership prevents the diffusion of responsibility that leaves resources unmaintained.
*Example:* `user/customers/CustomersResource.java`

### 6.5 Represent relationships as references or embedded data deliberately.
**[RECOMMENDED]** Choose between linking to a related resource and embedding its representation based on how consumers traverse the relationship and how independently the two evolve.
*Rationale:* The reference-versus-embed choice drives both payload size and coupling; making it by default produces one or the other by accident.

### 6.6 Fold sub-resource changes into the parent resource's version.
**[REQUIRED]** Sub-resources follow the same naming standards as top-level resources but are not independently versioned; a breaking sub-resource change increments the parent version.
*Rationale:* Consumers track one version per top-level resource rather than a matrix of sub-resource versions.

---

## 7. URL Structure

### 7.1 Target the endpoint base that matches the environment.
**[REQUIRED]** Publicly visible endpoints shall use the endpoint base for their environment.
*Rationale:* Environment-specific bases keep production, sandbox, and alpha traffic cleanly separated.

| Environment | Endpoint Base |
| --- | --- |
| Production | `https://api.example.com` |
| Sandbox | `https://api.sandbox.example.com` |
| Alpha | `https://api.alpha.example.com` |

### 7.2 Compose URLs as base / domain / resource / version.
**[REQUIRED]** Resource URLs are composed as Endpoint Base / Domain / Resource Name / Version, and URL resource names shall be lowercase alphabetic only.
*Rationale:* A fixed composition makes any resource's URL predictable from its identity.
*Example:* `https://api.example.com/user/customers/V1`

### 7.3 Pass instance IDs as template path segments.
**[REQUIRED]** A resource instance ID shall be passed as a template path segment, never as a query parameter.
*Rationale:* Path-segment identity keeps each instance individually addressable and cacheable.
*Example:* `.../customers/V1.1/25`

### 7.4 Serve interface metadata from the reserved `about` endpoints.
**[REQUIRED]** Reserved `about` endpoints, each returning both HTML and JSON, expose interface documentation, version history, and release notes.
*Rationale:* A uniform metadata surface lets consumers and tooling discover documentation the same way for every resource.

| Endpoint | Returns |
| --- | --- |
| `.../{resource}/{version}/about` | Interface documentation |
| `.../{resource}/about/versions` | Version history (version, lifecycle state, end-of-life date) |
| `.../{resource}/{version}/about/relnotes` | Release notes |

---

## 8. Naming

### 8.1 Name each API to convey its scope, uniquely and intuitively.
**[REQUIRED]** API names shall indicate the scope of resources offered, be intuitive to external developers, differentiate the API from all others, and be unique; syntax is capitalized words separated by spaces, terminated by the suffix "API".
*Rationale:* The name is the first thing a prospective consumer evaluates; it must communicate purpose at a glance.
*Example:* `Customer Management API`

### 8.2 Name resources as nouns, plural for collections.
**[REQUIRED]** Resource names shall be information-oriented nouns; multi-instance resources take plural names, and genuine singletons take singular names and omit the `/<ID>` pattern. Function-oriented (verb) resources require explicit approval and shall be rare.
*Rationale:* Noun-based, correctly-pluralized names make resource semantics self-evident.
*Example:* `customers` (collection), `configuration` (singleton)

### 8.3 Name parameters in camelCase.
**[REQUIRED]** Parameter names use camelCase — first word lowercase, subsequent words capitalized, characters `[a-zA-Z]` only, no spaces.
*Rationale:* A single casing convention removes a whole class of "was it snake or camel?" integration errors.
*Example:* `pageSize`, `lastModifiedDate`

### 8.4 Restrict names to the approved character sets and casing.
**[REQUIRED]** Names shall be nouns grounded in the Information Architecture, with reserved names (§11.2) never repurposed and casing/character rules applied per element type.
*Rationale:* Reserving names and constraining characters keeps identifiers unambiguous across languages and tools.

### 8.5 Keep names technology-independent and abbreviations rare.
**[RECOMMENDED]** Names should be technology-independent, and abbreviations should be minimal and well known.
*Rationale:* Technology-neutral names survive implementation changes and read clearly to a broad audience.

---

## 9. HTTP Methods

### 9.1 Use GET for safe, idempotent reads only.
**[REQUIRED]** GET shall be read-only, safe, and idempotent, never modifying server state.
*Rationale:* Safe reads can be cached, prefetched, and retried freely by intermediaries.

### 9.2 Use PUT to update existing resources idempotently, never to create.
**[REQUIRED]** PUT shall update an existing resource and shall be idempotent; PUT to a nonexistent resource returns 404.
*Rationale:* Restricting PUT to updates keeps creation semantics unambiguous and repeated PUTs harmless.

### 9.3 Use POST to create resources, returning the new resource URL.
**[REQUIRED]** POST shall create a new resource and return its URL; POST is neither safe nor idempotent and shall never be used to update.
*Rationale:* A single creation verb, distinct from update, keeps write intent explicit.

### 9.4 Use DELETE to remove resources idempotently.
**[REQUIRED]** DELETE shall remove the resource and be idempotent (not safe); subsequent access returns Not Found.
*Rationale:* Idempotent deletion lets clients retry after a lost response without special-casing.

### 9.5 Use HEAD to return a GET's headers with an empty body.
**[REQUIRED]** HEAD shall return exactly the headers a GET would produce, with no body.
*Rationale:* HEAD lets clients check existence, size, or freshness without transferring the representation.

### 9.6 Preserve each method's safety and idempotency guarantees.
**[REQUIRED]** Implementations shall not weaken the safety or idempotency guarantees defined for each verb.
*Rationale:* Intermediaries and clients rely on these guarantees to retry and cache correctly.

### 9.7 Honor a `method` query parameter for legacy clients.
**[REQUIRED]** To accommodate clients lacking full verb support, all APIs shall honor a `method` query parameter on GET requests, executing the semantics of the named verb.
*Rationale:* The override keeps constrained legacy clients interoperable without loosening the verb set for everyone.

### 9.8 Reject any verb outside the approved set.
**[REQUIRED]** Verbs outside GET/PUT/POST/DELETE/HEAD shall be rejected with 405, and the `Allow` header shall list supported methods.
*Rationale:* Explicit rejection with `Allow` tells the client exactly what it may do instead.

---

## 10. HTTP Headers

### 10.1 Require the standard request headers on every request.
**[REQUIRED]** Requests use `Accept` (representations returned as `application/json`; `about` metadata as JSON or HTML at the client's choice), `Accept-Charset` (UTF-8), and `Authorization` (OAuth 2 credentials).
*Rationale:* A fixed request-header contract makes negotiation and authentication uniform.

### 10.2 Set the standard response headers on every response.
**[REQUIRED]** Responses set the HTTP headers appropriate to the outcome, per their specification semantics.
*Rationale:* Correct response headers drive caching, redirection, retries, and authentication challenges without custom logic.

| Header | When |
| --- | --- |
| `Age` | On all responses |
| `Allow` | Required with every 405 |
| `Content-Type` | `application/json` for representations; JSON or HTML for `about` |
| `Expires` | Wherever caching is acceptable |
| `Last-Modified` | On responses |
| `Location` | Required with 302; set to the new resource URI on 201 |
| `Retry-After` | Required with 503 |
| `WWW-Authenticate` | Required with 401 |

### 10.3 Prefix every custom header with the organization name.
**[REQUIRED]** Custom headers begin with the organization name (shown here as `Example`), words separated by hyphens. Defined custom headers: `Example-Service-Bus` (each mediating ESB appends its ID), `Example-Service-Container` (the API container sets its ID on all responses), and `Example-Result-Set-Count` (element count whenever a collection is returned). ESB and container IDs conform to the Infrastructure Services Architecture identification standard.
*Rationale:* A reserved prefix prevents collisions with standard or third-party headers.

### 10.4 Apply content encoding per the HTTP specification.
**[RECOMMENDED]** `Content-Encoding` applies in both request and response directions per the HTTP specification.
*Rationale:* Standard content coding reduces bandwidth without bespoke compression schemes.

---

## 11. Request Parameters

### 11.1 Pass resource IDs as template parameters.
**[REQUIRED]** Resource instance IDs shall be conveyed as template path parameters, not query parameters (see §7.3).
*Rationale:* Keeping identity in the path preserves addressability and cache keys.

### 11.2 Reserve the standard query-parameter names for their defined purposes.
**[REQUIRED]** The reserved query-parameter names are standardized across all APIs and shall not be repurposed.
*Rationale:* Reserved names mean a consumer learns `limit`/`offset`/`sort`/`q` once and reuses them everywhere.

| Parameter | Purpose |
| --- | --- |
| `limit` | Maximum number of results returned |
| `offset` | Starting index of the result set |
| `suppressErrors` | Boolean; forces a 200 status while retaining the error body |
| `q` | OData query expression for complex searches |
| `sort` | Result-set ordering criteria |
| `method` | HTTP verb pass-through for legacy clients |

### 11.3 Avoid matrix parameters.
**[RECOMMENDED]** Matrix parameters (name–value pairs qualifying a single path segment) should not be used; where used, matrix names shall not clash with reserved query names, except `q`, which carries identical semantics.
*Rationale:* Matrix parameters are uncommon and add parsing complexity for little benefit.

### 11.4 Keep parameter semantics consistent across all APIs.
**[REQUIRED]** Parameter names shall be nouns, intuitive, technology-independent, grounded in the Information Architecture, and semantically identical across every API.
*Rationale:* Same-name-same-meaning is what lets a parameter be understood without consulting each API's docs.

---

## 12. Data Formats & Types

### 12.1 Represent all payloads as JSON.
**[REQUIRED]** Request and response representations shall use `application/json`.
*Rationale:* One representation format keeps client and server serialization simple and universally supported.

### 12.2 Encode all text as UTF-8.
**[REQUIRED]** All representations use UTF-8 encoding.
*Rationale:* A single encoding eliminates mojibake and charset-negotiation failures.

### 12.3 Format dates and times as ISO 8601.
**[REQUIRED]** Dates and timestamps shall be ISO 8601 / RFC 3339 strings, and timestamps shall carry an explicit UTC offset (`Z` for UTC).
*Rationale:* An unambiguous, sortable, timezone-explicit format prevents the most common data-interchange defects.
*Example:* `2026-07-15T09:30:00Z`

### 12.4 Represent numbers, booleans, and enumerations consistently.
**[RECOMMENDED]** Represent monetary and exact values as strings or integer minor units (never binary floats), booleans as JSON `true`/`false` (not `"true"`/`0`/`1`), and enumerations as documented UPPER_SNAKE_CASE string tokens.
*Rationale:* Consistent scalar conventions prevent precision loss and brittle truthiness checks.
*Example:* `"status": "IN_PROGRESS"`, `"amountMinor": 1050`

### 12.5 Omit absent values rather than sending null, per the defined rule.
**[RECOMMENDED]** A field with no value should be omitted rather than sent as `null`; where `null` is meaningful (an explicit clearing of a value), its meaning shall be documented for that field.
*Rationale:* A single, documented rule stops consumers from having to treat "absent" and "null" as separate cases by guesswork.

### 12.6 Format identifiers as UUIDs.
**[REQUIRED]** Resource instance identifiers shall be UUIDs (RFC 4122), represented as canonical lowercase strings.
*Rationale:* Opaque UUIDs decouple identity from any internal sequence or storage scheme.
*Example:* `"customerId": "7c9e6679-7425-40de-944b-e07fc1f90ae7"`

### 12.7 Use the designated standard codes for currency, country, and language.
**[RECOMMENDED]** Use ISO 4217 for currency, ISO 3166-1 alpha-2 for country, and BCP 47 for language tags.
*Rationale:* Standard code sets make cross-API and cross-system data directly comparable.
*Example:* `"currency": "USD"`, `"country": "US"`, `"language": "en-US"`

### 12.8 Support internationalization of content.
**[OPTIONAL]** APIs handling human-facing text may honor an `Accept-Language` request header and localize content and human-readable messages accordingly.
*Rationale:* Locale-aware responses serve a global consumer base without per-locale endpoints.
*Note (open decision):* `Accept-Language` is an addition to the request-header set in §10.1; confirm before adoption.

---

## 13. Collections

### 13.1 Paginate collections with `limit` and a zero-based `offset`.
**[REQUIRED]** All APIs shall support pagination via `limit` and `offset`, where `offset` is zero-based.
*Rationale:* One pagination idiom across the catalog means clients write paging logic once.
*Example:* `limit=25&offset=0` returns elements 0–24.

### 13.2 Apply the default and per-resource maximum page sizes.
**[REQUIRED]** The default `limit` is 10 unless the interface definition specifies otherwise; each interface definition shall declare a per-resource maximum, and requests above it are capped at the maximum. Requests exceeding the available elements return all remaining elements.
*Rationale:* Bounded page sizes protect the service from unbounded result sets while giving each resource sensible tuning.

### 13.3 Return the element count on every collection response.
**[REQUIRED]** Whenever a collection is returned, the `Example-Result-Set-Count` header shall be set to the element count.
*Rationale:* Clients can render totals and plan paging without a separate count call.

### 13.4 Accept complex queries through the `q` OData parameter.
**[RECOMMENDED]** Complex queries are expressed via `q` using OData `$filter` syntax; `q` shall not be combined with domain query parameters (those qualifying the resource, e.g. `name`), though system parameters like `limit`/`offset` may accompany it. APIs offering complex query shall support the full OData logical, arithmetic, string, date, math, and type operators.
*Rationale:* A single expressive query grammar avoids a proliferation of ad-hoc filter parameters.
*Example:* `?q=location eq 'Petaluma' and age lt 30`

### 13.5 Order results through the `sort` parameter.
**[RECOMMENDED]** Ordering is expressed via `sort` with syntax `[-]FieldName{"|"[-]FieldName}`, where a leading `-` means descending and left-to-right order sets precedence.
*Rationale:* A compact, uniform sort grammar covers multi-key ordering without bespoke parameters.
*Example:* `?sort=-age|lastName` orders by age descending, then last name ascending.

### 13.6 Serve pages from the live store, not per-client snapshots.
**[REQUIRED]** APIs shall serve pages from the live persistence store rather than caching per-client snapshots; the design assumes data changes infrequently enough for multi-request retrieval.
*Rationale:* Live paging avoids the memory and staleness cost of holding a snapshot per consumer.

---

## 14. Status Codes

### 14.1 Return only codes from the approved status set.
**[REQUIRED]** APIs shall return only this constrained set: **200, 201, 302, 304, 400, 401, 403, 404, 405, 409, 429, 500, 503**. Adherence is the joint responsibility of API implementers and the hosting platform, and 1xx codes are never returned.
*Rationale:* A small, well-known code set keeps client-side handling simple and uniform.

### 14.2 Signal success with the defined 2xx codes.
**[REQUIRED]** Use **200 OK** for any successful GET/PUT/DELETE/HEAD (no resource created) and **201 Created** for a successful POST, with `Location` set to the new resource URI and an empty body.
*Rationale:* Distinct success codes let clients distinguish "here is your result" from "your resource now exists here."

### 14.3 Signal redirection with the defined 3xx codes.
**[REQUIRED]** Use **302 Found** when a logical endpoint has moved and the platform knows the new location (returned in `Location`), and **304 Not Modified** for a conditional GET where the resource is unchanged (empty body). No other 3xx codes are used.
*Rationale:* Limiting redirection codes keeps client redirect and cache-validation logic predictable.

### 14.4 Signal client errors with the defined 4xx codes.
**[REQUIRED]** Use 400 (body syntax error), 401 (credentials absent/insufficient; `WWW-Authenticate` required), 403 (business-logic constraint violated), 404 (no resource at location), 405 (unsupported verb; `Allow` required), 409 (incompatible with current resource state), and 429 (rate SLA exceeded).
*Rationale:* A fixed 4xx vocabulary tells developers precisely which class of mistake to fix.

### 14.5 Signal server errors with the defined 5xx codes.
**[REQUIRED]** Use **500 Internal Server Error** for any server-side error not covered by another 5xx code, and **503 Service Unavailable** when a request within SLA cannot be served for capacity reasons.
*Rationale:* Separating "we failed" from "we are overloaded" lets clients retry the second and report the first.

---

## 15. Errors

### 15.1 Return the standard JSON error body on every error.
**[REQUIRED]** Every implementation shall catch every exception and return the standard error body; descriptions may contain any visible character except curly quotes and pipe.
*Rationale:* A single error shape lets every consumer parse and surface failures with one code path.

| Field | Content |
| --- | --- |
| `code` | Four-digit organization-defined error code |
| `name` | CapitalizedWord error name |
| `supportId` | Globally unique identifier for the occurrence |
| `problem` | Description of what went wrong |
| `solution` | *(Optional)* resolution instructions, whenever guidance is possible |
| `moreInfo` | URL to further documentation |

### 15.2 Make 4xx messages instructive and minimize 5xx external detail.
**[REQUIRED]** Client-side (4xx) errors are resolvable by the developer, so messages shall be rich and instructive; server-side (5xx) errors are not developer-resolvable, so external detail is minimized while the body carries references to internal debugging information.
*Rationale:* Detail helps where the developer can act and only leaks information where they cannot.

### 15.3 Assign every error a four-digit organization error code.
**[REQUIRED]** Each error carries a four-digit organization-defined `code` and a CapitalizedWord `name`.
*Rationale:* Stable codes let consumers branch on error type without string-matching prose.

### 15.4 Include a unique support ID on every error.
**[REQUIRED]** Each error response shall carry a globally unique `supportId` identifying the occurrence.
*Rationale:* A correlation handle turns a support conversation into a single-lookup investigation.

### 15.5 Honor `suppressErrors` to force a 200 while retaining the error body.
**[REQUIRED]** When `suppressErrors` is true, the response status is guaranteed 200 while the body still carries the standard error structure.
*Rationale:* Some constrained clients cannot process non-200 statuses; suppression keeps them functional without discarding error detail.

---

## 16. Security

### 16.1 Require TLS for all traffic.
**[REQUIRED]** All API traffic shall use TLS (current supported versions only); plaintext HTTP shall be refused or redirected.
*Rationale:* Transport encryption is the baseline that every other control depends on.

### 16.2 Authenticate every request with OAuth 2.
**[REQUIRED]** Requests shall present OAuth 2 credentials via the `Authorization` header; missing or invalid credentials yield 401 with `WWW-Authenticate`.
*Rationale:* A single, standard authentication scheme lets every API and gateway validate identity uniformly.

### 16.3 Authorize access through scopes and roles.
**[REQUIRED]** Access shall be governed by OAuth 2 scopes and the organization's roles; a properly authenticated but unauthorized request yields 403.
*Rationale:* Coarse authentication plus fine-grained scopes enforces least privilege per operation.

### 16.4 Validate and sanitize all input.
**[REQUIRED]** All input — path, query, headers, and body — shall be validated against its declared type and constraints and rejected with 400 when invalid.
*Rationale:* Strict input validation is the first line of defense against injection and malformed-data faults.

### 16.5 Protect and minimize sensitive data and PII.
**[REQUIRED]** Sensitive data and PII shall be minimized in payloads, never placed in URLs, encrypted in transit and at rest, and handled per the applicable privacy and data-governance policies.
*Rationale:* Data not collected or not exposed cannot be leaked; URLs in particular persist in logs and history.

### 16.6 Keep secrets out of URLs, logs, and source code.
**[REQUIRED]** Credentials, tokens, and keys shall never appear in URLs, log output, or source repositories.
*Rationale:* Each of these is routinely retained and widely readable, making them the most common source of credential leaks.

### 16.7 Defend against common API threats.
**[RECOMMENDED]** Designs should account for the prevailing API threat classes (e.g. the OWASP API Security Top 10), including broken object-level authorization, mass assignment, and excessive data exposure.
*Rationale:* Designing against known attack patterns is far cheaper than remediating them after exploitation.

---

## 17. Caching & Concurrency

### 17.1 Set caching headers wherever caching is acceptable.
**[REQUIRED]** Responses shall set `Expires`, `Last-Modified`, and `Age` wherever caching is acceptable (§10.2).
*Rationale:* Explicit freshness metadata lets intermediaries and clients cache safely instead of guessing.

### 17.2 Support conditional requests with `ETag` and 304.
**[RECOMMENDED]** Cacheable resources should carry an `ETag`, and APIs should honor `If-None-Match` on GET, returning 304 when the representation is unchanged.
*Rationale:* Validation with `ETag` avoids retransmitting unchanged representations, saving bandwidth and latency.
*Note (open decision):* `ETag`/`If-None-Match` are additions to the header sets in §10; confirm before adoption.

### 17.3 Enforce optimistic concurrency with `If-Match`.
**[RECOMMENDED]** Writes that must not clobber concurrent updates should require an `If-Match` precondition carrying the resource's `ETag`; a failed precondition yields 409 (rather than 412, which is outside the approved status set).
*Rationale:* Optimistic concurrency prevents lost updates without the cost of server-side locking.
*Note (open decision):* the conventional response is 412 Precondition Failed; because §14 excludes 412, this maps to 409. Confirm 409 mapping or admit 412 to the status set.

### 17.4 Accept idempotency keys for safe retries of writes.
**[RECOMMENDED]** POST operations should accept a client-supplied idempotency key so that a retried request after a lost response does not create a duplicate resource.
*Rationale:* Networks drop responses; without idempotency keys, safe retry of a non-idempotent create is impossible.
*Note (open decision):* introduces an `Example-Idempotency-Key` custom header (§10.3); confirm the name.

---

## 18. Rate Limiting & Quotas

### 18.1 Enforce each subscription's rate policy and tier.
**[REQUIRED]** The platform shall enforce the rate-limiting policy of each API subscription according to its tier.
*Rationale:* Enforced limits protect shared capacity and make one consumer's spike survivable for the rest.

### 18.2 Apply quotas per consumer.
**[RECOMMENDED]** Longer-window quotas (e.g. daily/monthly) should be applied per consumer in addition to short-window rate limits.
*Rationale:* Quotas align consumption with commercial agreements and catch sustained overuse that per-second limits miss.

### 18.3 Return 429 with `Retry-After` when limits are exceeded.
**[REQUIRED]** When a consumer exceeds its rate SLA and the platform is not blocking per policy, respond 429; 503 responses shall set `Retry-After` to a computed time when determinable, otherwise 2 seconds by default, applying exponential back-off to `Retry-After` on repeated 503s.
*Rationale:* A machine-readable back-off signal lets well-behaved clients recover without hammering the service.

### 18.4 Communicate remaining limits in response headers.
**[RECOMMENDED]** Responses should report the consumer's limit, remaining allowance, and reset time via custom `Example-RateLimit-*` headers.
*Rationale:* Proactive limit signaling lets clients self-throttle before they are rejected.
*Note (open decision):* introduces `Example-RateLimit-Limit`/`-Remaining`/`-Reset` custom headers (§10.3); confirm names.

---

## 19. Asynchronous Operations

### 19.1 Model long-running work as a job resource.
**[RECOMMENDED]** An operation too slow for a synchronous response should create a job/operation resource that the client polls for status and result.
*Rationale:* A first-class job resource makes long-running work observable, resumable, and cancelable.
*Note (open decision):* the conventional acknowledgement is **202 Accepted**, which §14 excludes. Either admit 202 (and possibly 303 See Other for result retrieval) to the status set, or acknowledge job creation with 201 and a job resource URL. Confirm before elaboration.

### 19.2 Let clients poll job status to completion.
**[RECOMMENDED]** The job resource should expose a status field and, on completion, a link to the resulting resource.
*Rationale:* Polling a status resource keeps the interaction within the stateless, resource-oriented model.

### 19.3 Offer batch or bulk operations where they reduce call volume.
**[OPTIONAL]** Where consumers routinely act on many items, a batch/bulk operation may be provided to reduce round trips.
*Rationale:* Bulk operations cut chattiness for high-volume workflows, but add partial-failure complexity — hence optional and case-by-case.

---

## 20. Events & Notifications

### 20.1 Deliver events to consumers through webhooks.
**[OPTIONAL]** Where consumers need to react to state changes, the API may deliver events via consumer-registered webhook callbacks.
*Rationale:* Push delivery removes the latency and cost of consumers polling for changes that rarely happen.

### 20.2 Sign every event payload.
**[REQUIRED]** *(where §20.1 is offered)* Event deliveries shall be signed (e.g. HMAC over the payload) so consumers can verify authenticity and integrity.
*Rationale:* An unsigned webhook is trivially spoofable; signing is what makes the callback trustworthy.

### 20.3 Manage subscriptions through a dedicated resource.
**[RECOMMENDED]** *(where §20.1 is offered)* Webhook subscriptions should be created and managed through a first-class subscription resource following the normal resource conventions.
*Rationale:* Treating subscriptions as resources reuses the whole standard rather than inventing a side-channel.

### 20.4 Retry failed deliveries with back-off.
**[RECOMMENDED]** *(where §20.1 is offered)* Failed deliveries should be retried with exponential back-off up to a documented limit, after which the event is recorded as undeliverable.
*Rationale:* Bounded retry with back-off tolerates transient consumer outages without unbounded delivery storms.

---

## 21. Documentation

### 21.1 Describe every API in a machine-readable OpenAPI definition.
**[REQUIRED]** Each API shall publish a machine-readable OpenAPI (3.x) definition kept in sync with the implementation.
*Rationale:* A machine-readable contract powers client generation, mock servers, and automated conformance checks.

### 21.2 Serve human documentation from the `about` endpoints.
**[REQUIRED]** Human-readable interface documentation shall be served from the reserved `about` endpoints (§7.4) in HTML and JSON.
*Rationale:* A uniform, in-band documentation location means consumers find docs the same way for every resource.

### 21.3 Publish release notes for every version.
**[REQUIRED]** Each version shall publish release notes via `.../{resource}/{version}/about/relnotes`.
*Rationale:* Release notes are how consumers learn what changed and whether they must act.

---

## 22. Observability

### 22.1 Propagate a correlation ID across every request.
**[REQUIRED]** Each request/response shall be associated with a correlation identifier, surfaced to consumers as the error `supportId` and carried through internal processing.
*Rationale:* End-to-end correlation is what makes a single failing request traceable across services.

### 22.2 Record service routing lineage in the standard headers.
**[REQUIRED]** Mediating ESBs shall append their ID to `Example-Service-Bus`, and the API container shall set `Example-Service-Container` on all responses (§10.3).
*Rationale:* Preserved routing lineage lets operators reconstruct the exact path a request took.

### 22.3 Log and expose metrics for every API.
**[RECOMMENDED]** APIs should emit structured logs and operational metrics (traffic, error rates, latency) sufficient to monitor health and support the standard's adoption and impact metrics.
*Rationale:* Without metrics, both operational health and the standard's own value are unmeasurable.

---

## 23. References & Glossary

### 23.1 Cite the normative external standards this document depends on.
**[REQUIRED]** This standard depends on: RFC 2119 (requirement keywords), RFC 4122 (UUID), RFC 3339 / ISO 8601 (date-time), the HTTP specifications (RFC 7230–7235 / RFC 9110), RFC 6749 (OAuth 2), RFC 8594 (`Sunset` header), OData `$filter` (query syntax), ISO 4217 (currency), ISO 3166 (country), and BCP 47 (language tags).
*Rationale:* Naming the normative basis keeps settled questions settled and points implementers to the authoritative source.

### 23.2 Define the key terms used throughout.
**[REQUIRED]** Key terms shall be defined here and used consistently.
*Rationale:* A shared glossary prevents the same word from carrying different meanings across sections.

| Term | Definition |
| --- | --- |
| API | A named, versioned, branded product: a logical grouping of resources offered to consumers through a subscription. |
| Resource | Any piece of information manipulable via a URL; functionality is offered as CRUD operations on resources. |
| Domain | An approved namespace that groups resources and sets development-ownership boundaries. |
| Guideline | A single requirement: a directive, its normative statement, rationale, obligation level, and examples. |
| Waiver | An explicit, documented, approved exception to a requirement. |
