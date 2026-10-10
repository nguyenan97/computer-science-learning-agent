using CostModel;

internal static class Checks
{
    public static void Run()
    {
        int passed = 0;
        void Check(string name, Action test) { test(); passed++; Console.WriteLine($"PASS {name}"); }
        void Equal<T>(IEnumerable<T> actual, IEnumerable<T> expected)
        { if (!actual.SequenceEqual(expected)) throw new Exception("Sequence mismatch"); }
        void Throws<T>(Action action) where T : Exception
        { try { action(); } catch (T) { return; } throw new Exception($"Expected {typeof(T).Name}"); }

        Check("stable order and unchanged input", () => {
            string[] input = ["B2", "A1", "B2", "C3", "A1"]; var before = input.ToArray();
            Equal(Deduplication.Scan(input), new[] { "B2", "A1", "C3" });
            Equal(Deduplication.Hash(input), new[] { "B2", "A1", "C3" }); Equal(input, before);
        });
        Check("empty, singleton and repeated input", () => {
            foreach (var (input, expected) in new[] {
                (Array.Empty<string>(), Array.Empty<string>()),
                (new[] { "A" }, new[] { "A" }), (new[] { "A", "A", "A" }, new[] { "A" }) })
            { Equal(Deduplication.Scan(input), expected); Equal(Deduplication.Hash(input), expected); }
        });
        Check("ordinal identity and explicit alternative comparer", () => {
            string[] input = ["a", "A", "a", " a ", ""];
            Equal(Deduplication.Scan(input), new[] { "a", "A", " a ", "" });
            Equal(Deduplication.Hash(input), new[] { "a", "A", " a ", "" });
            Equal(Deduplication.Hash(input, StringComparer.OrdinalIgnoreCase), new[] { "a", " a ", "" });
        });
        Check("null policy", () => {
            Throws<ArgumentNullException>(() => Deduplication.Scan(null!));
            Throws<ArgumentNullException>(() => Deduplication.Hash(null!));
            Throws<ArgumentException>(() => Deduplication.Scan(new[] { "A", null! }));
            Throws<ArgumentException>(() => Deduplication.Hash(new[] { "A", null! }));
            Throws<ArgumentException>(() => Deduplication.DuplicateSummary(new string[] { null! }));
        });
        Check("triangular count and repeated-ID count", () => {
            foreach (int n in new[] { 1, 128, 256, 512 }) {
                var input = Dataset.Make(n, n);
                var hashModel = Deduplication.CountHash(input);
                Equal(hashModel.Result, Deduplication.Hash(input));
                if (hashModel.AddCalls != n) throw new Exception("Wrong Add-call model");
                if (Deduplication.CountScan(Dataset.Make(n, n)).Comparisons != (long)n * (n - 1) / 2)
                    throw new Exception("Wrong distinct count model");
                if (Deduplication.CountScan(Dataset.Make(n, 1)).Comparisons != n - 1)
                    throw new Exception("Wrong repeated count model");
            }
        });
        Check("hash path avoids a membership scan on this workload", () => {
            var comparer = new CountingComparer(); var input = Dataset.Make(512, 512);
            Equal(Deduplication.Hash(input, comparer), input);
            if (comparer.Equalities >= 512) throw new Exception("Unexpected equality scan");
        });
        Check("forced collisions preserve correctness and expose quadratic work", () => {
            var comparer = new CountingComparer(constantHash: true); var input = Dataset.Make(128, 128);
            Equal(Deduplication.Hash(input, comparer), input);
            if (comparer.Equalities != 128L * 127 / 2) throw new Exception("Collision chain not exercised");
            Equal(Deduplication.Hash(new[] { "B", "A", "B" }, comparer), new[] { "B", "A" });
        });
        Check("duplicate counts and first-occurrence order", () => {
            Equal(Deduplication.DuplicateSummary(new[] { "B2", "A1", "B2", "C3", "A1" }),
                new[] { new OrderCount("B2", 2), new OrderCount("A1", 2) });
            Equal(Deduplication.DuplicateSummary(Array.Empty<string>()), Array.Empty<OrderCount>());
            Equal(Deduplication.DuplicateSummary(new[] { "A", "B" }), Array.Empty<OrderCount>());
            Equal(Deduplication.DuplicateSummary(new[] { "A", "A", "A" }), new[] { new OrderCount("A", 3) });
        });
        Console.WriteLine($"{passed} checks passed.");
    }

    private sealed class CountingComparer(bool constantHash = false) : IEqualityComparer<string>
    {
        public long Equalities { get; private set; }
        public bool Equals(string? x, string? y) { Equalities++; return StringComparer.Ordinal.Equals(x, y); }
        public int GetHashCode(string value) => constantHash ? 1 : StringComparer.Ordinal.GetHashCode(value);
    }
}
