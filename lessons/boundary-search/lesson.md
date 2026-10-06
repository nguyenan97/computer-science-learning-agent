<!-- contract-version: 1 -->
# Lesson 02 — Boundary search: from sorted arrays to time-window queries

**One full day: 420 minutes · 360 minutes of study + 60 minutes of breaks**

[Tiếng Việt](../../vi/lessons/boundary-search/lesson.md)

The previous lesson asked whether an ID had appeared before. Now the data is sorted, and we need a different answer: **where does a condition first become true?** That boundary lets us count events in a time window without scanning every event for every query. The complete algorithm, its reasoning and worked exercises are on this page; the standard-library links are further reading.

## Selection and measurable outcomes

**Goal:** implement a correct lower boundary for sorted timestamps and reuse it to count `start <= timestamp < end`, including duplicates and missing endpoints. Explain why queries use logarithmic comparisons while inserting into a flat list can still take linear work.

You need indexed access, comparisons and loops. The half-open interval convention is explained below. If binary search is new, start with the numbered example rather than memorizing code.

| Elapsed minutes | Activity | Hands-on minutes |
|---|---|---:|
| 0–20 | Recall the previous cost model; check indices and interval notation | 10 |
| 20–70 | Understand the partition and reconstruct the worked trace | 20 |
| 70–80 | Break | 0 |
| 80–125 | Read the selected standard-library sources and answer the questions | 10 |
| 125–170 | Inspect the implementation; trace equal, missing and beyond-range targets | 40 |
| 170–200 | Lunch and rest | 0 |
| 200–275 | Implement lower_bound, predict cases and debug | 70 |
| 275–285 | Break | 0 |
| 285–330 | Count element accesses and compare query/update costs | 40 |
| 330–340 | Break | 0 |
| 340–375 | Implement count_window and the record/key variation | 35 |
| 375–420 | Explain the invariant, revisit errors and choose a review question | 10 |

This route reserves 235 of 360 study minutes for active practice. Adjust the reading and coding blocks to your experience; paper traces work when you cannot run Python. Keep the main task bounded to sorted in-memory queries rather than building a database today.

## Retrieval warm-up and prerequisite check

Think through three questions:

1. Which positions belong to `[lo,hi)`? **Answer:** lo is included, hi is excluded; `[1,3)` contains indices 1 and 2.
2. What changes when an element is inserted at the start of an array-backed list? **Answer:** existing elements must move one position to the right; fast search does not remove that work.
3. Why did one loop not prove linear time in Lesson 01? **Answer:** the work hidden inside the body matters. Here, accessing the midpoint and comparing keys also need explicit assumptions.

For `[2,4,4,9]`, the values smaller than 4 occupy only index 0. The first index whose value is at least 4 is therefore **1**. Try `[1,1,3]`, target 1: the boundary is **0**. If this is unclear, draw each value above its index and separate “smaller than target” from “at least target” before coding.

## Problem and prediction

A service stores sorted timestamps:

```text
timestamps = [10, 10, 20, 30, 30, 40]
query       = [10, 30)
```

The interval includes both events at 10 and the event at 20, but excludes both events at 30: the answer is **3**. A scan can count them correctly in O(n) comparisons per query. For many queries on the same sorted data, find two boundaries instead:

- First index at or after start: 0.
- First index at or after end: 3.
- Count: `3−0=3`.

A search that returns any matching 30 could return index 4, incorrectly including one event at the excluded endpoint. We need a partition boundary, not merely an equality match. Missing endpoints also need a useful answer: `[11,39)` contains 20,30,30, so its count is 3 even though neither 11 nor 39 appears.

## Foundation and mental model

Define `lower_bound(values,x)` as the first index i with `values[i] >= x`. If no such index exists, return n. It splits the sorted array into two parts:

```text
values[:i]   are all < x
values[i:]   are all >= x
```

Those expressions describe the partitions; the implementation does not create slices.

### Why use an unknown interval [lo,hi)?

Maintain `0 <= lo <= hi <= n` and these facts:

- Every index before lo is already known to hold a value < x.
- Every index at or after hi is already known to hold a value >= x.
- Only `[lo,hi)` remains to inspect; the boundary may be at hi.

At the start, lo=0 and hi=n, so the known regions are empty and the entire array is unknown. At the end, lo==hi: the two known regions meet, and that position is the answer. Returning n is safe; we return an index, not `values[n]`.

At midpoint mid:

- If `values[mid] < x`, sorted order proves all earlier positions are also too small. Move lo to `mid+1`.
- Otherwise, mid and all later positions are at least x. Move hi to mid. Keep mid as a possible boundary; an equal value may have earlier duplicates.

