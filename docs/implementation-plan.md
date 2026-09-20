# Dragonfly Engineering Standards — Implementation Plan

> The standards themselves are indexed in [`STANDARDS.md`](../STANDARDS.md), which is the source of
> truth for what is Published. This plan tracks what is being authored and what is planned.
> Status: ☐ not started · ◐ in progress · ☑ done.

## How a standard completes

1. **Draft** — authored under its own directory as `<name>/<name>-standard.md`, header table
   carrying version and `Draft`, and a row in `STANDARDS.md`. Not built against.
2. **Agreed and being built** — each guideline moves into the Published version only when it is
   agreed *and* something is building to it. A guideline nobody is building to stays Draft.
3. **Published** — header and index both say so; exactly one version of a standard is Published at
   a time. Compliance is measured against it alone.
4. **Cited** — the resources and schemas that depend on it name it by version, so the dependency is
   a citation rather than an assumption.

## Standards

### Published

- ☑ **RESTful API Design Standard for Enterprise Reuse v1.0** — `rest-api-design/`

### In draft

- ◐ **RESTful API Design Standard v1.1** — `rest-api-design/`. v1.0 plus guidelines agreed for later
  (shared batch idiom §14.7). Publishes when those are being built.
- ◐ **Relational DB Design Standard** — `relational-db-design/`. Being built against by the EA
  Guidance and Risk and Compliance services; publish once the first service's schema review is
  complete.
- ◐ **Web Asset Delivery Standard** — `web-asset-delivery/`. Built against by the Architect web
  app's deploy.
- ◐ **Authorization Tuple Management Standard** — `authorization-tuple-management/`.
- ◐ **Authorization Design Standard** — `authorization-design/`. Skeleton; roles and
  closed-by-default agreed, the rest under elaboration.

### Planned

- ☐ **FMEA Rating Rubric Standard** — `fmea-rating-rubric/fmea-rating-rubric-standard.md`. The
  rubric a failure modes and effects analysis is rated under: the ten-point anchor tables for
  severity, occurrence and detection, aligned to AIAG-VDA, and action priority with severity
  dominating in place of a risk priority number, which is not to be computed or stored. Specific to
  FMEA — each kind of analysis defines its own rubric, and this one is not shared with any other.
  Once Published, cited from `failure-modes-effects-analysis-schema.json` (`severity`) in place of
  the convention that description currently assumes.
