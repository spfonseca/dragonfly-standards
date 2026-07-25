# RESTful API Design Standard for Enterprise Reuse

| Field | Value |
|---|---|
| **Version** | 1.1 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-07-20 |

## Purpose

This standard exists so that every REST API the organization builds behaves like part of one
coherent platform rather than a collection of independently-invented interfaces — establishing a
single set of conventions for naming, versioning, error handling, security, and lifecycle
management that both API producers and consumers can rely on without re-learning them for each new
API.

## Value Proposition

- **Accelerated development** — settled conventions remove whole classes of design decisions from
  every project (naming, pagination, errors, and versioning are decided once, organization-wide);
  the contract-first workflow lets producer and consumer teams build in parallel against the agreed
  interface; and familiarity compounds across the catalog, so each API is faster to build and
  faster to consume than the last.
- **Most cost-effective development** — the interface is the most expensive part of an API to
  change once consumers depend on it. Catching design defects at review time costs a fraction of
  post-release remediation, and uniform contracts unlock automation — generated clients, mocks,
  documentation, and gateway policy — that bespoke designs must hand-build.
- **Consistent design quality** — the standard encodes the organization's accumulated design
  judgment, so every API reflects its best thinking rather than the varying experience of whichever
  team built it. Predictable, least-surprise interfaces also eliminate the consumer defects caused
  by guessed-at semantics.
- **Enablement of reuse** — reuse is the result of intentional design that considers a collection
  of use cases rather than a single consumer's. APIs governed by this standard are platform APIs:
  the embodiment of business domains with development longevity, built to serve workflows that
  don't yet exist as readily as the one that funded them.

## Scope

This standard applies to all RESTful APIs intended for broad enterprise reuse. Backend-for-Frontend
(BFF) APIs are recommended, but not required, to conform to this standard.

---

## 1. APIs as Products

### 1.1 Ensure every API has a known, committed adopter before development begins.

[REQUIRED] The first release of each API shall have at least one known, committed adopter of value, identified before development begins. *Rationale:* APIs built without a demonstrated consumer become unused surface area that still carries lifecycle and security cost.

### 1.2 Quantify and justify each service's return on investment before design proceeds.

[REQUIRED] ROI shall be quantified at the service level — a service being a collection of related APIs — during roadmap planning and stored with the service's product documentation; design shall not proceed until the return is deemed sufficient. *Rationale:* Front-loading the economic decision prevents sunk-cost commitment to low-value interfaces.

### 1.3 Design each API for reuse across multiple consumers.

[RECOMMENDED] APIs should be designed for reuse across multiple consumers, so a single design serves many workflows rather than a single point-to-point integration. *Rationale:* Reuse is where the standardization overhead pays back; single-purpose APIs multiply catalog size without multiplying value.

### 1.4 Package each service as a cohesive set of APIs that collectively fulfill customer needs.

[RECOMMENDED] Each service should be packed with a cohesive set of APIs — a well-defined product offering — that collectively fulfills customer needs, and the total number of services a customer needs should be kept convenient for them, since each subscription requires management. *Rationale:* A customer served by a few well-packaged services integrates and manages far less than one forced to assemble and administer many fragmented subscriptions.

### 1.5 Treat every API as a first-class product.

[REQUIRED] APIs shall be managed as first-class products on par with the organization's other software products — with product-management support, funding, a roadmap, and self-service enablement for consumers. *Rationale:* An API without product ownership and investment decays into unsupported infrastructure that consumers cannot adopt on their own.

### 1.6 Name each service and API to convey its scope, uniquely and intuitively.

[REQUIRED] Service and API names shall indicate the scope of capabilities and resources offered, be intuitive to external developers, differentiate the offering from all others, and be unique; name syntax is capitalized words separated by spaces, terminated by the suffix "Service" or "API" respectively. Names should be technology-independent, and abbreviations should be minimal and well known. *Rationale:* The name is the first thing a prospective consumer evaluates; it must communicate purpose at a glance. *Example:* E-Commerce Service (service); Update Cart API (API)

## 2. Governance

### 2.1 Validate conformance automatically in the CI/CD pipeline.

[REQUIRED] CI/CD pipelines shall validate API definitions against this standard, and shall verify the API implementation against its OpenAPI contract definition. *Rationale:* Automated conformance checks catch drift on every build, where manual review cannot scale or keep pace.

### 2.2 Formally review every API design before implementation.

[REQUIRED] Every API design shall be formally reviewed at least once prior to implementation. *Rationale:* Interface mistakes are cheap to fix before code exists and expensive afterward, because the interface is the client contract.

### 2.3 Register every service in the service registry.

[REQUIRED] Every service shall be registered in the service registry, with the metadata — including owner, domain, and lifecycle stage — that makes it discoverable and subscribable. *Rationale:* A service that cannot be found or subscribed to delivers no reuse value regardless of its design quality.

### 2.4 Publish each service's lifecycle state and quality profile.

[REQUIRED] Each service shall publish its lifecycle state and a quality profile attestation so consumers know what they are getting before they depend on it. *Rationale:* Consumers can only make sound adoption decisions when maturity and quality are declared rather than discovered in production.

### 2.5 Limit and manage major version changes.

[REQUIRED] Major version changes shall be limited and actively managed: release only the minimum viable API — endpoint–verb combinations with clear business justification. *Rationale:* Every major version imposes migration cost on all consumers; shipping only well-understood, justified surface area minimizes the breaking changes that force one.

### 2.6 Batch backward-incompatible changes into a single major-version upgrade.

[RECOMMENDED] Accumulate breaking changes and release them together in one major version whenever practicable, rather than issuing frequent major version changes. *Rationale:* Each major upgrade imposes migration cost on every consumer; batching amortizes that cost.

### 2.7 Announce deprecations with the Deprecation response header.

[REQUIRED] Responses from a deprecated API version shall carry the Deprecation header (§10.15); the retirement date is communicated through the developer portal (§2.8), not a response header. *Rationale:* Machine-readable deprecation lets client tooling warn developers automatically, long before a human reads release notes.

### 2.8 Publish an end-of-life date whenever deprecating a version.

[REQUIRED] Deprecation shall record an end-of-life date, published to the developer portal where subscription occurs. *Rationale:* Consumers cannot plan migration without a firm retirement date.

### 2.9 Publish a migration plan for every major-version upgrade.

[REQUIRED] The provider shall supply a migration plan for every major version upgrade, published to the developer portal where subscription occurs. *Rationale:* A migration plan converts a breaking change from a surprise into a managed transition.

### 2.10 Rate-limit every API at the platform level.

[REQUIRED] All APIs shall be rate limited, with enforcement performed by the platform according to the consumer subscription terms — never by the provider implementation. *Rationale:* Enforced limits protect shared capacity, and centralizing enforcement in the platform keeps policy uniform and out of every provider's code.

## 3. Domain-Driven Design

### 3.1 Establish domain-driven boundaries.

[REQUIRED] Boundaries shall be domain-driven: bounded contexts each contain a set of domains, and every service shall be scoped within exactly one domain. *Rationale:* Boundaries drawn from the business domain keep services cohesive and ownership unambiguous; boundaries drawn from anything else drift as the organization changes.

### 3.2 Use an anti-corruption layer between bounded contexts.

[REQUIRED] Interactions between APIs in different bounded contexts shall pass through an anti-corruption layer. *Rationale:* Translating at the boundary keeps one context's model from leaking into and distorting another's.

### 3.3 Publish relevant business domain events.

[REQUIRED] All APIs shall publish their relevant business domain events. *Rationale:* Published events let other contexts react to state changes without synchronous coupling to the owning service.

### 3.4 Speak the language of the domain experts.

[REQUIRED] Within a given domain, resource names, fields, error codes, and documentation shall match the terms domain experts use. *Rationale:* A ubiquitous language eliminates translation between business and interface, where meaning is most often lost.

## 4. Architecture & REST Constraints

### 4.1 Give every resource a permanent, directly addressable URL and a UUID instance identifier.

[REQUIRED] Every resource shall be directly addressable by a stable URL, without prior navigation or session context; URLs are permanent — never recycled or repurposed for a different resource — and instance identifiers shall be unique and conform to UUID (RFC 4122). *Rationale:* Permanent, directly addressable identifiers keep references stable across distributed systems and prevent one resource's identity from silently becoming another's.

### 4.2 Represent all character-based interactions as JSON.

[REQUIRED] All character-based request and response content shall be represented as JSON (application/json). *Rationale:* A single mandatory representation guarantees any client can interoperate without bespoke encoding.

### 4.3 Expose only the approved uniform verb set.

[REQUIRED] Only GET, POST, PATCH, DELETE, and HEAD shall be used, each honoring its required semantics (§9): GET is safe and idempotent; POST is neither safe nor idempotent; PATCH is neither safe nor guaranteed idempotent; DELETE is idempotent but not safe; HEAD is safe and idempotent. *Rationale:* A constrained, uniform interface is what makes REST resources predictable across the whole API ecosystem.

### 4.4 Keep every interaction stateless.

[REQUIRED] APIs shall hold no in-memory client state between interactions; each request carries everything needed to process it in its headers, URL, and body. *Rationale:* Statelessness is what allows horizontal scaling and transparent failover.

### 4.5 Keep business APIs and Backend-for-Frontend APIs separate.

