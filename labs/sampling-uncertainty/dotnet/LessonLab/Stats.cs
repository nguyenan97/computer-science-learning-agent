// Original MIT teaching code, derived from the score inequality, not copied from SciPy.
using System.Numerics;

public readonly record struct Interval(double Low, double High)
{
    public double Width => High - Low;
    public bool Contains(double p) => Low <= p && p <= High;
}

public static class Stats
{
    public const double Z = 1.959963984540054; // Central 95% of a standard normal distribution.
    private static void Validate(int k, int n)
    {
        if (n < 1 || n > 10000 || k < 0 || k > n) throw new ArgumentOutOfRangeException(nameof(n));
    }
    public static Interval Wilson(int k, int n)
    {
        Validate(k, n);
        double h = (double)k / n, z2 = Z * Z, denominator = 1 + z2 / n;
        double center = (h + z2 / (2 * n)) / denominator;
        double radius = Z * Math.Sqrt(h * (1 - h) / n + z2 / (4 * n * n)) / denominator;
        return new Interval(k == 0 ? 0 : center - radius, k == n ? 1 : center + radius);
    }
    public static Interval Wald(int k, int n)
    {
        Validate(k, n);
        double h = (double)k / n, radius = Z * Math.Sqrt(h * (1 - h) / n);
        return new Interval(Math.Max(0, h - radius), Math.Min(1, h + radius));
    }
    public static BigInteger[] BinomialWeights(int n, int a, int b)
    {
        if (n < 1 || n > 320 || a < 0 || a > b || b < 1 || b > 50)
            throw new ArgumentOutOfRangeException(nameof(n));
        var weights = new BigInteger[n + 1]; BigInteger choose = 1;
        for (int k = 0; k <= n; k++)
        {
            weights[k] = choose * BigInteger.Pow(a, k) * BigInteger.Pow(b - a, n - k);
            if (k < n) choose = choose * (n - k) / (k + 1);
        }
        return weights; // Exact numerator; common denominator is b^n.
    }
    public static double Coverage(int n, int a, int b, Func<int, int, Interval> method, int copies = 1)
    {
        if (copies < 1 || (long)n * copies > 10000) throw new ArgumentOutOfRangeException(nameof(copies));
        var weights = BinomialWeights(n, a, b); BigInteger covered = 0;
        double p = (double)a / b;
        for (int k = 0; k <= n; k++)
            if (method(k * copies, n * copies).Contains(p)) covered += weights[k];
        // Exact integer sums; membership uses double. Scale the ratio before conversion,
        // so large denominators never overflow to infinity. Truncation is below 2^-53.
        BigInteger scale = BigInteger.One << 53;
        return (double)(covered * scale / BigInteger.Pow(b, n)) / (double)scale;
    }
}
