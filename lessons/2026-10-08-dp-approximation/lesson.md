# Lesson 04 - Dynamic programming and approximation: selecting jobs within a budget

[Tiếng Việt](../../vi/lessons/2026-10-08-dp-approximation/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/budget-selection/dotnet-lab.zip)

Lesson 03 showed why a promising route is not automatically optimal. Now an ASP.NET worker has a fixed processing budget and must choose whole jobs. Taking the best-looking job first can block a better combination. We will retain enough state to find the optimum, then derive a cheaper choice with a precise quality guarantee.

**Goal:** define a 0/1 budget-selection state, derive and prove its dynamic-programming recurrence, reconstruct the selected jobs and compare it with greedy selection. Prove why a modified greedy method returns at least half the optimum under explicit assumptions. The roadmap selects dynamic programming and approximation after graphs. You need arrays, loops, Big-O and the invariant/state ideas from Lessons 01-03; the recurrence and approximation proof are developed here.

## Core ideas

- **0/1 budget selection.** Each job is taken once or omitted; costs add and must fit the budget. With budget 6, a cost-4 job may prevent selecting two cost-3 jobs whose combined value is higher.
- **State and dynamic programming (DP).** Summarize what future decisions need, solve smaller states and reuse their answers. “First two jobs, budget 3” is a different state from “first three jobs, budget 3”, because a different job is still available.
- **Greedy choice.** Commit to a local rule instead of keeping alternatives. The largest value per cost may look attractive, but indivisible jobs leave gaps that later choices cannot repair.
- **Approximation guarantee.** Accept a feasible answer with a proved bound on its value. “At least half the optimum” means an optimum of 100 implies value at least 50 on every valid instance, not just the examples tested.

Each section has worked answers. You may use the reading-only route through the table, proofs and complete code. Limit setup to 15 minutes of the lab section; if the SDK is unavailable, continue with those explanations. No submission or saved learner record is needed.

## 1. Recall and foundation bridge

**Recall · 20 minutes.** Reconstruct the two selected mechanisms from earlier lessons and check the 0/1 constraint. **Done when:** you can distinguish a proved greedy choice from an attractive rule and state what must remain unique.

1. From Lesson 03: why may Dijkstra stop at a current minimum removal but not at first discovery of the target?

<details>
<summary>Answer</summary>

Discovery proves only that a route exists: a direct cost-10 edge can be improved by three cost-1 edges. For a current minimum label, a cheaper route would have an unfinished prefix with a smaller label; nonnegative remaining edges give the contradiction. Skip stale entries before stopping. That proof authorizes Dijkstra's choice. Today, a value/cost ordering needs its own argument; it cannot borrow the shortest-path proof.

</details>

2. From Lesson 01: how do HashSet and List preserve first-occurrence order, and how should key equality be chosen?

<details>
<summary>Answer</summary>

Read input in order and append to the list only when `HashSet.Add` returns true. The set checks membership; the list retains output order. Use a comparer matching the required equality. Changing case sensitivity changes the result. The lab uses unique job IDs with ordinal equality, so two distinct IDs may have the same cost/value and remain separate jobs. Reject a repeated ID instead of silently counting the same job twice.

</details>

3. A job costs 2 and has value 3; the budget is 4. What is the 0/1 optimum? What changes if unlimited copies are allowed?

<details>
<summary>Answer</summary>

The 0/1 optimum is 3: the one job may be selected only once. Unlimited copies give 6 from two copies. If the distinction feels unclear, list the valid subsets: empty or the single job. The foundation bridge is to label every decision by the item index as well as the remaining budget. Capacity alone cannot tell whether that job is still available.

</details>

## 2. Build the state, recurrence and proof

**Foundation · 50 minutes.** Complete the small DP table, reconstruct the selected jobs and explain the invariant. **Done when:** you can justify both branches and find the repeated-item bug in a compressed table.

### A concrete counterexample

Budget 6, with three indivisible jobs in input order:

| Job | Cost | Value | Value/cost |
|---|---|---|---|
| A | 4 | 7 | 1.75 |
| B | 3 | 5 | about 1.67 |
| C | 3 | 5 | about 1.67 |

Predict density-greedy's selection and the true optimum. Are B and C duplicates merely because their numbers match?

<details>
<summary>Answer</summary>

Density-greedy chooses A first, leaving 2 units. Neither B nor C fits, so its value is 7. Choosing B and C uses all 6 units and gives 10. They have different IDs and can both be selected. A repeated ID would violate the lab contract, but equal numeric fields do not.

</details>

### Define exactly what one cell means

Let `F(i,c)` be the maximum value obtainable using only the first i jobs, with total cost **at most** c. It does not mean “exactly c”. Empty selection is legal, so `F(0,c)=0`; positive costs give `F(i,0)=0`.

For job i with cost w and value v:

- If `w > c`, `F(i,c) = F(i-1,c)`.
- Otherwise, `F(i,c) = max(F(i-1,c), F(i-1,c-w)+v)`.

The first branch omits this job. The second takes it once and asks the previous row to fill the remaining budget. Both read row i-1, so that row cannot already contain job i. This recurrence is the rule used to compute a larger state from smaller states.

The contract is a fixed list of jobs with unique nonempty IDs, positive integer costs and nonnegative integer values. Costs and capacity use `int`, values use `long`. No job splitting, dependency, synergy or multiple resource constraint is included. Inputs must stay fixed during a call. Reject negative capacity, invalid IDs/costs/values and a sum of **all** job values above `long.MaxValue`, including overweight jobs. This conservative check makes every subset sum safe; `long.MaxValue` itself is a valid value here. Exact DP also limits its allocation to 2,000,000 cells, and the exhaustive oracle to 22 jobs. These are lab limits, not mathematical limits.

### Table and traceback

| Jobs considered | c=0 | c=1 | c=2 | c=3 | c=4 | c=5 | c=6 |
|---|---|---|---|---|---|---|---|
| None | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| A | 0 | 0 | 0 | 0 | 7 | 7 | 7 |
| A,B | 0 | 0 | 0 | 5 | 7 | 7 | 7 |
| A,B,C | 0 | 0 | 0 | 5 | 7 | 7 | 10 |

