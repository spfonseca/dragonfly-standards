# RESTful API Design Standard

**Status:** Normative. Requirements use "shall" (mandatory) and "should" (recommended). Waivers require explicit, documented, and approved rationale.

---

## 1. Introduction

This standard defines the design and implementation requirements for all of the organization's RESTful APIs. It serves three purposes: a guide during design, the criteria applied at design reviews, and the source of standardized implementation practices.

### 1.1 Best Practice Goals

- **Make adoption easy.** APIs shall present a low barrier to entry; the first developer experience is decisive, so standardized errors, pagination, and idioms exist to eliminate guesswork.
- **Ensure consistency.** Naming, verb semantics, parameters, information models, responses, and idioms shall be uniform across all APIs. Consistency aids learning, reduces frustration and usage errors, speeds adoption, improves consumer trust, and makes cross-organization development efficient.
- **Ensure design quality.** Interface design is deliberately front-loaded: APIs are gotten right before release, not rushed out.
- **Align with customer needs.** APIs are built only where a rigorous, managed determination of customer need exists.

### 1.2 Best Practice Adherence

Value accrues only when the whole organization follows these practices habitually and over time. Reusable design carries short-term overhead that pays off quickly and significantly.

### 1.3 Design Reviews

- The degree of adherence for each new API is set at planning time; full adherence is the default. Waivers are acceptable only when explicit, rationalized, and agreed upon.
- Designs are assessed offline by a review committee using the API Design Checklists, then adjudicated in an API Design Review before development may proceed.

### 1.4 Document Scope

The standard progresses from high-level API requirements through architecture, resources, HTTP mechanics, common idioms, and response handling.

### 1.5 Related Documents

API Program Framework, API Program Roadmap, API Product Lifecycle, API Design Reviews, Application Services Architecture, Information Architecture, and Infrastructure Services Architecture. Where this standard defers (metadata constraints, domain names, layering, vocabularies), those documents govern.

---

## 2. APIs

An API is a named, versioned, branded product: a logical grouping of resources offered to consumers through a subscription process that grants access rights and enables security and runtime management.

### 2.1 Customer Alignment

- Every API shall be associated with named, high-value application workflows, each linked to a customer segment or specific customer.
- Design shall balance internal and external consumer requirements per the API Adoption Strategy.
- APIs shall be developed only when they will be readily used upon production release.

### 2.2 Return on Investment

ROI shall be quantified during roadmap planning and stored with the API product documentation. Design shall not proceed until the return is deemed sufficient.

### 2.3 API Reuse

Reuse is a sum-of-parts quality requiring: understandability (an API is graspable within minutes of reading its interface), appropriate granularity, enabling abstraction, consistency, sufficient documentation, discoverability, adequate non-functional qualities, and graceful lifecycle management.

### 2.4 Granularity & Decomposition

- **Limit the total number of APIs** so consumers can find functionality easily, grasp the full catalog quickly, and avoid cumbersome multi-API subscription.
- **Group related resources.** An API shall be cohesive, like the methods of a well-designed class.
- **Enable independent evolution.** Resources with different evolution profiles (fast-changing feeds vs. a stable core object model) should be placed in separate APIs — though cohesion generally takes precedence over evolvability.
- **Limit client exposure to complexity.** Allocate resources so typical applications need only a small subset of APIs.
- **Consider access restrictions.** Allocation shall be expert-approved with respect to internal vs. external, free vs. charged, sensitive vs. non-sensitive, and preferred vs. non-preferred access.

### 2.5 Consistency

All APIs shall follow the common conventions for API naming, resource naming, endpoint design, REST verb semantics, parameter naming and semantics, request/response information models (per the Information Architecture), standardized responses, and shared programming idioms.

### 2.6 Ease of Coding the Common

Common workflows shall be easy for third parties to code. Designs shall provide sensible defaults, use sufficiently coarse-grained interactions to control call volume, favor simple data types over deep hierarchies, and return responses that chain naturally into subsequent requests.

### 2.7 Graceful Evolution

The golden rule: never break client code. To minimize backward-incompatible change:

