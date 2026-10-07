# Lesson 04 authoring and verification review

## Selection and scope

The latest main was `d29e32f46ca0bbcc92ede83cbfa3cce1b0866f8f` (Lesson 03).
The default planner reused that existing study-date lesson. The explicit request for
Lesson 04 following Lesson 03 was treated as the next study day, 2026-10-08, rather
than creating another 2026-10-07 artifact. Before editing the catalog,
`python scripts/daily_plan.py --on 2026-10-08` selected `algorithms.optimization`,
Dynamic programming and approximation, with covered graph prerequisites and a build
day. Selected recall: Lesson 03 Dijkstra finalization and Lesson 01 stable HashSet/List
membership. No personal answers, scores or mastery claims are recorded.

Full EN/VI lessons teach independent 0/1 job selection under one integer budget,
state meaning, recurrence, induction, traceback, descending rolling updates,
pseudopolynomial cost, a density counterexample and a proved half approximation.
A separate count-constrained exercise changes the state. Eight timed activity
sections follow the build profile, with breaks, completion conditions, examples
before formulas, a reading-only route and no total-time/date/schedule header.
Familiar English developer words remain in context rather than glossary entries.
All worked answers are immediately below their prompts in default-closed details.

## Primary sources read

PostgreSQL 17.6, tag `REL_17_6`, commit
`7885b94dd81b98bbab9ed878680d156df7bf857f`:

- `src/backend/optimizer/path/allpaths.c`: level-based `standard_join_search`,
  `set_cheapest`, and hook/GEQO selection above it.
- `src/backend/optimizer/path/joinrels.c`: legal smaller-set combinations,
  disjoint relation sets, `make_join_rel` and candidate paths.
- `src/backend/optimizer/util/pathnode.c`: `add_path`'s documented dominance
  criteria, including cost, path ordering, parameterization, rows and parallel safety.
- `COPYRIGHT`: PostgreSQL license; no product code is copied or adapted into the lab.

The bounded immutable links are on both pages. The case study distinguishes a list
of relation sets from a single winner per level and distinguishes source observations
from inference about losing alternatives. It does not claim exhaustive enumeration
of every syntactic join tree or a runtime-optimal plan. PostgreSQL 17's official
GEQO configuration documentation was retrieved: the default threshold is 12 FROM
items, with grouping/configuration qualifications and a planning-quality tradeoff.
There is no inference of a knapsack approximation guarantee for GEQO, nor of SQL
Server implementing PostgreSQL's planner.

Williamson and Shmoys, The Design of Approximation Algorithms, Section 3.1,
printed pages 65-67, and Exercise 3.1, printed page 77, were read from the authors'
electronic edition. The book presents nondominated pairs and a density prefix plus
best single. The lab uses a capacity-indexed table and continues after skipped jobs;
its original fractional-bound argument explicitly justifies that variant. Zero-value
jobs extend the positive-value source assumptions without improving any solution.
The book PDF is linked, not redistributed. Original prose is CC BY 4.0; original
lab code is MIT, with the license in its archive.

## Content and code review

EN/VI meanings were reviewed for contracts, recurrence/proof steps, numeric examples,
source claims, commands, predictions, observed results and limitations. Review
clarified that the exact-greedy case needs all eligible jobs to fit together, not
merely each job to fit individually. Added an explicit bridge from binary search,
BFS and Dijkstra invariants and a small dominance example where the source uses
nondominated cost/value pairs. Pre-merge review also separated each synthesis
self-check and its answer into its own immediate, default-closed panel.

Every take reads the previous item row; traceback skips ties and promises one
optimal feasible subset rather than a uniquely preferred subset. Rolling DP updates
downwards and returns only value. Density order uses BigInteger cross-products,
with original-index ties, avoiding floating-point collapse and long multiplication
overflow. A separate near-long-limit case checks this distinction. Selection does
not mutate input. Validation rejects duplicate/blank IDs, nonpositive cost, negative
value/capacity and total input-value overflow, including oversized jobs. Unlike the
previous distance lab, long.MaxValue is a valid value. Table guards reject rather
than silently replace an exact result with an approximation.

The exhaustive oracle enumerates subsets independently of DP/greedy; it shares
input validation and data types, not the optimization recurrence. Returned indices,
uniqueness, cost/value totals, optimal values and the half bound are checked.
The count-limited solution has its own subset oracle and bounded three-dimensional
table; the original half theorem is not asserted under the new count constraint.

## Verification completed

- `python scripts/check_all.py`: 48 repository tests; planner/catalog/links,
  generated coverage/navigation, EN/VI structure/code parity; all four labs checked
  from temporary source copies and extracted downloadable ZIPs. Every archived C#
  project built successfully. New lab: zero build warnings and errors.
- New lab `--check`: 12,226 inputs compared against exhaustive optima, including
  all 12,096 three-job inputs with costs 1-3, values 0-3 and capacities 0-6,
  120 deterministic seeded samples and 10 boundary/examples, plus rejection cases.
- All six C# fences are identical across EN/VI; five match lab files byte-for-byte.
  Code copied directly from page fences, including SDK/project setup, compiles and
  passes demo/check/experiment. The transfer program passes 720 count-limited cases
  and returns 8 on the motivating K=1 example.
- Experiment: 52 CSV rows from 13 controlled cases match all predicted optima,
  greedy/protected values and DP/subset counts. Capacity 3/7 and exact cost scaling
  variations were also executed and matched their worked answers.
- ZIP inventory and bytes match all 10 lab source, project, setup, guide and license
  files exactly; no bin/obj or other build artifacts.
- Local Chromium public-site diagnostic: 8 lesson pages, 8 language switches,
  8 previous/next clicks, 195 internal document links and 23 asset links;
  no runtime errors or third-party requests. Includes the staged ZIP and source links.
- Additional desktop/mobile checks: all 17 answer panels in each language start
  closed and toggle both ways. The main answer renders all five C# sources; transfer
  renders its sixth source. Mobile checks at 390px passed; Vietnamese mobile layout
  was visually inspected.
- Typography and `git diff --check`: passed. No em/en dashes or initially open
  answers in new pages or guides. Navigation and catalog coverage were regenerated
  through the repository script.

## Limits and publication

The finite suite supplements proofs; it cannot establish correctness for every input.
The experiments count different operation units and exclude validation/setup, not
elapsed time, peak memory, GC, database query performance or worker p99. No production
transaction/fairness system, PostgreSQL query execution, or elapsed-time benchmark
was run. Approximation/value estimates and independent-job assumptions need separate
validation against a real workload. Browser/ZIP verification targets the candidate
site locally. The new lesson is not claimed live on Pages before PR merge.
