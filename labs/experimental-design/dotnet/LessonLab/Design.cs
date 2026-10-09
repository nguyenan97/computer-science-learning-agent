public sealed record Unit(string Id, int Y0, int Y1);
public sealed record Pair(Unit Left, Unit Right);
public sealed record Seen(string LeftId, string RightId, bool LeftTreated,
    int LeftOutcome, int RightOutcome);
public sealed record Tail(int Extreme, int Total)
{
    public double P => (double)Extreme / Total;
}

public static class Design
{
    public static void Validate(Pair[] pairs)
    {
        if (pairs.Length is < 1 or > 10)
            throw new ArgumentOutOfRangeException(nameof(pairs));
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var u in pairs.SelectMany(p => new[] { p.Left, p.Right }))
            if (string.IsNullOrWhiteSpace(u.Id) || !ids.Add(u.Id) ||
                u.Y0 is < 0 or > 10000 || u.Y1 is < 0 or > 10000)
                throw new ArgumentException("Invalid unit, outcome or repeated ID.");
    }

    public static Seen[] Observe(Pair[] pairs, int mask)
    {
        Validate(pairs);
        if (mask < 0 || mask >= (1 << pairs.Length))
            throw new ArgumentOutOfRangeException(nameof(mask));
        return pairs.Select((p, b) =>
        {
            bool left = (mask & (1 << b)) != 0;
            return new Seen(p.Left.Id, p.Right.Id, left,
                left ? p.Left.Y1 : p.Left.Y0,
                left ? p.Right.Y0 : p.Right.Y1);
        }).ToArray();
    }

    public static long[] Differences(Seen[] seen)
    {
        if (seen.Length is < 1 or > 10)
            throw new ArgumentOutOfRangeException(nameof(seen));
        var ids = new HashSet<string>(StringComparer.Ordinal);
        foreach (var s in seen)
            if (string.IsNullOrWhiteSpace(s.LeftId) || !ids.Add(s.LeftId) ||
                string.IsNullOrWhiteSpace(s.RightId) || !ids.Add(s.RightId) ||
                s.LeftOutcome is < 0 or > 10000 || s.RightOutcome is < 0 or > 10000)
                throw new ArgumentException("Invalid observed record.");
        return seen.Select(s => s.LeftTreated
            ? (long)s.LeftOutcome - s.RightOutcome
            : (long)s.RightOutcome - s.LeftOutcome).ToArray();
    }

    public static double Estimate(Seen[] seen) =>
        (double)Differences(seen).Sum() / seen.Length;

    // Only a synthetic oracle can see both potential outcomes.
    public static double Oracle(Pair[] pairs)
    {
        Validate(pairs);
        return pairs.SelectMany(p => new[] { p.Left, p.Right })
            .Average(u => (double)u.Y1 - u.Y0);
    }

    public static double[] Distribution(Pair[] pairs)
    {
        Validate(pairs);
        return Enumerable.Range(0, 1 << pairs.Length)
            .Select(mask => Estimate(Observe(pairs, mask))).ToArray();
    }

    public static Tail SharpNull(Seen[] seen)
    {
        long[] d = Differences(seen);
        long observed = Math.Abs(d.Sum());
        int extreme = 0, total = 1 << d.Length;
        for (int mask = 0; mask < total; mask++)
        {
            long sum = 0;
            for (int b = 0; b < d.Length; b++)
                sum += (mask & (1 << b)) == 0 ? d[b] : -d[b];
            if (Math.Abs(sum) >= observed) extreme++;
        }
        return new Tail(extreme, total);
    }
}
