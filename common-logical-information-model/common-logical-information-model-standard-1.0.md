---
shortName: CLIMS
description: >-
  How the business's shared information is defined once, independent of any technology — its
  business objects, their attributes, relationships and identity — and how service schemas map to it.
adoptionMetrics:
  - Share of top-level resource schemas mapped to a business object in the model
impactMetrics:
  - Count of business objects defined differently by two services (target zero)
tags: [information-model, logical-data-model, business-objects, semantics]
softwareLifecycle: [ARCHITECTURE_AND_DESIGN, MAINTAIN_AND_EVOLVE]
solutionScope: [DATA_AND_PERSISTENCE, APIS_AND_INTEGRATIONS]
architectureQualities: [INTEROPERABILITY, MAINTAINABILITY]
---
# Common Logical Information Model Standard

| Field | Value |
|---|---|
| **Short Name** | CLIMS |
| **Version** | 1.0 |
| **Status** | Draft |
| **Author** | Steven Fonseca |
| **Last Updated** | 2026-10-09 |

## Purpose

This standard governs the common logical information model: the single, technology-neutral
definition of the business objects the organization's services hold — what each is, its attributes,
how objects relate, and how each is identified — and how a service's resource schemas map to it.

## Value Proposition

- **One meaning per business object** — every service that holds an object means the same thing by
  it, so data moves between services without translation.
- **Schemas start from the business** — a service's resources are derived from the model rather than
  invented per service.

## Scope

Applies to every business object held by more than one service, or exchanged between services.

It does not govern how an object is stored or served: physical schemas and API resources follow
their own standards and map to this model.

## Status

**This is a holding place, not a finished standard.** Its sections name the parts of the model; the
guidelines under each are later work.

## 1. Business Objects

### 1.1 Define each shared business object once in the model.

[REQUIRED] A business object held or exchanged by more than one service shall be defined once in
the common logical information model, with a name and a definition in the business's own terms.
*Rationale:* Two definitions of one object diverge, and every exchange between them needs a
translation.

## 2. Attributes and Relationships

### 2.1 Give every attribute and relationship a definition.

[REQUIRED] Each attribute and each relationship of a business object shall be named and defined in
the model, independent of how any system stores it. *Rationale:* An attribute without a definition
is read differently by each service that holds it.

### 2.2 Carry declared, product-owned classification in `classifications`.

[REQUIRED] Where a business object is classified along one or more axes the product declares rather
than its users, the attribute shall be named `classifications` and shall be an array of objects,
each carrying a `name` — the axis — and a `value` — the position on it. *Rationale:* An object is
classified along more than one axis almost as soon as it is classified at all, and an array of
pairs admits a new axis as data, where an attribute per axis admits one only as a schema change.
A `name` shall appear at most once: an object holds one position on each axis, and a classification
that genuinely takes several values is a different attribute, not a repeated name. *Rationale for
the single value:* a list grouped by an axis needs exactly one bucket per object, and a repeated
name leaves the renderer to show the object twice or pick one arbitrarily — neither of which any
contract states. *Example:*

```json
"classifications": [
  { "name": "area", "value": "library" },
  { "name": "sensitivity", "value": "privileged" }
]
```

### 2.3 Draw every classification name for a resource from an enumeration that resource declares.

[REQUIRED] For a given resource, the permitted `name` values shall be declared as an enumeration in
that resource's schema, and a classification naming an axis outside it shall be refused on write.
The enumeration is per resource — two resources may classify along different axes — and an axis
they share shall use the same name. *Rationale:* Without a declared set the axis is a free string,
and one misspelling silently creates an axis that a screen then groups by, with nothing anywhere to
show for it. Fixing the names while leaving the values open is what lets the vocabulary grow
without the structure moving.

### 2.4 Do not name a consumer-authored label and a declared classification alike.

[REQUIRED] An attribute written by the people using the product, for their own retrieval, on which
nothing is enforced, shall not share a name with one the product declares and a screen, report or
authorization decision depends on. The open case is `tags`, an array of strings, presentation only;
the declared case is `classifications` (§2.2). Neither substitutes for the other. *Rationale:* The
two carry opposite guarantees — one may hold anything and may be absent, the other is a contract —
and under one name a consumer treats whichever it met first as the rule, then builds on it.

## 3. Identity

### 3.1 Name how each business object is identified.

[REQUIRED] The model shall state how each business object is identified across services.
*Rationale:* Objects that cannot be matched across services cannot be integrated.

## 4. Mapping

### 4.1 Map each resource schema to the business object it represents.

[RECOMMENDED] A service's top-level resource schema should name the business object in the model it
represents. *Rationale:* The mapping is what lets a reader find every service holding an object.
