# IUH self-study topic map

<!-- Generated from topics.json and lessons/catalog.json. -->

Mapped to the course-name inventory of IUH master (2020) and doctoral (October 2022) outlines. Prerequisites and study objectives are project design. Coverage counts published lesson artifacts, not mastery, credits or degrees. Elective names are included as optional breadth; this is not an official graduation plan.

| Master / Doctoral | Area | Published topics / planned | Coverage |
|---|---|---:|---:|
| Master | AI and learning | 0/7 | 0.0% |
| Master | Algorithms | 5/5 | 100.0% |
| Master | Academic communication | 0/1 | 0.0% |
| Master | Data and databases | 0/3 | 0.0% |
| Master | General studies | 0/1 | 0.0% |
| Master | Information and modeling | 0/1 | 0.0% |
| Master | Leadership and risk | 0/2 | 0.0% |
| Master | Research methods | 0/3 | 0.0% |
| Master | Security | 0/1 | 0.0% |
| Master | Statistics | 0/2 | 0.0% |
| Master | Systems | 0/4 | 0.0% |
| Master | Visualization | 0/1 | 0.0% |
| Doctoral | AI and learning | 0/2 | 0.0% |
| Doctoral | Information and modeling | 0/1 | 0.0% |
| Doctoral | Research methods | 0/4 | 0.0% |
| Doctoral | Security | 0/1 | 0.0% |
| Doctoral | Systems | 0/4 | 0.0% |

**Total planned units: 5/43.**

[Course inventory and original study questions](topic-notes.md)

## Program contracts and invariants

- **Published** · Master · Algorithms · `build`
- **Foundations:** —
- **Objective:** Trace a loop, state its invariant and produce a counterexample to a broken boundary rule.
- **Practice:** Build a small table-driven checker with empty, duplicate and boundary inputs.

## Stable deduplication and cost models

- **Published** · Master · Algorithms · `build`
- **Foundations:** Program contracts and invariants
- **Objective:** Select scan or hashing under explicit order/equality/memory constraints and justify counts separately from timings.
- **Practice:** Implement, test collisions and benchmark scan versus HashSet on controlled datasets.

## Boundary search and ordered queries

- **Published** · Master · Algorithms · `build`
- **Foundations:** Program contracts and invariants
- **Objective:** Derive lower/upper bounds and implement half-open window counting with logarithmic access.
- **Practice:** Use pinned bisect source, trace duplicates, test access budget and transfer to timestamp windows.

## Graphs and strategy selection

- **Published** · Master · Algorithms · `build`
- **Foundations:** Program contracts and invariants
- **Objective:** Choose BFS or Dijkstra from edge assumptions and demonstrate a counterexample for the wrong choice.
- **Practice:** Build a route solver and compare visited nodes and path correctness.

## Dynamic programming and approximation

- **Published** · Master · Algorithms · `build`
- **Foundations:** Graphs and strategy selection
- **Objective:** Define state/recurrence, compare a greedy counterexample and bound solution quality for one optimization task.
- **Practice:** Implement a small exact oracle and compare candidate heuristics on generated instances.

## Storage, indexes and query plans

- **Planned** · Master · Data and databases · `build`
- **Foundations:** Boundary search and ordered queries
- **Objective:** Explain seek versus scan from selectivity, ordering and update cost, using a real query plan.
- **Practice:** Populate a local database, inspect plans and measure indexed and unindexed workloads.

## Transactions, concurrency and recovery

- **Planned** · Master · Data and databases · `build`
- **Foundations:** Storage, indexes and query plans
- **Objective:** Reproduce one isolation anomaly and explain the selected prevention and recovery mechanism.
- **Practice:** Run two concurrent clients with a logged schedule and crash/recovery trace.

## Probability, estimation and uncertainty

- **Planned** · Master · Statistics · `build`
- **Foundations:** —
- **Objective:** Interpret sampling variation and confidence intervals without treating one run as a universal result.
- **Practice:** Simulate samples, plot distributions and test assumptions on a reproducible seed.

## Experimental design and causal limits

- **Planned** · Master · Statistics · `build`
- **Foundations:** Probability, estimation and uncertainty
- **Objective:** Control one experiment, report uncertainty and distinguish association from a causal claim.
- **Practice:** Run baseline/treatment comparisons with confound checks and a reproducible notebook.

