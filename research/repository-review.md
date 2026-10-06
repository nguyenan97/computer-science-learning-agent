> Historical review. Its former personal-progress tools have been removed.
> Current workflow: [Maintaining](../docs/maintaining.md).

# Repository review — topic-based deep study

Reviewed 2026-10-06 against baseline `fe74583`. No repository AGENTS.md was present. Scope covers local runtime/state, source-backed pedagogy, bilingual lesson artifacts, navigation, staging and release configuration. This is not a learner experiment or a full security audit.

## Concrete defects and repairs

- The Pages workflow could deploy while validation failed in a separate workflow. It now calls the reusable validation workflow and makes deployment depend on its success. Both check out `github.sha`; publication is restricted to `main`. The release must pass PR checks before merge; main then runs validation again before deploying the same commit.
- Completion accepted an assessment linked to the lesson but for an unrelated topic. The runtime now requires a qualifying same-topic task observed by completion. Other-topic prerequisites remain recordable. Semantic objective/rubric relevance and learner provenance require the assessor to inspect actual evidence; string matching cannot prove them.
- CDN major tags could change without a repository commit. Docsify and Prism now use exact version URLs. Browser verification checks the staged candidate, while CDN availability is still an external dependency.

## Design changes

State v3 removes legacy course metadata. Migration accepts v1/v2 only into a fresh destination, preserves the source/evidence and refuses unsupported legacy completion without inventing observations. Planner separates self-reported context, caller flags, assessed evidence, unassessed work, unknown prerequisites and recorded misconceptions. Null profile budgets default to 420 elapsed minutes, including breaks; explicit shorter budgets remain valid.

The canonical bilingual topic inventory replaces academic administration. Substantive technical outlines remain as reading notes with [attribution](content-provenance.md); prior originals remain in the fixed historical snapshot. The renamed [skill](../skills/cs-daily-deep-study/SKILL.md), owned contracts and full-day sample emphasize controlled practical work, focused research and optional evidence submission.

## Review limits

The JSON validator verifies structural invariants, not truth of a learner response or semantic translation equivalence. Topic relationships, time allocation and mastery labels are conservative engineering choices, not experimentally validated educational models. [Verification](verification.md) reports checks actually executed and outstanding limits. [Learning-science review](learning-science-review.md) distinguishes read full-text sections, abstracts and inaccessible sources.
