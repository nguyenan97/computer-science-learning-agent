# Repository quality audit

Baseline: `9559644791992544bbeb252d4d1065a183c21d9b` on `main` (eight published lessons).
Scope: the eight complete EN/VI pages, their executable labs and transfer answers,
canonical skill/spec/profile/glossary, topic inventory/roadmap, catalog, scripts,
tests, public staging, Docsify configuration and the three CI workflows. This is
maintainer evidence, not a learner record. No lesson was added and no personal
answers, scores, attendance or learning progress were collected.

## Priorities and findings

Priorities were established before editing: first reproducibility or misleading
interpretation, then missing assumptions/evidence, recurring structural/workflow
errors, and finally wording/UI/maintenance. The baseline location below identifies
what was observed; section names remain useful after line numbers change.

| ID / priority / class | Location and evidence at baseline | Learner impact | Implemented repair |
|---|---|---|---|
| F01 / P1 / reproducibility | Lesson 01 section 8, Lesson 02 section 7: runnable solution pages omit parts of the downloaded project, including configuration and checks. Main checks execute source/ZIP, not a project reconstructed from either page. | Copying the page is insufficient; two agreeing translations can still disagree with downloads. | Complete named source/config fences in both pages; all eight pairs use the catalog's existing file set. Build/check independently extracted EN and VI projects, then source copies and extracted ZIPs. |
| F02 / P1 / environment | `labs/*/dotnet/global.json` for Lessons 01-06 allows `latestPatch`; executable projects do not fix the runtime. Lesson 01 benchmark pins the direct package without a checked-in transitive lock. Its optional EF example creates another roll-forward project. | Repeating commands can use a different environment/dependency graph while appearing to reproduce the lesson. | SDK 10.0.401/runtime 10.0.12 with roll-forward disabled; benchmark lock; optional `IdentityDemo` code/project/lock in the same ZIP and complete page answer. First-restore network needs are explicit. |
| F03 / P2 / workflow | `scripts/daily_plan.py:47` defaults to today's calendar date; baseline catalog ends on 2026-10-12 while this session's UTC date is 2026-10-09. | A request for the next lesson can accidentally select an existing day. | Mutually exclusive `--next` / `--on`; `--next` derives latest publication date + 1 before catalog mutation. No flag retains today's Vietnamese study date. Tests cover future dates, catalog order, empty catalog and CLI conflict. |
| F04 / P2 / answer access | `scripts/review_queue.py:149` emits one answer block for several questions and a typographic dash. Lesson 02 library questions/practice list group independent answers. | Opening one answer reveals unrelated answers; pasted planner recall violates the page contract. | One immediately following, default-closed block per question in queue output and both Lesson 02 pages; optional attempt wording and plain hyphens. |
| F05 / P2 / structure | Lesson 01 sections 2-5 and Lesson 02 sections 2-4 rely on a timebox elsewhere instead of each section's task/time/done line. | The reader cannot tell where to stop a local section. | Split the existing foundation budget into 10/15/10/15 and 10/25/15 minutes respectively, with a concrete product in each section. Existing breaks/budget remain intact. |
| F06 / P2 / answer placement | Lesson 03 section 5 exposes setup/code/results before its answer. Lesson 01 section 9 and Lesson 05 section 6 show recorded experiment results outside a result answer. | Predicting first is difficult and placement differs across lessons. | One complete closed lab answer in Lesson 03; its experiment file joins the complete lab. Separate interpretation prompts and closed result answers for the recorded benchmark/read/write tables. Defect prompts stay outside lab answers. |
| F07 / P2 / UI | Mobile VI Lesson 08 baseline DOM still says `lang=en`. Lesson links use rgb(66,185,131) on white (about 2.48:1 contrast). Wide table measured 483px of content in a 282px box, without explicit tabindex/focus treatment. | Incorrect language metadata, low-contrast reading and unclear keyboard access to clipped content. | Local Docsify hook sets language/title; high-contrast theme/token styles; visible focus and localized, keyboard-focusable overflowing table/code containers. Horizontal content scroll remains inside the page. |
| F08 / P2 / maintenance | `references/lesson-template.md` is a four-line pointer; skill repeats page-rule bullets despite spec ownership. | Future authors reconstruct the requirements manually and can propagate inconsistent structures. | Flexible scaffold, semantic review checklist and ownership/generated-artifact map; skill refers to the canonical spec rather than maintaining another page contract. Profile remains the owner of schedules. |
| F09 / P3 / presentation | Lesson 01 `LessonLab/Program.cs` / `Checks.cs` print agent/reference verification commentary. | Internal audit claims interrupt the example output. | Console output describes the task/checks only; finite-test limits stay in learner-useful explanations. |
| F10 / P2 / model assumptions | Lesson 08 complexity paragraph lists O(B*2^B) without stating the cost assumption for validating hashed IDs. | A reader can infer that arbitrarily long keys cost a constant amount. | Both languages state bounded numeric/ID costs and suitable hash distribution; variable-length identity processing has separate cost. No theorem, estimand or sharp-null interpretation was changed. |
| F11 / P3 / wording | VI Lesson 07 uses ambiguous numeral wording in covariance/standard-normal statements; profile has fragments such as “Trace ... ở pin”. | Unnecessary decoding of the intended mathematical value/activity. | Use explicit 0/1 where these are numbers and ordinary Vietnamese task wording. Familiar developer terms remain in context. |