For `F(2,6)`, taking B gives `F(1,3)+5 = 5`, while omitting B keeps 7. For `F(3,6)`, taking C gives `F(2,3)+5 = 10`, which improves 7. To reconstruct a solution, start at `(3,6)`. When its value differs from the previous row at the same capacity, take that job and subtract its cost. Otherwise omit it. Ties omit the later job; the contract promises an optimal value and one valid subset, not a unique subset or a secondary cost objective.

Exercise: trace back to job IDs from `(3,6)`, then do the same from `(3,5)`. Why is initializing every cell to zero correct for “at most” but wrong for “exactly” capacity?

<details>
<summary>Answer</summary>

At `(3,6)`, 10 differs from `F(2,6)=7`: take C and move to `(2,3)`. That value 5 differs from `F(1,3)=0`: take B and move to `(1,0)`. A is omitted. Return B,C with cost 6 and value 10. At `(3,5)`, 7 equals `F(2,5)` and `F(1,5)`; omit C and B, then take A with cost 4 and value 7.

“At most” permits spending zero at any capacity, so zero is a feasible baseline. For “exactly”, a positive capacity may be unreachable; zero would falsely label it feasible. Use an unreachable marker, seed only the zero-cost state and never add a value to an unreachable state. The lab implements only “at most”.

</details>

### Why the recurrence is correct

The invariant is: after row i is filled, every cell equals the optimum for the first i jobs and its budget. Base row 0 is correct because only the empty subset exists. Suppose row i-1 is correct. Any feasible subset in row i either omits job i, so it is bounded by `F(i-1,c)`, or takes it, so the other jobs fit c-w and are bounded by `F(i-1,c-w)+v`. Thus no feasible subset beats the maximum of the two branches. Conversely, each branch constructs a feasible subset from a previous-row optimum, so the maximum is attainable. This proves both the bound and existence by induction. Traceback follows exactly those choices.

Boundary search used an interval invariant to justify discarding a region. Here the invariant must describe optimal values for a whole item prefix; discarding a job just because its ratio is lower needs a new proof. BFS used layer order for unit edge costs, while Dijkstra used minimum labels for nonnegative costs. DP instead follows an order in which every dependency is already solved.

This reuses Lesson 03's state idea. The transitions go from one item layer to the next, forming a directed acyclic graph. Layer order makes dependencies final before use, so a priority queue is unnecessary. Turning rewards into negative costs would violate the earlier Dijkstra contract; acyclicity, rather than nonnegative cost, is what makes this dependency order safe.

### Work and the compressed-table trap

With n jobs and integer capacity C, the fill visits n(C+1) cells, plus the zero initialization of (n+1)(C+1) stored cells. Time is O((n+1)(C+1)) and traceback O(n); storage is O((n+1)(C+1)). For positive n,C this is usually written O(nC). A 2,000,000-cell `long` table has 16 MB of value storage before array overhead and result objects. Complexity counts bounded integer operations, not database calls.

If only the optimum value is needed, use one row and update capacities **downward**. Before processing job i, the array means row i-1. At c, lower index c-w has not yet been overwritten, so the take branch still uses the previous row. An upward loop would reuse the same job: cost 2/value 3 with budget 4 would write 3 at c=2 and then read it to write 6 at c=4. The lab includes both the full traceback table and the downward value-only variant.

Pause - 10 minutes away from the screen.

## 3. Read sources and derive a quality bound

**Source reading · 45 minutes.** Read the bounded sections, reconstruct the half-value argument and write three claim/evidence/limit rows. **Done when:** you can prove the guarantee without treating a successful experiment as proof.

