<!-- contract-version: 1 -->
# Boundary search: from sorted arrays to time-window queries

**Session:** sample-boundary-search · **Topic:** `advanced-algorithms.boundary-search.l1` · **Course:** Advanced Algorithms `6001127` · **Type/status:** core / generated · **Checked:** 2026-10-05. This is a reviewable example, not an assigned or completed learner lesson. [Record](record.json) stays outside real progress.

## Selection and measurable outcomes

The [curriculum](../../curricula/iuh/master/curriculum.md#advanced-algorithms--6001127) asks learners to analyze complexity, evaluate practical performance and select algorithms. Binary boundary search is an **instructor-selected foundation** for those outcomes; the curriculum does not explicitly prescribe this lesson or its prerequisites. It prepares later ordered indexing/query lessons without equating an array with a database B-tree.

The real state is empty, so no previous knowledge or due reviews are assumed. No core records exist to duplicate. In a live session, first run the planner and check the learner's goals, time/tools and diagnostic below; this generated sample is conditional on those answers. Prefer a prerequisite bridge if needed rather than labeling a new learner an expert.

By the end, independently:

1. State and preserve the partition invariant for `lower_bound`, including duplicates, empty input and missing targets.
2. Implement it without slicing/mutation and justify a logarithmic comparison/access bound.
3. Transfer the invariant to count events in a half-open time interval, explaining duplicate endpoint behavior and update-cost limitations.

**Short ~25 min:** 3 diagnostic, 6 model/example, 10 guided checkpoints, 4 independent window attempt, 2 exit; defer repo deep reading. **Standard ~55 min:** 5 diagnostic, 10 model/example, 20 lab, 10 challenge, 5 repo, 5 feedback/exit. **Extended ~85 min:** standard plus 15 record/key variant and 15 source/experiment. These budgets are planning heuristics, not scientific ratios. Record in_progress if the agreed work needs another day.

## Retrieval warm-up and prerequisite check

Without notes: what does a half-open interval `[lo, hi)` include? What happens to array indices after inserting at the start? Trace a loop that repeatedly halves a positive integer. With history, replace one prompt with a due-review question and save its observed response; do not clear a review just by reading it.

Diagnostic: for `[2,4,4,9]` list the indices satisfying value < 4, then give the insertion boundary before the first 4. Trace `lo=0,hi=4,mid=2`; can `hi=mid` still contain a valid answer? Explain why sorted order is essential.

If indexing/loop/sorted-order reasoning is weak, draw the list with numbered positions, partition a three-element list by hand and retrace with one duplicate. Recheck on `[1,1,3]` before coding. If still weak, make today a prerequisite-only session. Do not infer a score; store actual answers and hints.

## Problem and prediction

A service stores sorted event timestamps (integers, with duplicates). You need many queries “how many events occurred from start inclusive to end exclusive?” Scanning works but touches every event per query. Predict whether a binary search for “an equal timestamp” is enough when an endpoint repeats. Spend at most a couple of minutes trying a rule, then contrast it with the example. Novices may start with the example immediately.

## Foundation and mental model

**Foundational theory:** Maintain `0 <= lo <= hi <= n`; all indices before `lo` have value < x; all indices at/after `hi` have value >= x. The unknown partition is `[lo,hi)`. At `lo==hi` the partition boundary is known, including n when all values are smaller. Sorted input and a consistent ordering are required.

At midpoint m: if value < x, discard through m; otherwise retain m as a possible boundary and discard from m onwards from the unknown interval. Each step reduces its size roughly by half. Random-access arrays therefore need O(log n) element comparisons/accesses, O(1) auxiliary space. This does not make insertions O(log n): shifting list elements can cost O(n). Unsorted data, expensive access/key functions or special ordering values can change the assumptions.

**Current implementation connection, verified pinned baseline:** CPython `bisect_left` finds an insertion partition rather than testing equality. Its `key` parameter applies to array records but **not** the search x; `insort` search remains logarithmic while insertion is linear. These facts were read in the official code/docs at the pinned release, not inferred from generated code. This historical pin is not a current support/security recommendation; recheck the runtime appropriate to a live lesson.

**Instructor synthesis:** boundary reasoning transfers to range queries; array complexity alone cannot predict a database query plan, write amplification, collation or disk I/O.

## Worked example: narrating decisions

For a different example `[1,3,3,8]`, x=3:

| lo | hi | mid | value | Decision and justification |
|---|---|---|---|---|
| 0 | 4 | 2 | 3 | hi=2: equality belongs to the right partition; an earlier 3 may exist |
| 0 | 2 | 1 | 3 | hi=1: keep searching the earlier boundary |
| 0 | 1 | 0 | 1 | lo=1: index 0 is strictly smaller and cannot be the boundary |
| 1 | 1 | — | — | Return 1; both partitions satisfy the contract |

Why not immediately return mid on equality? That gives an arbitrary matching index, not necessarily the boundary. Explain this difference before moving to code. This example teaches the guided function; the optional window solution is available below.

## Guided lab: implement and observe the invariant

**Goal:** implement boundary search and justify its behavior. **Environment:** Python 3.12.x, standard library only, Linux/macOS/Windows shell equivalents; no database, network, packages or datasets needed. Locally verified on Python 3.12.14. Data is deterministic integer sequences generated by the checkpoint script. Python serves the partition objective with less setup here than SQL Server/.NET; the repo's default engineering stack remains available for later lessons.

From repo root:

```bash
cd labs/boundary-search
python --version
python observe.py
```

If Python 3.12 is unavailable, use an installed compatible runtime and record its version, or do paper traces; neither an unrun command nor paper trace counts as a code execution. The upstream CPython build is not required.

1. **Establish the specification.** Predict `bisect_left([2,4,4,9],4)` and with x=5 before running `observe.py`. Check observed positions against the left/right inequalities. Explain why a missing value still has a valid boundary. Checkpoint: duplicate boundary is 1; missing target 5 has boundary 3.
2. **Separate asymptotics from timing.** Predict how element reads change from n=8 to 1024 to 65536. Run the observer and record index/read counts. Checkpoint: indices 4/512/32768 and reads 3/10/16 on the verified runtime. These are deterministic element accesses, not universal runtime speedups. Explain why list insertion and expensive keys are different costs.
3. **Trace before implementing.** On paper, trace x=0 and x=10 for `[2,4,4,9]`; include empty input. Checkpoint: each iteration decreases `hi-lo`; terminating boundaries are 0 and 4. Explain why `hi=mid-1` can lose the half-open invariant.
4. **Fill the faded example.** Edit only `lower_bound` in `starter.py`: initialize the unknown interval; loop while it is nonempty; compute midpoint; choose the update from the partition condition; return the shared boundary. Keep the input unchanged and do not use slicing or built-in search. Predict duplicate and all-smaller cases before running checks.
5. **Self-check and debug.** Run the guided checks below. They compare with the standard-library oracle across sorted multisets of lengths 0–6, verify the partition/input preservation and reject linear-access/slicing solutions on larger data. Expected after a correct implementation: 2 tests pass. The unedited starter intentionally raises NotImplementedError. For a failure, use the smallest printed counterexample and trace lo/hi/mid; do not paste the oracle into the implementation.

```bash
python check.py --stage guided
```

After running, explain which branch preserves each part of the invariant, what the access-budget test measures and what it cannot establish (wall-clock speed, arbitrary comparator semantics). Save your implementation revision, a trace and the actual output for assessment.

Common debug paths: infinite loop → check strict interval shrinkage; wrong duplicate index → equality branch; empty-list IndexError → loop condition; target > max fails → allow returning n; source import/path error → run from the stated lab directory; tool failure → record version/message and use the paper trace while repairing the environment.

## GitHub repository activity and evaluation

**Chosen:** [python/cpython](https://github.com/python/cpython), official Python implementation, **77,489 stars**, `isArchived:false`, checked 2026-10-05 from GitHub HTML. Latest observed default-branch commit: [5fecd448…](https://github.com/python/cpython/commit/5fecd448bb120378978a37dde65dfce233d88c0d), 2026-10-05 01:49:56 UTC. GitHub API unavailable; exact embedded fields/targets/hashes are in [repository evidence](repository-evidence.json). Pinned teaching release **v3.12.7 → 0b05ead877f909b7efe712db758012d9dbece7ce**. This release is a reproducibility baseline, not a latest-release claim.

Maintainer authority is official Python; project identity establishes practical implementation relevance, while a quantified downstream usage survey was not done. Read docs expose preconditions/performance notes, implementation is small, tests include duplicates, random cases, slicing bounds and key semantics; no upstream benchmark or full build was run. PSF license text was read; no upstream code is vendored here. Entire CPython is complex to build, so restrict reading to four files.

Default-stack alternative `dotnet/runtime` is official and highly starred; its dated metadata and rejection rationale are in the evidence JSON. It is a valid future C# activity, but build/test setup adds cost without improving this small partition objective. Popularity did not determine the selection.

Use these precise pinned targets (defer deeper reading in short mode):

- [Lib/test/test_bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/test/test_bisect.py): read `TestBisect.precomputed` cases and `test_precomputed`, `test_random`, `test_lookups_with_key_function`. Infer the difference between left/right boundaries **before** looking at implementation. Pick one duplicate case and explain the inequalities.
- [Lib/bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/bisect.py): trace `bisect_left` and compare `bisect_right`. Explain why Python functions may be replaced by `_bisect` at import; the observer uses the installed interpreter implementation, not this historical Python file.
- [Doc/library/bisect.rst](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Doc/library/bisect.rst): read `bisect_left`, key semantics and Performance Notes. Predict a key-record search where x is already a key; connect comparator cost and insertion cost to the model.
- [LICENSE](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/LICENSE): check license before any reuse. Source reading is enough for this lab; you need not clone/build CPython.

Network fallback: use the local lab and state that upstream targets were not available to you. Do not pretend to read tests you could not open.

## Independent challenge: time windows

Optionally try without hints: implement `count_window` in `starter.py` for sorted integer timestamps. Contract: count `start <= t < end`, retain input, accept equal endpoints/empty data and raise ValueError when end < start. Avoid a scan, copying a slice or sorting per query; reuse partition reasoning. First design at least three tests covering duplicate endpoints, an empty window and missing endpoints. Predict each result before running.

```bash
python check.py --stage all
```

Expected after your attempt is correct: 4 tests pass. This is a near-to-changed-context transfer task, not proof of transfer to all database systems. **Extended variant:** design event records with a timestamp key, distinguish a timestamp x from a full record argument, and explain what breaks with unsorted inputs or timezone-inconsistent timestamps. Propose an update-heavy workload where a sorted flat list is a poor choice; compare with an index without claiming identical complexity constants.

Hints and the full worked solution are accessible below; attempting or submitting work is optional. Record actual hint use; assisted success is not independent evidence.

## Rubric, feedback and explain-back

| Outcome | Evidence / success criteria | Feedback and next check |
|---|---|---|
| Partition correctness | Empty, duplicate, missing and beyond-range cases; both inequalities; no mutation | Smallest counterexample; correct branch and retrace a new case |
| Reasoning and complexity | Explain invariant preservation/termination; logarithmic access test; distinguish insertion cost | If “binary search makes inserts logarithmic”, predict an insertion shift count |
| Independence and transfer | New window function/tests without hints; duplicate endpoints and validation | Log hints/errors; change endpoint/data context before reassessment |
| Explanation | Mechanism, assumptions, counterexample and relevant trade-off | Ask why returning any equality match is insufficient; compare records versus scalar keys |

Use qualitative outcomes (needs_support/developing/independent/unassessed). No fixed score threshold. A passing suite is one artifact, not a score or mastery claim. For each error record the original response, hint/feedback, revised explanation and a fresh attempt.

Explain-back: state the invariant in your own words; explain why the equality branch matters; defend your data structure for many reads versus many inserts. Exit ticket without notes: (1) reconstruct the partition for x absent; (2) predict a window with duplicated endpoints; (3) explain why a database ordered index is not a Python list and what additional cost model you would need.

## Research sources and review hooks

- **Curriculum source:** Advanced Algorithms `6001127`, local canonical outcome section; read 2026-10-05. Defines complexity/selection outcomes, not the exact chosen sequence.
- **Foundational/official implementation:** pinned CPython source/tests/docs above; directly read 2026-10-05. Establishes partition contract, comparator/key semantics and insertion trade-off; no latest-support assertion.
- **Learning research synthesis:** [Deans for Impact 2015 PDF](https://github.com/carpentries/instructor-training/blob/50745001271700a108de0622d80341965e249e5b/episodes/files/papers/science-of-learning-2015.pdf), questions 1–4, directly read 2026-10-05; supports scaffolding, retrieval, spacing and structural transfer. Primary paper access limits are in the [research report](../../research/learning-science-review.md).
- **Instructor synthesis:** diagnostic branch, this trace/lab, time budgets and rubric are designs to evaluate, not proven optimal methods.

After observed completion, choose a next due date with the learner based on performance and retention goal. Prompt A: reconstruct invariant and predict a different duplicate boundary unaided. Prompt B later: implement/justify a changed-context window query and compare an update-heavy design. If wrong/hinted, correct the misconception and retry sooner; if independent with explanation, consider a longer interval. Keep actual scheduled date, observation date and next-date reason. No scheduled review or mastery has been written for this unassigned sample.

For an actual assignment, create a new private session and copy the starter to its workspace. The public sample record remains outside real state; do not import its sample ID.

## Optional practice and worked answers

Reading only is valid; no task or submission is required to request another lesson.
Try the questions first if useful, or read the answers immediately. Solution-assisted
work does not establish independence.

- Warm-up: `[lo,hi)` includes lo and excludes hi; insertion at the front shifts old
  indices by one. Repeated integer halving takes logarithmically many iterations.
- Diagnostic: `[2,4,4,9]` has values <4 only at index 0; the boundary is 1. For
  mid=2 with equality, hi=2 retains the earlier boundary; the boundary itself may
  equal hi. Sorted order ensures discarded partitions satisfy their inequalities.
  Bridge recheck `[1,1,3]`, target 1 gives boundary 0.
- Missing/beyond-range traces: target 0 returns 0, target 10 returns 4; empty input
  returns 0. Each update shrinks hi-lo. `hi=mid-1` can skip a valid boundary: `[1,3]`,
  target 3 would incorrectly terminate at 0 after mid=1.
- Full guided and window implementation: [worked code](../../labs/boundary-search/mentor/solution.py).
  Initialize lo=0, hi=n; equality moves hi to mid, values < target move lo to mid+1.
  For a window subtract `lower_bound(end)-lower_bound(start)`; reject end<start.
  Two searches use O(log n) accesses and O(1) extra space.
- Window tests on `[10,10,20,30,30,40]`: [10,30) counts 3; [30,30) counts 0;
  [11,39) counts 3. Empty input counts 0; reversed endpoints raise ValueError.
- Exit answers: invariant partitions are <x before lo and >=x at/after hi. Returning
  an arbitrary equal midpoint loses the first duplicate. With records and a key,
  search x is already the key. Flat-list insertion is O(n); a database index also
  depends on page I/O, concurrency and its update/query cost model.
