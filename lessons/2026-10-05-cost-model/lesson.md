# Lesson 01 - Big-O and data structures: removing duplicate order IDs in C#

[Tiếng Việt](../../vi/lessons/2026-10-05-cost-model/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/cost-model/dotnet-lab.zip)

A simple loop can do billions of comparisons if each iteration searches a long list. This lesson analyzes that cost, uses `HashSet` to reduce the search work and examines the extra memory it needs. The same decision appears in EF Core change tracking, Azure Service Bus duplicate detection and SQL Server unique indexes.

**Objective:** deduplicate order IDs while preserving first-occurrence order, then explain when to scan and when to hash using correctness, comparison counts, execution time and allocated memory. Prerequisites: basic C# loops and collections.

## Core ideas

- **Cost model.** Before comparing algorithms, choose what to count. This lesson counts comparisons between two IDs; it is a simplified model, not a count of CPU instructions.
- **Big-O and Θ.** Big-O gives an upper bound on how fast cost grows for large inputs, ignoring constant factors: O(n) grows no faster than linearly, but may grow more slowly; for example, O(1) is also O(n). Θ gives a tight asymptotic bound: upper and lower bounds have the same order; `3n` is Θ(n), while `n²` is Θ(n²). Doubling n doubles the first formula and quadruples the second, but O alone does not promise those ratios or an execution time.
- **Worst case and expected case.** Worst case examines the most expensive input among inputs of the same size. Expected case averages cost under stated probability assumptions; with hashing, state the hash-distribution assumption instead of assuming every input is favorable.
- **Amortized analysis.** Add up the cost of a sequence of operations and spread it across them, without a probability assumption. A table expansion can be expensive, but does not happen on every insertion; the body will derive its total cost.
- **Invariant.** A property preserved after each loop step. If it holds initially, each step preserves it and it implies the requirement when the loop ends, it proves correctness. For example, after each step the result contains one copy of each ID read so far.

## 1. Quick self-check

**About 20 minutes - Check prerequisites:** try the questions, then open each answer to compare. This is the first lesson, so there are no earlier lessons to recall. **Stop when:** you know which questions need another look.

1. For `B2,A1,B2,C3,A1`, what output keeps the first-occurrence order? What does sorting do to it?

<details>
<summary>Answer</summary>

`B2,A1,C3`. Sorting gives `A1,B2,C3`, which breaks the "first occurrence order" requirement.

</details>

2. If you deduplicate `A,B,C,D` by comparing each ID with the result list so far, how many comparisons do you make?

<details>
<summary>Answer</summary>

`0+1+2+3 = 6`. The first item compares with nothing, the second with one item, and so on.

</details>

3. Do equal hashes mean equal IDs? Does a set in one process stop duplicates in another process?

<details>
<summary>Answer</summary>

No to both. Equal hashes can still be different keys, so equality is checked. Two processes each have their own empty set.

</details>

4. Is the benchmark’s `Allocated` column the most memory in use at one time?

<details>
<summary>Answer</summary>

No. `Allocated` measures the total new memory allocated by the operation. The most memory still in use at one time is a different quantity: earlier allocations may already have been reclaimed.

</details>

Not sure about sequential search? Draw `[B2, A1]`. Looking for `B2` stops after one comparison. Looking for `C3` compares with both items before you can say "not found". For `[X, Y, X]` the output is `[X, Y]` and the scan makes `0+1+1 = 2` comparisons. If this feels easy, spend the saved time on the experiment and the changed requirement later.

## 2. A small production requirement

**Requirement · 10 minutes.** State order, equality and null rules. **Done when:** the five-ID example has one unambiguous result.

A logistics job receives order IDs from a log or a message batch. An ID can appear many times. Return each ID **once, in the order it first appeared**.

```text
Input : B2, A1, B2, C3, A1
Output: B2, A1, C3
```

Fix three rules before optimizing anything:

- Compare exactly with `StringComparer.Ordinal`: `a` is not `A`. No silent trim or lowercase.
- Keep first-occurrence order. Sorting to `A1,B2,C3` breaks the requirement.
- Do not modify the input. The input list and each ID are not null; the lab code rejects null. An empty string is a valid value in this example.

This deduplicates **within one batch**; it does not ensure that each message is processed once across the system. Section 10 analyzes that limit. Write `n` for the input size and `u` for the number of different IDs.

**Try it:** how many items and how many different IDs are in the example? With a temporary output `[B2, A1]`, what must you do to know if `C3` was seen?

<details>
<summary>Answer</summary>

n = 5 items and u = 3 different IDs. To check `C3` against `[B2, A1]` with a sequential search you compare it with `B2` and then `A1`, and only then know it is new. If this "must check everything before saying no" idea is unclear, reread the trace in section 3 slowly; the rest of the lesson depends on it.

</details>

## 3. One loop, a lot of hidden work

**Trace · 15 minutes.** Count each comparison and derive the all-distinct sum. **Done when:** you can reconstruct the sum rather than count loop lines.

The familiar version:

```csharp
var result = new List<string>();
foreach (string id in values)
{
    if (!result.Contains(id))
        result.Add(id);
}
```

`List.Contains` searches the items already in `result` and stops when it finds an equal ID. If there is none, it must search all of them. One API call can hide a lot of work.

| ID being read | `result` before | Sequential comparisons | `result` after |
|---|---|---|---|
| B2 | [] | 0 | [B2] |
| A1 | [B2] | A1 vs B2: 1 | [B2,A1] |
| B2 | [B2,A1] | B2 vs B2: 1, stop | [B2,A1] |
| C3 | [B2,A1] | C3 vs B2 and A1: 2 | [B2,A1,C3] |
| A1 | [B2,A1,C3] | A1 vs B2, then A1: 2, stop | [B2,A1,C3] |

The total is **6 comparisons** in this model, although `foreach` ran 5 times. This is a counting model, not a measurement of CPU instructions in the .NET runtime.

### The all-distinct case

For `A,B,C,D` the counts are `0,1,2,3`. The k-th ID is compared with the k-1 IDs before it. For n distinct IDs:

```text
C(n) = 0 + 1 + 2 + ... + (n-1) = n(n-1)/2
```

To see the formula, write the sum forwards and backwards. Each pair of the same position adds up to n-1, and there are n pairs, so two copies of the sum equal `n(n-1)`. One copy is half of that.

| n, all different | Comparisons in the model |
|---:|---:|
| 128 | 8,128 |
| 256 | 32,640 |
| 512 | 130,816 |
| 100,000 | 4,999,950,000 |

Double the input and the work grows about four times. You cannot turn these numbers into milliseconds yet: CPU, runtime and data all change real time.

## 4. What Big-O says and does not say

**Cost model · 10 minutes.** Explain the asymptotic bound and its key-length assumption. **Done when:** you can reject a timing claim based only on Big-O.

**Formal definition.** `T(n)` is `O(n²)` if there are constants C and n₀ such that `T(n) ≤ C·n²` for all `n ≥ n₀`. It means "grows no faster than n²", not "takes n² seconds".

For all-distinct IDs, `n(n-1)/2` is dominated by the n² term, so the scan model is **Θ(n²)**: the upper and lower bounds have the same order. Saying O(n²) is true but looser. An O(n) algorithm also satisfies the O(n²) bound, so use the tight order when you explain.

**What if every ID is `A`?** After the first ID, each `Contains` finds a match immediately: only n-1 comparisons, which is Θ(n). Worst case does not mean every input is slow.

With u different IDs the list has at most u items, so the scan is bounded by `O(n(1+u))`. When u is small it can be good enough. When u has the same order as n, or u = Θ(n), the worst case is Θ(n²); all-distinct input is one example.

**Try it:** you see one `foreach` over n items. Can you say it is O(n)?

<details>
<summary>Answer</summary>

Not yet. You must add up the cost of the loop body on each iteration. `Contains`, a database query or a service call each have their own cost. Counting lines of code is not enough.

</details>

## 5. Separate "seen it?" from "output order"

**Mechanism · 15 minutes.** Prove the prefix invariant and account for extra storage. **Done when:** expected, amortized and worst-case claims remain distinct.

There are two different jobs: "have I seen this ID?" and "in what order do I output?". Use a `HashSet` for the first and a `List` for the second.

```csharp
var seen = new HashSet<string>(StringComparer.Ordinal);
var result = new List<string>();
foreach (string id in values)
{
    if (seen.Add(id))   // true: just added; false: already there
        result.Add(id);
}
```

