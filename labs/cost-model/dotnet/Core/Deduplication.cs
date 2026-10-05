namespace CostModel;

public sealed record OrderCount(string Id, int Count);

// Contract: non-null IDs, ordinal equality, first-occurrence order, unchanged input.
public static class Deduplication
{
    public static List<string> Scan(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var result = new List<string>();
        foreach (string value in values)
        {
            RejectNull(value);
            if (!result.Contains(value)) result.Add(value);
        }
        return result;
    }

    public static List<string> Hash(IReadOnlyList<string> values,
        IEqualityComparer<string>? comparer = null)
    {
        ArgumentNullException.ThrowIfNull(values);
        var seen = new HashSet<string>(comparer ?? StringComparer.Ordinal);
        var result = new List<string>();
        foreach (string value in values)
        {
            RejectNull(value);
            // Add is false for an existing equal ID; no separate Contains lookup.
            if (seen.Add(value)) result.Add(value);
        }
        return result;
    }

    public static List<OrderCount> DuplicateSummary(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var counts = new Dictionary<string, int>(StringComparer.Ordinal);
        var order = new List<string>();
        foreach (string value in values)
        {
            RejectNull(value);
            if (counts.TryGetValue(value, out int count)) counts[value] = count + 1;
            else { counts.Add(value, 1); order.Add(value); }
        }
        var result = new List<OrderCount>();
        foreach (string id in order)
            if (counts[id] > 1) result.Add(new OrderCount(id, counts[id]));
        return result;
    }

    // Explicit equality-count model; do not benchmark this instrumented method.
    public static (List<string> Result, long Comparisons) CountScan(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var result = new List<string>();
        long comparisons = 0;
        foreach (string value in values)
        {
            RejectNull(value);
            bool found = false;
            foreach (string previous in result)
            {
                comparisons++;
                if (StringComparer.Ordinal.Equals(previous, value)) { found = true; break; }
            }
            if (!found) result.Add(value);
        }
        return (result, comparisons);
    }

    private static void RejectNull(string? value)
    {
        if (value is null) throw new ArgumentException("Order IDs must not be null.");
    }

    // Count only calls in the explicit model, not hash/equality/resize work.
    public static (List<string> Result, int AddCalls) CountHash(IReadOnlyList<string> values)
    {
        ArgumentNullException.ThrowIfNull(values);
        var result = new List<string>();
        var seen = new HashSet<string>(StringComparer.Ordinal);
        int calls = 0;
        foreach (string value in values)
        {
            RejectNull(value);
            calls++;
            if (seen.Add(value)) result.Add(value);
        }
        return (result, calls);
    }
}

public static class Dataset
{
    public static string[] Make(int n, int distinct)
    {
        if (n <= 0 || distinct <= 0 || distinct > n) throw new ArgumentOutOfRangeException();
        return Enumerable.Range(0, n).Select(i => $"ORD-{i % distinct:D8}").ToArray();
    }
}
