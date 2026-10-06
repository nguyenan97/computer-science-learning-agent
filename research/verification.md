> Historical review. Its former personal-progress tools have been removed.
> Current workflow: [Maintaining](../docs/maintaining.md).

# Verification — topic-based full-day study

This record documents local pre-merge checks on 2026-10-06, based on `fe74583`. Release workflow and deployment status are recorded separately in GitHub Actions. No real private learner state was read, migrated or modified; state cases use synthetic temporary workspaces.

## Executed checks

- Runtime regressions cover same-topic completion, unknown/self-reported/observed knowledge, full-day/short budgets, v1/v2 migration and evidence preservation, private artifacts, repair links, due reviews and public/private isolation.
- CI configuration is checked for a reusable validation gate, a main-branch deployment condition, least-privilege validation and identical `github.sha` checkouts. This documents local configuration checks; the release PR must also pass GitHub CI before merge.
- Topic graph generation validates bilingual fields, unique nonblank IDs, missing prerequisites and cycles. Generated maps are checked for drift; navigation mirrors and shared contract versions are validated.
- Python reference labs: 4 boundary-search checks and 4 cost-model checks pass. Observed counts agree with lesson examples.
- .NET SDK 10.0.401: all 8 C# correctness checks pass and the observation command produces the advertised stable output/counts. BenchmarkDotNet 0.15.8 executes 12 Dry cases. Dry validates the harness, not speed estimates; no new ShortRun/production benchmark claim.

Integrated checks: **47 unit tests pass**; map/navigation/learning validators pass; site stages **76 public files**. Chromium verifies **4 lesson pages, 4 language switches, 4 previous/next clicks, 97 internal document links and 2 download assets** with verified TLS. The extracted ZIP runs all **8 C# checks** and builds the benchmark project with zero warnings/errors without a repository checkout. Visual home/lesson review confirms meaningful rendered content, navigation and no horizontal page overflow or JavaScript runtime exceptions. Docsify emits four expected 404 probes for nested `_navbar.md`/`_sidebar.md` before loading the correct ancestor menu; these were inspected and are not broken lesson links.

## Content and skill review

The renamed [skill](../skills/cs-daily-deep-study/SKILL.md) and bilingual owned contracts specify a complete day, optional submissions, accessible answers, evidence-based adaptation and no gate on the next lesson. Both published lessons include full inline explanations, runnable examples, reasoned answers and catalog-generated related/previous/next links. All inline Python examples execute; the two inline C# methods compile and pass order, equality, boundary and null-policy checks. Navigation regressions cover reordering, first/last boundaries, invalid targets and lesson-file/parent symlinks without private or partial writes. The [cost-model sample](../lessons/2026-10-05-cost-model/lesson.md) has matching English/Vietnamese objectives, commands, solutions, rubric and schedule: 420 elapsed minutes = 360 learning + 60 breaks; 235 planned active minutes (65.3%). The timetable is a design heuristic; actual learner time was not measured.

The [learning-science review](learning-science-review.md) and [access log](deep-study-source-checks.json) distinguish inspected full-text sections, abstract-only evidence and inaccessible materials. [Provenance](content-provenance.md) retains inherited attribution without institutional requirements in active planning. The former evaluation scenarios were synthetic specifications, not executed model benchmarks; they were removed when the daily loop became catalog-driven.

## Limits

No independent learner response, delayed retention/transfer outcome or educational-effectiveness study was conducted. Semantic objective/evidence relevance, assistance provenance and translation quality require assessor review; JSON matching does not prove them. The current topic sequence, allocation of time and mastery labels are project choices. No upstream .NET/CPython full suite, Windows/macOS test, live production deployment in this local record, new statistically useful performance benchmark or exhaustive systematic literature review is claimed. The project license remains undecided.
