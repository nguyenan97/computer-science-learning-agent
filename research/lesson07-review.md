# Lesson 07 authoring and verification review

## Selection and scope

Main at selection: `24461a4efb07b4dcb9273cdd1e76f52fcac4db75`.
The last catalog day was 2026-10-10. Before editing the catalog,
`python scripts/daily_plan.py --on 2026-10-11` selected
`statistics.uncertainty`, Probability, estimation and uncertainty, build profile.
The topic has no published prerequisite. Recall selects Lesson 06 stale-scope
and Lesson 04 rolling-direction. This follows inventory order, not the prior title.

The two full pages introduce Bernoulli variables, IID, expectation, variance,
covariance, sampling distributions, a normal cutoff and frequentist confidence
before relying on them. Eight timed blocks and four rest blocks follow the profile.
The minimal source/code choices leave room for derivation and changed-context work.
There are 20 immediate, default-closed panels per page, including the observed
experiment/chart. Reading-only and 15-minute setup routes are supplied.

Original-request and batch units extend the earlier independent-check/invariant
context. Existing SQL Server, SQLite performance, interleaving, process-crash and
delivery limits are retained; no learner activity or personal progress is recorded.

## Sources read and attribution

Actual SciPy `_binomtest.py` at tag v1.16.2, immutable GitHub commit
`b1296b9b4393e251511fe8fdd3e58c22a1124899`, was downloaded and read:

- Lines 10-114: result fields, method/confidence validation and dispatch;
  default exact versus wilson/wilsoncc.
- Lines 117-159: numerical tail inversion and zero/all-event boundaries.
- Lines 162-199: one/two-sided quantile choice, center/radius,
  continuity-correction branches and boundary handling.

The case is the scientific product's result API for binary counts: users receive
an interval with an explicit method, not only a point estimate. Source verifies
that API and branches; recommending the same explicitness for a .NET report is
instructor design inference. No claim about every user's motivation, large-scale
production adoption, complete numerical solver or SciPy runtime parity is made.
The C# formula is independently derived from the score inequality, not copied.
The SciPy BSD notice was read; linked source is not redistributed.

Official SciPy 1.16.2 proportion_ci/binomtest documentation was read, including
methods/returns and the exact 7/50 interval example. OpenStax Introductory Statistics
2e 8.3 was read through binomial/normal proportion modeling and error bounds;
7.1's opening sampling-distribution/spread discussion was read. R binom.test
Details was read for Clopper-Pearson's at-least-nominal binomial coverage versus
length. Those properties are not transferred to Wilson or dependent data.
NIST and Penn State endpoints were unavailable; no claims rely on unseen content.
SciPy references primary papers, but full texts were not read, so no paper-specific
empirical claims are made. Prose/chart are original CC BY 4.0; teaching code MIT.

## Formula, assumptions and translation review

The prefix invariant k=sum(outcomes), 0<=k<=n is preserved by append. Bernoulli
variance uses X^2=X; independence removes covariance in the sample mean.
Normal approximation is introduced, not assumed to be a finite-sample theorem.
Quadratic inversion proves the returned score-acceptance interval, not coverage
exactly 95%. The count/interval/model/representativeness distinctions are explicit.

Wald zero width at k=0 is a counterexample even after clipping. For p=0.02,n=20,
zero counts are common; Wilson's finite-model coverage 0.940101 still falls below
nominal 0.95. More simulation repetitions do not repair that interval procedure.
The finite binomial sum is coverage evaluation, not exact CI endpoint construction.

Twenty perfectly linked ten-row groups have the same mean as twenty latent units;
variance is p(1-p)/20. The group repair assumes equal sizes and identical within-group
outcomes, not arbitrary traffic. Dedupe does not establish independence or stationarity.
An exact descriptive cohort fraction and inference to a process are distinguished.

BigInteger sums use rational numerator weights and a common denominator; membership
uses double Wilson endpoints. Ratio scaling before conversion avoids infinity for
large supported denominators and truncates below 2^-53. Numerical rounding remains.
The deterministic generator rejects an incomplete modulo range, which avoids modulo
bias under a uniform-output idealization, not serial correlation or poor RNG quality.

EN/VI meaning, each prompt/answer, source scopes, commands, output, formulas and
terminology were reviewed. Covariance and standard normal were added before use.
No typographic em/en dashes, opening budget/date/schedule, or English-word glossary.

## Local verification

- `python scripts/check_all.py` passed: 48 repository tests, catalog/planner,
  navigation/coverage/parity/links and public staging. All seven labs run from
  temporary source and extracted archives; archived projects build. New lab has
  zero warnings/errors and locked restore, SDK 10.0.401/runtime 10.0.12.
- 20,300 Wilson cases for n=1-200 match a bisection inversion of the score condition,
  with 2e-12 endpoint tolerance, range/point inclusion and complement checks.
  Exhaustive binary sequences for n=1-10 independently match p=1/2 binomial
  weights. Three-draw p=1/5 fixture, large probability sums/denominator and
  degenerate probabilities supplement endpoints, seed and argument checks.
- An independent Python Fraction sum using score/Wald acceptance rather than
  Wilson endpoint code agrees with all 11 reported rounded model coverage sums.
- Five on-page C# source fences match lab source byte-for-byte; all six fences
  including transfer agree EN/VI. SDK/project/lock and source are extracted from
  the actual page, restored with --locked-mode, then demo/check/experiment run
  with --no-restore. Eleven experiment rows match the recorded execution, and
  the 60 histogram bins match the public synthetic CSV.
- The complete batch transfer Program was executed: batch interval
  [0.0279,0.3010], naive row interval [0.0657,0.1494]. The integer-division defect
  was executed and failed the independent score-root check as predicted.
- The generated ZIP has exactly 11 source/setup/guide/license files, CRC passes,
  each byte agrees with source; no bin/obj/packages/generated CSV/database.
  Required checks also run/build the extracted archive.
- The plot was generated with standard Matplotlib from C#'s actual synthetic
  distribution.csv. Each n has 2,000 observations; all 60 bins and full 0-1
  horizontal range are retained, with common axes. The plot was visually reviewed.
- Chromium checks: 14 EN/VI pages, 14 switches, 14 neighbor clicks,
  337 internal document links, 55 assets; no runtime errors/outside requests.
- Lesson 07 desktop 1440px/mobile 390px: 20 initially closed panels per language
  toggle; five lab code fences and the transfer render; language and previous/next
  routes work. Open tables scroll horizontally without document overflow; the
  chart loads. Candidate ZIP link maps the advertised future deployment URL to
  staged bytes for download verification; it does not claim publication before merge.
- Final prose changes are checked with validation/parity/nav generation and
  git diff --check; PR CI verifies the final committed tree again.

## Unverified scope

No production requests, random-generator independence/quality, drifting rates,
missing telemetry, irregular clusters, general cluster methods, representative
sampling audit, SQL Server query/dashboard integration, SciPy/R runtime or exact
interval solver are executed. Seeded results describe this synthetic workload;
they are not throughput/latency measurements or universal 95% guarantees.
Earlier physical durability/distributed payment claims remain unverified.
CI is checked at the final PR head and each optional diagnostic step is reported
in the PR/response. GitHub Pages is not claimed current before an authorized merge.
