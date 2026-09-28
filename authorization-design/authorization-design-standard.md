---
shortName: AUTHZ
description: >-
  How access to a platform's APIs and experiences is designed: scopes sized to experiences, facts on
  subjects, people and machine accounts as one kind of subject, tenancy from the token, deny by
  default within an organization, where checks run, platform-level facts, and roles.
adoptionMetrics:
  - Share of services whose every read passes a scope gate and then one class-visibility check before the query
  - Share of services whose authorization requirements name a model relation for every endpoint
impactMetrics:
  - Count of records reachable by organization membership alone (target zero)
  - Median time for a new member to be granted their first class visibility, from invitation accepted
tags: [authorization, openfga, oauth, scopes, tenancy, roles]
softwareLifecycle: [REQUIREMENTS_ANALYSIS, ARCHITECTURE_AND_DESIGN, IMPLEMENTATION]
solutionScope: [IDENTITY_AND_ACCESS, SECURITY_CONTROLS, APIS_AND_INTEGRATIONS, USER_INTERFACES]
architectureQualities: [SECURITY, PRIVACY, USABILITY, MAINTAINABILITY]
industryReferences:
  - {title: "Zanzibar: Google's Consistent, Global Authorization System (2019)", url: "https://research.google/pubs/zanzibar-googles-consistent-global-authorization-system/"}
  - {title: "RFC 6749 — The OAuth 2.0 Authorization Framework", url: "https://www.rfc-editor.org/rfc/rfc6749"}
  - {title: "OpenFGA modeling guides", url: "https://openfga.dev/docs/modeling"}
supportingStandards: [APIDS-v1]
---

# Authorization Design Standard

| Field | Value |
|---|---|
| **Short Name** | AUTHZ |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-09-13 |

## Purpose

This standard governs how access to a platform's APIs and experiences is **designed**: what OAuth
scopes mean and how they are sized, what relationship facts mean and who may assert them, how the
two layers divide the work, who the subjects are (people and machines alike), and where a decision
is made. It is the companion of the [Authorization Tuple Management Standard](../authorization-tuple-management/authorization-tuple-management-standard.md),
which governs how facts are written once a design says what they are.

The principle it exists to hold: **a scope says which experience a caller is for; a fact says what
that caller may do to what, once inside it.** Designed together, a caller holding the right scope
has a good reason to see the experience and very likely has access to the data it renders; a caller
without it should not be looking at the screen. Designed apart, the scope model starts encoding the
permission model, drifts from it, and both stop meaning anything.

## Value Proposition

- **One rule for who sees what** — a scope says which experience a caller is for, a fact says what
  that caller may do to what; designed together they stay meaningful, designed apart the scope model
  drifts into a second permission model.
- **Closed by default inside an organization** — a hundred-person organization does not share
  everything with every member; visibility reaches a member through a role assigned deliberately.
- **People and machines authorized the same way** — a pipeline's account holds membership and facts
  exactly as a person's does, so no service special-cases it.
- **One model, spelled not invented** — types and relations are owned by the platform and loaded
  once; a service checks relations by name and never grows its own vocabulary.

## Scope

Applies to every API and user experience built on the platform, to the provisioning of every client
(human-facing or machine), and to the authorization model the platform loads. Does not cover token
verification mechanics or the write path of the relationship store.

Any requirement may be waived only through an explicit, documented, approved waiver recorded in the
product's implementation guidance.

---

## 1. Two Layers

### 1.1 Keep scopes on the client and facts on the subject.

[REQUIRED] A scope is a property of the **client**: whether this application may touch a class of
resource at all. A fact is a property of the **subject**: whether this person or machine may do
this to this object. Neither substitutes for the other.

*Rationale:* Scopes and facts are different questions, and a call passes both gates. Designed apart,
the scope model starts encoding the permission model, drifts from it, and both stop meaning anything.

### 1.2 Pass the scope gate first, then the fact check, on every request — reads included.

[REQUIRED] Every request passes the scope gate first, then the fact check — reads included: a
collection read is scope, then one check that the caller may see the class in this organization
(§5, §9), then the query. A missing scope is a provisioning error and answers 403; a missing fact
is an access decision and answers per §6.

*Rationale:* The two gates fail for different reasons and different people fix them: a client's
provisioning, or a subject's standing.

### 1.3 Draft placeholder: which questions belong to which layer.

