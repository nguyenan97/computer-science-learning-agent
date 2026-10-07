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
