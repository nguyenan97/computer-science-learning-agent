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
