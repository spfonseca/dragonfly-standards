# Dragonfly Standards

A curated set of standards intended to **guide application development** across
the organization. These standards give teams a shared, consistent foundation to
design and build against — used as guidance while designing, as the criteria
applied during reviews, and as the source of standardized implementation
practices.

## What's Here

This repository collects standards in several complementary formats:

- **Markdown files** (`.md`) — the human-readable standards themselves:
  narrative guidance, requirements, and rationale. Requirements use "shall"
  (mandatory) and "should" (recommended).
- **JSON files** (`.json`) — machine-readable definitions such as schemas,
  configuration, and structured rules that tooling can consume and enforce.
- **Agent files** — instructions and context intended for AI coding agents, so
  automated assistants apply these standards consistently when helping build
  applications.

## Structure

Standards are organized into topic-focused directories. Each directory holds the
documents for one area.

| Directory | Description |
| --- | --- |
| [`rest-api-design/`](./rest-api-design/) | Design and implementation requirements for RESTful APIs. |

*(More standards will be added over time.)*

## How to Use These Standards

- **When designing** — consult the relevant standard early; full adherence is
  the default.
- **During review** — designs are assessed against these standards before
  development proceeds.
- **When implementing** — follow the standardized practices to keep naming,
  behavior, and idioms consistent across applications.

Deviations should be explicit, documented, and approved rather than assumed.

## Contributing

Standards evolve. Propose changes on a feature branch and open a pull request so
they can be reviewed before merging into `main`.
