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