## Learning systems and honest evaluation

- **Planned** · Master · AI and learning · `build`
- **Foundations:** Experimental design and causal limits
- **Objective:** Build a baseline, prevent leakage and explain metric trade-offs on a held-out dataset.
- **Practice:** Fit a small model, inspect errors and compare against a simple rule baseline.

## Neural networks and optimization

- **Planned** · Master · AI and learning · `build`
- **Foundations:** Learning systems and honest evaluation
- **Objective:** Diagnose overfitting or optimization failure with loss curves and one controlled intervention.
- **Practice:** Implement a small network, verify gradients and run a targeted ablation.

## Language models and retrieval evaluation

- **Planned** · Master · AI and learning · `build`
- **Foundations:** Learning systems and honest evaluation
- **Objective:** Evaluate one text/retrieval pipeline with an error taxonomy and transparent dataset limitations.
- **Practice:** Compare lexical and embedding retrieval and inspect failed queries.

## Image processing and vision

- **Planned** · Master · AI and learning · `build`
- **Foundations:** Neural networks and optimization
- **Objective:** Explain a representation choice and evaluate robustness on a bounded image task.
- **Practice:** Compare a classical transform and a learned baseline under controlled perturbations.

## Parallelism and synchronization

- **Planned** · Master · Systems · `build`
- **Foundations:** Program contracts and invariants
- **Objective:** Reproduce a race, fix synchronization and explain scaling limits from measured work and overhead.
- **Practice:** Compare serial and parallel implementations with correctness and contention checks.

## Distributed data and fault tolerance

- **Planned** · Master · Systems · `build`
- **Foundations:** Transactions, concurrency and recovery, Parallelism and synchronization
- **Objective:** Trace failure/retry behavior and justify consistency and idempotency choices.
- **Practice:** Inject duplicate delivery and process failure into a small local pipeline.

## Networks and communication

- **Planned** · Master · Systems · `build`
- **Foundations:** Program contracts and invariants
- **Objective:** Explain latency, throughput and protocol behavior from a captured request trace.
- **Practice:** Measure a local client/server and inspect retries, timeouts and congestion assumptions.

## Security and threat modeling

- **Planned** · Master · Security · `build`
- **Foundations:** Networks and communication
- **Objective:** State assets/trust boundaries and verify one mitigation against a reproducible attack case.
- **Practice:** Build an isolated test harness for authorization, input handling or cryptographic misuse.

## Cloud pipelines and observability

- **Planned** · Master · Systems · `build`
- **Foundations:** Distributed data and fault tolerance
- **Objective:** Reason about delivery, cost and recovery for a pipeline using measured events.
- **Practice:** Prototype locally first, inject faults and record latency/cost assumptions before optional cloud work.

## Information theory and simulation

- **Planned** · Master · Information and modeling · `paper`
- **Foundations:** Probability, estimation and uncertainty
- **Objective:** Connect entropy or a stochastic model to one measurable engineering question.
- **Practice:** Simulate a channel or queue, compare predicted and observed distributions.

## Reading, reproduction and research synthesis

- **Planned** · Master · Research methods · `paper`
- **Foundations:** Experimental design and causal limits
- **Objective:** State a falsifiable question, reproduce a bounded claim and separate evidence from inference.
- **Practice:** Inspect methods/code, run a minimal reproduction and write a claim–evidence–limitation log.

## Data exploration and communication

- **Planned** · Master · Visualization · `build`
- **Foundations:** Probability, estimation and uncertainty
- **Objective:** Choose a faithful visualization and diagnose a misleading representation.
- **Practice:** Build EDA plots with missingness/outlier checks and explain one decision from the data.

## Philosophy

- **Planned** · Master · General studies · `paper`
- **Foundations:** —
- **Objective:** What assumptions make a scientific claim testable, and what would count against it?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## English

- **Planned** · Master · Academic communication · `paper`
- **Foundations:** —
- **Objective:** How can you rewrite a technical claim in English without overstating the evidence?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Advanced Artificial Intelligence

