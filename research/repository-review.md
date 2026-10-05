# Repository review before refactor

Reviewed 2026-10-05, baseline commit `fd054f6`. Working tree was clean. No repository AGENTS.md was found. Read the skill, both curricula and translations, all references/ledgers, map generator, navigation validator, Docsify configuration and three CI workflows.

## Strengths

- Curriculum facts are canonical in English; the generator extracts explicit relationships and labels instructional synthesis separately. Preserve this boundary and the original curriculum years.
- The learning loop already emphasizes retrieval, practical exercises, explain-back, transfer and gradual hints.
- Source policy recognizes primary docs, theory, maintenance and implementation/tests rather than stars alone.
- Bilingual navigation and generated-map drift already have checks in CI.

## Gaps and consequences

| Before | Consequence | Change |
|---|---|---|
| Skill repeats source policy, pedagogy, output shape and fixed scoring gates | Multiple conflicting policy owners; long skill can drift | Slim dispatch skill; references own specific contracts |
| English and Vietnamese ledgers both call themselves canonical | Potential split history | One versioned JSON state; bilingual ledger pages are pointers |
| Append record at lesson generation; no lifecycle | Produced content can appear learned/completed | Generated → assigned → in_progress → completed; evidence required |
| Score is null but no assessment context/hints or review history | Cannot justify mastery or adapt reliably | Append assessment evidence, rubric basis, hints, misconceptions and review attempts |
| Review dates attached at generation | Dates are detached from attempts; overdue handling unspecified | Reviews follow completion, every rescheduling preserves prior due and observation |
| Default graduate skill assumption, fixed time/score gates and hard-coded update year | Unknown learners receive too much; heuristic looks scientific | Diagnostic start, bounded modes, rubric-based adaptation and verification at lesson time |
| Github “high-signal” preference without a repeatable dossier | Links may be stale, unpinned or too large to study | Dated metadata, explicit targets, commit pin, quality/adoption uncertainty |
| Generic lab outline, no runnable example | No proof workflow can produce reproducible practice | Tested deterministic lab with independent starter, checkpoint tests and mentor solution |
| CI checks navigation/map only | State/evidence errors can pass | Schema + semantic validator, scenario tests, lesson contract checks and CI |

No curriculum facts were rewritten; generated maps remain unchanged. No database, backend, deployment or publication was added. Reported research access limits are in the learning-science review. State is intentionally empty; no past work was fabricated. There were no existing LESSON_RECORD entries to migrate. For future legacy imports, unknown status is not completion: preserve old records as artifacts, create generated/unassessed entries, and ask for actual attempt/completion evidence before upgrading them.
