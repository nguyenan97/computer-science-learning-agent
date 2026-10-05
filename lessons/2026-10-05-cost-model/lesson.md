# Lesson 01 — Big-O and data structures: removing duplicate order IDs

**Date:** 5 October 2026, Asia/Bangkok · **90 minutes**, optional **180+ minutes**.
**Topic:** advanced-algorithms.cost-model-membership.l1.
**IUH:** Advanced Algorithms `6001127`; connection to Advanced Database `6001111`.
[Tiếng Việt](../../vi/lessons/2026-10-05-cost-model/lesson.md) · [Lab](../../labs/cost-model/lab.py) · [Worked code](../../labs/cost-model/solution.py) · [Sources](../../lessons/2026-10-05-cost-model/sources.json).

**Main idea:** one visible loop can still cost O(n²) when each iteration searches an
increasingly long list. Changing the data structure can reduce total work, but check
output order, memory and hashing assumptions before claiming an improvement.

## Why this first lesson?

Your goals combine CS foundations, the IUH curriculum and useful current knowledge
for work. Advanced Algorithms requires complexity/performance analysis and algorithm
selection; Advanced Database includes indexing and hashing. This lesson is a tutor-selected
foundation connecting those outcomes, **not an official IUH lesson or prerequisite**.

There is no observed evidence of your proficiency or earlier work, and no recorded
review due. Compared with binary search, this topic requires less index/invariant
background; compared with transactions, it needs less setup and develops a cost model
first. Python/C#/SQL proficiency is not assumed. This is the first published daily lesson.

After reading, you can check whether you can:

1. Count membership work during deduplication instead of just counting loops.
2. Explain when a set reduces time and what additional memory it needs.
3. Preserve first-occurrence order and transfer the idea to duplicate counting.

All self-checks, labs and exercises are **optional, with immediately accessible answers**.
You do not need to submit work to receive the next lesson. Reading worked answers is
a valid study path; it does not itself establish independent proficiency.

## A 90-minute path

| Time | Activity | Reading-only alternative |
|---|---|---|
| 0–10 | Prerequisite self-check and bridge | Read questions/answers; slow down where needed |
| 10–35 | Cost model, Big-O, worst/expected/amortized | Follow the counting argument and table |
| 35–55 | Trace two deduplication approaches | Read the steps and invariant |
| 55–75 | Optional lab | Inspect verified output without installing Python |
| 75–85 | Challenge and trade-offs | Read the duplicate-counting solution |
| 85–90 | Recap and proposed review prompts | Read answers; take notes if useful |

Budgets apply to **one language version**, not reading both translations.

## 1. Self-checks with answers

**A.** How many elements and distinct IDs are in `['B2','A1','B2']`?

**Answer:** 3 elements, 2 distinct IDs. Input length n differs from distinct count u.

**B.** With `result=['B2','A1']`, how many comparisons might a sequential scan need
to determine whether C3 is present?

**Answer:** 2. Absence requires checking the entire list. Finding B2 could stop immediately.

**C.** Deduplicate `['B2','A1','B2','C3','A1']`, preserving first occurrence.

**Answer:** `['B2','A1','C3']`. Alphabetical order has the same values but violates the requirement.

**Bridge:** a list is an ordered sequence; `for value in values` visits its elements;
`==` compares equality; `append` adds at the end; `in` tests membership. A set's `add`
stores a value without creating a second equal entry. `{}` is an empty dictionary;
an empty set is `set()`. If syntax is unfamiliar, use these definitions and the trace;
no diagnostic submission is needed to continue reading.

## 2. Work scenario and specification

A job receives order IDs from logs, sometimes repeatedly. Return distinct IDs in
first-received order, without changing the original input.

```text
Input : B2, A1, B2, C3, A1
Output: B2, A1, C3
```

Assume string IDs and exact, case-sensitive equality: a and A are different IDs.
Do not silently trim or lowercase; identity rules are a business decision.

**Optional prediction:** “There is one for loop, so the algorithm must be O(n).”

**Answer:** not enough information. Inspect the work inside the loop; list membership
can scan the accumulated output.

## 3. Cost model and Big-O

Let n be input length and u the number of distinct IDs, with 0 ≤ u ≤ n. Initially
assume bounded-cost key comparison/hashing; revisit key length in the trade-offs.

Big-O describes an upper bound on how cost grows for large inputs, **not elapsed seconds**.
If T(n) ≤ C·n² for sufficiently large n and a constant C, then T(n) is O(n²).
Θ(n²) describes matching upper/lower growth bounds in that model; here it applies
to scanning deduplication with all-distinct input.

