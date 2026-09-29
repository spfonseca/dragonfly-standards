"""Read a standard's markdown into the `standards` resource shape, and say where it breaks the format.

The format is in STANDARDS.md ("Authoring format"). A standard that breaks it is not converted: every
problem is reported, with its line, so the markdown is fixed rather than the output patched.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_URL = "https://github.com/spfonseca/dragonfly-standards/blob/main"
STATUS_TO_STATE = {"Published": "ACTIVE", "Draft": "DRAFT", "Retired": "RETIRED"}
LEVELS = ("REQUIRED", "RECOMMENDED", "OPTIONAL")
SOFTWARE_LIFECYCLE = {
    "REQUIREMENTS_ANALYSIS", "ARCHITECTURE_AND_DESIGN", "IMPLEMENTATION", "BUILD_AND_INTEGRATION",
    "VERIFICATION_AND_TESTING", "RELEASE", "DEPLOYMENT", "OPERATE_AND_SUPPORT", "MAINTAIN_AND_EVOLVE", "RETIRE",
}
SOLUTION_SCOPE = {
    "SOFTWARE_ARCHITECTURE", "APPLICATION_COMPONENTS", "USER_INTERFACES", "APIS_AND_INTEGRATIONS",
    "DATA_AND_PERSISTENCE", "AI_AND_ML_SYSTEMS", "RUNTIME_AND_EXECUTION", "INFRASTRUCTURE", "NETWORKING",
    "IDENTITY_AND_ACCESS", "SECURITY_CONTROLS", "ENVIRONMENTS_AND_CONFIGURATION", "DELIVERY_AND_AUTOMATION",
    "DEPENDENCIES_AND_EXTERNAL_SERVICES", "OBSERVABILITY", "QUALITY_AND_TESTING", "DOCUMENTATION_ASSETS",
}
ARCHITECTURE_QUALITIES = {
    "AVAILABILITY", "RELIABILITY", "RESILIENCE", "RECOVERABILITY", "PERFORMANCE", "SCALABILITY", "SECURITY",
    "PRIVACY", "COMPLIANCE", "MAINTAINABILITY", "MODIFIABILITY", "EXTENSIBILITY", "INTEROPERABILITY",
    "PORTABILITY", "USABILITY", "ACCESSIBILITY", "TESTABILITY", "OBSERVABILITY", "OPERABILITY",
    "DEPLOYABILITY", "SUPPORTABILITY", "COST_EFFICIENCY",
}
FRONT_MATTER = {
    "shortName", "description", "adoptionMetrics", "impactMetrics", "tags", "softwareLifecycle",
    "solutionScope", "architectureQualities", "industryReferences",
}

SECTION = re.compile(r"^## (0|[1-9][0-9]*)\. (\S.*)$")
GUIDELINE = re.compile(r"^### (0|[1-9][0-9]*)\.([1-9][0-9]*) (\S.*)$")
LEVEL = re.compile(r"^\[(REQUIRED|RECOMMENDED|OPTIONAL)\]\s*")
ANY_LEVEL = re.compile(r"\[(REQUIRED|RECOMMENDED|OPTIONAL)\]")
MARKER = re.compile(r"(\*Rationale:\*|\*Examples?:\*)\s*")
TABLE_ROW = re.compile(r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.*?)\s*\|\s*$")
BULLET = re.compile(r"^-\s+\*\*(.+?)\*\*\s*(?:---|—|–|-)\s*(.*)$")


@dataclass
class Problems:
    path: Path
    items: list[str] = field(default_factory=list)

    def add(self, line: int | None, message: str) -> None:
        self.items.append(f"{self.path}:{line}: {message}" if line else f"{self.path}: {message}")


def _join(lines: list[str]) -> str:
    return "\n".join(lines).strip()


def _split_front_matter(text: str, problems: Problems) -> tuple[dict, list[str], int]:
    lines = text.split("\n")
    if lines[0] != "---":
        problems.add(1, "no front matter: the file must open with a `---` block (STANDARDS.md, Authoring format).")
        return {}, lines, 0
    try:
        end = lines.index("---", 1)
    except ValueError:
        problems.add(1, "front matter is not closed with `---`.")
        return {}, lines, 0
    try:
        meta = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as error:
        problems.add(1, f"front matter is not YAML: {error}")
        return {}, lines[end + 1:], end + 1
    return meta, lines[end + 1:], end + 1


def _check_meta(meta: dict, problems: Problems) -> None:
    for key in sorted(set(meta) - FRONT_MATTER):
        problems.add(1, f"front matter: unknown key `{key}`.")
    if not re.fullmatch(r"[A-Z]{5}", str(meta.get("shortName", ""))):
        problems.add(1, "front matter: `shortName` must be five capital letters.")
    description = meta.get("description")
    if not isinstance(description, str) or not description.strip():
        problems.add(1, "front matter: `description` is required.")
    elif len(description.strip()) > 320:
        problems.add(1, f"front matter: `description` is {len(description.strip())} characters; the limit is 320.")
    for key in ("adoptionMetrics", "impactMetrics", "tags"):
        value = meta.get(key)
        if not isinstance(value, list) or not value or not all(isinstance(v, str) and v.strip() for v in value):
            problems.add(1, f"front matter: `{key}` must be a non-empty list of strings.")
    for key, allowed in (("softwareLifecycle", SOFTWARE_LIFECYCLE), ("solutionScope", SOLUTION_SCOPE),
                         ("architectureQualities", ARCHITECTURE_QUALITIES)):
        value = meta.get(key)
        if not isinstance(value, list) or not value:
            problems.add(1, f"front matter: `{key}` must be a non-empty list.")
            continue
        for bad in [v for v in value if v not in allowed]:
            problems.add(1, f"front matter: `{key}` has `{bad}`, which is not one of the service's values.")
    for ref in meta.get("industryReferences") or []:
        if not (isinstance(ref, dict) and set(ref) == {"title", "url"} and str(ref["url"]).startswith("http")):
            problems.add(1, "front matter: each `industryReferences` entry is `{title, url}`.")


def _header(lines: list[str], offset: int, problems: Problems) -> tuple[str, dict[str, str]]:
    title = next((l[2:].strip() for l in lines if l.startswith("# ")), "")
    if not title:
        problems.add(offset + 1, "no `# Title` line.")
    fields = {}
    for line in lines[:40]:
        match = TABLE_ROW.match(line)
        if match:
            fields[match.group(1)] = match.group(2)
    return title, fields


def _value_proposition(lines: list[str], offset: int, problems: Problems) -> list[str]:
    try:
        start = lines.index("## Value Proposition")
    except ValueError:
        problems.add(None, "no `## Value Proposition` section.")
        return []
    items: list[str] = []
    for n, line in enumerate(lines[start + 1:], start + 1):
        if line.startswith("## "):
            break
        if line.startswith("-"):
            match = BULLET.match(re.sub(r"^-\s+", "- ", line))
            if not match:
                problems.add(offset + n + 1, "a value-proposition bullet is `- **Label** — text`.")
                items.append(line[1:].strip())
                continue
            items.append(f"{match.group(1)} — {match.group(2).strip()}")
        elif line.strip() and items:
            items[-1] = f"{items[-1]} {line.strip()}"
    if not items:
        problems.add(offset + start + 1, "`## Value Proposition` has no bullets.")
    return [re.sub(r"\s+", " ", i) for i in items]


def _glossary(lines: list[str], offset: int, problems: Problems) -> list[dict]:
    start = next((n for n, l in enumerate(lines) if l.strip() == "## Glossary"), None)
    if start is None:
        return []
    terms = []
    rows = 0
    for n, line in enumerate(lines[start + 1:], start + 1):
        if line.startswith("## "):
            break
        if not line.startswith("|"):
            if rows:  # prose may introduce the table, never follow it
                if line.strip() and line.strip() != "---":
                    problems.add(offset + n + 1, "the glossary is one table, `| Term | Definition |`, and nothing after it.")
            continue
        rows += 1
        if rows <= 2:  # header and rule
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 2 or not all(cells):
            problems.add(offset + n + 1, "a glossary row is `| Term | Definition |`.")
            continue
        terms.append({"term": cells[0].strip("*"), "definition": cells[1]})
    return terms


def _body(lines: list[tuple[int, str]], number: str, problems: Problems) -> dict:
    """A guideline's body: `[LEVEL] text`, then `*Rationale:* text`, then any `*Example:*` blocks —
    each marker on its own line or inline, after the text it follows. A guideline may carry further
    statements, each `[LEVEL] text *Rationale:* text`; they are joined, the level is the first's."""
    content = [(n, l) for n, l in lines]
    while content and not content[0][1].strip():
        content.pop(0)
    at = content[0][0] if content else None
    if not content or not LEVEL.match(content[0][1]):
        problems.add(at, f"{number}: the body must open with [REQUIRED], [RECOMMENDED] or [OPTIONAL].")
        return {}
    text = "\n".join(l for _, l in content)
    statements = _statements(text)
    level = statements[0][0]
    descriptions, rationales, examples = [], [], []
    for index, (statement_level, statement) in enumerate(statements):
        pieces = MARKER.split(statement)
        description = pieces[0].strip()
        seen_example = False
        for marker, piece in zip(pieces[1::2], pieces[2::2]):
            if marker.startswith("*Rationale"):
                if seen_example:
                    problems.add(at, f"{number}: *Rationale:* comes before a statement's examples.")
                rationales.append(piece.strip())
            else:
                seen_example = True
                examples.append(piece.strip())
        if not description:
            problems.add(at, f"{number}: a statement with no normative text after its level.")
        descriptions.append(description if index == 0 else f"[{statement_level}] {description}")
    body = {"level": level, "description": "\n\n".join(descriptions)}
    if not any(rationales):
        problems.add(at, f"{number}: no *Rationale:*.")
    else:
        body["rationale"] = "\n\n".join(r for r in rationales if r)
    if any(examples):
        body["examples"] = [e for e in examples if e]
    return body


