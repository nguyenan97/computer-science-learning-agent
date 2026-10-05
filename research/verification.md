# Verification and remaining limitations

Checked locally **2026-10-05**, Python **3.12.14**, jsonschema **4.26.0**. No deployment/publication, learner assessment or upstream CPython build was performed. The real state remains empty; sample record is generated outside it; synthetic low-result data is marked `fixture:true`.

## Results

| Check | Result / scope |
|---|---|
| `python scripts/generate_curriculum_map.py --check` | English/Vietnamese maps unchanged and up to date; generated files were not manually edited |
| `python scripts/validate_docs_navigation.py` | Bilingual Docsify route mirrors and navbar/hash-routing contract pass |
| `python scripts/learning_state.py validate` | Empty canonical version-1 state valid, no invented progress |
| `python scripts/learning_state.py plan` | Diagnostic action, no due reviews, no pending work, unknown time budget |
| `python scripts/validate_learning.py` | Real/fixture isolation, schema/semantic invariants, contract versions, sample sections, pinned targets/artifact paths and local Markdown links pass |
| `python -m unittest discover -s tests -v` | 14 behavioral tests pass; synthetic only, including lifecycle/CLI rejection, delayed evidence and review history |
| `python check.py --module mentor/solution.py --stage all` in lab | 3 tests pass: 1,260 small sorted-multiset/target cases, 18 large/access-budget cases and independent half-open-window cases; tests also check input preservation and reject slicing in the counted search |
| `python observe.py` in lab | n=8/1024/65536: insertion indices 4/512/32768 and element reads 3/10/16; duplicate target index=1, missing target index=3 |
| Pinned-source content | Four CPython source/test/doc/license downloads at resolved SHA match hashes of read release files |

The starter intentionally contains TODO/NotImplementedError. Mentor-solution verification proves the reference exercise is runnable; it cannot establish learner success. The observer counts element accesses, not time or production speedup. No CI run on GitHub is claimed; the new workflow contains the same local gates and existing workflows remain present.

## Required scenario coverage

| Scenario | Observed expected behavior in synthetic tests |
|---|---|
| New learner / no history | Diagnostic, no inferred expertise/mastery |
| Assigned but not attempted | Resume; status cannot jump to completed; mastery unknown |
| Weak prerequisite | Bridge and recheck rather than new core topic |
| Overdue review | Remains due until evidence-bearing review; old scheduled date preserved; next date must follow observation |
| Low result | Completion permitted with real practice evidence, but remediation recommended and mastery not awarded |
| Independent learner ready for more | Same-day evidence provisional; later unaided recall plus transfer supports deeper variation; newer failed/partial evidence can reduce confidence |
| Inaccessible source / cannot run lab | Fallback flagged; offline trace/local equivalent or deferral, limitations retained; no fabricated execution |

Extra negative checks reject fixture-as-real state, missing reciprocal assessment links, completion without practice, scores lacking a basis, hinted work labelled independent, duplicate core IDs and inconsistent review history. The CLI smoke test validates add/assign/start/evidence/complete/review/reschedule on a temporary fixture; a rejected completion leaves the saved bytes unchanged. Planning as of an earlier date excludes future assessment evidence.

## Limits and follow-up

- **Primary learning-science papers were inaccessible through the restricted proxy.** Twelve DOI candidates were attempted and logged unavailable. The accessible Deans for Impact PDF and Carpentries teaching sections were directly read, but this is not independent full-text verification of those meta-analyses. Productive-failure/mastery guidance is provisional. Follow the source log to complete scholarly verification with authorized access; no precision effect claims were added.
- GitHub API was inaccessible. Stars/archived/default-branch SHA and latest observed commit time were read from GitHub HTML/commit pages. Historical release pin and raw content were verified; no newest-release/support assertion or quantified downstream-adoption study was made.
- Schema/evidence checks cannot prove that a human actually authored an artifact or that a rubric judgment is correct. Semantic duplication and translation meaning require tutor/reviewer judgment; version checks detect structural drift only.
- Dates have day granularity; same-day review ordering is not modeled. A later day is only a minimum delay, not proof of long-term mastery. There is no validated psychometric model, automatic decay or universally optimal review scheduler. Human judgment chooses intervals with explicit reasons.
- Local state uses atomic replacement and one writer; concurrent edits need coordination. History is append-oriented through the CLI, but manual editing remains possible. Preserve learner artifacts/revisions and review history when editing records.
- No original curriculum PDF, live IUH regulations, interactive browser rendering, cloud/SQL/.NET lab or upstream CPython test suite was verified. The sample is deliberately a standard-library Python equivalent; docs distinguish this from an upstream build.

Daily usage: ask for a time-bounded lesson → validate/read state and due work → diagnostic → choose/research one objective or repair/review → predict/run/explain lab → submit independent artifact and feedback → persist observed lifecycle/evidence → choose/reassess delayed review. See [workflow](../references/learning-workflow.md) and [sample](../lessons/boundary-search/lesson.md).