`Add` already checks for duplicates, so you do not need `Contains` followed by `Add` (two searches). Never rely on `HashSet` enumeration order; the order comes from `result.Add` following the input.

### Why hashing helps

A hash function turns an ID into a number that selects a bucket of entries to check. You search that bucket instead of the whole list. A collision occurs when different IDs land in the same bucket. **Equal hashes do not guarantee equal IDs**: the runtime still checks equality.

Load factor is the number of entries divided by the number of buckets: 8 entries and 16 buckets gives 0.5. Growing the table fast enough relative to the entry count bounds the average bucket size.

If hashes spread well, each bucket stays small, and the cost of one key is bounded, then a lookup does a constant amount of work on average. Three words appear here, and they are different promises:

- **Expected** means "on average under an assumption" about how keys spread. It does not promise anything about a single input.
- **Amortized** means total cost over many operations. One resize may cost O(u), but growing capacity by a factor each time means the sum `1+2+4+...` stays O(u). This explains the principle; it does not say .NET uses exactly those capacities.
- **Worst case**: bad hashing or an unlucky comparer can create long collision chains and push the whole batch back to O(n²). .NET adds protection for some string comparers. Do not assume every custom comparer has it.

So the hash version is **expected O(n)** for the whole batch, with amortized resizing, under those assumptions. The lab counts n `Add` calls; that number is not total hash, equality and resize work.

If IDs have up to L characters, hashing and equality can cost O(L). When L changes with the input, include it: expected `O(n(1+L))`. Do not drop key length just because you use a `HashSet`.

### Prove it with an invariant

After reading any prefix of the input: `seen` contains exactly the IDs read so far, and `result` contains each of them once, in first-occurrence order.

At the start both are empty. A repeated ID makes `Add` return false: nothing changes. A new ID makes `Add` return true and it is appended at the end of `result`, so the order stays right. When the input is finished, the invariant is the requirement. You changed the cost and kept the behavior.

### Memory: same Big-O does not mean same bytes

| Approach | Time in the model | Extra memory, without output | Output |
|---|---|---|---|
| Scan a List | O(n(1+u)); Θ(n²) when all different | O(1) | O(u) |
| HashSet + List | Expected O(n), with assumptions | O(u) | O(u) |

`HashSet` needs extra bucket and entry arrays. `List` holds references to input strings, rather than making copies. When a larger array is needed, the runtime allocates it and copies the data; the old array may wait for GC to reclaim it once it is unreachable.

**Total allocated memory, live memory and peak working set are three different quantities.** Peak live memory is the most memory alive at one time; peak working set is the most process memory resident in RAM. Allocating two arrays one after another does not mean both remain alive forever.

`new HashSet<string>(n, ...)` or `new List<string>(n)` can reduce resizing when you know the size, but with a large n and small u you reserve too much. If you preallocate for n, do not call that storage O(u) when u is small and independent of n. Keep this tweak out of the main version for now.

**Break · 10 minutes.** Leave the screen.

## 6. Sources and research questions

**About 45 minutes - Read and compare sources:** answer the four questions in your own words, stating a claim and supporting evidence. **Stop when:** each answer has a source and a limit to the claim.

Sources for this lesson:

