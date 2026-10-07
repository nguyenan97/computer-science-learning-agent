# Lesson 02 - Boundary search with binary search and time-window counts

[Tiếng Việt](../../vi/lessons/boundary-search/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/boundary-search/dotnet-lab.zip)

Lesson 01 asked whether an ID had been seen before. With sorted data, you can also ask: **where does a condition first become true?** Finding two such positions lets you count events in a time window without scanning every event for every query. Apache Kafka's time index also uses binary search, but it searches a summary index before reading the original records.

**Goal:** implement a correct lower boundary for sorted timestamps and reuse it to count `start <= timestamp < end`, including duplicates and endpoints that are not in the data. Explain why a query costs a logarithmic number of comparisons, why inserting into an array-backed list can still cost linear work, and how a production system (Kafka) adapts boundary search to its storage. You need indexed access, comparisons and loops. Each section tells you what to do and for how long.

## Main concepts

- **Binary search.** Compare the middle element of a sorted array with the target to eliminate about half the remaining region. Repeat until the result is determined.
- **Lower bound.** The first position with a value greater than or equal to `x`, or the array length if no such value exists. For `[2, 4, 4, 9]` and `x = 4`, the lower bound is position 1.
- **Half-open interval `[a, b)`.** It includes `a` and excludes `b`. Adjacent time windows `[10, 20)` and `[20, 30)` count an event at 20 exactly once.
- **Loop invariant.** A statement that holds before the loop and is preserved by every iteration. Here, all elements before `lo` are smaller than the target; this helps prove that the returned position is correct.
- **Cost model and O(log n).** Count element reads and assume each read and comparison costs O(1). Halving the search region gives an O(log n) upper bound on reads rather than linear growth in n; Big-O is an asymptotic upper bound, not the exact read count of each query.

## 1. Recall and prerequisite check

**Recall · about 20 minutes.** Answer from memory, then open each answer. The first question comes from Lesson 01. **Finish when:** you know which question needs another read.

1. Why can a single loop that calls `List.Contains` take quadratic time?

<details>
<summary>Answer</summary>

On all-distinct input the result grows from 0 to n-1 elements. Each miss scans the whole current result, so the total is `0+1+...+(n-1) = n(n-1)/2` comparisons. Counting loops alone hides the work inside `Contains`.

</details>

2. Which positions belong to `[lo, hi)`?

<details>
<summary>Answer</summary>

`lo` is included and `hi` is excluded. `[1, 3)` contains positions 1 and 2.

</details>

3. What happens when you insert an element at the start of an array-backed list?

<details>
<summary>Answer</summary>

Every existing element moves one slot to the right. Fast search does not remove that work.

</details>

Warm-up: in `[2, 4, 4, 9]`, which position is the first value that is at least 4? Repeat for `[1, 1, 3]` and target 1.

<details>
<summary>Answer</summary>

For the first array, only index 0 is smaller than 4, so the boundary is **1**. For the second, nothing is smaller than 1, so the boundary is **0**. If this feels unclear, write each value above its index and draw a line between "smaller than target" and "at least target" before reading code.

</details>

## 2. Problem and prediction

**Foundations · about 50 minutes for sections 2-4.** Predict the results, trace the search on paper and reconstruct the invariant. **Finish when:** you can explain the invariant of section 3 without notes.

A service stores sorted timestamps:

```text
timestamps = [10, 10, 20, 30, 30, 40]
query       = [10, 30)
```

Predict how many events the window includes and which two boundaries you need.

<details>
<summary>Answer</summary>

The window includes both events at 10 and the event at 20, and excludes both events at 30. The answer is **3**. For the two boundaries:

- First position at or after `start` (10): 0.
- First position at or after `end` (30): 3.
- Count: `3 - 0 = 3`.

</details>

A scan counts correctly but costs O(n) comparisons per query. For many queries on the same sorted data, two boundary searches avoid repeating the scan.

A plain "find 30" search may return position 4, the second 30, and wrongly include an event at the excluded endpoint. You need a **partition boundary**, not just an equality match. Endpoints missing from the data need a useful answer too: `[11, 39)` contains 20, 30 and 30, so the count is 3 even though neither 11 nor 39 appears.

## 3. The lower bound and the unknown interval

