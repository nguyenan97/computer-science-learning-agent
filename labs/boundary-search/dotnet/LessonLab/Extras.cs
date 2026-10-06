namespace BoundarySearchLab;

public sealed class CountedSequence(int n) : IReadOnlyList<long>
{
    public int Reads { get; private set; }
    public int Count => n;

    public long this[int index]
    {
        get
        {
            if ((uint)index >= (uint)n) throw new ArgumentOutOfRangeException(nameof(index));
            Reads++;
            return index * 2L;
        }
    }

    public IEnumerator<long> GetEnumerator() => throw new NotSupportedException();
    System.Collections.IEnumerator System.Collections.IEnumerable.GetEnumerator() => GetEnumerator();
}

public sealed record Event(long Timestamp, string Id);

public static class RecordSearch
{
    public static int LowerBound<T>(IReadOnlyList<T> items, long target, Func<T, long> key)
    {
        ArgumentNullException.ThrowIfNull(items);
        ArgumentNullException.ThrowIfNull(key);
        int lo = 0, hi = items.Count;
        while (lo < hi)
        {
            int mid = lo + (hi - lo) / 2;
            if (key(items[mid]) < target)
                lo = mid + 1;
            else
                hi = mid;
        }
        return lo;
    }
}

public static class Observe
{
    public static int Run()
    {
        foreach (int n in new[] { 8, 1024, 65536 })
        {
            var values = new CountedSequence(n);
            int index = BoundarySearch.LowerBound(values, n);
            Console.WriteLine($"{n} {index} {values.Reads}");
        }

        Event[] events = [new(10, "A"), new(20, "B"), new(20, "C"), new(30, "D")];
        int left = RecordSearch.LowerBound(events, 20, e => e.Timestamp);
        int right = RecordSearch.LowerBound(events, 30, e => e.Timestamp);
        Console.WriteLine($"records: {left} {right} {right - left}");
        return 0;
    }
}
