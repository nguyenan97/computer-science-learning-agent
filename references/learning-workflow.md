<!-- contract-version: 3 -->
# Daily workflow and private state

This owns selection, lifecycle, evidence, review and persistence. [Pedagogy](pedagogy.md)
owns instruction, [source policy](source-policy.md) owns research and
[lesson template](lesson-template.md) owns output. The [skill](../skills/master-iuh-daily-learning/SKILL.md)
implements interaction gates. English owns policy; Vietnamese translates the same contract.

## Start and select

1. Locate the learner's private workspace and validate its state. Inspect due reviews,
   unfinished assigned work, generated drafts and unresolved assessment IDs.
2. Ask for unknown goal/time/background/tools/timezone. Empty history means unknown
   skill. Include 2–3 optional prerequisite self-checks with answers and bridge branches; do not block daily lesson delivery. Save only actual voluntary responses.
   Diagnostic may be a remediation session linked to the intended topic; do not invent
   previous completion. If only a draft is requested, mark prerequisite fit conditional.
3. Offer due retrieval within the time budget. Weak prerequisite → bridge/recheck;
   assigned/in_progress → resume; generated → inspect and deliver only when appropriate.
   An unresolved error takes priority over increasing difficulty. Opening content does
   not clear due work.
4. Compare a few curriculum objectives by readiness, goal fit, continuity and practical
   value. Label official relationships versus inferred instructional sequencing. Check
   IDs and objective/concepts against all core work, including generated drafts.
   Review/remediation name related topics; deepening needs a changed objective.
5. Research the smallest relevant source set and implementation slice. Use short
   (~25), standard (~55) or extended (~85 minute) budgets, trimmed to actual time.
   Offer optional independent attempts and feedback; split setup/extra reading.

`plan` is advisory, not a curriculum selector or prerequisite certificate.
`--prerequisite ready/weak` must reflect observed diagnostic evidence.
Inspect topic-level unresolved errors even for prerequisite topics that lack a completed lesson.
An old positive topic never certifies readiness for another objective.

## Private storage and first use

The only active state defaults to **.learning-private/learning-state.json** (ignored
by Git), or a selected external `--state` path. Keep authored learner lessons, code
and evidence under that state's parent, using artifact paths relative to it.
The public [example](../state/learning-state.example.json) is an empty initialization
template, not learner progress. Public ledgers are pointers. Never commit real state
or artifacts to a public repository: excluding them from Pages alone is insufficient.
Use a durable private workspace with one writer; atomic replacement does not implement
concurrent-agent locking or backups. Never claim persistence if the host loses files.

From repository root (Python 3.12):

```bash
python -m pip install -r requirements-dev.txt
python scripts/learning_state.py init
python scripts/learning_state.py validate
python scripts/learning_state.py plan
# Set only values actually supplied by the learner:
python scripts/learning_state.py profile --minutes 25 --goal 'Goal stated by learner'
python scripts/learning_state.py add lessons /tmp/generated-lesson.json
python scripts/learning_state.py transition session-id assigned
python scripts/learning_state.py transition session-id in_progress
python scripts/learning_state.py add assessments /tmp/observed-assessment.json
python scripts/learning_state.py transition session-id completed
python scripts/learning_state.py add reviews /tmp/review-prompt.json
python scripts/learning_state.py review review-id assessment-id --next-due YYYY-MM-DD --reason 'Observed evidence and retention goal'
```

Place global `--state /private/path/learning-state.json` before the subcommand to
select another learner workspace. `init` never overwrites an existing destination.
For v1: `python scripts/learning_state.py migrate --from-state /private/old-v1.json`.
Migration writes a fresh v2 destination, preserves the source and all evidence, and
adds empty repair links; it never invents that previous errors were repaired.
For real v1 lessons, also supply `--artifact-root /original/repository-or-workspace`;
lesson files are copied without overwriting. Preserve referenced code/output revisions
alongside them and verify evidence references before resuming; free-text evidence links
are not rewritten automatically.
Do not delete legacy evidence after migration until its contents have been checked.

