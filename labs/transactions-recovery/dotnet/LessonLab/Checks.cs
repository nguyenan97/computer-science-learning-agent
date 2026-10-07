public static class Checks
{
    private static void Require(bool ok, string why) { if (!ok) throw new Exception(why); }
    private static void Throws<T>(Action action) where T : Exception
    {
        try { action(); } catch (T) { return; }
        throw new Exception($"Expected {typeof(T).Name}.");
    }
    public static async Task Run()
    {
        using var store = new Store();
        using (var c = Store.Open(store.FilePath)) Require(Store.Engine(c) == "3.50.4", "Unexpected engine version.");
        var broken = await Schedules.Run(store.FilePath, 7, 5, Strategy.Blind);
        Require(broken.Remaining == 5 && broken.Reserved == 12, "Lost-update witness missing.");
        int cases = 0;
        for (int initial = 0; initial <= 8; initial++)
            for (int a = 1; a <= 5; a++)
                for (int b = 1; b <= 5; b++)
                {
                    store.Reset(initial); var actual = await Schedules.Run(store.FilePath, a, b, Strategy.Retry);
                    // Independent serial business model: no SQL, version predicate or retry state.
                    int left = initial, total = 0, commits = 0;
                    bool acceptA = a <= left; if (acceptA) { left -= a; total += a; commits++; }
                    bool acceptB = b <= left; if (acceptB) { left -= b; total += b; commits++; }
                    Require(actual.Remaining == left && actual.Reserved == total && actual.Version == commits, "Serial oracle differs.");
                    Require(actual.First == (acceptA ? Outcome.Committed : Outcome.Rejected)
                        && actual.Second == (acceptB ? Outcome.Committed : Outcome.Rejected), "Wrong admission decision.");
                    Require(actual.Remaining + actual.Reserved == initial, "Conservation failed."); cases++;
                }
        store.Reset(10); Require(Schedules.Snapshot(store.FilePath) == 517, "Stale snapshot not rejected.");
        store.Reset(10);
        using (var c = Store.Open(store.FilePath))
        {
            var old = Store.Read(c);
            Throws<InvalidOperationException>(() => Store.Reserve(c, "fail", 7, old, failAfterUpdate: true));
            Require(Store.Read(c) == old && Store.Reserved(c) == 0, "Rollback left half a reservation.");
            Require(Store.Reserve(c, "same", 7, old) == Outcome.Committed, "Initial request failed.");
            Require(Store.Reserve(c, "same", 7, old) == Outcome.Replayed, "Replay consumed stock.");
            Require(Store.Read(c).Available == 3 && Store.Reserved(c) == 7, "Replay changed the result.");
            Throws<ArgumentException>(() => Store.Reserve(c, "same", 6, old));
            Throws<ArgumentException>(() => Store.Reserve(c, " ", 1, old));
            Throws<ArgumentOutOfRangeException>(() => Store.Reserve(c, "bad", 0, old));
            Throws<ArgumentOutOfRangeException>(() => store.Reset(1001));
        }
        store.Reset(1000);
        using (var c = Store.Open(store.FilePath))
        {
            Require(Store.Reserve(c, new string('x', 100), 1000, Store.Read(c)) == Outcome.Committed, "Upper-bound reservation failed.");
            Require(Store.Read(c) == new StockView(0, 1) && Store.Reserved(c) == 1000, "Upper-bound totals differ.");
            Require(Store.Reserve(c, "empty", 1, Store.Read(c)) == Outcome.Rejected, "Empty stock admitted a request.");
            Throws<ArgumentOutOfRangeException>(() => Store.Reserve(c, "large", 1001, Store.Read(c)));
            Throws<ArgumentException>(() => Store.Reserve(c, new string('x', 101), 1, Store.Read(c)));
        }
        var before = await Crash.Run("before"); var after = await Crash.Run("after");
        Require(before.A == 100 && before.B == 100 && before.Noise == 0, "Uncommitted work became visible.");
        Require(after.A == 90 && after.B == 110 && after.Noise == 64, "Acknowledged commit lost.");
        Console.WriteLine($"PASS: {cases} serial-oracle schedules; stale snapshot=517; rollback/replay; 2 crash boundaries.");
    }
}
