using System.Numerics;

public static class Checks
{
    private static void Require(bool test, string why) { if (!test) throw new Exception(why); }
    private static void Throws(Action action)
    {
        try { action(); } catch (ArgumentOutOfRangeException) { return; }
        throw new Exception("Expected argument rejection.");
    }
    // Numerical inversion of the acceptance condition, without Wilson's closed formula.
    private static Interval ScoreRoots(int k, int n)
    {
        double h = (double)k / n;
        bool Accepted(double p) => n * (h - p) * (h - p) <= Stats.Z * Stats.Z * p * (1 - p);
        double low = 0, high = 1;
        if (k != 0)
        {
            double left = 0, right = h;
            for (int i = 0; i < 80; i++) { double mid = (left + right) / 2; if (Accepted(mid)) right = mid; else left = mid; }
            low = (left + right) / 2;
        }
        if (k != n)
        {
            double left = h, right = 1;
            for (int i = 0; i < 80; i++) { double mid = (left + right) / 2; if (Accepted(mid)) left = mid; else right = mid; }
            high = (left + right) / 2;
        }
        return new Interval(low, high);
    }
    public static void Run()
    {
        int cases = 0;
        for (int n = 1; n <= 200; n++)
            for (int k = 0; k <= n; k++)
            {
                var actual = Stats.Wilson(k, n); var oracle = ScoreRoots(k, n);
                Require(Math.Abs(actual.Low - oracle.Low) < 2e-12 && Math.Abs(actual.High - oracle.High) < 2e-12, "Score inversion differs.");
                Require(actual.Low >= 0 && actual.High <= 1 && actual.Contains((double)k / n), "Invalid interval.");
                var complement = Stats.Wilson(n - k, n);
                Require(Math.Abs(actual.Low - (1 - complement.High)) < 2e-12, "Complement differs."); cases++;
            }
        var zero = Stats.Wilson(0, 20);
        Require(zero.Low == 0 && Math.Abs(zero.High - 0.1611251580528194) < 1e-12, "Zero-case fixture differs.");
        Require(Stats.Wald(0, 20).Width == 0, "Wald counterexample missing.");
        // Exhaustive binary sequences give a second, independent count of the binomial weights.
        for (int n = 1; n <= 10; n++)
        {
            var counts = new int[n + 1];
            for (uint bits = 0; bits < (1u << n); bits++) counts[BitOperations.PopCount(bits)]++;
            var weights = Stats.BinomialWeights(n, 1, 2);
            for (int k = 0; k <= n; k++) Require(weights[k] == counts[k], "Sequence oracle differs.");
        }
        foreach (int n in new[] { 20, 80, 320 })
        {
            var weights = Stats.BinomialWeights(n, 1, 5);
            Require(weights.Aggregate(BigInteger.Zero, (s, w) => s + w) == BigInteger.Pow(5, n), "Probability mass differs.");
        }
        Require(Stats.BinomialWeights(3, 1, 5).SequenceEqual(new BigInteger[] { 64, 48, 12, 1 }), "Three-draw fixture differs.");
        Require(double.IsFinite(Stats.Coverage(320, 1, 50, Stats.Wilson)), "Large denominator overflowed.");
        Require(Stats.Coverage(20, 0, 5, Stats.Wilson) == 1 && Stats.Coverage(20, 5, 5, Stats.Wilson) == 1, "Degenerate probability differs.");
        var rng = new Draws(1);
        foreach (int value in new[] { 48271, 182605794, 1291394886, 1914720637, 2078669041 })
            Require(rng.NextRaw() == value, "Generator sequence differs.");
        var same = new Draws(101); var again = new Draws(101);
        for (int i = 0; i < 100; i++) Require(same.Bernoulli(1, 5) == again.Bernoulli(1, 5), "Seed not reproducible.");
        Throws(() => Stats.Wilson(0, 0)); Throws(() => Stats.Wilson(21, 20)); Throws(() => Stats.Wilson(-1, 20));
        Throws(() => Stats.Wilson(0, 10001)); Throws(() => new Draws(0)); Throws(() => rng.Below(0));
        Throws(() => rng.Bernoulli(2, 1)); Throws(() => Stats.Coverage(20, 1, 5, Stats.Wilson, 0));
        Console.WriteLine($"PASS: {cases} score inversions; binary-sequence weights; endpoints; seed; validation.");
    }
}
