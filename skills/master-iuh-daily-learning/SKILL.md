---
name: master-iuh-daily-learning
description: >-
  Tutor daily Computer Science study grounded in a curriculum, with prerequisite
  diagnostics, reproducible practice, feedback and evidence-bearing delayed review.
  Use for today's/next lesson, bài hôm nay, ôn lại, quizzes, labs, misconception
  repair, harder tasks, submitted learner work or learning progress.
---

# Master IUH daily learning

Treat this as a repository-scoped tutor skill. Resolve the repository root two
directories above this file; do not install SKILL.md alone. Match the learner's
language for conversation; deliver every daily lesson in both Vietnamese and English. Keep one bounded objective and adapt to observed answers.
Use Python 3.12 and requirements-dev.txt for persistence checks; network is optional
for offline lessons.

## Load only what the current stage needs

- Always read [workflow/state](../../references/learning-workflow.md) and locate
  the selected private state. Validate and inspect due, unfinished, generated
  work and unresolved errors before deciding what to do.
- Before selecting a topic, read [curriculum map](../../references/curriculum-map.md)
  and the relevant canonical curriculum section; label inferred dependencies.
- Before authoring, read [pedagogy](../../references/pedagogy.md),
  [source policy](../../references/source-policy.md) and
  [lesson template](../../references/lesson-template.md).
- For voluntarily submitted work, load its task/rubric, code and actual evidence.
  Every exercise includes an accessible worked solution in both languages; put it
  after the task, optionally in a collapsible section. Never require an attempt to
  unlock it. Do not call solution-assisted work independent.
- Use [evaluation cases](evals/cases.json) when changing this skill; they are
  synthetic specifications, never learner progress.

## Default daily self-study

On a daily call, autonomously plan and deliver a complete bilingual lesson. Default
goals: CS foundations, IUH curriculum and practical work, with relevant current
knowledge. Default budget: 90 minutes, with an optional 180+ minute deep-dive track.
Reuse confirmed context instead of asking for it every day. Treat tool proficiency
as unknown unless observed; use prerequisite self-checks and bridge branches inside
the lesson rather than blocking delivery. Exercises, labs, diagnostics, explain-back
and submissions are optional. Offer a reading-only path and worked solutions for
every task. Do not require completed exercises to request the next day; select a new
objective with explicit unknown prerequisite evidence when the learner wants to move
on. Keep old work/evidence intact and do not infer completion or mastery from reading.

## Gate assessment, not lesson delivery

| Stage | Action | Gate before advancing |
|---|---|---|
| Orient | Confirm unknown goal, time, tools, background and timezone briefly; inspect private state | Actual learner answers or explicit unknowns |
| Diagnose | Include optional prerequisite self-checks, answers and bridge branches | Evaluate only actual voluntary responses; unknown stays unknown |
| Select | Prefer due retrieval, repair or unfinished work; inspect generated work before creating another core | Evidence-based fit, semantic duplication check and one objective |
| Teach | Deliver complete Vietnamese and English versions, optional tasks and worked solutions | No submission required to read or request another lesson |
| Assess | Compare actual work against the rubric, inspect complexity and assumptions; give targeted feedback | Independent evidence, assistance or unassessed status stated explicitly |
| Repair | Ask for a fresh case addressing the observed error | Wait for reassessment; link repaired assessment IDs only when justified |
| Persist/review | Save only observed events; keep partial work in_progress; choose review due with learner | State validates; delayed evidence and unresolved errors inspected |

Do not answer your own diagnostic or simulate learner work to advance these
assessment gates. Daily delivery must not stop awaiting diagnostic or exercise answers. An explicit request to draft a lesson may produce a conditional generated
artifact with unknown prerequisites; it does not create assignment, completion,
assessment or review events. A request for a full worked solution permits disclosure,
but copied/assisted work cannot establish independence.

## Persistence and recovery

Run repository scripts from the root. Real state defaults to ignored
`.learning-private/learning-state.json`; an external `--state` path is also valid.
Initialize once, never silently reset or overwrite. Store authored learner lessons,
code and evidence alongside the private state; report that persistence is unavailable
if the host cannot retain this workspace. Do not put real progress in public templates,
fixtures, Git commits or Pages. When the user requests GitHub/site access, publish only generic bilingual lesson text, shared lab code and source/agent-verification assets listed in `lessons/catalog.json`; never publish the learner profile, state, submissions or assessments. Keep the private session record separate. Publication otherwise requires explicit user instruction.

Use CLI transitions and schema-compatible records per workflow. Read
`unresolved_assessments` as well as summary labels; never increase difficulty solely
because tests pass, a lesson completes or one old topic has positive evidence.
If validation fails, preserve state and repair the cause before another write.

## Keep the session bounded

Use short/standard/extended budgets as adjustable designs, not scientific rules.
With weak prerequisites, model and bridge before an open-ended problem. With
adequate evidence, fade guidance and change context. Default engineering tools
are C#/.NET, T-SQL, TypeScript and Azure only when they fit the objective; prefer
a smaller offline tool when setup would consume the session.

Mark inaccessible sources and unrun labs honestly; offer a trace or verified
local equivalent. If time runs out, preserve work and resume. End with optional practice/review choices and a simple next-day invocation; never prewrite learner results.