Each branch removes mid from the unknown region and strictly reduces hi−lo. This proves termination. Roughly halving the remaining region gives O(log n) comparisons for n>=2; empty/singleton inputs need only constant work. A random-access array and bounded comparison cost are assumptions. A linked list, costly key extraction or remote access changes the actual cost.

## Worked example: narrating decisions

For `[1,3,3,8]`, x=3:

| lo | hi | mid | value | Decision and reason |
|---|---|---|---|---|
| 0 | 4 | 2 | 3 | hi=2: equal belongs to the right partition; an earlier 3 may exist |
| 0 | 2 | 1 | 3 | hi=1: keep the earlier boundary candidate |
| 0 | 1 | 0 | 1 | lo=1: index 0 is too small |
| 1 | 1 | — | — | Return 1; the partitions now meet |

Returning 2 at the first equality would find a match but not the first match. The boundary definition determines the equality branch.

A target below the minimum, such as 0, repeatedly moves hi left and returns 0. A target above the maximum, such as 10, moves lo right and returns 4. Empty input starts with lo==hi==0 and returns 0 without reading any element.

## Guided lab: implement and observe the invariant

The complete Python implementation uses only indexing and comparison:

```python
def lower_bound(values, target):
    lo, hi = 0, len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

The midpoint is always a valid element while lo<hi. The code does not mutate values, copy subarrays or sort. You must supply data already sorted under the same ordering used for comparison. Checking sortedness on every query would itself cost O(n); establish the invariant when creating or updating the data instead.

### Predict cases before running or tracing

```python
values = [2, 4, 4, 9]
assert lower_bound(values, 4) == 1
assert lower_bound(values, 5) == 3
assert lower_bound(values, 0) == 0
assert lower_bound(values, 10) == 4
assert lower_bound([], 4) == 0
assert values == [2, 4, 4, 9]
```

A missing value has an insertion position: target 5 belongs between the last 4 and 9. This is why lower_bound remains useful without an equality match.

Use the 75-minute block to reconstruct the method (20), predict edge cases (15), trace and test (20), deliberately introduce/debug a branch error (15), then explain the correction (5). Two especially useful mistakes:

- `hi=mid-1`: on `[1,3]`, target 3, the first midpoint is 1; setting hi=0 loses the correct answer 1. The half-open invariant needs hi=mid.
- `lo=mid`: when the region has length one and the value is too small, mid==lo, so the interval never shrinks. Use lo=mid+1.

Other clues: wrong first duplicate → inspect equality; empty-input error → read elements only inside the nonempty loop; target above maximum fails → allow the answer n.

### Observe the cost without confusing it with timing

This sequence computes a value on indexed access and counts reads, so it can demonstrate scaling without allocating a large array:

```python
class Counted:
    def __init__(self, n):
        self.n = n
        self.reads = 0

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        if not 0 <= i < self.n:
            raise IndexError(i)
        self.reads += 1
        return i * 2

for n in (8, 1024, 65536):
    values = Counted(n)
    index = lower_bound(values, n)
    print(n, index, values.reads)
```

Worked output:

```text
8 4 3
1024 512 10
65536 32768 16
```

The target is near the middle of these synthetic sequences. Increasing n from 1,024 to 65,536 multiplies size by 64 but adds only six reads. Other targets can use a different number of reads; the worst-case growth remains logarithmic. This counts element accesses, not CPU instructions, wall-clock time or database page reads.

## Read the standard-library implementation

Python's official `bisect` implementation uses this partition idea. The following source slice is pinned so you can compare a stable implementation rather than a moving branch:

- [Lib/bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/bisect.py): find bisect_left; compare its equality branch with bisect_right.
- [Lib/test/test_bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/test/test_bisect.py): select one duplicate and one missing-value case; predict the partition before reading the expected result.
- [Official bisect documentation](https://docs.python.org/3/library/bisect.html): read the partition definition, key semantics and Performance Notes.

**Reading answers:** bisect_left returns the boundary before equal values; bisect_right returns the boundary after equal values. The Python module can use a C implementation internally, so the installed interpreter need not execute the Python source body line by line. The contract remains the useful comparison.

For the 45-minute experiment block, compare element reads for targets below, inside and above the sequence; predict how doubling n changes the bound. Then count how many entries must move when inserting near the front. Search is O(log n), but an array-backed list insertion is O(n) because storage must shift. Sorting an unsorted batch once costs O(n log n) in the usual comparison model; that preparation is separate from the cost of each later query.

## Independent challenge: time windows

Implement `count_window(timestamps,start,end)` for sorted integer timestamps. Count start-inclusive/end-exclusive events, keep input unchanged, accept empty data and equal endpoints, and raise ValueError for end<start. Avoid scanning, copying a slice or sorting per query.

The full solution subtracts two lower boundaries:

```python
def count_window(timestamps, start, end):
    if end < start:
        raise ValueError("end precedes start")
    return lower_bound(timestamps, end) - lower_bound(timestamps, start)

