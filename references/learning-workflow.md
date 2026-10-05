<!-- contract-version: 1 -->
# Daily workflow and state contract

This page owns selection, lifecycle, assessment, review scheduling and persistence. [Pedagogy](pedagogy.md) owns instructional design; [source policy](source-policy.md) owns research; [lesson template](lesson-template.md) owns the lesson output. The short [skill](../skills/master-iuh-daily-learning/SKILL.md) dispatches to these contracts. English owns policy; Vietnamese pages translate the same version. JSON schema owns field names/types; this page explains their meaning.

## Before authoring

1. Read and validate **state/learning-state.json**, the only learner state. Never read the translated ledger as a second history. Inspect pending assigned/in-progress work, completed objectives, evidence and all due/overdue reviews using the learner timezone.
2. If time, goal, background or tools are unknown, ask briefly. An empty ledger means unknown skill, not beginner or expert. Use 2–3 targeted prerequisite questions or a small task and save the actual answer/evidence. A diagnostic can be an in-progress remediation session linked to the intended topic; do not invent a prior completed lesson.
3. Offer due retrieval first, with a time budget. A due item stays due until attempted and assessed; opening a lesson never clears it. Use a review-only session when appropriate. A weak prerequisite triggers a bridge/recheck. Resume assigned work instead of producing a duplicate.
4. Select one next core objective from curriculum facts and the clearly labelled inferred dependencies. Compare a few useful candidates by readiness, goal fit, curriculum value, continuity and practical value. Record why this one won; no arbitrary score pretends to be scientific.
5. For every candidate compare topic ID **and objective/concepts** with generated, assigned and completed core work. The validator blocks identical core IDs; the tutor must check semantic equivalence. A tag overlap can flag a candidate, never automatically prove a duplicate. Review/remediation intentionally revisit and name `related_to`; deepening must specify a new or harder objective.
6. Research durable theory and directly relevant implementation guidance. Record the source roles and uncertainty. Technical lessons normally examine one useful repository; choose none when it would distract, with a reason. Research current facts at lesson time, without a fixed “update year.”
7. Choose short (~25 min), standard (~55 min) or extended (~85 min), then trim to available time. These are editable product defaults. Preserve an independent attempt and feedback; move extra source reading or transfer depth to another session. Never squeeze every section into a tiny day.

`python scripts/learning_state.py plan` returns advisory priorities; it neither chooses curriculum concepts nor certifies prerequisites. `--prerequisite ready/weak` is a tutor input grounded in an observed diagnostic, not automatic inference. Availability flags expose fallback planning, not source verification.

## Canonical state (schema version 1)

Use [schema](../state/learning-state.schema.json) and `python scripts/learning_state.py validate`. Python 3.12 and pinned development requirements are used in CI. Date-only records use `learner.timezone`; they do not distinguish attempts within one day. No database is needed.

| Collection / fields | Meaning |
|---|---|
| learner | timezone, time budget, goals, background; null/empty means not yet known |
| lessons | unique session `id`; stable `topic_id` (`course-slug.concept.depth`); course code, objective, concept tags, prerequisite topics; `kind` core/review/remediation/deepening; related topics; artifact path, review prompts, constraints |
| lifecycle | generated: artifact exists; assigned: explicitly delivered/accepted; in_progress: learner reports a real attempt; completed: learner finishes the agreed work, with observed task evidence (practice, retrieval, transfer or prerequisite work). Completion can include errors or unassessed work; it is never mastery |
| assessments | task and actual evidence (response, code path + revision, test output, trace); assessed_by; observed date; outcome needs_support/developing/independent/unassessed; nullable score/basis; hints actually used, misconceptions, nullable explanation quality; corrective feedback and next action |
| reviews | one ongoing prompt with source completed lesson, initial/current due date, and append-only attempts referencing assessed retrieval/transfer evidence; each attempt keeps scheduled_for, next_due_on and reason |

Leave missing results as null/unassessed. A rubric score needs an explicit basis; independent work cannot have used hints. Agent lab verification is **not** learner evidence. Save learner explanations verbatim or cite their artifact before evaluating them. `assessment.topic_id` can name a prerequisite; that assessment's lesson still names the real session in which it was observed. Save an independent new-context task as `transfer`, not merely a passing code test.

Mastery is derived by the script, never manually assigned: unknown → developing / needs_remediation → provisional independent practice → retained_and_transferred if later independent recall and transfer exist. These are **scoped evidence summaries and conservative design heuristics**, not psychometric estimates. A date later than completion is the minimum observable delay, not an adequate scientific retention horizon. Look at the actual interval, task, rubric and newest contradictory evidence; reassess if old positive evidence is no longer reliable.

## Safe local updates

Install checks with `python -m pip install -r requirements-dev.txt`. Tutor prepares a record using the schema, shows the lesson and records only events actually observed. The CLI validates before replacing the local JSON file atomically; one writer at a time (no concurrent-agent locking).

```bash
python scripts/learning_state.py validate
python scripts/learning_state.py plan
python scripts/learning_state.py add lessons /tmp/generated-lesson.json
python scripts/learning_state.py transition session-id assigned
python scripts/learning_state.py transition session-id in_progress
python scripts/learning_state.py add assessments /tmp/observed-assessment.json
python scripts/learning_state.py transition session-id completed
python scripts/learning_state.py add reviews /tmp/review-prompt.json
# After actual retrieval, add its assessment first, then:
python scripts/learning_state.py review review-id assessment-id --next-due YYYY-MM-DD --reason 'Observed recall; selected interval fits learner goal'
```

Generated records have all later lifecycle dates null. Assignment/completion are not automatic side effects of adding assessments. Record partial work even when the lesson cannot be completed. Reviews start after completion; for an abandoned/partial lesson use its assessment `next_action` and resume/repair rather than fabricating completed state. Only tutor/learner chooses dates based on evidence: failure → corrective explanation and earlier retry; partial/hinted recall → maintain/reduce gap; independent recall plus transfer → consider a longer gap. No automatic fixed offset, no retroactive backfilling of missed reviews. Add new attempts instead of overwriting history. Do not edit old evidence to improve a score.

Fixtures live under `tests/fixtures/`, explicitly `fixture: true`; CLI needs `--allow-fixture --state ...`. They never replace the canonical real state. The complete sample lesson's unassigned record is outside real state as well. Markdown ledgers are navigation pointers, not stored counters or progress mirrors.

## Feedback and fallback

Classify a gap as missing knowledge, wrong model, execution defect, tool/API misuse or unexamined trade-off. Give feedback tied to the error; ask for correction and a fresh attempt. Reduce scaffolding when independent delayed evidence supports it. Increase ambiguity/depth or move to a new prerequisite-safe objective; never increase difficulty merely because a lesson was completed.

If a source is inaccessible: mark unavailable, use an already verified pinned source for stable claims, or defer changing claims. If a lab cannot run: offer an offline trace/small equivalent, record the environmental limit and do not call it executed. If time runs out: keep in_progress; split the lab without awarding mastery. If the state is invalid: stop writing it and repair with evidence/history intact; do not silently reset progress.
