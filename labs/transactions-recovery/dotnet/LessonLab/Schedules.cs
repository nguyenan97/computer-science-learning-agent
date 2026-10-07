using System.Collections.Concurrent;

public sealed record RunResult(Outcome First, Outcome Second, int Conflicts, int Retries,
    int Remaining, long Reserved, int Version, string[] Trace);

public static class Schedules
{
    private static TaskCompletionSource<bool> Gate() => new(TaskCreationOptions.RunContinuationsAsynchronously);
    public static async Task<RunResult> Run(string path, int q1, int q2, Strategy strategy)
    {
        if (!Enum.IsDefined(strategy)) throw new ArgumentOutOfRangeException(nameof(strategy));
        var read1 = Gate(); var read2 = Gate(); var written1 = Gate();
        var log = new ConcurrentQueue<string>(); int conflicts = 0, retries = 0;
        var first = Task.Run(async () => {
            using var c = Store.Open(path); var s = Store.Read(c);
            log.Enqueue($"T1 READ available={s.Available} version={s.Version}"); read1.SetResult(true);
            await read2.Task.WaitAsync(TimeSpan.FromSeconds(20));
            var result = Store.Reserve(c, "A", q1, s, strategy != Strategy.Blind);
            log.Enqueue($"T1 {result}"); written1.SetResult(true); return result;
        });
        var second = Task.Run(async () => {
            await read1.Task.WaitAsync(TimeSpan.FromSeconds(20));
            using var c = Store.Open(path); var s = Store.Read(c);
            log.Enqueue($"T2 READ available={s.Available} version={s.Version}"); read2.SetResult(true);
            await written1.Task.WaitAsync(TimeSpan.FromSeconds(20));
            var result = Store.Reserve(c, "B", q2, s, strategy != Strategy.Blind);
            log.Enqueue($"T2 {result}");
            if (result == Outcome.Conflict)
            {
                conflicts++;
                if (strategy == Strategy.Retry)
                {
                    retries++; s = Store.Read(c);
                    log.Enqueue($"T2 READ available={s.Available} version={s.Version}");
                    result = Store.Reserve(c, "B", q2, s);
                    if (result == Outcome.Conflict) conflicts++;
                    log.Enqueue($"T2 {result}");
                }
            }
            return result;
        });
        var results = await Task.WhenAll(first, second).WaitAsync(TimeSpan.FromSeconds(25));
        using var final = Store.Open(path); var stock = Store.Read(final);
        return new RunResult(results[0], results[1], conflicts, retries,
            stock.Available, Store.Reserved(final), stock.Version, log.ToArray());
    }
    public static int Snapshot(string path)
    {
        using var reader = Store.Open(path); using var writer = Store.Open(path);
        using var tx = reader.BeginTransaction(deferred: true);
        var old = Store.Read(reader, tx);
        if (Store.Reserve(writer, "snapshot-writer", 7, Store.Read(writer)) != Outcome.Committed)
            throw new Exception("Writer did not commit.");
        if (Store.Read(reader, tx) != old) throw new Exception("Snapshot changed.");
        int code;
        try { Store.Exec(reader, "UPDATE Stock SET Available=Available-1 WHERE Id=1", tx);
            throw new Exception("Stale snapshot unexpectedly wrote."); }
        catch (Microsoft.Data.Sqlite.SqliteException ex) when (ex.SqliteErrorCode == 5)
        { code = ex.SqliteExtendedErrorCode; }
        tx.Rollback();
        if (Store.Read(reader).Available != 3 || code != 517) throw new Exception("Unexpected pinned-version snapshot result.");
        return code;
    }
}
