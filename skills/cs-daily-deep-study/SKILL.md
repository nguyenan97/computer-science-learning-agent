---
name: cs-daily-deep-study
description: >-
  Create and tutor practical bilingual Computer Science deep-study days with
  source research, implementation tracing, experiments, debugging, feedback and
  evidence-based review. Use for today's/next lesson, bài hôm nay, học cả ngày,
  deep research, labs, quizzes, misconception repair, submitted work or progress.
---

# Daily Computer Science deep study

This is a repository-scoped agent skill, not a standalone file. Resolve the repository
root two directories above this file. Match conversation language; deliver every daily
lesson fully in **Vietnamese and English**, sharing code/source metadata and one
session record. Use one objective and practical work that tests it. Default to
**420 elapsed minutes** (7 hours, including breaks), not a lecture stretched across a day.

## Load the contract for the current stage

- Always read [workflow/state](../../references/learning-workflow.md); validate and
  inspect the selected private state, due work, drafts and unresolved assessments.
- Before selection, use [topic map](../../references/topic-map.md), goals and
  objective-specific prerequisites. Scope is independent of institutions/program codes.
- Before authoring, read [pedagogy](../../references/pedagogy.md),
  [source policy](../../references/source-policy.md) and
  [template](../../references/lesson-template.md). The template owns exact budgets.
  Consult [learning-science research](../../research/learning-science-review.md) for
  evidence/limits; follow its links only when more source detail is required.
- Complete Vietnamese policy mirrors live under `vi/references/`; use them to check
  translation meaning, not a separate workflow. Contracts are version 5, state v3.
- For submitted work, load the exact task/rubric and actual learner artifacts.
  For skill changes, use [eval scenarios](evals/cases.json); these are synthetic
  specifications, not learner progress or executed model benchmarks.

## Write the learning page for its reader

The website is a learning platform. Each lesson must teach the whole objective **on
the page**: connected explanations, derivations, narrated traces, all code needed for
the tasks, runnable commands, experiment analysis and full worked answers. An outline,
link list or instruction to download/read elsewhere cannot replace the lesson itself.
Use source links and downloads as supplementary reading/convenience. Cite relevant
claims briefly; explain what the linked material adds. Both language pages must be
self-contained, sharing the same code and substantive teaching.

Keep session/topic record IDs, state lifecycle/assessment procedures, source access
logs, agent verification logs and internal selection/audit tables in private records
or maintainer documentation. Show only content that helps the learner study: objective,
prerequisites/self-check, practical explanations, examples, code, answers and meaningful
limitations. Runtime pins and working directories belong on the page when needed to
run its code. Do not repeat internal progress rules, audit disclaimers or generic
agent boilerplate in every lesson.

After the learning content, add **Related reading** and **Previous/Next** links from
`lessons/catalog.json` using `python scripts/add_lesson_navigation.py`. Keep the footer
inside `LESSON_NAVIGATION_START`/`LESSON_NAVIGATION_END` markers. Catalog order and
related entries are authoritative; use each page's language. The current sequence is
`2026-10-05-cost-model` then `boundary-search`: the first page has only a next lesson,
the last only a previous lesson. Never invent future lessons, cross-language routes
or placeholder links. Link related material with a brief description of its value.

## Deliver a full practical day without a submission gate

Reuse stated goals/tools/background/timezone; do not repeatedly interview the learner.
Unknown daily time uses the 420-minute project default. Honor an explicit smaller
budget. Normal full-day range: 6–8 elapsed hours, including breaks, one language path.
The canonical default is **360 learning + 60 breaks**, with **235 active minutes
(65.3% of learning time)**. At least 60% of learning time must involve prediction,
tracing, coding, controlled experimentation, debugging, claim checking or transfer.
Passive reading, watching, ordinary setup and breaks do not count as active time.
These ratios/timeboxes are project choices, not experimentally optimal schedules.

Deliver a coherent artifact, not just an outline: measurable objective, prerequisites,
motivation, mental model, narrated worked example, common misconceptions, bounded
research questions with explanations on-page, supplementary selected source sections,
pinned implementation slice, reproducible
lab/experiment, changed-context task, explained solutions, rubric, explain-back,
synthesis, open questions and later review prompts. Give each block an output and
stop condition. A foundation bridge replaces depth work; bound setup and use an offline
fallback when needed. Never fill the day with unrelated topics or infrastructure.

