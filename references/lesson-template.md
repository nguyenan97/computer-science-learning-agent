<!-- contract-version: 1 -->
# Lesson template

This owns lesson structure. [Workflow](learning-workflow.md) owns selection/state; [pedagogy](pedagogy.md) owns instruction; [source policy](source-policy.md) owns evidence. Adapt section length to available time rather than copying a long form every day.

## Header and selection

Session ID, topic ID, course code and curriculum section; type core/review/remediation/deepening; status generated. State why next, prerequisites and actual diagnostic evidence/unknowns, due-review choice and semantic-duplication check. List 2–4 measurable outcomes, time mode and environment constraints.

## Retrieval and prerequisite check

No-notes recall from due/previous material; for no history use a diagnostic, without assuming earlier knowledge. Include a short observable prerequisite task and branching instructions: ready → proceed; weak → bridge/recheck; unknown → gather evidence.

## Problem, foundation and current connection

Concrete motivating problem and prediction. Minimum mental model with assumptions/invariant; clearly label curriculum, foundational theory, current version-specific guidance and instructor synthesis. Include only directly relevant updates, with checked date and uncertainty. One worked example narrates decisions.

## Guided lab

Objective and prerequisites; OS/runtime/tool versions, dependency/data versions, deterministic starter/setup commands, working directory and fallback. Each numbered step has a purpose, prediction before run, expected observable checkpoint, self-check and explain-after prompt. Include common errors and a debug path. Prefer local reproducibility; do not add infrastructure for its own sake.

## Repository activity

A dated source dossier following source policy, or a reason to omit GitHub. Pin precise targets. Ask learner to infer behavior from tests, trace code or compare trade-offs. State upstream build versus local-equivalent verification separately.

## Independent challenge and feedback

Transfer to a changed requirement/context without full solution in the handout. Provide separately gated hints and mentor solution. Rubric maps directly to outcomes; capture evidence, independence, errors, explanation and corrective feedback. Ask explain-back and exit-ticket questions, including a new-context question.

## Sources and review hooks

For each source: role, contribution, URL/pin, checked date and status/limits. Define later recall and transfer prompts. Choose due dates **after actual completion/attempt evidence** using workflow; proposed hooks are not performed reviews.

## Record artifact

A separate schema-compatible generated lesson JSON; it records design, not results. All future lifecycle dates null, assessment_ids empty. No score, mastery or actual review event is created by lesson generation. On delivery/attempt/completion persist only observed lifecycle events via workflow. See the [sample](../lessons/boundary-search/lesson.md).

Suggested mode budgets (design heuristics): short 25 = 3 check + 6 model/example + 10 lab + 4 independent + 2 exit; standard 55 = 5 check + 10 model/example + 20 lab + 10 independent + 5 repo + 5 feedback/exit; extended 85 adds 15 deeper transfer and 15 source/experiment. If setup alone exceeds the budget, use an offline trace or split the session.
