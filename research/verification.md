# Verification and remaining limitations

Runtime refactor checked locally **2026-10-05**, Python **3.12.14**, jsonschema
**4.26.0**, PyYAML **6.0.3**. All walkthroughs use synthetic data in temporary workspaces; no actual
learner history was created. These changes have not been pushed, merged or deployed.
The earlier main commit had successful GitHub checks and a Pages deployment; that
is separate from verification of this refactor.

## Current results

| Check | Result / scope |
|---|---|
| Curriculum generator --check | EN/VI maps unchanged and up to date |
| Docsify navigation | Route mirrors, navbar and hash routing pass |
| Learning validator | Empty public v2 template, fixture isolation, semantic checks, matching contract versions, skill metadata/eval identifiers, sample artifacts and local links pass; rejects tracked private workspace |
| Unittest discover | 27 behavioral tests pass, all synthetic |
| Reference lab --stage all | 4 tests pass, including partition/search budget, window edge cases, input preservation and logarithmic window access |
| Observer | n=8/1024/65536: indices 4/512/32768, reads 3/10/16; duplicate index 1, missing index 3 |
| OpenAI skill-creator quick_validate | Skill frontmatter/name/description valid; this is structural, not a model-behavior evaluation |
| Public-site builder | Stages public documentation/template/fixed sample; planted synthetic private state, legacy state and extra learner lesson excluded; symlink-based public inclusion rejected |
| Diff whitespace | git diff --check passes |

Regression tests cover: an unrelated developing exit cannot erase needs_support;
only valid explicit independent non-exit repair links resolve errors; unresolved
prerequisite topics remain visible without a completed lesson; generated drafts are
reused; lifecycle and review dates project through an earlier day; same-day failed
review/retry retains order and true dates; linear or mutating challenge implementations
are rejected; initialization never overwrites; invalid changes preserve file bytes;
real artifact paths cannot escape the workspace; v1 migration preserves original
bytes, keeps errors unresolved and copies lesson files from an explicit artifact root.

The seven-day synthetic CLI walkthrough executes generated → assigned → in_progress
→ practice → completed → scheduled review → failed recall → same-day repair → delayed
recall/transfer. It preserves three actual simulated review attempts and the original
scheduled date. This proves script interoperability for the scenario, not learning.

## Research and behavioral limits

The [runtime design review](runtime-design-review.md) and [source log](runtime-source-checks.json)
record Agent Skills/OpenAI engineering guidance and directly read IES/WWC practice-guide
sections. The earlier Deans for Impact/Carpentries source checks remain historical
records; inaccessible candidate primary papers are still not independently verified.
No effect size, universal spacing schedule, token saving or learner improvement is claimed.

Six [skill evaluation specifications](../skills/master-iuh-daily-learning/evals/cases.json)
cover cold start, interrupted drafts, contradictory evidence, same-day correction,
offline short sessions and draft-only requests. They have not been run as isolated
model trials against a baseline. Deterministic state tests do not prove tutor adherence.

Dates are day-granularity with append order within a day; no intra-day retention
interval is inferred. Plan projections are not a historical audit of profile changes
or review creation time. The evidence summary is a conservative heuristic, not a
validated psychometric model; tutor must assess repair relevance, difficulty,
explanation, independence and semantic duplication.

Private files are Git-ignored, not encrypted. Do not force-add learner data to a public
repository. One-writer coordination, durable storage and backups remain host tasks.
Migration preserves free-text evidence references without rewriting them; keep their
code/output revisions and check links before resuming.

Translation checks are structural; bilingual semantic review is still required.
Original curriculum PDFs/current IUH regulations, full upstream CPython tests,
SQL/.NET/cloud labs, interactive browser rendering and real learner retention were
not verified in this refactor. The starter remains intentionally unfinished, and
mentor solutions are separated by tutoring convention rather than access control.

Follow-up preference update: daily delivery now includes complete Vietnamese/English versions, optional exercises with accessible solutions, 90-minute default and optional 180+ minute depth. No submission gate for a new lesson. Assessment still requires actual evidence. Seven evaluation specifications are defined; no model benchmark claimed.

Public lesson follow-up: Lesson 01 is published in paired EN/VI paths with its shared lab and source/agent-check assets. Pages reads an explicit lesson catalog. Packaging tests now verify both public language versions, reject private catalog paths, and still exclude synthetic private markers. Personal session state is not included.