- **Manage design uncertainty.** Every endpoint–verb combination shall be rated 1 (high certainty) through 5 (high uncertainty) and presented at design review; high-uncertainty pairings shall not ship to production.
- **Release only the minimum viable API** — only endpoint–verb combinations with clear business justification.
- **Use an Alpha program** to gather third-party feedback where uncertainty is high.
- **Design for likely future requirements** when implementation cost is low; a business owner decides for uncertain or costly requirements.
- **Use parameterization** to improve adaptability.
- **Batch backward-incompatible changes** into a single major version upgrade whenever practicable.
- **Provide a migration plan** at design review for every major version upgrade.

### 2.8 API Naming

- The Technical Product Manager drives naming, building consensus with the Chief Architect and CTO; the CTO minimally engages the CMO.
- Names shall indicate the scope of resources offered, be intuitive to developers outside the organization, functionally differentiate the API from all others, and be unique.
- Syntax: capitalized words separated by spaces, terminated by the suffix "API" (`API Name = Word, Space, {Word, Space}, "API"`).
- Abbreviations shall be minimal and well known. Names shall be technology-independent.

### 2.9 Versioning

- **Major number:** incremented sequentially for any backward-incompatible change (any syntactic or semantic difference that can alter guaranteed behavior).
- **Minor number:** incremented for changes that preserve the client contract.
- **Syntax:** `"V" MajorNumber "." MinorNumber` (major starts at 1).
- **Alpha syntax:** `"V" Number "-Alpha"`, incrementing sequentially from V1-Alpha per alpha release.
- Major version updates shall be minimized; minor updates may be frequent but must be verified backward compatible and stable.

### 2.10 Metadata

API metadata shall be captured per the Application Services Architecture and be available at design review time.

---

## 3. Architecture

### 3.1 REST

All APIs adhere to the REST architectural style over HTTP:

- **Addressable resources.** Every resource shall have a URL. Instance IDs shall be unique and conform to UUID (IETF RFC 4122).
- **Representation-oriented.** APIs shall honor HTTP `Accept` and `Content-Type` semantics. All APIs shall accept `application/json` request bodies and shall be able to return `application/json` representations.
- **Uniform, constrained interface.** Only GET, PUT, POST, DELETE, and HEAD shall be used:
  - **GET** — read-only; safe and idempotent.
  - **PUT** — update an existing resource only (never create); idempotent; PUT on a nonexistent resource returns 404.
  - **POST** — create a new resource, returning its URL; never used to update; neither safe nor idempotent.
  - **DELETE** — remove the resource; idempotent, not safe; subsequent access returns Not Found.
  - **HEAD** — return the headers a GET would produce, with an empty body.
- **Method query parameter.** To accommodate legacy clients lacking full verb support, all APIs shall honor a `method` query parameter on GET requests, executing the semantics of the verb named in the parameter.
- **Stateless.** All APIs shall be stateless; no in-memory state between client interactions.
- **HATEOAS.** Not supported. The cost (computation, bandwidth, representation complexity) outweighs current client-side value; this position is periodically reassessed.

### 3.2 Layering

Resources are typed and assigned to layers per the Application Services Architecture: Business Resources in the Business Resource Layer, Core Resources in the Core Resource Layer, each following that document's constraints.

### 3.3 Abstraction

- Every endpoint–method combination shall be reviewed and approved by a qualified API designer.
- APIs shall hide implementation details, including persistence mechanisms — especially technologies likely to be replaced.
- Abstractions shall promote reuse across multiple workflows, limit client exposure to complexity, and permit multiple underlying implementations: when a technology change is anticipated, the interface shall expose only functionality common to the viable alternatives.

---

## 4. Resources

A resource is any piece of information manipulable via a URL; application functionality is offered as CRUD operations on resources.

### 4.1 Granularity & Decomposition

Resource design shall model the essence of the resource — its fundamental attributes and relationships — informed by how customers will actually use it, and shall deliberately manage resource size, complexity, and the choice between referenced and embedded information.

### 4.2 Information Architecture Adherence

Resource structure and semantics shall be defined in, and adhere to, the organization's Information Architecture.

### 4.3 Endpoint Base

All publicly visible endpoints shall use the endpoint base matching their environment:

| Environment | Endpoint Base |
| --- | --- |
| Production | `https://api.example.com` |
| Sandbox | `https://api.sandbox.example.com` |
| Alpha | `https://api.alpha.example.com` |

### 4.4 Domains

- Every resource belongs to exactly one domain; domains namespace resources and set development ownership boundaries.
- Only domain names approved in the Application Services Architecture shall be used.
- Resource code shall live in a package named for the resource, nested inside a package named for its domain (e.g., `user/customers/CustomersResource.java`).