| Growth | Rough change in the expression when n doubles | Example under suitable assumptions |
|---|---:|---|
| O(1) | Unchanged | A bounded-cost operation |
| O(log n) | Adds a constant amount | Binary search on sorted data |
| O(n) | 2× | One scan |
| O(n log n) | Slightly more than 2× | Some comparison sorts |
| O(n²) | 4× | Comparing each item with many others |

This illustrates cost expressions, not guaranteed wall-clock ratios.

### Approach 1: scan the accumulated output

```python
result = []
for value in values:
    if value not in result:
        result.append(value)
```

For all-distinct input, each new element compares with every earlier result:

```text
0 + 1 + 2 + ... + (n-1) = n(n-1)/2
```

Thus worst-case cost is Θ(n²) with unit-cost comparisons. A bound using both n and
u is O(n(1+u)); small u can make this approach nearly linear. When all IDs are equal,
there are just n−1 comparisons after the first element. Not every input costs n².

### Approach 2: set for membership, list for output

```python
result = []
seen = set()
for value in values:
    if value not in seen:
        seen.add(value)
        result.append(value)
```

Hashing directs lookup to table locations rather than always scanning from the start.
With suitable hashing/equality and table management, lookup has expected O(1) cost;
insertion also involves amortized analysis because resizing can occasionally be expensive.
The overall process is expected O(n) under the key-cost assumptions. **This does not
guarantee every lookup is O(1)**: collisions or expensive keys can slow it down; unfavorable
cases can make the overall cost O(n²).

- **Worst case:** the most unfavorable allowed input/behavior within the stated model.
- **Expected:** an expectation under distribution/randomness assumptions, not every input.
- **Amortized:** spread cost over a sequence of operations, including expensive resizes;
  it is different from expectation and does not make every insertion cheap.

For strings of length L, initial hashing or equality can depend on L. Cached hashes
can reduce some work, but not every key/comparison is O(1) in a real workload.

### Memory and correctness

Both return an O(u) output list. **Excluding output**, scanning needs O(1) additional
state while hashing needs O(u) for seen. **Including output**, both use O(u), but the
hashing version has extra overhead. Same Big-O does not mean the same number of bytes.

Do not return `list(set(values))` when preserving first occurrence: sets **do not
promise insertion order**. One run accidentally returning the desired order does not
establish an ordering contract.

## 4. Worked trace and invariant

| value | result after processing | seen as a mathematical set, not an ordering |
|---|---|---|
| B2 | [B2] | {B2} |
| A1 | [B2, A1] | {B2, A1} |
| B2 | [B2, A1] | {B2, A1} |
| C3 | [B2, A1, C3] | {B2, A1, C3} |
| A1 | [B2, A1, C3] | {B2, A1, C3} |

**Invariant:** after each processed prefix, seen contains exactly the IDs in that
prefix; result contains each once, in first-occurrence order within the prefix.

Initially both are empty. For an already-seen ID, change neither. For a new ID, add
to seen and append to result. The invariant remains true; processing the entire input
therefore satisfies the specification.

**Optional question:** do n membership calls prove the algorithm always takes O(n)?

**Answer:** no. Calls are not primitive work: one call may perform several hash/equality
operations, and seen.add also costs something. The lab deliberately separates counts.

## 5. Reproducible optional lab

Standard-library Python, deterministic synthetic input; no database server, network,
or external package. The tutor ran **Python 3.12.14**, embedded SQLite **3.53.1**.
These are reproducibility versions, not a latest-production-version recommendation.

From the repository root:

```bash
cd labs/cost-model
python --version
python lab.py
python check.py --module solution.py
```

Without a runtime, inspect the trace/output below. A paper trace is not executed code.
Starter intentionally needs implementation; reading/running solution.py is available now.

**Step 1 — specification:** predict the order-ID output, then run if desired.
Checkpoint: `[B2,A1,C3]`. Explain that result preserves order while seen answers membership.

**Step 2 — count a model:** unique_scan explicitly counts equality; unique_hash counts
membership calls. For distinct inputs:

| n | Scan equality checks | Hash membership calls |
|---:|---:|---:|
| 128 | 8,128 | 128 |
| 256 | 32,640 | 256 |
| 512 | 130,816 | 512 |