[OPTIONAL] To be filled before this standard leaves Draft: which questions belong to which layer,
with the test: if the answer depends on *which* object, it is a fact.

*Rationale:* Placeholder for authored text.

## 2. Scope Design

### 2.1 Grant two scopes per top-level resource, per client, never per endpoint.

[REQUIRED] Two scopes per top-level resource, `<resource>:read` and `<resource>:write`, granted per
client and never per endpoint: an experience is "browse it" or "manage it". Anything finer is a
fact.

*Rationale:* Scopes coincide with experiences; an endpoint-level scope is a permission model
wearing a scope's name.

### 2.2 Grant a client only the scopes of the experiences it offers.

[REQUIRED] A client is granted the scopes of the experiences it offers, and only those. The user
interface keys the visibility of an experience off the same scopes (and the access API), so a
user is never shown an entry point to data the client cannot render.

*Rationale:* A caller without the scope should not be looking at the screen.

### 2.3 Draft placeholder: a screen for one party may deserve its own resource and scope pair.

[OPTIONAL] To be filled before this standard leaves Draft: when a screen exists for one party only
(platform administration, say), that is a sign it may deserve a resource — and therefore a scope
pair — of its own, rather than a special scope.

*Rationale:* Placeholder for authored text.

### 2.4 Draft placeholder: the audience scope, and why it grants nothing.

[OPTIONAL] To be filled before this standard leaves Draft: the audience scope, and why it grants
nothing.

*Rationale:* Placeholder for authored text.

## 3. Subjects and Principals

### 3.1 Model a machine account as a client-credentials client with its service-account user.

[REQUIRED] A machine account is a client-credentials client with its service-account user. The
client carries the credential and the scopes; the service-account user carries organization
membership and every fact, exactly as a person's user does. Services never special-case it.

*Rationale:* People and machines are the same kind of subject; only the credential differs.

### 3.2 Place every machine account in exactly one organization, administered like a person.

[REQUIRED] Machine accounts are members of exactly one organization, so their tenancy is
unambiguous, and are administered through the same organization administration as people.

*Rationale:* A subject with no organization has no tenancy, and a second administration surface is
a second place to get it wrong.

### 3.3 Draft placeholder: users are who a token is about; clients are what it is issued to.