[REQUIRED] Business APIs and Backend-for-Frontend (BFF) APIs shall always be separated: business APIs are long-lived and designed for enterprise reuse; BFF APIs are short-lived and specific to a product user experience. *Rationale:* Mixing the two couples durable enterprise contracts to the churn of individual user experiences, so neither can evolve at its natural pace.

### 4.6 Make the common workflows the easiest ones to code.

[RECOMMENDED] APIs should make their common workflows the easiest ones to code. *Rationale:* The first developer experience of an API is decisive for adoption; developers embrace APIs whose everyday tasks take the least effort to code.

### 4.7 Design each API around a single, well-bounded responsibility.

[REQUIRED] Each API shall be designed around a single, well-bounded responsibility; endpoints that mix domains shall not be exposed. *Rationale:* A mixed-domain API couples unrelated consumers and evolution cycles, so no one can change without everyone paying.

### 4.8 Make every API independently deployable.

[REQUIRED] APIs shall be independently deployable. *Rationale:* Deployment coupling turns every release into a multi-team coordination event and erases the autonomy that service boundaries exist to provide.

### 4.9 Prohibit shared databases between services.

[REQUIRED] Services shall not share databases; data owned by another service shall be accessed only through that service's API. *Rationale:* A shared database is a hidden contract that bypasses the API, coupling services at the schema level where change is hardest to manage.

### 4.10 Route all traffic through a mediating intermediary.

[REQUIRED] All API traffic shall be routed through a platform-managed intermediary (such as an API gateway); direct client-to-service connections shall not be permitted, and clients shall not depend on the intermediary topology between themselves and the service. *Rationale:* The intermediary is where authentication, rate limiting, and observability are enforced — traffic that bypasses it bypasses every platform control — and topology independence leaves the provider free to change intermediaries without breaking clients.

### 4.11 Keep representations free of client- and channel-specific formatting.

[REQUIRED] Resource representations shall be free of client-specific or channel-specific formatting logic. *Rationale:* Formatting baked into a representation serves one consumer and burdens every other; presentation belongs to the client.

### 4.12 Allow verb-based endpoints where they are more natural, used judiciously.

[RECOMMENDED] Pure REST resource modeling should be bent to allow verb-based endpoints when a verb is more natural for developers to understand — applied judiciously, through the API types below. *Rationale:* Developers understand "cancel an order" faster than a contrived state mutation on the entity; pragmatism serves adoption better than purity.

### 4.13 Use Entity APIs to manipulate resource state.

[REQUIRED] An Entity API manipulates the state of a resource (CRUD); its state effects are on the resource itself, it uses the full verb set (GET, POST, PATCH, DELETE, HEAD), and its URL is the plural resource noun. *Rationale:* Anchoring state manipulation to the resource keeps CRUD uniform and predictable across every business object. *Example:* `/orders/{id}`

### 4.14 Use Function APIs to compute values.

[REQUIRED] A Function API computes a value and shall be pure — never producing side effects; it uses POST only, and its URL is the verb under the service name. *Rationale:* A declared-pure computation can be called freely from any workflow without state consequences. *Example:* `/pricing/calculate`

### 4.15 Use Task APIs to perform a business action on a single resource.

[REQUIRED] A Task API performs a business action whose state effects are confined to a single resource; it uses POST only, and its URL places the verb as the last path segment on that resource. *Rationale:* Naming the action on its resource keeps business operations discoverable without distorting the entity model with pseudo-attributes. *Example:* `/orders/{id}/cancel`

### 4.16 Use Orchestration APIs to perform a business action spanning multiple resources.

[REQUIRED] An Orchestration API performs a business action whose state effects span multiple resources; it uses POST only, and its URL places the verb as the last path segment, attached to the most prominent resource in the orchestration. *Rationale:* A single orchestration endpoint gives multi-resource workflows one addressable, governable home instead of scattering them across clients. *Example:* `/orders/{orderId}/fulfill`

## 5. Resilience

### 5.1 Tolerate retries and duplicate delivery.

[REQUIRED] All APIs shall tolerate retries and duplicate delivery (at-least-once semantics), whether through natural idempotency or idempotency keys (§10.20). *Rationale:* Networks redeliver; an operation that corrupts state on a second delivery fails exactly when the infrastructure is doing its job.

### 5.2 Prohibit client affinity.

[REQUIRED] No API implementation shall depend on client affinity; any instance of an API shall be able to handle any request. *Rationale:* Affinity-free handling is what makes horizontal scaling and transparent failover possible.

### 5.3 Enforce timeouts on all downstream calls and fail fast.

[REQUIRED] Every downstream call shall carry a timeout, and APIs shall fail fast rather than queue work indefinitely. *Rationale:* An unbounded wait converts one slow dependency into exhausted threads and connections everywhere upstream.

### 5.4 Use circuit breakers when consuming other APIs.

[RECOMMENDED] APIs consuming other APIs should implement circuit breakers to prevent cascading failures. *Rationale:* A tripped breaker turns a failing dependency into a fast, handled error instead of a platform-wide outage.

### 5.5 Apply the tolerant reader principle to responses.

[REQUIRED] Clients shall ignore unknown fields in responses rather than fail; request bodies, by contrast, shall conform to the schema, with undeclared fields rejected (§13.4). *Rationale:* Tolerant reading lets providers add response fields as compatible minor changes (§6.1) without coordinating every consumer, while strict request validation keeps the attack and error surface closed.

### 5.6 Avoid distributed transactions across APIs.

[REQUIRED] Transactions shall not span APIs; use eventual consistency, with failures undone through compensating actions per the Saga pattern. *Rationale:* A transaction spanning APIs holds locks across ownership boundaries and makes every participant's availability everyone's problem.

### 5.7 Degrade gracefully when optional dependencies are unavailable.

[RECOMMENDED] APIs should deliver partial functionality when optional dependencies are unavailable rather than failing the whole request. *Rationale:* Graceful degradation keeps the workflows that never needed the failed dependency alive.

### 5.8 Offer short operations synchronously and long-running operations asynchronously.

[REQUIRED] APIs shall answer synchronous requests within short, predictable response times; any operation that cannot shall be offered asynchronously via the job pattern (§14). *Rationale:* Long synchronous calls hold connections open, invite client timeouts, and hide progress that a job resource would expose.

## 6. Versioning

### 6.1 Version every API and resource model as major.minor.

[REQUIRED] All APIs and resource models shall be versioned following `<major number>.<minor number>`: increment the major number for any backward-incompatible change and the minor number for changes that preserve the client contract. Only top-level resources are versioned (§7.8). *Rationale:* A predictable version contract lets consumers upgrade minors freely and plan for majors deliberately.

### 6.2 Recognize the common backward-incompatible API changes.

[REQUIRED] A backward-incompatible API change is any syntactic or semantic difference that can alter behavior a client was guaranteed; common cases are removing or renaming an operation, adding a required request parameter or field, removing or changing the semantics of an existing parameter, changing the meaning of a status code or error code, and tightening the authorization an operation requires. *Rationale:* A shared, precise definition prevents breaking changes from being mislabeled as minor.

### 6.3 Recognize the common backward-incompatible resource-model changes.

[REQUIRED] A backward-incompatible resource-model change alters what a client was guaranteed about the model; common cases are removing or renaming a field, changing a field's data type, format, or semantics, making an optional field required, tightening a constraint on an existing field, and removing or repurposing an enumeration value. Adding optional fields and adding new enumeration values are backward compatible (§5.5) — except values of the reserved 'state' enumeration, whose changes are always breaking (§7.12). *Rationale:* Model evolution stays honest when every provider judges compatibility by the same cases.

### 6.4 Constrain API and resource versions to the same major number.

[REQUIRED] When a resource is carried in an API request or response body, the resource model's major version number shall be the same as the API's major version number. *Rationale:* One major version across the interface and its payloads means a single compatibility judgment covers the whole exchange.

## 7. Resource Modeling

### 7.1 Name each resource as the noun of the business object it represents, plural for collections.

[REQUIRED] Every resource represents a coarse-grained business object, and its name shall be the information-oriented noun for that business object; multi-instance resources take plural names, and genuine singletons take singular names and omit the /\<ID\> pattern. Function-oriented (verb) resources require explicit approval and shall be rare. Names should be technology-independent, with abbreviations minimal and well known. *Rationale:* Naming the business object directly makes resource semantics self-evident to anyone who knows the domain. *Example:* `customers` (collection), `configuration` (singleton)

### 7.2 Model each resource around its essential attributes and relationships.

[REQUIRED] Resource design shall capture the business essence of the resource — its fundamental attributes and relationships — informed by how customers actually use it. *Rationale:* Modeling from real usage produces resources that fit customer workflows.

### 7.3 Ensure the resource model is a data abstraction over the implementation.

[REQUIRED] The resource model shall provide a data abstraction over the implementation: attributes that only the backend requires are not exposed, and the physical schema of backend capabilities shall not determine the resource design directly. *Rationale:* An abstracted model couples consumers to the business object rather than to persistence decisions that change beneath it.

### 7.4 Choose resource granularity from real customer usage.

[RECOMMENDED] Deliberately manage resource size, complexity, and the choice between referenced and embedded information based on consumer access patterns, avoiding both chatty micro-resources and monolithic blobs. *Rationale:* Right-sized resources minimize both over-fetching and chatty multi-call sequences.

