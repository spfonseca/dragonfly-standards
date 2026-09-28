"""The markdown-to-`standards` conversion (scripts/standard_md.py), against small authored files."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from standard_md import convert  # noqa: E402

FRONT = """---
shortName: WIDGT
description: How widgets are built.
adoptionMetrics: [Share of widgets built to it]
impactMetrics: [Widget defects per release]
tags: [widgets]
softwareLifecycle: [IMPLEMENTATION]
solutionScope: [APPLICATION_COMPONENTS]
architectureQualities: [RELIABILITY]
---
"""
HEADER = """# Widget Standard

| Field | Value |
|---|---|
| **Short Name** | WIDGT |
| **Version** | 1.2 |
| **Status** | Draft |
| **Author** | Ada Lovelace |

## Value Proposition

- **Fewer defects** — widgets behave alike.
"""


def write(tmp_path, body, front=FRONT):
    path = tmp_path / "widgets" / "widget-standard.md"
    path.parent.mkdir(exist_ok=True)
    path.write_text(front + HEADER + body)
    return convert(path, tmp_path)



def test_sections_guidelines_and_their_parts(tmp_path):
    standard, problems = write(tmp_path, """
## 1. Building

### 1.1 Build widgets from parts.

[REQUIRED] A widget shall be built from parts. *Rationale:* Parts are reusable. *Example:* a gear.

### 1.2 Paint them.

[RECOMMENDED] A widget should be painted.

*Rationale:* Paint protects it.
[OPTIONAL] It may be blue. *Rationale:* Blue is calm.

## Glossary

| Term | Definition |
|---|---|
| Widget | A small thing. |
""")
    assert problems == []
    assert (standard["shortName"], standard["majorVersionNumber"], standard["minorVersionNumber"], standard["state"]) == ("WIDGT", 1, 2, "DRAFT")
    assert standard["author"] == {"firstName": "Ada", "lastName": "Lovelace"}
    assert standard["valueProposition"] == ["Fewer defects — widgets behave alike."]
    assert standard["sections"] == [{"number": "1", "name": "Building"}]
    first, second = standard["requirements"]
    assert first == {"sectionNumber": "1", "directive": "Build widgets from parts.", "level": "REQUIRED",
                     "description": "A widget shall be built from parts.", "rationale": "Parts are reusable.",
                     "examples": ["a gear."]}
    assert second["level"] == "RECOMMENDED"
    assert second["description"] == "A widget should be painted.\n\n[OPTIONAL] It may be blue."
    assert second["rationale"] == "Paint protects it.\n\nBlue is calm."
    assert standard["glossary"] == [{"term": "Widget", "definition": "A small thing."}]


def test_every_break_is_named_and_nothing_converts(tmp_path):
    standard, problems = write(tmp_path, """
## 1. Building

### 1.2 Skipped a number.

A widget shall be built. *Rationale:* none.

## 3. Empty
""", front="")
    assert standard is None
    text = "\n".join(problems)
    for expected in ("no front matter", "out of sequence", "must open with [REQUIRED]",
                     "section 3 does not follow section 1", "section 3 (Empty) has no guideline"):
        assert expected in text


def test_a_level_inside_code_is_not_a_second_statement(tmp_path):
    standard, problems = write(tmp_path, """
## 1. Building

### 1.1 Mark levels.

[REQUIRED] Write `[OPTIONAL]` in code when quoting a level. *Rationale:* Clarity.
""")
    assert problems == []
    assert standard["requirements"][0]["description"] == "Write `[OPTIONAL]` in code when quoting a level."
