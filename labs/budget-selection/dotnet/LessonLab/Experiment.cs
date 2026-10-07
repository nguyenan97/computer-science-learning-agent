using System.Globalization;

public static class Experiment
{
    public static void Run()
    {
        Console.WriteLine("case,n,capacity,algorithm,value,quality,workUnit,work,ratioComparisons");
        Case("demo", [new("A", 4, 7), new("B", 3, 5), new("C", 3, 5)], 6);
        foreach (int capacity in new[] { 10, 40, 1000 })
            Case("density-trap", [new("tiny", 1, 2), new("large", capacity, capacity)], capacity);
        foreach (int k in new[] { 4, 20, 1000 })
            Case("near-half", [new("tiny", 1, 2), new("left", k, k), new("right", k, k)], 2 * k);
        foreach (int n in new[] { 8, 12, 16 }) Case("n-scaling", Generate(n), 25);
        foreach (int capacity in new[] { 20, 40, 80 }) Case("capacity-scaling", Generate(16), capacity);
    }

    private static Job[] Generate(int n) => Enumerable.Range(0, n)
        .Select(i => new Job($"j{i}", 1 + i * 7 % 11, 1 + i * 13 % 19)).ToArray();

    private static void Case(string name, Job[] jobs, int capacity)
    {
        var exact = Budget.Exact(jobs, capacity);
        var oracle = Oracle.Solve(jobs, capacity);
        if (exact.Value != oracle.Value) throw new InvalidOperationException("Experiment oracle mismatch.");
        Print(name, jobs.Length, capacity, "Exact", exact, exact.Value, "cells");
        Print(name, jobs.Length, capacity, "Oracle", oracle, exact.Value, "subsets");
        Print(name, jobs.Length, capacity, "Density", Budget.DensityGreedy(jobs, capacity), exact.Value, "items");
        Print(name, jobs.Length, capacity, "HalfApprox", Budget.HalfApprox(jobs, capacity), exact.Value, "items");
    }

    private static void Print(string name, int n, int capacity, string algorithm, Choice choice, long optimum, string unit)
    {
        decimal quality = optimum == 0 ? 1 : (decimal)choice.Value / optimum;
        Console.WriteLine($"{name},{n},{capacity},{algorithm},{choice.Value}," +
            $"{quality.ToString("F4", CultureInfo.InvariantCulture)},{unit},{choice.Work},{choice.RatioComparisons}");
    }
}