### 7.5 Define resource structure in the organization's shared information model.

[REQUIRED] Resource structure and semantics shall be defined in, and adhere to, the organization's shared information model. *Rationale:* A shared information model is what lets the same concept mean the same thing across every API.

### 7.6 Assign each resource to exactly one owning domain.

[REQUIRED] Every resource belongs to exactly one approved domain, which namespaces it and sets development-ownership boundaries; resource code lives in a package named for the resource, nested in its domain package. *Rationale:* Single ownership prevents the diffusion of responsibility that leaves resources unmaintained. *Example:* `user/customers/CustomersResource.java`

### 7.7 Represent relationships as references or embedded data deliberately.

[RECOMMENDED] Choose between linking to a related resource and embedding its representation based on how consumers traverse the relationship and how independently the two evolve. *Rationale:* The reference-versus-embed choice drives both payload size and coupling; making it by default produces one or the other by accident.

### 7.8 Fold sub-resource changes into the parent resource's version.

[REQUIRED] Sub-resources follow the same naming standards as top-level resources but are not independently versioned; a breaking sub-resource change increments the parent version. *Rationale:* Consumers track one version per top-level resource rather than a matrix of sub-resource versions.

### 7.9 Carry common metadata in a top-level metadata attribute on every resource.

[REQUIRED] Every textual resource representation shall carry a top-level metadata JSON object (§16.1) holding, at minimum: createdAt and lastUpdatedAt timestamps (ISO 8601, §16.3), resourceType (the resource's type name, e.g. order, cart), and resourceVersion (the resource model version, §6.1). For an org-scoped resource it shall additionally carry organizationId (the owning organization) and createdBy (the identifier of the user who created it) — read-only provenance the server assigns and immutably maintains (§13.7); consumers treat both as informational and never send them on write. *Rationale:* Uniform metadata in one predictable place lets consumers and tooling handle provenance, freshness, and versioning identically across every resource; carrying the owning organization and creator here — rather than as domain attributes — states ownership without inviting clients to build logic on tenancy, and gives cross-organization viewers (a guest or collaborator, for whom the owning organization is not their own) the context to display it. *Example:*

```json
"metadata": {
  "createdAt": "2026-07-15T09:30:00Z",
  "lastUpdatedAt": "2026-07-16T14:05:00Z",
  "resourceType": "order",
  "resourceVersion": "1.4",
  "organizationId": "b3f1c2a0-4e5d-4a1b-9c8e-7d6f5a4b3c2d",
  "createdBy": "9d2c7e10-1a2b-3c4d-5e6f-7a8b9c0d1e2f"
}
```

### 7.10 Enumerate the lifecycle states of every stateful resource.

[REQUIRED] Resources with a lifecycle shall enumerate its possible states. Whether a lifecycle resource supports hard DELETE, a terminal state, or both is the resource designer's decision, made per resource. *Rationale:* An explicit state enumeration makes resource behavior reviewable, testable, and predictable to every consumer instead of emergent from implementation.

### 7.11 Expose the current lifecycle state in the reserved state attribute.

[REQUIRED] The current lifecycle state shall be exposed in a top-level 'state' attribute of the resource representation; the attribute name 'state' is reserved platform-wide for this purpose and shall not be used for any other meaning. *Rationale:* One reserved attribute means every consumer finds the lifecycle state the same way on every resource.

### 7.12 Treat any change to the state set as backward-incompatible.

[REQUIRED] Adding, removing, or renaming a state is a breaking change requiring a major version increment (§6.1). *Rationale:* Clients reasonably branch on the enumerated state values; an unknown state breaks client logic.

## 8. URL Structure

### 8.1 Target the endpoint base that matches the environment.

[REQUIRED] Endpoints shall use the endpoint base for their environment, following the pattern `api.<environment>.<domain name>`, where environment is one of dev, stage, qa, perf, or sandbox and is omitted for production. *Rationale:* Environment-specific bases keep traffic for each environment cleanly separated.

| Environment | Prefix | Endpoint Base |
|---|---|---|
| Production | *(none)* | `https://api.example.com` |
| Development | `dev` | `https://api.dev.example.com` |
| Staging | `stage` | `https://api.stage.example.com` |
| Quality Assurance | `qa` | `https://api.qa.example.com` |
| Performance | `perf` | `https://api.perf.example.com` |
| Sandbox | `sandbox` | `https://api.sandbox.example.com` |

### 8.2 Compose every path segment as lowercase words separated by dashes.

[REQUIRED] All URL path segments shall use lowercase alphabetic characters only, with a dash between words. *Rationale:* A single, case-safe segment syntax eliminates the casing mismatches that plague clients, servers, and documentation. *Example:* `/purchase-orders`

### 8.3 Place the API major version immediately after the endpoint base.

[REQUIRED] The first path segment after the endpoint base shall be the major version number of the API, in the form `v<number>`. *Rationale:* Version-first URLs make the contract in play unambiguous for every request. *Example:* `https://api.example.com/v1/orders`

### 8.4 Address a collection resource as the versioned endpoint base plus the plural resource name.

[REQUIRED] The URL of a collection resource shall be `<endpoint base>/v<number>/<plural resource name>`. *Rationale:* One predictable collection address per resource means any consumer can find it from the resource name alone. *Example:* `https://api.example.com/v1/orders`

### 8.5 Serve the latest minor version and identify it in a response header.

[REQUIRED] Because URLs carry only the major version, the API shall serve the latest minor version of that major and shall identify the version actually returned in the API-Version custom response header (§10.17), in the form `<major number>.<minor number>`. *Rationale:* Consumers receive compatible improvements automatically while every response remains self-identifying.

### 8.6 Address a resource instance as the collection URL plus its identifier.

[REQUIRED] The URL of an instance of a collection resource shall be `<endpoint base>/v<number>/<plural resource name>/<resourceId>`: the collection URL (§8.4) followed by the instance identifier as a path segment, never as a query parameter. *Rationale:* Instance addresses derived mechanically from the collection address keep every object individually addressable and cacheable. *Example:* `https://api.example.com/v1/orders/7c9e6679-7425-40de-944b-e07fc1f90ae7`

### 8.7 Nest sub-resource URLs shallowly, reserving the deepest level for truly exceptional cases.

[REQUIRED] A sub-resource is addressed by appending its name and instance identifier to the parent instance URL, `<endpoint base>/v<number>/<plural resource name>/<resourceId>/<sub-resource name>/<sub-resourceId>`, and a sub-sub-resource by one further name and identifier pair, `.../<sub-resource name>/<sub-resourceId>/<sub-sub-resource name>/<sub-sub-resourceId>`; nesting a third level (sub-sub-sub resources) shall be reserved for truly exceptional cases. *Rationale:* Shallow nesting keeps URLs comprehensible and stops deep object graphs from being encoded as identifiers. *Example:* `https://api.example.com/v1/orders/{orderId}/line-items/{lineItemId}`

### 8.8 Address elements of array-valued sub-resources by server-assigned identifier.

[REQUIRED] When a sub-resource or sub-sub-resource collection is an array, an element shall be addressed by a server-assigned, immutable UUID path segment (§16.7), with the path parameter named `<singular element name>Id`; positional (index-based) addressing shall not be used. *Rationale:* Positional indexes shift as elements are added and removed, so a held reference can silently come to address a different element; a server-assigned identifier keeps every reference stable for the element's lifetime. *Example:* `https://api.example.com/v1/persons/{personId}/secondary-addresses/{addressId}`

### 8.9 Serve interface metadata from the reserved metadata endpoints.

[REQUIRED] The API provider shall serve the reserved metadata endpoints for every top-level resource, each returning both HTML and JSON, exposing interface documentation, version history, and release notes; when the request headers do not specify a representation, JSON is returned. *Rationale:* A uniform metadata surface lets consumers and tooling discover documentation the same way for every resource.

| Endpoint | Returns |
|---|---|
| `<top-level resource name>/interface-doc` | Interface documentation |
| `<top-level resource name>/version-history` | Version history (version, lifecycle state, end-of-life date) |
| `<top-level resource name>/release-notes` | Release notes |

## 9. HTTP Methods

### 9.1 Use GET for safe, idempotent reads only.

[REQUIRED] GET shall be read-only, safe, and idempotent, never modifying server state. *Rationale:* Safe reads can be cached, prefetched, and retried freely by intermediaries.

### 9.2 Use PATCH to update existing resources, never to create.

[REQUIRED] PATCH shall apply a partial update to an existing resource: an absent field is left unchanged and a null field is cleared (§16.6); the request body is ordinary application/json (§16.1), and PATCH to a nonexistent resource returns 404. A singleton sub-resource shares its parent's existence: PATCH against an empty value sets it (a set failing the sub-resource's validation yields 400), and 404 applies only when the parent itself does not exist. *Rationale:* Restricting PATCH to existing resources keeps creation semantics unambiguous.

### 9.3 Use POST to create resources, returning the new resource URL.

[REQUIRED] POST shall create a new resource and return its URL; POST is neither safe nor idempotent and shall never be used to update. *Rationale:* A single creation verb, distinct from update, keeps write intent explicit.

### 9.4 Use DELETE to remove resources idempotently.

[REQUIRED] DELETE shall remove the resource and be idempotent (not safe); subsequent access returns Not Found. *Rationale:* Idempotent deletion lets clients retry after a lost response without special-casing.

