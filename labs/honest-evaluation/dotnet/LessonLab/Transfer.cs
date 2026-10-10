public static class Transfer
{
    public static void Run()
    {
        // One customer contributes four errors; another contributes one success.
        Ticket[] rows = [new("a1", "A", 0, true), new("a2", "A", 0, true),
            new("a3", "A", 0, true), new("a4", "A", 0, true), new("b1", "B", 0, false)];
        var rule = new Rule("never-alert", 10);
        var rowMatrix = Evaluation.Count(rows, rule);
        double macroCost = rows.GroupBy(x => x.Group).Average(g =>
            (double)Evaluation.Count(g.ToArray(), rule).Cost(4) / g.Count());
        if (rowMatrix.Cost(4) != 16 || Math.Abs(macroCost - 2) > 1e-12)
            throw new InvalidOperationException("Wrong unit weighting.");
        Console.WriteLine($"Row mean cost={(double)rowMatrix.Cost(4) / rows.Length:F3}; equal-customer mean cost={macroCost:F3}");
    }
}