- [Microsoft: List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0) and [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0) for the equality check, return value and resize behavior.
- [MIT OCW: Hashing II, pages 1-3](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/160b3b5f9da2e03815ca1e6ee0dba62a_MIT6_006F11_lec09.pdf) for the load factor assumption and amortized table growth.
- [BenchmarkDotNet good practices](https://benchmarkdotnet.org/articles/guides/good-practices.html) for a fair Release benchmark.

Four questions to answer:

1. What work does `List.Contains` hide?

<details>
<summary>Answer</summary>

A sequential search. A hit stops early; a miss reads every item before it.

</details>

2. Why can one `Add` cost O(u) while a whole batch is expected O(n)?

<details>
<summary>Answer</summary>

Resize costs add up like `1+2+4+...`, so they total O(u). The expected O(1) lookup also needs good hashing and bounded key cost, which are assumptions.

</details>

3. Why do collisions keep results correct but threaten performance?

<details>
<summary>Answer</summary>

Equality still separates different keys, so the answer is right. A long chain means more comparisons per lookup.

</details>

4. What can a synthetic benchmark tell you about a real service?

<details>
<summary>Answer</summary>

Only about the workload and scope you measured. Production key distribution, peak memory and p99 latency need their own measurement.

</details>

## 7. Reading real code: collections and EF Core

**About 45 minutes - Follow the implementation:** read the `HashSet.Add` path, then compare it with EF Core’s use of a dictionary. **Stop when:** you can explain what EF Core stores and which problem the dictionary solves.

### Collection source

`List.Contains` calls `IndexOf`, which finally searches an array. The .NET runtime may specialize some types and make the constant factor smaller, but a miss still checks every earlier candidate.

`HashSet.Add` takes a different path:

```text
ID -> compute hash -> choose bucket -> look at entries in the bucket
   -> hash matches AND ID equal? return false
   -> otherwise go to the next entry
   -> no equal entry? take a slot (resize if needed), insert, return true
```

A **bucket** is the entry point to a group of candidates. A **collision chain** links entries in the same bucket. A stored hash rejects most candidates cheaply; equality decides identity. A resize creates bigger storage and moves entries, so one `Add` can be expensive even though the amortized cost is small.

Trace three cases: an empty set receives B2; B2 comes again; A1 is new and has the same hash as B2.

<details>
<summary>Answer</summary>

B2 is inserted and `Add` returns true. B2 again is found equal and `Add` returns false. A1 is compared with B2, found different, then inserted and `Add` returns true. The separate `List` keeps the output order in all three cases.

</details>

Pinned source to read: [List.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/List.cs#L336) and [HashSet.cs](https://github.com/dotnet/runtime/blob/4271d88e0aebf3d04f188f1334c2220d80555ef6/src/libraries/System.Private.CoreLib/src/System/Collections/Generic/HashSet.cs#L1411) from a .NET 10 commit. Find where the bucket is chosen, where equality is checked, where false is returned and where resize happens. You do not need to build the runtime.

### Case study: EF Core uses a dictionary so loading rows does not scan

If your project uses EF Core, this is a familiar place to see the same decision in a product. The project is [dotnet/efcore](https://github.com/dotnet/efcore), read at commit `7adff35c6c583fa6f7aa3939389ab3314be330ab`.

**The product problem.** In a tracking query, rows with the same key must share an entity. If 100 posts reference one blog, EF Core reuses one `Blog` instance to track changes consistently instead of holding 100 instances with the same key. This is identity resolution. Before creating an entity from each row, EF Core must answer: "is there already an entity with this key?"

**What the code does** (verified in the pinned source):

- In [`IdentityMap.cs` line 18](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L18) the tracker holds `Dictionary<TKey, InternalEntityEntry> _identityMap`. The key is the entity's key value; the value is the tracked entry.
- In [line 36](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L36) the dictionary is created with the key's own equality comparer from the model. This is the same rule as your `StringComparer.Ordinal`: the equality used for "seen" must match the identity you want.
- A tracking query looks up the key **before creating an entity**. [`ShapedQueryCompilingExpressionVisitor` lines 473-513](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/Query/ShapedQueryCompilingExpressionVisitor.cs#L473) generates a call to `QueryContext.TryGetEntry(key, keyValues, ...)`. That delegates to the state manager and identity map. On a hit the query reuses `entry.Entity`; only a miss creates a new entity. The identity map's key lookup is a dictionary read ([line 105](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L105)).
- Registering the new query entity is a separate step: [`QueryContext.StartTracking`](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/Query/QueryContext.cs#L148) calls [`StateManager.StartTrackingFromQuery`](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/StateManager.cs#L324). Its initial `TryGetEntry(entity)` checks the object reference, not the row key; it then creates an entry and registers it through `AddOrUpdate` ([line 347](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/StateManager.cs#L347)).
- Attaching a second distinct instance with an already tracked key is another path. `IdentityMap.Add` can throw an identity conflict ([lines 267-279](https://github.com/dotnet/efcore/blob/7adff35c6c583fa6f7aa3939389ab3314be330ab/src/EFCore/ChangeTracking/Internal/IdentityMap.cs#L267)); the query's `AddOrUpdate` sets `updateDuplicate: true` and skips that branch. Do not confuse attachment conflicts with query identity resolution.

**What the official docs add.** The EF docs on [efficient querying](https://learn.microsoft.com/ef/core/performance/efficient-querying#tracking,-no-tracking-and-identity-resolution) say EF keeps a dictionary of tracked instances and checks it by key when new data is loaded, and that this lookup and maintenance "take up some time". They also say a no-tracking query does not do identity resolution, so the same blog would be materialized 100 times. The [identity resolution page](https://learn.microsoft.com/ef/core/change-tracking/identity-resolution#identity-resolution-and-queries) gives the reason: identity resolution has to remember every instance it returned, which hurts streaming a large number of entities.

**Map it to the lesson.**

| This lesson | EF Core |
|---|---|
| `seen` set | `_identityMap` dictionary, keyed by entity key |
| Ordinal equality chosen on purpose | Key comparer taken from the model |
| O(u) extra memory to avoid repeated scanning | One entry per distinct entity while it remains tracked; detaching or clearing the tracker removes entries |
| Skip the set to save memory | `AsNoTracking`: no dictionary, but duplicates |

**Instructor inference, not verified in code.** If EF had searched a list of tracked entities for every row, loading n rows with u different entities would cost O(n·u) key comparisons, the same shape as `List.Contains`. EF's history is not claimed here; this is only the counterfactual that shows why a dictionary is the natural choice. No EF timing was measured in this lesson.

**How to apply it in your project.**

1. Large read-only list (a grid or an export): use `AsNoTracking()`. You skip the dictionary and the snapshot. Expect repeated parent objects, so do not rely on "same customer = same instance".
2. Read-only result where shared parents must be the same object: use `AsNoTrackingWithIdentityResolution()`. You pay for a temporary dictionary during the query.
3. Your own code needs "seen this key?" across thousands of rows (merging API results, building a lookup for a join): use `HashSet` or `Dictionary` with an explicit comparer, as EF does. Do not call `list.Contains` or `Any` in a loop.
4. If a `DbContext` lives long and loads a lot, its identity map grows with the number of distinct entities. Prefer one short-lived context per unit of work.

### Optional check: see identity resolution in a running query

Use 15 minutes of this implementation-reading block for this check instead of part of the source reading. It uses .NET SDK 10.0.401, EF Core SQLite 10.0.12 and an in-memory SQLite database, so no database server is needed.

Two `Post` rows, IDs 1 and 2, both refer to `BlogId = 1`. For each query mode, predict whether `ReferenceEquals(posts[0].Blog, posts[1].Blog)` is true and how many entities remain in the context's change tracker. Why must each query use a fresh `DbContext`? Run the check or, if package restore is unavailable, trace the code and output in the answer.

<details>
<summary>Answer</summary>

The same lab ZIP includes `IdentityDemo`. SDK/runtime pins in its shared `global.json` and project match the main lab; its lock file fixes direct and transitive EF Core dependencies. The first restore needs NuGet access. Run from the extracted `dotnet` directory or `labs/cost-model/dotnet` in a checkout:

```bash
dotnet restore IdentityDemo --locked-mode
dotnet run --no-restore -c Release --project IdentityDemo
```

`IdentityDemo/IdentityDemo.csproj`:

<!-- lab-file: IdentityDemo/IdentityDemo.csproj -->
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RuntimeFrameworkVersion>10.0.12</RuntimeFrameworkVersion>
    <RollForward>Disable</RollForward>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode>true</RestoreLockedMode>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore.Sqlite" Version="10.0.12" />
  </ItemGroup>
</Project>
```

`IdentityDemo/packages.lock.json`:

<!-- lab-file: IdentityDemo/packages.lock.json -->
```json
{
  "version": 1,
  "dependencies": {
    "net10.0": {
      "Microsoft.EntityFrameworkCore.Sqlite": {
        "type": "Direct",
        "requested": "[10.0.12, )",
        "resolved": "10.0.12",
        "contentHash": "rRXkKBWHjtngj2DYqSXOThGpqiR0LQkxk0b0PIVDhVEzfwpgOR7dbKMw1/My8unDCTCwn/blclR7imxntYGvEg==",
        "dependencies": {
          "Microsoft.EntityFrameworkCore.Sqlite.Core": "10.0.12",
          "Microsoft.Extensions.Caching.Memory": "10.0.12",
          "Microsoft.Extensions.Configuration.Abstractions": "10.0.12",
          "Microsoft.Extensions.DependencyModel": "10.0.12",
          "Microsoft.Extensions.Logging": "10.0.12",
          "SQLitePCLRaw.bundle_e_sqlite3": "2.1.12",
          "SQLitePCLRaw.core": "2.1.12"
        }
      },
      "Microsoft.Data.Sqlite.Core": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "2aL9eL5HQr0V4b8V909SD+jQAx6qnTTl7sT/v3D8dIvmr2UGdpZIQxqm1pj2Js3e4EYTvpw0oMH7DjapJJuPPw==",
        "dependencies": {
          "SQLitePCLRaw.core": "2.1.12"
        }
      },
      "Microsoft.EntityFrameworkCore": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "e7OrVN8U5yr4kuwdTHWBHGVQIVsGfMkAr0Ej1/BnrS989Q0XBVANpIzNZ2bc1GvMZ0/XwMt5InTnmKskxGy99Q==",
        "dependencies": {
          "Microsoft.EntityFrameworkCore.Abstractions": "10.0.12",
          "Microsoft.EntityFrameworkCore.Analyzers": "10.0.12",
          "Microsoft.Extensions.Caching.Memory": "10.0.12",
          "Microsoft.Extensions.Logging": "10.0.12"
        }
      },
      "Microsoft.EntityFrameworkCore.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "kDrux7T6C3V/YYYe2LXr7x6AEsVyq5Y2YoTE9er1SwbDtap3z1g8RgxNh5eKQVyB4T+DKvBBJ4Ezd/VZzJQJZg=="
      },
      "Microsoft.EntityFrameworkCore.Analyzers": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "Kd4o2oO1A6dfKxjz5LS16QyLtpCFTUiFWwmBABETAXRsSImBdRdWeKjSgbbRhAMiV3a3/nWr95ZtzClT4uaADQ=="
      },
      "Microsoft.EntityFrameworkCore.Relational": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "OiHmr8XzX96dbgMsYGe8qoqg4KxibdZG2r0QUVJBGktFInOp8IrABe8jvcbo5hrqeWfbwpK7fCEBiEPbY/ik4A==",
        "dependencies": {
          "Microsoft.EntityFrameworkCore": "10.0.12",
          "Microsoft.Extensions.Caching.Memory": "10.0.12",
          "Microsoft.Extensions.Configuration.Abstractions": "10.0.12",
          "Microsoft.Extensions.Logging": "10.0.12"
        }
      },
      "Microsoft.EntityFrameworkCore.Sqlite.Core": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "DAGu68RfIDD5d6qYhtQqMUsRS7hKKFqHI6h/9VUa4FjMcQ8+IJA0rK+1pDZtrDJ+yi3YAG0L2TSViZ0csEDM0w==",
        "dependencies": {
          "Microsoft.Data.Sqlite.Core": "10.0.12",
          "Microsoft.EntityFrameworkCore.Relational": "10.0.12",
          "Microsoft.Extensions.Caching.Memory": "10.0.12",
          "Microsoft.Extensions.Configuration.Abstractions": "10.0.12",
          "Microsoft.Extensions.DependencyModel": "10.0.12",
          "Microsoft.Extensions.Logging": "10.0.12",
          "SQLitePCLRaw.core": "2.1.12"
        }
      },
      "Microsoft.Extensions.Caching.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "sI3A6MUAyZwccLnwq0cXuRmC3WBtXieimBWafXSfhRJ4jnM2uGVXrqImDDVyW27u4vVaTOGlJxNJd8d1FGvCNQ==",
        "dependencies": {
          "Microsoft.Extensions.Primitives": "10.0.12"
        }
      },
      "Microsoft.Extensions.Caching.Memory": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "fhC3DHcBcFF4bXvHIxFtXJYNut7q7ZItqNFcgWfrIgmpVImlcEKNHhE7ztpNSPJYMHYYStS5QGND2I5mC26yeA==",
        "dependencies": {
          "Microsoft.Extensions.Caching.Abstractions": "10.0.12",
          "Microsoft.Extensions.DependencyInjection.Abstractions": "10.0.12",
          "Microsoft.Extensions.Logging.Abstractions": "10.0.12",
          "Microsoft.Extensions.Options": "10.0.12",
          "Microsoft.Extensions.Primitives": "10.0.12"
        }
      },
      "Microsoft.Extensions.Configuration.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "8xaGcvS/qZ1otoxPQCEJkNva389CVL/plNcvIETZhQTETYdRkYDPEYhUMoAGONo4FU45ufdfE0j29AfWVVj0wA==",
        "dependencies": {
          "Microsoft.Extensions.Primitives": "10.0.12"
        }
      },
      "Microsoft.Extensions.DependencyInjection": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "lXyK2O5GoYvfxW8eCFcD16JFbcoSTM1sJkAM0UHS1jZyl9NYMW64Tqm6OQFT0IDBjZi+xHt95/Zg+nxZhGFhZg==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "10.0.12"
        }
      },
      "Microsoft.Extensions.DependencyInjection.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "9/qymSh7hVDMGTGwrLz8MRp5zRyXy9adGDOs4HwRdnLil3oZGYuWeZjbmHgCQ9BL1qBroVfgUK3U/nb61617Cw=="
      },
      "Microsoft.Extensions.DependencyModel": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "rDPQVTxh/zMTDF7wHlRqL/jjZbwjAP6315ydBxj51pZW7qkAwGwjoSiMutxYI91xmOE3ZXjAGHbYRqzyJV7Urw=="
      },
      "Microsoft.Extensions.Logging": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "6I46fTPfgYkrjRYfRXbho9WOvOelTnNjWuZws/hzGHDASH1LEJeA4VKK9k3wJvido8o7jJSB5WkMTonX7HM1bA==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection": "10.0.12",
          "Microsoft.Extensions.Logging.Abstractions": "10.0.12",
          "Microsoft.Extensions.Options": "10.0.12"
        }
      },
      "Microsoft.Extensions.Logging.Abstractions": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "+24lC4plfbEDNfLAdTV/SWKS7dW+16X4HdydO3R++134kSNTzcbYA4KpR1Hdh6uWisB8Za3AzwyOn+K+NxWIug==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "10.0.12"
        }
      },
      "Microsoft.Extensions.Options": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "TDYD33TSRpXKZWlmTXNlj5kCihxatmv2Ec1u6C+bMYLphCS7PoSLE9Pjd/nunDoE7yETk+LLKjVJX78HYtWjpA==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "10.0.12",
          "Microsoft.Extensions.Primitives": "10.0.12"
        }
      },
      "Microsoft.Extensions.Primitives": {
        "type": "Transitive",
        "resolved": "10.0.12",
        "contentHash": "dYfCLR52UA+3DL7C4I/pvSaRPkNqxrUAQmbFL2u0zvYKKzqgrFCJl08Df+F1aYc8leu9JvpC9bsURUdpExcBXQ=="
      },
      "SQLitePCLRaw.bundle_e_sqlite3": {
        "type": "Transitive",
        "resolved": "2.1.12",
        "contentHash": "mAgscpQMLw5/nfA1Q5oJVAT29yROUo1ifZGbbTpx/lwZpSxMUGoYbKfmvdm8oXER+RzxqBmmQzeBEVKfeHv2nw==",
        "dependencies": {
          "SQLitePCLRaw.lib.e_sqlite3": "2.1.12",
          "SQLitePCLRaw.provider.e_sqlite3": "2.1.12"
        }
      },
      "SQLitePCLRaw.core": {
        "type": "Transitive",
        "resolved": "2.1.12",
        "contentHash": "ETpNw9DY3ckWLgRRAeCHj+GKOuPi61aeczkXhgHexUvqoZBAYg8RYESE2J7O1M7+o6QbdSEZwrw9bfqztUVWXg=="
      },
      "SQLitePCLRaw.lib.e_sqlite3": {
        "type": "Transitive",
        "resolved": "2.1.12",
        "contentHash": "fWi8Dbknuhgg72fWinIdjXVaqO1hHL4YBBwVLnr7e1c9TAZwJ0QE38j9syW1hwx6HaqEVTwI+O07WPdZn8Rp0w=="
      },
      "SQLitePCLRaw.provider.e_sqlite3": {
        "type": "Transitive",
        "resolved": "2.1.12",
        "contentHash": "W3oH4XIfCzFrgUSDKHhN6N+dgzA5YHOR2VxX8GB6Qy7CyrJJgxPEG8NirgYWlPQC5P2jz2knSsexWu4tDUL33g==",
        "dependencies": {
          "SQLitePCLRaw.core": "2.1.12"
        }
      }
    }
  }
}
```

`IdentityDemo/Program.cs`:

<!-- lab-file: IdentityDemo/Program.cs -->
```csharp
using Microsoft.Data.Sqlite;
using Microsoft.EntityFrameworkCore;