### 9.5 Use HEAD to return a GET's headers with an empty body.

[REQUIRED] HEAD shall return exactly the headers a GET would produce, with no body. *Rationale:* HEAD lets clients check existence, size, or freshness without transferring the representation.

### 9.6 Reject any verb outside the approved set.

[REQUIRED] Verbs outside GET/POST/PATCH/DELETE/HEAD shall be rejected with 405, and the Allow header shall list supported methods. *Rationale:* Explicit rejection with Allow tells the client exactly what it may do instead.

## 10. HTTP Headers

### 10.1 Use only the essential header set.

[REQUIRED] APIs shall use only the headers defined in this section — an essential set kept deliberately small, as with the approved status codes (§12.1); further standard headers are adopted only by updating this standard. *Rationale:* Reducing unnecessary complexity aids adoption and ease of use for producers and consumers alike.

### 10.2 Compose custom headers as a reserved custom name plus the header name.

[REQUIRED] Request and response. Custom headers shall be used only where no standard HTTP header exists, and follow `<custom name>-<header name>`, words separated by hyphens; the custom name is a reserved prefix, such as an organization, platform, or product name. *Rationale:* A reserved prefix prevents collisions with standard or third-party headers.

### 10.3 Use Accept to negotiate the response representation.

[REQUIRED] Request. Accept states the representation the client wants: representations are returned as application/json, and the metadata endpoints (§8.9) return JSON or HTML at the client's choice; when Accept is absent, JSON is returned. *Rationale:* Standard negotiation lets any client obtain a representation it can process without out-of-band agreement.

### 10.4 Use Accept-Charset to declare UTF-8.

[REQUIRED] Request. Accept-Charset is UTF-8 (§16.2). *Rationale:* One declared encoding eliminates charset-negotiation failures.

### 10.5 Use Authorization to carry the caller's credentials.

[REQUIRED] Request. Every request carries the caller's access credentials in Authorization, per the organization's approved authentication scheme (§13.2). *Rationale:* A single, standard credential location lets every API and intermediary validate identity uniformly.

### 10.6 Use Content-Type to make every payload self-describing.

[REQUIRED] Request and response. Every payload shall declare its representation via a correct Content-Type carrying a standard, IANA-registered media type: application/json for representations, JSON or HTML for the metadata endpoints. *Rationale:* Self-describing payloads let any client and intermediary interpret content without out-of-band knowledge.

### 10.7 Use Content-Encoding for standard compression.

[RECOMMENDED] Request and response. Standard content encodings (e.g. gzip) apply in both directions per the HTTP specification. *Rationale:* Standard content coding reduces bandwidth without bespoke compression schemes.

### 10.8 Use Cache-Control to declare cacheability on every response.

[REQUIRED] Response. Every response carries Cache-Control per the caching rules (§17.1–§17.3); origin services never set Age, which belongs to intermediary caches (§17.2). *Rationale:* Explicit cacheability on every response replaces heuristic caching with declared intent.

### 10.9 Use Allow with every 405.

[REQUIRED] Response. Every 405 shall carry Allow listing the supported methods (§9.6). *Rationale:* Explicit rejection with Allow tells the client exactly what it may do instead.

### 10.10 Use Expires only for legacy compatibility.

[OPTIONAL] Response. Expires may accompany Cache-Control for legacy consumers; it shall not substitute for it (§17.2). *Rationale:* Cache-Control is the authoritative mechanism; Expires exists for clients that predate it.

### 10.11 Use Last-Modified for legacy compatibility and If-Modified-Since validation.

[OPTIONAL] Response. Last-Modified may accompany Cache-Control (§17.2) and enables If-Modified-Since validation where provided (§17.6). *Rationale:* Modification timestamps enable validation without retransmitting the representation, at legacy-client fidelity.

### 10.12 Use Location with 302 and 201.

[REQUIRED] Response. Location is required with 302, carrying the new location, and is set to the new resource URI on 201. *Rationale:* A machine-readable target lets clients follow moves and find created resources without parsing bodies.

### 10.13 Use Retry-After with 503 and 429.

[REQUIRED] Response. A request exceeding the consumer's rate limit shall receive 429 with Retry-After set; 503 responses shall set Retry-After to a computed time when determinable, otherwise 2 seconds by default, applying exponential back-off to Retry-After on repeated 503s; and GETs of non-terminal asynchronous operation status include Retry-After as a polling hint (§14.5). When over-limit traffic becomes excessive, the platform may silently block it, owing the client no particular response. *Rationale:* A machine-readable back-off signal lets well-behaved clients recover without hammering the service.

### 10.14 Use WWW-Authenticate with every 401.

[REQUIRED] Response. Every 401 carries WWW-Authenticate describing the required authentication (§13.2). *Rationale:* The challenge tells the client how to authenticate rather than leaving it to guess.

### 10.15 Use Deprecation on responses from deprecated API versions.

[REQUIRED] Response. Responses from a deprecated API version carry the Deprecation header (§2.7); only APIs are deprecated, never the resources they utilize. *Rationale:* Machine-readable deprecation lets client tooling warn developers automatically.

### 10.16 Use Example-Result-Set-Count on every collection response.

[REQUIRED] Response (custom). Whenever a collection is returned, Example-Result-Set-Count carries the element count (§15.4). *Rationale:* Clients can render totals and plan paging without a separate count call.

### 10.17 Use API-Version to identify the version served.

[REQUIRED] Response (custom). Every response carries an API-Version custom header following the `<custom name>-<header name>` pattern (§10.2), stating the version served as `<major number>.<minor number>` (§8.5). *Rationale:* Self-identifying responses remove all ambiguity about which contract produced them. *Example:* `Dragonfly-API-Version: 1.5`

### 10.18 Use Correlation-Id to relate the requests of a business workflow.

[REQUIRED] Request and response (custom). Applications conducting a multi-request conversation with another application or platform shall carry the same Correlation-Id custom header, following the `<custom name>-<header name>` pattern (§10.2), on every request in the conversation, and responses echo it. *Rationale:* A conversation-level identifier is what ties the many requests of one business workflow together across applications. *Example:* `Dragonfly-Correlation-Id: 7c9e6679-7425-40de-944b-e07fc1f90ae7`

### 10.19 Use Request-Id to trace a single request end to end.

[REQUIRED] Request and response (custom). Every request is assigned a unique Request-Id custom header following the `<custom name>-<header name>` pattern (§10.2), generated by the platform when the client does not supply one, echoed on the response, and propagated across the full request/response path (§22.1). *Rationale:* A per-request identifier that travels the whole path is what makes one failing request traceable across every service it touched. *Example:* `Dragonfly-Request-Id: 550e8400-e29b-41d4-a716-446655440000`

### 10.20 Use Idempotency-Key where duplicate creation is costly.

[REQUIRED] Request (custom). A POST operation whose duplicate execution is costly — e.g. payments, order placement, provisioning — shall accept a client-supplied Idempotency-Key custom header following the `<custom name>-<header name>` pattern (§10.2), and a retried request carrying the same key shall not create a duplicate resource; other POST operations need not support the key. *Rationale:* Networks drop responses; where a duplicate create is expensive, the key is what makes retry safe — and where it is harmless, the bookkeeping is not worth mandating. *Example:* `Dragonfly-Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000`

### 10.21 Use ETag to identify the representation returned.

[REQUIRED] Response. Cacheable and concurrency-sensitive representations carry an ETag; ETags used for concurrency are strong validators (§17.5). *Rationale:* The ETag is the validator underpinning both conditional retrieval and optimistic concurrency.

### 10.22 Use Vary to declare representation variance.

[REQUIRED] Response. When any request header influences the representation returned for a URL, the response declares that header in Vary (§17.4). *Rationale:* Without accurate Vary, caches serve one consumer's representation to another.

### 10.23 Use If-None-Match for conditional retrieval.

[REQUIRED] Request. Clients may present a held ETag in If-None-Match on GET and HEAD; the API honors it, returning 304 when the representation is unchanged (§17.6). *Rationale:* Validation avoids retransmitting representations the client already holds.

### 10.24 Use If-Match for optimistic concurrency.

[REQUIRED] Request. Writes that must not clobber concurrent updates require If-Match carrying the resource's current ETag; a stale or missing precondition yields 412 (§17.7). *Rationale:* The precondition is what turns a lost-update race into a detectable, retryable failure.

### 10.25 Use If-Modified-Since where Last-Modified is provided.

[RECOMMENDED] Request. Where a resource provides Last-Modified (§10.11), the API should honor If-Modified-Since on GET and HEAD (§17.6). *Rationale:* Timestamp validation gives legacy clients conditional retrieval without ETag support.

## 11. Request Parameters

### 11.1 Name parameters in camelCase.

[REQUIRED] Parameter names use camelCase — first word lowercase, subsequent words capitalized, characters [a-zA-Z] only, no spaces. *Rationale:* A single casing convention removes a whole class of "was it snake or camel?" integration errors. *Example:* `pageSize`, `lastModifiedDate`

### 11.2 Reserve the standard query-parameter names for their defined purposes.

[REQUIRED] The reserved query-parameter names are standardized across all APIs and shall not be repurposed. *Rationale:* Reserved names mean a consumer learns page/pageSize/sort/q once and reuses them everywhere.