values = [10, 10, 20, 30, 30, 40]
assert count_window(values, 10, 30) == 3
assert count_window(values, 30, 30) == 0
assert count_window(values, 11, 39) == 3
assert count_window([], 10, 30) == 0
```

**Why subtraction works:** lower_bound(start) is the number of values strictly below start; lower_bound(end) is the number strictly below end. Removing the former leaves exactly the values at least start and below end. Duplicates at start are included; duplicates at end are excluded. Equal endpoints produce identical boundaries and count zero. Two logarithmic searches are still O(log n), with O(1) auxiliary space.

### Change the representation: event records and keys

Real events carry more than a timestamp. Python's bisect key is applied to records in the array, **not to the search target**:

```python
from bisect import bisect_left

events = [
    {"timestamp": 10, "id": "A"},
    {"timestamp": 20, "id": "B"},
    {"timestamp": 20, "id": "C"},
    {"timestamp": 30, "id": "D"},
]
key = lambda event: event["timestamp"]
left = bisect_left(events, 20, key=key)
right = bisect_left(events, 30, key=key)
assert (left, right, right - left) == (1, 3, 2)
```

Pass 20, not a full event record, as the target. The list must be sorted by timestamp. Use a consistent unit and timezone interpretation; mixing seconds/milliseconds or incompatible timestamp representations can silently invalidate the query. Key extraction happens on examined records; expensive keys may justify precomputed keys, with extra storage and synchronization on updates.

For frequent writes, a flat sorted list may be a poor fit. Ordered indexes or trees have their own query/update and storage costs. The partition reasoning transfers, but an in-memory comparison count alone does not predict database I/O, concurrency, collation or query plans.

## Rubric, feedback and explain-back

Use these checks to review your implementation:

| Check | What a good explanation contains | If unclear, try |
|---|---|---|
| Partition correctness | Both inequalities; empty, duplicate, missing and beyond-range cases | Draw numbered values and the two partitions |
| Termination/cost | Each branch shrinks hi−lo; logarithmic comparisons under random access | Trace a one-element unknown interval |
| Window behavior | Two boundaries; start included, end excluded | Duplicate both endpoints |
| Trade-off | Fast queries do not remove insertion shifts or expensive key work | Count moves for a front insertion |

Explain in your own words why equality moves hi, why returning n is valid and why an arbitrary matching midpoint is insufficient. If a case fails, preserve the smallest example, correct the rule and test a new example. This is more useful than memorizing the two update statements.

## Further questions and review plan

After a delay, reconstruct the partition and trace a new duplicate target without notes. Then change the event representation or endpoint values and explain the window result. Revisit sooner after an error and increase the gap when the reasoning is reliable.

Three questions for deeper reading: Why do left and right boundaries differ on equality? What work does a key function add? Why is insort still linear despite binary search? The linked standard-library implementation and docs answer these questions.

## Optional practice and worked answers

- `[1,1,3]`, target 1: boundary 0; no element belongs to the smaller partition.
- `[2,4,4,9]`, target 5: boundary 3; all three earlier elements are smaller.
- `[10,10,20,30,30,40]`, window `[20,40)`: count 3, from boundaries 2 and 5.
- The same array, window `[41,50)`: count 0, from boundaries 6 and 6.
- Reversed endpoints: reject the query before subtracting boundaries.
- Record search: the target is a key value; maintain the same ordering when updating the list.

## Read further

- [Python bisect documentation](https://docs.python.org/3/library/bisect.html): precise left/right partition contracts, key behavior and insertion costs.
- [CPython bisect source](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/bisect.py) and [tests](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/test/test_bisect.py): compare implementation choices with your trace and test design.
- [Python sorting how-to](https://docs.python.org/3/howto/sorting.html): establish sorted data, key functions and stable ordering before querying.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Lesson 01 — Cost models and stable deduplication](../2026-10-05-cost-model/lesson.md) — Review how hidden work inside a loop determines its cost.
- [Technical topic notes](../../references/topic-notes.md) — Explore ordered indexes, query processing and algorithm design.

---

[← Previous: Lesson 01 — Big-O and stable deduplication in C#](../2026-10-05-cost-model/lesson.md) · [All lessons](../../README.md)
<!-- LESSON_NAVIGATION_END -->
