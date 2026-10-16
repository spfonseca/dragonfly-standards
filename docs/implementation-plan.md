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
- ◐ **FMEA Rating Rubric Standard** — `fmea-rating-rubric/`. Written to the implementation: the
  three ten-point tables the EA Guidance service serves as `/v1/fmea-analysis/rubrics`, severity
  dominating with no RPN, re-rating after actions taken. Built against by the FMEA library and
  worksheet. Once Published, cited from `failure-modes-effects-analysis-schema.json`.

### Planned

- none

## Tooling

- ☑ **Publish standards to the platform's content bucket** — `scripts/publish-to-content.py`, run by
  hand for now. Converts the listed standards, drafts included, into the `standards` resource shape
  and writes them to the bucket the platform's initialization reads.

## Backlog

- **Publish from CI rather than by hand**, authenticating through workload identity federation.
- **Review the owned-record resource pattern, and move what is standard-setting out of it.**
  `dragonfly-app-platform-svs-kit/rest-microsvs-python-shareddb/owned-record-resource-pattern.md` was
  written by AI and has never been reviewed. It says of itself that it "adds no rule" to the API
  standard or the authorization pattern and only fixes choices they leave open. Most of it does
  exactly that. Some of it does not: it states general rules that hold for any resource, which
  makes a pattern into a standard by the back door — a rule read only by services that happen to
  call themselves owned records.

  The candidates for promotion, as a starting hypothesis rather than a conclusion:

  | In the pattern today | Belongs in |
  |---|---|
  | A list whose authorization answer may be incomplete is `503` with `Retry-After`, never a short page | RESTful API Design Standard, or Authorization Design |
  | The race outcomes — PATCH after PATCH is `412`, PATCH or DELETE after DELETE is `404`, never `412` | RESTful API Design Standard |
  | Authorization tuples are written after the row commits, so a failed insert leaves no grant | Authorization Tuple Management Standard |
  | A write's check is sent `HIGHER_CONSISTENCY`; a read's may lag the cache TTL | Authorization Design Standard |

  A fifth is a different failure: the pattern's create rule reads "any member, **never a guest**",
  which assumes a guest exists as a distinct principal and that a resource pattern is where to say
  so. Whether guests are a kind of principal at all — as against a user who acts in their own
  organization and simply reaches fewer artifacts — is the Authorization Design Standard's
  question. Found 2026-10-15 while writing `ai-chat-conversations`, where the rider described
  nothing: a conversation is created empty and belongs to whoever started it.

  Genuine instantiation, and staying: the page-size cap, `q` left out, no `Idempotency-Key` on
  create, DELETE taking no `If-Match`, the default sort, and three roles per resource.

  **Why it matters now.** The pattern is already load-bearing — the SDK implements it as
  `dragonfly_service_sdk.owned_record`, the microservice pattern's `CLAUDE.md` instructs builds to
  follow it, and `ai-chat-conversations` inherits eleven decisions from it by citation. Services
  are accepting unreviewed rules one requirements document at a time. Until the review lands, a
  requirements document citing it should say the pattern is not reviewed and list what it is
  accepting, as that one now does.
