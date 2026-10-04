# Curriculum Dependency Map

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

| Code | Course |
|---|---|
| `6012401` | Philosophy |
| `6011401` | English |
| `6001111` | Advanced Database |
| `6001114` | Computational Statistics |
| `6001115` | Advanced Artificial Intelligence |
| `6001127` | Advanced Algorithms |
| `6001130` | Advanced Data Mining |
| `6001122` | Natural Language Processing |
| `6001121` | Information Security & Safe |
| `6001124` | Parallel Computing |
| `6001129` | Text and Web Analytics |
| `6001210` | Leadership Development |
| `6001219` | Risk Analysis |
| `6001132` | Special Topic |
| `6001131` | Digital Image Processing |
| `6001223` | Deep Learning |
| `6001212` | Pattern Recognition and Analysis |
| `6013400` | Scientific Research Methodology |
| `6001218` | Information Theory |
| `6001220` | Internet Technology of Modern Things |
| `6001222` | Data Processing on Cloud Computing |
| `6001221` | Big Data Analytics |
| `6001126` | Data Analysis Applications |
| `6001225` | Data Visualization |
| `6001229` | Master Thesis |

### Explicit relationships extracted from the Master curriculum

| Course | Source-derived prerequisite/corequisite statement |
|---|---|
| Advanced Artificial Intelligence (`6001115`) | Prerequisite(s): Artificial Intelligence |
| Advanced Data Mining (`6001130`) | Prerequisite(s): Advanced Artificial Intelligence; Advanced Database |
| Natural Language Processing (`6001122`) | Prerequisite(s): Artificial Intelligence, Machine Learning, Deep Learning |
| Digital Image Processing (`6001131`) | Prerequisite(s): Calculus 2, Programming Techniques, Data Structures and Algorithms |
| Deep Learning (`6001223`) | Prerequisite(s): Artificial Intelligence; Co-requisite: Machine Learning |
| Pattern Recognition and Analysis (`6001212`) | Prerequisite(s): Statistics Computing and Applications; Advanced Artificial Intelligence |
| Internet Technology of Modern Things (`6001220`) | Prerequisite(s): Artificial Intelligence; Co-requisite: Deep Learning |

### Source-supported research preparation

The canonical Master curriculum supports the following preparation path, but does not label every arrow as a formal prerequisite:

`Scientific Research Methodology` → `Special Topic / focused literature work` → `Master Thesis`

---

## PhD track — generated course/research index

| Code | Course |
|---|---|
| `6201100` | Deep Learning |
| `6201109` | Big Data Analytics |
| `6201101` | Modern Networking and Communication Technologies |
| `6201102` | Advanced Computer Vision |
| `6201103` | Modern Information Systems Security |
| `6201104` | High Performance Computing |
| `6201105` | Parallel Programming for Multicore Systems |
| `6201106` | Modeling and Simulation Techniques |
| `6201301` | Literature Review |
| `6201200` | Research Topic 1 |
| `6201201` | Research Topic 2 |
| `6201999` | PhD Thesis |

### Explicit relationships extracted from the PhD curriculum

| Course | Source-derived prerequisite/corequisite statement |
|---|---|
| Advanced Computer Vision (`6201102`) | Image Processing (prior), Computer Vision (prerequisite), Deep Learning (co-requisite) |

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
