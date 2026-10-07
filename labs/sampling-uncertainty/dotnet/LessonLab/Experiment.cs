using System.Globalization;

public static class Experiment
{
    private const int Repetitions = 2000;
    private sealed record Result(string Case, int Units, int Records, int A, int B, string Method,
        int[] Counts, Func<int, int, Interval> Interval, int Copies = 1);
    public static void Run()
    {
        var results = new List<Result>(); var rng = new Draws(101);
        var prefix = new Dictionary<int, int[]> { [20] = new int[Repetitions], [80] = new int[Repetitions], [320] = new int[Repetitions] };
        for (int r = 0; r < Repetitions; r++)
        {
            int successes = 0;
            for (int i = 1; i <= 320; i++) { successes += rng.Bernoulli(1, 5); if (prefix.ContainsKey(i)) prefix[i][r] = successes; }
        }
        foreach (var (n, counts) in prefix)
            foreach (string method in new[] { "Wilson", "Wald" })
                results.Add(new Result("prefix", n, n, 1, 5, method, counts, method == "Wilson" ? Stats.Wilson : Stats.Wald));
        rng = new Draws(202); var rare = new int[Repetitions];
        for (int r = 0; r < Repetitions; r++) for (int i = 0; i < 20; i++) rare[r] += rng.Bernoulli(1, 50);
        results.Add(new Result("rare", 20, 20, 1, 50, "Wilson", rare, Stats.Wilson));
        results.Add(new Result("rare", 20, 20, 1, 50, "Wald", rare, Stats.Wald));
        rng = new Draws(303); var iid = new int[Repetitions]; var groups = new int[Repetitions];
        for (int r = 0; r < Repetitions; r++)
            for (int i = 0; i < 200; i++) { int x = rng.Bernoulli(1, 5); iid[r] += x; if (i < 20) groups[r] += x; }
        results.Add(new Result("iid", 200, 200, 1, 5, "Wilson", iid, Stats.Wilson));
        results.Add(new Result("cluster-naive", 20, 200, 1, 5, "Wilson", groups.Select(k => 10 * k).ToArray(), Stats.Wilson, 10));
        results.Add(new Result("cluster-unit", 20, 200, 1, 5, "Wilson", groups, Stats.Wilson));
        Console.WriteLine("case,units,records,p,method,covered,repetitions,empirical,binomial_sum,mean_width");
        foreach (var row in results)
        {
            int covered = 0; double width = 0, p = (double)row.A / row.B;
            foreach (int k in row.Counts) { var ci = row.Interval(k, row.Units * row.Copies); if (ci.Contains(p)) covered++; width += ci.Width; }
            double exact = Stats.Coverage(row.Units, row.A, row.B, row.Interval, row.Copies);
            Console.WriteLine(FormattableString.Invariant($"{row.Case},{row.Units},{row.Records},{p:F2},{row.Method},{covered},{Repetitions},{(double)covered / Repetitions:F4},{exact:F6},{width / Repetitions:F6}"));
        }
        using var csv = new StreamWriter("distribution.csv", false);
        csv.WriteLine("n,bin_left,bin_right,count,repetitions");
        foreach (var (n, counts) in prefix)
        {
            var bins = new int[20]; foreach (int k in counts) bins[Math.Min(19, k * 20 / n)]++;
            for (int b = 0; b < bins.Length; b++) csv.WriteLine(FormattableString.Invariant($"{n},{b / 20.0:F2},{(b + 1) / 20.0:F2},{bins[b]},{Repetitions}"));
        }
        Console.WriteLine("# wrote distribution.csv; seeds=101/202/303; no elapsed-time benchmark");
    }
}
