# Relational DB Design Standard

| Field | Value |
|---|---|
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-08-20 |

## Purpose

This standard exists so that every relational schema backing the organization's APIs is designed
the same way — one set of conventions for naming, keys, typing, constraints, and indexing that
keeps schemas readable, evolvable, and mechanically consistent with the API contracts above them.

## Scope

This standard applies to every relational schema owned by a service built on the platform
(PostgreSQL in practice), and to how services use the database at runtime. The API contract above
it is governed by the RESTful API Design Standard. Any requirement in this standard may be waived
only through an explicit, documented, approved waiver, recorded in the service's implementation
guidance.

---

## 1. Naming

### 1.1 Name tables as plural, snake_case nouns.

[REQUIRED] Table names shall be plural nouns in lowercase snake_case, named for the business
object they store — matching the resource the table backs. *Rationale:* One predictable mapping
from resource to table makes any schema navigable from its API contract alone. *Example:*
`people`, `purchase_orders`

### 1.2 Name columns as snake_case nouns, unabbreviated.

[REQUIRED] Column names shall be lowercase snake_case nouns, with abbreviations minimal and well
known. *Rationale:* A single casing convention and full words remove per-table decoding effort.
*Example:* `first_name`, `shipping_address_id`

### 1.3 Name join tables after both sides.

[REQUIRED] A many-to-many join table is named `<table a>_<table b>`, the two sides in
alphabetical order. *Rationale:* A fixed composition makes the relationship visible from the name
alone. *Example:* `people_teams`

### 1.4 Name constraints and indexes with typed prefixes.

[REQUIRED] Constraint and index names follow `<prefix>_<table>_<columns>`: `pk_` primary key,
`fk_` foreign key, `uq_` unique, `ck_` check, `ix_` index. *Rationale:* Typed, predictable names
make migration diffs and error messages self-explanatory. *Example:* `uq_people_email`

## 2. Keys and Identity

### 2.1 Use a UUID primary key named id.

[REQUIRED] Every table's primary key is `id uuid`, application-generated (UUIDv4); sequence
integers shall never be exposed as identity. *Rationale:* Opaque, globally unique keys match the
API standard's resource identifiers and never collide across environments or merges. *Example:*
`id uuid PRIMARY KEY`

### 2.2 Never use business data as the primary key.

[REQUIRED] Natural keys (emails, codes, account numbers) shall not be primary keys; their
uniqueness is enforced with unique constraints instead. *Rationale:* Business data changes;
identity must not.

### 2.3 Declare every relationship as a real foreign key.

[REQUIRED] A reference to another table is a `<singular table name>_id` column with a declared
foreign-key constraint; relationships enforced only in application code shall not exist.
*Rationale:* The database is the last line of defense for referential integrity — an undeclared
relationship is an integrity bug waiting for a code path that forgets it. *Example:*
`person_id uuid REFERENCES people (id)`

## 3. Data Types

### 3.1 Give every attribute a real typed column.

[REQUIRED] Every persisted attribute gets its own typed column; JSON/JSONB columns shall not be
used for application attributes. *Rationale:* Typed columns keep the schema fully expressible
as an ERD, constraints enforceable, and migrations meaningful diffs rather than no-ops around an
opaque blob.

[REQUIRED] One exception: a document defined by an external specification, read and written only as
a whole, may occupy a single JSON/JSONB column — a registered JSON Schema is the case this exists
for. It applies only where all three hold: the document's own specification defines its validity,
decomposing it into columns would encode that specification in DDL, and no query filters, sorts or
joins reach inside it. A payload *described* by such a document is not covered — those are
application attributes and take typed columns. *Rationale:* Normalizing a specification-defined
document reimplements its grammar as tables, which is more brittle than storing it whole. The
prohibition exists to stop attributes hiding in blobs, not to forbid documents that are genuinely
opaque to the database.

### 3.2 Store timestamps as timestamptz in UTC.

[REQUIRED] All timestamps are `timestamptz`, written in UTC by the application layer.
*Rationale:* One timezone-explicit type eliminates the entire class of naive-datetime defects.

