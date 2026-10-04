#!/usr/bin/env python3
"""Generate references/curriculum-map.md from canonical curriculum Markdown files.

The canonical curriculum files own course facts. This generator owns only the
rendered index and learning-agent relationship view so the repository does not
maintain the same curriculum facts manually in multiple places.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "curricula/iuh/master/curriculum.md"
PHD = ROOT / "curricula/iuh/phd/curriculum.md"
OUTPUT = ROOT / "references/curriculum-map.md"

COURSE_HEADING = re.compile(
    r"^#{2,3}\s+(.+?)\s+—\s+`([^`]+)`(?:\s+\(([^)]*credits?)\))?\s*$",
    re.IGNORECASE,
)


@dataclass
class Course:
    name: str
    code: str
    credits: str = ""
    prerequisite: str = ""
    corequisite: str = ""
    relationship_note: str = ""


def clean_statement(value: str) -> str:
    return value.strip().rstrip(".")


def parse_courses(path: Path) -> list[Course]:
    lines = path.read_text(encoding="utf-8").splitlines()
    courses: list[Course] = []
    current: Course | None = None

    for line in lines:
        match = COURSE_HEADING.match(line.strip())
        if match:
            current = Course(
                name=match.group(1).strip(),
                code=match.group(2).strip(),
                credits=(match.group(3) or "").strip(),
            )
            courses.append(current)
            continue

        if current is None:
            continue

        stripped = line.strip()
        if stripped.startswith("**Prerequisites:**"):
            current.prerequisite = clean_statement(
                stripped.removeprefix("**Prerequisites:**")
            )
        elif stripped.startswith("**Prerequisite:**"):
            current.prerequisite = clean_statement(
                stripped.removeprefix("**Prerequisite:**")
            )
        elif stripped.startswith("**Co-requisite in the source:**"):
            current.corequisite = clean_statement(
                stripped.removeprefix("**Co-requisite in the source:**")
            )
        elif stripped.startswith("**Prerequisite relationships in source:**"):
            current.relationship_note = clean_statement(
                stripped.removeprefix("**Prerequisite relationships in source:**")
            )

    return courses


def course_table(courses: list[Course]) -> str:
    rows = ["| Code | Course |", "|---|---|"]
    rows.extend(f"| `{course.code}` | {course.name} |" for course in courses)
    return "\n".join(rows)


def relationship_table(courses: list[Course]) -> str:
    rows = [
        "| Course | Source-derived prerequisite/corequisite statement |",
        "|---|---|",
    ]

    for course in courses:
        statements: list[str] = []
        if course.prerequisite:
            statements.append(f"Prerequisite(s): {course.prerequisite}")
        if course.corequisite:
            statements.append(f"Co-requisite: {course.corequisite}")
        if course.relationship_note:
            statements.append(course.relationship_note)

        if statements:
            rows.append(
                f"| {course.name} (`{course.code}`) | {'; '.join(statements)} |"
            )

    if len(rows) == 2:
        rows.append("| — | No explicit prerequisite/corequisite statements found |")

    return "\n".join(rows)


def generate() -> str:
    master = parse_courses(MASTER)
    phd = parse_courses(PHD)

    return f"""# Curriculum Dependency Map

> **Generated file — do not edit manually.**  
> Canonical curriculum facts live in:
> - [IUH Master of Computer Science](../curricula/iuh/master/curriculum.md)
> - [IUH PhD in Computer Science](../curricula/iuh/phd/curriculum.md)
>
> Regenerate with `python scripts/generate_curriculum_map.py`. CI uses `--check` to detect drift.

## Ownership model

This file is a **derived planning view**, not a third curriculum source.

- The two canonical curriculum files own **course names, codes, credits, objectives, outcomes, prerequisites, co-requisites, research components and source inconsistencies**.
- This generated map owns only **navigation, explicit relationship extraction and learning-agent synthesis**.
- If this map conflicts with a canonical curriculum file, the canonical curriculum file wins.
- Sections labelled **Learning-agent synthesis** are instructional relationships inferred for sequencing/interleaving; they are **not official IUH prerequisites**.

