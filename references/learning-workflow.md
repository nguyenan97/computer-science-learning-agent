<!-- contract-version: 5 -->
# Daily workflow and private state

This owns selection, lifecycle, evidence, review and persistence. [Pedagogy](pedagogy.md), [source policy](source-policy.md) and [template](lesson-template.md) own instruction, research and output. The [skill](../skills/cs-daily-deep-study/SKILL.md) implements this workflow. English and Vietnamese carry the same contract version.

## Start and choose

1. Validate the selected private state; inspect due reviews, assigned/in-progress lessons, generated drafts and unresolved assessments. Preserve evidence.
2. Reuse stated goals, time, tools, professional background and timezone. Background/readiness self-reports are claims, separate from observed objective-specific evidence. Unknown stays unknown; absence of evidence does not imply no programming experience.
3. Include 2–3 optional prerequisite self-checks with worked answers and a foundation bridge. Actual relevant responses justify adaptation; no response permits conditional delivery without invented diagnostics. Old positive topics do not certify another objective.
4. Consider due retrieval, repair and unfinished work before greater difficulty. Reuse an appropriate draft. If a new day is requested without earlier completion, preserve its status and deliver a bounded objective with explicit unknowns. Planner advice is not an access lock.
5. Compare objectives in the [topic map](topic-map.md) by prerequisites, continuity, goals and practical value. Sequencing is project design. Check IDs and semantic overlap against all core work, including drafts. Deepening needs a changed objective; review/remediation identify related topics.
6. Research a small useful source set, then deliver the complete bilingual day. Default 420 elapsed minutes including breaks (360 learning, 235 active); honor smaller explicit budgets. A bridge replaces depth; setup has a stop condition; questions can move to later days.

`plan` reports evidence and advice. A readiness flag/profile is not a certificate. Inspect unresolved observations, including prerequisites with no completed source lesson.

## Learning page versus internal session

Deliver a narrated learning page with complete explanations, task code, experiments
and worked answers inline. Cite sources briefly; linked reading and downloads are
supplementary. Use the reader's practical questions to organize it. Keep selection
audits, session/topic record IDs, learner evidence tables, state transitions, source
access logs and assessment procedures in the private session or maintainer docs.
Do not turn internal workflow rules into repeated lesson boilerplate.

The public page ends with related reading and available previous/next lesson links
from `lessons/catalog.json`, rendered by `scripts/add_lesson_navigation.py` in the
footer markers described by the template. Preserve language and catalog order; no
invented next page. Navigation is content access, never a progress/assessment gate.
Internal evidence and privacy rules below remain fully enforced.

## Private storage and first use

State defaults to ignored **.learning-private/learning-state.json**, or an external `--state`. Keep lessons/code/source and experiment notes/evidence under that state's parent with relative artifact paths. The public [example](../state/learning-state.example.json) is empty initialization, not progress. Never commit personal state/artifacts or include them in Pages, fixtures or examples. Use one writer: atomic replacement is not locking or backup. Do not claim persistence when the host cannot retain files.

From repository root (Python 3.12):

```bash
python -m pip install -r requirements-dev.txt
python scripts/learning_state.py init
python scripts/learning_state.py validate
python scripts/learning_state.py plan
# Change only to values actually supplied by the learner:
python scripts/learning_state.py profile --minutes 420 --goal 'Goal stated by learner'
python scripts/learning_state.py add lessons /tmp/generated-lesson.json
python scripts/learning_state.py transition session-id assigned
python scripts/learning_state.py transition session-id in_progress
python scripts/learning_state.py add assessments /tmp/observed-assessment.json
python scripts/learning_state.py transition session-id completed
python scripts/learning_state.py add reviews /tmp/review-prompt.json
python scripts/learning_state.py review review-id assessment-id --next-due YYYY-MM-DD --reason 'Observed evidence and retention goal'
```

