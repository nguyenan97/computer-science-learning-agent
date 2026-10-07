# Lesson 03 - Shortest paths: choosing BFS or Dijkstra

[Tiếng Việt](../../vi/lessons/2026-10-07-shortest-paths/lesson.md) · [Download the C# lab](https://nguyenan97.github.io/computer-science-learning-agent/labs/shortest-paths/dotnet-lab.zip)

Lesson 02 made a search correct by preserving a partition. Here, the question is which route can be declared optimal. A direct road may have fewer segments and still take longer than three smaller roads. Choosing a queue before defining what “shortest” means can give a fast, wrong answer.

**Goal:** choose BFS for the fewest edges and Dijkstra for the smallest sum of nonnegative costs. Prove when a distance becomes final, reconstruct a route, repair an early-stop bug and compare operation counts. The roadmap places this in graph strategy selection, after program reasoning. You need arrays, loops and the invariant/cost-model ideas from Lessons 01 and 02; no previous graph course is assumed.

## Core ideas

- **Directed graph and edge cost.** Nodes represent places or states; an edge permits movement in one direction and carries a cost. `A -> B (4)` permits A to B at cost 4, without promising a return edge.
- **Shortest path depends on the objective.** A route can minimize edge count or total cost. One edge costing 10 uses fewer edges than three edges costing 1 each, but has higher total cost.
- **BFS (breadth-first search).** Explore by number of edges from the start. In an all-unit-cost graph, it reaches every one-edge option before any two-edge option, so first discovery gives the minimum edge count.
- **Dijkstra.** Explore the smallest currently known total cost first and improve other distances through it. With nonnegative edge costs, removing a current minimum candidate makes its distance final; discovering it earlier does not.

The sections include complete answers. You may read the traces and code without executing them. If setup takes longer than 15 minutes of the lab section, use that reading route and keep the remaining time for reasoning; record no scores or submissions.

## 1. Recall and prerequisite bridge

**Recall · 20 minutes.** Reconstruct the selected Lesson 02 invariant and check two foundations. **Done when:** you can name a precondition and explain why first discovery may need reconsideration.

1. State the `lower_bound` invariant and explain why returning `lo` is correct.

<details>
<summary>Answer</summary>

For sorted data, every position before `lo` has a value below the target; every position from `hi` onward has a value at least the target. Unknown positions are in `[lo,hi)`. Each branch preserves the partition and shrinks the unknown interval. At `lo == hi`, this is the first position with value at least the target, or n. Sortedness justifies discarding positions. Today, nonnegative weights justify finalizing a distance.

</details>

2. Does `A -> B` imply `B -> A`? Can two edges between the same nodes have different costs?

<details>
<summary>Answer</summary>

Neither direction is implied in a directed graph. Parallel edges are allowed: A to B might cost 4 on one service and 7 on another. An adjacency list stores the outgoing edges of each node. To model an undirected connection, add both directions explicitly. Our lab accepts parallel edges and self-loops.

</details>

3. From A, first discover C at cost 9; later discover A to B to C costing 1+1. What should happen to C's tentative distance and parent?

<details>
<summary>Answer</summary>

Change the distance from 9 to 2 and change its parent to B. “Discovered” means a route exists; it does not mean the route is optimal. If this is unclear, draw the three arrows, add their costs and compare the two routes. This is the foundation bridge: keep best-known distances in an array and parents in a separate array before reasoning about queues.

</details>

## 2. Model, trace and correctness

**Foundation · 50 minutes.** Run both strategies by hand, state their invariants and build a counterexample. **Done when:** you can justify the stopping rule and explain the role of nonnegative costs.

### Example before the formula

Use node IDs S=0, A=1, B=2, T=3. S has a direct edge to T costing 10, and a three-edge route through A and B costing 1 on each edge. T has no outgoing edges.

Predict which path minimizes edge count and which minimizes total cost. Would it be safe for Dijkstra to stop when S first inserts T?

<details>
<summary>Answer</summary>

S to T uses one edge but costs 10. S to A to B to T uses three edges and costs 3. Stopping on insertion would return 10 before the cheaper route is explored. BFS on a graph with every edge replaced by cost 1 answers the edge-count question; it does not answer the original weighted question.

</details>

For a route P, its cost is `cost(P) = sum of w(u,v) over its edges`. Define `δ(s,v)` as the minimum route cost from s to v, with infinity for unreachable nodes. `dist[v]` is the best cost found so far; it starts at infinity except `dist[s]=0`. A **relaxation** tries the route through u: if `dist[u] + w(u,v) < dist[v]`, update the distance and `parent[v]=u`. Each finite label represents a real route, so it cannot be smaller than the true minimum.

**Lab contract:** a finite, fixed directed graph, IDs `0..V-1`, and nonnegative integer costs. Return one minimum cost and its node sequence. An unreachable target returns `null` and an empty path; source equal to target returns 0 and `[source]`. Parallel edges and zero-cost cycles are allowed. BFS additionally requires every edge cost to be 1. Graph construction rejects invalid IDs, negative costs and `long.MaxValue`; the last value is reserved for infinity. If any candidate sum examined by Dijkstra reaches or exceeds that reserved value, throw `OverflowException`, even if that candidate would not improve the target. This is an explicit numeric limit, not a claim about arbitrary-size integers.

### BFS: discovery is enough under unit costs

A FIFO queue removes nodes in nondecreasing edge distance. While processing layer k, newly discovered nodes enter layer k+1 behind nodes already waiting. Mark a node when enqueuing it, so a cycle or two incoming edges cannot enqueue it repeatedly.

The invariant is: every discovered distance is the smallest edge count, and the queue contains nodes in nondecreasing distance with at most two consecutive layers. Initially only s, at distance 0, is queued. If a newly discovered v had a shorter route than k+1, its predecessor on that route would have been processed in an earlier layer and would already have discovered v. This contradiction proves first discovery is optimal. Our code stops when the target is dequeued, which also makes the counters easy to compare.

All edges costing the same positive constant c have the same optimal routes as unit costs; multiply the edge count by c afterward. The lab deliberately accepts only 1 in `Bfs`. If every cost is 0, any reachable route has minimum cost 0. Mixed zero and positive costs require a different strategy; this lesson uses Dijkstra.

### Dijkstra: removal of the current minimum is enough

In the following trace, a queue entry is `(cost,node)`. The entry `(10,T)` stays in the queue after T improves to 3. It is **stale**: its cost no longer equals the current label.

| Removed current entry | Distance updates | Entries left, sorted for explanation |
|---|---|---|
| (0,S) | T=10, A=1 | (1,A), (10,T) |
| (1,A) | B=2 | (2,B), (10,T) |
| (2,B) | T=3, parent[T]=B | (3,T), (10,T) |
| (3,T) | Target is final; return | (10,T) is never needed |

The invariant is: each finalized node has its true minimum distance; finite tentative labels represent actual routes; every unfinished finite label has a matching queue entry. Choose u with the smallest current label. Suppose a cheaper route to u existed. On that route, let y be the first unfinished node and x its finalized predecessor. Processing x already offered a cost to y no greater than the route's prefix cost. With nonnegative remaining edges, that prefix costs no more than the alleged cheaper route to u. Then `dist[y] < dist[u]`, contradicting the choice of u. For the source, the empty route costs 0 and nonnegative cycles cannot improve it.

Zero edges preserve this proof: the required comparison is “no more than”, not “strictly less than”, for the remaining suffix. Only strict improvements update parents, so an equal-cost zero cycle does not create repeated updates. Finalizing u scans its outgoing edges; a later route cannot improve it. Skip stale entries **before** counting a finalization or deciding to stop. A target can be returned on its current minimum removal, never on its first insertion.

### What breaks the proof?

Construct a negative-edge counterexample using `S -> T (2)`, `S -> A (5)`, `A -> T (-10)`. What result does an early-return Dijkstra produce, and which proof step fails?

<details>
<summary>Answer</summary>

It removes T at 2 before A at 5 and returns 2. The route through A actually costs -5. The prefix reaching A costs 5, greater than the whole route costing -5, so the nonnegative-suffix argument fails. A negative edge does not always cause a wrong answer, but the general guarantee is lost. Bellman-Ford handles negative edges and detects reachable negative cycles; if such a cycle lies on a route to the target, no finite minimum exists. Our lab rejects all negative edges at graph construction, including those in disconnected components.

</details>

### Count work under the actual queue design

For BFS, each node enters the queue at most once and each outgoing edge is scanned at most once. Initializing arrays touches V entries even if the target is nearby. Time is O(V+E), with O(V) search memory, beyond O(V+E) graph storage.

For the lab's Dijkstra, a strict improvement enqueues a new entry instead of decreasing an existing key. There are at most E improvements and E+1 total insertions; the heap can hold O(E+1) entries, including old ones. Each heap operation costs O(log(E+2)). The bound is `O(V + E log(E+2))` time and O(V+E) search memory. On a simple graph, E is at most V², so this is often written `O((V+E) log V)` for V>=2. With arbitrary parallel edges, keep the E-based bound. Early return can reduce scanned edges, but does not remove the array initialization cost. Counting only “nodes visited” hides queue work.

Pause - 10 minutes away from the screen.

## 3. Read sources and map the idea to a project

**Source reading · 45 minutes.** Inspect the three bounded references below and write three claim/evidence/limit rows. **Done when:** each claim names the assumption that supports it and one conclusion the source does not establish.

Read the description, pseudocode and complexity sections of [Boost BFS](https://www.boost.org/doc/libs/1_85_0/libs/graph/doc/breadth_first_search.html) and [Boost Dijkstra](https://www.boost.org/doc/libs/1_85_0/libs/graph/doc/dijkstra_shortest_paths.html). Then read the Remarks of [.NET PriorityQueue](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.priorityqueue-2?view=net-10.0). These are reference algorithms and API documentation; the lab is an original implementation with its own queue policy.

Questions: What does BFS's distance count? Which input condition justifies Dijkstra? Does the .NET queue preserve FIFO order among equal priorities? Can Boost's stated Dijkstra complexity be copied directly to this lab?

<details>
<summary>Answer</summary>

| Claim | Evidence | Assumption or limit |
|---|---|---|
| BFS minimizes edge count | Boost defines distance as the number of edges and uses a queue with discovery marking | It does not minimize varying road durations |
| Dijkstra permits nonnegative weights | Boost's description and relaxation pseudocode | Negative weights invalidate the guarantee; the page's stated O(V log V + E) is not a bound for our duplicate-entry heap |
| PriorityQueue removes a minimum priority | Microsoft documents a quaternary min-heap and no FIFO guarantee for equal priorities | The lab uses `(cost,node ID)` to make ties deterministic; this does not select the lexicographically smallest full path |

The lab's complexity must follow its actual insertions and heap size. A source can confirm a mechanism without confirming every implementation or performance claim built around it.

</details>

### Application: a .NET warehouse routing service

Suppose SQL Server stores warehouse locations and directed connections, with an integer `TravelSeconds` cost on each connection. An ASP.NET service loads one version into an immutable adjacency list, computes a route for a request and returns `{graphVersion, cost, path}`. Angular draws the path. A version identifies the exact graph used; closing a corridor creates a new version rather than mutating an in-flight search.

Use BFS for the fewest hand-offs when every connection counts equally. Use Dijkstra for the smallest sum of travel seconds. Do not add seconds and monetary charges without defining the conversion and business objective. A retry can reuse a cached result only when graph version, endpoints and objective match. Building and validating the graph costs O(V+E), so reuse a snapshot across queries instead of querying SQL Server once per relaxation.

If a turn's cost depends on the previous corridor, location alone is not enough state. Represent `(location, incoming corridor)` as the search node. If travel cost depends on departure time, the static-edge assumptions no longer suffice. Production routing needs a model for that dependence and for when costs are observed; this lab does not solve it. Queueing, database access and graph loading also remain outside its counters.

Design question: a team wants to minimize travel time and then the number of transfers among equal-time routes. Is the lab's `(cost,node ID)` priority enough?

<details>
<summary>Answer</summary>

No. Node ID only resolves processing ties. Define each distance as `(totalSeconds, transfers)` and compare these pairs lexicographically, adding `(edgeSeconds, 1)` on each step. With nonnegative seconds and transfer increments, the monotonic extension argument still works. Store and compare the entire objective pair when relaxing and skipping stale entries. Node ID can be a third queue tie-break but must not replace the second objective. This is a proposed extension, not the lab's implemented contract.

</details>

## 4. Case study: OSRM's route query

**Implementation reading · 45 minutes.** Trace one relaxation in OSRM and compare its queue policy with the lab. **Done when:** you can separate the verified mechanism, a product trade-off and the part the lab does not reproduce.

The Open Source Routing Machine serves routes over OpenStreetMap road data. We inspect **v5.27.1, commit `4f3ee609ec1af40eb1f445c6706cfa5beb04c990`**, specifically its CH (Contraction Hierarchies) route-search slice. This is a product case: the query must choose a useful driving route, not merely the smallest count of road segments. The [README](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/README.md#quick-start) demonstrates a Berlin map extract, describes preprocessing pipelines and recommends MLD by default; CH is highlighted for very large distance matrices. We do not infer a measured node count or response latency from those descriptions.

### A bounded source walk

1. In [`profiles/car.lua`](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/profiles/car.lua#L15-L38), the default `weight_name` is `routability`, with duration and distance as commented alternatives. The turn handler also computes penalties. **Weight is the profile's objective, not automatically distance or travel seconds.**
2. In [`directShortestPathSearch`, CH specialization](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/src/engine/routing_algorithms/direct_shortest_path.cpp#L20-L64), the code obtains forward and reverse heaps, inserts endpoint candidates, calls `search`, unpacks the packed path and extracts a route.
3. In [`routingStep`](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/include/engine/routing_algorithms/routing_base_ch.hpp#L117-L186), it removes a minimum heap node, checks a possible meeting with the reverse search, manages a route-cost upper bound, applies stopping/stalling logic and relaxes outgoing edges.
4. In [`relaxOutgoingEdges`](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/include/engine/routing_algorithms/routing_base_ch.hpp#L51-L83), it checks edge direction, asserts positive edge weight, forms a candidate sum, inserts unseen nodes and updates parent plus `DecreaseKey` on a strict improvement. This slice makes the link between relaxation and a production route decision visible.

Trace exercise: u is removed at cost 2, an outgoing edge to v costs 3 and v is already in the heap at cost 9. What changes? What if v is already at 5?

<details>
<summary>Answer</summary>

The candidate is 5. For v at 9, update its parent to u, update its cost to 5 and decrease its heap key. For v already at 5, the strict comparison fails and its existing parent remains. The code tests the direction flag before considering the edge. In our lab, the first case adds a new `(5,v)` entry and leaves `(9,v)` to be skipped later; OSRM updates its indexed heap entry.

</details>

### The product decision and its limits

**Verified:** this CH slice chooses heap minima and improves distances by edge weight; it asserts strictly positive traversed weights, handles forward/reverse directions and returns an unpacked route. The lab's allowance for zero weights is broader than that assertion. OSRM has endpoint offsets, including negative initial offsets: comments near `routingStep` explain the extra termination adjustment. Those offsets do not authorize arbitrary negative road edges in our Dijkstra contract.

**Design inference:** replacing this weighted selection with FIFO layers would generally optimize segment count and could choose a slower or less suitable route. We infer that consequence from the objective and algorithm; we are not claiming the maintainers documented a rejected BFS experiment. Preprocessing and indexed heaps trade additional data structures and maintenance complexity for less query work. The source confirms their existence; this reading does not quantify the gain.

The lab reproduces only the minimum-label/relaxation idea. It does not reproduce bidirectional stopping, CH shortcuts, stalling, map snapping, turn modeling or an OSRM API benchmark. For the warehouse project, adopt the explicit objective and immutable graph version first; choose a more involved routing engine only when graph size and query workload justify it.

Lunch and rest - 30 minutes.

## 5. C# lab: implement, check and repair

**Lab · 75 minutes.** Run the demo, inspect the implementation, execute checks and explain the deliberate bug below. **Done when:** the correctness command passes and you can explain why the target is final at removal, including the zero-edge case.

Use **.NET SDK 10.0.401**, target **net10.0**, with no external packages. Download and extract the ZIP; its top-level directory is `dotnet`. Or create that directory and the four `LessonLab/*.cs` files shown below. These are all the executable lab sources, so the page can be used without source downloads.

`dotnet/global.json`:

```json
{
  "sdk": { "version": "10.0.401", "rollForward": "latestPatch" }
}
```

`dotnet/LessonLab/LessonLab.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>Exe</OutputType>
    <TargetFramework>net10.0</TargetFramework>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

From a terminal inside the extracted `dotnet` directory:

```bash
dotnet --version
dotnet run -c Release --project LessonLab
dotnet run -c Release --project LessonLab -- --check
dotnet run -c Release --project LessonLab -- --experiment
```

Expected demo output:

```text
BFS unit projection: hops=1, path=0->3
Dijkstra original: cost=3, path=0->1->2->3
The BFS path costs 10 in the original graph. Dijkstra costs 3.
```

If the SDK is already installed, restore needs no third-party package. After one successful build, `dotnet run --no-restore -c Release --project LessonLab -- --check` works offline. Without the SDK, use the worked trace and answers; neither an online service nor SQL Server is needed. If the pinned SDK is missing, install that version rather than silently changing the target. The [lab guide](../../labs/shortest-paths/dotnet/README.md) has setup and source links.

### Graph and route solvers

`LessonLab/Routes.cs` copies edges into private adjacency arrays, so callers cannot change weights midway through a search. `ReadOnlySpan<Edge>` exposes a read-only view without allocating a new collection. Costs use `long`; node IDs use `int`. The graph is validated once, while source/target checks run for each query.

```csharp
// Original teaching code, MIT. This is not adapted from OSRM.
public readonly record struct Link(int From, int To, long Cost);
public readonly record struct Edge(int To, long Cost);

public sealed class Graph
{
    private readonly Edge[][] adjacency;
    public int Count => adjacency.Length;
    public bool UnitCosts { get; }

    public Graph(int count, params Link[] links)
    {
        if (count <= 0) throw new ArgumentOutOfRangeException(nameof(count));
        ArgumentNullException.ThrowIfNull(links);
        var lists = Enumerable.Range(0, count).Select(_ => new List<Edge>()).ToArray();
        bool unit = true;
        foreach (var link in links)
        {
            if ((uint)link.From >= (uint)count || (uint)link.To >= (uint)count)
                throw new ArgumentOutOfRangeException(nameof(links), "Invalid node ID.");
            if (link.Cost < 0 || link.Cost == long.MaxValue)
                throw new ArgumentOutOfRangeException(nameof(links), "Cost must be in [0, long.MaxValue).");
            unit &= link.Cost == 1;
            lists[link.From].Add(new Edge(link.To, link.Cost));
        }
        adjacency = lists.Select(list => list.ToArray()).ToArray();
        UnitCosts = unit;
    }

    public ReadOnlySpan<Edge> Neighbors(int node) => adjacency[node];
}

public sealed record Route(long? Distance, int[] Path, int Settled, long Scanned, long Stale);

public static class Routes
{
    private static void Validate(Graph graph, int source, int target)
    {
        ArgumentNullException.ThrowIfNull(graph);
        if ((uint)source >= (uint)graph.Count || (uint)target >= (uint)graph.Count)
            throw new ArgumentOutOfRangeException(nameof(source), "Invalid source or target.");
    }

    private static Route Finish(long[] distance, int[] parent, int target,
                                int settled, long scanned, long stale)
    {
        if (distance[target] == long.MaxValue)
            return new Route(null, [], settled, scanned, stale);
        var path = new List<int>();
        for (int node = target; node != -1; node = parent[node]) path.Add(node);
        path.Reverse();
        return new Route(distance[target], path.ToArray(), settled, scanned, stale);
    }

    public static Route Bfs(Graph graph, int source, int target)
    {
        Validate(graph, source, target);
        if (!graph.UnitCosts)
            throw new ArgumentException("BFS requires every cost to be 1.", nameof(graph));
        var distance = Enumerable.Repeat(long.MaxValue, graph.Count).ToArray();
        var parent = Enumerable.Repeat(-1, graph.Count).ToArray();
        var queue = new Queue<int>();
        distance[source] = 0;
        queue.Enqueue(source);
        int settled = 0;
        long scanned = 0;
        while (queue.TryDequeue(out int node))
        {
            settled++;
            if (node == target) break;
            foreach (var edge in graph.Neighbors(node))
            {
                scanned++;
                if (distance[edge.To] != long.MaxValue) continue;
                distance[edge.To] = distance[node] + 1;
                parent[edge.To] = node;
                queue.Enqueue(edge.To);
            }
        }
        return Finish(distance, parent, target, settled, scanned, 0);
    }

    public static Route Dijkstra(Graph graph, int source, int target)
    {
        Validate(graph, source, target);
        var distance = Enumerable.Repeat(long.MaxValue, graph.Count).ToArray();
        var parent = Enumerable.Repeat(-1, graph.Count).ToArray();
        var queue = new PriorityQueue<int, (long Cost, int Node)>();
        distance[source] = 0;
        queue.Enqueue(source, (0, source));
        int settled = 0;
        long scanned = 0, stale = 0;
        while (queue.TryDequeue(out int node, out var priority))
        {
            if (priority.Cost != distance[node]) { stale++; continue; }
            settled++;
            if (node == target) break;
            foreach (var edge in graph.Neighbors(node))
            {
                scanned++;
                // long.MaxValue is reserved for unreachable, not a finite distance.
                if (edge.Cost >= long.MaxValue - priority.Cost)
                    throw new OverflowException("Reached candidate exceeds the finite-distance range.");
                long candidate = priority.Cost + edge.Cost;
                if (candidate >= distance[edge.To]) continue;
                distance[edge.To] = candidate;
                parent[edge.To] = node;
                queue.Enqueue(edge.To, (candidate, edge.To));
            }
        }
        return Finish(distance, parent, target, settled, scanned, stale);
    }
}
```

`parent` stores how the best route was reached. Follow parents backward from the target and reverse the list. `null` distance distinguishes an unreachable target from a reachable zero-cost route. With nonnegative weights and strict updates, a finalized node cannot acquire a better parent, so zero cycles do not form a parent cycle. Equal-cost alternatives may leave different valid routes; the contract promises one, not all routes. Node IDs alone cannot identify which of two parallel edges was taken. Return edge IDs too if the UI must show a particular service or corridor.

### Demo entry point

`LessonLab/Program.cs`:

```csharp
if (args.Length == 0)
{
    var graph = new Graph(4, new(0, 3, 10), new(0, 1, 1), new(1, 2, 1), new(2, 3, 1));
    var hops = Routes.Bfs(new Graph(4, new(0, 3, 1), new(0, 1, 1), new(1, 2, 1), new(2, 3, 1)), 0, 3);
    var weighted = Routes.Dijkstra(graph, 0, 3);
    Console.WriteLine($"BFS unit projection: hops={hops.Distance}, path={string.Join("->", hops.Path)}");
    Console.WriteLine($"Dijkstra original: cost={weighted.Distance}, path={string.Join("->", weighted.Path)}");
    Console.WriteLine("The BFS path costs 10 in the original graph. Dijkstra costs 3.");
}
else if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else throw new ArgumentException("Use no arguments, --check or --experiment.");
```

### Correctness checks and bug repair

Run `--check`. It compares Dijkstra against an independent repeated-relaxation oracle on small graphs, verifies that returned paths exist and have the stated cost, and compares BFS on unit-cost projections. It includes an improved target discovered early, an actually dequeued stale entry, disconnected nodes, equal-cost alternatives, parallel edges, self-loops, zero cycles, rejected negative costs and the numeric boundary.

Exercise: a developer adds `if (edge.To == target) return ...;` immediately after enqueuing an improved distance. Explain the defect and repair it. Then explain why changing `candidate >= distance[edge.To]` to `candidate > distance[edge.To]` is also dangerous.

<details>
<summary>Answer</summary>

The first change returns T at 10 in the demo before the route costing 3 is found. Remove that early return. Keep the target check after dequeue and after rejecting stale entries, as in `Routes.cs`. To reproduce the regression without changing the solver, the deterministic test checks that the demo graph returns 3.

The second change enqueues equal-cost candidates and changes parents on ties. On a reachable zero-cost cycle, it can keep adding entries indefinitely; a zero self-loop can even set its own parent. Use a strict improvement: skip `candidate >= distance[edge.To]`. The tests include both a zero cycle and a zero self-loop, so they exercise this requirement. BFS's discovery marking is valid only for its own unit-cost contract; copying it into Dijkstra would prevent later improvements.

</details>

`LessonLab/Checks.cs` below is the complete check runner. The oracle is a small Bellman-Ford-style repeated relaxation without a priority queue. Its inputs are nonnegative with tiny weights, so it is independent of the heap policy and never approaches overflow. Its random seed fixes the cases for this SDK; passing a finite suite is evidence, not a proof for every graph.

<details>
<summary>Answer - complete correctness runner</summary>

```csharp
public static class Checks
{
    private static int queries;
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

    public static long PathCost(Graph graph, int[] path)
    {
        long sum = 0;
        for (int i = 1; i < path.Length; i++)
        {
            long best = long.MaxValue;
            foreach (var edge in graph.Neighbors(path[i - 1]))
                if (edge.To == path[i]) best = Math.Min(best, edge.Cost);
            Require(best != long.MaxValue, "Path uses a missing edge.");
            sum = checked(sum + best);
        }
        return sum;
    }

    // Independent oracle for small graphs: repeated relaxation, no priority queue.
    private static long? Oracle(Graph graph, int source, int target)
    {
        var distance = Enumerable.Repeat(long.MaxValue, graph.Count).ToArray();
        distance[source] = 0;
        for (int pass = 0; pass < graph.Count - 1; pass++)
        {
            bool changed = false;
            for (int node = 0; node < graph.Count; node++)
            {
                if (distance[node] == long.MaxValue) continue;
                foreach (var edge in graph.Neighbors(node))
                {
                    long candidate = checked(distance[node] + edge.Cost);
                    if (candidate >= distance[edge.To]) continue;
                    distance[edge.To] = candidate;
                    changed = true;
                }
            }
            if (!changed) break;
        }
        return distance[target] == long.MaxValue ? null : distance[target];
    }

    private static void Compare(Graph graph, int source, int target, bool bfs = false)
    {
        Route route = bfs ? Routes.Bfs(graph, source, target) : Routes.Dijkstra(graph, source, target);
        Require(route.Distance == Oracle(graph, source, target), "Distance differs from oracle.");
        if (route.Distance is null) Require(route.Path.Length == 0, "Unreachable path must be empty.");
        else
        {
            Require(route.Path[0] == source && route.Path[^1] == target, "Wrong path endpoints.");
            Require(route.Path.Length <= graph.Count, "Parent cycle.");
            Require(PathCost(graph, route.Path) == route.Distance, "Path cost differs from distance.");
        }
        queries++;
    }

    public static void Run()
    {
        var trap = new Graph(4, new(0, 3, 10), new(0, 1, 1), new(1, 2, 1), new(2, 3, 1));
        Compare(trap, 0, 3);
        Require(Routes.Dijkstra(trap, 0, 3).Distance == 3, "Early-discovery regression.");
        Throws<ArgumentException>(() => Routes.Bfs(trap, 0, 3));
        var stale = new Graph(5, new(0, 1, 9), new(0, 2, 1), new(2, 1, 1), new(1, 3, 1));
        Compare(stale, 0, 4);
        Require(Routes.Dijkstra(stale, 0, 4).Stale == 1, "Expected a skipped old entry.");
        var zero = new Graph(4, new(0, 1, 0), new(1, 0, 0), new(1, 2, 2), new(0, 2, 9),
                             new(1, 2, 2), new(2, 2, 0));
        Compare(zero, 0, 2); Compare(zero, 0, 0); Compare(zero, 0, 3);
        var single = new Graph(1);
        Compare(single, 0, 0); Compare(single, 0, 0, true);
        var tie = new Graph(4, new(0, 2, 1), new(0, 1, 1), new(1, 3, 1), new(2, 3, 1));
        Compare(tie, 0, 3); Compare(tie, 0, 3, true);
        Require(Routes.Dijkstra(tie, 0, 3).Path.SequenceEqual(new[] { 0, 1, 3 }), "Tuple tie-break.");
        var large = new Graph(3, new(0, 1, long.MaxValue - 1), new(1, 2, 0));
        Require(Routes.Dijkstra(large, 0, 2).Distance == long.MaxValue - 1, "Finite-range boundary.");
        Throws<OverflowException>(() => Routes.Dijkstra(
            new Graph(3, new(0, 1, long.MaxValue - 1), new(1, 2, 1)), 0, 2));
        Throws<ArgumentOutOfRangeException>(() => new Graph(0));
        Throws<ArgumentOutOfRangeException>(() => new Graph(2, new Link(0, 1, -1)));
        Throws<ArgumentOutOfRangeException>(() => new Graph(2, new Link(0, 1, long.MaxValue)));
        Throws<ArgumentOutOfRangeException>(() => new Graph(2, new Link(0, 2, 1)));
        Throws<ArgumentOutOfRangeException>(() => Routes.Dijkstra(single, -1, 0));
        Throws<ArgumentOutOfRangeException>(() => Routes.Bfs(single, 0, 1));
        Throws<ArgumentNullException>(() => Routes.Dijkstra(null!, 0, 0));

        var random = new Random(20261007);
        for (int sample = 0; sample < 80; sample++)
        {
            int n = random.Next(2, 9);
            var links = new List<Link>();
            for (int from = 0; from < n; from++)
                for (int to = 0; to < n; to++)
                    if (random.Next(4) == 0) links.Add(new(from, to, random.Next(0, 8)));
            var graph = new Graph(n, links.ToArray());
            var unit = new Graph(n, links.Select(link => link with { Cost = 1 }).ToArray());
            for (int source = 0; source < n; source++)
                for (int target = 0; target < n; target++)
                {
                    Compare(graph, source, target);
                    Compare(unit, source, target);
                    Compare(unit, source, target, true);
                }
        }
        Console.WriteLine($"PASS: {queries} oracle/path comparisons plus deterministic boundary and rejection checks.");
    }
}
```

</details>

The command prints a `PASS` line after the oracle/path comparisons and rejection checks. If it fails, first read which contract was violated: a non-unit graph is an invalid BFS input, while a weighted target returning 10 instead of 3 is an algorithm defect. An `OverflowException` reports a reached candidate outside the stated range; silently wrapping that sum could create a false negative priority.

Pause - 10 minutes away from the screen.

## 6. Controlled experiment: less work can answer the wrong question

**Experiment · 45 minutes.** Predict counts, run `--experiment`, then change one cost or adjacency order. **Done when:** you can distinguish an observed counter from a complexity bound and a latency claim.

Use a directed chain with n nodes, edges `0 -> 1 -> ... -> n-1`, plus a direct edge `0 -> n-1` stored first. For n=64, 256 and 1024, keep the topology and target fixed within each pair. In the unit case every edge costs 1. In the weighted case only the direct edge changes to `2*n`; the chain edges stay 1. Compare Dijkstra on the weighted graph with BFS on an explicit unit-cost projection, then evaluate the BFS path on the original graph.

**Hypothesis:** projection-BFS does little work but minimizes the wrong objective for the weighted graph. Dijkstra must process the chain to certify its cheaper route. These are deterministic operation counts, not a timing benchmark. `Settled` counts current dequeues, including the target; `Scanned` counts examined outgoing edges; `Stale` counts discarded outdated entries. They exclude graph creation, array initialization, path reversal, heap comparison counts and SQL/API work.

Predict the four n=64 rows and explain why unit-cost Dijkstra may process one more node than BFS.

<details>
<summary>Answer</summary>

| Mode | Algorithm | Result | Cost in original graph | Settled | Scanned | Stale |
|---|---|---|---|---|---|---|
| Unit | BFS | 1 edge | 1 | 2 | 2 | 0 |
| Unit | Dijkstra | Cost 1 | 1 | 3 | 3 | 0 |
| Weighted projection | BFS | 1 edge | 128 | 2 | 2 | 0 |
| Weighted | Dijkstra | Cost 63 | 63 | 64 | 64 | 0 |

BFS sees the direct edge first and queues the target before node 1. Dijkstra's two candidates have equal cost 1, so its `(cost,node ID)` priority removes node 1 before node 63. Node 1 scans another edge before the target is removed. In the weighted case the target stays at 128 until the chain improves it to 63. The old target entry is still in the heap at return, so `Stale=0` does not mean no stale entries were created. The separate unreachable-target test drains an old entry and verifies the stale-skip branch.

</details>

`LessonLab/Experiment.cs`, the full generator and CSV writer:

```csharp
public static class Experiment
{
    public static void Run()
    {
        Console.WriteLine("n,mode,algorithm,result,originalCost,settled,scanned,stale");
        foreach (int n in new[] { 64, 256, 1024 })
        {
            var unit = new List<Link> { new(0, n - 1, 1) };
            var weighted = new List<Link> { new(0, n - 1, 2L * n) };
            for (int i = 0; i < n - 1; i++)
            {
                unit.Add(new(i, i + 1, 1));
                weighted.Add(new(i, i + 1, 1));
            }
            var unitGraph = new Graph(n, unit.ToArray());
            var weightedGraph = new Graph(n, weighted.ToArray());
            Print(n, "unit", "BFS", Routes.Bfs(unitGraph, 0, n - 1), unitGraph);
            Print(n, "unit", "Dijkstra", Routes.Dijkstra(unitGraph, 0, n - 1), unitGraph);
            // Explicitly changes the objective to fewest edges, not weighted cost.
            Print(n, "weighted-projection", "BFS", Routes.Bfs(unitGraph, 0, n - 1), weightedGraph);
            Print(n, "weighted", "Dijkstra", Routes.Dijkstra(weightedGraph, 0, n - 1), weightedGraph);
        }
    }

    private static void Print(int n, string mode, string algorithm, Route route, Graph original)
    {
        Console.WriteLine($"{n},{mode},{algorithm},{route.Distance},{Checks.PathCost(original, route.Path)}," +
                          $"{route.Settled},{route.Scanned},{route.Stale}");
    }
}
```

For n=256 and 1024, weighted Dijkstra's route costs 255 and 1023, respectively; projection-BFS's original costs are 512 and 2048. Dijkstra settles n nodes and scans n edges in this topology. Run the command to compare these predictions with your output.

Variation: change the direct weighted edge to 0, then separately restore its cost and put that edge last in the adjacency list. Predict distance and counts before running.

<details>
<summary>Answer</summary>

At direct cost 0, Dijkstra removes the target immediately after the source: distance 0, settled 2, scanned 2. BFS on the unit projection still chooses one edge; evaluating that path on the changed original also gives 0, coincidentally matching the weighted optimum. This does not validate BFS for general mixed weights.

With the direct edge stored last in the unit graph, BFS queues node 1 first and then the target. It settles 3 nodes and scans 3 edges; the minimum edge count remains 1. Dijkstra's tuple ordering keeps its unit-case counts at 3/3. The weighted-case optimum and n/n counters stay unchanged. Adjacency order can alter work and which tied route is returned without changing the optimal distance.

</details>

**Interpretation limits:** these observations verify this workload and these counters. They do not rank elapsed time, GC pressure, heap memory peaks or service p99. A larger n alone is not a representative road map: real graphs have branches, parallel routes, different degree distributions and many queries. To study elapsed time, separately fix topology and valid objective, exclude setup deliberately, warm up the runtime, repeat measurements and report variation. Do not use a fast answer to a different objective as the performance baseline.

Pause - 10 minutes away from the screen.

## 7. Transfer: a route constraint changes the state

**Changed-context exercise · 35 minutes.** Solve a budgeted-route request and show why keeping one distance per location loses information. **Done when:** you can state the new state, transitions and acceptance condition.

A warehouse can cross at most one paid corridor. Minimize travel time subject to this limit. The directed connections are S to X costing 1 second with one paid crossing, S to Y costing 2 with none, Y to X costing 0 with none, and X to T costing 1 with one paid crossing. May Dijkstra retain only the cheapest time to X and discard every slower arrival there? Design a C# solution using the existing solver, and state the answer for this graph.

<details>
<summary>Answer</summary>

No. The fastest arrival at X costs 1 but has already used the paid crossing, so it cannot continue to T. The arrival through Y costs 2 and retains the allowance; it reaches T at total time 3. Store state `(location, usedPaid)` rather than location alone. For a budget K, encode it as `location*(K+1)+usedPaid`. An edge consuming p crossings connects `(u,k)` to `(v,k+p)` only when `k+p <= K`; its weight is travel seconds, still nonnegative. This expanded graph has `(K+1)*V` states and at most `(K+1)*E` edges, so a large budget has a real memory cost.

Add a synthetic target with zero-cost edges from all allowed states at T. The existing Dijkstra then returns the minimum over those states, and the last synthetic node can be omitted from the displayed path. The full concrete instance is:

```csharp
// IDs: S0=0,S1=1,X0=2,X1=3,Y0=4,Y1=5,T0=6,T1=7,Goal=8.
var constrained = new Graph(9,
    new(0, 3, 1),                 // S0 -> X1: consume one paid crossing.
    new(0, 4, 2), new(1, 5, 2),  // S -> Y: no paid crossing.
    new(4, 2, 0), new(5, 3, 0),  // Y -> X: no paid crossing.
    new(2, 7, 1),                 // X0 -> T1: consume one paid crossing.
    new(6, 8, 0), new(7, 8, 0)); // Allowed T states -> synthetic goal.
Route answer = Routes.Dijkstra(constrained, 0, 8);
Console.WriteLine($"cost={answer.Distance}, states={string.Join("->", answer.Path)}");
// cost=3, states=0->4->2->7->8
```

This is a graph-model extension, not a change to Dijkstra's proof. The cheapest location-only label was insufficient because future legal moves depended on the budget already spent. For K=0, no consuming edge is allowed; for unreachable allowed target states, the synthetic target remains unreachable. Without a paid-crossing constraint, the original fastest route costs 2 via S-X-T.

</details>

## 8. Synthesis and next question

**Synthesis · 45 minutes.** Write a short decision note covering the objective, invariant, queue policy, numeric range and what the experiment cannot establish. **Done when:** the note rejects a wrong strategy using a counterexample and names one remaining question.

Use this final prompt: a teammate says, “Both algorithms find a path; BFS visited fewer nodes, so deploy BFS for travel seconds.” Respond in five or six sentences using today's evidence. Then choose one recall question to revisit: why Dijkstra can finalize a node, why stale entries exist, or why a route constraint expands the state.

<details>
<summary>Answer</summary>

BFS minimizes edge count; travel seconds require minimizing a weighted sum. The direct route at cost 10 versus a three-edge route at cost 3 is a counterexample to using FIFO layers for that objective. Dijkstra finalizes a current minimum label because nonnegative suffixes cannot make an unfinished route cheaper. Our lazy heap can hold multiple entries for one node, so stale entries must be skipped before processing or stopping. The experiment shows less counted work can solve a different problem; it does not establish latency or memory behavior in production. I would use the weighted solver on a versioned graph and next investigate whether time-dependent travel estimates require a richer model.

</details>

The model to retain is: choose the objective and state first, then justify the frontier order and stopping rule. BFS and Dijkstra share distance/parent arrays but certify those distances at different moments. The next question is how algorithm choice changes when a model assumption changes, such as negative costs or a useful lower estimate of the remaining route.

Sources are linked where their claims are used. The [OSRM source](https://github.com/Project-OSRM/osrm-backend/blob/4f3ee609ec1af40eb1f445c6706cfa5beb04c990/include/engine/routing_algorithms/routing_base_ch.hpp) is credited to Project OSRM contributors under BSD-2-Clause; we link and analyze it without copying its code. All C# here is original MIT teaching code; original lesson prose is CC BY 4.0.

<!-- LESSON_NAVIGATION_START -->
## Related reading

- [Lesson 02 - Boundary search](../boundary-search/lesson.md) - Recall how an invariant and a precondition justify a stopping rule.
- [C# lab guide](../../labs/shortest-paths/dotnet/README.md) - SDK setup, correctness checks, experiment and source downloads.

---

[← Previous: Lesson 02 - Boundary search with binary search and time-window counts](../boundary-search/lesson.md) · [All lessons](../../README.md)
<!-- LESSON_NAVIGATION_END -->