Define `lowerBound(values, x)` as the first index `i` with `values[i] >= x`, or `n` if there is none. It splits the sorted array:

```text
values[:i]   are all < x
values[i:]   are all >= x
```

Those expressions describe the two parts; the code does not create slices.

### Why keep an unknown interval [lo, hi)?

Maintain `0 <= lo <= hi <= n` and these facts:

- Every position before `lo` is known to hold a value `< x`.
- Every position at or after `hi` is known to hold a value `>= x`.
- Only `[lo, hi)` is still unknown. The boundary may be exactly at `hi`.

At the start `lo = 0` and `hi = n`: nothing is known, the whole array is unknown. At the end `lo == hi`: the two known regions meet, and that position is the answer. Returning `n` is safe because you return an index, not `values[n]`.

At the midpoint `mid`:

- If `values[mid] < x`, sorted order proves every earlier position is also too small. Move `lo` to `mid + 1`.
- Otherwise `mid` and everything after it is at least `x`. Move `hi` to `mid`. Keep `mid` as a possible answer: an equal value may have earlier duplicates.

Each branch removes `mid` from the unknown region, so `hi - lo` strictly shrinks. That proves termination. With n unknown elements, at most `floor(n / 2)` remain after one iteration. The largest possible number of reads for `n >= 1` is therefore `floor(log₂(n)) + 1`, which is O(log n); empty input reads no elements.

For example, `log₂(8) = 3` corresponds to the halvings `8 -> 4 -> 2 -> 1`; `floor` rounds down to an integer. The algorithm may still read the last remaining element, giving a bound of 4 reads for 8 elements and 17 for 65,536. Doubling n adds one to this bound; an individual query can use fewer reads.

This model assumes `values[i]` and comparisons cost O(1). Arrays and `List<T>` provide that indexed-access cost, but the `IReadOnlyList<T>` interface alone does not promise it. A linked list, expensive key extraction or a remote lookup changes the cost analysis.

### Narrated trace

For `[1, 3, 3, 8]` and `x = 3`:

| lo | hi | mid | value | Decision and reason |
|---|---|---|---|---|
| 0 | 4 | 2 | 3 | hi = 2: an equal value belongs to the right part; an earlier 3 may exist |
| 0 | 2 | 1 | 3 | hi = 1: keep the earlier candidate |
| 0 | 1 | 0 | 1 | lo = 1: position 0 is too small |
| 1 | 1 | - | - | Return 1; the two parts meet |

Returning 2 at the first equal value would find a match but not the first match. The equality branch is what makes this a boundary search.

A target below the minimum (say 0) keeps moving `hi` left and returns 0. A target above the maximum (say 10) keeps moving `lo` right and returns 4. An empty input starts with `lo == hi == 0` and returns 0 without reading any element.

## 4. Implement it in C#