using var connection = new SqliteConnection("Data Source=:memory:");
connection.Open();
var options = new DbContextOptionsBuilder<BlogDb>()
    .UseSqlite(connection).Options;
using (var seed = new BlogDb(options))
{
    seed.Database.EnsureCreated();
    var blog = new Blog { Id = 1 };
    seed.Posts.AddRange(
        new Post { Id = 1, Blog = blog },
        new Post { Id = 2, Blog = blog });
    seed.SaveChanges();
}

Check("Tracking", 0, expectedSame: true, expectedTracked: 3);
Check("NoTracking", 1, expectedSame: false, expectedTracked: 0);
Check("IdentityResolution", 2, expectedSame: true, expectedTracked: 0);
Console.WriteLine("All checks passed.");

void Check(string name, int mode, bool expectedSame, int expectedTracked)
{
    using var db = new BlogDb(options);
    IQueryable<Post> query = db.Posts.Include(p => p.Blog).OrderBy(p => p.Id);
    query = mode switch
    {
        1 => query.AsNoTracking(),
        2 => query.AsNoTrackingWithIdentityResolution(),
        _ => query
    };
    var posts = query.ToList();
    if (posts.Count != 2 || posts.Any(p => p.Blog.Id != 1))
        throw new InvalidOperationException("Expected two posts for Blog 1.");
    bool same = ReferenceEquals(posts[0].Blog, posts[1].Blog);
    int tracked = db.ChangeTracker.Entries().Count();
    Console.WriteLine($"{name}: sameBlog={same}, tracked={tracked}");
    if (same != expectedSame || tracked != expectedTracked)
        throw new InvalidOperationException($"Unexpected result for {name}.");
}

sealed class BlogDb(DbContextOptions<BlogDb> options) : DbContext(options)
{
    public DbSet<Post> Posts => Set<Post>();
}

sealed class Blog
{
    public int Id { get; set; }
}

sealed class Post
{
    public int Id { get; set; }
    public int BlogId { get; set; }
    public Blog Blog { get; set; } = null!;
}
```

Run it from the project directory:

```bash
dotnet run
```

Expected output:

```text
Tracking: sameBlog=True, tracked=3
NoTracking: sameBlog=False, tracked=0
IdentityResolution: sameBlog=True, tracked=0
All checks passed.
```

The tracking query reuses one `Blog` object and leaves three entities in the context: two posts and one blog. `AsNoTracking()` creates two separate `Blog` objects with the same key and leaves the context empty. `AsNoTrackingWithIdentityResolution()` reuses one `Blog` within the query using a temporary tracker, then leaves the context empty too. `ReferenceEquals` compares object identity; matching key values alone do not make two objects the same instance.

The seed context is disposed before querying, and each mode gets a new context. Otherwise already tracked objects could affect the result. The open SQLite connection keeps the in-memory database alive across these contexts. The assertions check correctness, not query speed; this is not a benchmark.

</details>

**Break · 30 minutes (lunch).** Eat and rest.

## 8. Guided C# practice

**About 75 minutes - Write and test code:** implement the method, predict edge cases, run tests, deliberately violate a requirement and repair it. **Stop when:** the checks pass and you can explain an avoided defect and an assumption the code needs.

Implement stable deduplication under the ordinal/order/null rules. Predict edge cases and compare against the scan reference. You may open the complete solution immediately.

<details>
<summary>Answer - setup, complete code and results</summary>

SDK **10.0.401**, runtime **10.0.12**; SDK/runtime roll-forward is disabled. Copy paths relative to `dotnet`. Restore resolves only the pinned packages; the benchmark lock file fixes transitive dependencies too.

`global.json`:

<!-- lab-file: global.json -->
```json
{
  "sdk": { "version": "10.0.401", "rollForward": "disable" }
}
```

`Core/Core.csproj`:

<!-- lab-file: Core/Core.csproj -->
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

`Core/Deduplication.cs`:

<!-- lab-file: Core/Deduplication.cs -->
```csharp
namespace CostModel;

