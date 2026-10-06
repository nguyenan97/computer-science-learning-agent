# Technical topic map

<!-- Generated from topics.json by scripts/generate_topic_map.py. -->

Choose a practical question you want to answer. Each topic below names useful foundations, a concrete objective and a way to test your understanding with code or an experiment. If a foundation is unfamiliar, start with a small trace or example before the larger task.

Use [topic notes](topic-notes.md) to explore the ideas further. The suggested relationships guide your study; you can adapt them to what you already understand.

## Program contracts and invariants

- **Useful foundations:** check the basics needed by the task
- **Learning objective:** Trace a loop, state its invariant and produce a counterexample to a broken boundary rule.
- **Practice:** Build a small table-driven checker with empty, duplicate and boundary inputs.

## Stable deduplication and cost models

- **Useful foundations:** Program contracts and invariants
- **Learning objective:** Select scan or hashing under explicit order/equality/memory constraints and justify counts separately from timings.
- **Practice:** Implement, test collisions and benchmark scan versus HashSet on controlled datasets.

## Boundary search and ordered queries

- **Useful foundations:** Program contracts and invariants
- **Learning objective:** Derive lower/upper bounds and implement half-open window counting with logarithmic access.
- **Practice:** Use pinned bisect source, trace duplicates, test access budget and transfer to timestamp windows.

## Graphs and strategy selection

- **Useful foundations:** Program contracts and invariants
- **Learning objective:** Choose BFS or Dijkstra from edge assumptions and demonstrate a counterexample for the wrong choice.
- **Practice:** Build a route solver and compare visited nodes and path correctness.

## Dynamic programming and approximation

- **Useful foundations:** Graphs and strategy selection
- **Learning objective:** Define state/recurrence, compare a greedy counterexample and bound solution quality for one optimization task.
- **Practice:** Implement a small exact oracle and compare candidate heuristics on generated instances.

## Storage, indexes and query plans

- **Useful foundations:** Boundary search and ordered queries
- **Learning objective:** Explain seek versus scan from selectivity, ordering and update cost, using a real query plan.
- **Practice:** Populate a local database, inspect plans and measure indexed and unindexed workloads.

## Transactions, concurrency and recovery

- **Useful foundations:** Storage, indexes and query plans
- **Learning objective:** Reproduce one isolation anomaly and explain the selected prevention and recovery mechanism.
- **Practice:** Run two concurrent clients with a logged schedule and crash/recovery trace.

## Probability, estimation and uncertainty

- **Useful foundations:** check the basics needed by the task
- **Learning objective:** Interpret sampling variation and confidence intervals without treating one run as a universal result.
- **Practice:** Simulate samples, plot distributions and test assumptions on a reproducible seed.

## Experimental design and causal limits

- **Useful foundations:** Probability, estimation and uncertainty
- **Learning objective:** Control one experiment, report uncertainty and distinguish association from a causal claim.
- **Practice:** Run baseline/treatment comparisons with confound checks and a reproducible notebook.

## Learning systems and honest evaluation

- **Useful foundations:** Experimental design and causal limits
- **Learning objective:** Build a baseline, prevent leakage and explain metric trade-offs on a held-out dataset.
- **Practice:** Fit a small model, inspect errors and compare against a simple rule baseline.

## Neural networks and optimization

- **Useful foundations:** Learning systems and honest evaluation
- **Learning objective:** Diagnose overfitting or optimization failure with loss curves and one controlled intervention.
- **Practice:** Implement a small network, verify gradients and run a targeted ablation.

## Language models and retrieval evaluation

- **Useful foundations:** Learning systems and honest evaluation
- **Learning objective:** Evaluate one text/retrieval pipeline with an error taxonomy and transparent dataset limitations.
- **Practice:** Compare lexical and embedding retrieval and inspect failed queries.

## Image processing and vision

- **Useful foundations:** Neural networks and optimization
- **Learning objective:** Explain a representation choice and evaluate robustness on a bounded image task.
- **Practice:** Compare a classical transform and a learned baseline under controlled perturbations.

## Parallelism and synchronization

- **Useful foundations:** Program contracts and invariants
- **Learning objective:** Reproduce a race, fix synchronization and explain scaling limits from measured work and overhead.
- **Practice:** Compare serial and parallel implementations with correctness and contention checks.

## Distributed data and fault tolerance

- **Useful foundations:** Transactions, concurrency and recovery, Parallelism and synchronization
- **Learning objective:** Trace failure/retry behavior and justify consistency and idempotency choices.
- **Practice:** Inject duplicate delivery and process failure into a small local pipeline.

## Networks and communication

- **Useful foundations:** Program contracts and invariants
- **Learning objective:** Explain latency, throughput and protocol behavior from a captured request trace.
- **Practice:** Measure a local client/server and inspect retries, timeouts and congestion assumptions.

## Security and threat modeling

- **Useful foundations:** Networks and communication
- **Learning objective:** State assets/trust boundaries and verify one mitigation against a reproducible attack case.
- **Practice:** Build an isolated test harness for authorization, input handling or cryptographic misuse.

## Cloud pipelines and observability

- **Useful foundations:** Distributed data and fault tolerance
- **Learning objective:** Reason about delivery, cost and recovery for a pipeline using measured events.
- **Practice:** Prototype locally first, inject faults and record latency/cost assumptions before optional cloud work.

## Information theory and simulation

- **Useful foundations:** Probability, estimation and uncertainty
- **Learning objective:** Connect entropy or a stochastic model to one measurable engineering question.
- **Practice:** Simulate a channel or queue, compare predicted and observed distributions.

## Reading, reproduction and research synthesis

- **Useful foundations:** Experimental design and causal limits
- **Learning objective:** State a falsifiable question, reproduce a bounded claim and separate evidence from inference.
- **Practice:** Inspect methods/code, run a minimal reproduction and write a claim–evidence–limitation log.

## Data exploration and communication

- **Useful foundations:** Probability, estimation and uncertainty
- **Learning objective:** Choose a faithful visualization and diagnose a misleading representation.
- **Practice:** Build EDA plots with missingness/outlier checks and explain one decision from the data.
