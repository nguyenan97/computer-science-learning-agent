public static class Experiment
{
    public static void Run()
    {
        var sets = Data.Split();
        Evaluation.Disjoint(sets);
        var clean = Evaluation.Fit(sets[0], 4);
        var cleanResult = Evaluation.Count(sets[2], clean);
        // Deliberately invalid: Late is only known after the outcome window.
        var leaked = sets.Select(s => s.Select(x => x with
            { Risk = x.Late ? 9 : 0 }).ToArray()).ToArray();
        var invalid = Evaluation.Fit(leaked[0], 4);
        var invalidResult = Evaluation.Count(leaked[2], invalid);
        Console.WriteLine($"Feature availability: clean accuracy={cleanResult.Accuracy:F3} cost={cleanResult.Cost(4)}; leaked accuracy={invalidResult.Accuracy:F3} cost={invalidResult.Cost(4)}");

        // Same four held-out customers, four training rows and balanced labels.
        var target = Enumerable.Range(4, 4).Select(i =>
            new Ticket($"new-{i}", $"c{i}", 0, i % 2 == 1)).ToArray();
        var proper = Enumerable.Range(0, 4).Select(i =>
            new Ticket($"old-{i}", $"c{i}", 0, i % 2 == 1)).ToArray();
        var overlap = target.Select(x => x with { Id = "prior-" + x.Id }).ToArray();
        Evaluation.Disjoint(proper, target);
        double Score(Ticket[] train)
        {
            var learned = train.ToDictionary(x => x.Group, x => x.Late, StringComparer.Ordinal);
            int correct = target.Count(x =>
                (learned.TryGetValue(x.Group, out bool y) && y) == x.Late);
            return (double)correct / target.Length;
        }
        Console.WriteLine($"Customer exposure: disjoint accuracy={Score(proper):F3}; overlap accuracy={Score(overlap):F3}");
        try { Evaluation.Disjoint(overlap, target); }
        catch (ArgumentException) { Console.WriteLine("Group guard rejects overlap despite unique row IDs."); }
    }
}
