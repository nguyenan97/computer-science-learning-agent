# Lesson 01 — Big-O and data structures: removing duplicate order IDs in C#

**One full day: 420 minutes · 360 minutes of study + 60 minutes of breaks · Updated 6 October 2026**

[Tiếng Việt](../../vi/lessons/2026-10-05-cost-model/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/cost-model/dotnet-lab.zip)

A loop can look simple and still perform billions of comparisons. This lesson shows where that work comes from, how a different data structure changes it, and what you give up in memory. Everything needed to understand the algorithm, its complete implementation and the worked exercises is on this page. The downloadable lab and official sources add executable experiments and deeper reading.

**Your goal:** implement batch deduplication that keeps the first occurrence of each ID, then justify scan versus hashing for a changed input distribution using correctness, operation counts and CPU/allocation measurements. You need basic C# loops and collections; the complexity analysis starts from a concrete trace.

## A full-day route

| Elapsed minutes | Activity | Hands-on minutes |
|---|---|---:|
| 0–20 | Quick self-check: identify what you can explain and what needs revisiting | 10 |
| 20–70 | Contract, mental model and worked trace (§§1–4); reconstruct a trace and cost count | 20 |
| 70–80 | Break away from the screen | 0 |
| 80–125 | Read selected sources (§6 and Read further); answer the four research questions | 10 |
| 125–170 | Trace the implementation (§6): one miss, hit and collision | 40 |
| 170–200 | Lunch and rest | 0 |
| 200–275 | Guided practice (§5): implement, test and debug | 70 |
| 275–285 | Break | 0 |
| 285–330 | Controlled experiment (§6): predict, measure and compare | 40 |
| 330–340 | Break | 0 |
| 340–375 | Changed-context challenge (§7): duplicate counts | 35 |
| 375–420 | Explain the decision, correct mistakes and choose a review question (§8) | 10 |

The route reserves 235 of 360 study minutes for coding, tracing, test design, debugging and experiments. Setup and waiting for a benchmark are not practice. Adjust the blocks to your tools and energy; if setup takes too long, use the inline traces and existing example report. Finish with one clear decision and one open question rather than extending the day to get a tidy benchmark.

## Quick self-check

Try these without notes, or read the answers first and return to them later:

1. For `B2,A1,B2,C3,A1`, what is the stable output? How does sorting change it?
2. How many equality checks does a sequential scan make for `A,B,C,D`?
3. Do equal hashes imply equal IDs? Can a set in one process prevent duplicates in another?
4. Does “allocated per operation” mean peak memory?

**Answers:** (1) `B2,A1,C3`; sorting gives `A1,B2,C3` and breaks the order requirement. (2) `0+1+2+3=6`. (3) No: equality still distinguishes collisions, and two processes have separate sets. (4) No: allocation is the amount newly allocated during the measured operation, not the maximum live memory.

If sequential search is unfamiliar, draw `[B2,A1]`. Searching for B2 stops after one comparison; searching for C3 checks both entries before concluding absence. For `[X,Y,X]`, the stable output is `[X,Y]` and the scan makes `0+1+1=2` comparisons. If these traces are easy, spend more time on the measurement and changed-context challenge.

## 1. Start with a small production requirement

A logistics job receives order IDs from logs or a message batch. IDs may recur. Return each ID **once, in first-occurrence order**.

```text
Input : B2, A1, B2, C3, A1
Output: B2, A1, C3
```

Set three requirements before optimizing:

- Exact equality with `StringComparer.Ordinal`: `a` differs from `A`; do not silently trim or lowercase.
- First-occurrence order: sorting into `A1,B2,C3` violates the requirement.
- Unchanged input. Neither input nor any ID may be null; the lab rejects null. Empty strings remain valid values for this example.

This is deduplication **within one batch**, not exactly-once message processing.

**Think it through:** how many elements and distinct IDs are there? With partial output `[B2,A1]`, how do you determine whether C3 has appeared?

**Solution:** `n=5` elements and `u=3` distinct IDs. A sequential search for C3 must check both B2 and A1. If “check every element before concluding absence” is unclear, follow the next trace slowly; that is the central prerequisite.

## 2. One loop can still do a lot of work

A familiar implementation:

```csharp
var result = new List<string>();
foreach (string id in values)
{
    if (!result.Contains(id))
        result.Add(id);
}
```

List.Contains searches existing elements and stops when it finds equality. On a miss it searches the entire list. A single API call can hide substantial work from the outer code.

