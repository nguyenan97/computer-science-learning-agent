# Lesson 02 - Boundary search: from sorted arrays to time-window queries

**Study at your pace: trace → implement → test → transfer**

[Tiếng Việt](../../vi/lessons/boundary-search/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/boundary-search/dotnet-lab.zip)

The previous lesson asked whether an ID had appeared before. Now the data is sorted, and we need a different answer: **where does a condition first become true?** That boundary lets us count events in a time window without scanning every event for every query. The complete algorithm, its reasoning and worked exercises are on this page; the standard-library links are further reading.

## Selection and measurable outcomes

**Goal:** implement a correct lower boundary for sorted timestamps and reuse it to count `start <= timestamp < end`, including duplicates and missing endpoints. Explain why queries use logarithmic comparisons while inserting into a flat list can still take linear work.

You need indexed access, comparisons and loops. The half-open interval convention is explained below. If binary search is new, start with the numbered example rather than memorizing code.

| Block | Activity | Concrete output |
|---|---|---|
| 1 | Recall cost models and half-open intervals | Explain the included indices and the cost of a front insertion |
| 2 | Derive the partition and reconstruct the trace | Label both known regions and every update |
| 3 | Predict duplicate, empty and missing-target cases | Expected boundary for each case before running code |
| 4 | Implement and debug the C# lab | A lower boundary and window count checked against edge cases |
| 5 | Compare library contracts and count element reads | Explain equality search, insertion encoding and query/update cost |
| 6 | Transfer the window contract to event records and T-SQL | A query with matching endpoint semantics and an index explanation |
| 7 | Explain back and revisit one error | State the invariant and answer a fresh duplicate case without notes |

Take breaks and expand source reading according to your available research time. Every block can be traced on paper; running the lab is optional. Keep the core task bounded to sorted queries, then use the database section to understand the transfer rather than build a database application today.

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

Reconstruct the method, predict edge cases, trace and test, deliberately introduce/debug a branch error, then explain the correction. Two especially useful mistakes:

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

## Transfer to C#: search contracts and a runnable lab

C# is the implementation language for this lesson's runnable lab. The Python examples remain because CPython exposes a short, readable `bisect_left` implementation and its tests: compare the partition contract across languages, rather than add a Python dependency to your .NET work.

### BinarySearch finds a match; it does not promise the first duplicate

Both [`Array.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0) and [`List<T>.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0) require data sorted under the search comparer. A successful search returns a matching index, but the contract does **not** guarantee the first or last matching duplicate. A missing target returns the bitwise complement of its insertion position: decode a **negative** result with `~result`.

```csharp
long[] values = [10, 10, 20, 30, 30, 40];
int match = Array.BinarySearch(values, 30L);
Console.WriteLine(values[match]);

List<long> list = [.. values];
int result = list.BinarySearch(11L);
int position = result >= 0 ? result : ~result;
Console.WriteLine($"{result}, {position}");
```

This prints `30`, then `-3, 2`: 11 would be inserted at index 2. `-result` would produce 3 and be wrong. When a target is above the maximum, the insertion position is `Count`; it is a valid boundary but not an element you can read. An absent key has no duplicates to resolve, so this decoded position equals a lower boundary. A successful equality search provides no such first-duplicate promise. Do not subtract two successful `BinarySearch` results to count a window with duplicate endpoints.

### Implement the partition in C#

