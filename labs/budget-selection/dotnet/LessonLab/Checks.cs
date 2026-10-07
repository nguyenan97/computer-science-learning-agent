using System.Numerics;

public static class Checks
{
    private static int instances;
    private static void Require(bool condition, string message)
    {
        if (!condition) throw new InvalidOperationException(message);
    }

    private static void Throws<T>(Action action) where T : Exception
    {
        try { action(); }
        catch (T) { return; }
        throw new InvalidOperationException($"Expected {typeof(T).Name}.");
    }

    private static void Feasible(Job[] jobs, int capacity, Choice result)
    {
        Require(result.Indices.Distinct().Count() == result.Indices.Length, "Reused job.");
        long cost = 0, value = 0;
        foreach (int index in result.Indices)
        {
            Require((uint)index < (uint)jobs.Length, "Invalid result index.");
            cost += jobs[index].Cost;
            value = checked(value + jobs[index].Value);
        }
        Require(cost <= capacity && cost == result.Cost && value == result.Value, "Invalid choice totals.");
    }

    private static void Compare(Job[] jobs, int capacity)
    {
        var snapshot = jobs.ToArray();
        var oracle = Oracle.Solve(jobs, capacity);
        var exact = Budget.Exact(jobs, capacity);
        var greedy = Budget.DensityGreedy(jobs, capacity);
        var approx = Budget.HalfApprox(jobs, capacity);
        foreach (var choice in new[] { oracle, exact, greedy, approx }) Feasible(jobs, capacity, choice);
        Require(exact.Value == oracle.Value, "DP differs from exhaustive optimum.");
        Require(Budget.ExactValueRolling(jobs, capacity) == oracle.Value, "Rolling DP differs from optimum.");
        Require(greedy.Value <= oracle.Value && approx.Value <= oracle.Value, "Value exceeds optimum.");
        Require(approx.Value >= greedy.Value, "Single-item protection reduced the value.");
        Require((BigInteger)2 * approx.Value >= oracle.Value, "Half guarantee violated.");
        Require(jobs.SequenceEqual(snapshot), "Input changed.");
        instances++;
    }

    public static void Run()
    {
        Compare([], 0); Compare([], 4);
        Compare([new("A", 4, 7), new("B", 3, 5), new("C", 3, 5)], 6);
        Compare([new("single", 2, 3)], 4); // An ascending rolling loop would incorrectly return 6.
        Compare([new("heavy", 100, 1000), new("zero", 1, 0), new("small", 2, 3)], 3);
        Compare([new("a", 1, 0), new("b", 2, 0)], 2);
        Compare([new("A", 1, 2), new("B", 1000, 1000)], 1000);
        Compare([new("A", 1, 2), new("B", 1000, 1000), new("C", 1000, 1000)], 2000);
        Compare([new("maximum", 1, long.MaxValue)], 1);
        Job[] close = [new("low", 1, long.MaxValue / 2), new("high", 1, long.MaxValue / 2 + 1)];
        Compare(close, 1);
        Require(Budget.DensityGreedy(close, 1).Indices.SequenceEqual(new[] { 1 }), "Rounded ratio ordering.");
        Throws<ArgumentNullException>(() => Budget.Exact(null!, 1));
        Throws<ArgumentOutOfRangeException>(() => Budget.Exact([], -1));
        Throws<ArgumentException>(() => Budget.HalfApprox([new("x", 0, 1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("x", -1, 1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("x", 1, -1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("", 1, 1)], 2));
        Throws<ArgumentException>(() => Budget.Exact([new("x", 1, 1), new("x", 2, 1)], 2));
        Throws<OverflowException>(() => Budget.Exact([new("x", 1, long.MaxValue), new("y", 1, 1)], 1));
        Throws<ArgumentOutOfRangeException>(() => Budget.Exact([new("x", 1, 1)], 1_000_000));
        Throws<ArgumentOutOfRangeException>(() => Budget.Exact([], int.MaxValue));
        Throws<ArgumentOutOfRangeException>(() => Budget.ExactValueRolling([], int.MaxValue));
        Throws<ArgumentOutOfRangeException>(() => Oracle.Solve(
            Enumerable.Range(0, 23).Select(i => new Job($"id{i}", 1, 1)).ToArray(), 1));

        // Exhaust all three-job inputs with costs 1-3, values 0-3, capacities 0-6.
        for (int encoded = 0; encoded < 12 * 12 * 12; encoded++)
        {
            var jobs = new Job[3];
            int rest = encoded;
            for (int i = 0; i < jobs.Length; i++)
            {
                int code = rest % 12; rest /= 12;
                jobs[i] = new Job($"j{i}", code / 4 + 1, code % 4);
            }
            for (int capacity = 0; capacity <= 6; capacity++) Compare(jobs, capacity);
        }
        var random = new Random(20261008);
        for (int sample = 0; sample < 120; sample++)
        {
            Job[] jobs = Enumerable.Range(0, random.Next(0, 11))
                .Select(i => new Job($"j{i}", random.Next(1, 16), random.Next(0, 31))).ToArray();
            Compare(jobs, random.Next(0, 31));
        }
        Console.WriteLine($"PASS: {instances} instances checked against exhaustive optimum, feasibility and half guarantee.");
    }
}