| Parameter | Purpose |
|---|---|
| `page` | Page of the result set to return; page 1 is the first |
| `pageSize` | Maximum number of results per page |
| `q` | OData query expression for complex searches |
| `sort` | Result-set ordering criteria |
| `expand` | Related resources to embed in the representation (§18) |

### 11.3 Never use matrix parameters.

[REQUIRED] Matrix parameters (name–value pairs qualifying a single path segment) shall not be used. *Rationale:* Matrix parameters are uncommon and add parsing complexity for little benefit.

### 11.4 Keep parameter semantics consistent within the bounded context.

[REQUIRED] Parameter names shall be nouns, intuitive, technology-independent, aligned with the vocabulary of their domain (§3.4), and semantically consistent across the APIs of their bounded context, with abbreviations minimal and well known. *Rationale:* Same-name-same-meaning within a bounded context lets a parameter be understood without consulting each API's docs.

### 11.5 Pass multiple values by repeating the parameter for each value.

[REQUIRED] A request parameter carrying multiple values shall be repeated once per value, never packed into a single delimited string. *Rationale:* Repetition is the standard HTTP form that every framework parses natively; delimiter packing forces bespoke parsing and escaping onto every consumer. *Example:* `?status=open&status=pending`

## 12. Responses

### 12.1 Use only the essential status-code set.

[REQUIRED] APIs shall return only the status codes defined in this section; 1xx codes are never returned, and adherence is the joint responsibility of API implementers and the hosting platform. *Rationale:* Reducing unnecessary complexity aids adoption and ease of use for producers and consumers alike.

### 12.2 Use 200 OK for success without resource creation.

[REQUIRED] 200 is returned for any successful GET, PATCH, DELETE, or HEAD. *Rationale:* A single everyday success code keeps the common case unambiguous.

### 12.3 Use 201 Created when POST creates a resource.

[REQUIRED] 201 is returned for a successful POST, with Location set to the new resource URI (§10.12) and the created resource's representation as the body. *Rationale:* Returning the representation spares every consumer an immediate follow-up GET for the resource it just created.

### 12.4 Use 202 Accepted when the operation continues after the response.

[REQUIRED] 202 is returned when an asynchronous operation is successfully initiated (§14.3): the work continues after the response, whose body carries the tracking representation. *Rationale:* A distinct acceptance code tells the client the request was valid but the outcome is still pending.

### 12.5 Use 302 Found when a logical endpoint has moved.

[REQUIRED] 302 is returned when a logical endpoint has moved and the platform knows the new location, carried in Location (§10.12). *Rationale:* A machine-readable redirect keeps clients working across endpoint moves.

### 12.6 Use 304 Not Modified on conditional reads of unchanged resources.

[REQUIRED] 304 is returned for a conditional GET where the representation is unchanged, with an empty body. *Rationale:* Validation without retransmission saves bandwidth on every cache hit.

### 12.7 Use 400 Bad Request for malformed or invalid requests.

[REQUIRED] 400 is returned when the request body cannot be parsed or input fails validation against its declared types and constraints (§13.4). *Rationale:* A clear syntax-and-validation signal tells the developer the fix is in the request itself.

### 12.8 Use 401 Unauthorized when credentials are absent or invalid.

[REQUIRED] 401 is returned when credentials are missing or insufficient, with WWW-Authenticate (§10.14). *Rationale:* A distinct authentication signal, with its challenge, tells the client how to get in — not merely that it can't.

### 12.9 Use 403 Forbidden for authorization and business-rule denials.

[REQUIRED] 403 is returned when a properly authenticated request is not permitted — an authorization failure (§13.3) or a violated business-logic constraint. *Rationale:* Separating "who are you" from "you may not" lets clients react correctly to each.

### 12.10 Use 404 Not Found when no resource exists at the location.

[REQUIRED] 404 is returned when no resource exists at the requested location. *Rationale:* A definitive absence signal lets clients distinguish a missing resource from a failing service.

### 12.11 Use 405 Method Not Allowed for unsupported verbs.

[REQUIRED] 405 is returned for any verb outside the approved set or unsupported by the resource, with Allow listing the supported methods (§9.6, §10.9). *Rationale:* Explicit rejection with Allow tells the client exactly what it may do instead.

### 12.12 Use 409 Conflict when the request is incompatible with resource state.

[REQUIRED] 409 is returned when the request cannot be applied to the current state of the resource. *Rationale:* A state-conflict signal tells the client to re-read and reconcile rather than blindly retry.

### 12.13 Use 412 Precondition Failed when a write's precondition is stale or missing.

[REQUIRED] 412 is returned for a conditional write whose If-Match precondition is stale or absent (§10.24, §17.7). *Rationale:* The precondition failure is what turns a lost-update race into a detectable, retryable failure instead of a silent overwrite.

### 12.14 Use 429 Too Many Requests when the rate limit is exceeded.

[REQUIRED] 429 is returned when the consumer exceeds its rate limit, with Retry-After set (§10.13). *Rationale:* A machine-readable back-off signal lets well-behaved clients recover without hammering the service.

### 12.15 Use 500 Internal Server Error for uncovered server-side failures.

[REQUIRED] 500 is returned for any server-side error not covered by another approved code. *Rationale:* A catch-all failure code separates "we failed" from every condition the client can act on.

### 12.16 Use 503 Service Unavailable for capacity shortfalls.

[REQUIRED] 503 is returned when a request within SLA cannot be served for capacity reasons, with Retry-After set (§10.13). *Rationale:* Separating "we are overloaded" from "we failed" lets clients retry the first and report the second.

### 12.17 Return the standard problem-details error body on every error.

[REQUIRED] Every implementation shall catch every exception and return the standard error body, based on RFC 9457 Problem Details — type, title, status, and detail as the RFC defines them — plus the supportId extension member (§12.19). type is a URI identifying the specific error condition, dereferencing to its documentation, and treated by clients as an opaque, permanent identifier. supportId is always equal to the Request-Id of the failing request (§10.19). *Rationale:* One RFC-based error shape lets every consumer parse failures with a single code path; status carries the standardized coarse classification, and the type URI is at once the branchable identifier and the documentation address.

| Field | Content |
|---|---|
| `type` | URI identifying the specific error condition, dereferencing to its documentation; opaque and permanent |
| `title` | Short, human-readable summary of the condition, stable across occurrences |
| `status` | The HTTP status code of this response, as a JSON number |
| `detail` | Human-readable explanation of this specific occurrence |
| `supportId` | Extension member: globally unique identifier of the occurrence — always equal to the request's Request-Id (§10.19) |

*Example:*