## Schema version 2 and event meaning

[Schema](../state/learning-state.schema.json) owns fields/types.

| Collection | Meaning |
|---|---|
| learner | timezone, minutes, goals, background; empty/null means unknown |
| lessons | unique session, stable topic/course/objective/concepts, prerequisites, related topics, private artifact path, review hooks and constraints |
| lifecycle | generated: artifact exists; assigned: delivered/accepted; in_progress: actual attempt; completed: agreed work finished with observed practice/retrieval/transfer/prerequisite evidence. Errors or unassessed work can coexist with completion |
| assessments | actual response/code revision/output/trace, assessor, date, outcome, nullable score/basis, hints, misconceptions, explanation, feedback and next action; resolves_assessment_ids explicitly links repaired needs_support observations |
| reviews | completed source lesson, prompt, initial/current due and append-only attempts; each keeps assessment ID, previous scheduled date, next due and rationale |

Preserve responses verbatim or cite an immutable artifact revision. Agent test runs
are not learner attempts. Unknown results stay unassessed/null. Numeric scores need
a rubric basis. Hinted/copied work is not independent. Save changed-context work as
transfer only when its task truly changes the context.

Dates use learner timezone. Assessment array order breaks ties within a day; append
new observations and never reorder old ones. Same-day correction is allowed but does
not establish delayed retention. Review observations must follow source completion;
next due may equal observation date for an immediate retry, keeping the item due.
Keep retry attempts in order and record early/late scheduling decisions honestly.

## Evidence and repair

Every needs_support observation remains unresolved until a later independent,
non-exit assessment on the same topic explicitly lists it in resolves_assessment_ids.
Tutor must establish that the new task addresses the same error with a fresh case;
same-topic linkage alone cannot prove relevance. Unrelated exit answers, partial work,
or absence of a new error do not resolve it. Retain both original and repair evidence.

The summary is conservative and scoped: unknown → developing/needs_remediation →
provisional independent practice → retained_and_transferred when independent recall
and transfer occur after completion, with no unresolved errors. Read actual interval,
difficulty, explanation and hints. One later date is only minimum observable delay,
not a scientifically sufficient retention horizon. `plan --on YYYY-MM-DD` projects
recorded lifecycle/review events through that date; it is not a full historical audit
of profile edits or when a review was originally created.

## Feedback, scheduling and recovery

Give feedback after a real attempt, identify knowledge/model/execution/tool/trade-off
gaps and request correction plus a fresh case. Schedule reviews after completion;
for partial sessions preserve assessments/next_action and resume without inventing
completion. Failure → correction and an earlier retry; assisted recall → shorter or
maintained gap; independent delayed recall/transfer → consider a longer gap according
to the retention goal. No universal fixed offsets or fabricated missed attempts.

Fixtures require explicit `fixture:true`, `--allow-fixture` and a separate path;
they never enter real progress. Sample artifacts remain public design examples.
Inaccessible source → mark status/use verified stable material/defer. Unrun lab →
paper trace or local equivalent with limits. Time exhausted → keep in_progress.
Invalid state → preserve it and repair with evidence intact; never silently reset.

## Optional self-study and continuity

Default daily delivery is complete Vietnamese and English lessons, 90 minutes plus optional 180+ minute depth. Exercises and submissions are optional, with worked solutions accessible immediately. If the learner requests the next lesson without attempting the previous one, preserve its status and unknown mastery; do not treat planner resume/review advice as a lock. Record delivery only when actually delivered. Keep one record per bilingual session. Do not mark completion, schedule evidence-based review or resolve errors solely because content/answers were read. Record an assessment only for actual voluntarily supplied evidence.

## Public lesson access

When publication is requested, copy only generic lesson content to `lessons/<lesson-id>/lesson.md` and its Vietnamese mirror under `vi/lessons/`. Put shared runnable code in `labs/`; list approved files in `lessons/catalog.json` for Pages staging. Adjust links/commands to public paths and keep personal profile/state/submissions/assessments out. Publishing a lesson is not learner completion and creates no assessment.
