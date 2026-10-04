# Pedagogy

## Learning Model

Optimize for durable recall and transfer, not the feeling of familiarity.

Use:

- retrieval practice
- spaced practice
- interleaving
- self-explanation
- worked examples followed by faded guidance
- deliberate practice on errors
- project/problem-based learning
- immediate feedback after an attempt

## Daily Loop

### 1. Retrieve

Start without notes.

Ask 3-5 short questions from prior material. Mix recall and application.

### 2. Encounter a Problem

Present a realistic problem that creates a need for the new concept.

The learner should know what they are trying to solve before reading the explanation.

### 3. Build the Mental Model

Teach the minimum theory required to reason about the problem.

Use diagrams, invariants, equations, execution traces, or data-flow models when useful.

### 4. Guided Practice

Show one worked example and narrate decisions.

Avoid multiple near-identical examples.

### 5. Independent Practice

Give a task with less scaffolding.

Require a decision, not just syntax reproduction.

### 6. Feedback

Classify errors:

- knowledge gap
- incorrect mental model
- careless execution
- tool/API misuse
- design trade-off not considered

Use the error class to determine the next hint.

### 7. Explain Back

Ask the learner to explain:

- what problem the concept solves
- how it works
- when it fails
- what alternative exists
- what trade-off matters

### 8. Revisit Later

Reinsert the concept in future warm-ups and mixed problems.

Suggested default review offsets are +1 day, +3 days, +7 days, and +21 days. These are a scheduling heuristic and may be adapted to performance.

## Practice Allocation

For a 60-minute lesson, a good default is:

- 5 min retrieval warm-up
- 10-15 min theory + worked example
- 20 min guided / semi-guided lab
- 15 min independent challenge
- 5 min explain-back + exit ticket

## Interleaving

Do not only alternate courses randomly.

Interleave concepts that force discrimination, for example:

- index seek vs scan
- optimistic vs pessimistic concurrency
- BFS vs Dijkstra vs A*
- confidence interval vs prediction interval
- precision vs recall vs ROC-AUC
- concurrency vs parallelism
- retry vs circuit breaker

## Productive Failure

For suitable topics, let the learner attempt a plausible but incomplete solution before teaching the canonical approach.

Do not let failure become aimless. Time-box it and debrief explicitly.

## Mastery Signals

Strong evidence of learning:

- can solve a novel variation
- can predict system behavior
- can explain trade-offs
- can debug a broken example
- can choose between alternatives and justify the choice
- can connect the concept to a different course / domain

Weak evidence:

- recognizes terminology
- copies a sample
- follows a step list without explanation
- answers only the exact example previously shown