### 3.3 Store exact decimals as NUMERIC, never binary floats.

[REQUIRED] Exact quantities use `numeric(p, s)`; `float`/`double precision` is reserved for
genuinely inexact measurements. *Rationale:* Binary floats cannot represent exact decimal values;
the wire contract's exactness guarantees must hold in storage too.

### 3.4 Store enumerations as UPPER_SNAKE_CASE text with a CHECK constraint.

[REQUIRED] Enumerated values are stored as text tokens matching the wire vocabulary, constrained
by a CHECK listing the permitted values; native database enum types shall not be used.
*Rationale:* Text-plus-CHECK keeps the vocabulary visible and cheap to evolve by migration, where
native enums make every vocabulary change a type surgery. *Example:*
`state varchar(30) NOT NULL CHECK (state IN ('OPEN', 'SHIPPED', 'CANCELED'))`

### 3.5 Bound text columns to the contract's limits.

[REQUIRED] Text columns declare the same length bounds the API contract declares for the fields
they back. *Rationale:* A bound enforced only at the API layer is one bypassed write away from
data the contract says cannot exist. *Example:* API `maxLength: 100` → `varchar(100)`

## 4. Common Columns

### 4.1 Carry created_at, updated_at, created_by_id, and updated_by_id on every table.

[REQUIRED] Every table carries `created_at` and `updated_at` (`timestamptz`, set by the
application layer, not triggers), backing the API metadata object's createdAt/lastUpdatedAt, and
`created_by_id` and `updated_by_id` — the user's UUID taken from the validated token (never client
input), mapping mechanically (§8.1) to the API's createdById/updatedById. `created_at` and
`created_by_id` are set once at creation and **never updated** — immutable provenance backing the
API's read-only createdById (RESTful API Design Standard §7.9, §13.7); `updated_at` and
`updated_by_id` are rewritten on every change. Full row-change history is a per-resource decision
recorded in the resource's implementation guidance, not a platform mandate. *Rationale:* Uniform
provenance columns cost nothing at design time and are unrecoverable if missing later; an immutable
creator column keeps "who made this" true for the life of the row even after the user leaves; full
history is adopted only where regulation or dispute risk justifies its write and storage cost.

### 4.2 Use soft delete only where required, via deleted_at.

[OPTIONAL] Hard delete is the default; where a resource's guidance requires soft delete, it is a
nullable `deleted_at timestamptz`, and every query excludes soft-deleted rows by default.
*Rationale:* Soft delete is a per-resource business decision with real query-discipline cost —
adopted deliberately, never by reflex.

### 4.3 Store the lifecycle state in a state column.

[REQUIRED] A resource with a lifecycle stores its current state in a `state` column per §3.4,
backing the API's reserved state attribute. *Rationale:* One reserved column per lifecycle
resource mirrors the wire contract exactly.

## 5. Normalization and Relationships

### 5.1 Normalize to third normal form by default.

[REQUIRED] Schemas are normalized to 3NF; any denormalization is an explicit, documented
exception justified by a measured access pattern. *Rationale:* Normalization by default keeps
one fact in one place; exceptions made deliberately stay maintainable.

### 5.2 Model many-to-many relationships with join tables.

[REQUIRED] Many-to-many relationships use a join table (§1.3) of the two foreign keys, with its
own composite uniqueness. *Rationale:* Array-of-IDs and delimited-string shortcuts defeat both
referential integrity and indexing.

### 5.3 Keep derived data out of the schema.

[RECOMMENDED] Computed values should be derived at read time rather than stored; a stored
derivation is a documented exception with a defined recomputation trigger. *Rationale:* Stored
derivations drift from their inputs the first time a write path forgets them.

## 6. Integrity

### 6.1 Enforce in the database everything it can express.

[REQUIRED] NOT NULL, uniqueness, foreign keys, and CHECK constraints shall be declared in the
schema wherever the rule is expressible there; application-layer validation complements database
constraints, never substitutes for them. *Rationale:* Application checks guard one code path —
constraints guard every path, including the ones not written yet.

