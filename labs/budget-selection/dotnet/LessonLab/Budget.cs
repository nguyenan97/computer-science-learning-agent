// Original MIT teaching code. No PostgreSQL or textbook code is copied.
using System.Numerics;

public readonly record struct Job(string Id, int Cost, long Value);
public sealed record Choice(long Value, int Cost, int[] Indices, long Work, long RatioComparisons = 0);

public static class Budget
{
    public const long MaxCells = 2_000_000;

    public static void Validate(Job[] jobs, int capacity)
    {
        ArgumentNullException.ThrowIfNull(jobs);
        if (capacity < 0) throw new ArgumentOutOfRangeException(nameof(capacity));
        var ids = new HashSet<string>(StringComparer.Ordinal);
        long total = 0;
        foreach (var job in jobs)
        {
            if (string.IsNullOrWhiteSpace(job.Id) || !ids.Add(job.Id))
                throw new ArgumentException("IDs must be nonempty and unique (ordinal).", nameof(jobs));
            if (job.Cost <= 0 || job.Value < 0)
                throw new ArgumentException("Costs must be positive; values nonnegative.", nameof(jobs));
            total = checked(total + job.Value);
        }
    }

    public static Choice Exact(Job[] jobs, int capacity)
    {
        Validate(jobs, capacity);
        long cells = (jobs.Length + 1L) * (capacity + 1L);
        if (cells > MaxCells)
            throw new ArgumentOutOfRangeException(nameof(capacity), "DP table exceeds the lab cell limit.");
        var best = new long[jobs.Length + 1, capacity + 1];
        long work = 0;
        for (int i = 1; i <= jobs.Length; i++)
        {
            Job job = jobs[i - 1];
            for (int c = 0; c <= capacity; c++)
            {
                work++;
                best[i, c] = best[i - 1, c];
                if (job.Cost <= c)
                    best[i, c] = Math.Max(best[i, c], checked(best[i - 1, c - job.Cost] + job.Value));
            }
        }
        var selected = new List<int>();
        int remaining = capacity;
        for (int i = jobs.Length; i > 0; i--)
        {
            if (best[i, remaining] == best[i - 1, remaining]) continue;
            selected.Add(i - 1);
            remaining -= jobs[i - 1].Cost;
        }
        selected.Reverse();
        return new Choice(best[jobs.Length, capacity], capacity - remaining, selected.ToArray(), work);
    }

    public static long ExactValueRolling(Job[] jobs, int capacity)
    {
        Validate(jobs, capacity);
        if (capacity + 1L > MaxCells)
            throw new ArgumentOutOfRangeException(nameof(capacity), "Rolling array exceeds the lab cell limit.");
        var best = new long[capacity + 1];
        foreach (var job in jobs)
            for (int c = capacity; c >= job.Cost; c--)
                best[c] = Math.Max(best[c], checked(best[c - job.Cost] + job.Value));
        return best[capacity];
    }

    public static Choice DensityGreedy(Job[] jobs, int capacity) => Density(jobs, capacity, false);
    public static Choice HalfApprox(Job[] jobs, int capacity) => Density(jobs, capacity, true);

    private static Choice Density(Job[] jobs, int capacity, bool protectSingle)
    {
        Validate(jobs, capacity);
        var order = Enumerable.Range(0, jobs.Length).Where(i => jobs[i].Cost <= capacity).ToList();
        long comparisons = 0;
        order.Sort((a, b) =>
        {
            comparisons++;
            // Descending value/cost without floating-point rounding or long overflow.
            int comparison = ((BigInteger)jobs[b].Value * jobs[a].Cost)
                .CompareTo((BigInteger)jobs[a].Value * jobs[b].Cost);
            return comparison != 0 ? comparison : a.CompareTo(b);
        });
        var selected = new List<int>();
        int used = 0, bestSingle = -1;
        long value = 0, work = 0;
        foreach (int index in order)
        {
            work++;
            if (bestSingle < 0 || jobs[index].Value > jobs[bestSingle].Value) bestSingle = index;
            if (jobs[index].Cost > capacity - used) continue;
            selected.Add(index);
            used += jobs[index].Cost;
            value = checked(value + jobs[index].Value);
        }
        if (protectSingle && bestSingle >= 0 && jobs[bestSingle].Value > value)
            return new Choice(jobs[bestSingle].Value, jobs[bestSingle].Cost, [bestSingle], work, comparisons);
        selected.Sort();
        return new Choice(value, used, selected.ToArray(), work, comparisons);
    }
}