Baseline artifacts can be inspected at
[the reviewed commit](https://github.com/nguyenan97/computer-science-learning-agent/tree/9559644791992544bbeb252d4d1065a183c21d9b).
These are reproducibility, structure, assumption and UI findings, not a claim that
all mathematical content was wrong. Harmless translation/style differences are
not classified as correctness defects. No verified counterexample to the central
algorithms or statistical derivations was found in this review's stated scope.

## Lesson review and continuity

The review considered meaning and derivations in both languages, not just matching
heading counts. Each lesson has a concrete opening example, a correctness argument,
a useful counterexample, changed-context work, accessible solutions and finite
verification limits. The following records the substantive checks and retained scope.

| Lesson | Learning argument, prerequisites and transfer | Independent check / retained limitation |
|---|---|---|
| 01 - Cost model | First-occurrence order and explicit equality; derive the triangular sum; distinguish expected, amortized and worst-case hashing; prefix invariant. Transfer to duplicate counts, EF identity and durable request identity. | Scan vs hash, forced-collision witness, order/null/comparer cases. Eight groups pass. EF's three query modes reproduce shared-instance/tracker counts; no EF performance claim. Historical ShortRun has wide uncertainty and is illustrative only. |
| 02 - Boundary search | Sorted random-access contract; unknown half-open interval; duplicate-aware partition/preservation/termination; count by two ranks. Kafka summary seek followed by scan is a different contract. | Seventeen check groups include an exhaustive small-array predicate-scan oracle and boundary checks. Read-count growth excludes key extraction, insertion shifts and I/O. T-SQL remains an unexecuted application example. |
| 03 - Shortest paths | Explain adjacency/state/cost, reuse invariant reasoning, trace FIFO vs nonnegative weighted extraction and stale entries. Counterexamples reject discovery-time termination and negative-cost misuse. Transfer changes state to include arrival corridor. | 7,683 oracle/path comparisons; repeated relaxation avoids the priority queue. Path validity and numeric/sentinel boundaries are checked. Selected graphs do not prove every input; OSRM CH offsets/asserts are not arbitrary negative lab edges. |
| 04 - DP/approximation | State and recurrence are introduced through budget examples; induction splits include/exclude; descending compression preserves the previous row. Density trap and near-half family test the actual guarantee. Transfer adds a count constraint. | 12,226 inputs compared with subset enumeration; 720 count-limited transfer cases. Shared input validation is stated. Pseudo-polynomial resource policy, exact integer comparisons and half guarantee retain their premises; no optimizer/production quality guarantee. |
| 05 - Index/query plans | Build pages/B-tree/locator/composite ordering before seek/scan/covering discussion; separate rank counting from COUNT/SUM traversal. Transfer changes aggregation into ordered keyset pagination. | 11,416 aggregate comparisons against a C# predicate scan; index maintenance/rollback and tied timestamps. Warm local SQLite timing is workload evidence, not SQL Server or production latency. Cross-request snapshot is an assumption, not implemented concurrency control. |
| 06 - Transactions/recovery | Introduce schedules/ACID before distinguishing atomic writes from valid decisions; demonstrate stale values outside a transaction and a still-open WAL snapshot separately. Guarded version update, bounded fresh retry, rollback and receipt boundary. | 225 forced serial-order schedules against an independent business model; code 517, rollback/replay and two acknowledged process-kill boundaries. These do not cover every interleaving/fairness, power loss/device flush or distributed exactly-once delivery. |
| 07 - Sampling/uncertainty | Explain units, fixed parameter, sampling variation and covariance before interval/coverage formulas. Derive Wilson from score inequality; enumerate a finite binomial model and challenge row independence. Transfer changes requests to equal-size batches. | 20,300 score-root inversions, small binary-sequence weight oracle, endpoints and deterministic seeds. Wilson finite coverage can fall below nominal; linked rows are not independent evidence. Exact integer model weights do not validate a real-world model; endpoints still use double. |
| 08 - Experimental design | Bridge uncertainty to association/confounding/potential outcomes; trace one-treatment-per-pair and derive assignment expectation/variance. Select-low counterexample and sharp-null enumeration have distinct purposes. Transfer uses binary damage outcomes and batch units. | 64 independently scanned assignments, 6,561 small potential tables, variance and null rejection size 2/64; packing example returns effect -0.25, observed -0.5 and p=0.5. Balanced subsets need not obey paired assignment; sharp null is stronger than average effect zero. Synthetic outcomes do not establish production causality. |

The profile budgets were checked through the planner and page section allocation;
setup/source reading have worked or reading-only routes. Complete solutions are
folded to avoid making every source line mandatory reading. Whether an individual
learner finishes these days in the default budget was not measured. No learner
completion or comprehension is inferred from this artifact review. The existing
three recall entries per lesson already ask for mechanisms/assumptions; they were
reviewed and preserved rather than replaced with terminology quizzes.

## Source-reading evidence

Actual files were retrieved over verified TLS at all cited immutable blob commits:
27 distinct files, including attribution/license files. Read ranges/functions were
bounded by the lesson's claims. A successful fetch is only access evidence; the
mechanisms below were inspected separately. Full repositories were not built.

| Lesson | Commit | Read slice and supported behavior |
|---|---|---|
| 01 | runtime `4271d88e0aebf3d04f188f1334c2220d80555ef6`; EF `7adff35c6c583fa6f7aa3939389ab3314be330ab` | `List.cs` Contains/IndexOf and `HashSet.cs` AddIfNotPresent bucket/equality/resize; EF `IdentityMap.cs`, `ShapedQueryCompilingExpressionVisitor.cs` materialization branch, `QueryContext.cs` lookup/standalone state manager and `StateManager.cs` query registration. Reuse before materialization differs from attachment conflict. |
| 02 | Kafka `8ed535f41c2a8a783e64a3b4ff9468ab682959b8` | `LogSegment.java` append maxima/findOffsetByTimestamp, `TimeIndex.java` maybeAppend/lookup, `AbstractIndex.java` warm-section comment/binary search and `FileRecords.java` timestamp scan. The comment's historical latency observation was not reproduced. |
| 03 | OSRM `4f3ee609ec1af40eb1f445c6706cfa5beb04c990` | README, `car.lua`, `direct_shortest_path.cpp` CH specialization and `routing_base_ch.hpp` routingStep/relaxOutgoingEdges. Profile weight/hints, positive assert and DecreaseKey are bounded source facts; real routing workload/MLD is not the lab. |
| 04 | PostgreSQL `7885b94dd81b98bbab9ed878680d156df7bf857f` | `allpaths.c` standard_join_search, `joinrels.c` join_search_one_level, `pathnode.c` add_path/set_cheapest and COPYRIGHT. Legal-subset search and non-dominated physical paths do not reduce PostgreSQL to the teaching knapsack. |
| 05 | SQLite `8ed5e7365e6f12f427910188bbf6b254daad2ef6` | `btree.c` record comparison/cursor search, `where.c` row-locator/covering decisions, `vdbe.c` deferred seek and aggregate dispatch. Record visits remain separate from positioning. |
| 06 | Same SQLite commit | `wal.c`: overview, walDecodeFrame, walIndexRecover, sqlite3WalBeginWriteTransaction and walFrames, using the page's cited ranges. Header freshness and committed-frame boundaries support the modeled cases, not every pager/VFS failure. |
| 07 | SciPy `b1296b9b4393e251511fe8fdd3e58c22a1124899` | `_binomtest.py` lines 10-199: result/method dispatch, exact endpoints and Wilson branches; license. Exact default and Wilson alternatives are verified code facts. SciPy/R runtime and full root/quantile solvers were not executed. |
| 08 | GrowthBook `7f0b1c3059ac634edd82b18e43ce7d92d08dbb3e` | SDK `core.ts` ordinary allocation/missing-ID/tracking path and `util.ts` hash versions, half-open ranges and variation choice. Hash stability/ranges are verified; uniform real IDs, causal validity and durable exposure delivery require further evidence. |

Design recommendations (cache choice, indexes, short transactions, consistent
experiment identity) are instructor inferences, not claims about maintainers'
intent or validated integration. IUH original PDFs remain independently unverified
as already documented in content provenance; roadmap prerequisites are project
design, not official degree rules. No new full-paper reproduction is claimed.

## Ownership and authoring workflow

[Maintaining](../maintaining.md#ownership-and-generated-artifacts) maps official
rule owners and edited/generated artifacts. The skill is one canonical file with a
symlink; the spec owns authoring, profile owns budgets, glossary guides wording,
topics own selection/prerequisites and catalog owns published order/assets/recall.
The scaffold and checklist consume those rules. Existing pedagogy/source/workflow
pointer files are kept as pointers. Nav/home/sidebar/coverage marked outputs are
generated; explanation and source lab content are manually edited.

For future lessons: capture `daily_plan.py --next` in ignored scratch before catalog
mutation, justify the chosen objective and foundation bridge, allocate the actual
build/paper blocks to checkable products, then draft with the flexible scaffold.
Review evidence/meaning with the checklist, add metadata, regenerate and verify.
No fixed paragraph template or duplicate schedule table is introduced. The present
catalog's next-date smoke check yields 2026-10-13; this audit did not author that day.

Mechanical checks now detect named-file omissions/drift, translated raw C# literal
drift, malformed/default-open answers and typographic dashes with actionable
locations. They do not decide whether a proof is valid, a prerequisite is sufficient,
a transfer task is meaningful or a translation is natural. Those remain manual
review responsibilities. No framework/runtime UI dependency was added; local
styles/hooks keep vendor files and their verified hashes unchanged.

## Verification

Environment: Python 3.12.14, .NET SDK 10.0.401/runtime 10.0.12 on Linux;
Playwright 1.62.0 with system Chromium. All builds ran in ignored/temporary copies.
Commands below are repository-root commands; staging outputs must be fresh paths.

- `python scripts/check_all.py`: 56 Python tests; catalog/profile/topic/nav/public
  contracts; eight parity pairs; 312 closed/balanced source answer blocks;
  page-derived EN/VI build/check for eight labs; source-copy and extracted-ZIP
  checks for all eight; build every project, including benchmark and optional EF.
- `python scripts/check_all.py --benchmarks-only`: 12 BenchmarkDotNet Dry cases
  execute. This is harness smoke evidence, not a replacement ShortRun performance
  study; diagnostic small-iteration warnings are expected.
- Run demo/check and observe/experiment directly from page-derived projects;
  compare deterministic outputs/counts with both pages. Lessons 03/04 announce
  counts in prose (7,683 / 12,226) rather than complete output fences.
  Transfer entry points for Lessons 03-08 run separately and agree with published
  answers; Lesson 02 record transfer is included in observe/check.
- Optional EF assertions run from both extracted page projects and the extracted
  ZIP, returning tracking=True/3, no-tracking=False/0 and identity-resolution=True/0.
  The required CI builds this project; the local supplementary run checks its output.
- Seeded `distribution.csv` and `assignments.csv` are byte-identical to published
  CSVs. Recomputed finite model outputs agree with the rounded published values.
  SQLite query counts, sums, plans and allocated-byte values agree; fresh timings
  vary, so historical timing values were not treated as fixed expected output or
  replaced by new measurements. Lesson 01 historical ShortRun was not rerun.
- Rerun navigation/coverage and compare bytes; independently stage twice and compare
  all 150 public files, including eight ZIPs. Outputs are identical. Archive
  allowlists contain no build output, private records or maintainer reports.
- Browser link diagnostics on all 16 EN/VI pages, with 800ms delayed document loads:
  language and neighbor navigation, 375 linked documents and 60 asset links;
  no runtime errors/third-party requests.
- Browser interactions on all 16 pages at 1440x1000 and 390x844: 624 answer checks start closed and toggle; 484 exact rendered code blocks,
  176 table checks, four plot loads, 60 keyboard horizontal-scroll checks, 32 language
  switches/neighbor clicks and 32 actual downloaded candidate ZIP byte comparisons.
  Minimum tested link/inline-code/token text contrast is 4.674:1. Screenshots of
  desktop introduction and mobile code/trace/chart were also inspected.
- `git diff --check`: no whitespace errors.

A malformed Markdown fence introduced while packaging the optional EF example
was caught by page extraction and browser navigation checks, repaired, and the
full checks rerun. This was an implementation correction, not a baseline finding.

Final-head CI evidence belongs in the PR description with immutable run links and
commit SHA: inspect required validation and every optional diagnostic step outcome
and log, including continue-on-error failures and benchmark warnings. This avoids
claiming that a green optional job proves all diagnostics passed or embedding a
self-referential commit hash in this report. Pages deployment is deliberately not
part of this unmerged PR's verification.

## Remaining work and verification limits

- No SQL Server/T-SQL execution, real cloud integration, full PostgreSQL/Kafka/OSRM/
  GrowthBook build or SciPy/R runtime validation. The newly archived EF SQLite
  example verifies its three query modes, not EF internals/performance as a whole.
- No power-loss/device-cache/flush certification, arbitrary crash positions,
  fairness/high-contention study or distributed exactly-once guarantee.
- No production performance or causal representativeness claim. Deterministic
  generators and synthetic outcomes cannot establish IID real traffic or no
  interference/missingness. No full-paper empirical result was reproduced anew.
- Chromium at two widths and selected keyboard/contrast/layout checks are not a
  full WCAG conformance audit or Firefox/Safari/screen-reader verification. Test
  those when there is an identified need; no speculative performance optimization.
- Paper-day scaffold/profile compatibility is structurally reviewed; no new paper
  day was published or timed with a learner. Likewise, no completion-time usability
  study was performed. A future real-time teaching trial may revise block depth.
- Named-file extraction currently serves one runnable lab directory per lesson,
  as all published entries do. Define namespaces if a future lesson adds multiple
  independent runnable lab directories instead of duplicating another file manifest.
- Optional EF and changed-context output assertions were run locally; generic
  continuous automation of additional entry points can be a follow-up if authors
  add more of them. Main lab checks and all project builds are already required.

No merge or deployment was performed. Changes are submitted for maintainer review.
