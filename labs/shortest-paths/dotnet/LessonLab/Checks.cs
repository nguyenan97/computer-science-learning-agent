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