```json
{
  "type": "https://errors.example.com/order-already-shipped",
  "title": "Order already shipped",
  "status": 409,
  "detail": "Order 7c9e6679 has already shipped and cannot be cancelled.",
  "supportId": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 12.18 Make 4xx messages instructive and minimize 5xx external detail.

[REQUIRED] Client-side (4xx) errors are resolvable by the developer, so messages shall be rich and instructive; server-side (5xx) errors are not developer-resolvable, so external detail is minimized while the body carries references to internal debugging information. *Rationale:* Detail helps where the developer can act; on 5xx errors it helps no one and discloses internal system details to the public — an information-disclosure risk (§13.4).

### 12.19 Include a unique support ID on every error.

[REQUIRED] Each error response shall carry a globally unique supportId identifying the occurrence; the supportId is always equal to the Request-Id of the failing request (§10.19). *Rationale:* A correlation handle turns a support conversation into a single-lookup investigation.

### 12.20 Reuse the standard domain-independent error types; declare API-specific types per API.

[REQUIRED] The error-type slugs below are standard and domain-independent; when an API returns one of these conditions it shall use the standard slug — resolved against the service's error type base URI — rather than minting its own. Error types specific to an API shall be declared per API in the service's API endpoint requirements, as a list of type slugs, before implementation. *Rationale:* Consumers branch on the type URI; a shared vocabulary for the universal conditions keeps that branching identical across every API, while the per-API list makes domain-specific conditions reviewable up front instead of invented mid-build.

| Type slug | Status | Condition |
|---|---|---|
| `validation-error` | 400 | Malformed request, or input failing the declared types/constraints (§12.7) |
| `protected-field` | 400 | Attempt to clear or change a field the API declares protected |
| `immutable-identifier` | 400 | Client supplied or changed a server-generated identifier |
| `invalid-reference` | 400 | Request references a resource that does not exist or cannot be used |
| `authentication-error` | 401 | Credentials absent or invalid (§12.8) |
| `permission-denied` | 403 | Authenticated but not authorized (§12.9) |
| `not-found` | 404 | No resource at the location (§12.10); APIs may declare resource-specific `<resource>-not-found` types instead |
| `method-not-allowed` | 405 | Verb not supported at the path (§12.11) |
| `precondition-failed` | 412 | Conditional-write precondition stale or missing (§12.13, §17.7) |
| `rate-limit-exceeded` | 429 | Rate limit exceeded (§12.14) |
| `internal-error` | 500 | Uncovered server-side failure (§12.15) |
| `service-unavailable` | 503 | Capacity shortfall (§12.16) |

## 13. Security

### 13.1 Expose API endpoints over HTTPS only.

[REQUIRED] API endpoints shall be exposed over HTTPS only. *Rationale:* Transport encryption is the baseline that every other control depends on.

### 13.2 Authenticate at the gateway, then re-verify locally in every API.

[REQUIRED] Requests shall present a centrally issued, short-lived, scope-bearing access token in the Authorization header. The gateway performs full authentication — signature, expiry, issuer, audience, revocation — and forwards the validated JWT; each API re-verifies the token locally and statelessly, then applies its own authorization (§13.3). Missing or invalid credentials yield 401 with WWW-Authenticate (§10.14). *Rationale:* Heavy checks run once at the gateway; cheap local re-verification keeps every API safe regardless of how a request arrived; authorization stays where the business rules live.

### 13.3 Authorize through the platform authorization engine.

[REQUIRED] APIs shall perform authorization through the core platform's authorization engine; a properly authenticated but unauthorized request yields 403. *Rationale:* One shared authorization engine gives every API the same policy model and audit trail, instead of per-API reinventions that drift.

### 13.4 Own the application-layer security checks in every implementation.

[REQUIRED] The web application firewall (WAF) filters known attack patterns; the implementation owns every check that requires knowledge of the contract, the domain, or the caller. These checks are required regardless of upstream controls:

- Validate every request against the published OpenAPI contract — types, bounds, required fields — and reject anything that does not conform (§12.7), including undeclared fields.
- Verify the bearer token locally (§13.2); never accept identity from plain headers.
- Enforce authorization per object (§13.3): the caller must be entitled to the specific resource and fields being read or written, with all queries scoped to the caller's tenancy.
- Access data stores only through parameterized queries; encode all output for its destination context.
- Fail closed before side effects, and return standard error bodies (§12.17) that never echo input or leak internals.

*Rationale:* Upstream controls can be bypassed, misconfigured, or removed; the checks owned by the implementation are the ones that hold no matter how a request arrived.

### 13.5 Protect and minimize sensitive data and PII.

[REQUIRED] Sensitive data and PII shall be minimized in payloads, never placed in URLs or log output, encrypted in transit and at rest, and handled per the applicable privacy and data-governance policies. *Rationale:* Data not collected or not exposed cannot be leaked; URLs in particular persist in logs and history.

### 13.6 Keep secrets out of URLs, logs, and source code.

[REQUIRED] Credentials, tokens, and keys shall never appear in URLs, log output, or source repositories. *Rationale:* Each of these is routinely retained and widely readable, making them the most common source of credential leaks.

### 13.7 Assign tenancy and ownership from the authenticated identity, never from the client.

[REQUIRED] A resource's owning organization (its tenancy) and its creator shall be assigned by the server from the authenticated caller's identity at creation, and shall be immutable thereafter. The API shall never read tenancy or ownership from client input: a create or update payload carrying either is rejected, or the fields are ignored — never honored. Reads may expose them only as read-only provenance metadata (§7.9). *Rationale:* Deriving tenancy from the token and never the payload is what prevents a caller from creating or moving a resource into another organization's scope (a tenancy-escape / IDOR class of flaw); making ownership server-assigned and immutable keeps a resource with its owning organization independently of who created it or who later edits it — the organization owns the resource through the member who created it, but that ownership does not follow the user out of the organization.


## 14. Asynchronous Operations

### 14.1 Keep the API runtime free of blocking work.

[REQUIRED] An API runtime requirement, invisible to the API contract: request handling shall never be stalled by blocking work. Slow or processor-heavy operations run outside the request-handling path using the framework's mechanisms for that purpose; background work is always supervised; and every outbound call carries a timeout (§5.3) and explicit limits on connections and concurrent calls. *Rationale:* One blocking operation in the request-handling path stalls every request that worker is serving.

### 14.2 The asynchronous operation pattern: apply it to any work exceeding the synchronous threshold.

[REQUIRED] An asynchronous operation is one whose result is not returned in the initiating response; any operation that cannot reliably complete within the synchronous response threshold — 10 seconds at the 99th percentile — shall be designed as one. All validation and authorization run synchronously in the initiating request — work that will predictably fail is never accepted. *Rationale:* A fixed threshold, set safely below every gateway and client timeout, keeps the sync-versus-async choice deliberate and reviewable; rejecting doomed work up front spares consumers polling toward a guaranteed failure.

### 14.3 Asynchronous operations — initiation: return 202 Accepted and track progress on the resource itself.

[REQUIRED] Initiation returns 202 Accepted (§12.4) with the resource representation carrying its status; the resource being operated on is the tracking object. An explicit job resource is defined only when the operation has no natural resource (e.g. bulk import, recomputation), and then follows all normal resource conventions. *Rationale:* Tracking on the natural resource avoids a parallel job catalog for every operation.

### 14.4 Asynchronous operations — status: use the standard vocabulary on job resources.

[REQUIRED] Where an explicit job resource tracks the operation (§14.3), its status is a closed vocabulary — PENDING, RUNNING, SUCCEEDED, FAILED, CANCELED (§16.4) — with created, started, and finished timestamps (§16.3); a FAILED status carries the standard error body (§12.17), and the GET reading it returns 200. Processing progress shall never be encoded in a resource's business state machine (§7.10): where the resource itself is the tracking object, in-flight processing is signaled by Retry-After on its GET responses (§14.5). *Rationale:* A resource's state is a business construct; processing is not, so it travels as metadata rather than distorting the domain model.

### 14.5 Asynchronous operations — polling: make all produced state retrievable by GET at any time.

[REQUIRED] All asynchronously produced state shall be retrievable via standard GET at any time; queryable state is the source of truth and the universal floor — every consumer, first-party or external, can always poll. While an operation is in flight, the GET returns the full current representation with Retry-After (§10.13): the header's presence signals the representation is current but non-final, its value is the polling hint, and such responses cap their cache lifetime accordingly — Cache-Control: no-store or a max-age no longer than the hint (§17.2). The contract declares how long completed operation state remains retrievable and what is returned after expiry. *Rationale:* A queryable floor stays correct for every consumer regardless of how notifications behave, and the pending signal rides a header so processing never leaks into the business representation.

### 14.6 Asynchronous operations — completion: publish a thin event for every terminal transition.

[REQUIRED] Every terminal status transition shall publish a completion event to the platform notification service (§20), carrying only the resource identifier and new status; consumers fetch the representation. Notification is an accelerator over the queryable floor (§14.5), never a substitute: consumers reconcile by query on connect, reconnect, or delivery gap. *Rationale:* Thin events avoid duplicating representations in flight, and the queryable floor keeps correctness independent of delivery.

### 14.7 Offer batch operations through the shared batch idiom.

**⚠ Requires further editing:** the batch idiom below needs more elaboration before adoption; excluded from v1.0.

[OPTIONAL] A batch operation may be offered when a routine consumer workflow applies the same operation to many items, making per-item calls prohibitively chatty. Where offered, the batch shall follow the shared idiom: a POST to the collection URL with batch as the final path segment; a request body carrying an items array, bounded by a contract-declared maximum batch size and rejected with 400 above it; non-transactional execution returning 200 with a per-item items array positionally aligned to the request, each entry carrying its own status code and, on failure, the standard error body (§12.17); and the asynchronous operation pattern (§14.2) when the batch cannot complete within the synchronous threshold. *Rationale:* One shared idiom keeps batch bounds, partial-failure behavior, and result alignment identical everywhere, so consumers learn it once. *Example:* `POST https://api.example.com/v1/orders/batch`

## 15. Collections

### 15.1 Return a JSON object, never a bare array, from a collection GET.

[REQUIRED] A GET on a collection resource shall return a JSON object — never a top-level array — whose items attribute carries the array of embedded resource representations, alongside the collection's _links (§19.4). *Rationale:* The envelope gives navigation links, and any future collection-level attribute, a home that a bare array can never gain without a breaking change. *Example:*

```json
{
  "_links": {
    "self": { "href": "https://api.example.com/v1/orders?page=2&pageSize=25" },
    "next": { "href": "https://api.example.com/v1/orders?page=3&pageSize=25" }
  },
  "items": [
    {
      "orderId": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
      "state": "OPEN",
      "_links": { "self": { "href": "https://api.example.com/v1/orders/7c9e6679-7425-40de-944b-e07fc1f90ae7" } }
    }
  ]
}
```

### 15.2 Paginate collections with page and pageSize.

[REQUIRED] All APIs shall support pagination via page and pageSize, where page 1 is the first page. *Rationale:* One pagination idiom across the catalog means clients write paging logic once. *Example:* `page=1&pageSize=25` returns the first 25 elements.

### 15.3 Specify the maximum page size in the API contract.

[REQUIRED] Every API contract shall specify its maximum page size; requests above the maximum are capped at it, and requests exceeding the available elements return all remaining elements. *Rationale:* A declared, enforced maximum protects the service from unbounded result sets while giving each resource sensible tuning.

### 15.4 Return the element count on every collection response.

[REQUIRED] Whenever a collection is returned, the Example-Result-Set-Count header shall be set to the element count. *Rationale:* Clients can render totals and plan paging without a separate count call.

### 15.5 Accept complex queries through the q OData parameter.

[RECOMMENDED] Complex queries are expressed via q using OData $filter syntax, restricted to the inexpensive subset defined by the grammar below and applied only to the query parameters the API already exposes for individual pass-in. q shall not be combined with domain query parameters (those qualifying the resource, e.g. name), though system parameters like page/pageSize and sort may accompany it. *Rationale:* The subset keeps every predicate index-friendly and cheap to evaluate while retaining the grouping and cross-field OR that individual parameters cannot express.

