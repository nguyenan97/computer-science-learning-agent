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