- **Planned** · Master · AI and learning · `build`
- **Foundations:** Probability, estimation and uncertainty
- **Objective:** When does evidence change a probabilistic prediction, and how can you check the update?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Text and Web Analytics

- **Planned** · Master · AI and learning · `build`
- **Foundations:** Language models and retrieval evaluation
- **Objective:** How do duplicate documents and collection bias distort a retrieval experiment?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Leadership Development

- **Planned** · Master · Leadership and risk · `paper`
- **Foundations:** —
- **Objective:** How can a team make a technical decision while preserving dissent and accountability?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Risk Analysis

- **Planned** · Master · Leadership and risk · `paper`
- **Foundations:** Probability, estimation and uncertainty
- **Objective:** Which decision changes when both the likelihood and cost of failure are uncertain?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Special Topic

- **Planned** · Master · Research methods · `paper`
- **Foundations:** Reading, reproduction and research synthesis
- **Objective:** Can you bound a new technical question tightly enough to reproduce one relevant result?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Pattern Recognition and Analysis

- **Planned** · Master · AI and learning · `build`
- **Foundations:** Learning systems and honest evaluation
- **Objective:** What changes when the cost of a false positive differs from that of a false negative?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Data Analysis Applications

- **Planned** · Master · Data and databases · `build`
- **Foundations:** Experimental design and causal limits
- **Objective:** Can a reproducible analysis separate data cleaning decisions from the final claim?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Master Thesis

- **Planned** · Master · Research methods · `paper`
- **Foundations:** Reading, reproduction and research synthesis
- **Objective:** Can you specify a feasible research question, baseline and evaluation protocol in a proposal?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Deep Learning

- **Planned** · Doctoral · AI and learning · `paper`
- **Foundations:** Neural networks and optimization
- **Objective:** Which ablation would challenge the claimed mechanism of a deep-learning paper?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Big Data Analytics

- **Planned** · Doctoral · Systems · `build`
- **Foundations:** Distributed data and fault tolerance
- **Objective:** Can a distributed result be reproduced across workload sizes and failure conditions?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Modern Networking and Communication Technologies

- **Planned** · Doctoral · Systems · `paper`
- **Foundations:** Networks and communication
- **Objective:** Which workload and latency assumptions limit a networking research claim?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Advanced Computer Vision

- **Planned** · Doctoral · AI and learning · `paper`
- **Foundations:** Image processing and vision, Deep Learning
- **Objective:** Does a vision result survive a change of scene, camera or evaluation distribution?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Modern Information Systems Security

- **Planned** · Doctoral · Security · `paper`
- **Foundations:** Security and threat modeling
- **Objective:** What threat-model change invalidates a security paper’s comparison?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## High Performance Computing

- **Planned** · Doctoral · Systems · `build`
- **Foundations:** Parallelism and synchronization
- **Objective:** Which hardware bottleneck explains scaling, and how can you separate it from measurement noise?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Parallel Programming for Multicore Systems

- **Planned** · Doctoral · Systems · `build`
- **Foundations:** Parallelism and synchronization, High Performance Computing
- **Objective:** Can a synchronization design retain correctness while reducing contention under a changed schedule?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Modeling and Simulation Techniques

- **Planned** · Doctoral · Information and modeling · `build`
- **Foundations:** Information theory and simulation
- **Objective:** Which observations validate a simulator, and which predictions remain outside its calibrated domain?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Literature Review

- **Planned** · Doctoral · Research methods · `paper`
- **Foundations:** Reading, reproduction and research synthesis
- **Objective:** Can you organize conflicting papers by assumptions and evidence instead of publication order?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Research Topic 1

- **Planned** · Doctoral · Research methods · `paper`
- **Foundations:** Literature Review
- **Objective:** Can you reproduce a baseline closely enough to identify a specific unresolved question?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## Research Topic 2

- **Planned** · Doctoral · Research methods · `paper`
- **Foundations:** Research Topic 1
- **Objective:** What experiment could refute your proposed improvement, including an unchanged or negative result?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.

## PhD Thesis

- **Planned** · Doctoral · Research methods · `paper`
- **Foundations:** Research Topic 2
- **Objective:** Which contribution remains defensible after comparison, replication and explicit limitations?
- **Practice:** Develop one worked case, compare it with a counterexample and write the limits of the resulting argument.