---

## Master track — generated course index

{course_table(master)}

### Explicit relationships extracted from the Master curriculum

{relationship_table(master)}

### Source-supported research preparation

The canonical Master curriculum supports the following preparation path, but does not label every arrow as a formal prerequisite:

`Scientific Research Methodology` → `Special Topic / focused literature work` → `Master Thesis`

---

## PhD track — generated course/research index

{course_table(phd)}

### Explicit relationships extracted from the PhD curriculum

{relationship_table(phd)}

### Source-supported doctoral research sequence

`Literature Review` → `Research Topic 1` → `Research Topic 2` → `PhD Thesis`

The PhD curriculum also identifies Master's-level supplementary knowledge for candidates who need additional foundation work; the detailed shared foundations remain in the canonical Master curriculum rather than being duplicated here.

---

## Learning-agent synthesis

The relationships below are maintained as instructional planning rules. They connect the official course content into a usable learning graph, but should not be presented as formal university prerequisite rules unless the canonical curriculum explicitly says so.

### Master knowledge dependencies

- **Computational Statistics** → Pattern Recognition, Data Mining evaluation, model evaluation and empirical analysis.
- **Advanced Algorithms** → AI search/optimization, graph and web analytics, scalable computation.
- **Advanced Database** → Data Mining, Big Data Analytics and Cloud Data Processing.
- **Advanced Artificial Intelligence** → Data Mining, Pattern Recognition, Deep Learning and NLP foundations.
- **Deep Learning** → modern NLP, Computer Vision and AI-enabled IoT applications.
- **Parallel Computing** → Big Data execution, scalable ML and distributed/high-performance processing.
- **Scientific Research Methodology** → research design, Special Topic work and thesis preparation.

### Master → PhD bridges

- **Deep Learning** → PhD Deep Learning and Advanced Computer Vision.
- **Parallel Computing** → High Performance Computing and Parallel Programming for Multicore Systems.
- **Advanced Data Mining / Big Data Analytics** → PhD Big Data Analytics.
- **Information Security & Safe** → Modern Information Systems Security.
- **Digital Image Processing / Pattern Recognition** → Advanced Computer Vision.
- **IoT / Cloud Data Processing** → Modern Networking and Communication Technologies.
- **Master Thesis / research methodology** → Literature Review, Research Topic 1/2 and doctoral thesis practice.

### High-value interleaving pairs

- database indexing ↔ algorithm complexity
- hypothesis testing ↔ experiment / A-B-test reasoning
- entropy ↔ decision trees / cross-entropy reasoning
- graph algorithms ↔ web analytics
- concurrency control ↔ distributed-system consistency
- parallelism ↔ Big Data execution plans
- security ↔ cloud / IoT architecture
- model evaluation ↔ statistical inference
- visualization ↔ decision quality
- research methodology ↔ every empirical mini-project

---

## Maintenance contract

When either canonical curriculum changes:

1. Edit only the relevant `curricula/iuh/.../curriculum.md` source.
2. Run `python scripts/generate_curriculum_map.py`.
3. Review the generated diff in `references/curriculum-map.md`.
4. If conceptual sequencing also changed, update the **Learning-agent synthesis** section in this generator, then regenerate.
5. Run `python scripts/generate_curriculum_map.py --check` before committing.

This keeps official curriculum facts in one place while still giving the learning agent a compact dependency graph for topic selection.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when the generated map differs from the committed file.",
    )
    args = parser.parse_args()

    content = generate()

    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != content:
            print(
                "references/curriculum-map.md is out of date. "
                "Run: python scripts/generate_curriculum_map.py",
                file=sys.stderr,
            )
            return 1
        print("curriculum-map.md is up to date")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"generated {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