### 4.5 Versioning

- Top-level resources are versioned with the same major.minor scheme and syntax as APIs (`"V" MajorNumber "." MinorNumber`, major from 1).
- Omitting the minor number in an endpoint URL selects the latest minor version of that major version (e.g., `/user/customers/V1` resolves to V1.5 if that is latest; `/user/customers/V1.3` pins V1.3).
- Sub-resources shall not be versioned; a backward-incompatible sub-resource change increments the parent resource version.

### 4.6 Resource Name

- Names shall be information-oriented nouns; function-oriented (verb) resources require explicit approval and shall be rare.
- Multi-instance resources take plural names (`customers`); genuinely singleton resources take singular names and omit the `/<ID>` pattern.
- **Resource URL:** Endpoint Base / Domain / Resource Name / Version — e.g., `https://api.example.com/user/customers/V1`. URL resource names shall be lowercase alphabetic only.
- **Implementation class:** resource name capitalized plus the suffix `Resource` (e.g., `CustomersResource`), alphabetic characters only, placed per the packaging rule above.
- Sub-resources follow the same naming standards as top-level resources.

---

## 5. HTTP Content

### 5.1 HTTP Request Headers

- **Accept:** representations are returned as `application/json`; resource metadata via the `about` path segment may be returned as `application/json` or `text/html` at the client's choosing.
- **Accept-Charset:** all responses use UTF-8.
- **Authorization:** used for passing OAuth 2 credentials.

### 5.2 HTTP Response Headers

Per HTTP specification semantics:

- **Age** — set on all responses.
- **Allow** — required with every 405 response, listing supported methods.
- **Content-Type** — `application/json` for representations; JSON or HTML for `about` metadata.
- **Expires** — set wherever caching is acceptable.
- **Last-Modified** — set on responses.
- **Location** — required with 302 responses (and set to the new resource URI on 201).
- **Retry-After** — required with 503 responses.
- **WWW-Authenticate** — required with 401 responses.

### 5.3 Request and Response Headers

**Content-Encoding** applies in both directions per the HTTP specification.

### 5.4 Custom HTTP Headers

- All custom headers begin with the organization's name (shown here as `Example`), words separated by hyphens.
- **Example-Service-Bus:** each mediating ESB appends its ID, preserving routing lineage.
- **Example-Service-Container:** the API container sets its ID on all responses.
- **Example-Result-Set-Count:** set to the element count whenever a collection is returned.

ESB and container IDs conform to the Infrastructure Services Architecture identification standard.

---

## 6. HTTP Parameters

### 6.1 Parameter Naming

- Names shall be nouns, intuitive, technology-independent, and semantically grounded in the Information Architecture; semantics shall be consistent across all of the organization's APIs.
- Reserved names (§6.3) shall never be repurposed. Abbreviations shall be minimal and well known.
- **Syntax:** camelCase — first word lowercase, subsequent words capitalized, characters `[a-zA-Z]` only, no spaces.

### 6.2 Template Parameters

- **Primary use:** passing a resource instance ID as a path segment — e.g., `.../customers/v1.1/25`. Template parameters, not query parameters, shall be used for IDs.
- **Reserved `about` endpoints** (all shall return HTML and JSON):
  - `.../{resource}/{version}/about` — interface documentation.
  - `.../{resource}/about/versions` — version history, returned as triplets of version number, lifecycle state, and end-of-life date.
  - `.../{resource}/{version}/about/relnotes` — release notes.

### 6.3 Query Parameters

Reserved names, standardized across all APIs:

| Parameter | Purpose |
| --- | --- |
| `limit` | Maximum number of results returned |
| `offset` | Starting index of the result set |
| `suppressErrors` | Boolean; forces a 200 status while retaining the error body |
| `q` | OData query expression for complex searches |
| `sort` | Result-set ordering criteria |
| `method` | HTTP verb pass-through for legacy clients |

### 6.4 Matrix Parameters

Matrix parameters (name-value pairs qualifying an individual path segment) shall generally not be used; they are uncommon and add complexity. There are no reserved matrix names, but matrix names shall not clash with reserved query names — except `q`, which if used carries identical semantics.

---

## 7. Common Interface Idioms

The idioms below are standardized so clients never learn per-API variations.

### 7.1 Result Set Pagination