public sealed record OrderCount(string Id, int Count);

// Contract: non-null IDs, ordinal equality, first-occurrence order, unchanged input.
public static class Deduplication
{
    public static List<string> Scan(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var result = new List<string>();
        foreach (string value in values)
        {
            RejectNull(value);
            if (!result.Contains(value)) result.Add(value);
        }
        return result;
    }

    public static List<string> Hash(IReadOnlyList<string> values,
        IEqualityComparer<string>? comparer = null)
    {
        ArgumentNullException.ThrowIfNull(values);
        var seen = new HashSet<string>(comparer ?? StringComparer.Ordinal);
        var result = new List<string>();
        foreach (string value in values)
        {
            RejectNull(value);
            // Add is false for an existing equal ID; no separate Contains lookup.
            if (seen.Add(value)) result.Add(value);
        }
        return result;
    }

    public static List<OrderCount> DuplicateSummary(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var counts = new Dictionary<string, int>(StringComparer.Ordinal);
        var order = new List<string>();
        foreach (string value in values)
        {
            RejectNull(value);
            if (counts.TryGetValue(value, out int count)) counts[value] = count + 1;
            else { counts.Add(value, 1); order.Add(value); }
        }
        var result = new List<OrderCount>();
        foreach (string id in order)
            if (counts[id] > 1) result.Add(new OrderCount(id, counts[id]));
        return result;
    }

    // Explicit equality-count model; do not benchmark this instrumented method.
    public static (List<string> Result, long Comparisons) CountScan(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var result = new List<string>();
        long comparisons = 0;
        foreach (string value in values)
        {
            RejectNull(value);
            bool found = false;
            foreach (string previous in result)
            {
                comparisons++;
                if (StringComparer.Ordinal.Equals(previous, value)) { found = true; break; }
            }
            if (!found) result.Add(value);
        }
        return (result, comparisons);
    }

    private static void RejectNull(string? value)
    {
        if (value is null) throw new ArgumentException("Order IDs must not be null.");
    }

    // Count only calls in the explicit model, not hash/equality/resize work.
    public static (List<string> Result, int AddCalls) CountHash(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var result = new List<string>();
        var seen = new HashSet<string>(StringComparer.Ordinal);
        int calls = 0;
        foreach (string value in values)
        {
            RejectNull(value);
            calls++;
            if (seen.Add(value)) result.Add(value);
        }
        return (result, calls);
    }
}

public static class Dataset
{
    public static string[] Make(int n, int distinct)
    {
        if (n <= 0 || distinct <= 0 || distinct > n) throw new ArgumentOutOfRangeException();
        return Enumerable.Range(0, n).Select(i => $"ORD-{i % distinct:D8}").ToArray();
    }
}
```

`LessonLab/LessonLab.csproj`:

<!-- lab-file: LessonLab/LessonLab.csproj -->
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RuntimeFrameworkVersion>10.0.12</RuntimeFrameworkVersion>
    <RollForward>Disable</RollForward>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
  <ItemGroup><ProjectReference Include="../Core/Core.csproj" /></ItemGroup>
</Project>
```

`LessonLab/Program.cs`:

<!-- lab-file: LessonLab/Program.cs -->
```csharp
using CostModel;

if (args.Contains("--check")) { Checks.Run(); return; }

string[] example = ["B2", "A1", "B2", "C3", "A1"];
Console.WriteLine($"Stable result: {string.Join(", ", Deduplication.Hash(example))}");
Console.WriteLine($"Example scan comparisons: {Deduplication.CountScan(example).Comparisons}");
Console.WriteLine("n,scan_equality_comparisons,hash_add_calls (not hash-table work)");
foreach (int n in new[] { 128, 256, 512 })
{
    string[] values = Dataset.Make(n, n);
    var hashed = Deduplication.CountHash(values);
    Console.WriteLine($"{n},{Deduplication.CountScan(values).Comparisons},{hashed.AddCalls}");
}
Console.WriteLine($"128 identical IDs: {Deduplication.CountScan(Dataset.Make(128, 1)).Comparisons} scan comparisons");
Console.WriteLine($"Duplicates: {string.Join(", ", Deduplication.DuplicateSummary(example).Select(x => $"{x.Id}={x.Count}"))}");
```

`LessonLab/Checks.cs`:

<!-- lab-file: LessonLab/Checks.cs -->
```csharp
using CostModel;

internal static class Checks
{
    public static void Run()
    {
        int passed = 0;
        void Check(string name, Action test) { test(); passed++; Console.WriteLine($"PASS {name}"); }
        void Equal<T>(IEnumerable<T> actual, IEnumerable<T> expected)
        { if (!actual.SequenceEqual(expected)) throw new Exception("Sequence mismatch"); }
        void Throws<T>(Action action) where T : Exception
        { try { action(); } catch (T) { return; } throw new Exception($"Expected {typeof(T).Name}"); }

        Check("stable order and unchanged input", () => {
            string[] input = ["B2", "A1", "B2", "C3", "A1"]; var before = input.ToArray();
            Equal(Deduplication.Scan(input), new[] { "B2", "A1", "C3" });
            Equal(Deduplication.Hash(input), new[] { "B2", "A1", "C3" }); Equal(input, before);
        });
        Check("empty, singleton and repeated input", () => {
            foreach (var (input, expected) in new[] {
                (Array.Empty<string>(), Array.Empty<string>()),
                (new[] { "A" }, new[] { "A" }), (new[] { "A", "A", "A" }, new[] { "A" }) })
            { Equal(Deduplication.Scan(input), expected); Equal(Deduplication.Hash(input), expected); }
        });
        Check("ordinal identity and explicit alternative comparer", () => {
            string[] input = ["a", "A", "a", " a ", ""];
            Equal(Deduplication.Scan(input), new[] { "a", "A", " a ", "" });
            Equal(Deduplication.Hash(input), new[] { "a", "A", " a ", "" });
            Equal(Deduplication.Hash(input, StringComparer.OrdinalIgnoreCase), new[] { "a", " a ", "" });
        });
        Check("null policy", () => {
            Throws<ArgumentNullException>(() => Deduplication.Scan(null!));
            Throws<ArgumentNullException>(() => Deduplication.Hash(null!));
            Throws<ArgumentException>(() => Deduplication.Scan(new[] { "A", null! }));
            Throws<ArgumentException>(() => Deduplication.Hash(new[] { "A", null! }));
            Throws<ArgumentException>(() => Deduplication.DuplicateSummary(new string[] { null! }));
        });
        Check("triangular count and repeated-ID count", () => {
            foreach (int n in new[] { 1, 128, 256, 512 }) {
                var input = Dataset.Make(n, n);
                var hashModel = Deduplication.CountHash(input);
                Equal(hashModel.Result, Deduplication.Hash(input));
                if (hashModel.AddCalls != n) throw new Exception("Wrong Add-call model");
                if (Deduplication.CountScan(Dataset.Make(n, n)).Comparisons != (long)n * (n - 1) / 2)
                    throw new Exception("Wrong distinct count model");
                if (Deduplication.CountScan(Dataset.Make(n, 1)).Comparisons != n - 1)
                    throw new Exception("Wrong repeated count model");
            }
        });
        Check("hash path avoids a membership scan on this workload", () => {
            var comparer = new CountingComparer(); var input = Dataset.Make(512, 512);
            Equal(Deduplication.Hash(input, comparer), input);
            if (comparer.Equalities >= 512) throw new Exception("Unexpected equality scan");
        });
        Check("forced collisions preserve correctness and expose quadratic work", () => {
            var comparer = new CountingComparer(constantHash: true); var input = Dataset.Make(128, 128);
            Equal(Deduplication.Hash(input, comparer), input);
            if (comparer.Equalities != 128L * 127 / 2) throw new Exception("Collision chain not exercised");
            Equal(Deduplication.Hash(new[] { "B", "A", "B" }, comparer), new[] { "B", "A" });
        });
        Check("duplicate counts and first-occurrence order", () => {
            Equal(Deduplication.DuplicateSummary(new[] { "B2", "A1", "B2", "C3", "A1" }),
                new[] { new OrderCount("B2", 2), new OrderCount("A1", 2) });
            Equal(Deduplication.DuplicateSummary(Array.Empty<string>()), Array.Empty<OrderCount>());
            Equal(Deduplication.DuplicateSummary(new[] { "A", "B" }), Array.Empty<OrderCount>());
            Equal(Deduplication.DuplicateSummary(new[] { "A", "A", "A" }), new[] { new OrderCount("A", 3) });
        });
        Console.WriteLine($"{passed} checks passed.");
    }

    private sealed class CountingComparer(bool constantHash = false) : IEqualityComparer<string>
    {
        public long Equalities { get; private set; }
        public bool Equals(string? x, string? y) { Equalities++; return StringComparer.Ordinal.Equals(x, y); }
        public int GetHashCode(string value) => constantHash ? 1 : StringComparer.Ordinal.GetHashCode(value);
    }
}
```

