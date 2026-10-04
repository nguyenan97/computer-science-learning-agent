#!/usr/bin/env python3
"""Generate bilingual curriculum dependency maps from canonical curriculum Markdown.

English curriculum files under ``curricula/`` are the canonical source of curriculum
facts. This generator renders compact English and Vietnamese planning views so the
repository does not maintain course facts manually in multiple maps.
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
OUTPUT_EN = ROOT / "references/curriculum-map.md"
OUTPUT_VI = ROOT / "vi/references/curriculum-map.md"

COURSE_HEADING = re.compile(
    r"^#{2,3}\s+(.+?)\s+—\s+`([^`]+)`(?:\s+\(([^)]*credits?)\))?\s*$",
    re.IGNORECASE,
)

VI_NAMES = {
    "Philosophy": "Triết học",
    "English": "Tiếng Anh",
    "Advanced Database": "Cơ sở dữ liệu nâng cao",
    "Computational Statistics": "Thống kê tính toán",
    "Advanced Artificial Intelligence": "Trí tuệ nhân tạo nâng cao",
    "Advanced Algorithms": "Thuật toán nâng cao",
    "Advanced Data Mining": "Khai phá dữ liệu nâng cao",
    "Natural Language Processing": "Xử lý ngôn ngữ tự nhiên",
    "Information Security & Safe": "An toàn và bảo mật thông tin",
    "Parallel Computing": "Tính toán song song",
    "Text and Web Analytics": "Phân tích văn bản và Web",
    "Leadership Development": "Phát triển năng lực lãnh đạo",
    "Risk Analysis": "Phân tích rủi ro",
    "Special Topic": "Chuyên đề",
    "Digital Image Processing": "Xử lý ảnh số",
    "Deep Learning": "Học sâu",
    "Pattern Recognition and Analysis": "Nhận dạng và phân tích mẫu",
    "Scientific Research Methodology": "Phương pháp nghiên cứu khoa học",
    "Information Theory": "Lý thuyết thông tin",
    "Internet Technology of Modern Things": "Công nghệ IoT hiện đại",
    "Data Processing on Cloud Computing": "Xử lý dữ liệu trên điện toán đám mây",
    "Big Data Analytics": "Phân tích dữ liệu lớn",
    "Data Analysis Applications": "Ứng dụng phân tích dữ liệu",
    "Data Visualization": "Trực quan hóa dữ liệu",
    "Master Thesis": "Luận văn Thạc sĩ",
    "Modern Networking and Communication Technologies": "Công nghệ mạng và truyền thông hiện đại",
    "Advanced Computer Vision": "Thị giác máy tính nâng cao",
    "Modern Information Systems Security": "An toàn hệ thống thông tin hiện đại",
    "High Performance Computing": "Tính toán hiệu năng cao",
    "Parallel Programming for Multicore Systems": "Lập trình song song cho hệ thống đa lõi",
    "Modeling and Simulation Techniques": "Kỹ thuật mô hình hóa và mô phỏng",
    "Literature Review": "Tổng quan nghiên cứu",
    "Research Topic 1": "Chuyên đề nghiên cứu 1",
    "Research Topic 2": "Chuyên đề nghiên cứu 2",
    "PhD Thesis": "Luận án Tiến sĩ",
}


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


def display_name(course: Course, locale: str) -> str:
    if locale == "vi" and course.name in VI_NAMES:
        return f"{course.name} — {VI_NAMES[course.name]}"
    return course.name


def course_table(courses: list[Course], locale: str = "en") -> str:
    if locale == "vi":
        rows = ["| Mã | Học phần |", "|---|---|"]
    else:
        rows = ["| Code | Course |", "|---|---|"]
    rows.extend(
        f"| `{course.code}` | {display_name(course, locale)} |" for course in courses
    )
    return "\n".join(rows)


def translate_relationship_note(value: str) -> str:
    return (
        value.replace("Image Processing (prior)", "Image Processing (học trước)")
        .replace("Computer Vision (prerequisite)", "Computer Vision (tiên quyết)")
        .replace("Deep Learning (co-requisite)", "Deep Learning (học song hành)")
    )


def relationship_table(courses: list[Course], locale: str = "en") -> str:
    if locale == "vi":
        rows = [
            "| Học phần | Prerequisite/corequisite trích từ canonical source |",
            "|---|---|",
        ]
    else:
        rows = [
            "| Course | Source-derived prerequisite/corequisite statement |",
            "|---|---|",
        ]

    for course in courses:
        statements: list[str] = []
        if course.prerequisite:
            prefix = "Tiên quyết" if locale == "vi" else "Prerequisite(s)"
            statements.append(f"{prefix}: {course.prerequisite}")
        if course.corequisite:
            prefix = "Học song hành" if locale == "vi" else "Co-requisite"
            statements.append(f"{prefix}: {course.corequisite}")
        if course.relationship_note:
            note = (
                translate_relationship_note(course.relationship_note)
                if locale == "vi"
                else course.relationship_note
            )
            statements.append(note)

        if statements:
            rows.append(
                f"| {display_name(course, locale)} (`{course.code}`) | {'; '.join(statements)} |"
            )

    if len(rows) == 2:
        empty = (
            "Không tìm thấy prerequisite/corequisite được khai báo rõ"
            if locale == "vi"
            else "No explicit prerequisite/corequisite statements found"
        )
        rows.append(f"| — | {empty} |")

    return "\n".join(rows)


def generate_en(master: list[Course], phd: list[Course]) -> str:
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
3. Review the generated diffs in both curriculum maps.
4. If conceptual sequencing also changed, update the **Learning-agent synthesis** sections in this generator, then regenerate.
5. Run `python scripts/generate_curriculum_map.py --check` before committing.

This keeps official curriculum facts in one place while still giving the learning agent a compact dependency graph for topic selection.
"""


