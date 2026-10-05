# Lesson 01 — Big-O and data structures: removing duplicate order IDs in C#

**90 minutes · Optional 180+ minute deep track · Updated 5 October 2026**

[Tiếng Việt](../../vi/lessons/2026-10-05-cost-model/lesson.md) · [C# lab guide](../../labs/cost-model/dotnet/README.md) · [Download complete lab ZIP](https://nguyenan97.github.io/computer-science-learning-agent/labs/cost-model/dotnet-lab.zip) · [Complete worked code](../../labs/cost-model/dotnet/Core/Deduplication.cs)

**Today's idea:** the data structure determines the search cost inside a loop. Replacing `List.Contains` with `HashSet.Add` can reduce CPU work substantially, provided you preserve the business contract and examine memory costs.

This lesson is for an experienced C#/.NET, API and database engineer strengthening CS foundations. Loop syntax and REST basics are prior context. The mathematical analysis is explained from the beginning; programming experience alone does not establish Big-O proficiency.

This is a tutor-selected foundation for **IUH Advanced Algorithms `6001127`**: complexity analysis, practical performance and algorithm selection, with a connection to Advanced Database `6001111`. It is not an official IUH lesson plan. Topic: `advanced-algorithms.cost-model-membership.l1`.

Three outcomes to check: explain the comparison count; choose stable deduplication; interpret CPU/allocation benchmarks with appropriate limits. **Every exercise, lab and submission is optional, with accessible solutions.** Reading only is a valid path; it is not evidence of independent proficiency.

## A 90-minute path

| Time | Study | Reading-only alternative |
|---|---|---|
| 0–15 | Problem, contract and trace | Follow the small example without installing anything |
| 15–40 | Count work and understand Big-O | Follow the derivation step by step |
| 40–60 | HashSet, correctness and memory | Read the code and invariant |
| 60–80 | Optional C# lab | Inspect verified output |
| 80–90 | Variation and recap | Read the task followed by its solution |

The budget applies to **one language version**. Benchmarking and runtime reading belong to the 180+ minute track; finishing them is not required for the next lesson. No actual learner work has been assessed and no review is due.

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

**Optional self-check:** how many elements and distinct IDs are there? With partial output `[B2,A1]`, how do you determine whether C3 has appeared?

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

**Optional self-check:** can a single foreach prove O(n)?

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

## 5. Optional C# lab: check reasoning before measuring speed

The [full guide](../../labs/cost-model/dotnet/README.md) provides the ZIP, setup, benchmark and troubleshooting. The core lab needs the .NET SDK, with no SQL Server, Docker, Python or third-party package. Verified environment: **SDK 10.0.401, runtime 10.0.12, Linux x64**; target net10.0. You need not retarget a production application.

From an updated repository clone's root:

```bash
cd labs/cost-model/dotnet
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

**Step 1 — contract.** Predict the five-ID output, then read/run the lab. Checkpoint: `B2, A1, C3`; scan comparisons = 6. Solution: existing IDs are not appended; input and first-occurrence order are preserved.

**Step 2 — formula.** Predict n=128/256/512, then compare:

```text
n,scan_equality_comparisons,hash_add_calls (not hash-table work)
128,8128,128
256,32640,256
512,130816,512
128 identical IDs: 127 scan comparisons
```

Solution: distinct scan input matches n(n−1)/2; repeated input needs only n−1 comparisons. The Add column counts calls and does not prove every runtime operation is O(1).

**Step 3 — behavior.** Run `--check`; expect **8 checks passed**. Cases include empty/singleton input, ordinal equality, input preservation, null policy, duplicate counting and a comparer forcing identical hashes. Collision solution: equality preserves correctness, but comparison counts become triangular. Reference-code tests do not establish that you completed the lesson.

Without an SDK, read the checkpoints and [complete code](../../labs/cost-model/dotnet/Core/Deduplication.cs). Writing code is not required to read solutions or request the next lesson.

## 6. The 180+ minute track: measure CPU/allocation and read implementation

Allow about 30 additional minutes for setup/benchmarking, 30 for interpreting reports and 30 for runtime reading. BenchmarkDotNet **0.15.8** needs NuGet/network for its first restore. Run Release without a debugger:

```bash
# Still in labs/cost-model/dotnet
dotnet run -c Release --project Benchmarks -- --filter '*DedupeBenchmarks*' --job short
```

Input is created in GlobalSetup outside measurement. Each invocation creates fresh output; both methods have the same equality/output contract. The matrix is n=128/512/2048 with nominal 10%/100% distinct IDs of fixed width. **Optional prediction:** which allocates more? Does hashing retain as large an advantage when u is small?

**Solution:** Hash keeps an extra table and usually allocates more. Small u shortens the List, potentially reducing the time advantage. Measure actual time; do not infer a speed ratio from Big-O.

The agent ran all **12 ShortRun cases**, with three warmup and three measurement iterations per case. Example: n=512, all distinct:

| Approach | Mean | Error, half of 99.9% CI | Allocated per operation |
|---|---:|---:|---:|
| Scan | 922.355 µs | 2,261.779 µs | 8,384 B |
| Hash | 22.218 µs | 19.147 µs | 42,896 B |

Cloud Debian 13, Intel Xeon Platinum 8573C, .NET 10.0.12. The environment denied elevated process priority; wide intervals and a short run make timings **illustrative for this workload**, not production promises. The [full report](benchmark-report.md) and [execution log](benchmark-run.txt) preserve environment and limitations. Allocated excludes prebuilt input; it is not peak memory or service p99. The timing benchmark does not use CountScan's counters.

### Read a runtime slice without building all of .NET

Official repository `dotnet/runtime`, release v10.0.12 pinned at commit `4271d88e0aebf3d04f188f1334c2220d80555ef6`:

- [List.Contains](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/List.cs#L336): predict which call does the searching; follow IndexOf.
- [HashSet.AddIfNotPresent](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/HashSet.cs#L1411): locate hashing, buckets, equality, false return and resizing.
- [Upstream capacity test](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Collections/tests/Generic/HashSet/HashSet.Generic.Tests.cs#L552): identify the behavior tested upstream.

**Worked answer:** List.Contains calls IndexOf → Array.IndexOf. HashSet selects a bucket by hash and follows an entry chain; equality distinguishes colliding IDs. Existing IDs return false, and full storage can resize. The capacity test exercises growing element counts, not a universal O(1) proof. The agent read these sections and ran the local equivalent; **the upstream build/test suite was not executed**.

## 7. Transfer: count repeated IDs and retain first-occurrence order

**Optional exercise:** for `B2,A1,B2,C3,A1`, return `[(B2,2),(A1,2)]`, omitting IDs appearing once. Empty input returns `[]`; `A,A,A` returns `[(A,3)]`.

**Solution:** use a Dictionary for counts and a separate List for new-ID order. After reading the input, traverse the order List and emit only counts greater than one. Do not depend on Dictionary enumeration order.

```csharp
var counts = new Dictionary<string, int>(StringComparer.Ordinal);
var order = new List<string>();
foreach (string id in values)
{
    if (counts.TryGetValue(id, out int count)) counts[id] = count + 1;
    else { counts.Add(id, 1); order.Add(id); }
}
var duplicates = new List<(string Id, int Count)>();
foreach (string id in order)
    if (counts[id] > 1) duplicates.Add((id, counts[id]));
```

Invariant: counts equals occurrences in the processed prefix; order preserves first occurrences. Expected O(n+u)=O(n), auxiliary O(u), under hashing/key assumptions. The [runnable validated solution](../../labs/cost-model/dotnet/Core/Deduplication.cs) uses an OrderCount record rather than a tuple; behavior is equivalent.

### Production bridge: batch deduplication and idempotency

**Optional scenario:** two instances process message ID B2 concurrently with separate HashSets. Does this prevent system-wide duplicate processing?

**Solution:** no. Both sets start empty and both insert successfully. Enforce storage identity using a unique constraint/index on the appropriate business key, such as tenant + event ID, with transaction/conflict handling. A separate SELECT-before-INSERT still races. SQL Server collation must match identity rules; C# Ordinal does not automatically make database equality identical.

If a side effect is outside the database transaction, a unique key alone does not guarantee exactly-once execution of that side effect; an appropriate idempotency/transaction protocol is needed. Today's lesson establishes this boundary without requiring a distributed-system implementation.

## 8. Recap and continuation

**Three optional checks with answers:**

1. Why can one foreach be Θ(n²)? **Answer:** its body searches a growing List, summing 0+1+…+n−1.
2. Why both HashSet and List? **Answer:** membership and output ordering are separate responsibilities; the table costs additional memory.
3. Can hashing always be faster, or an API singleton set prevent every duplicate? **Answer:** no. Small workloads, key/comparer costs and allocations matter; local sets do not solve retries/multiple instances, and unbounded shared sets introduce memory/concurrency concerns.

For feedback you may send an explanation, code or report and state whether you read the solution. Rubric: contract/edge cases; reasoning with assumptions; operation counts versus measurements; production limits. Responses after solution exposure are assisted; a fresh task is needed for an independent assessment.

Suggested 1/3/7-day review hooks: reconstruct comparison counts, explain expected/amortized costs, transfer to duplicate counts or tenant-scoped identity. Core answers are in sections 2/4/7. These are study suggestions, not recorded reviews or confirmed progress schedules.

Next invocation: **“Dùng master-iuh-daily-learning, viết bài hôm nay cho tôi.”** No submission required. Publication/reference execution does not record learner completion or mastery.

## Sources and verification limits

Checked **5 October 2026**. The [source dossier](sources.json) records pins, metadata and reading scope.

- **Curriculum:** [IUH Master condensed curriculum](../../curricula/iuh/master/curriculum.md), course 6001127 outcomes. Current institutional PDFs/regulations were not reverified.
- **Theory:** [MIT 6.006 Hashing II, pages 1–3](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf): hashing assumptions, resizing and amortization; not a .NET benchmark.
- **API/implementation:** [List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0), [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0) and pinned runtime above. API documentation describes ordinary O(1) lookup; this lesson additionally states collision/key assumptions.
- **Measurement:** [BenchmarkDotNet getting started](https://benchmarkdotnet.org/articles/guides/getting-started.html), [good practices](https://benchmarkdotnet.org/articles/guides/good-practices.html); reports are actual agent execution, not learning evidence.
- **Database:** [SQL Server unique indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/create-unique-indexes?view=sql-server-ver17); the production bridge is instructor synthesis. No SQL Server lab or production workload was run.

Local lab/reference checks and a benchmark were executed. No learner study establishing the educational effectiveness of this lesson has been performed.