| Current ID | `result` before step | Sequential comparisons | `result` after step |
|---|---|---|---|
| B2 | [] | 0 | [B2] |
| A1 | [B2] | A1 with B2: 1 | [B2,A1] |
| B2 | [B2,A1] | B2 with B2: 1, stop | [B2,A1] |
| C3 | [B2,A1] | C3 with B2 and A1: 2 | [B2,A1,C3] |
| A1 | [B2,A1,C3] | A1 with B2 then A1: 2, stop | [B2,A1,C3] |

The total is **6 equality comparisons** in this sequential model, although foreach has only five iterations. This models the algorithm; it does not count .NET runtime CPU instructions.

### When every ID is distinct

For `A,B,C,D`, the comparison counts are `0,1,2,3`. The kth ID checks k−1 previous IDs. For n IDs:

```text
C(n) = 0 + 1 + 2 + ... + (n−1) = n(n−1)/2
```

To derive it, write the sum forwards and backwards. Each aligned pair adds to n−1 and there are n pairs. Two sums equal n(n−1), so one sum is half that.

| n, all distinct | Model comparisons |
|---:|---:|
| 128 | 8,128 |
| 256 | 32,640 |
| 512 | 130,816 |
| 100,000 | 4,999,950,000 |

Doubling the input nearly quadruples the work. These counts cannot be converted directly into milliseconds: hardware, runtime and data affect actual execution time.

## 3. What question does Big-O answer?

A **cost model** states what we count. For now, treat comparing/hashing one ID as bounded-cost work; n is the input length. This is an analytical assumption, not a law about arbitrary strings.

Big-O gives an **asymptotic upper bound**: T(n) is O(n²) if constants C and n₀ exist such that `T(n) ≤ Cn²` for every `n ≥ n₀`. It does not mean “n² seconds”.

For distinct IDs, n(n−1)/2 has a quadratic leading term. The sequential model is **Θ(n²)**: matching upper and lower growth bounds. O(n²) is correct but less precise. An O(n) algorithm also satisfies an O(n²) upper bound, so use a tight order when explaining behavior.

**What if every ID is A?** After the first ID, Contains succeeds immediately. There are just n−1 comparisons: Θ(n). Worst-case complexity does not say every input costs that much.

With u distinct IDs, the accumulated list is at most u long. The entire scan approach is bounded by `O(n(1+u))`. A small u may make it adequate; when u grows with n, the worst case becomes quadratic.

**Think it through:** can a single foreach prove O(n)?

**Solution:** no. Sum the body cost over the iterations. Contains, database queries and service calls each have their own costs; source-code line counts are insufficient.

## 4. Separate lookup from output ordering

We need two different answers: “have we seen this ID?” and “what order should the output have?”. Use a HashSet for the first and a List for the second.

```csharp
var seen = new HashSet<string>(StringComparer.Ordinal);
var result = new List<string>();
foreach (string id in values)
{
    if (seen.Add(id))   // true: newly inserted; false: already present
        result.Add(id);
}
```

Add already detects duplicates; a separate Contains followed by Add would search twice for a new ID. Do not depend on HashSet enumeration order: appending to result in input order establishes the output contract.

### Why does hashing help?

Imagine a table with buckets. Hashing an ID chooses a bucket to search instead of scanning the entire List from the beginning. **Equal hashes do not prove equal IDs**: collisions still require equality checks.

With sufficiently well-distributed hashing, controlled bucket occupancy and bounded key cost, expected lookup work in the hashing model is constant. However:

- **Expected:** an expectation under distribution/randomness assumptions, not a guarantee for every input.
- **Amortized:** total cost over a sequence of operations. One resize can cost O(u), but geometric growth avoids copying the whole table on every insertion. Work like `1+2+4+...` totals O(u). This illustrates the principle, not the exact .NET capacity sequence.
- **Worst case:** an unfavorable comparer/hash can create long collision chains and make the batch O(n²). .NET has additional protection for certain string comparers; do not assume all custom comparers receive the same protection.

Consequently the hash approach has **expected O(n)** total batch cost, including amortized growth, under these assumptions. The lab makes n Add calls; that is not the total hash/equality/resize work.

For maximum string length L, hashing or equality may depend on L. If L varies with input size, include it in the model: for example expected O(n(1+L)) for hashing under the remaining assumptions, counting both key work and per-item overhead. HashSet does not make key length disappear.

### Prove the result remains correct with an invariant

After each processed prefix, seen contains exactly the IDs encountered; result contains each once in first-occurrence order.

