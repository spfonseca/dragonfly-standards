#!/usr/bin/env python3
"""Convert every standard in this repository into the `standards` resource shape and publish the array
to environments' content buckets, for the platform's initialization to load.

Every `<dir>/*.md` standard is converted, drafts included (a draft loads as DRAFT). A standard that
breaks the authoring format (STANDARDS.md) stops the publish, with every problem listed. Run by a
member of initial-content-publishers, with their own credentials; by hand for now.

    scripts/publish-to-content.py --check                         # convert and report; write nothing
    scripts/publish-to-content.py --out standards.json            # write the array locally
    scripts/publish-to-content.py --project dev-d-architect       # publish
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from standard_md import convert  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OBJECT = "initial-content/standards/standards.json"
NOT_STANDARDS = {"docs", "scripts", ".git", ".github"}


def standard_files() -> list[Path]:
    return sorted(p for p in ROOT.glob("*/*.md") if p.parent.name not in NOT_STANDARDS and not p.parent.name.startswith("."))


def convert_all() -> tuple[list[dict], list[str]]:
    standards, problems = [], []
    for path in standard_files():
        standard, found = convert(path, ROOT)
        problems += found
        if standard:
            standards.append(standard)
    by_version = defaultdict(list)
    names = defaultdict(set)
    for s in standards:
        by_version[(s["shortName"], s["majorVersionNumber"], s["minorVersionNumber"])].append(s["name"])
        names[s["shortName"]].add(s["name"])
    for key, found in by_version.items():
        if len(found) > 1:
            problems.append(f"{key[0]} v{key[1]}.{key[2]} is authored more than once.")
    for short, found in names.items():
        if len(found) > 1:
            problems.append(f"{short}: every version carries the same title; found {sorted(found)}.")
    declared = {f"{s['shortName']}-v{s['majorVersionNumber']}" for s in standards}
    active = {f"{s['shortName']}-v{s['majorVersionNumber']}" for s in standards if s["state"] == "ACTIVE"}
    for s in standards:
        for ref in s["supportingStandards"]:
            if ref not in declared:
                problems.append(f"{s['shortName']}: supporting standard {ref} is not in this repository.")
            elif ref not in active:
                problems.append(f"{s['shortName']}: supporting standard {ref} has no Published version.")
    standards.sort(key=lambda s: (s["shortName"], s["majorVersionNumber"], s["minorVersionNumber"]))
    return standards, problems


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--project", nargs="+", default=[])
    args = parser.parse_args()

    standards, problems = convert_all()
    if problems:
        print("\n".join(problems), file=sys.stderr)
        sys.exit(f"{len(problems)} problem(s); nothing published.")
    counts = ", ".join(f"{s['shortName']} {s['majorVersionNumber']}.{s['minorVersionNumber']} "
                       f"{s['state']} ({len(s['requirements'])})" for s in standards)
    print(f"==> {len(standards)} standards: {counts}")
    text = json.dumps({"standards": standards}, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"    wrote {args.out}")
    if args.check:
        return
    for project in args.project:
        from google.cloud import storage

        storage.Client(project=project).bucket(f"{project}-content").blob(OBJECT).upload_from_string(
            text, content_type="application/json")
        print(f"    published gs://{project}-content/{OBJECT}")


if __name__ == "__main__":
    main()