Global `--state /private/path/learning-state.json` goes before the subcommand. `init` never overwrites. Planning uses 420 minutes when time is unknown; this is not an invented preference.

## Schema v3 and migration

[Schema](../state/learning-state.schema.json) owns fields/types. V3 removes course metadata, retaining stable topic/session IDs and evidence.

| Collection | Meaning |
|---|---|
| learner | Timezone, stated minutes/goals/background; empty/null is unknown; self-report is not assessment |
| lessons | Session/topic, objective, concepts, prerequisites, related topics, private artifact, constraints, review hooks |
| lifecycle | generated: artifact exists; assigned: delivered/accepted; in_progress: actual attempt; completed: agreed objective-related work finished with qualifying evidence |
| assessments | Actual response/revision/output/trace, assessor/date/kind, nullable score/basis, assistance, errors, explanation, feedback, next action and repair links |
| reviews | Completed source, prompt, initial/current due and append-only actual attempts with assessment ID and rationale |

Completion needs referenced practice/retrieval/transfer/prerequisite evidence **on the lesson topic**, dated within its started/completed interval. Another prerequisite topic may be stored but cannot complete this objective. The engine checks structure; **the tutor must verify objective/task/rubric/evidence semantic alignment**. Matching IDs cannot prove alignment. Assisted work/needs_support may qualify as completed agreed work, never as independent proficiency. Exit-only responses, reading, agent runs and generated content cannot complete a lesson.

Migrate v1 or v2:

```bash
python scripts/learning_state.py --state /private/new-state.json migrate --from-state /private/old-state.json --artifact-root /original/workspace
```

Migration writes a fresh v3 destination, preserves source/evidence and copies lesson artifacts without overwriting. Keep v2 repair links; missing v1 links become empty, never inferred repairs. Preserve code/output revisions and verify free-text evidence links; they are not automatically rewritten. Invalid legacy completion links fail before destination writing. Inspect originals and correct only with justified private edits, or retain the source pending review; do not invent assessments, drop observations or delete legacy evidence. Retired metadata is removed only from the new state; the original remains an archive.

## Observe, assess and repair

Save responses verbatim or cite immutable revisions. Agent tests check artifacts, never learner attempts. Record assistance separately; unknown stays unassessed/null. Scores need rubric basis; solution-assisted work is not independent. Transfer needs meaningful changed context, not just a new input.

Dates use learner timezone. Append assessments without reordering; order breaks same-day ties. Each needs_support observation remains unresolved until a later independent non-exit same-topic assessment explicitly names it in `resolves_assessment_ids`. Verify the fresh task addresses the same error; matching topics or absence of another error cannot prove repair. Preserve both observations.

Summaries are scoped/conservative: unknown → developing/needs_remediation → provisional independent practice → retained_and_transferred when independent recall and transfer follow completion without unresolved errors. Read difficulty, actual delay, explanation and hints. Same-day repair is not delayed retention; one later date is minimum observable separation, not a scientific threshold. `plan --on YYYY-MM-DD` projects recorded lesson/review events, not a full history of profile edits or review creation.

## Schedule, continue and recover

After actual completion/attempt evidence, propose review prompts/dates according to retention goal. Record each real review, including failed/early/late attempts. Failure → correction/nearer check; assistance → maintained/shorter gap; delayed independent evidence → possibly longer gap. Intervals are design choices. Next due may equal observation date for immediate retry; review observations follow source completion.

Keep partial work in_progress with a next action. Reading, solution viewing, generation and publication do not create assessments/completion/repairs/performed reviews. Tasks/submissions are optional; EN/VI answers and reading-only route remain accessible. The next day needs no prior submission.

Fixtures need `fixture:true`, a separate path and `--allow-fixture`; never real progress. Mark failed source access/unrun labs with trace/local equivalents and limits. Preserve invalid state while repairing its cause. Publish only generic approved assets when explicitly requested; never automatically deploy or publish personal material.