`Benchmarks/Benchmarks.csproj`:

<!-- lab-file: Benchmarks/Benchmarks.csproj -->
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <RuntimeFrameworkVersion>10.0.12</RuntimeFrameworkVersion>
    <RollForward>Disable</RollForward>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <RestorePackagesWithLockFile>true</RestorePackagesWithLockFile>
    <RestoreLockedMode>true</RestoreLockedMode>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="../Core/Core.csproj" />
    <PackageReference Include="BenchmarkDotNet" Version="0.15.8" />
  </ItemGroup>
</Project>
```

`Benchmarks/Program.cs`:

<!-- lab-file: Benchmarks/Program.cs -->
```csharp
using BenchmarkDotNet.Attributes;
using BenchmarkDotNet.Running;
using CostModel;

BenchmarkSwitcher.FromAssembly(typeof(DedupeBenchmarks).Assembly).Run(args);

[MemoryDiagnoser]
public class DedupeBenchmarks
{
    [Params(128, 512, 2048)] public int N { get; set; }
    [Params(10, 100)] public int UniquePercent { get; set; }
    private string[] values = [];

    [GlobalSetup]
    public void Setup() => values = Dataset.Make(N, Math.Max(1, N * UniquePercent / 100));

    [Benchmark(Baseline = true)] public List<string> Scan() => Deduplication.Scan(values);
    [Benchmark] public List<string> Hash() => Deduplication.Hash(values);
}
```

`Benchmarks/packages.lock.json`:

<!-- lab-file: Benchmarks/packages.lock.json -->
```json
{
  "version": 1,
  "dependencies": {
    "net10.0": {
      "BenchmarkDotNet": {
        "type": "Direct",
        "requested": "[0.15.8, )",
        "resolved": "0.15.8",
        "contentHash": "paCfrWxSeHqn3rUZc0spYXVFnHCF0nzRhG0nOLnyTjZYs8spsimBaaNmb3vwqvALKIplbYq/TF393vYiYSnh/Q==",
        "dependencies": {
          "BenchmarkDotNet.Annotations": "0.15.8",
          "CommandLineParser": "2.9.1",
          "Gee.External.Capstone": "2.3.0",
          "Iced": "1.21.0",
          "Microsoft.CodeAnalysis.CSharp": "4.14.0",
          "Microsoft.Diagnostics.Runtime": "3.1.512801",
          "Microsoft.Diagnostics.Tracing.TraceEvent": "3.1.21",
          "Microsoft.DotNet.PlatformAbstractions": "3.1.6",
          "Perfolizer": "[0.6.1]",
          "System.Management": "9.0.5"
        }
      },
      "BenchmarkDotNet.Annotations": {
        "type": "Transitive",
        "resolved": "0.15.8",
        "contentHash": "hfucY0ycAsB0SsoaZcaAp9oq5wlWBJcylvEJb9pmvdYUx6PD6S4mDiYnZWjdjAlLhIpe/xtGCwzORfzAzPqvzA=="
      },
      "CommandLineParser": {
        "type": "Transitive",
        "resolved": "2.9.1",
        "contentHash": "OE0sl1/sQ37bjVsPKKtwQlWDgqaxWgtme3xZz7JssWUzg5JpMIyHgCTY9MVMxOg48fJ1AgGT3tgdH5m/kQ5xhA=="
      },
      "Gee.External.Capstone": {
        "type": "Transitive",
        "resolved": "2.3.0",
        "contentHash": "2ap/rYmjtzCOT8hxrnEW/QeiOt+paD8iRrIcdKX0cxVwWLFa1e+JDBNeECakmccXrSFeBQuu5AV8SNkipFMMMw=="
      },
      "Iced": {
        "type": "Transitive",
        "resolved": "1.21.0",
        "contentHash": "dv5+81Q1TBQvVMSOOOmRcjJmvWcX3BZPZsIq31+RLc5cNft0IHAyNlkdb7ZarOWG913PyBoFDsDXoCIlKmLclg=="
      },
      "Microsoft.CodeAnalysis.Analyzers": {
        "type": "Transitive",
        "resolved": "3.11.0",
        "contentHash": "v/EW3UE8/lbEYHoC2Qq7AR/DnmvpgdtAMndfQNmpuIMx/Mto8L5JnuCfdBYtgvalQOtfNCnxFejxuRrryvUTsg=="
      },
      "Microsoft.CodeAnalysis.Common": {
        "type": "Transitive",
        "resolved": "4.14.0",
        "contentHash": "PC3tuwZYnC+idaPuoC/AZpEdwrtX7qFpmnrfQkgobGIWiYmGi5MCRtl5mx6QrfMGQpK78X2lfIEoZDLg/qnuHg==",
        "dependencies": {
          "Microsoft.CodeAnalysis.Analyzers": "3.11.0"
        }
      },
      "Microsoft.CodeAnalysis.CSharp": {
        "type": "Transitive",
        "resolved": "4.14.0",
        "contentHash": "568a6wcTivauIhbeWcCwfWwIn7UV7MeHEBvFB2uzGIpM2OhJ4eM/FZ8KS0yhPoNxnSpjGzz7x7CIjTxhslojQA==",
        "dependencies": {
          "Microsoft.CodeAnalysis.Analyzers": "3.11.0",
          "Microsoft.CodeAnalysis.Common": "[4.14.0]"
        }
      },
      "Microsoft.Diagnostics.NETCore.Client": {
        "type": "Transitive",
        "resolved": "0.2.510501",
        "contentHash": "juoqJYMDs+lRrrZyOkXXMImJHneCF23cuvO4waFRd2Ds7j+ZuGIPbJm0Y/zz34BdeaGiiwGWraMUlln05W1PCQ==",
        "dependencies": {
          "Microsoft.Extensions.Logging": "6.0.0"
        }
      },
      "Microsoft.Diagnostics.Runtime": {
        "type": "Transitive",
        "resolved": "3.1.512801",
        "contentHash": "0lMUDr2oxNZa28D6NH5BuSQEe5T9tZziIkvkD44YkkCGQXPJqvFjLq5ZQq1hYLl3RjQJrY+hR0jFgap+EWPDTw==",
        "dependencies": {
          "Microsoft.Diagnostics.NETCore.Client": "0.2.410101"
        }
      },
      "Microsoft.Diagnostics.Tracing.TraceEvent": {
        "type": "Transitive",
        "resolved": "3.1.21",
        "contentHash": "/OrJFKaojSR6TkUKtwh8/qA9XWNtxLrXMqvEb89dBSKCWjaGVTbKMYodIUgF5deCEtmd6GXuRerciXGl5bhZ7Q==",
        "dependencies": {
          "Microsoft.Diagnostics.NETCore.Client": "0.2.510501",
          "System.Reflection.TypeExtensions": "4.7.0"
        }
      },
      "Microsoft.DotNet.PlatformAbstractions": {
        "type": "Transitive",
        "resolved": "3.1.6",
        "contentHash": "jek4XYaQ/PGUwDKKhwR8K47Uh1189PFzMeLqO83mXrXQVIpARZCcfuDedH50YDTepBkfijCZN5U/vZi++erxtg=="
      },
      "Microsoft.Extensions.DependencyInjection": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "k6PWQMuoBDGGHOQTtyois2u4AwyVcIwL2LaSLlTZQm2CYcJ1pxbt6jfAnpWmzENA/wfrYRI/X9DTLoUkE4AsLw==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "6.0.0"
        }
      },
      "Microsoft.Extensions.DependencyInjection.Abstractions": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "xlzi2IYREJH3/m6+lUrQlujzX8wDitm4QGnUu6kUXTQAWPuZY8i+ticFJbzfqaetLA6KR/rO6Ew/HuYD+bxifg=="
      },
      "Microsoft.Extensions.Logging": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "eIbyj40QDg1NDz0HBW0S5f3wrLVnKWnDJ/JtZ+yJDFnDj90VoPuoPmFkeaXrtu+0cKm5GRAwoDf+dBWXK0TUdg==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection": "6.0.0",
          "Microsoft.Extensions.DependencyInjection.Abstractions": "6.0.0",
          "Microsoft.Extensions.Logging.Abstractions": "6.0.0",
          "Microsoft.Extensions.Options": "6.0.0"
        }
      },
      "Microsoft.Extensions.Logging.Abstractions": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "/HggWBbTwy8TgebGSX5DBZ24ndhzi93sHUBDvP1IxbZD7FDokYzdAr6+vbWGjw2XAfR2EJ1sfKUotpjHnFWPxA=="
      },
      "Microsoft.Extensions.Options": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "dzXN0+V1AyjOe2xcJ86Qbo233KHuLEY0njf/P2Kw8SfJU+d45HNS2ctJdnEnrWbM9Ye2eFgaC5Mj9otRMU6IsQ==",
        "dependencies": {
          "Microsoft.Extensions.DependencyInjection.Abstractions": "6.0.0",
          "Microsoft.Extensions.Primitives": "6.0.0"
        }
      },
      "Microsoft.Extensions.Primitives": {
        "type": "Transitive",
        "resolved": "6.0.0",
        "contentHash": "9+PnzmQFfEFNR9J2aDTfJGGupShHjOuGw4VUv+JB044biSHrnmCIMD+mJHmb2H7YryrfBEXDurxQ47gJZdCKNQ=="
      },
      "Perfolizer": {
        "type": "Transitive",
        "resolved": "0.6.1",
        "contentHash": "CR1QmWg4XYBd1Pb7WseP+sDmV8nGPwvmowKynExTqr3OuckIGVMhvmN4LC5PGzfXqDlR295+hz/T7syA1CxEqA==",
        "dependencies": {
          "Pragmastat": "3.2.4"
        }
      },
      "Pragmastat": {
        "type": "Transitive",
        "resolved": "3.2.4",
        "contentHash": "I5qFifWw/gaTQT52MhzjZpkm/JPlfjSeO/DTZJjO7+hTKI+0aGRgOgZ3NN6D96dDuuqbIAZSeA5RimtHjqrA2A=="
      },
      "System.CodeDom": {
        "type": "Transitive",
        "resolved": "9.0.5",
        "contentHash": "cuzLM2MWutf9ZBEMPYYfd0DXwYdvntp7VCT6a/wvbKCa2ZuvGmW74xi+YBa2mrfEieAXqM4TNKlMmSnfAfpUoQ=="
      },
      "System.Management": {
        "type": "Transitive",
        "resolved": "9.0.5",
        "contentHash": "n6o9PZm9p25+zAzC3/48K0oHnaPKTInRrxqFq1fi/5TPbMLjuoCm/h//mS3cUmSy+9AO1Z+qsC/Ilt/ZFatv5Q==",
        "dependencies": {
          "System.CodeDom": "9.0.5"
        }
      },
      "System.Reflection.TypeExtensions": {
        "type": "Transitive",
        "resolved": "4.7.0",
        "contentHash": "VybpaOQQhqE6siHppMktjfGBw1GCwvCqiufqmP8F1nj7fTUNtW35LOEt3UZTEsECfo+ELAl/9o9nJx3U91i7vA=="
      },
      "core": {
        "type": "Project"
      }
    }
  }
}
```

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
```