def generate_vi(master: list[Course], phd: list[Course]) -> str:
    return f"""# Bản đồ dependency của chương trình

> **File được generate — không chỉnh sửa thủ công.**  
> Canonical curriculum facts nằm trong:
> - [IUH Master of Computer Science](../../curricula/iuh/master/curriculum.md)
> - [IUH PhD in Computer Science](../../curricula/iuh/phd/curriculum.md)
>
> Generate lại bằng `python scripts/generate_curriculum_map.py`. CI dùng `--check` để phát hiện drift.

## Ownership model

File này là **derived planning view**, không phải curriculum source thứ ba.

- Hai canonical curriculum file sở hữu **course name, code, credit, objective, outcome, prerequisite, co-requisite, research component và source inconsistency**.
- Generated map chỉ sở hữu **navigation, explicit relationship extraction và learning-agent synthesis**.
- Nếu map mâu thuẫn với canonical curriculum, canonical curriculum luôn được ưu tiên.
- Các phần có nhãn **Learning-agent synthesis** là relationship phục vụ sequencing/interleaving và **không phải prerequisite chính thức của IUH**.

---

## Master track — generated course index

{course_table(master, "vi")}

### Relationship trích trực tiếp từ Master curriculum

{relationship_table(master, "vi")}

### Research preparation được source hỗ trợ

Canonical Master curriculum hỗ trợ preparation path sau, nhưng không định nghĩa mọi mũi tên là formal prerequisite:

`Scientific Research Methodology` → `Special Topic / focused literature work` → `Master Thesis`

---

## PhD track — generated course/research index

{course_table(phd, "vi")}

### Relationship trích trực tiếp từ PhD curriculum

{relationship_table(phd, "vi")}

### Doctoral research sequence được source hỗ trợ

`Literature Review` → `Research Topic 1` → `Research Topic 2` → `PhD Thesis`

PhD curriculum cũng xác định supplementary knowledge ở mức Master's cho candidate cần bổ sung nền tảng; detailed shared foundation vẫn nằm trong canonical Master curriculum thay vì duplicate ở đây.

---

## Learning-agent synthesis

Các relationship dưới đây là instructional planning rule. Chúng kết nối official course content thành learning graph có thể sử dụng, nhưng không được trình bày như formal university prerequisite trừ khi canonical curriculum ghi rõ.

### Master knowledge dependencies

- **Computational Statistics — Thống kê tính toán** → Pattern Recognition, Data Mining evaluation, model evaluation và empirical analysis.
- **Advanced Algorithms — Thuật toán nâng cao** → AI search/optimization, graph/web analytics, scalable computation.
- **Advanced Database — Cơ sở dữ liệu nâng cao** → Data Mining, Big Data Analytics và Cloud Data Processing.
- **Advanced Artificial Intelligence — Trí tuệ nhân tạo nâng cao** → Data Mining, Pattern Recognition, Deep Learning và NLP foundation.
- **Deep Learning — Học sâu** → modern NLP, Computer Vision và AI-enabled IoT application.
- **Parallel Computing — Tính toán song song** → Big Data execution, scalable ML và distributed/high-performance processing.
- **Scientific Research Methodology — Phương pháp nghiên cứu khoa học** → research design, Special Topic và thesis preparation.

### Bridge từ Master → PhD

- **Deep Learning** → PhD Deep Learning và Advanced Computer Vision.
- **Parallel Computing** → High Performance Computing và Parallel Programming for Multicore Systems.
- **Advanced Data Mining / Big Data Analytics** → PhD Big Data Analytics.
- **Information Security & Safe** → Modern Information Systems Security.
- **Digital Image Processing / Pattern Recognition** → Advanced Computer Vision.
- **IoT / Cloud Data Processing** → Modern Networking and Communication Technologies.
- **Master Thesis / research methodology** → Literature Review, Research Topic 1/2 và doctoral thesis practice.

### High-value interleaving pairs

- database indexing ↔ algorithm complexity
- hypothesis testing ↔ experiment / A-B-test reasoning
- entropy ↔ decision tree / cross-entropy reasoning
- graph algorithm ↔ web analytics
- concurrency control ↔ distributed-system consistency
- parallelism ↔ Big Data execution plan
- security ↔ cloud / IoT architecture
- model evaluation ↔ statistical inference
- visualization ↔ decision quality
- research methodology ↔ mọi empirical mini-project

---

## Maintenance contract

Khi canonical curriculum thay đổi:

1. Chỉ sửa source `curricula/iuh/.../curriculum.md` tương ứng.
2. Cập nhật bản dịch curriculum trong `vi/curricula/iuh/.../curriculum.md`.
3. Chạy `python scripts/generate_curriculum_map.py`.
4. Review diff của cả hai curriculum map.
5. Nếu conceptual sequencing thay đổi, cập nhật phần **Learning-agent synthesis** trong generator rồi generate lại.
6. Chạy `python scripts/generate_curriculum_map.py --check` trước khi commit.

Cách này giữ official curriculum fact ở một nơi nhưng vẫn cung cấp dependency graph song ngữ cho topic selection của learning agent.
"""


def generate_all() -> dict[Path, str]:
    master = parse_courses(MASTER)
    phd = parse_courses(PHD)
    return {
        OUTPUT_EN: generate_en(master, phd),
        OUTPUT_VI: generate_vi(master, phd),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when either generated curriculum map differs from the committed file.",
    )
    args = parser.parse_args()

    outputs = generate_all()

    if args.check:
        stale: list[Path] = []
        for path, content in outputs.items():
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path)
        if stale:
            print(
                "Generated curriculum map(s) are out of date: "
                + ", ".join(str(path.relative_to(ROOT)) for path in stale)
                + ". Run: python scripts/generate_curriculum_map.py",
                file=sys.stderr,
            )
            return 1
        print("English and Vietnamese curriculum maps are up to date")
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"generated {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
