using System.Globalization;

public static class Experiment
{
    public static Pair[] Cohort(int effect = -4, bool poor = false)
    {
        int[] baseline = [10, 14, 20, 28, 40, 52, 60, 76, 80, 100, 120, 144];
        Unit[] units = baseline.Select((y, i) => new Unit($"u{i}", y, y + effect)).ToArray();
        return Enumerable.Range(0, 6).Select(b => poor
            ? new Pair(units[b], units[b + 6])
            : new Pair(units[2 * b], units[2 * b + 1])).ToArray();
    }

    public static void Demo()
    {
        var pairs = Cohort();
        var seen = Design.Observe(pairs, 21);
        Console.WriteLine("pair,left_treated,left_seen,right_seen,treatment_minus_control");
        var d = Design.Differences(seen);
        for (int b = 0; b < seen.Length; b++)
            Console.WriteLine($"{b},{seen[b].LeftTreated},{seen[b].LeftOutcome},{seen[b].RightOutcome},{d[b]}");
        var p = Design.SharpNull(seen);
        Console.WriteLine($"estimate={Design.Estimate(seen):F4}; synthetic_oracle={Design.Oracle(pairs):F4}; sharp_null={p.Extreme}/{p.Total}={p.P:F4}");
    }

    public static void Run()
    {
        Console.WriteLine("effect,pairing,policy,estimate,design_mean,design_sd,min,max,sharp_null_p");
        using var csv = new StreamWriter("assignments.csv");
        csv.WriteLine("effect,pairing,mask,estimate");
        foreach (int effect in new[] { 0, -4 })
        foreach (bool poor in new[] { false, true })
        {
            var pairs = Cohort(effect, poor);
            double[] values = Design.Distribution(pairs);
            double mean = values.Average();
            double sd = Math.Sqrt(values.Average(x => (x - mean) * (x - mean)));
            string pairing = poor ? "poor" : "close";
            for (int mask = 0; mask < values.Length; mask++)
                csv.WriteLine(FormattableString.Invariant($"{effect},{pairing},{mask},{values[mask]:F8}"));
            var seen = Design.Observe(pairs, 21);
            Console.WriteLine($"{effect},{pairing},random-pair,{Design.Estimate(seen):F4},{mean:F4},{sd:F4},{values.Min():F4},{values.Max():F4},{Design.SharpNull(seen).P:F4}");
            var selected = Design.Observe(pairs, 63);
            // The randomization distribution is invalid for this deterministic policy.
            Console.WriteLine($"{effect},{pairing},select-low,{Design.Estimate(selected):F4},NA,NA,NA,NA,NA");
        }
        Console.WriteLine("# 64 equally weighted assignments per random-pair case; wrote assignments.csv; synthetic milliseconds, not measured latency");
    }
}
