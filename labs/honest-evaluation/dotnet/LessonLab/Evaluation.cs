// Original teaching code, MIT. Not adapted from scikit-learn.
public sealed record Ticket(string Id, string Group, int Risk, bool Late);
public sealed record Rule(string Name, int Threshold)
{
    public bool Predict(int risk) => risk >= Threshold;
}
public readonly record struct Matrix(long TP, long FP, long FN, long TN)
{
    public long N => TP + FP + FN + TN;
    public double Accuracy => (double)(TP + TN) / N;
    public double? Precision => TP + FP == 0 ? null : (double)TP / (TP + FP);
    public double? Recall => TP + FN == 0 ? null : (double)TP / (TP + FN);
    public long Cost(int missedCost) => checked(FP + missedCost * FN);
}
public static class Evaluation
{
    public static void Validate(Ticket[] rows)
    {
        if (rows.Length is < 1 or > 10000)
            throw new ArgumentException("Require 1-10000 rows.");
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var row in rows)
            if (row is null || string.IsNullOrWhiteSpace(row.Id)
                || string.IsNullOrWhiteSpace(row.Group) || row.Risk is < 0 or > 9
                || !ids.Add(row.Id))
                throw new ArgumentException("Require unique IDs, nonempty groups and risk 0-9.");
    }
    public static void Disjoint(params Ticket[][] sets)
    {
        var ids = new HashSet<string>(StringComparer.Ordinal);
        var groups = new HashSet<string>(StringComparer.Ordinal);
        foreach (var set in sets)
        {
            Validate(set);
            var localGroups = set.Select(x => x.Group).Distinct(StringComparer.Ordinal);
            if (set.Any(x => !ids.Add(x.Id)) || localGroups.Any(x => !groups.Add(x)))
                throw new ArgumentException("Overlapping row IDs or customer groups.");
        }
    }
    public static Matrix Count(Ticket[] rows, Rule rule)
    {
        Validate(rows);
        if (rule.Threshold is < 0 or > 10) throw new ArgumentException("Threshold 0-10.");
        long tp = 0, fp = 0, fn = 0, tn = 0;
        foreach (var row in rows)
        {
            bool prediction = rule.Predict(row.Risk);
            if (prediction && row.Late) tp++;
            else if (prediction) fp++;
            else if (row.Late) fn++;
            else tn++;
        }
        return new Matrix(tp, fp, fn, tn);
    }
    public static Rule Majority(Ticket[] train)
    {
        Validate(train);
        return new Rule("majority", train.Count(x => x.Late) > train.Length / 2 ? 0 : 10);
    }
    public static Rule Fit(Ticket[] train, int missedCost)
    {
        Validate(train);
        if (missedCost is < 1 or > 1000) throw new ArgumentException("FN cost 1-1000.");
        var best = new Rule($"fit-FN{missedCost}", 0);
        long bestCost = long.MaxValue;
        for (int threshold = 0; threshold <= 10; threshold++)
        {
            var candidate = new Rule(best.Name, threshold);
            long cost = Count(train, candidate).Cost(missedCost);
            // Ascending candidates plus <= implements largest-threshold ties.
            if (cost <= bestCost) { best = candidate; bestCost = cost; }
        }
        return best;
    }
    public static Rule Select(Rule[] candidates, Ticket[] validation, int missedCost)
    {
        Validate(validation);
        if (candidates.Length == 0 || missedCost is < 1 or > 1000)
            throw new ArgumentException("Require candidates and FN cost 1-1000.");
        return candidates.OrderBy(r => Count(validation, r).Cost(missedCost)).First();
    }
    public static Rule[] Candidates(Ticket[] train) =>
        [Majority(train), new Rule("fixed-rule", 7), Fit(train, 1), Fit(train, 4)];
}