Initially both are empty. An existing ID makes Add return false, changing neither. A new ID makes Add return true and is appended to the output, preserving order. At the end the invariant is precisely the original contract. We changed cost while preserving behavior.

### Memory: identical Big-O does not mean identical bytes

| Approach | Time in the model | Auxiliary memory, excluding output | Output |
|---|---|---|---|
| List scan | O(n(1+u)); Θ(n²) for all-distinct input | O(1) | O(u) |
| HashSet + List | Expected O(n), with assumptions | O(u) | O(u) |

HashSet stores additional bucket/entry arrays; List stores string references. This code does not clone input strings. Capacity growth allocates and copies arrays; old arrays may need garbage collection. **Allocated bytes, surviving memory and peak working set are different measurements.**

`new HashSet<string>(n, ...)` or `new List<string>(n)` can reduce resizing with an appropriate known capacity, but large n/small u can overallocate. Preallocating n makes that storage O(n), not O(u) when u is independently small. This optimization is outside the main lesson.

## 5. Guided C# practice: a complete implementation

Here is the full method, including its null policy. Put it inside a class if you run it locally; the logic does not require a database or a framework.

```csharp
public static List<string> StableUnique(IReadOnlyList<string> values)
{
    ArgumentNullException.ThrowIfNull(values);
    var seen = new HashSet<string>(StringComparer.Ordinal);
    var result = new List<string>();
    foreach (string id in values)
    {
        if (id is null)
            throw new ArgumentException("Order IDs must not be null.");
        if (seen.Add(id))
            result.Add(id);
    }
    return result;
}
```

`seen` and `result` start empty for each batch. Every ID reaches Add exactly once. A new ID enters the set and is appended to the list; an existing one changes neither. The method reads the input without changing it. The list references the same string objects rather than cloning them.

Example call:

```csharp
string[] input = ["B2", "A1", "B2", "C3", "A1"];
var unique = StableUnique(input);
Console.WriteLine(string.Join(", ", unique)); // B2, A1, C3
```

### Work through the 75-minute practice block

1. **Reconstruct the method (20 minutes).** Close the example, write it again and explain the prefix invariant from §4. If you get stuck, use the complete method above.
2. **Predict edge cases (15 minutes).** Write expected results before tracing or running:

   | Input | Expected result |
   |---|---|
   | `[]` | `[]` |
   | `a,A,a` | `a,A` |
   | `A,A,A` | `A` |
   | `"",B2,""` | `"",B2` |
   | null input | `ArgumentNullException` |
   | a null ID | `ArgumentException` |

3. **Test and debug (15 minutes).** Compare the output with these expectations and check that input is unchanged. For a mismatch, trace the smallest failing batch instead of rewriting the whole method.
4. **Deliberately break one rule (10 minutes).** Append every ID, sort the result, or use `OrdinalIgnoreCase`. Appending all IDs retains duplicates; sorting breaks first-occurrence order; case-insensitive equality merges `a` and `A`. Restore the intended contract before measuring.
5. **Explore collisions (10 minutes).** Suppose a comparer returns hash 1 for every ID but still compares IDs ordinally. The result stays correct, but an absent ID may inspect every entry in that bucket. With 128 distinct IDs, a chain-based implementation makes `128×127/2=8,128` equality checks. Equal keys must have equal hashes, and equality/hash behavior must remain stable while keys are stored.
6. **Wrap up (5 minutes).** Explain one bug you prevented and one assumption your implementation relies on.

**Common debugging clues:** duplicates remain → append only when Add returns true; order changes → retain the explicit output list; `a/A` merge → inspect the comparer; unexpectedly slow hashing → look for a hidden List.Contains; null behavior changes → keep validation explicit.

### An inline Python comparison

The same separation of membership and output order can be written with a Python set:

```python
def stable_unique(values):
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result

assert stable_unique(["B2", "A1", "B2", "C3", "A1"]) == ["B2", "A1", "C3"]
```

This version requires hashable keys and uses Python equality; it does not adopt the C# method's null policy. It performs a membership test and then an insertion for a new key, whereas C# Add handles both in one call. The same high-level cost reasoning applies under suitable hashing assumptions; constants and collision behavior depend on the implementation.

## 6. Research, implementation inspection and a controlled experiment

### Connect the model to real collection code

List.Contains calls IndexOf, which ultimately searches the array. The .NET runtime can specialize this search for particular types, improving constants without removing the need to examine preceding candidates on a miss.

HashSet.Add follows a different path:

```text
ID → calculate hash → select bucket → inspect entries in that bucket
   → matching hash AND equal ID? return false
   → otherwise follow the next entry
   → no equal entry? allocate a slot (resize if needed), insert, return true
```

A **bucket** is an entry point into a group of candidates. A **collision chain** links entries that land in the same bucket. The stored hash helps reject candidates cheaply; equality decides identity. Resizing creates larger storage and redistributes entries, so an individual Add can be expensive even when a long sequence has good amortized cost.

Trace these cases: an empty set receiving B2; B2 appearing again; a new A1 with the same hash as B2. Answers: insert B2 and return true; find equal B2 and return false; compare A1 with B2, see they differ, insert A1 and return true. Stable output order comes from the separate list in all three cases.

For deeper inspection, the official [List.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/List.cs#L336) and [HashSet.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/HashSet.cs#L1411) are pinned to a reproducible .NET 10 implementation. Locate bucket selection, equality, the false return and resizing. You do not need to build the runtime to understand these paths.

### Four research questions

| Question | Answer to look for |
|---|---|
| What work does List.Contains hide? | Sequential search; early exit on a hit, full scan on a miss. |
| Why can one Add be O(u) while the sequence is expected O(n)? | Resizing costs accumulate geometrically; expected lookup additionally needs suitable hashing and bounded key cost. |
| Why do collisions preserve correctness but threaten performance? | Correct equality separates distinct keys; a long chain adds comparisons. |
| What can a synthetic benchmark tell us about a service? | It compares the measured workload and allocation scope; production distributions, peak memory and service p99 need separate measurements. |

### Make the comparison fair

Measure scan and hash with the same input, equality and output-order contract. Construct input before measurement, and make each measured call produce a fresh result. Otherwise one path may receive warmed state or skip allocation while the other cannot.

The downloadable lab uses BenchmarkDotNet 0.15.8, N=128/512/2048 and nominal distinct ratios 10%/100%, with fixed-width IDs. For N=128 and 10%, actual distinct count is `floor(128×0.10)=12`. Predict before running: as u decreases, the list scan becomes shorter; the extra hash table often allocates more. Big-O alone cannot tell you a speed ratio.

Run benchmarks in Release without a debugger. Read Mean, Error and Allocated together. In BenchmarkDotNet, Error here is half the 99.9% confidence interval, not a guaranteed maximum error. Allocated includes fresh output/table storage and excludes prebuilt input; it does not measure peak working set, surviving heap or service p99.

A reference ShortRun from 5 October 2026, with n=512 and all IDs distinct:

| Approach | Mean | Error | Allocated per operation |
|---|---:|---:|---:|
| Scan | 922.355 µs | 2,261.779 µs | 8,384 B |
| Hash | 22.218 µs | 19.147 µs | 42,896 B |

The run used Debian 13, Intel Xeon Platinum 8573C and .NET 10.0.12, with three warmup and three measurement iterations per case. The intervals are very wide: treat the time values as illustrative, not as a dependable service speedup. The extra allocated bytes show a trade-off, not total application memory. [The complete report](benchmark-report.md) includes the workload matrix.

### Your experiment notebook

Use the 45-minute block to change one factor—n, distinct ratio, key length or initial capacity—and preserve the output contract. Correctness comes before timing. Do not benchmark a comparison-counting method against an uninstrumented one: the counters alter the work.

| Write before running | Write after running |
|---|---|
| Input size, actual u, key width/distribution | Actual parameters and environment |
| Prediction and its mechanism | Mean, interval and allocation |
| One factor being changed | Whether the prediction held |
| Expected correctness result | Any failure or surprising observation |
| What would make the result inconclusive? | Supported decision and remaining limits |

If you do not run a benchmark, use the reference report to practise interpretation and leave your own measurement blank. If results are missing or too noisy, the conclusion is “insufficient measurement for a speed claim.” Check input construction, comparer, build mode and intervals before inventing an explanation for a surprising ratio. A harness Dry run checks execution, not performance.

## 7. Changed-context challenge: report duplicate counts

A support report now needs counts instead of unique IDs. For `B2,A1,B2,C3,A1`, return `[(B2,2),(A1,2)]`, omitting IDs that appear only once. Keep ordinal identity, first-occurrence order, unchanged input and the same null policy.

Try designing the solution before reading on. You need counts for lookup and a separate list for order. Increment the count on every occurrence; append to the order list only the first time an ID appears.

```csharp
public sealed record OrderCount(string Id, int Count);

public static List<OrderCount> DuplicateSummary(IReadOnlyList<string> values)
{
    ArgumentNullException.ThrowIfNull(values);
    var counts = new Dictionary<string, int>(StringComparer.Ordinal);
    var order = new List<string>();
    foreach (string id in values)
    {
        if (id is null)
            throw new ArgumentException("Order IDs must not be null.");
        if (counts.TryGetValue(id, out int count))
            counts[id] = count + 1;
        else
        {
            counts.Add(id, 1);
            order.Add(id);
        }
    }
    var result = new List<OrderCount>();
    foreach (string id in order)
        if (counts[id] > 1)
            result.Add(new OrderCount(id, counts[id]));
    return result;
}
```

The invariant has two parts: counts equals the number of occurrences in the processed prefix, and order contains each encountered ID once in first-occurrence order. A second pass over order filters counts greater than one. Expected work is O(n+u)=O(n), with O(u) extra storage under the same hashing/key assumptions. We do not depend on Dictionary enumeration order.

| Input | Worked result |
|---|---|
| `A,B,B,A,C` | `[(A,2),(B,2)]` |
| `a,A,a` | `[(a,2)]` |
| `[]` or `X,Y` | `[]` |
| `A,A,A` | `[(A,3)]` |

If you sort by count, you change the report's ordering. If you increment only new IDs, `A,A,A` exposes the bug. Trace `A,B,B,A,C`: order stays `A,B,C`, counts becomes A=2/B=2/C=1, and the final pass returns A then B.

### Production connection: batch deduplication and idempotency

Two service instances can both accept B2 because their sets start empty. A batch HashSet therefore cannot enforce system-wide identity. Use an appropriate storage key, such as tenant + event ID, with a unique constraint/index and transaction/conflict handling. A separate SELECT-before-INSERT still races.

Storage equality must match your intended identity: SQL Server collation may treat strings differently from C# Ordinal. If a side effect occurs outside the database transaction, a unique key alone does not guarantee exactly-once execution of that side effect. That requires a suitable idempotency/transaction protocol.

## 8. Explain your decision and revisit it

Close the examples and explain:

1. Why can one foreach be Θ(n²)? **Answer:** its body searches a growing list, summing `0+1+…+n−1` on distinct input.
2. Why use both HashSet and List? **Answer:** membership and stable output order are separate jobs; the hash table costs extra storage.
3. Can hashing always be faster? **Answer:** no; small batches, low u, key costs, allocations and cache behavior matter.
4. For `A,B,A,B`, how many scan comparisons occur? **Answer:** `0+1+1+2=4`, versus six for four distinct IDs.

A useful final explanation states the contract, expected workload, chosen structure, supporting reasoning and one limit. Example: “For many distinct bounded-length IDs, I would use HashSet plus List. The invariant preserves stable order, while the scan count grows quadratically. Hashing has expected linear work under suitable assumptions and uses extra storage. The example benchmark illustrates that trade-off with substantial timing uncertainty. I would measure real key distributions and memory before promising production latency.”

When reviewing your own solution, check four things: edge cases and invariant; n/u/key-cost assumptions; fair measurement and its limits; and whether the duplicate-count variation still preserves order. If one explanation is unclear, revisit its small counterexample and try new IDs. After a delay, reconstruct the count or implement the variation without notes. Review sooner after a mistake and increase the gap when recall becomes reliable; 1/3/7-day gaps are adjustable starting suggestions.

Open questions for later: What changes with long identifiers? How much memory can the batch use? How should tenant identity match storage equality? Choose one rather than expanding today's scope indefinitely.

## Read further

- [Microsoft: List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0) and [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0): confirm equality, return values and resizing behavior.
- [MIT OCW: Hashing II, pages 1–3](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf): derive load-factor assumptions and amortized table growth.
- [BenchmarkDotNet good practices](https://benchmarkdotnet.org/articles/guides/good-practices.html): prepare a fair Release benchmark and avoid extrapolating one environment's result.
- [SQL Server unique indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/create-unique-indexes?view=sql-server-ver17): extend the batch example to storage-enforced uniqueness.
- [C# lab guide](../../labs/cost-model/dotnet/README.md): optional setup, benchmark commands and troubleshooting when you want to run the experiments.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Topic map](../../references/topic-map.md) — Choose the foundations or deeper topic to study next.
- [C# lab guide](../../labs/cost-model/dotnet/README.md) — SDK setup, copyable commands and benchmark troubleshooting.

---

[All lessons](../../README.md) · [Next: Lesson 02 — Boundary search and time windows →](../boundary-search/lesson.md)
<!-- LESSON_NAVIGATION_END -->