This is the full implementation from [the C# lab](../../labs/boundary-search/dotnet/README.md). It accepts arrays and `List<long>` through indexed `IReadOnlyList<long>` access:

```csharp
public static class BoundarySearch
{
    public static int LowerBound(IReadOnlyList<long> values, long target)
    {
        ArgumentNullException.ThrowIfNull(values);
        int lo = 0, hi = values.Count;
        while (lo < hi)
        {
            int mid = lo + (hi - lo) / 2;
            if (values[mid] < target)
                lo = mid + 1;
            else
                hi = mid;
        }
        return lo;
    }

    public static int CountWindow(IReadOnlyList<long> timestamps, long start, long end)
    {
        ArgumentNullException.ThrowIfNull(timestamps);
        if (end < start)
            throw new ArgumentException("end precedes start", nameof(end));
        return LowerBound(timestamps, end) - LowerBound(timestamps, start);
    }
}
```

The equality branch keeps the first duplicate as a candidate. `lo + (hi - lo) / 2` avoids adding two large `int` indices; `(lo + hi) / 2` can overflow in C#, whereas Python integers do not have that fixed-width limit. The methods compare `long` keys without subtracting them, so extreme timestamps do not cause arithmetic overflow. The logarithmic comparison claim still assumes constant-time `Count`, indexing and comparison; an arbitrary `IReadOnlyList` implementation need not satisfy those assumptions.

From `labs/boundary-search/dotnet`, with SDK 10.0.401:

```bash
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

The default run shows a lower boundary of 3 for 30 and window counts 3, 0 and 3 for `[10,30)`, `[30,30)` and `[11,39)`. Checks cover first duplicates, absent targets, empty/equal/reversed windows, negative and extreme keys, input preservation and .NET insertion encoding. They also search a virtual array with `int.MaxValue` positions without allocating it, and compare small cases against a scan. A failing check exits nonzero. Reimplement before comparing if useful; the worked answer is always available and lab completion is optional.

## Read the standard-library implementation

Python's official `bisect` implementation uses this partition idea. The following source slice is pinned so you can compare a stable implementation rather than a moving branch:

- [Lib/bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/bisect.py): find bisect_left; compare its equality branch with bisect_right.
- [Lib/test/test_bisect.py](https://github.com/python/cpython/blob/0b05ead877f909b7efe712db758012d9dbece7ce/Lib/test/test_bisect.py): select one duplicate and one missing-value case; predict the partition before reading the expected result.
- [Official bisect documentation](https://docs.python.org/3/library/bisect.html): read the partition definition, key semantics and Performance Notes.

**Reading answers:** bisect_left returns the boundary before equal values; bisect_right returns the boundary after equal values. The Python module can use a C implementation internally, so the installed interpreter need not execute the Python source body line by line. The contract remains the useful comparison.

For the cost experiment, compare element reads for targets below, inside and above the sequence; predict how doubling n changes the bound. Then count how many entries must move when inserting near the front. Search is O(log n), but an array-backed list insertion is O(n) because storage must shift. Sorting an unsorted batch once costs O(n log n) in the usual comparison model; that preparation is separate from the cost of each later query.

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

## Transfer to SQL Server: a time window over an index

The same membership contract maps directly to T-SQL: `ts >= @s AND ts < @e`. In a scratch database, this example preserves duplicate timestamps as distinct events:

```sql
CREATE TABLE dbo.Events
(
    event_id bigint IDENTITY(1, 1) NOT NULL PRIMARY KEY,
    ts datetime2(7) NOT NULL
);
CREATE INDEX IX_Events_ts ON dbo.Events(ts);

INSERT dbo.Events(ts) VALUES
('2026-10-06T10:00:00'),
('2026-10-06T10:00:00'),
('2026-10-06T10:10:00'),
('2026-10-06T10:30:00'),
('2026-10-06T10:30:00'),
('2026-10-06T10:40:00');

DECLARE @s datetime2(7) = '2026-10-06T10:00:00';
DECLARE @e datetime2(7) = '2026-10-06T10:30:00';
IF @e < @s THROW 50001, 'end precedes start', 1;

SELECT COUNT_BIG(*) AS event_count
FROM dbo.Events
WHERE ts >= @s AND ts < @e;
```

The expected count is **3**: both rows at start and the row at 10:10 are included; both rows at end are excluded. Equal bounds return zero. `BETWEEN @s AND @e` would include end and change the contract. Do not use a unique index on `ts` unless the domain forbids simultaneous events; timestamps and event identity answer different questions.

The range predicate is **sargable**: the indexed column is directly compared with compatible parameter types, allowing SQL Server to use index seek boundaries. A function such as `CAST(ts AS date)` around the column can prevent this direct range access; compute query bounds before the query instead. Sargability permits a seek but does not guarantee one: selectivity, statistics, table size and the optimizer determine the plan. Inspect an actual execution plan and `SET STATISTICS IO ON` when you run the optional SQL example.

Two lower boundaries in a random-access array give a count by index subtraction. A normal SQL Server index does not make `COUNT_BIG` an equivalent O(log n) operation: the execution may still visit all qualifying index entries to aggregate the count. Range location and range counting have separate costs. `datetime2` stores no timezone; use a consistent UTC convention or an explicitly normalized representation for both stored values and bounds. Match units and precision rather than add an arbitrary “epsilon” to an inclusive endpoint. The console lab checks integer-window logic and does not execute this SQL example.

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
- [List<T>.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0) and [Array.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0): duplicate-match and complemented insertion-position contracts.
- [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17): range predicates, index choices and query plans.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Lesson 01 - Big-O and data structures: removing duplicate order IDs in C#](../2026-10-05-cost-model/lesson.md) - Review how hidden work inside a loop determines its cost.
- [Technical topic notes](../../references/topic-notes.md) - Explore ordered indexes, query processing and algorithm design.

---

[← Previous: Lesson 01 - Big-O and data structures: removing duplicate order IDs in C#](../2026-10-05-cost-model/lesson.md) · [All lessons](../../README.md)
<!-- LESSON_NAVIGATION_END -->
