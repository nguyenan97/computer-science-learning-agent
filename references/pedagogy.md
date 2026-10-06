<!-- contract-version: 5 -->
# Pedagogy for daily deep study

Teach durable recall, independent technical reasoning and changed-context transfer. The [research review](../research/learning-science-review.md) distinguishes examined evidence from project choices; [workflow](learning-workflow.md) owns progress. No method or daily schedule is best for every learner.

## Teach directly on the learning page

A lesson is a complete explanation, not a reading assignment or an agent report.
Narrate the problem, model, decisions, code and results in connected prose on-page.
Include the complete code needed for each task and full worked answers beside the
task. External sources and downloads supplement this material; they do not replace
essential explanations or solutions. Both language versions must teach independently.

Display the objective, prerequisites/self-check, useful examples, runnable commands,
troubleshooting, trade-offs and reflection. Keep internal session IDs, source-access
tables, state/assessment procedures and agent logs in private or maintainer records.
Avoid repeated policy boilerplate; expose uncertainty only where it changes how the
learner understands or uses a result. End with curated related reading and available
previous/next lessons, generated from the catalog as described in the [template](lesson-template.md).

## Know what is known

Separate four categories for each prerequisite and objective:

| Category | Meaning | Teaching decision |
|---|---|---|
| Self-reported | The learner describes experience, confidence or prior reading | Use relevant examples and avoid redundant syntax instruction; do not certify mastery |
| Observed evidence | Actual learner response/code/trace with task, date, context and assistance | Adapt only within the demonstrated scope; old evidence may be stale |
| Unknown / unverified | No relevant observation, or work performed only by the agent | Provide a self-check and foundation bridge; absence of evidence is not incompetence |
| Observed misconception | A specific incorrect model or recurring error supported by an actual response | Give targeted correction, then a fresh relevant case; preserve unresolved evidence |

A successful test run confirms the tested artifact under that environment. Reading, solution copying, lesson delivery, hours studied and agent verification do not establish learner proficiency. Capture independent, hinted and solution-assisted work honestly. Use a fresh unseen variation if an answer has already been shown.

## Instructional loop

Retrieve without notes → investigate a concrete contract → build a small mental model → examine a worked example → trace implementation → code and experiment → debug → transfer to a changed requirement → explain the result and limits → revisit after delay.

For an unfamiliar prerequisite, model the process before open exploration. With adequate evidence, start with a bounded prediction/attempt and debrief it. Integrate explanations beside relevant code/diagrams, then fade guidance. A difficult attempt without consolidation is not automatically productive learning.

Translate the learning-science principles into these activities:

- **Retrieval:** reconstruct an invariant, procedure or strategy without notes; compare with a worked answer and correct it. Recognition and rereading are different activities.
- **Spacing:** revisit actual attempts on later days, recording delay and assistance. Adapt to the retention goal and observations; fixed offsets are optional heuristics.
- **Interleaving:** after forming a model, mix related alternatives and ask which fits and why. Mixing unrelated topics is not a substitute for strategy discrimination.
- **Worked examples:** expose decisions, assumptions and a counterexample, then use completion tasks and fresh independent variations. Adjust scaffolding to relevant evidence.
- **Purposeful practice:** isolate an observed weak subskill, set a performance criterion, vary the case and use feedback. Ordinary coding or elapsed time alone does not satisfy the stronger research definition of deliberate practice.
- **Feedback:** after an actual attempt, name the mismatch between the task criterion and reasoning, give an actionable correction and invite a fresh case. Separate conceptual errors from setup/tool failures.
- **Cognitive load:** minimize irrelevant setup, introduce one model at a time, make checkpoints visible and use offline equivalents when tools dominate. Keep useful reasoning difficulty; lower reported effort alone is not better learning.

Use a concrete production contract and small trace before terminology. Derive the cost/model, connect it to implementation and identify where the simplified model stops. Choose the discipline's appropriate ecosystem and bridge to the familiar stack; do not add infrastructure merely to match a profile.

## A full day with more practice than exposition

Default: **420 elapsed minutes**, with **360 learning minutes and 60 break minutes**, for one language path. The normal range is 360–480 elapsed minutes (6–8 hours); honor a smaller explicit budget. The schedule and at least **60% active learning time** are project requirements, not experimentally established optima.

The canonical schedule is in the [template](lesson-template.md): 235 of 360 learning minutes are active (65.3%). Active time means predicting/tracing, implementing, designing or running a controlled experiment, debugging, checking a claim or solving a changed-context task. Passive reading, watching, ordinary setup and breaks do not count. Every block produces a concrete artifact or question; the budget includes setup and source access. Do not fill seven hours with exposition or label passive source reading as practice.

Use one main objective, supporting measurable outcomes and optional depth. Stop or switch to a fallback after bounded setup failure; defer secondary questions instead of adding unrelated objectives. Preserve partial work when time/energy runs out. The reading-only path explains what to read, inspect and skip, keeping worked answers accessible; its users may continue the next day without submissions or fabricated mastery.

## Rubrics, correction and review

Establish objective-specific criteria before tasks: correctness/edge cases, model/invariant, reproducibility/experimental controls, assumptions and trade-offs, independence, and changed-context transfer. Use qualitative judgments unless a numeric score has a documented basis. Same-day evidence is provisional; delayed retrieval and transfer strengthen only the assessed scope. A later calendar date is not a universally sufficient retention horizon.

Hints progress conceptual → structural → implementation-specific. Each optional exercise, diagnostic and exit question has a worked answer separated from its prompt. Submission never unlocks an answer or another lesson. Completion requires observed work relevant to this objective; the engine checks topic linkage, while the tutor must check task/rubric alignment. Keep completion separate from independent proficiency and durable mastery.

End with a synthesis artifact: revised mental model, tested claims, limitations, remaining questions and proposed later recall/transfer prompts. Proposed prompts are not performed reviews. Record assessments only for actual voluntary evidence.