### 6.2 Scope tenant-owned tables with the owning organization ID.

[REQUIRED] Tables holding tenant-owned data carry the owning organization's ID (`organization_id`,
mapping to the API's metadata organizationId, §7.9) as a foreign-keyed column, and every query is
constrained to the rows the platform authorization engine grants the caller — usually the caller's
organization, plus anything legitimately shared across organizations. `organization_id` is
assigned by the application at creation from the creating user's organization, **never from client
input, and is immutable thereafter** (RESTful API Design Standard §13.7): the organization owns the
row through the member who created it, but that ownership neither is client-settable nor follows
the user out of the organization. *Rationale:* The organization column is what authorization
decisions are applied against, so it must be trustworthy — server-stamped and immovable, not
something a caller can supply or a later edit can change to escape its tenant; the engine remains
the single authority on cross-organization access.

## 7. Indexing

### 7.1 Index every foreign key.

[REQUIRED] Every foreign-key column gets an index. *Rationale:* Unindexed foreign keys turn joins
and cascades into table scans — the single most common self-inflicted relational performance
fault.

### 7.2 Index the columns backing filterable and sortable API parameters.

[REQUIRED] Every column backing a query parameter the API exposes for filtering or sorting gets
an index supporting that access. *Rationale:* The API standard keeps its query grammar
index-friendly on the promise that the indexes exist.

### 7.3 Add no speculative indexes.

[RECOMMENDED] Beyond §7.1 and §7.2, an index should exist only for a demonstrated query pattern.
*Rationale:* Every index taxes every write; unused ones are pure cost.

## 8. API Alignment

### 8.1 Map wire camelCase to column snake_case mechanically.

[REQUIRED] Wire field names map to column names by case convention alone — camelCase to
snake_case with no renames, so the mapping is derivable in both directions. *Rationale:* A
mechanical mapping needs no lookup table and cannot drift. *Example:* `firstName` ↔ `first_name`

## 9. Resilience

### 9.1 Use a bounded connection pool, budgeted against the instance.

[REQUIRED] Every service uses a bounded connection pool; pool size and overflow are declared in
service configuration, and the sum across all services shall fit the environment's published
connection budget, which the platform maintains. The platform defaults are pool 2 + overflow 3
per service instance in non-production, and pool 5 + overflow 5 in production. *Rationale:*
Connections are the shared instance's scarcest resource; framework defaults exhaust a small
instance with two services, where budgeted declarations keep every addition accountable.

### 9.2 Set a 4-second statement timeout on every connection.

[REQUIRED] Every service sets a 4-second statement timeout on every connection; a declared,
documented query may override it, and any operation that cannot reliably complete within the API
standard's synchronous threshold is designed as an asynchronous operation instead. *Rationale:* Two attempts
fit inside the 10-second synchronous ceiling with margin, and an unbounded query stalls a pooled
connection every other request is waiting for.

### 9.3 Retry transient failures only, once.

[REQUIRED] Services retry deadlocks, serialization failures, and dropped connections once within
the request's time budget; constraint violations and data errors are never retried. *Rationale:*
Transient faults succeed on the second attempt; deterministic failures fail identically every
time, so retrying them only adds load.

### 9.4 Keep transactions short, at READ COMMITTED by default.

[REQUIRED] A service's transactions span only the database work itself — no external I/O (HTTP
calls, queue publishes, model invocations) while a transaction is open. The default isolation
level is READ COMMITTED; stricter isolation is adopted per declared operation where an invariant
requires it.
*Rationale:* Short transactions keep locks and pooled connections available, and per-operation
escalation pays the serialization-failure cost only where it buys correctness.

## 10. Observability

### 10.1 Consume the platform's database observability; build none per service.

[REQUIRED] The platform provides the database observability floor — instance metrics dashboards
(active connections against the budget, CPU, memory, IOPS, transaction rate) and
pg_stat_statements query statistics enabled on every database. Services build no database
observability of their own. *Rationale:* One platform-owned floor covers every service
identically, for the cost of an instance flag and shared dashboards.

