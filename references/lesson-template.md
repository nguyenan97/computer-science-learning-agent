<!-- contract-version: 3 -->
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

Make practice optional. Transfer to a changed requirement/context and include a full worked solution after every exercise, including self-checks and exit questions. Keep task and answer visually separate, optionally collapsed, but accessible without submission. Assessment is optional; use a fresh unseen task for any later independence claim. Rubric maps directly to outcomes; capture evidence, independence, errors, explanation and corrective feedback. Ask explain-back and exit-ticket questions, including a new-context question.

## Sources and review hooks

For each source: role, contribution, URL/pin, checked date and status/limits. Define later recall and transfer prompts. Choose due dates **after actual completion/attempt evidence** using workflow; proposed hooks are not performed reviews.

## Record artifact

A separate schema-compatible generated lesson JSON; it records design, not results. All future lifecycle dates null, assessment_ids empty. No score, mastery or actual review event is created by lesson generation. On delivery/attempt/completion persist only observed lifecycle events via workflow. See the [sample](../lessons/boundary-search/lesson.md).

Suggested mode budgets (design heuristics): short 25 = 3 check + 6 model/example + 10 lab + 4 independent + 2 exit; standard 55 = 5 check + 10 model/example + 20 lab + 10 independent + 5 repo + 5 feedback/exit; extended 85 adds 15 deeper transfer and 15 source/experiment. If setup alone exceeds the budget, use an offline trace or split the session.

Store learner-specific artifacts relative to the private state directory, not in public `lessons/`. Deliver a complete lesson without waiting for diagnostic/task responses. Use conditional prerequisite branches; wait for real responses only when assessment is requested.

## Daily bilingual delivery

Provide complete Vietnamese and English versions with the same objectives, examples, commands, optional exercises, worked answers and sources. Store paired private artifacts (`lesson.vi.md`, `lesson.en.md`) for one session/topic; do not create two progress records. Default 90 minutes plus an optional 180+ minute deep-dive track; budgets apply to one language path, not reading both translations. Include a reading-only path. Exercises and submission are optional and never unlock the next lesson.
