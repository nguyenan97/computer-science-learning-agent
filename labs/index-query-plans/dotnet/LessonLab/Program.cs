if (args is ["--check"]) Checks.Run();
else if (args is ["--experiment"]) Experiment.Run();
else if (args.Length == 0)
{
    using var db = new Database();
    db.Insert(Database.Generate(2000));
    Console.WriteLine($"SQLite {db.Version}");
    foreach (var layout in new[] { IndexLayout.None, IndexLayout.Thin, IndexLayout.Covering })
    {
        db.SetIndexes(layout);
        var result = db.Run(AccessPath.Auto, 1, 0, 10);
        Console.WriteLine($"{layout}: count={result.Count}, amount={result.Amount}");
        Console.WriteLine(db.Plan(AccessPath.Auto, 1, 0, 10));
    }
}
else throw new ArgumentException("Use no arguments, --check or --experiment.");