### 10.2 Log query shape and duration, never parameter values.

[REQUIRED] Services log each query's shape (the parameterized statement), its duration, and the
Request-Id; bound parameter values shall never be logged. *Rationale:* Shape plus duration
answers every performance question a log can answer; parameter values would turn logs into an
unguarded copy of the database, PII included.

## 11. Security

### 11.1 Give each service its own runtime and migration users.

[REQUIRED] Each service owns two database identities, shared with no other service: one for
runtime and one for migrations. **Where the platform offers IAM database authentication, the
runtime identity shall be the service's own workload identity rather than a named password user** —
the service authenticates with a short-lived token it obtains itself, so no runtime database
password is created, stored, or rotated. Password users remain the form on a platform without IAM
database authentication, named `<service name>_app` and `<service name>_migrate` with the
snake_case service name unique across the shared instance. Either way the two identities stay
distinct. *Rationale:* Per-service identities keep one leak's blast radius to one service, and a
separate migration identity keeps schema-altering power out of runtime hands; binding the runtime
identity to the workload removes the credential entirely, which is strictly better than protecting
one — there is nothing to leak, and nothing to forget to rotate. *Example:*
`order_management_app`, `order_management_migrate`

### 11.2 Grant the runtime user DML only.

[REQUIRED] The service grants its runtime user SELECT, INSERT, UPDATE, and DELETE on its own
database and nothing else; all DDL — including pre-release schema creation — executes as the
migration user.
*Rationale:* A compromised runtime credential can damage data but cannot drop or reshape the
schema.

### 11.3 Give each service its own database on the shared instance.

[REQUIRED] Each service provisions its own database on the shared instance; schemas within a
shared database shall not be used as the isolation boundary. *Rationale:* A database is the
strongest boundary Postgres offers on shared infrastructure — no cross-service visibility,
per-database ownership and extensions, and clean per-service restore.

### 11.4 Take credentials from the platform secret manager, and connect over TLS.

[REQUIRED] Where a database credential exists, it comes only from the platform secret manager —
never environment files or repositories — and every connection to the database uses TLS. A runtime
using IAM database authentication (§11.1) has no credential to store: it presents a short-lived
token minted for its workload identity, and the connection is encrypted by the platform's own
connector. *Rationale:* Secrets live where rotation and audit exist, and transport encryption is
the baseline everything else assumes — but the strongest form of both is a credential that was
never issued.

## 12. Backup and Recovery

### 12.1 Rely on platform backups: daily, point-in-time recovery, 7-day retention.

[REQUIRED] The platform provides automated daily backups with point-in-time recovery enabled and
7-day retention on the shared instance — the required floor values, configurable upward per
platform instantiation. Services shall not hand-roll their own backup tooling. *Rationale:* One
tested platform mechanism beats one improvised job per service, and fixed floor values make
recovery a property of the platform rather than a per-team hope.

### 12.2 Declare recovery objectives and verify restore.

[REQUIRED] Each service declares its recovery point and recovery time objectives in its
implementation guidance; the platform executes a restore drill — before the service's first
production release and annually thereafter — and the service verifies its restored data.
*Rationale:* A backup that has never been restored is an assumption; declared objectives make
"good enough" checkable.

### 12.3 Back up before every production schema migration.

[REQUIRED] The platform's delivery pipeline takes a backup or snapshot immediately before
applying any schema migration in production. *Rationale:* The moment most likely to need recovery
is the moment the schema changes; an automatic snapshot turns a bad migration into a restore
instead of an incident.

## 13. Schema Migration

### 13.1 Use versioned migrations in staging and production only.

[REQUIRED] Staging and production schemas change only through versioned migrations. In every
other environment, a schema change may simply drop and recreate the database from the current
models — no migration is authored for non-production environments, and no effort is ever spent
migrating non-production data. *Rationale:* Non-production data is disposable by definition;
writing, rebasing, and running migrations against it has historically consumed significant
development time for zero production value.
