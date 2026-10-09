# Lesson 08 authoring and verification review

## Selection and teaching scope

Main at selection: `e59358aeb3207dfbb4b54f272db68f900a42361f`.
The latest catalog date was 2026-10-11. Before any catalog edit,
`python scripts/daily_plan.py --on 2026-10-12` selected
`statistics.experiments`, Experimental design and causal limits, build profile.
Its prerequisite `statistics.uncertainty` is covered by Lesson 07.
Recall: Lesson 07 confidence-scope, Lesson 05 cover-order and Lesson 01 hash-limits.
Selection follows the inventory, not a guess from the preceding lesson title.

Both complete pages introduce potential outcomes, consistency, no interference,
assignment versus sampling, confounding, a paired estimator and a sharp null.
The eight timed work sections and four break/lunch lines follow the build profile.
Each page has 21 separate immediate, default-closed answer panels, including lab,
transfer and observed experiment results; setup is bounded and reading-only work
is possible. Three bilingual future recalls and catalog-generated navigation/
coverage are updated. Coverage is 9/43 planned units, statistics 2/2; this counts
published artifacts, not learner knowledge. No learner records are saved.

## Actual sources and boundaries

GrowthBook source was downloaded at immutable commit
`7f0b1c3059ac634edd82b18e43ce7d92d08dbb3e`:

- `packages/sdk-js/src/core.ts`: runExperiment guard 427-447, identity exclusion
  528-545, hashing/range/exclusion 674-730, callback dispatch 814-833,
  getHashAttribute 1073-1108 and onExperimentViewed 76-113.
- `packages/sdk-js/src/util.ts`: hash versions 19-46, half-open membership/
  chooseVariation 53-75 and getBucketRanges 183-233.
- LICENSE: SDK slice lies outside enterprise directories under MIT.

Verified: ordinary-path hash assignment, missing-identity/invalid-version/range
exclusion and conditional user-context tracking dedupe. Not verified: SDK runtime,
statistical engine, all override/sticky/bandit paths, persistence/delivery or
uniformity/independence on actual identities. Identity/configuration stability and
causal identification are separate. The .NET/Angular/Azure proposal is instructor
inference, not a measured integration. No SDK text/code is redistributed.

Hernan and Robins, author-hosted What If August 2026 PDF, sections 1.1-1.2,
printed pages 3-6 including interference, and 2.1, pages 13-16, were read.
OpenStax Introductory Statistics 2e 1.4 was read from the opening design explanation
through aspirin/blinding. Its broad finite-balance wording is explicitly qualified.
The current GrowthBook JavaScript SDK initialization/tracking example was read
for product context. NIST/Penn State access failures and an OpenIntro missing URL
supply no claims. No later observational identification estimators are implied.
Original prose is CC BY 4.0 and original teaching code is MIT.

## Mathematical and EN/VI review

One treated/control unit per pair is the assignment invariant; accumulated d is
the treatment-minus-control prefix sum. Pair choices are independent, but the two
assignments within a pair are complementary. Potential outcomes are fixed; only
assignment varies. Two equiprobable orientations average half the pair effects,
so E_design[D]=tau. This does not require IID outcomes or representative sampling.
The constant-effect variance sum(gap^2)/B^2 is labelled fixture-specific.

The Simpson reversal is a descriptive weighted-average example, not a causal
identification proof. Sharp-null flips freeze observed outcomes and use inclusive
absolute integer tails across all assignments. They test individual no-effect,
not zero average effect, posterior null probability or an effect interval.
All-outcome oracle distribution is available only in the simulator. Mask 21 is a
preselected illustration, not a randomized draw. Deterministic select-low reports
NA for unsupported equal-probability inference. Synthetic milliseconds are not
measured service latency. Prior production/SQL Server/runtime/durability/delivery
limits are not promoted to verified findings.

EN/VI formulas, prompts, answers, terminology, source scope, units, code, pins,
commands and observed outputs were reviewed. No en/em dashes or opening total/
date/schedule. The binary packing transfer reports percentage points, not ms.

## Local checks

- `python scripts/check_all.py` passed: 48 repository tests, catalog/planner,
  nav/coverage/parity/links and 144 public staged files. All eight labs run from
  source copies and extracted ZIPs; archived projects build. New lab: zero
  warnings/errors, SDK 10.0.401/runtime 10.0.12, locked restore, no external NuGet.
- 64 paired estimates match an independent 12-bit balanced-subset arm scan;
  6561 exhaustive small potential-outcome tables check an integer expectation
  identity; variance, trace, relabeling, ties, null size and invalid inputs pass.
- Five C# fences agree EN/VI; four source files and all SDK/project/lock config
  are extracted from the actual page and match source bytes. Demo/check/experiment
  run with locked restore and --no-restore; the complete transfer runs too.
- Independent maintainer Python Fraction enumeration verifies all 256 CSV estimates,
  four means/variances and null tails 54/64,52/64,54/64,58/64. This is a maintainer
  check, not a learner Python dependency or production measurement.
- Executed sign-orientation and strict-tail mutants fail the independent arm-scan
  and tail checks; the supplied implementation passes.
- Generated ZIP CRC/inventory pass: exactly ten source/setup/guide/license files,
  each matching source bytes; extracted ZIP runs --check. No bin/obj/CSV in ZIP.
- Chromium whole-site: 16 pages/switches/neighbor clicks, 381 document links,
  57 assets, no runtime errors or external requests; delayed documents 800 ms.
- Lesson desktop 1440px/mobile 390px EN/VI: all 21 panels initially closed and
  toggle both ways, four lab and one transfer code fences render; tables scroll
  without page overflow, language and previous/next navigation work. Mobile
  prose/table/code screenshots were visually reviewed. The candidate download
  click maps the advertised future ZIP URL to staged bytes, validates ten files
  and does not establish that Pages has deployed this lesson.

## Unverified scope and publication

No real traffic, live randomization/RNG audit, GrowthBook SDK/statistical-engine
execution, SQL Server/dashboard integration, missing outcomes, repeated stopping,
production interference, future-cohort generalization or causal-effect confidence
interval is validated. Four complete synthetic design scenarios support only the
stated finite results. Earlier SciPy/R runtime and exact-interval solver remain
unrun. CI is verified at the final PR head, including individual continue-on-error
diagnostics, in the PR report. No merge or Pages update is claimed.