This is the full implementation from [the C# lab](../../labs/boundary-search/dotnet/README.md). It accepts arrays and `List<long>` through indexed `IReadOnlyList<long>` access.

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

Why it is written this way:

- The equality branch (`hi = mid`) keeps the first duplicate as a candidate.
- `lo + (hi - lo) / 2` avoids adding two large `int` indices; `(lo + hi) / 2` can overflow in C#.
- Keys are compared, not subtracted, so extreme `long` timestamps cannot overflow.
- The method never changes the input, copies a slice or sorts. Checking sortedness on each query would itself cost O(n), so establish the sorted order when you create or update the data.

**Why subtracting two boundaries works.** `LowerBound(start)` is the number of values strictly below `start`. `LowerBound(end)` is the number strictly below `end`. Subtract the first and you keep exactly the values that are at least `start` and below `end`. Duplicates at `start` are included, duplicates at `end` are excluded, equal endpoints give identical boundaries and count 0. Two O(log n) searches are still O(log n), with O(1) extra space.

**Break · 10 minutes.** Leave the screen.

## 5. Library contracts and sources

**Source reading · about 45 minutes.** Compare the two search APIs, run the example and answer the three questions below. **Finish when:** each answer has a claim, a supporting source and a limit.

Sources for this block:

- [`Array.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0) and [`List<T>.BinarySearch`](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0): sorted-input requirement, duplicate behavior and the complemented result.
- [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17): range predicates, index choices and query plans (used in section 9).

`BinarySearch` finds **a** match, not necessarily the first duplicate. Both methods require data sorted under the search comparer. A successful search returns a matching index, but the contract does **not** say which of several equal values. A missing target returns the bitwise complement of its insertion position, so decode a **negative** result with `~result`.

```csharp
long[] values = [10, 10, 20, 30, 30, 40];
int match = Array.BinarySearch(values, 30L);
Console.WriteLine(values[match]);

List<long> list = [.. values];
int result = list.BinarySearch(11L);
int position = result >= 0 ? result : ~result;
Console.WriteLine($"{result}, {position}");
```

This prints `30`, then `-3, 2`: 11 would be inserted at index 2. `-result` would give 3, which is wrong. A target above the maximum has insertion position `Count`, a valid boundary but not an element you can read. For an absent key this decoded position equals the lower bound. For a successful match there is no first-duplicate promise, so do not subtract two successful `BinarySearch` results to count a window with duplicate endpoints.

Three questions:

1. Why is a plain equality search not enough for window counts?

<details>
<summary>Answer</summary>

With duplicates it can return any matching position, so subtracting two results can include or drop events at the endpoints. You need the first position at or after each endpoint, which is a partition boundary.

</details>

2. How do you turn the result of `List<T>.BinarySearch` into a lower bound when the key is absent?

<details>
<summary>Answer</summary>

Decode the negative result with `~result`. That is the insertion position, which for an absent key is exactly the first position holding a larger value.

</details>

3. What assumptions make the logarithmic claim true?

<details>
<summary>Answer</summary>

Data sorted under the same ordering used by the comparison, constant-time indexed access, and constant-time comparison. A linked list, an expensive key function or a remote lookup breaks the claim.

</details>

## 6. Reading real code: Kafka's time index

**Code reading · about 45 minutes.** Follow the linked Kafka functions, trace the small example and compare it with the lesson's algorithm. **Finish when:** you can explain why Kafka searches a sorted summary first, then scans records whose timestamps need not be sorted.

The problem is familiar from any event stream: a consumer asks "at which offset can I start reading for this timestamp?" The project is [apache/kafka](https://github.com/apache/kafka), read at commit `8ed535f41c2a8a783e64a3b4ff9468ab682959b8`.

**The product problem.** A partition is an append-only sequence of messages split into segment files. An offset labels a message's logical position, not its byte position in a file. Scanning a large segment from the beginning for every query would be expensive, while indexing every record uses more storage. Kafka searches for the first message with `timestamp >= target` and `offset >= startingOffset`. The records' timestamps can move backward, so applying our binary search directly to the log would be incorrect. Kafka builds a sorted summary instead.

Three steps in the source:

1. **Sparse, sorted summary.** During append, [`LogSegment`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java#L261) tracks `maxTimestampSoFar`, the largest timestamp seen so far, and its batch's last offset. After `bytesSinceLastIndexEntry > indexIntervalBytes`, it appends an offset-index entry and calls `timeIndex().maybeAppend` with that running maximum. [`TimeIndex.maybeAppend`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/TimeIndex.java#L180) writes a time entry only when the timestamp is greater than the previous entry's. The time index is therefore sorted even when the original record timestamps are not. This is the sorted precondition from section 3, applied to a summary rather than the raw log.
2. **Binary search the index.** [`TimeIndex.lookup`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/TimeIndex.java#L152) calls `largestLowerBoundSlotFor`: the entry whose timestamp is the largest one that is `<=` the target. This is the mirror image of our lower bound.
3. **Scan to finish the query.** [`LogSegment.findOffsetByTimestamp`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java#L752) uses the offset index to map `max(indexedOffset, startingOffset)` to a file position, then calls [`FileRecords.searchForTimestamp`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/clients/src/main/java/org/apache/kafka/common/record/internal/FileRecords.java#L349). That method walks batches, skips those whose maximum timestamp is too small, and inspects records until both timestamp and offset satisfy the query. The index reduces where scanning starts, but `indexIntervalBytes` is not a hard bound on the scan: time entries may stop growing while timestamps stay below a previous maximum, and batches vary in size. With m index entries, the index search has O(log m) comparison cost; the whole query also includes the scan.

Trace a tiny time index with four summary entries, `running-max timestamp -> offset`: `1000 -> 0`, `1500 -> 40`, `2100 -> 85`, `2600 -> 130`. A consumer asks for timestamp 2000, with `startingOffset = 0`.

<details>
<summary>Answer</summary>

Kafka's search keeps a closed range `[lo, hi]` and picks `mid = (lo + hi + 1) >>> 1`. Start with `lo = 0, hi = 3`: mid = 2, entry 2100 is larger than 2000, so `hi = 1`. Next `lo = 0, hi = 1`: mid = 1, entry 1500 is smaller than 2000, so `lo = 1`. Now `lo == hi == 1`, so the result is slot 1, the entry `1500 -> 40`. Kafka then looks up the file position of offset 40 in the offset index (another sparse lookup), reads the log from there and returns the first record whose timestamp is at least 2000. If the target is below the first entry (500), the search returns no slot and `TimeIndex.lookup` returns the segment's base offset instead.

</details>

**What differs from the lesson's search, and why it matters.**

| Our `LowerBound` | Kafka's `indexSlotRangeFor` |
|---|---|
| First position `>= x` | Largest slot `<= x`, then a scan finishes the job |
| Half-open `[lo, hi)`, `mid = lo + (hi - lo) / 2` | Closed `[lo, hi]`, `mid = (lo + hi + 1) >>> 1`, may return early on an exact match |
| Every timestamp is sorted in the array | Running maxima are sorted in the index; record timestamps need not be sorted |
| Cost counted in comparisons | Also counts which memory pages each comparison touches |

Kafka memory-maps its index files and accesses them through the operating system's page cache. Data is read in pages, so the same number of comparisons need not lead to the same query time.

A comment in [`AbstractIndex.java`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/AbstractIndex.java#L340) explains that as a file grows, textbook binary search can start accessing pages that have not been used recently. If they are no longer cached, the thread waits for disk reads. The authors report produce latency jumping from a few milliseconds to about a second in this test. This is a measurement reported in the comment, not reproduced in this lesson.

Their fix in [`indexSlotRangeFor`](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/AbstractIndex.java#L492) checks the boundary of a tail region, with `warmEntries() = 8192 / entrySize()` (about 8 KiB of entries). Targets beyond that boundary search the tail; other targets search the earlier region. This tail is called "warm" because frequent access makes its pages more likely to remain cached. Comparison count stays logarithmic in the number of entries; the pages accessed change.

**Limit of the analogy.** With record timestamps `[10, 30, 20]`, the window `[20, 30)` contains one event, but our two searches both return 1 and wrongly give count 0. The sorted-input contract was violated. Kafka's seek finds a starting offset; later records can still have earlier timestamps. Subtracting Kafka offsets does not count a timestamp window. Use a separate timestamp-ordered view or scan with the window predicate when you need that count.

**Inference for application.** If your application mostly queries recent data, examine the region it accesses alongside the comparison count. Big-O describes how cost grows with data size; it does not identify the pages or cache lines read. Measure the effectiveness of an access-region split on your application's data and query workload.

**How to apply it in your project.**

1. For many range queries on data sorted by the query key, use a lower bound instead of scanning the whole list for each query. Decode `BinarySearch` with `~result` only when the key is absent.
2. For a large file, a sparse sorted index can reduce storage and the scan's starting point. Measure both index lookup and the remaining scan; index density and the data's ordering determine the trade-off.
3. For window counts on a timestamp-sorted array, use half-open `[start, end)` and subtract the two boundaries. An unsorted log needs a different strategy.
4. Appending preserves sorted key order only when the new key is at least the last key. Otherwise insert at the proper position and pay the shift, sort a batch, or choose an ordered index suited to updates.

**Break · 30 minutes (lunch).** Eat and rest.

## 7. Guided C# practice

**Practice · about 75 minutes.** Rebuild `LowerBound` from the invariant, predict edge cases, run the checks and deliberately introduce a bug to analyze. **Finish when:** the checks pass and you can explain one bug you avoided and one assumption the algorithm needs.

Run from `labs/boundary-search/dotnet` with SDK 10.0.401:

```bash
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

The default run shows a lower boundary of 3 for 30 and window counts 3, 0 and 3 for `[10,30)`, `[30,30)` and `[11,39)`. The 17 checks cover first duplicates, absent targets, empty, equal and reversed windows, negative and extreme keys, input preservation, .NET's insertion encoding, a virtual array with `int.MaxValue` positions, and small cases compared against a scan. A failing check exits nonzero. You can also work without running anything: every step can be traced on paper.

Steps:

1. **Rebuild it (20 minutes).** Close the code, rewrite `LowerBound` and say the invariant of section 3 aloud. If stuck, look at section 4.
2. **Predict edge cases (15 minutes).** Write your answer before tracing:

   | Array and call | Question |
   |---|---|
   | `[2,4,4,9]`, target 4 | First position? |
   | `[2,4,4,9]`, target 5 | Insertion position? |
   | `[2,4,4,9]`, targets 0 and 10 | Both ends? |
   | `[]`, target 4 | Does it read any element? |
   | `[10,10,20,30,30,40]`, window `[20,40)` | Count? |
   | same array, window `[41,50)` | Count? |

<details>
<summary>Expected results</summary>

| Array and call | Result |
|---|---|
| `[2,4,4,9]`, target 4 | 1 |
| `[2,4,4,9]`, target 5 | 3 |
| `[2,4,4,9]`, targets 0 and 10 | 0 and 4 |
| `[]`, target 4 | 0, no element is read |
| `[10,10,20,30,30,40]`, window `[20,40)` | 3 (boundaries 2 and 5) |
| same array, window `[41,50)` | 0 (boundaries 6 and 6) |

A reversed window such as `[30,10)` must be rejected before subtracting.

</details>

3. **Run and debug (20 minutes).** Run the checks. When one fails, trace the smallest failing array instead of rewriting the method.
4. **Break one branch on purpose (15 minutes).** Try `hi = mid - 1` on `[1, 3]`, target 3, then try `lo = mid` on `[1]`, target 2. Which invariant or termination argument fails? Trace the second change on paper so you can stop a non-terminating loop.

<details>
<summary>Answer</summary>

- With `hi = mid - 1`, the first midpoint is 1; setting `hi = 0` loses the right answer 1. The half-open invariant needs `hi = mid`: an equal value may be the answer.
- With `lo = mid`, when one element remains and it is too small, `mid == lo` and the interval never shrinks. Use `lo = mid + 1` to remove that position.

</details>

5. **Wrap up (5 minutes).** Explain one bug you avoided and one assumption the code needs.

**Debug hints:** wrong first duplicate -> look at the equality branch; error on empty input -> read elements only inside the non-empty loop; target above the maximum fails -> allow the answer `n`.

**Break · 10 minutes.** Leave the screen.

## 8. Observe the cost

**Observation · about 45 minutes.** Predict element reads, run the experiment and compare the results. **Finish when:** you can explain how reads grow and one cost this count does not measure.

This sequence computes a value on each indexed read and counts reads, so it shows scaling without allocating a big array. It is in the lab as `LessonLab/Extras.cs`:

```csharp
public sealed class CountedSequence(int n) : IReadOnlyList<long>
{
    public int Reads { get; private set; }
    public int Count => n;

    public long this[int index]
    {
        get
        {
            if ((uint)index >= (uint)n) throw new ArgumentOutOfRangeException(nameof(index));
            Reads++;
            return index * 2L;
        }
    }

    public IEnumerator<long> GetEnumerator() => throw new NotSupportedException();
    System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator() => GetEnumerator();
}
```

Predict the number of reads for n = 8, 1,024 and 65,536 with `BoundarySearch.LowerBound(new CountedSequence(n), n)`, then run:

```bash
dotnet run -c Release --project LessonLab -- --observe
```

Repeat with a target below all keys and one above all keys. What changes in the number of reads, and what does this count leave out?

<details>
<summary>Answer and observed output</summary>

Observed output on the lab's .NET SDK 10.0.401 (the line format is `n index reads`):

```text
8 4 3
1024 512 10
65536 32768 16
records: 1 3 2
```

The target is near the middle of these synthetic sequences. Growing n from 1,024 to 65,536 multiplies the size by 64 but adds only six reads. The exact worst-case bound is `floor(log₂(n)) + 1`, or 17 for n = 65,536. For that n, target -1 takes 17 reads; targets n and `2L * n` take 16. Counts for other targets can vary while staying within the bound. The lab's logarithmic check uses the middle target; it does not exhaust every large input. This counts element reads, not CPU instructions, wall-clock time or database page reads; Kafka's page-cache story in section 6 is exactly the kind of cost it cannot see.

</details>

Now count the other side. Inserting near the front of an array-backed list of n elements moves about n elements, so a sorted `List<long>` that receives random inserts pays O(n) per write even though each search is O(log n). Sorting an unsorted batch once costs O(n log n) in the usual comparison model; that preparation is separate from the per-query cost.

| Write before you run | Write after you run |
|---|---|
| Predicted reads for each n | Observed reads |
| Which target gives the most reads? | What you saw for targets below, inside and above |
| What this count cannot measure | One sentence on the limit |

**Break · 10 minutes.** Leave the screen.

## 9. Transfer: event records, then SQL Server

**Application · about 35 minutes.** Replace individual timestamps with records, predict the result and compare with the SQL query. **Finish when:** you have checked the record example's two boundaries and explained a target beyond the data.

### Records with a timestamp key

An event usually contains a timestamp and an ID. Different events can share a timestamp while having different IDs:

```csharp
public sealed record Event(long Timestamp, string Id);
```

Change `LowerBound` to accept `IReadOnlyList<T> items`, a `long target` and `Func<T, long> key`. The list is sorted by the returned key. Try it on `[(10,A), (20,B), (20,C), (30,D)]`: find the two boundaries for `[20, 30)` and its event count. Also check target 31, which is beyond the final key.

<details>
<summary>Answer</summary>

The key is applied to the records in the array, not to the target. Keep the original invariant, replacing `items[mid]` with `key(items[mid])` in the comparison:

```csharp
public static class RecordSearch
{
    public static int LowerBound<T>(IReadOnlyList<T> items, long target, Func<T, long> key)
    {
        ArgumentNullException.ThrowIfNull(items);
        ArgumentNullException.ThrowIfNull(key);
        int lo = 0, hi = items.Count;
        while (lo < hi)
        {
            int mid = lo + (hi - lo) / 2;
            if (key(items[mid]) < target)
                lo = mid + 1;
            else
                hi = mid;
        }
        return lo;
    }
}
```

`LowerBound(events, 20, e => e.Timestamp)` is 1 and `LowerBound(events, 30, e => e.Timestamp)` is 3, so the count is `3 - 1 = 2` (B and C). Target 31 returns 4, one past the end. The target is a key value (20), not a full event. The list must be sorted by that same key. The lab's `--observe` prints `records: 1 3 2`, and `--check` includes these record boundaries.

</details>

Use one unit and timezone interpretation. Mixing seconds and milliseconds can silently break a query. The key function runs on every examined record; an expensive key may justify precomputing keys, at the cost of storage and keeping them in sync on updates. For frequent writes a flat sorted list may be a poor fit; ordered indexes or trees have their own query, update and storage costs.

### SQL Server: a time window over an index

The same contract is `ts >= @s AND ts < @e` in T-SQL. In a scratch database, this example keeps duplicate timestamps as separate events:

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

Predict the count, then try equal bounds. How would replacing the predicate with `BETWEEN @s AND @e` change the result?

<details>
<summary>Answer</summary>

The expected count is **3**: both rows at the start and the 10:10 row are included; both rows at the end are excluded. Equal bounds return 0. `BETWEEN @s AND @e` would include the end and count 5, changing the contract. Do not make `ts` unique unless the domain forbids simultaneous events: timestamps and event identity answer different questions.

</details>

This SQL example needs SQL Server and is not executed by the C# lab; its result is a prediction from the rows and predicate, not a database measurement.

The predicate is **sargable**: the indexed column is compared directly with a compatible parameter type, so SQL Server can use the index to seek to the range. A predicate such as `DATEPART(year, ts) = @year` computes a value from the column instead of giving a direct range to seek; use `ts >= @yearStart AND ts < @nextYearStart` instead. Sargable permits a seek but does not promise one: selectivity, statistics, table size and the optimizer decide the plan, so check the actual execution plan and `SET STATISTICS IO ON`.

Two lower bounds on an array give a count by subtracting indexes. A normal SQL Server index does not make `COUNT_BIG` an O(log n) operation: finding the range is cheap, but counting may still visit every qualifying index entry. Locating a range and counting it have separate costs. `datetime2` has no timezone, so use one convention (for example UTC) for stored values and bounds, and match precision rather than adding an "epsilon" to an inclusive endpoint.

## 10. Synthesis and review

**Synthesis · about 45 minutes.** Explain the algorithm without notes, check the table and solve the new example. **Finish when:** you have one design choice with its reason and one question to investigate further.

Explain in your own words why equality moves `hi`, why returning `n` is valid, and why any matching midpoint is not enough. If a case fails, keep the smallest example, correct the rule and test a new example. That works better than memorizing the two update lines.

| Check | A good explanation contains | If unclear, try |
|---|---|---|
| Partition correctness | Both inequalities; empty, duplicate, missing and beyond-range cases | Draw numbered values and the two parts |
| Termination and cost | Each branch shrinks `hi - lo`; logarithmic comparisons under random access | Trace a one-element unknown interval |
| Window behavior | Two boundaries; start included, end excluded | Duplicate both endpoints |
| Trade-off | Fast queries do not remove insertion shifts, key cost or page-access cost | Count moves for a front insertion |

Fresh case to answer without notes: `[5, 5, 5, 7, 9]`, window `[5, 9)`.

<details>
<summary>Answer</summary>

`LowerBound(5) = 0` and `LowerBound(9) = 4`, so the count is 4: all three 5s and the 7. The 9 at the end is excluded. Compare with a plain equality search for 5, which could return position 1 and make the subtraction wrong.

</details>

Optional practice: find the boundary for `[1,1,3]`, target 1, then `[2,4,4,9]`, target 5. On `[10,10,20,30,30,40]`, count `[20,40)` and `[41,50)`. Explain how to handle reversed endpoints `[30,10)` and what must stay sorted when you search records by a key.

<details>
<summary>Answers to the practice list</summary>

- `[1,1,3]`, target 1: boundary 0; no element belongs to the smaller part.
- `[2,4,4,9]`, target 5: boundary 3; all three earlier elements are smaller.
- `[10,10,20,30,30,40]`, window `[20,40)`: count 3, from boundaries 2 and 5.
- The same array, window `[41,50)`: count 0, from boundaries 6 and 6.
- Reversed endpoints: reject the query before subtracting boundaries.
- Record search: the target is a key value; keep the same ordering when updating the list.

</details>

After a delay, rebuild the search and trace a new duplicate target without notes; then change the record representation or the endpoints and explain the window result. Revisit sooner after an error and wait longer once the reasoning is reliable.

Questions to carry forward: why do left and right boundaries differ on equality? What work does a key function add? Why is inserting into a sorted list still linear despite binary search? What extra work remains after Kafka's index lookup?

<details>
<summary>Answer</summary>

A left boundary keeps equal values in the right part (`hi = mid`); a right boundary puts them in the left part (`lo = mid + 1` on equality) to find the first strictly greater value. A key function runs on each inspected record, so its cost adds to each comparison. Finding an insertion position is logarithmic but moving the later list elements is linear. Kafka still maps an offset to a file position, scans batches and records, and may wait for disk pages. A sparse index's comparison count alone does not describe the whole query's cost.

</details>

## Read further

- [Apache Kafka time index](https://github.com/apache/kafka/blob/8ed535f41c2a8a783e64a3b4ff9468ab682959b8/storage/src/main/java/org/apache/kafka/storage/internals/log/AbstractIndex.java#L340): the warm-section comment and `indexSlotRangeFor`, pinned to the commit read in section 6.
- [List<T>.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch?view=net-10.0) and [Array.BinarySearch](https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch?view=net-10.0): duplicate-match and complemented insertion-position contracts.
- [SQL Server index design guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide?view=sql-server-ver17): range predicates, index choices and query plans.
- [C# lab guide](../../labs/boundary-search/dotnet/README.md): setup, commands and checks.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Lesson 01 - Big-O and data structures: removing duplicate order IDs in C#](../2026-10-05-cost-model/lesson.md) - Review how hidden work inside a loop determines its cost.
- [Technical topic notes](../../references/topic-notes.md) - Explore ordered indexes, query processing and algorithm design.

---

[← Previous: Lesson 01 - Big-O and data structures: removing duplicate order IDs in C#](../2026-10-05-cost-model/lesson.md) · [All lessons](../../README.md)
<!-- LESSON_NAVIGATION_END -->