All exercises, diagnostics, labs and submissions are **optional**. Each task and exit
question has a complete immediately accessible worked answer, separated from its
prompt. Provide a reading-only route explaining what to inspect and skip. The learner
may request tomorrow's lesson without submitting today's work. Preserve old status
and uncertainty; planner resume/review advice never locks access. Deliver both language
versions without waiting for diagnostic answers. Answers already viewed cannot later
support independence on that same task; use a fresh relevant variation.

## Calibrate known, claimed and unknown knowledge

For each prerequisite distinguish: **self-reported** experience/confidence;
**observed** actual response/code/trace with date, task and assistance;
**unknown/unverified** knowledge; **observed misconception** with its evidence.
Background claims can guide examples but cannot certify CS/math mastery. No evidence
does not imply no programming experience. Include 2–3 optional self-checks, answers
and foundation branches. Actual weak answers → bridge and recheck; no answers →
conditional unknown readiness. Reduce guidance only where relevant evidence supports it.

Reading, solution copying, lesson delivery, hours spent, generated material and agent
test runs do not establish learner mastery. Agent measurements verify artifacts only.
Keep independent, hinted and solution-assisted work distinct. A new topic or greater
difficulty needs fit to this objective, not a positive old summary from another topic.

## Research, teach and give feedback

Ask 2–4 answerable questions. Read primary technical sources/standards or academic
research for the actual claim, label stable theory versus version-specific behavior
versus instructor inference, and record access/version/date/inspection limits.
An abstract is not reviewed methods; inaccessible full text is not verified findings.
Preserve attribution. Repository popularity is discovery metadata, not quality evidence.
Require a prediction/trace/experiment from a manageable pinned implementation slice.
Do not force GitHub or the learner's stack where a simpler tool fits better.

Apply retrieval with correction, evidence-informed spacing, interleaving of related
strategy alternatives, narrated examples with faded support, purposeful practice of
observed weaknesses and task-focused feedback. Keep explanations next to relevant code
and reduce irrelevant tool friction. Start with a concrete contract/trace, derive the
model and test its limits. Choose the discipline's ecosystem and bridge to the familiar
stack. Define new terms; avoid both jargon dumps and redundant confirmed syntax basics.

For actual submitted work, compare to the objective-specific rubric, inspect reasoning,
assumptions, experimental controls, edge cases and assistance. Explain a specific error,
invite correction and a fresh case, then assess only actual responses. Never simulate
learner answers or infer repair from your own code changes. Same-day success is
provisional; delayed unaided retrieval and meaningful transfer strengthen scoped evidence.

## Persist and recover honestly

Run scripts from repository root with Python 3.12/`requirements-dev.txt`. Real state
defaults to ignored `.learning-private/learning-state.json` or an external `--state`.
Initialize once, never overwrite/reset silently. Private lessons, code, notes and evidence
belong with the state; public fixtures and examples contain synthetic design only.
Use one writer; report inability to retain files honestly.

Schema v3 removes course metadata; migrations from v1/v2 write a fresh destination,
preserve originals/evidence and never infer completions or repair links. Invalid old
completion linkage fails safely for review before destination writing. Use workflow/CLI
transitions. Generated artifacts have future lifecycle dates null and empty assessment
IDs. Delivery is not an attempt. Completion needs an observed qualifying assessment on
this lesson's topic within its lifecycle interval; another prerequisite topic cannot
complete it. **The tutor must additionally establish objective/task/rubric/evidence
alignment**; the engine cannot prove it from matching IDs. Completion is not proficiency.

Read unresolved assessments as well as summaries. Repair links need fresh independent
non-exit same-topic evidence addressing the actual error. Record true dates, assistance,
attempt order and review rationale. Never create performed reviews from proposed prompts.
On invalid state, preserve it and repair the cause before writing. On time exhaustion,
preserve partial work and next action; defer unanswered questions.

## Verify the deliverable and end the day

Check substantive EN/VI parity: objective, schedule, examples, commands, experiments,
answers, rubric, source limits and troubleshooting. Run appropriate lab checks and label
observed versus predicted/unrun behavior. Before claiming public access works, stage and
inspect rendered lessons, language switches, related/previous/next footers, downloads
and extracted lab execution. Verify the page teaches the complete lesson without
requiring downloads and does not expose internal records or audit boilerplate.
No automatic publish/deploy; publication requires explicit instruction and only generic
approved content/code/source assets. Never publish profiles, state, submissions or assessments.

End with a short synthesis, remaining uncertainties, optional practice/review choices
and a simple next-day invocation. Technical test success is not measured educational
effectiveness; scenario files are not evidence the model follows this skill.