Read Williamson and Shmoys, [The Design of Approximation Algorithms, Section 3.1, printed pages 65-67, and Exercise 3.1 on page 77](https://www.designofapproxalgs.com/book.pdf#page=65). The section explains exact knapsack DP using non-dominated cost/value pairs and why numeric capacity affects complexity. Our lab uses a capacity-indexed table rather than copying that representation. For the same item prefix, a cost/value pair (2,5) dominates (3,4): it uses less budget and yields more value, so adding any available suffix cannot make the latter preferable under the additive model. The exercise gives the modified density-greedy idea with a best-single-job safeguard; the derivation below explains why it works. The book assumes positive values; zero-valued jobs in the lab cannot improve a subset and do not change the argument.

### Numeric size is not input length

A budget of 1,000,000 has roughly twice as many bits as 1,000, but a capacity-indexed table needs roughly 1,000 times as many columns. This is **pseudopolynomial**: polynomial in the numeric capacity C, not necessarily polynomial in its binary encoding length. If C uses b bits, it can be nearly `2^b`, so O(nC) can be exponential in b. Compressing to one row saves memory but does not remove the dependence on C. An exact value-indexed or sparse-state design may help under other bounds; it needs its own implementation and analysis.

### From a failed greedy rule to a proved approximation

Discard jobs whose individual cost exceeds C; none can occur in a valid solution. Sort the others by decreasing value/cost. Let G be the value from taking each job that still fits and skipping those that do not. Let B be the largest value of one individually feasible job. Return the better of those two subsets, so `A = max(G,B)`.

To see why G alone has no fixed positive guarantee, use capacity W>2 and two jobs: a tiny job with cost 1/value 2, and a large job with cost W/value W. Greedy takes the tiny job first, then the large one does not fit. Its quality is `2/W`, which tends to zero as W increases. The single-job safeguard returns the large job.

For the proof, allow fractional jobs temporarily: part of a cost-3/value-6 job could cost 1 and earn 2. This **relaxed problem** allows every integral subset, so its optimum U is an upper bound on the 0/1 optimum OPT. Fractional density ordering is optimal: moving a little capacity from a lower-density job to an unfilled higher-density job cannot reduce value. Repeating that exchange gives a full prefix and at most one fractional next job.

Let P be the full prefix before the first job that cannot fit, and let that next job have value t. Then `U <= value(P)+t`. Our skip-and-continue greedy retains that prefix and may add later jobs, so `G >= value(P)`. Because the rejected job fits on its own after filtering, `B >= t`. Therefore:

`OPT <= U <= value(P)+t <= G+B <= 2*max(G,B) = 2*A`.

Hence `A >= OPT/2`. If all eligible jobs fit together, greedy is already optimal. If none fits, OPT and A are both 0. The book's exercise stops at the first rejected job; continuing to add feasible nonnegative-value jobs only strengthens the prefix bound. This explains the lab variant rather than attributing a different algorithm to the source.

Exercise: which assumptions support the bound? Does the theorem promise exact optimality or apply to jobs that depend on each other? Write a short claim ledger.

<details>
<summary>Answer</summary>

| Claim | Evidence | Assumption or limit |
|---|---|---|
| DP retains a best answer for each subproblem | Section 3.1 and the two-case induction in section 2 | The lab's state uses a single additive integer cost and independent 0/1 jobs |
| Capacity-indexed DP is pseudopolynomial | The book compares numeric magnitude with binary encoding length | One-row memory does not make O(nC) polynomial in log C |
| Modified density greedy returns at least OPT/2 | Exercise 3.1's strategy and the fractional-bound derivation above | Costs are positive, values nonnegative and additive, jobs independent and individually feasible after filtering |

The theorem is a worst-case value guarantee, not exact optimality, a latency estimate or an average-case prediction. Dependencies, multiple resources or interaction bonuses change the feasible family or objective, so this proof cannot be carried over without a new argument. An empirical ratio above 1/2 on every tested instance is consistent with the proof, not a substitute for it.

</details>

## 4. Project application and PostgreSQL case study

**Implementation reading · 45 minutes.** Trace one planner level and relate its state design to a .NET batch selector. **Done when:** you can identify retained alternatives and separate estimated cost from measured performance.

### Application: choosing a .NET processing batch

An ASP.NET worker reads eligible export or audit jobs from SQL Server. Each has a stable ID, a positive estimated cost in integer slots and an additive business value. Build a fixed, versioned list and choose a subset within the slot budget. Use exact DP when C and n fit the memory/time budget; use the proved half-value method when a looser value guarantee is acceptable. Return the selected IDs, total estimated cost/value, algorithm and input version so Angular can explain the choice.

If a job appears twice, reject or dedupe it according to an explicit business rule before optimization. Selecting IDs in memory is separate from reserving them: the worker must revalidate and atomically claim the chosen jobs, for example within a database transaction. Another worker may otherwise take the same work. This lesson implements selection, not transaction handling or scheduling fairness.

If estimates are fractional, rounding each cost upward to slots preserves the estimated budget constraint but can exclude useful combinations. Rounding downward can make the original costs exceed the budget. Neither policy guarantees a wall-clock deadline when estimates are wrong. Dependencies and bonuses are also outside the additive independent-job model.

### Read one real optimizer at an immutable commit

PostgreSQL 17.6 uses DP to build alternative join plans. We inspect commit **`7885b94dd81b98bbab9ed878680d156df7bf857f`**, tag `REL_17_6`. It is a product use of subproblem reuse, not an implementation of our knapsack lab. For a query joining Orders, Customers and Regions, deciding the first join changes intermediate data and later costs; greedily choosing a promising pair does not consider all useful alternatives.

1. [`standard_join_search`](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/path/allpaths.c#L3381-L3493) sets level 1 to the initial relations, then processes levels 2 through `levels_needed`. After generating each level's paths, it calls `set_cheapest` for each join relation. The explicit DP comment and loops are the bounded slice to read.
2. [`join_search_one_level`](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/path/joinrels.c#L60-L205) extends smaller joins and considers legal combinations of two smaller groups. A level is a **list of relation sets**, not one “best pair” for that size. Clause and join-order checks limit which candidates are generated.
3. [`make_join_rel`](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/path/joinrels.c#L693-L789) combines relation IDs, checks legality and adds implementation paths to the relation representing that set. The same set may receive paths from different decompositions.
4. [`add_path`'s documented policy](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/util/pathnode.c#L361-L415) retains alternatives based on cost, ordering, parameterization, rows and parallel safety. A cheap path alone is not always enough state for later joins.

Source exercise: for four ordinary inner-join relations A,B,C,D, what lower-level groups can contribute at level 4? Why does retaining only one cheapest path per size lose information?

<details>
<summary>Answer</summary>

Level 4 can extend a three-relation group with one relation or combine two disjoint two-relation groups, when join clauses or restrictions permit those candidates. For example, AB with CD differs from AC with BD; both union to ABCD. At level 2, AB and AC are different states, even if both contain two relations, because their remaining relations and clauses differ. Paths for the same relation set may also differ in useful ordering or parameterization. The code's lists and path policies retain that distinction. This is a mechanism trace, not an assertion that every syntactically possible join tree is enumerated.

</details>

### Workload and trade-off

**Verified:** the source grows join-relation levels bottom up, adds paths from alternatives and uses explicit path-retention criteria. The choice between `standard_join_search` and GEQO is visible [just above it](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/src/backend/optimizer/path/allpaths.c#L3361-L3378). PostgreSQL's [version 17 configuration documentation](https://www.postgresql.org/docs/17/runtime-config-query.html#RUNTIME-CONFIG-QUERY-GEQO) says `geqo_threshold` defaults to 12 FROM items and explains the planning-time/suboptimal-plan trade-off; FULL OUTER JOIN grouping and other settings affect that count. This is a documented workload threshold, not a node-count or latency measurement.

**Design inference:** replacing these alternatives with one greedy pair per level could discard a useful future plan. We infer that from the state differences and code; we do not claim the maintainers ran our knapsack experiment. Their optimizer controls search growth with legality checks, path pruning and an alternative search strategy. Unlike our simple DP table, planner costs are estimates and retained paths have additional properties. There is no 1/2 knapsack guarantee for GEQO implied by this reading.

In your batch service, first ask what information affects later feasibility or value. A dependency group or a second resource cannot be safely hidden inside one scalar label. We have read source, not executed PostgreSQL query plans or reproduced its performance. We also do not assert that SQL Server implements the same planner; it is the project's data source in the application example.

Lunch and rest - 30 minutes.

## 5. C# lab: build, check and repair

**Lab · 75 minutes.** Implement the state recurrence and two greedy methods, run correctness checks and repair the compressed-table defect. **Done when:** the command passes and you can explain why a job cannot be selected twice.

Implement `Exact`, `DensityGreedy` and `HalfApprox` under section 2's contract. Return value, cost and original item indices, with each index at most once. Use an independent exhaustive solver for small inputs. The complete runnable answer is below, including setup and all five source files.

<details>
<summary>Answer - complete runnable lab</summary>

Use **.NET SDK 10.0.401**, target **net10.0**, without external packages. Extract the ZIP and work inside its `dotnet` directory. From a checkout, use `labs/budget-selection/dotnet`. Alternatively create the project with the files below; no source download is required. The [lab guide](../../labs/budget-selection/dotnet/README.md) supplies optional individual downloads.

`dotnet/global.json`:

<!-- lab-file: global.json -->
```json
{
  "sdk": { "version": "10.0.401", "rollForward": "disable" }
}
```

`dotnet/LessonLab/LessonLab.csproj`:

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
</Project>
```

Run from the `dotnet` directory:

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --experiment
```

The demo is expected to print:

```text
Exact: value=10, cost=6, ids=B,C
Density: value=7, cost=4, ids=A
HalfApprox: value=7, cost=4, ids=A
```

Install the matching SDK from Microsoft if needed. Once built, `dotnet run --no-restore -c Release --project LessonLab -- --check` runs offline with no third-party restore. If the SDK cannot be installed, use the table and code-reading route. No SQL Server or PostgreSQL instance is needed.

`LessonLab/Budget.cs`: `Validate` rejects repeated IDs rather than silently deduping. `Exact` reads only the previous row and reconstructs on strict improvement. `ExactValueRolling` returns only the value. The density comparator uses integer cross-products with `BigInteger` to avoid rounded ratios and `long` multiplication overflow; values/costs have fixed 64/32-bit bounds here. Equal densities use the original index as a tie-break. These methods do not mutate the input.

<!-- lab-file: LessonLab/Budget.cs -->
```csharp
// Original MIT teaching code. No PostgreSQL or textbook code is copied.
using System.Numerics;

public readonly record struct Job(string Id, int Cost, long Value);
public sealed record Choice(long Value, int Cost, int[] Indices, long Work, long RatioComparisons = 0);

public static class Budget
{
    public const long MaxCells = 2_000_000;

    public static void Validate(Job[] jobs, int capacity)
    {
        ArgumentNullException.ThrowIfNull(jobs);
        if (capacity < 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        var ids = new HashSet<string>(StringComparer.Ordinal);
        long total = 0;
        foreach (var job in jobs)
        {
            if (string.IsNullOrWhiteSpace(job.Id) || !ids.Add(job.Id))
                throw new ArgumentException("IDs must be nonempty and unique (ordinal).", nameof(jobs));
            if (job.Cost <= 0 || job.Value < 0)
                throw new ArgumentException("Costs must be positive; values nonnegative.", nameof(jobs));
            total = checked(total + job.Value);
        }
    }

    public static Choice Exact(Job[] jobs, int capacity)
    {
        Validate(jobs, capacity);
        long cells = (jobs.Length + 1L) * (capacity + 1L);
        if (cells > MaxCells)
            throw new ArgumentOutOfRangeException(nameof(capacity), "DP table exceeds the lab cell limit.");
        var best = new long[jobs.Length + 1, capacity + 1];
        long work = 0;
        for (int i = 1; i <= jobs.Length; i++)
        {
            Job job = jobs[i - 1];
            for (int c = 0; c <= capacity; c++)
            {
                work++;
                best[i, c] = best[i - 1, c];
                if (job.Cost <= c)
                    best[i, c] = Math.Max(best[i, c], checked(best[i - 1, c - job.Cost] + job.Value));
            }
        }
        var selected = new List<int>();
        int remaining = capacity;
        for (int i = jobs.Length; i > 0; i--)
        {
            if (best[i, remaining] == best[i - 1, remaining]) continue;
            selected.Add(i - 1);
            remaining -= jobs[i - 1].Cost;
        }
        selected.Reverse();
        return new Choice(best[jobs.Length, capacity], capacity - remaining, selected.ToArray(), work);
    }

    public static long ExactValueRolling(Job[] jobs, int capacity)
    {
        Validate(jobs, capacity);
        if (capacity + 1L > MaxCells)
            throw new ArgumentOutOfRangeException(nameof(capacity), "Rolling array exceeds the lab cell limit.");
        var best = new long[capacity + 1];
        foreach (var job in jobs)
            for (int c = capacity; c >= job.Cost; c--)
                best[c] = Math.Max(best[c], checked(best[c - job.Cost] + job.Value));
        return best[capacity];
    }

    public static Choice DensityGreedy(Job[] jobs, int capacity) => Density(jobs, capacity, false);
    public static Choice HalfApprox(Job[] jobs, int capacity) => Density(jobs, capacity, true);

    private static Choice Density(Job[] jobs, int capacity, bool protectSingle)
    {
        Validate(jobs, capacity);
        var order = Enumerable.Range(0, jobs.Length).Where(i => jobs[i].Cost <= capacity).ToList();
        long comparisons = 0;
        order.Sort((a, b) =>
        {
            comparisons++;
            // Descending value/cost without floating-point rounding or long overflow.
            int comparison = ((BigInteger)jobs[b].Value * jobs[a].Cost)
                .CompareTo((BigInteger)jobs[a].Value * jobs[b].Cost);
            return comparison != 0 ? comparison : a.CompareTo(b);
        });
        var selected = new List<int>();
        int used = 0, bestSingle = -1;
        long value = 0, work = 0;
        foreach (int index in order)
        {
            work++;
            if (bestSingle < 0 || jobs[index].Value > jobs[bestSingle].Value) bestSingle = index;
            if (jobs[index].Cost > capacity - used) continue;
            selected.Add(index);
            used += jobs[index].Cost;
            value = checked(value + jobs[index].Value);
        }
        if (protectSingle && bestSingle >= 0 && jobs[bestSingle].Value > value)
            return new Choice(jobs[bestSingle].Value, jobs[bestSingle].Cost, [bestSingle], work, comparisons);
        selected.Sort();
        return new Choice(value, used, selected.ToArray(), work, comparisons);
    }
}
```

`LessonLab/Oracle.cs`: examine every subset. It shares input validation, but uses neither the DP recurrence nor ratio ordering, making it an independent reference for optimization on the accepted domain. For n>=1, time is O(n·2^n) and extra search memory O(n). The 22-job guard keeps an accidentally huge reference run bounded.

<!-- lab-file: LessonLab/Oracle.cs -->
```csharp
// Exhaustive independent reference for small instances, original MIT code.
public static class Oracle
{
    public static Choice Solve(Job[] jobs, int capacity)
    {
        Budget.Validate(jobs, capacity);
        if (jobs.Length > 22) throw new ArgumentOutOfRangeException(nameof(jobs), "Oracle limit is 22 jobs.");
        long best = 0, work = 0;
        int bestMask = 0, bestCost = 0;
        for (int mask = 0; mask < (1 << jobs.Length); mask++)
        {
            work++;
            long cost = 0, value = 0;
            for (int i = 0; i < jobs.Length; i++)
                if ((mask & (1 << i)) != 0)
                {
                    cost += jobs[i].Cost;
                    value = checked(value + jobs[i].Value);
                }
            if (cost <= capacity && value > best)
            {
                best = value;
                bestCost = (int)cost;
                bestMask = mask;
            }
        }
        int[] indices = Enumerable.Range(0, jobs.Length).Where(i => (bestMask & (1 << i)) != 0).ToArray();
        return new Choice(best, bestCost, indices, work);
    }
}
```

`LessonLab/Program.cs`:

<!-- lab-file: LessonLab/Program.cs -->
```csharp
if (args.Length == 0)
{
    Job[] jobs = [new("A", 4, 7), new("B", 3, 5), new("C", 3, 5)];
    foreach (var entry in new[] {
        (Name: "Exact", Result: Budget.Exact(jobs, 6)),
        (Name: "Density", Result: Budget.DensityGreedy(jobs, 6)),
        (Name: "HalfApprox", Result: Budget.HalfApprox(jobs, 6)) })
        Console.WriteLine($"{entry.Name}: value={entry.Result.Value}, cost={entry.Result.Cost}, " +
                          $"ids={string.Join(",", entry.Result.Indices.Select(i => jobs[i].Id))}");
}
else if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else throw new ArgumentException("Use no arguments, --check or --experiment.");
```

`LessonLab/Checks.cs`: verify feasibility, no repeated index, exact optimum, the rolling result, no input mutation and the half-value inequality. Exhaust all three-job combinations with costs 1-3, values 0-3 and capacities 0-6; add seeded random and numeric-boundary cases. The comparison `2*A >= OPT` uses `BigInteger`, since twice a valid `long` result can exceed `long.MaxValue`. Tests with nearly equal large ratios catch a floating-point ordering mistake.

<!-- lab-file: LessonLab/Checks.cs -->
```csharp
using System.Numerics;

public static class Checks
{
    private static int instances;
    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private static void Throws<T>(Action action) where T : Exception
    {
        try { action(); }
        catch (T) { return; }
        throw new InvalidOperationException($"Expected {typeof(T).Name}.");
    }

    private static void Feasible(Job[] jobs, int capacity, Choice result)
    {
        Require(result.Indices.Distinct().Count() == result.Indices.Length, "Reused job.");
        long cost = 0, value = 0;
        foreach (int index in result.Indices)
        {
            Require((uint)index < (uint)jobs.Length, "Invalid result index.");
            cost += jobs[index].Cost;
            value = checked(value + jobs[index].Value);
        }
        Require(cost <= capacity && cost == result.Cost && value == result.Value, "Invalid choice totals.");
    }

    private static void Compare(Job[] jobs, int capacity)
    {
        var snapshot = jobs.ToArray();
        var oracle = Oracle.Solve(jobs, capacity);
        var exact = Budget.Exact(jobs, capacity);
        var greedy = Budget.DensityGreedy(jobs, capacity);
        var approx = Budget.HalfApprox(jobs, capacity);
        foreach (var choice in new[] { oracle, exact, greedy, approx }) Feasible(jobs, capacity, choice);
        Require(exact.Value == oracle.Value, "DP differs from exhaustive optimum.");
        Require(Budget.ExactValueRolling(jobs, capacity) == oracle.Value, "Rolling DP differs from optimum.");
        Require(greedy.Value <= oracle.Value && approx.Value <= oracle.Value, "Value exceeds optimum.");
        Require(approx.Value >= greedy.Value, "Single-item protection reduced the value.");
        Require((BigInteger)2 * approx.Value >= oracle.Value, "Half guarantee violated.");
        Require(jobs.SequenceEqual(snapshot), "Input changed.");
        instances++;
    }

    public static void Run()
    {
        Compare([], 0); Compare([], 4);
        Compare([new("A", 4, 7), new("B", 3, 5), new("C", 3, 5)], 6);
        Compare([new("single", 2, 3)], 4); // An ascending rolling loop would incorrectly return 6.
        Compare([new("heavy", 100, 1000), new("zero", 1, 0), new("small", 2, 3)], 3);
        Compare([new("a", 1, 0), new("b", 2, 0)], 2);
        Compare([new("A", 1, 2), new("B", 1000, 1000)], 1000);
        Compare([new("A", 1, 2), new("B", 1000, 1000), new("C", 1000, 1000)], 2000);
        Compare([new("maximum", 1, long.MaxValue)], 1);
        Job[] close = [new("low", 1, long.MaxValue / 2), new("high", 1, long.MaxValue / 2 + 1)];
        Compare(close, 1);
        Require(Budget.DensityGreedy(close, 1).Indices.SequenceEqual(new[] { 1 }), "Rounded ratio ordering.");
        Throws<ArgumentNullException>(() => Budget.Exact(null!, 1));
        Throws<ArgumentOutOfRangeException>(() => Budget.Exact([], -1));
        Throws<ArgumentException>(() => Budget.HalfApprox([new("x", 0, 1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("x", -1, 1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("x", 1, -1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("", 1, 1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("x", 1, 1), new("x", 2, 1)], 2));
        Throws<OverflowException>(() => Budget.Exact([new("x", 1, long.MaxValue), new("y", 1, 1)], 1));
        Throws<ArgumentOutOfRangeException>(() => Budget.Exact([new("x", 1, 1)], 1_000_000));
        Throws<ArgumentOutOfRangeException>(() => Budget.Exact([], int.MaxValue));
        Throws<ArgumentOutOfRangeException>(() => Budget.ExactValueRolling([], int.MaxValue));
        Throws<ArgumentOutOfRangeException>(() => Oracle.Solve(
            Enumerable.Range(0, 23).Select(i => new Job($"id{i}", 1, 1)).ToArray(), 1));

        // Exhaust all three-job inputs with costs 1-3, values 0-3, capacities 0-6.
        for (int encoded = 0; encoded < 12 * 12 * 12; encoded++)
        {
            var jobs = new Job[3];
            int rest = encoded;
            for (int i = 0; i < jobs.Length; i++)
            {
                int code = rest % 12; rest /= 12;
                jobs[i] = new Job($"j{i}", code / 4 + 1, code % 4);
            }
            for (int capacity = 0; capacity <= 6; capacity++) Compare(jobs, capacity);
        }
        var random = new Random(20261008);
        for (int sample = 0; sample < 120; sample++)
        {
            Job[] jobs = Enumerable.Range(0, random.Next(0, 11))
                .Select(i => new Job($"j{i}", random.Next(1, 16), random.Next(0, 31))).ToArray();
            Compare(jobs, random.Next(0, 31));
        }
        Console.WriteLine($"PASS: {instances} instances checked against exhaustive optimum, feasibility and half guarantee.");
    }
}
```

`LessonLab/Experiment.cs`: generates the controlled workloads explained in section 6. `Work` uses different named units for different algorithms. Ratio comparisons are counted separately and do not include the final index sort. The printed quality uses decimal display rounding; the sorter and correctness inequality use exact arithmetic. If OPT is 0, quality is reported as 1 by convention because every feasible zero-value result is optimal, not because 0/0 was evaluated.

<!-- lab-file: LessonLab/Experiment.cs -->
```csharp
using System.Globalization;

public static class Experiment
{
    public static void Run()
    {
        Console.WriteLine("case,n,capacity,algorithm,value,quality,workUnit,work,ratioComparisons");
        Case("demo", [new("A", 4, 7), new("B", 3, 5), new("C", 3, 5)], 6);
        foreach (int capacity in new[] { 10, 40, 1000 })
            Case("density-trap", [new("tiny", 1, 2), new("large", capacity, capacity)], capacity);
        foreach (int k in new[] { 4, 20, 1000 })
            Case("near-half", [new("tiny", 1, 2), new("left", k, k), new("right", k, k)], 2 * k);
        foreach (int n in new[] { 8, 12, 16 }) Case("n-scaling", Generate(n), 25);
        foreach (int capacity in new[] { 20, 40, 80 }) Case("capacity-scaling", Generate(16), capacity);
    }

    private static Job[] Generate(int n) => Enumerable.Range(0, n)
        .Select(i => new Job($"j{i}", 1 + i * 7 % 11, 1 + i * 13 % 19)).ToArray();

    private static void Case(string name, Job[] jobs, int capacity)
    {
        var exact = Budget.Exact(jobs, capacity);
        var oracle = Oracle.Solve(jobs, capacity);
        if (exact.Value != oracle.Value) throw new InvalidOperationException("Experiment oracle mismatch.");
        Print(name, jobs.Length, capacity, "Exact", exact, exact.Value, "cells");
        Print(name, jobs.Length, capacity, "Oracle", oracle, exact.Value, "subsets");
        Print(name, jobs.Length, capacity, "Density", Budget.DensityGreedy(jobs, capacity), exact.Value, "items");
        Print(name, jobs.Length, capacity, "HalfApprox", Budget.HalfApprox(jobs, capacity), exact.Value, "items");
    }

    private static void Print(string name, int n, int capacity, string algorithm, Choice choice, long optimum, string unit)
    {
        decimal quality = optimum == 0 ? 1 : (decimal)choice.Value / optimum;
        Console.WriteLine($"{name},{n},{capacity},{algorithm},{choice.Value}," +
            $"{quality.ToString("F4", CultureInfo.InvariantCulture)},{unit},{choice.Work},{choice.RatioComparisons}");
    }
}
```

The correctness command prints a `PASS` line after 12,226 checked instances, plus invalid-input/size/overflow rejections. Equal-cost/value jobs with different IDs remain distinct. Different algorithms may return different tied subsets; compare feasibility and value rather than requiring identical indices. Finite tests support the proofs but cannot replace them.

</details>

Bug-repair exercise: a developer changes the rolling loop to `for (int c = job.Cost; c <= capacity; c++)`. Explain the first wrong result and give the repair. Why should a table-size error not silently switch to greedy?

<details>
<summary>Answer</summary>

For the single cost-2/value-3 job and capacity 4, the changed code writes `best[2]=3`, then reads that current-job value at `best[2]` to write `best[4]=6`. It has solved an unlimited-copy problem. Restore the downward loop in `ExactValueRolling`: at c=4, `best[2]` is still the previous row's 0, so the result stays 3. The deterministic single-job test checks both full and rolling DP against the subset oracle.

A cell-limit rejection is a resource-policy failure, not permission to change an exact-result contract. The caller may explicitly choose `HalfApprox` and report its value guarantee, reduce or remodel the budget, or use another exact method. The lab throws instead of silently substituting a different quality contract. An aggregate-value overflow similarly rejects input rather than returning wrapped scores.

</details>

Pause - 10 minutes away from the screen.

## 6. Controlled experiments: work and quality are separate

**Experiment · 45 minutes.** Predict the CSV, run `--experiment`, then vary input size, numeric capacity and greedy failure cases separately. **Done when:** you can report a quality ratio and explain what each work counter omits.

The generator fixes job costs/values and changes only the named variable within each family. Every case runs exact DP and the exhaustive oracle on identical input before evaluating density-greedy and `HalfApprox`. This controls the objective and validates OPT. It counts operations, without a stopwatch or claims about production latency.

- **Density trap:** costs/values `(1,2)` and `(W,W)`, capacity W, for W=10,40,1000. Predict G/OPT and A/OPT as W grows.
- **Near-half case:** `(1,2),(k,k),(k,k)`, capacity 2k, for k=4,20,1000. Predict why the safeguard cannot promise substantially more than 1/2 in general.
- **n scaling:** take the first 8,12,16 jobs from one deterministic sequence, capacity 25. Compare the oracle's subset count with DP cells; these are different work units.
- **Capacity scaling:** keep the same 16 jobs and change C=20,40,80. Inspect cells and value separately: a larger table need not yield a proportionally larger value.

Predict the first two families and identify which observation could contradict the implementation of the theorem.

<details>
<summary>Answer</summary>

| Family | Parameter | OPT | Density value | Protected value | Density/OPT | Protected/OPT |
|---|---|---|---|---|---|---|
| Density trap | W=10 | 10 | 2 | 10 | 0.2000 | 1.0000 |
| Density trap | W=40 | 40 | 2 | 40 | 0.0500 | 1.0000 |
| Density trap | W=1000 | 1000 | 2 | 1000 | 0.0020 | 1.0000 |
| Near-half | k=4 | 8 | 6 | 6 | 0.7500 | 0.7500 |
| Near-half | k=20 | 40 | 22 | 22 | 0.5500 | 0.5500 |
| Near-half | k=1000 | 2000 | 1002 | 1002 | 0.5010 | 0.5010 |

In the near-half family with k>2, OPT takes the two cost-k jobs for value 2k. Greedy takes the tiny job and one cost-k job for k+2; the best single job is only k, so the safeguard keeps greedy. Its ratio is `1/2 + 1/k`, approaching 1/2. In the density trap, plain greedy tends toward zero while the safeguard returns OPT. These deliberately selected cases illustrate worst-case behavior, not a random distribution of real batches.

A feasible protected value below OPT/2 on an accepted input would contradict the proved implementation claim and require debugging the algorithm, exact comparator or test reference. A value above OPT indicates an invalid subset, duplicate item, wrong reference or different objective. Neither result can be dismissed as measurement noise in this deterministic integer experiment.

</details>

Predict the remaining groups before checking.

<details>
<summary>Answer</summary>

| Variable | Parameter | DP fill cells | Oracle subsets | OPT | Density/protected value |
|---|---|---|---|---|---|
| n, C=25 | 8 | 208 | 256 | 55 | 49 |
| n, C=25 | 12 | 312 | 4096 | 79 | 79 |
| n, C=25 | 16 | 416 | 65536 | 89 | 89 |
| C, n=16 | 20 | 336 | 65536 | 74 | 74 |
| C, n=16 | 40 | 656 | 65536 | 118 | 118 |
| C, n=16 | 80 | 1296 | 65536 | 146 | 146 |

</details>

DP's `Work` counts filled cells excluding the initialized base row; the oracle counts enumerated subsets, each of which inspects n jobs. Greedy counts eligible jobs in its post-sort scan. Validation, filtering, initialization, traceback and return-index sorting are outside those counters; density comparisons have their own column. Do not compare a cell to a subset as equal CPU work. Optimization complexity bounds assume bounded numeric operations after validation; ID processing and input I/O add their own costs. Density methods use O(n log n) sorting time and O(n) extra memory under that model.

Variation: change the demo's capacity from 6 to 3, then to 7; finally multiply every cost and capacity by 10 while keeping values unchanged. Predict feasible choices, values and DP work before running.

<details>
<summary>Answer</summary>

At capacity 3, exact and both greedy methods choose one of B,C for value 5. At capacity 7, A plus one of B,C fits and yields 12; all methods can achieve it. Full DP visits 12 cells at C=3 and 24 at C=7. At the original C=6 it visits 21.

Scaling every cost and capacity by 10 leaves feasible subsets and optimum 10 unchanged, but full DP visits `3*(60+1)=183` cells, compared with 21. The table guard can eventually reject large scales even though the mathematical selection problem is equivalent. Dividing all costs/capacity by a shared exact factor can undo this artificial growth; arbitrary rounding needs separate feasibility analysis. Density ordering is unchanged under a uniform cost scale.

</details>

**Limits:** these counts and ratios verify these instances, not runtime, peak memory, concurrency, fairness or worker p99. A mean quality on sampled jobs does not strengthen a worst-case theorem. Real value estimates, dependencies and multiple budgets may invalidate the model. To measure elapsed performance, hold the objective fixed, separate setup, warm up the runtime, repeat runs and report variation. No elapsed-time benchmark or database experiment is part of this lab.

Pause - 10 minutes away from the screen.

## 7. Transfer: add a second constraint

**Transfer · 35 minutes.** Change the batch contract to “at most K jobs” and derive a state before writing code. **Done when:** the implementation rejects an infeasible combination and matches an independent small oracle.

The original state forgets how many jobs were selected. Consider capacity 6, K=1 and jobs A=(6,8), B=(3,5), C=(3,5). Why is keeping the original table and truncating its returned list unsafe? Define a recurrence, give its complexity and implement a value-only solution. Test K=0,1,2, a capacity of 0 and K larger than n.

<details>
<summary>Answer - model, complete code and checks</summary>

The old table chooses B+C for 10. Truncation leaves value 5 although A alone yields 8. Even if the list's score is recomputed correctly, truncation cannot recover an alternative already discarded by the state.

Define H(i,c,k) as the greatest value using the first i jobs, cost at most c and count at most k. Empty prefixes, zero capacity and k=0 have value 0 under the positive-cost contract. For k>0, skip from H(i-1,c,k), or, when cost fits, take value plus H(i-1,c-cost,k-1). The previous item layer and reduced count prevent repetition and enforce both constraints. The same skip/take induction proves correctness. Cap K at n; time and table memory are O((n+1)(C+1)(min(K,n)+1)). It returns only the value, not selected IDs.

Keep `Budget.cs` from the lab and replace `Program.cs` in a separate copy with this complete program. Remove the other lab files if desired; none are needed. Run `dotnet run -c Release --project LessonLab`. Its independent oracle enumerates subsets and checks their count as well as cost. The table guard is a resource policy, not an approximation.

```csharp
using System.Numerics;

var demo = new[] { new Job("A", 6, 8), new Job("B", 3, 5), new Job("C", 3, 5) };
if (CountLimited.Solve(demo, 6, 1) != 8) throw new Exception("Transfer example failed.");
var random = new Random(20261008);
int checkedCases = 0;
for (int sample = 0; sample < 60; sample++)
{
    var jobs = Enumerable.Range(0, random.Next(0, 9))
        .Select(i => new Job($"J{i}", random.Next(1, 8), random.Next(0, 16))).ToArray();
    foreach (int capacity in new[] { 0, 5, 12 })
        foreach (int limit in new[] { 0, 1, 2, jobs.Length + 3 })
        {
            long expected = CountLimited.Oracle(jobs, capacity, limit);
            if (CountLimited.Solve(jobs, capacity, limit) != expected)
                throw new Exception("Count-limited value differs from exhaustive optimum.");
            checkedCases++;
        }
}
try { CountLimited.Solve(demo, 6, -1); throw new Exception("Negative limit accepted."); }
catch (ArgumentOutOfRangeException) { }
try { CountLimited.Solve(demo, int.MaxValue, 1); throw new Exception("Large table accepted."); }
catch (ArgumentOutOfRangeException) { }
Console.WriteLine($"PASS: {checkedCases} count-limited cases; demo value=8.");

public static class CountLimited
{
    public static long Solve(Job[] jobs, int capacity, int maxJobs)
    {
        Budget.Validate(jobs, capacity);
        if (maxJobs < 0) throw new ArgumentOutOfRangeException(nameof(maxJobs));
        int limit = Math.Min(maxJobs, jobs.Length);
        BigInteger cells = (BigInteger)(jobs.Length + 1L) * (capacity + 1L) * (limit + 1L);
        if (cells > Budget.MaxCells) throw new ArgumentOutOfRangeException(nameof(capacity));
        var best = new long[jobs.Length + 1, capacity + 1, limit + 1];
        for (int i = 1; i <= jobs.Length; i++)
            for (int c = 0; c <= capacity; c++)
                for (int k = 1; k <= limit; k++)
                {
                    best[i, c, k] = best[i - 1, c, k];
                    Job job = jobs[i - 1];
                    if (job.Cost <= c)
                        best[i, c, k] = Math.Max(best[i, c, k],
                            checked(best[i - 1, c - job.Cost, k - 1] + job.Value));
                }
        return best[jobs.Length, capacity, limit];
    }

    public static long Oracle(Job[] jobs, int capacity, int maxJobs)
    {
        Budget.Validate(jobs, capacity);
        if (maxJobs < 0) throw new ArgumentOutOfRangeException(nameof(maxJobs));
        if (jobs.Length > 22) throw new ArgumentOutOfRangeException(nameof(jobs));
        long best = 0;
        for (int mask = 0; mask < (1 << jobs.Length); mask++)
        {
            long cost = 0, value = 0;
            int count = 0;
            for (int i = 0; i < jobs.Length; i++)
                if ((mask & (1 << i)) != 0)
                {
                    count++;
                    cost += jobs[i].Cost;
                    value = checked(value + jobs[i].Value);
                }
            if (cost <= capacity && count <= maxJobs) best = Math.Max(best, value);
        }
        return best;
    }
}
```

Expected: `PASS: 720 count-limited cases; demo value=8.` The tests use deterministic small inputs; the induction, rather than 720 successes, supports the general claim. The original half-approximation proof does not automatically survive a count constraint: its fractional budget-only upper bound and candidate construction must be reconsidered.

</details>

## 8. Synthesis and retrieval

**Synthesis · 45 minutes.** Close the page, reconstruct the argument, then check the answers below. **Done when:** you can identify which state to keep, which contract makes it correct and what the experiment actually observed.

1. Why does the item layer matter, and why can one row only be updated downwards?

<details>
<summary>Answer 1</summary>

The layer records availability of each job; both branches read the previous prefix. In one row, descending capacities preserve that previous-prefix meaning at the lower lookup. Ascending updates can reuse the current job. A count limit adds a count dimension; changing constraints can change the state.

</details>

2. When is O(nC) a misleading “polynomial” claim?

<details>
<summary>Answer 2</summary>

C is a numeric capacity, not its bit length. Doubling its value doubles table work even when its representation grows by one bit. This is pseudopolynomial; a table guard may reject a mathematically valid instance. Smaller memory alone does not remove the time dependency.

</details>

3. What protects the density method, and why does PostgreSQL's GEQO not inherit that guarantee?

<details>
<summary>Answer 3</summary>

Choose the better of the density solution and best feasible single job. Under positive costs, nonnegative additive values and one budget, the fractional bound proves at least OPT/2. GEQO searches a different constrained plan space with estimated costs; neither this construction nor this proof describes it.

</details>

4. Separate assumptions, predictions, observations and inferences for this lab. Which production claims still need evidence?

<details>
<summary>Answer 4</summary>

**Assumptions:** indivisible independent jobs, unique IDs, positive integer costs, additive nonnegative values, one fixed capacity and the lab's numeric/resource contract. **Predictions:** the DP values and operation formulas; the deliberately bad greedy families. **Observations after running:** the displayed CSV rows and finite-suite checks. **Inferences:** agreement on those inputs and reproduction of the chosen failure modes. The general optimum/half claims rely on proof plus a reviewed implementation. Worker latency, cost-estimate accuracy, transactional safety, fairness, PostgreSQL query performance and real batch quality still need separate evidence. A source inspection establishes program structure at the cited commit, not runtime behavior measured on our database.

</details>

The next session should retrieve the state meaning, the downward-update counterexample and the half-bound's assumptions before changing the objective or constraints.

## Sources and reuse

- David P. Williamson and David B. Shmoys, [The Design of Approximation Algorithms](https://www.designofapproxalgs.com/book.pdf), Section 3.1, printed pages 65-67 and Exercise 3.1, printed page 77. Original explanations here; the book PDF is linked, not redistributed.
- PostgreSQL source at commit `7885b94dd81b98bbab9ed878680d156df7bf857f`, tag `REL_17_6`: bounded links in Section 4. [PostgreSQL license](https://github.com/postgres/postgres/blob/7885b94dd81b98bbab9ed878680d156df7bf857f/COPYRIGHT). No PostgreSQL code is copied into this lab.
- [PostgreSQL 17 GEQO configuration](https://www.postgresql.org/docs/17/runtime-config-query.html#RUNTIME-CONFIG-QUERY-GEQO) supplies the documented threshold and tradeoff; it does not supply a knapsack approximation guarantee.
- Lesson prose is CC BY 4.0. All lab code is original MIT teaching code; its license is included in the ZIP.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Lesson 03 - Shortest paths](../2026-10-07-shortest-paths/lesson.md) - Recall state and finalization arguments.
- [C# lab guide](../../labs/budget-selection/dotnet/README.md) - SDK setup, checks, experiment and sources.

---

[← Previous: Lesson 03 - Shortest paths: choosing BFS or Dijkstra](../2026-10-07-shortest-paths/lesson.md) · [All lessons](../../README.md) · [Next: Lesson 05 - Indexes and query plans: when a seek still does much work →](../2026-10-09-index-query-plans/lesson.md)
<!-- LESSON_NAVIGATION_END -->
