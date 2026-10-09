public static class Checks
{
    private static void Require(bool ok, string message)
    {
        if (!ok) throw new Exception(message);
    }

    private static void Invalid(Action action)
    {
        try { action(); }
        catch (ArgumentException) { return; }
        throw new Exception("Invalid input accepted.");
    }

    private static int Bits(int mask)
    {
        int n = 0;
        while (mask != 0) { n += mask & 1; mask >>= 1; }
        return n;
    }

    public static void Run()
    {
        var pairs = Experiment.Cohort();
        double[] actual = Design.Distribution(pairs);
        // Independent oracle: select 6 of 12, retain one per pair, scan arm totals.
        var independent = new List<double>();
        for (int mask = 0; mask < (1 << 12); mask++)
        {
            if (Bits(mask) != 6) continue;
            long treatment = 0, control = 0;
            bool valid = true;
            for (int b = 0; b < 6; b++)
            {
                bool left = (mask & (1 << (2 * b))) != 0;
                bool right = (mask & (1 << (2 * b + 1))) != 0;
                if (left == right) { valid = false; break; }
                var p = pairs[b];
                treatment += left ? p.Left.Y1 : p.Right.Y1;
                control += left ? p.Right.Y0 : p.Left.Y0;
            }
            if (valid) independent.Add((double)(treatment - control) / 6);
        }
        Require(independent.Count == 64, "Assignment space differs.");
        Require(actual.Order().SequenceEqual(independent.Order()), "Independent arm scan differs.");
        Require(Math.Abs(actual.Average() - Design.Oracle(pairs)) < 1e-12, "Expectation differs.");
        Require(Math.Abs(actual.Average(x => (x + 4) * (x + 4)) - 1456.0 / 36) < 1e-12,
            "Design variance differs.");
        var seen = Design.Observe(pairs, 21);
        Require(Design.Differences(seen).SequenceEqual(new long[] { -8, 4, -16, 12, -24, 20 }),
            "Trace differs.");
        Require(Design.Estimate(seen) == -2, "Estimate differs.");

        // Exhaust all 3^8 potential-outcome tables for four units in two pairs.
        for (int table = 0; table < 6561; table++)
        {
            int code = table;
            var units = new Unit[4];
            for (int i = 0; i < 4; i++)
            {
                int y0 = code % 3; code /= 3;
                int y1 = code % 3; code /= 3;
                units[i] = new Unit($"id{i}", y0, y1);
            }
            Pair[] tiny = [new(units[0], units[1]), new(units[2], units[3])];
            long sum = 0;
            for (int mask = 0; mask < 4; mask++) sum += Design.Differences(Design.Observe(tiny, mask)).Sum();
            long effects = units.Sum(u => (long)u.Y1 - u.Y0);
            Require(sum == 2 * effects, "Unbiasedness identity differs.");
        }
        var nullPairs = Experiment.Cohort(0);
        int rejections = 0;
        for (int mask = 0; mask < 64; mask++)
        {
            var tail = Design.SharpNull(Design.Observe(nullPairs, mask));
            Require(tail.Total == 64 && tail.Extreme is >= 1 and <= 64, "Tail bounds differ.");
            if (20 * tail.Extreme <= tail.Total) rejections++;
        }
        Require(rejections == 2, "Sharp-null size differs.");
        Require(Design.SharpNull(Design.Observe(nullPairs, 63)).Extreme == 2, "Inclusive tails differ.");
        var equal = new[] { new Pair(new Unit("a", 5, 5), new Unit("b", 5, 5)) };
        Require(Design.SharpNull(Design.Observe(equal, 0)).P == 1, "Zero differences differ.");
        var reversed = seen.Select(s => new Seen(s.RightId, s.LeftId, !s.LeftTreated,
            s.RightOutcome, s.LeftOutcome)).ToArray();
        Require(Design.Estimate(reversed) == Design.Estimate(seen), "Pair relabeling differs.");
        Invalid(() => Design.Observe(pairs, -1));
        Invalid(() => Design.Observe(pairs, 64));
        Invalid(() => Design.Validate([]));
        Invalid(() => Design.Validate([new Pair(pairs[0].Left, pairs[0].Left)]));
        Invalid(() => Design.Validate([new Pair(new Unit("x", -1, 2), new Unit("y", 1, 2))]));
        Invalid(() => Design.Validate(Enumerable.Repeat(equal[0], 11).ToArray()));
        Invalid(() => Design.Estimate([]));
        Invalid(() => Design.Estimate([new Seen("a", "a", true, 1, 2)]));
        Console.WriteLine("PASS: 64 independent assignments; 6561 potential tables; variance; sharp-null size 2/64; ties; validation.");
    }
}
