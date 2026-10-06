<!-- contract-version: 5 -->
# Full-day lesson template

This owns lesson structure and the daily budget. [Workflow](learning-workflow.md) owns state; [pedagogy](pedagogy.md) owns teaching; [source policy](source-policy.md) owns research. Deliver a complete Vietnamese lesson and complete English mirror with shared code and one internal bilingual session record. Budget one language path.

## A complete learning page

Write a connected explanation that teaches the objective entirely on-page. Include
the necessary foundations, narrated examples/traces, complete task code, copyable
commands, experiment interpretation and full worked answers. Sources, repositories
and downloadable labs supplement the lesson; they cannot replace its explanations,
code or solutions. Both EN and VI pages must be independently usable.

Only learner-useful material belongs in the lesson. Keep session/topic record IDs,
selection audits, source access/status tables, state/schema/assessment procedures
and agent logs in private records or maintainer docs. Use short citations and explain
uncertainty where it affects a result. Do not repeat internal rules or generic agent
boilerplate across lessons.

## Header, objective and readiness

On-page: a meaningful title, practical motivation, one main measurable objective,
2–4 supporting outcomes and concrete prerequisites. Use a short readiness self-check
to help the reader choose the foundation bridge or main path. Explain prerequisite
ideas inline; links to earlier lessons are optional refreshers.

In the private author/session record: session/topic IDs, lesson kind/status, selection
reason, semantic-duplication check and evidence separating self-report, observations,
unknown prerequisites and misconceptions. Do not render this audit in the lesson.

Provide a short self-check, worked answer and branches: relevant evidence → reduce redundant guidance; weak response → foundation bridge/recheck; no response → conditional bridge and unknown readiness. Deliver the lesson without waiting for answers.

## Full-day plan

Default 420 elapsed minutes (7 hours); adapt to 360–480 minutes or an explicit smaller budget. Include breaks/setup, one objective, concrete block outputs and stop conditions. At least 60% of learning minutes are active technical work; distinguish active time from passive reading/setup. These are project choices, not scientific optimal timings.

| Block | Elapsed minutes | Active minutes | Observable output |
|---|---:|---:|---|
| Orient, retrieve and prerequisite self-check | 20 | 10 | Prediction, recalled model, unknowns |
| Foundation, mental model and worked trace | 50 | 20 | Annotated trace, invariant and counterexample |
| Break | 10 | 0 | Rest |
| Read sources to answer research questions | 45 | 10 | Claim ledger and testable prediction |
| Inspect and trace implementation/tests | 45 | 40 | Code trace, predicted behavior, alternative |
| Lunch/rest | 30 | 0 | Rest |
| Guided implementation and debugging lab | 75 | 70 | Running artifact, cases, debugging notes |
| Break | 10 | 0 | Rest |
| Controlled experiment and result analysis | 45 | 40 | Measurements, controls, limits |
| Break | 10 | 0 | Rest |
| Changed-context transfer and defect repair | 35 | 35 | Fresh variation and justified trade-off |
| Synthesis, explain-back, self-assessment and review plan | 45 | 10 | Learning memo, remaining questions, future prompts |
| **Total** | **420** | **235** | **360 learning + 60 breaks; 65.3% active learning** |

Scale thoughtfully instead of multiplying all tasks blindly. A bridge replaces depth work rather than extending the day. Stop setup after a stated limit (default 15 minutes is a heuristic); use an offline trace/equivalent or defer. End a block at its timebox, preserve artifacts and carry questions forward.

## Problem, mental model and worked example

Start with a concrete technical contract and prediction. Explain the minimum foundation, assumptions, cost/model or invariant, narrated example, counterexample, common misconceptions and real application. Define new terms when introduced. Familiar programming context does not certify mathematical prerequisites.

## Research questions and source reading

Give 2–4 bounded questions and explain the relevant findings/models inline. Narrate
the reasoning and selected implementation slice, including task code and assumptions.
Show how to form a claim, predict a case and test it. Optional source reading names
the precise section and what deeper question it helps answer. Cite sources briefly;
keep access/version audits and repository dossiers in the author record. Explain
material limitations or contradictions in the narrative, without an audit table.

## Reproducible lab and experiment

List objective, prerequisites, OS/runtime/dependency/data pins, working directory,
commands, expected output and offline fallback. Provide the deterministic starter,
every essential task implementation and worked solution inline, with file names so
the reader can assemble/run them without downloading a ZIP. Downloads are convenient
copies. Explain each step's purpose, prediction, checkpoint, self-check and debug path.
Design and narrate an experiment with question/hypothesis, variable, controls,
cases/seed, measurement, result and limits. Distinguish conceptual, implementation
and environment errors. Keep agent verification logs outside the lesson.

## Transfer, worked answers and rubric

Change data/requirements/representation and explain why the task tests this objective. Every exercise, self-check and exit question has a full accessible worked answer immediately after the prompt or in a collapsible section. Trying first is optional; answers require no submission. Later independence assessment uses an unseen relevant variation if the answer was read.

Give learner-readable success criteria for correctness/edge cases, reasoning/invariant,
controls/reproducibility, explained trade-offs and transfer. Narrate likely errors,
targeted correction and a fresh case. Explain-back prompts cover mechanism,
assumptions, counterexample, discrepant results and where the model stops. Record
assistance and formal assessments privately; do not show state procedures on-page.

## Synthesis, uncertainty and next day

End with a memo template: previous → revised model; verified claims → evidence/limits; self-reported versus demonstrated versus unknown; open questions; stop/resume decision. Include later unaided reconstruction and changed-context prompts. Hooks are not performed reviews or mastery claims; schedule due dates from actual evidence using workflow.

Give an explicit reading-only route through model, worked traces, selected sources, lab explanation, solutions and synthesis. Hands-on work/submissions remain optional. The next day is accessible with no responses; preserve unknown completion/mastery.

## Bottom of the page: related reading and previous/next

After the learning synthesis, include **Related reading** followed by available
**Previous/Next** lessons. Generate this footer from `lessons/catalog.json` with
`python scripts/add_lesson_navigation.py`; keep its generated block between
`<!-- LESSON_NAVIGATION_START -->` and `<!-- LESSON_NAVIGATION_END -->`. Use curated
links with a short reason to read them. Keep EN links on EN pages and VI links on VI
pages. The catalog supplies order and related entries; never hard-code invented
future pages or append internal audit/state documents as learner recommendations.

Current order: `2026-10-05-cost-model` → `boundary-search`. The first lesson has a next
link only; the last has a previous link only. If catalog entries change, regenerate
both languages. A missing neighbor is omitted. Reading sources and downloads remain
supplementary; this footer does not gate access based on progress or submissions.

## Artifacts and quality check

Store private `lesson.vi.md` and `lesson.en.md` under the state parent. A schema-v3 generated record contains design only: future lifecycle dates null, empty assessment IDs and no course metadata. Share code/source metadata; compare outcomes, schedule, prompts, solutions, limits and troubleshooting for substantive parity.

Generic examples may live in `lessons/` and `vi/lessons/` with shared labs/catalog-approved downloads. Publication needs explicit instruction. Before claiming usability, check the complete inline lesson, generated related/previous/next footer, language switches, direct downloads and extracted-lab execution. Keep checks/logs and internal metadata in maintainer/private records; explain only limitations useful to the learner. The [full-day example](../lessons/2026-10-05-cost-model/lesson.md) illustrates this template; older short examples are not the daily default.
