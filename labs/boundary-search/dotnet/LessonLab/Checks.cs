using System.Collections;

namespace BoundarySearchLab;

public static class Checks
{
    public static int Run()
    {
        long[] values = [10, 10, 20, 30, 30, 40];
        (string Name, Action Body)[] checks =
        [
            ("empty boundary and window", () =>
            {
                Equal(0, BoundarySearch.LowerBound([], 4));
                Equal(0, BoundarySearch.CountWindow([], 10, 30));
            }),
            ("first duplicate", () => Equal(3, BoundarySearch.LowerBound(values, 30))),
            ("missing endpoint", () => Equal(2, BoundarySearch.LowerBound(values, 11))),
            ("before minimum and after maximum", () =>
            {
                Equal(0, BoundarySearch.LowerBound(values, 0));
                Equal(values.Length, BoundarySearch.LowerBound(values, 41));
            }),
            ("negative keys and extreme longs", () =>
            {
                long[] extremes = [long.MinValue, -10, -10, 0, long.MaxValue];
                Equal(0, BoundarySearch.LowerBound(extremes, long.MinValue));
                Equal(1, BoundarySearch.LowerBound(extremes, -10));
                Equal(3, BoundarySearch.LowerBound(extremes, -1));
                Equal(4, BoundarySearch.LowerBound(extremes, long.MaxValue));
                Equal(4, BoundarySearch.CountWindow(extremes, long.MinValue, long.MaxValue));
            }),
            ("duplicate start included and end excluded", () =>
                Equal(3, BoundarySearch.CountWindow(values, 10, 30))),
            ("equal endpoints", () => Equal(0, BoundarySearch.CountWindow(values, 30, 30))),
            ("missing window endpoints", () => Equal(3, BoundarySearch.CountWindow(values, 11, 39))),
            ("outside windows", () =>
            {
                Equal(0, BoundarySearch.CountWindow(values, -10, 0));
                Equal(0, BoundarySearch.CountWindow(values, 41, 50));
            }),
            ("reversed endpoints rejected", () =>
                Throws<ArgumentException>(() => BoundarySearch.CountWindow(values, 30, 10))),
            ("input preserved", () =>
            {
                long[] before = [.. values];
                BoundarySearch.LowerBound(values, 30);
                BoundarySearch.CountWindow(values, 10, 30);
                if (!values.SequenceEqual(before)) throw new InvalidOperationException("Input changed");
            }),
            ("framework match and missing-value encoding", () =>
            {
                int match = Array.BinarySearch(values, 30L);
                if (match < 0 || values[match] != 30) throw new InvalidOperationException("Expected a matching value");
                List<long> list = [.. values];
                foreach (long target in new long[] { 0, 11, 41 })
                {
                    int arrayResult = Array.BinarySearch(values, target);
                    int listResult = list.BinarySearch(target);
                    if (arrayResult >= 0 || listResult >= 0) throw new InvalidOperationException("Target is absent");
                    Equal(BoundarySearch.LowerBound(values, target), ~arrayResult);
                    Equal(BoundarySearch.LowerBound(values, target), ~listResult);
                }
            }),
            ("null rejected", () =>
            {
                Throws<ArgumentNullException>(() => BoundarySearch.LowerBound(null!, 0));
                Throws<ArgumentNullException>(() => BoundarySearch.CountWindow(null!, 0, 1));
            }),
            ("large logical array and overflow-safe midpoint", () =>
            {
                var logical = new LogicalSequence();
                Equal(int.MaxValue - 1, BoundarySearch.LowerBound(logical, 2L * (int.MaxValue - 1)));
                if (logical.Reads > 31) throw new InvalidOperationException("Too many element reads");
            }),
            ("element reads stay logarithmic", () =>
            {
                foreach (int n in new[] { 8, 1024, 65536 })
                {
                    var counted = new CountedSequence(n);
                    Equal(n / 2, BoundarySearch.LowerBound(counted, n));
                    if (counted.Reads > Math.Log2(n) + 1) throw new InvalidOperationException($"Too many reads for {n}");
                }
            }),
            ("records searched by key", () =>
            {
                Event[] events = [new(10, "A"), new(20, "B"), new(20, "C"), new(30, "D")];
                Equal(1, RecordSearch.LowerBound(events, 20, e => e.Timestamp));
                Equal(3, RecordSearch.LowerBound(events, 30, e => e.Timestamp));
                Equal(4, RecordSearch.LowerBound(events, 31, e => e.Timestamp));
            }),
            ("exhaustive small arrays against scan oracle", CheckSmallArrays)
        ];

        int failures = 0;
        foreach (var check in checks)
        {
            try
            {
                check.Body();
                Console.WriteLine($"PASS {check.Name}");
            }
            catch (Exception exception)
            {
                failures++;
                Console.Error.WriteLine($"FAIL {check.Name}: {exception.Message}");
            }
        }
        Console.WriteLine($"{checks.Length - failures}/{checks.Length} checks passed");
        return failures == 0 ? 0 : 1;
    }

    private static void CheckSmallArrays()
    {
        for (int length = 0; length <= 5; length++)
        {
            int variants = 1;
            for (int i = 0; i < length; i++) variants *= 3;
            for (int variant = 0; variant < variants; variant++)
            {
                long[] values = new long[length];
                int digits = variant;
                for (int i = 0; i < length; i++)
                {
                    values[i] = digits % 3 - 1;
                    digits /= 3;
                }
                Array.Sort(values);
                for (long start = -2; start <= 2; start++)
                {
                    Equal(values.Count(value => value < start), BoundarySearch.LowerBound(values, start));
                    for (long end = start; end <= 2; end++)
                        Equal(values.Count(value => start <= value && value < end),
                            BoundarySearch.CountWindow(values, start, end));
                }
            }
        }
    }

    private static void Equal(int expected, int actual)
    {
        if (expected != actual) throw new InvalidOperationException($"Expected {expected}, got {actual}");
    }

    private static void Throws<TException>(Action action) where TException : Exception
    {
        try { action(); }
        catch (TException) { return; }
        throw new InvalidOperationException($"Expected {typeof(TException).Name}");
    }

    private sealed class LogicalSequence : IReadOnlyList<long>
    {
        public int Count => int.MaxValue;
        public int Reads { get; private set; }
        public long this[int index]
        {
            get
            {
                if ((uint)index >= (uint)Count) throw new ArgumentOutOfRangeException(nameof(index));
                Reads++;
                return 2L * index;
            }
        }
        public IEnumerator<long> GetEnumerator() => throw new NotSupportedException("Use indexed access");
        IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
    }
}
