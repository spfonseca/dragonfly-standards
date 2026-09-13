# Authorization Design Standard

| Field | Value |
|---|---|
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

## Scope

Applies to every API and user experience built on the platform, to the provisioning of every client
(human-facing or machine), and to the authorization model the platform loads. Does not cover token
verification mechanics or the write path of the relationship store.

Any requirement may be waived only through an explicit, documented, approved waiver recorded in the
product's implementation guidance.

---

## 1. Two Layers

> Scopes and facts are different questions, and a call passes both gates.

- [REQUIRED] A scope is a property of the **client**: whether this application may touch a class of
  resource at all. A fact is a property of the **subject**: whether this person or machine may do
  this to this object. Neither substitutes for the other.
- [REQUIRED] Every request passes the scope gate first, then the fact check. A missing scope is a
  provisioning error and answers 403; a missing fact is an access decision and answers per §6.
- Which questions belong to which layer, with the test: if the answer depends on *which* object,
  it is a fact.

## 2. Scope Design

> Scopes coincide with experiences.

- [REQUIRED] Two scopes per top-level resource, `<resource>:read` and `<resource>:write`, granted per
  client and never per endpoint: an experience is "browse it" or "manage it". Anything finer is a
  fact.
- [REQUIRED] A client is granted the scopes of the experiences it offers, and only those. The user
  interface keys the visibility of an experience off the same scopes (and the access API), so a
  user is never shown an entry point to data the client cannot render.
- When a screen exists for one party only (platform administration, say), that is a sign it may
  deserve a resource — and therefore a scope pair — of its own, rather than a special scope.
- The audience scope, and why it grants nothing.

## 3. Subjects and Principals

> People and machines are the same kind of subject; only the credential differs.

- Users are who a token is about (`sub`); clients are what it is issued to (`azp`).
- [REQUIRED] A machine account is a client-credentials client with its service-account user. The
  client carries the credential and the scopes; the service-account user carries organization
  membership and every fact, exactly as a person's user does. Services never special-case it.
- [REQUIRED] Machine accounts are members of exactly one organization, so their tenancy is
  unambiguous, and are administered through the same organization administration as people.
- Which identities may write durable data (an organization's own machine accounts) and which may
  not (probe and validation identities).

## 4. Tenancy and Ownership

> Who owns a thing is read from the token, never from a payload.

- [REQUIRED] A resource's owning organization and creator are assigned from the authenticated
  identity at creation and are immutable (RESTful API Design Standard §13.7).
- [REQUIRED] The platform organization is an ordinary organization: it owns what the platform ships,
  and is administered like any other. Nothing in a service knows it is special.
- What "the platform" as an object is, distinct from the platform organization.

## 5. Deny by Default and Cross-Organization Access

> No fact means nothing — including that the thing exists.

- [REQUIRED] Without a membership, role or direct relation, a subject learns nothing about an object,
  its existence included.
- [REQUIRED] Cross-organization access is never membership in the other organization. It is a direct
  relation on the specific object, or a platform-level grant (§7).
- Publication: when registering a thing is deciding to show it to everyone admitted, and how that is
  stated.

## 6. Where Checks Run

> The decision is live, in the service, never read off the token.

- [REQUIRED] Facts are checked at request time against the authorization store, in the service that
  owns the resource. The token carries capability (scopes), not decisions.
- One check per request when the visible set is the whole collection; per-object checks only where
  visibility differs per row.
- [REQUIRED] The deny shape: 403 when the caller may see the object but not do this to it; the
  resource's own 404 when the caller may not see it at all.
- Where a backend-for-frontend may check on a service's behalf, and where it may not.

## 7. Platform-Level Facts

> Some facts only the platform asserts.

- Which facts these are: an organization admitted, a developer admitted to read interfaces, a
  feature enabled, an organization suspended.
- [REQUIRED] Platform-level grants are placed on the platform object, not on any organization, so no
  organization is affiliating the grantee and deny-by-default (§5) is undisturbed.
- Who may assert them (platform owner and administrators) and through which experience — the same
  organization administration, with the platform's facts in addition.

## 8. Vocabulary and Mechanism

> The model is owned once; services spell relations, never invent them.

- [REQUIRED] The authorization model — types and relations — is owned by the platform and loaded
  once. A service checks relations the model defines and introduces object types through the
  model, never ad hoc.
- [REQUIRED] Mechanism (engine connection, the check dependency, the deny shape, tuple helpers) lives
  in the shared SDK and knows no relation by name. Vocabulary (relation and type names, typed
  helpers) lives with the product that owns the model, derived from it so the two cannot drift.
- Policy — which relation an endpoint checks — is stated in the service's authorization
  requirements and nowhere else.

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