Expected demo output:

```text
Stable result: B2, A1, C3
Example scan comparisons: 6
n,scan_equality_comparisons,hash_add_calls (not hash-table work)
128,8128,128
256,32640,256
512,130816,512
128 identical IDs: 127 scan comparisons
Duplicates: B2=2, A1=2
```

The check command reports `8 checks passed`. The scan/reference cases cover order, identity, empty input, null rejection and duplicate counts, not arbitrary comparer laws or production delivery.

</details>

Steps:

1. **Build it yourself (20 minutes).** Close the example, rewrite the method and explain the prefix invariant from section 5. If stuck, look at the full method above.
2. **Predict edge cases (15 minutes).** Write your expected result before tracing or running:

   | Input | Question |
   |---|---|
   | `[]` | What is returned? |
   | `a,A,a` | Are `a` and `A` merged? |
   | `A,A,A` | How many items remain? |
   | `"",B2,""` | Is the empty string valid? |
   | input is null | Which exception? |
   | one ID is null | Which exception? |

<details>
<summary>Expected results</summary>

| Input | Expected result |
|---|---|
| `[]` | `[]` |
| `a,A,a` | `a,A` |
| `A,A,A` | `A` |
| `"",B2,""` | `"",B2` |
| input is null | `ArgumentNullException` |
| one ID is null | `ArgumentException` |

</details>

3. **Test and debug (15 minutes).** Compare output with your expectations and check that the input did not change. When something differs, trace the smallest failing batch instead of rewriting the method.
4. **Break one rule on purpose (10 minutes).** Append every ID, sort the result, or use `OrdinalIgnoreCase`. Appending everything keeps duplicates; sorting breaks first-occurrence order; a case-insensitive comparer merges `a` and `A`. Restore the contract before you measure.
5. **Collision survey (10 minutes).** Suppose a comparer returns hash 1 for every ID but still uses ordinal equality. Results stay correct, but a new ID may be compared with every entry in the bucket. With 128 distinct IDs, a chained implementation does `128×127/2 = 8,128` equality checks. Equal keys must have equal hashes, and hash and equality must stay stable while the key is stored.
6. **Wrap up (5 minutes).** Explain one bug you avoided and one assumption the implementation needs.

**Debug hints:** duplicates remain -> append only when `Add` returns true; order changed -> keep a separate output list; `a` and `A` merged -> check the comparer; hashing is unexpectedly slow -> look for a hidden `List.Contains`; null behavior changed -> keep the explicit checks.




**Break · 10 minutes.** Leave the screen.

## 9. Controlled experiment

**About 45 minutes - Measure one change:** choose a factor, state a hypothesis, measure and compare with the prediction. **Stop when:** you have one evidence-supported decision and one thing you cannot conclude.

**Fair comparison.** Measure scan and hash on the same input, with the same equality and the same ordering contract. Build the input before the measured part, and make each measured call create a new result. Otherwise one path may reuse warm state or skip allocation while the other still allocates.

The downloadable lab uses BenchmarkDotNet 0.15.8, N = 128, 512, 2048, nominal distinct ratios 10% and 100%, and fixed-length IDs. For N = 128 and 10%, the real distinct count is `floor(128×0.10) = 12`. Predict before running: fewer distinct IDs make the List scan shorter; hash tables usually allocate more. Big-O does not give a speed ratio.

Run in Release, without a debugger. Read `Mean`, `Error` and `Allocated` together. `Error` is half the width of BenchmarkDotNet’s 99.9% confidence interval, not a guaranteed error bound. `Allocated` includes memory for new output and table storage, but not the prebuilt input; it does not measure peak working set or live heap.

This benchmark measures batch execution time, not service request latency. If p99 latency is 100 ms, about 99% of measured requests finish within 100 ms; average batch time does not establish that quantity.

From the lab's `dotnet` directory, run:

```bash
dotnet run -c Release --project Benchmarks -- --filter '*DedupeBenchmarks*' --job short
```

This optional project needs a NuGet restore and runs 12 workload cases. Inspect the reports in `BenchmarkDotNet.Artifacts/results`; if setup exceeds your timebox, use the sample report below instead.

Interpret this recorded ShortRun: what do its interval and allocation support, and what remains uncertain?

<details>
<summary>Answer - recorded benchmark</summary>

Sample ShortRun from 5 October 2026, n = 512, all IDs distinct:

| Approach | Mean | Error | Allocated per operation |
|---|---:|---:|---:|
| Scan | 922.355 µs | 2,261.779 µs | 8,384 B |
| Hash | 22.218 µs | 19.147 µs | 42,896 B |

