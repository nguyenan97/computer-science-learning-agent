# Runtime and skill design review

Checked 2026-10-05. Scope: repair concrete runtime defects and define an interactive,
repository-scoped tutor. [Source snapshot](runtime-source-checks.json) records fetched
bytes, dates, access status, hashes and limits. This is a targeted engineering review,
not a systematic learning-science review or an effectiveness experiment.

## Sources and decisions

- [Agent Skills specification](https://agentskills.io/specification): name/description,
  compatibility, focused instructions and progressive resource loading. Keep the skill
  concise; declare that its relative references require the complete repository.
- [Best practices](https://agentskills.io/skill-creation/best-practices) and
  [evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills):
  realistic edge cases, concrete assertions and comparison with a baseline. Add six
  evaluation specifications; do not report a model pass rate without executing them
  in isolated sessions and judging outputs.
- [OpenAI skill-creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md):
  clear triggers, reusable scripts/references, validation and iteration. Add optional
  OpenAI interface metadata; it is product-specific, not required by the base format.
  Online main-branch snapshots are recorded by hashes, not assumed immutable URLs.
- Pashler et al., [IES/WWC 2007 practice guide](https://ies.ed.gov/ncee/WWC/Docs/PracticeGuide/20072004.pdf):
  read the evidence table (printed p. 2) and recommendations on spacing, worked
  examples, retrieval, study allocation and explanations. The guide rates spacing
  and example/problem alternation moderate, retrieval re-exposure (5b) and deep
  explanation (7) strong, prequestions (5a) and allocation recommendations (6a/6b)
  low under its framework. It includes school/college settings and cautions about
  generalization and complex structured knowledge. Do not convert these labels into
  effect sizes or proof for graduate CS AI tutoring.

## Implementation rationale

Interaction gates separate authoring from learner evidence: orient → diagnose →
select → teach → assess → repair → persist/review. A draft-only request remains
conditional. Actual code/output/explanation is required before assessing a task;
showing a solution changes the independence claim. No model-generated learner events.

Unresolved needs_support observations need explicit later independent reassessment
links. This is a conservative engineering contract, not a validated mastery model.
The validator checks identity, topic, ordering and outcome; tutor still must judge
whether the fresh task really repairs the original error. Partial or unrelated exit
answers never clear the old error. Append order distinguishes same-day attempts;
true dates continue to distinguish retention delay. Immediate correction and later
retention are separate observations; no fixed universal schedule is imposed.

Private state defaults to an ignored workspace, with init/profile/v1 migration and
non-overwriting initialization. Public Pages packaging copies only documentation,
empty templates and a fixed sample. Ignoring files is not encryption or access control;
real data must not be force-added to a public repository. Local durability, backups
and one-writer discipline remain host responsibilities.

A seven-day synthetic CLI walkthrough tests state transitions and scheduling,
not whether a learner retained CS knowledge. Controlled repeated with/without-skill
model evaluations and real learner trials remain future work. No speed/token or
learning improvement numbers are inferred from this refactor.

Follow-up preference update: daily delivery now includes complete Vietnamese/English versions, optional exercises with accessible solutions, 90-minute default and optional 180+ minute depth. No submission gate for a new lesson. Assessment still requires actual evidence. Seven evaluation specifications are defined; no model benchmark claimed.