Verified order-ID input uses **6 scan equality checks** and **5 hash membership calls**.
128 identical A1 IDs use **127 scan equality checks**.

**Checkpoint answer:** the distinct scan count equals n(n−1)/2; doubling n roughly
quadruples it. Hash membership calls equal n, not total hash-table work. This is not
an elapsed-time benchmark or a “1,000× faster” claim. Explicit scan counters model the
algorithm; they do not count every CPython list.__contains__ implementation optimization.

**Step 3 — implement only if desired:** fill unique_hash and duplicate_summary in
[starter.py](../../labs/cost-model/starter.py), then:

```bash
python check.py --module starter.py
```

Expected for a correct implementation: **4 tests pass**. [solution.py](../../labs/cost-model/solution.py)
contains full answers. Checks cover empty/duplicate/case sensitivity/order/input preservation,
collisions and an equality model that detects scanning rather than hashing. They cannot
prove every production workload is fast or establish the learner's reasoning.

**Debug:** duplicates remain → check seen updates; order wrong → do not return the
set; unhashable TypeError → choose a hashable key, such as a stable string ID, rather
than a mutable list/dict. Import failure → use the stated working directory.
NotImplementedError from an unchanged starter is intentional.

## 6. Changed-context challenge with full solution

**Optional task:** return IDs appearing more than once together with their frequencies,
in first-occurrence order, without changing input. The order example should produce
`[('B2',2),('A1',2)]`.

**Solution:** a dictionary stores frequency. Python guarantees dictionary insertion
order from version 3.7; updating an existing key does not move it to the end.

```python
def duplicate_summary(values):
    counts = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return [(value, count) for value, count in counts.items() if count > 1]
```

Expected O(n+u), simplified to O(n) because u≤n, under hashing/key assumptions; O(u)
memory. Empty input → []; all distinct → []; three x values → `[('x',3)]`.
check.py includes those cases.

**Optional rubric:** correct edge cases; preserved input/order; justified invariant
and complexity assumptions; honest independence/solution assistance; explanation of
memory/key/collision trade-offs. No required score or submission.

## 7. GitHub activity and verified implementation knowledge

Selected **python/cpython**, official implementation, **77,493 stars**, archived=false,
checked via GitHub API on 5 October 2026. Observed main commit:
`182f3231542e84fd1b0c795898f69f61fe35df0e`, **10:09:25 Asia/Bangkok**.
Teaching release pin: **v3.12.14 → 2abcf904b8dac8c999d2b3aac76681abb333798a**.
Stars are discovery metadata, not proof of quality/adoption. LICENSE includes PSF
license/history; API SPDX says NOASSERTION, which does not mean no license exists.
No upstream build or upstream suite was run; the tutor read a small slice and ran a local lab.

Alternative **dotnet/runtime** is official, 18,312 stars, archived=false at checking;
not selected because standard-library Python teaches this cost model with less setup.
This is not a judgment that .NET is worse. No downstream usage survey or upstream
benchmark was conducted.

Optional source-reading tasks, with answers:

- [listobject.c — list_contains](https://github.com/python/cpython/blob/2abcf904b8dac8c999d2b3aac76681abb333798a/Objects/listobject.c#L441):
  locate its loop and stopping condition. **Answer:** start at index 0, stop on equality
  or exhaustion; one membership call can involve many comparisons.
- [setobject.c — set_lookkey](https://github.com/python/cpython/blob/2abcf904b8dac8c999d2b3aac76681abb333798a/Objects/setobject.c):
  why does a hash lookup still have a loop? **Answer:** probing/collisions can require
  multiple locations, with hash and equality checks; hashing is not always one step.
- [test_set.py — test_contains/test_add](https://github.com/python/cpython/blob/2abcf904b8dac8c999d2b3aac76681abb333798a/Lib/test/test_set.py):
  inspect duplicate and unhashable cases. **Answer:** adding Q twice creates no duplicate;
  mutable lists are invalid keys and TypeError cases are tested.

**Current connection:** Python's 3.12-line docs were read for set/hashable and dictionary
ordering. The online page was labeled **3.12.15**, while the lab/pin is 3.12.14;
pinned docs confirm the semantics used here. Neither version observation establishes
latest support/security guidance.

## 8. A 180+ minute track

Add these to the 90-minute reading path:

### 25 minutes — source reading and cost model

Use the three targets above and describe “outer loop count × inner membership cost.”
**Model answer:** scan over distinct data sums 0…n−1; set lookup probes and can resize,
so expected/amortized costs need assumptions. Counted calls are not elapsed time.

### 25 minutes — SQL on a small equivalent dataset

```bash
python lab.py --sql
```

```sql
SELECT order_id, COUNT(*)
FROM events
GROUP BY order_id
ORDER BY MIN(pos);
```

**Answer:** `B2:2, A1:2, C3:1`. To retain only duplicates, add `HAVING COUNT(*) > 1`
before ORDER BY → B2:2, A1:2. pos explicitly stores ingestion order. SQL results
have no guaranteed ordering without ORDER BY. GROUP BY does not prove the engine uses
the same algorithm as Python: sorting/indexing/other plans can be used. Real workloads
require query-plan, cardinality, index and I/O analysis; do not infer SQL performance here.

### 25 minutes — intentional collisions

```bash
python lab.py --collisions
```

The worked lab creates Key objects whose __hash__ always returns 1. On the verified
runtime, 100 calls caused **11,964 equality checks**, with correct output. That exact
count is a runtime observation, not a universal bound. **Answer:** collisions affect
cost without necessarily breaking correctness; equal hash values do not imply equal keys.

### 15 minutes — choosing a design for a large job

**Optional task:** 10 million records, long IDs and limited RAM. Is a set always best?

**Answer:** no. Consider u, ID length, object overhead and how long seen must retain
state. For large u consider external sorting/deduplication, database uniqueness or
disk-backed state. Each has ordering/I/O/concurrency costs. RAM sets may suit small keys,
moderate u and fast lookup; n alone does not determine a winner. Deduplication before
an API call does not guarantee exactly-once behavior: concurrency, crashes and retries
also require appropriate idempotency/unique constraints, a future topic.

For more than 180 minutes, optionally run `python lab.py --timing`. The script uses
timeit repeats and fixed input; the tutor **did not run timing** and reports no speedup.
Measurements include instrumentation and depend on interpreter/hardware/cache/data;
they do not replace a job-specific benchmark.

## 9. Recap and proposed review, with answers

1. **Is one for loop always O(n)?** No: its body can grow with accumulated data.
2. **Why both list and set?** Membership efficiency versus ordered output.
3. **Is set always O(1)?** No: assumptions, collisions, resizing and key costs matter.
4. **Must O(n) beat O(n²) for small n?** No: constants, overhead and actual inputs matter.
5. **Does reading answers mean mastery?** No; you can still use them and read the next lesson.

Proposed review hooks, not actual scheduled reviews: on another day reconstruct
n(n−1)/2 for new distinct data or count duplicates in event IDs. Answers use the
same scan argument/dictionary solution above. After seeing answers, use a fresh unseen
task if requesting an independent assessment.

Possible next lesson: **binary search and invariants** if comparisons/loops are comfortable;
otherwise first read **arrays, index access and loops**. This is conditional planning,
not verified prerequisite mastery. Invoke the same skill for the next lesson; no submission needed.

## 10. Source roles and verification boundary

- **Curriculum:** condensed IUH Master 2020, Advanced Algorithms/Advanced Database,
  read locally 5 October 2026. Official scope within the repo; original PDFs/current
  institutional rules were not rechecked.
- **Theory:** MIT OCW 6.006 Fall 2011, [Lecture 9 Hashing II](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf),
  pages 1–3 read 5 October 2026: expected lookup, load factor, resizing and amortization.
  Chaining illustrates theory; CPython sets use open addressing, a different implementation.
- **Official technical:** [Python set/dict docs](https://docs.python.org/3.12/library/stdtypes.html#set-types-set-frozenset),
  [pinned stdtypes.rst](https://github.com/python/cpython/blob/2abcf904b8dac8c999d2b3aac76681abb333798a/Doc/library/stdtypes.rst)
  and CPython source/tests/license above; relevant sections read 5 October 2026.
- **SQL semantics:** [SQLite SELECT](https://www.sqlite.org/lang_select.html), grouping/ordering
  sections read 5 October 2026; local equivalent executed, not a SQL Server benchmark.
- **Tutor synthesis:** order-ID scenario, topic choice, budgets, rubric and original lab.
  Not a scientific claim about optimal study duration; no CPython code is vendored.

The agent ran the reference lab and 4 tests. No learner submission or assessment exists.
[sources.json](../../lessons/2026-10-05-cost-model/sources.json) preserves hashes/pin/metadata; [observations](../../lessons/2026-10-05-cost-model/agent-observations.txt)
are agent output, not learner progress.