The run used Debian 13, Intel Xeon Platinum 8573C, .NET 10.0.12, three warmup and three measurement iterations per case. The intervals are very wide, so the times only illustrate; they are not a trustworthy service speedup. The extra bytes show the trade-off, not whole-application memory. The [full report](benchmark-report.md) has the workload matrix.

</details>

### Your experiment notebook

Change one factor (n, distinct ratio, key length or initial capacity) and keep the output contract. Check correctness before timing. Do not benchmark a method with a comparison counter against one without: the counter changes the work.

| Write before you run | Write after you run |
|---|---|
| Input size, real u, key length and distribution | Real parameters and environment |
| Prediction and the mechanism behind it | Mean, interval, allocation |
| The one factor you will change | Did the prediction hold? |
| Expected correctness result | Any failure or surprise |
| What would make you unable to conclude? | Decision supported and remaining limits |

If you do not run the benchmark, use the sample report to practice interpretation and leave your own results blank. If results are missing or too noisy, conclude "not enough measurements to claim a speedup". Check input creation, comparer, build mode and interval before inventing a reason for a surprising ratio. The Dry harness only checks that the code runs; it is not a performance measurement.

**Break · 10 minutes.** Leave the screen.

## 10. Changed requirement: duplicate report

**About 35 minutes - Solve a changed requirement:** design the solution, compare it with the answer and work through the table. **Stop when:** you have traced or run the four inputs.

Support needs a count instead of unique IDs. For `B2,A1,B2,C3,A1` return `[(B2,2),(A1,2)]` and drop IDs that appear once. Keep ordinal identity, first-occurrence order, unchanged input and the same null policy.

Design your method and predict the output for these inputs before opening the answer. Check empty input and null rejection too.

| Input to test | What to check |
|---|---|
| `A,B,B,A,C` | Counts and first-occurrence order |
| `a,A,a` | Ordinal equality |
| `X,Y` | IDs that occur only once |
| `A,A,A` | Every occurrence contributes to the count |

<details>
<summary>Answer</summary>

Use a count lookup and a separate list to keep order. Every occurrence increments a count; only the first occurrence adds the ID to the list.

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

The invariant has two parts: `counts` equals the number of occurrences in the prefix read so far, and `order` holds each seen ID once in first-occurrence order. The final pass over `order` keeps counts above one. Expected O(n+u) = O(n), with O(u) extra storage under the same hashing and key assumptions. Do not rely on `Dictionary` enumeration order.

| Input | Result |
|---|---|
| `A,B,B,A,C` | `[(A,2),(B,2)]` |
| `a,A,a` | `[(a,2)]` |
| `[]` or `X,Y` | `[]` |
| `A,A,A` | `[(A,3)]` |

Sorting by count would change the report order. Incrementing only new IDs would fail on `A,A,A`. Trace of `A,B,B,A,C`: `order` stays `A,B,C`, counts become A=2, B=2, C=1, and the last pass returns A then B.

</details>

### Production: batch dedupe is not idempotency

Idempotency means retrying the same event does not apply its business effect again. Two service instances can both receive B2, because each has its own set. A batch `HashSet` does not prevent the other instance from applying the event. Use a key the database enforces as unique, for example tenant + event ID, and **store the processed-event marker and the business update in one transaction**. The transaction must commit both writes or roll back both.

```sql
-- Illustrative example; not executed against SQL Server.
CREATE UNIQUE INDEX UX_OrderEvents_Tenant_Event
    ON dbo.OrderEvents (TenantId, EventId);

-- A duplicate (TenantId, EventId) fails with error 2601
-- (or 2627 for a unique constraint). This only proves the key exists.
```

A consumer starts a transaction, inserts the event marker into `OrderEvents`, updates the order, then commits. It acknowledges the message only after commit. If it fails before commit, both writes roll back and a retry can process the event. If it commits but fails before acknowledging, the retry finds the marker and does not apply the update twice.

On a duplicate-key error, roll back the failed attempt and confirm the conflict is on **this event key**, rather than an unrelated unique index. Only when the marker and business update follow the atomic transaction rule does that marker mean "already processed". Other database errors still need handling or retry. A marker committed alone can survive a crash before the order update and make a later retry skip unfinished work; the [Idempotent Consumer pattern](https://learn.microsoft.com/azure/architecture/patterns/idempotent-consumer) explains why these writes must be atomic.

A plain `SELECT` before `INSERT` still has a race condition: two instances can both see "not found" before either inserts. Storage equality must also match the identity you want: SQL Server collation can treat strings differently from C# Ordinal.

The same size trade-off shows up in Azure. [Service Bus duplicate detection](https://learn.microsoft.com/azure/service-bus-messaging/duplicate-detection) remembers `MessageId` values for a configurable time window and drops a repeated send. The docs say a bigger window affects throughput because every recorded ID must be matched, so keep the window as small as you can. That is your `seen` set again, with a time limit to bound memory. It protects against duplicate sends, but the [Idempotent Consumer pattern](https://learn.microsoft.com/azure/architecture/patterns/idempotent-consumer#problems-and-considerations) warns it does not replace idempotent processing in the consumer. If a side effect lives outside your database transaction, a unique key alone does not make it exactly-once.

On the Angular side, the same idea in TypeScript:

```typescript
// Set keeps insertion order, so the first occurrence wins. Strings compare case-sensitively.
const unique = [...new Set(orderIds)];
```

## 11. Synthesis and review

**About 45 minutes - Explain and review:** state the decision aloud or in writing without notes, then check it. **Stop when:** you have one decision statement and one unresolved question.

Close the examples and explain:

1. Why can one `foreach` be Θ(n²)?

<details>
<summary>Answer</summary>

The body searches a list that keeps growing, so the total is `0+1+...+(n-1)` when the input is all distinct.

</details>

2. Why do you need both a `HashSet` and a `List`?

<details>
<summary>Answer</summary>

Membership and output order are two jobs. The hash table costs extra storage.

</details>

3. Is hashing always faster?

<details>
<summary>Answer</summary>

No. Small batches, low u, key cost, allocation and cache behavior all matter.

</details>

4. For `A,B,A,B`, how many comparisons does a scan make?

<details>
<summary>Answer</summary>

`0+1+1+2 = 4`, compared with six for four distinct IDs.

</details>

A good final explanation names the contract, the expected workload, the chosen structure, the argument for it and one limit. Example: "For many distinct IDs of bounded length I use a HashSet plus a List. The invariant keeps first-occurrence order, and the scan count grows quadratically. Hashing is expected linear under suitable assumptions and costs more storage. The sample benchmark shows the trade-off but its timing uncertainty is large. I need real key distribution and memory numbers before promising production latency."

Review yourself on four points: edge cases and the invariant; assumptions about n, u and key cost; fair measurement and its limits; whether the duplicate-count variant keeps order. If an explanation is unclear, go back to a small counterexample and try a new ID. After some time, rebuild the counts or the variant without notes. If you get it wrong, review sooner; if recall is easy, wait longer. The 1/3/7-day schedule is a starting point you can adjust.

Questions to carry forward: what changes with long identifiers? How much memory can a batch use? How should tenant-scoped identity match storage equality? Pick one; do not expand today's goal forever.

## Read further

- [Microsoft: List.Contains](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.contains?view=net-10.0) and [HashSet.Add](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.hashset-1.add?view=net-10.0): equality check, return value and resize.
- [EF Core: Efficient querying](https://learn.microsoft.com/ef/core/performance/efficient-querying#tracking,-no-tracking-and-identity-resolution) and [Identity resolution](https://learn.microsoft.com/ef/core/change-tracking/identity-resolution): the change tracker as a dictionary.
- [Azure Service Bus duplicate detection](https://learn.microsoft.com/azure/service-bus-messaging/duplicate-detection): a time-bounded seen set at message level.
- [SQL Server unique indexes](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/create-unique-indexes?view=sql-server-ver17): uniqueness enforced by storage.
- [C# lab guide](../../labs/cost-model/dotnet/README.md): setup, benchmark commands and optional troubleshooting.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Topic map](../../references/topic-map.md) - Choose the foundations or deeper topic to study next.
- [C# lab guide](../../labs/cost-model/dotnet/README.md) - SDK setup, copyable commands and benchmark troubleshooting.

---

[All lessons](../../README.md) · [Next: Lesson 02 - Boundary search with binary search and time-window counts →](../boundary-search/lesson.md)
<!-- LESSON_NAVIGATION_END -->
