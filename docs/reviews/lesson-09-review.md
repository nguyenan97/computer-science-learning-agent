# Lesson 09 authoring and verification

Baseline: main `063692ab47f6054afb81d1d83f627204f31812eb`, after PR #16.
Scope: one new EN/VI build day and its original C# lab; no repository-wide re-audit.
No learner submissions, scores or personal progress are stored.

## Selection before catalog mutation

`python scripts/daily_plan.py --next` was saved in ignored
`work/lesson09-plan-before-catalog.json` before editing metadata. It selected
2026-10-13, `ml.evaluation`, build, after the existing 2026-10-12 publication.
The inventory's eligible prerequisite is `statistics.experiments`. Coverage
counts publications, not learner knowledge. No topic/roadmap/profile rule changed.
The roadmap is represented by `references/topics.json` and its generated topic
map; there is no separate `roadmap.md` source to maintain.

The exact three selected recall prompts/answers are preserved: Lesson 08 paired
assignment target, Lesson 06 stale WAL snapshot retry and Lesson 02 BinarySearch
insertion/duplicate contract. The bridge separates an information contract from
causal assignment and database isolation instead of equating those mechanisms.
New foundations explain features/labels, supervised fitting, a finite rule family,
confusion counts, cost, validation selection, held-out audit and overfitting.

Profile allocation: recall 20, foundation 50, break 10, sources 45,
implementation reading 45, lunch 30, lab 75, break 10, experiment 45, break 10,
transfer 35, synthesis 45. Each study section has a task, minutes and stop product;
setup is bounded to 15 minutes within the lab. No opening duration/schedule table.
This is artifact budgeting, not a measured learner completion-time study.

## Semantic, formula and code review

- Recomputed all eleven training losses independently from the synthetic rows:
  unit-cost minimizers 5-8 select 8; FN=4 uniquely selects 5. The finite-family
  proof includes threshold 0/10 extremes and an explicit largest-threshold tie rule.
- Recomputed the four validation costs (16,4,8,1), freeze cutoff 5, and all four
  test confusion tables/ratios/costs. Its 60% accuracy/cost 7 versus negative
  baseline 70%/12 explains the objective; cutoff-7 baseline cost 5 remains visible.
  Test outcomes never reselect the winner. This does not prove generalization.
- Count-loop and prefix-search invariants are stated separately from the expectation
  argument for independent new evaluation data. Independence between observations
  is not unnecessarily required for linearity of expectation. Fixed synthetic
  partitions do not claim IID sampling, confidence coverage or representativeness.
- The ratio policy explicitly prints undefined for zero denominators. A score 7
  is not a 70% probability; no calibration or causal savings is claimed.
- Experiment A changes supplied score to unavailable future-label-derived score
  with rows/labels/partitions/family/loss fixed. Its 1.0 accuracy is an invalid
  information protocol, not production performance. Experiment B keeps balanced
  training size and the held-out target fixed while exposing customers to a
  separate memorizer. It is not a threshold-sensitivity experiment.
- Transfer changes the target unit: ticket mean cost 16/5 versus equal-customer
  mean (4+0)/2. Duplicating A's full set gives ticket mean 32/9 but unchanged
  customer mean; selective duplication would not have that invariance. This
  aggregation does not refit a customer-weighted model or certify fairness.
- EN/VI meaning, numerical limits, commands and source scope were reviewed directly.
  Overfitting validation is explained where used; “target quantity” avoids relying
  on an unexplained estimand term. Structural parity is only supplementary evidence.
- Every independent self-check has its own immediate closed answer. Lab files/results,
  experiment results and transfer solution are inside their own closed answers.
  The public test fixture is explicitly a teaching aid rather than a truly hidden
  dataset; simulated costs are decision units, not dollars or timed service work.

## Source evidence

Source files were actually fetched with TLS verification and read at scikit-learn
commit `102e5daf66759cf896beeee229d1bf7c80ab2ba4`:

| File / range | Verified support | Limit |
|---|---|---|
| `doc/common_pitfalls.rst` 15-224 | Consistent transforms; fit preprocessing/feature selection within train; illustrative random-label leakage example | Documented numerical examples were not rerun |
| `doc/modules/model_evaluation.rst` 575-599, 769-800, 1030-1064 | Accuracy, matrix axis convention, binary precision/recall formulas | No broad metric/API parity claim; our null policy is explicit |
| `sklearn/model_selection/_search.py` 1014-1103 | Candidate/split product and per-task clone passed to fit/score | No scheduling or performance measurement |
| `sklearn/model_selection/_validation.py` 792-872 | Separate slices, train fit and held-out score, callback/error branches | Fold test is validation for parameter selection, not a final search audit; broader routing unreviewed |
| `sklearn/pipeline.py` 519-578, 630-658, 793-811 | Intermediate training fit, final fit, prediction transform/predict path | Caller features, grouping/timestamps and custom estimators remain caller responsibilities |
| `COPYING` | BSD-3-Clause attribution | No upstream code was redistributed or adapted into the C# lab |

The .NET/Angular/Azure feature-history/dashboard recommendation is design inference.
No sklearn runtime, ML.NET, SQL Server, Azure or production feature-store integration
was executed. Prior SQLite/crash/receipt/Wilson/paired-design/sharp-null limits remain
unchanged; no prior lesson's empirical claims or metadata were rewritten.

## Executed local checks

Environment: Python 3.12.14, SDK 10.0.401/runtime 10.0.12, Linux;
Playwright 1.62.0/system Chromium. Builds execute in temporary/ignored copies.
The new lab has no external packages. Exact SDK/runtime roll-forward is disabled;
first installation/restore network needs and offline no-restore commands are stated.

- `python scripts/check_all.py`: 56 Python tests, catalog/profile/skill/nav/public
  contracts, nine EN/VI parity pairs, 348 balanced/default-closed source answers;
  18 page-derived lab groups; all nine source-copy and extracted-ZIP checks/builds.
- The new lab's demo, check, experiment and transfer modes were also run from
  each isolated EN/VI page-derived project and its extracted ZIP. All twelve
  executions exactly match the announced outputs. Correctness checks cover 1554
  small ordered datasets/two costs (3108 fits), independent confusion cells,
  domain extremes, ties, invalid inputs and row/customer split guards. The oracle
  shares representation/comparison but avoids the production search/count/loss.
- The new ZIP has eleven source/config/guide/license files. No bin/obj/database
  or private data. Two independent public builds have 164 byte-identical files,
  including nine byte-identical ZIPs. A second nav/coverage generation changes no bytes.
- Browser link check with 800ms document delay: 18 lesson pages, 417 internal
  document links, 61 assets; all language/neighbor clicks succeed, no runtime
  errors or third-party requests.
- Desktop/mobile interactions across all pages: 36 visits, 696 closed-answer
  checks/toggles, 548 exact code blocks, 196 tables, four existing plot loads,
  58 keyboard scroll checks, 36 downloads/language switches/neighbor clicks.
  Minimum tested text contrast 4.674:1, no page overflow or clipped prose code.
  Screenshots of the new VI introduction/table/code at both widths were inspected.
- The documented strict-inequality mutant was executed in an isolated copy and
  rejected by the independent checker. The selection-defect answer also states
  that combined validation/test costs 28,9,17,8 still select cutoff 5 in this
  fixture: unchanged choice does not make the information protocol valid.
  No executable behavior/output changed during prose clarification. Final parity,
  answer-contract, public-link/nav checks and the complete desktop/mobile browser
  interaction check were rerun after the final text edits and passed.

CI evidence at the final head belongs in the PR description: required validation and
individual diagnostic logs/outcomes, including continue-on-error. An open PR is not
Pages deployment. No merge or deployment is authorized for this lesson request.

## Limits

No production dataset, probabilistic calibration, drift/missing-outcome system,
causal intervention, confidence interval implementation, nested CV, learned scaler
or equal-customer refitting was tested. No performance timing is claimed.
Small exhaustive datasets plus selected boundaries are not every possible input.
Two Chromium widths/selected keyboard/contrast checks are not complete WCAG,
Firefox/Safari or screen-reader verification. Profile budgeting is not learner
completion evidence. Existing CI platform notices are maintenance follow-ups.
