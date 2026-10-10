# Flexible lesson scaffold

The [lesson spec](lesson-spec.md) is the authoring contract; this document supplies
prompts and a copyable shape. Use the planner's actual minutes and outputs from the
[profile](study-profile.json). Replace placeholders, translate meaning into full EN/VI
pages, and remove these maintainer instructions from the lesson. Split or combine
sections to serve the topic. Section numbers and identical paragraph shapes are optional.

## Plan before drafting

Run `python scripts/daily_plan.py --next` before catalog edits for the next lesson.
Note the chosen objective/day type, selected recall, inherited knowledge and new
foundation. Allocate each block to a concrete artifact. Bound setup and source reading;
keep a reading-only route. Put this allocation in scratch work, not an opening schedule.

## Copyable page shape

Use the title, language link and ZIP link, then a short concrete problem. State the
goal as something the learner can produce/check. Explain only the central ideas with
small examples; develop formal definitions later.

```markdown
## Recall and foundation bridge

**Recall · [planner minutes].** [Reconstruct the selected argument.] **Done when:** [Checkable output.]

1. [One selected recall question.]

<details>
<summary>Answer</summary>

[Reasoning, assumptions and a useful boundary case.]

</details>

2. [Next question, followed by its own details block.]

## Example, mechanism and argument

**Foundation · [planner minutes].** [Annotate a trace.] **Done when:** [Explain why each step is legal.]

[Concrete input and prediction prompt, then its own worked answer.]
[Define state/contract after the example. Explain mechanism, formula, correctness
argument and a counterexample. Say which prerequisite is being introduced now.]

Pause - [planner break minutes] away from the screen.

## Sources and project decision

**Source reading · [planner minutes].** [Read named sections.] **Done when:** [Claim/evidence/limit ledger.]

[A bounded source question, immediately followed by its answer.]

## Pinned implementation and real application

**Source analysis · [planner minutes].** [Trace one product decision.] **Done when:** [Separate verified code behavior from design inference.]

[Commit, file/functions, read range, product problem and trade-off.]
[Map to a project with an explicit boundary on unrun integration.]

Lunch - [planner minutes] to eat and rest.

## Lab or reproduction

**Lab · [planner minutes].** [Implement/check/repair.] **Done when:** [Oracle agreement and explained defect.]

[One concrete task, result/error contract, setup timebox and reading-only route.]

<details>
<summary>Answer - complete lab and results</summary>

[Pinned SDK/runtime/dependencies, working directory, all complete named files,
copyable commands, expected or observed output and scope of correctness checks.]

</details>

[One defect question. Follow it with its own answer rather than hide its prompt
inside the complete-lab answer.]

Pause - [planner minutes] away from the screen.

## Controlled experiment or comparison

**Experiment · [planner minutes].** [Vary one factor.] **Done when:** [Interpret one observation within its limits.]

[Assumptions, prediction, changed/fixed variables, workload and command.]
[Ask for a result or interpretation. Follow immediately with a closed answer
containing worked output, observed/inferred distinction and uncontrolled factors.]

Pause - [planner minutes] away from the screen.

## Transfer

**Transfer · [planner minutes].** [Change a consequential condition.] **Done when:** [New state/assumptions and independent check.]

[Change the unit, constraint, failure model or objective, not just variable names.]
[Give a complete worked solution in its own closed answer.]

## Synthesis and next question

**Synthesis · [planner minutes].** [Write a decision.] **Done when:** [Model, evidence, limits and next falsifying question.]

[Individual retrieval prompts with individual immediate answers.]
[Short revised model and what remains unknown. Cite reuse/licensing where relevant.]
```

Named runnable fences use the spec's `lab-file` marker adjacent to their opening
fence; examples and alternative transfer programs remain unmarked. The tooling
extracts file content, so it must be complete rather than `...` or a source link.

## Paper-day adaptation

Use the paper schedule rather than replacing its blocks with the build schedule.
Foundation supplies the minimum mathematics. Paper reading annotates actual
methods and claims; claim checking distinguishes evidence and alternative explanations.
After lunch, reproduction yields one derivation, table or runnable result with a stated
scope. Comparison challenges it with a baseline/counterexample/related paper. Synthesis
and writing yield a falsifiable next question and cited critique. Analytic reproduction
can be appropriate; say which executable reproduction was not run. Preserve answers,
reading-only access and break placement while changing the section purposes.

Before publishing, use the [maintainer review checklist](../docs/lesson-review.md).
