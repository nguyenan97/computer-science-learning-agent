public static class Checks
{
    static void Require(bool condition) { if (!condition) throw new Exception("Check failed."); }
    static void Reject(Action action)
    {
        try { action(); } catch (ArgumentException) { return; }
        throw new Exception("Expected rejection.");
    }
    // Independent 2x2 table indexed by actual and prediction; no Count call.
    static Matrix Oracle(Ticket[] rows, Rule rule)
    {
        var cells = new long[2, 2];
        foreach (var x in rows) cells[x.Late ? 1 : 0, x.Risk >= rule.Threshold ? 1 : 0]++;
        return new(cells[1, 1], cells[0, 1], cells[1, 0], cells[0, 0]);
    }
    public static void Run()
    {
        int fits = 0;
        // All ordered datasets of length 1-4, risks 0-2, labels 0/1.
        for (int n = 1; n <= 4; n++)
        for (int code = 0; code < (int)Math.Pow(6, n); code++)
        {
            int state = code;
            var rows = new Ticket[n];
            for (int i = 0; i < n; i++)
            {
                int value = state % 6; state /= 6;
                rows[i] = new($"id{i}", $"group{i}", value / 2, value % 2 == 1);
            }
            foreach (int missedCost in new[] { 1, 4 })
            {
                // Reverse enumeration, direct per-row loss; no Fit/Count/Cost.
                int expected = -1; long minimum = long.MaxValue;
                for (int t = 10; t >= 0; t--)
                {
                    long loss = rows.Sum(x => x.Risk >= t
                        ? (x.Late ? 0L : 1L) : (x.Late ? missedCost : 0L));
                    if (loss < minimum) { minimum = loss; expected = t; }
                    var rule = new Rule("oracle", t);
                    Require(Evaluation.Count(rows, rule) == Oracle(rows, rule));
                }
                Require(Evaluation.Fit(rows, missedCost).Threshold == expected);
                fits++;
            }
        }
        var sets = Data.Split(); Evaluation.Disjoint(sets);
        var candidates = Evaluation.Candidates(sets[0]);
        Require(candidates.Select(x => x.Threshold).SequenceEqual(new[] { 10, 7, 8, 5 }));
        var selected = Evaluation.Select(candidates, sets[1], 4);
        Require(selected.Threshold == 5);
        Require(Evaluation.Count(sets[2], selected) == new Matrix(2, 3, 1, 4));
        Require(Evaluation.Count(sets[2], candidates[0]).Precision is null);
        Require(Evaluation.Count([new("z", "Z", 9, false)], new("zero", 10)).Recall is null);
        Require(Evaluation.Majority([new("a", "A", 0, true), new("b", "B", 9, false)]).Threshold == 10);
        Require(Evaluation.Select([new("first", 10), new("second", 10)], sets[1], 4).Name == "first");
        var flippedTest = sets[2].Select(x => x with { Late = !x.Late }).ToArray();
        Evaluation.Disjoint(sets[0], sets[1], flippedTest);
        Require(Evaluation.Select(candidates, sets[1], 4) == selected);
        // Risk 0/9 and all labels also exercise full-domain boundaries.
        foreach (int risk in new[] { 0, 9 }) foreach (bool y in new[] { false, true })
            Require(Evaluation.Fit([new("edge", "edge", risk, y)], 4).Threshold == (y ? risk : 10));
        Reject(() => Evaluation.Fit([], 4));
        Reject(() => Evaluation.Fit(sets[0], 0));
        Reject(() => Evaluation.Count([new("bad", "G", 10, false)], selected));
        Reject(() => Evaluation.Count([new("bad", "G", 0, false)], new("bad", 11)));
        Reject(() => Evaluation.Count([new("x", "G", 0, false), new("x", "H", 1, true)], selected));
        Reject(() => Evaluation.Disjoint(sets[0], [sets[0][0] with { Id = "other" }]));
        Reject(() => Evaluation.Disjoint(sets[0], [sets[0][0] with { Group = "other" }]));
        Console.WriteLine($"PASS: {fits} fits; independent confusion tables; split/tie/boundary guards.");
    }
}