- All APIs shall support pagination via `limit` and `offset`; `offset` is zero-based (limit=25, offset=0 returns elements 0–24).
- Requests exceeding the available elements return all remaining elements.
- Default `limit` is 10 unless the interface definition specifies otherwise (recommended per-resource tuning).
- Each interface definition shall declare a per-resource maximum; requests above it are capped at the maximum.
- **Freshness:** APIs shall serve pages from the live persistence store rather than caching snapshots per client; designs assume data changes infrequently enough for multi-request retrieval.

### 7.2 Search

- Complex queries are passed via the `q` parameter, e.g., `?q=location eq Petaluma and age lt 30`.
- **No combining:** `q` shall not be combined with domain query parameters (parameters qualifying the resource, such as `name`); system parameters like `limit` and `offset` may accompany it.
- **Syntax:** OData `$filter` expression syntax.
- **Support:** APIs offering complex query shall support all OData logical operators, arithmetic operators, string functions, date functions, math functions, and type functions.

### 7.3 Sorting

- Criteria pass via the `sort` parameter with syntax `[-]FieldName{"|"[-]FieldName}`, where FieldName is a JSON attribute name, a leading `-` means descending, and left-to-right order sets precedence.
- Example: `?sort=-age|lastName` orders by age descending, then last name ascending.

### 7.4 Field Limiting

Not supported. May be introduced in a future version of this standard.

### 7.5 Field Expansion

Not supported. The interface and implementation complexity, cost, and unfamiliarity to developers outweigh the network savings.

---

## 8. Response

Every response adheres to the HTTP specification. To keep the client burden low, APIs return only this constrained status code set: **200, 201, 302, 304, 400, 401, 403, 404, 405, 409, 429, 500, 503**. Adherence is the joint responsibility of API implementers and the hosting platform.

### 8.1 Nominal Responses

- **1xx** — never returned.
- **200 OK** — any successful GET, PUT, DELETE, or HEAD (no new resource created); body content depends on the method and request.
- **201 Created** — successful POST; `Location` header set to the new resource URI; response body empty (201 responses are deliberately kept minimal to simplify client code).
- **302 Found** — the logical endpoint has moved and the platform knows the new location, returned in the `Location` header.
- **304 Not Modified** — conditional GET where the resource is unchanged; empty body. No other 3xx codes are used.

### 8.2 Error Responses

Every implementation shall catch every exception and respond per this section.

**Standard error body (JSON), all errors:**

| Field | Content |
| --- | --- |
| `code` | Four-digit organization-defined error code |
| `name` | CapitalizedWord error name |
| `supportId` | Globally unique identifier for the occurrence |
| `problem` | Description of what went wrong |
| `solution` | *(Optional)* resolution instructions, included whenever resolution guidance is possible |
| `moreInfo` | URL to further documentation |

Descriptions may contain any visible character except curly quotes and pipe.

**Client-side errors (4xx)** — resolvable by the developer, so messages shall be rich and instructive:

- **400 Bad Request** — request body contains syntax errors.
- **401 Unauthorized** — credentials absent or insufficient; `WWW-Authenticate` header required.
- **403 Forbidden** — request violates business-logic constraints on resource manipulation.
- **404 Not Found** — no resource at the requested location.
- **405 Method Not Allowed** — unsupported verb; `Allow` header lists supported methods.
- **409 Conflict** — request incompatible with current resource state; the body shall clearly explain the conflict and resolution steps.
- **429 Too Many Requests** — client exceeded its rate SLA and the platform is not blocking per the subscribed rate-limiting policy.

**Server-side errors (5xx)** — not developer-resolvable, so external detail is minimized while bodies include references to internal debugging information:

- **500 Internal Server Error** — every server-side error not covered by another 5xx code.
- **503 Service Unavailable** — request within SLA but capacity is insufficient. `Retry-After` shall be set to a computed time when determinable, otherwise 2 seconds by default; repeated 503s shall apply exponential back-off to the `Retry-After` value.

### 8.3 Cache-Related Header Requirements

Caching behavior is governed by the headers enumerated in Section 5 (`Expires`, `Last-Modified`, `Age`, and conditional-GET support via 304).

### 8.4 Error Suppression

All APIs shall support the `suppressErrors` query parameter. When true, the response status is guaranteed to be 200 while the body still carries the standard error structure of §8.2.