Expressions are bounded in three ways. Nesting shall not exceed 3 levels of parenthesized grouping, keeping expressions readable and evaluation predictable. An expression shall contain at most 10 predicates, capping the total work a single query can demand. An in-list shall contain at most 20 values, keeping membership tests cheap. An expression exceeding any of these bounds, or referencing any other field, is rejected with 400.

```
<query>      := <predicate> { ("and" | "or") <predicate> }
<predicate>  := <comparison> | "not" <predicate> | "(" <query> ")"
<comparison> := <field> <operator> <value>
              | <field> ("eq" | "ne") null
              | <field> "in" "(" <value> { "," <value> } ")"
              | "startswith" "(" <field> "," <string> ")"
<operator>   := "eq" | "ne" | "gt" | "ge" | "lt" | "le"
<field>      := a query parameter the API exposes for individual pass-in
<value>      := <string> | <number> | <date-time>   (dates per ISO 8601, §16.3)
```

*Examples:*

| Query | Meaning |
|---|---|
| `?q=status eq 'OPEN'` | Equality on one field |
| `?q=age ge 21 and age lt 65` | Range via comparisons |
| `?q=status in ('OPEN','PENDING')` | Membership in a bounded list |
| `?q=location eq 'Petaluma' and (age lt 30 or status eq 'OPEN')` | Cross-field OR with grouping |
| `?q=startswith(lastName, 'Fon') and closedDate eq null` | Prefix match and null check |

### 15.6 Order results through the sort parameter.

[RECOMMENDED] Ordering is expressed via sort with syntax `[-]FieldName{"|"[-]FieldName}`, where each field shall be a query parameter the API exposes for individual pass-in (the same field set available to q, §15.5), a leading `-` means descending, and left-to-right order sets precedence. *Rationale:* A compact, uniform sort grammar covers multi-key ordering without bespoke parameters. *Example:* `?sort=-age|lastName` orders by age descending, then last name ascending.


## 16. Data Formats & Types

### 16.1 Represent all textual payloads as JSON.

[REQUIRED] All textual request and response representations shall use application/json (§4.2); binary content is outside this rule. *Rationale:* One representation format keeps client and server serialization simple and universally supported.

### 16.2 Encode all text as UTF-8.

[REQUIRED] All textual representations use UTF-8 encoding; binary content is outside this rule. *Rationale:* A single encoding eliminates mojibake and charset-negotiation failures.

### 16.3 Format dates and times as ISO 8601.

[REQUIRED] Dates and timestamps shall be ISO 8601 / RFC 3339 strings, and timestamps shall carry an explicit UTC offset (Z for UTC). *Rationale:* An unambiguous, sortable, timezone-explicit format prevents the most common data-interchange defects. *Example:* `2026-07-15T09:30:00Z`

### 16.4 Represent numbers, booleans, and enumerations consistently.

[REQUIRED] 32-bit integers and floating-point values shall be JSON numbers. 64-bit integers shall be strings, regardless of magnitude. Exact decimal values shall be strings. Booleans shall be JSON true/false (never "true"/0/1). Enumerations shall be documented UPPER_SNAKE_CASE string tokens, and shall never include a catch-all value such as OTHER — absence means undeclared (§16.6), and a genuinely new case gets a new documented token, which is a compatible change (§6.3). *Rationale:* Consistent scalar conventions prevent precision loss and brittle truthiness checks. *Example:* `"count": 42, "enabled": true, "status": "IN_PROGRESS"`

### 16.5 Represent money as a structured value, never a bare number.

[REQUIRED] Monetary amounts shall be represented as an object with currencyCode (ISO 4217, §16.8), units (whole currency units, a 64-bit integer carried as a string per §16.4), and nanos (nano-units as a 32-bit integer number, between -999,999,999 and +999,999,999, carrying the same sign as units). *Rationale:* A structured amount makes the currency explicit and keeps arithmetic exact, eliminating both float rounding and ambiguous unit conventions. *Example:* `"price": { "currencyCode": "USD", "units": "7", "nanos": 650000000 }` represents US$7.65

### 16.6 Give absent and null identical semantics.

[REQUIRED] An absent field and a null field carry the same meaning: the field has no value. A field with no value shall be omitted rather than sent as null, and a received null shall be interpreted as the field having no value. The one exception is a PATCH request body (§9.2), where an absent field means "leave unchanged" and a null field explicitly clears the value. *Rationale:* One universal equivalence removes the per-field, case-by-case interpretation that distinct absent and null semantics force on every consumer, while the PATCH exception preserves partial updates.

### 16.7 Format identifiers as UUIDs.

[REQUIRED] Resource instance identifiers shall be UUIDs (RFC 4122), represented as canonical lowercase strings. *Rationale:* Opaque UUIDs decouple identity from any internal sequence or storage scheme. *Example:* `"customerId": "7c9e6679-7425-40de-944b-e07fc1f90ae7"`

### 16.8 Use the designated standard codes for currency, country, and language.

[REQUIRED] Use ISO 4217 for currency, ISO 3166-1 alpha-2 for country, and BCP 47 for language tags. *Rationale:* Standard code sets make cross-API and cross-system data directly comparable. *Example:* `"currency": "USD", "country": "US", "language": "en-US"`

## 17. Caching & Optimistic Concurrency

### 17.1 Declare cacheability explicitly on every response.

[REQUIRED] Every response shall carry a Cache-Control header; no response may be silent on cacheability. *Rationale:* In the absence of explicit directives, intermediaries apply heuristic caching — silence does not mean "not cached," it means "cached unpredictably."

### 17.2 Set freshness directives where caching is acceptable.

[REQUIRED] Cacheable responses shall set Cache-Control with an explicit max-age and a public or private scope directive; private shall be used for any representation that varies by consumer. Expires and Last-Modified may be included for legacy compatibility but shall not substitute for Cache-Control. Origin services shall not set Age (it is an intermediary-cache header). *Rationale:* Explicit freshness and scope metadata let clients and shared caches (gateways, CDNs) cache safely; Cache-Control is the authoritative HTTP/1.1+ mechanism and overrides Expires.

### 17.3 Prohibit caching of sensitive representations.

[REQUIRED] Responses containing PII, credentials, tokens, or other data classified as sensitive under §13 shall set Cache-Control: no-store, and error responses shall set Cache-Control: no-store. *Rationale:* Explicit suppression is the only reliable protection against sensitive data persisting in shared or client caches.

### 17.4 Declare representation variance with Vary.

[REQUIRED] When any request header influences the representation returned for a URL — including Accept or Accept-Encoding — the response shall declare that header in Vary. *Rationale:* Without accurate Vary, caches serve one consumer's representation to another, producing wrong-language, wrong-format, or wrong-version responses.

### 17.5 Provide ETags on cacheable and concurrency-sensitive resources.

[REQUIRED] Cacheable resource representations, and any resource supporting conditional writes (§17.7), shall carry an ETag; ETags used for concurrency shall be strong validators. *Rationale:* The ETag is the validator underpinning both conditional retrieval (§17.6) and optimistic concurrency (§17.7); weak validators are not valid for If-Match preconditions.

### 17.6 Support conditional retrieval with 304.

[REQUIRED] APIs shall honor If-None-Match on GET and HEAD, returning 304 Not Modified when the representation is unchanged; a 304 response shall carry the same ETag, Cache-Control, and Vary values as the equivalent 200 response, and no body. Where Last-Modified is provided, If-Modified-Since should likewise be honored. *Rationale:* Validation avoids retransmitting unchanged representations, saving bandwidth and latency; incomplete 304 headers corrupt downstream cache state.

### 17.7 Enforce optimistic concurrency with If-Match.

[REQUIRED] Writes that must not clobber concurrent updates shall require an If-Match precondition carrying the resource's current ETag. A stale or missing precondition yields 412 Precondition Failed with the standard error body (§12); the client remedy is to re-GET the resource and retry with the fresh ETag. 412 is distinct from 409 Conflict, which is reserved for business-state conflicts (e.g. an invalid state transition). *Rationale:* Optimistic concurrency prevents lost updates without server-side locking; preserving the 412/409 distinction lets clients automate the refetch-and-retry loop. **⚠ Open decision:** 412 must be admitted to the approved status set in §12 (304 is already approved, §12.6).

### 17.8 Invalidate platform-controlled caches on write.

[RECOMMENDED] A successful PATCH, POST, or DELETE affecting a resource should invalidate that resource's cached representations in gateway and CDN caches under platform control. *Rationale:* Client caches cannot be invalidated remotely — max-age values shall therefore reflect genuine staleness tolerance — but platform-controlled caches can and should serve fresh state after writes.

### 17.9 Confine cacheability to GET and HEAD.

[REQUIRED] Only responses to GET and HEAD are cacheable. Function API responses (§4.14) are served via POST and are therefore not cacheable, notwithstanding their side-effect-free semantics; this is an accepted trade-off of the POST-only rule. *Rationale:* Confining caching to safe methods keeps cache correctness independent of application semantics.


## 18. Resource Expansion

### 18.1 Optionally expand referenced top-level resources, one level deep, on GET only.