def _statements(text: str) -> list[tuple[str, str]]:
    """Split at each [LEVEL] that is not inside code."""
    code = [(m.start(), m.end()) for m in re.finditer(r"```.*?```|`[^`\n]*`", text, flags=re.S)]
    cuts = [m for m in ANY_LEVEL.finditer(text) if not any(a <= m.start() < b for a, b in code)]
    return [(m.group(1), text[m.end(): cuts[i + 1].start() if i + 1 < len(cuts) else len(text)].strip())
            for i, m in enumerate(cuts)]


def _outside_code(text: str) -> str:
    return re.sub(r"```.*?```|`[^`]*`", "", text, flags=re.S)


def convert(path: Path, root: Path) -> tuple[dict | None, list[str]]:
    problems = Problems(path.relative_to(root))
    meta, lines, offset = _split_front_matter(path.read_text(encoding="utf-8"), problems)
    _check_meta(meta, problems)
    title, fields = _header(lines, offset, problems)
    version = fields.get("Version", "")
    if not re.fullmatch(r"[1-9][0-9]*\.(0|[1-9][0-9]*)", version):
        problems.add(None, "the header table's **Version** must be `<major>.<minor>`.")
        version = "1.0"
    status = fields.get("Status", "")
    if status not in STATUS_TO_STATE:
        problems.add(None, f"the header table's **Status** must be one of {', '.join(STATUS_TO_STATE)}; it is `{status}`.")
    if "Short Name" in fields and fields["Short Name"] != meta.get("shortName"):
        problems.add(None, "the header table's **Short Name** differs from the front matter's `shortName`.")
    author = fields.get("Author", "").split()
    if len(author) < 2:
        problems.add(None, "the header table's **Author** must be a first and last name.")

    sections: list[dict] = []
    requirements: list[dict] = []
    section: str | None = None
    guideline: tuple[int, str, str] | None = None
    buffer: list[tuple[int, str]] = []
    counts: dict[str, int] = {}
    in_fence = False

    def flush() -> None:
        if guideline is None:
            return
        line, number, directive = guideline
        body = _body(buffer, number, problems)
        if body:
            requirements.append({"sectionNumber": section, "directive": directive, **body})

    for n, line in enumerate(lines, offset + 1):
        if line.startswith("```"):
            in_fence = not in_fence
        if in_fence:
            if guideline:
                buffer.append((n, line))
            continue
        if line.startswith("## "):
            flush()
            guideline, buffer = None, []
            match = SECTION.match(line)
            if match:
                if match.group(1) in counts:
                    problems.add(n, f"section {match.group(1)} appears twice.")
                if sections and int(match.group(1)) != int(sections[-1]["number"]) + 1:
                    problems.add(n, f"section {match.group(1)} does not follow section {sections[-1]['number']}.")
                section = match.group(1)
                counts[section] = 0
                sections.append({"number": section, "name": match.group(2).strip()})
            else:
                section = None
            continue
        if line.startswith("### "):
            flush()
            buffer = []
            match = GUIDELINE.match(line)
            if section is None:
                guideline = None
                problems.add(n, "a `###` guideline outside a numbered `## N.` section.")
                continue
            if not match or match.group(1) != section:
                guideline = None
                problems.add(n, f"a guideline heading in section {section} is `### {section}.M Directive.`")
                continue
            counts[section] += 1
            if int(match.group(2)) != counts[section]:
                problems.add(n, f"guideline {section}.{match.group(2)} is out of sequence (expected {section}.{counts[section]}).")
            guideline = (n, f"{section}.{match.group(2)}", match.group(3).strip())
            continue
        if guideline:
            buffer.append((n, line))
        elif section is not None and ANY_LEVEL.search(line):
            problems.add(n, f"section {section}: a [LEVEL] statement outside a `###` guideline.")
    flush()
    for s in sections:
        if counts[s["number"]] == 0:
            problems.add(None, f"section {s['number']} ({s['name']}) has no guideline; a numbered section holds guidelines, anything else is unnumbered.")
    if not sections:
        problems.add(None, "no numbered `## N.` sections.")

    if problems.items:
        return None, problems.items
    major, minor = (int(v) for v in version.split("."))
    rel = path.relative_to(root).as_posix()
    standard = {
        "shortName": meta["shortName"],
        "name": title,
        "majorVersionNumber": major,
        "minorVersionNumber": minor,
        "state": STATUS_TO_STATE[status],
        "author": {"firstName": author[0], "lastName": " ".join(author[1:])},
        "description": meta["description"].strip(),
        "valueProposition": _value_proposition(lines, offset, problems),
        "adoptionMetrics": meta["adoptionMetrics"],
        "impactMetrics": meta["impactMetrics"],
        "tags": meta["tags"],
        "softwareLifecycle": meta["softwareLifecycle"],
        "solutionScope": meta["solutionScope"],
        "architectureQualities": meta["architectureQualities"],
        "industryReferences": meta.get("industryReferences") or [],
        "additionalResources": [{"title": title, "url": f"{REPO_URL}/{rel}",
                                 "description": "The standard as authored, in Markdown.", "type": "CHECKLIST"}],
        "glossary": _glossary(lines, offset, problems),
        "sections": sections,
        "requirements": requirements,
    }
    return (None, problems.items) if problems.items else (standard, [])