[OPTIONAL] To be filled before this standard leaves Draft: users are who a token is about (`sub`);
clients are what it is issued to (`azp`). Together with which identities may write durable data
(an organization's own machine accounts) and which may not (probe and validation identities).

*Rationale:* Placeholder for authored text.

## 4. Tenancy and Ownership

### 4.1 Assign owning organization and creator from the authenticated identity, immutably.

[REQUIRED] A resource's owning organization and creator are assigned from the authenticated
identity at creation and are immutable (RESTful API Design Standard §13.7).

*Rationale:* Who owns a thing is read from the token, never from a payload.

### 4.2 Treat the platform organization as an ordinary organization.

[REQUIRED] The platform organization is an ordinary organization: it owns what the platform ships,
and is administered like any other. Nothing in a service knows it is special.

*Rationale:* A special case in every service is a rule nobody can keep; an ordinary organization
needs none.

### 4.3 Draft placeholder: what "the platform" as an object is, distinct from the platform organization.

[OPTIONAL] To be filled before this standard leaves Draft: what "the platform" as an object is,
distinct from the platform organization.

*Rationale:* Placeholder for authored text.

## 5. Deny by Default and Cross-Organization Access

### 5.1 Reveal nothing — not even existence — without a membership, role or direct relation.

[REQUIRED] Without a membership, role or direct relation, a subject learns nothing about an object,
its existence included.

*Rationale:* No fact means nothing — including that the thing exists; a 403 confirms an id.

### 5.2 Close by default within an organization.

[REQUIRED] Membership grants no visibility of the organization's data. A member sees a class of
data only through a role that carries that visibility, assigned deliberately; a new member sees
nothing until one is. A service therefore never answers a read from the token's organization
alone — the organization scopes the query, a fact decides whether the caller may see the class
(§6).

*Rationale:* An organization of a hundred people does not share everything with every member.

### 5.3 Never grant cross-organization access through membership in the other organization.

[REQUIRED] Cross-organization access is never membership in the other organization. It is a direct
relation on the specific object, or a platform-level grant (§7).

*Rationale:* Membership is belonging; a share is a fact about one thing.

### 5.4 Draft placeholder: publication.

[OPTIONAL] To be filled before this standard leaves Draft: publication — when registering a thing
is deciding to show it to everyone admitted, and how that is stated.

*Rationale:* Placeholder for authored text.

## 6. Where Checks Run

### 6.1 Check facts at request time, in the service that owns the resource.

[REQUIRED] Facts are checked at request time against the authorization store, in the service that
owns the resource. The token carries capability (scopes), not decisions. One check per request
when the visible set is the whole collection; per-object checks only where visibility differs per
row.

*Rationale:* The decision is live, in the service, never read off the token — a token cannot be
revoked before it expires.

### 6.2 Answer 403 when the caller may see the object but not do this; the resource's 404 when they may not see it.

[REQUIRED] The deny shape: 403 when the caller may see the object but not do this to it; the
resource's own 404 when the caller may not see it at all.

*Rationale:* The API answers identically for a thing that does not exist and one the caller may not
see.

### 6.3 Draft placeholder: where a backend-for-frontend may check on a service's behalf, and where it may not.

[OPTIONAL] To be filled before this standard leaves Draft: where a backend-for-frontend may check
on a service's behalf, and where it may not.

*Rationale:* Placeholder for authored text.

## 7. Platform-Level Facts

### 7.1 Place platform-level grants on the platform object, never on any organization.

[REQUIRED] Platform-level grants are placed on the platform object, not on any organization, so no
organization is affiliating the grantee and deny-by-default (§5) is undisturbed. These are the
facts only the platform asserts: an organization admitted, a developer admitted to read
interfaces, a feature enabled, an organization suspended.

*Rationale:* Some facts only the platform asserts, and placing them on an organization would make
its members' standing depend on the platform's.

### 7.2 Draft placeholder: who may assert platform-level facts, and through which experience.

[OPTIONAL] To be filled before this standard leaves Draft: who may assert them (platform owner and
administrators) and through which experience — the same organization administration, with the
platform's facts in addition.

*Rationale:* Placeholder for authored text.

## 8. Vocabulary and Mechanism

### 8.1 Own the authorization model once, at the platform; services spell relations, never invent them.

[REQUIRED] The authorization model — types and relations — is owned by the platform and loaded
once. A service checks relations the model defines and introduces object types through the
model, never ad hoc.

*Rationale:* Two vocabularies for the same fact cannot be reconciled; one model can be reviewed.

### 8.2 Keep mechanism in the shared SDK and vocabulary with the model's owner.

[REQUIRED] Mechanism (engine connection, the check dependency, the deny shape, tuple helpers) lives
in the shared SDK and knows no relation by name. Vocabulary (relation and type names, typed
helpers) lives with the product that owns the model, derived from it so the two cannot drift.
Policy — which relation an endpoint checks — is stated in the service's authorization
requirements and nowhere else.

*Rationale:* A helper that knows a relation by name is a second copy of the model.

## 9. Roles

### 9.1 Grant capability and visibility through roles, never through membership itself.

[REQUIRED] Capabilities and visibility are granted by roles assigned to users or groups, never
by membership itself. Which relations a role carries is stated in the model; which roles exist
is a product decision. Roles for machine accounts are the same roles, assigned to the
service-account user.

*Rationale:* Visibility and capability reach a member through roles; membership is only belonging.

### 9.2 Ship application roles; let organizations compose custom roles from the same relations.

[REQUIRED] The platform ships **application roles** — the ones an organization administrator
finds useful on day one (a viewer and a manager per product area, for instance) — and
organizations may define **custom roles** composed from the same relations.

*Rationale:* The platform ships some roles and organizations define more; composing them from the
same relations keeps one model.

### 9.3 Draft placeholder: what a new member holds before any role is assigned, and who may assign roles.

[OPTIONAL] To be filled before this standard leaves Draft: what a new member holds before any role
is assigned (nothing, or a product-defined base role), and who may assign roles (organization
administrators, through organization administration).

*Rationale:* Placeholder for authored text.

## Open questions

To settle before this leaves Draft.

- Whether platform administration needs any scope of its own, or is fully the organization-administration
  scopes plus platform-level facts (§2, §7).
- Whether machine accounts appear in organization administration as members of a distinct kind, or
  as members like any other (§3).
- How a product declares object types into the platform-owned model (§8).
- Whether the access API is the single source the UI reads for experience visibility, or scopes on
  the token suffice (§2).

## Status

- [ ] Filled out
- [ ] Reviewed
- [ ] Published