[OPTIONAL] An API may support resource expansion, on GET operations only, for the top-level resource IDs carried within a resource — and that single level is the only expansion supported. The resource IDs to expand are those named in the expand query parameter (§11.2); all expansions are returned in an extra attribute added to the response — a top-level _resourceExpansions JSON object, where each attribute name is the resource ID name and its value is the expanded resource; the resource representation itself is unchanged. Requests naming an unsupported expansion are rejected with 400. *Rationale:* One-level expansion collapses N+1 request patterns into a single call while keeping payload size and evaluation cost strictly bounded. *Example:* `?expand=customerId` returns `"_resourceExpansions": { "customerId": { ...the customer resource... } }`

### 18.2 Keep expanded representations identical to their canonical form.

[REQUIRED] (where expansion is offered) An expanded resource shall be represented exactly as a direct GET of that resource's own URL (§8.6) would return it, at the same version. *Rationale:* One schema per resource, however it arrives, keeps client parsing single-pathed.

## 19. HATEOAS Links

### 19.1 Include hypermedia links in a _links object, each link an object.

[RECOMMENDED] Resource representations should carry a top-level _links JSON object relating the resource to itself, its associated resources, and the legal next actions: each attribute name is a relation name (§19.3), and each value is an object carrying at minimum href — an absolute URL requiring no client-side interpolation — plus the HTTP method where it is not GET. A link value shall always be an object, never a bare string. *Rationale:* Links make relationships and permitted transitions discoverable from the representation itself, and the object shape can later gain title, type, or deprecation metadata without the breaking change (§6.3) that a bare string would force. *Example:* `"_links": { "self": { "href": "https://api.example.com/v1/orders/7c9e6679-7425-40de-944b-e07fc1f90ae7" }, "cancel": { "href": "https://api.example.com/v1/orders/7c9e6679-7425-40de-944b-e07fc1f90ae7/cancel", "method": "POST" } }`

### 19.2 Always include a self link, including on embedded items.

[REQUIRED] (where links are provided) Every representation shall include a self relation identifying the resource's canonical URL — including each embedded item in a collection. *Rationale:* A canonical self-reference keeps identity unambiguous whether a resource is fetched directly, embedded, or expanded.

### 19.3 Draw relation names from the standard vocabulary defined here.

[REQUIRED] (where links are provided) Relation names shall come from this vocabulary: the IANA-registered relations below where they apply, and organization-vocabulary names for business relations (e.g. cancel, approve), governed with the same registry discipline as custom headers (§10.2). *Rationale:* Shared relation names are what allow a generic client to interpret links across the whole API ecosystem.

| Relation | Meaning |
|---|---|
| `self` | The canonical URL of this resource |
| `next` | The next page of a collection (§19.4) |
| `prev` | The previous page of a collection |
| `first` | The first page of a collection |
| `last` | The last page of a collection |

### 19.4 Provide navigation links on top-level collection GET responses.

[REQUIRED] Every GET response from a top-level resource collection shall carry first/prev/next/last links alongside the standard pagination parameters. For sub-resource collections, navigation links are optional — each API declares in its endpoint requirements whether its sub-resource collection GETs generate them (warranted when the collection is large enough to paginate). *Rationale:* Navigation links let clients page by following links instead of recomputing page numbers; small, bounded sub-resource collections are returned whole, where navigation links add size without value.

## 20. Event Publication

### 20.1 Publish a state-transition event on every state change.

[REQUIRED] Whenever a resource's state changes, the owning API shall publish an event to the platform bus communicating entry into the new state; creation counts as entry into the initial state and requires an event. *Rationale:* State-transition events let the rest of the platform react to lifecycle progress without polling the resource.

### 20.2 Treat state-transition events as the floor, not the ceiling.

[REQUIRED] State-transition events are the minimal required event set, not a ceiling: APIs shall additionally publish business events for other externally meaningful changes per the domain-event rule (§3.3). *Rationale:* Lifecycle entry alone does not capture every change other contexts need to react to.

## 21. Documentation

### 21.1 Describe every API in a machine-readable OpenAPI definition.

[REQUIRED] Each API shall publish a machine-readable OpenAPI (3.x) definition, kept in sync with the implementation, documenting every endpoint and operation the API offers — its parameters, request and response schemas, status codes, and headers. *Rationale:* A machine-readable contract covering the full surface powers client generation, mock servers, and automated conformance checks (§2.1); an undocumented endpoint is invisible to all of them.

### 21.2 Model every top-level resource as a standalone schema referenced by the contract.

[REQUIRED] Every top-level resource shall be modeled as its own standalone JSON Schema file, and
the OpenAPI definition shall reference those files rather than redefining the resource inline.
*Rationale:* One schema file per resource gives the model a single authoritative definition that
every contract references instead of copies.

### 21.3 Scope each OpenAPI specification to a single service.

[REQUIRED] An OpenAPI specification shall contain only the APIs of a single service.
*Rationale:* One contract per service keeps ownership, versioning, and review boundaries aligned
with the unit that ships.

### 21.4 Publish release notes for every version.

[REQUIRED] Each version shall publish release notes, served from the release-notes metadata endpoint (§8.9). *Rationale:* Release notes are how consumers learn what changed and whether they must act.

## 22. Observability

### 22.1 Propagate the Request-Id across every request path.

[REQUIRED] Each request/response shall be associated with its unique Request-Id (§10.19), surfaced to consumers as the error supportId and carried through internal processing. *Rationale:* A per-request identifier carried end to end is what makes a single failing request traceable across services.

### 22.2 Preserve the conversational context carried by the Correlation-Id.

[REQUIRED] Logs and traces shall record the Correlation-Id (§10.18) whenever one is present, preserving the conversational context that ties a client's multiple discrete communications into one business workflow. *Rationale:* Workflow-level troubleshooting needs the whole conversation, not just the single request in hand.

### 22.3 Record the serving infrastructure internally, never in responses.

[REQUIRED] The serving container and routing path shall be recorded internally — in structured logs and traces keyed by the Request-Id (§22.1) — and never exposed in response headers. *Rationale:* Operators still locate the exact instance behind a fault, without leaking backend topology to clients.

### 22.4 Log and expose metrics for every API.

[RECOMMENDED] APIs should emit structured logs and operational metrics (traffic, error rates, latency) sufficient to monitor health and support the standard's adoption and impact metrics. *Rationale:* Without metrics, both operational health and the standard's own value are unmeasurable.

### 22.5 Expose a health endpoint for every API.

[REQUIRED] Every API shall expose a health endpoint at the reserved path segment health, reporting its own liveness and readiness: 200 when able to serve, 503 otherwise. The response body is exactly `{ "status": "UP" }` with 200 and `{ "status": "DOWN" }` with 503 — a single status attribute whose only values are UP and DOWN. The endpoint is probed internally, is exempt from authentication and rate limiting, and shall not be exposed through the public gateway. *Rationale:* Orchestrators and load balancers route and restart on the API's own verdict; a probe that needs credentials or rate budget cannot be trusted precisely when things are failing, and one fixed body shape keeps every prober trivial. *Example:* `GET .../health` returns 200 with `{ "status": "UP" }`

## References & Glossary

### Normative References

This standard depends on: RFC 2119 (requirement keywords), RFC 4122 (UUID), RFC 3339 / ISO 8601 (date-time), the HTTP specifications (RFC 7230–7235 / RFC 9110), RFC 9457 (Problem Details), RFC 6749 (OAuth 2), OData $filter (query syntax), ISO 4217 (currency), ISO 3166 (country), and BCP 47 (language tags). *Rationale:* Naming the normative basis keeps settled questions settled and points implementers to the authoritative source.

### Glossary

Key terms are defined here and used consistently throughout. *Rationale:* A shared glossary prevents the same word from carrying different meanings across sections.

| Term | Definition |
|---|---|
| API | A named, versioned, branded product: a logical grouping of resources offered to consumers through a subscription. |
| Service | A logical aggregate of related APIs, packaged, registered, and subscribed to as one product offering. |
| Resource | A coarse-grained business object, addressable by URL; every API operation is performed in the context of a resource, its corresponding business object. |
| Domain | An approved namespace that groups resources and sets development-ownership boundaries. |
| Bounded Context | A boundary within which a domain model and its ubiquitous language are consistent; each bounded context contains a set of domains. |
| Anti-Corruption Layer | A translation layer through which APIs in different bounded contexts interact, keeping one context's model from leaking into another's. |
| Guideline | A single requirement: a directive, its normative statement, rationale, obligation level, and examples. |
| Waiver | An explicit, documented, approved exception to a requirement. |

---

## Backlog — Statements to Reconcile

Statements displaced from their original guideline pending a proper home elsewhere in the standard.

- (from 1.3) APIs should be understandable within minutes, appropriately granular, well abstracted, consistent, documented, and discoverable.
- (from old 4.5) Resources shall be typed and assigned to their architectural layer — Business Resources in the Business Resource Layer, Core Resources in the Core Resource Layer.
- (from old 16.9) Internationalization of human-facing content (e.g. honoring Accept-Language) — likely an application-layer concern rather than an API-standard requirement; reconcile with the application/BFF standards.
- (from 1.4) Group related resources into cohesive APIs.
- (from 1.4) Limit the total number of APIs so the catalog stays small and discoverable.
- (from 1.4) Separate resources with sharply different evolution profiles, with cohesion generally taking precedence over evolvability.
