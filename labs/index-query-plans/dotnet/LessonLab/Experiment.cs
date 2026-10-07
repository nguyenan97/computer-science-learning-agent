using System.Diagnostics;
using System.Globalization;

public static class Experiment
{
    private static string F(double value) => value.ToString("F4", CultureInfo.InvariantCulture);
    private static double Median(double[] values) { var copy = values.Order().ToArray(); return copy[copy.Length / 2]; }

    public static void Run()
    {
        EventRow[] rows = Database.Generate(20_000);
        using (var db = new Database())
        {
            db.Insert(rows); db.SetIndexes(IndexLayout.Both);
            Console.WriteLine($"# SQLite={db.Version}; query warmups=3, rounds=9; pageSize=4096; journal=DELETE; synchronous=FULL");
            Console.WriteLine("kind,case,path,n,matches,amount,medianMs,minMs,maxMs,allocatedDbBytes");
            foreach (int end in new[] { 10, 1000, 10000 })
            {
                AccessPath[] paths = [AccessPath.Scan, AccessPath.Thin, AccessPath.Covering];
                var expected = Database.Reference(rows, 1, 0, end);
                var commands = paths.Select(p => db.Query(p, 1, 0, end)).ToArray();
                try
                {
                    foreach (var cmd in commands)
                    { cmd.Prepare(); for (int warmup = 0; warmup < 3; warmup++) Database.Read(cmd); }
                    var times = paths.Select(_ => new double[9]).ToArray();
                    for (int round = 0; round < 9; round++)
                        for (int slot = 0; slot < paths.Length; slot++)
                        {
                            int i = (slot + round) % paths.Length; // Rotate execution order.
                            var watch = Stopwatch.StartNew();
                            Totals result = Database.Read(commands[i]);
                            watch.Stop();
                            if (result != expected) throw new InvalidOperationException("Measured query changed the answer.");
                            times[i][round] = watch.Elapsed.TotalMilliseconds;
                        }
                    for (int i = 0; i < paths.Length; i++)
                    {
                        Console.WriteLine($"query,end={end},{paths[i]},{rows.Length},{expected.Count},{expected.Amount}," +
                            $"{F(Median(times[i]))},{F(times[i].Min())},{F(times[i].Max())},{db.AllocatedBytes}");
                        Console.WriteLine($"# plan end={end} {paths[i]}: {db.Plan(paths[i], 1, 0, end)}");
                    }
                }
                finally { foreach (var cmd in commands) cmd.Dispose(); }
            }
        }
        EventRow[] writeRows = Database.Generate(5000);
        // Fresh databases; schema/index creation excluded, transaction+inserts+commit included.
        IndexLayout[] layouts = [IndexLayout.None, IndexLayout.Thin, IndexLayout.Covering];
        var writes = layouts.Select(_ => new double[5]).ToArray();
        var sizes = new long[layouts.Length];
        for (int round = -1; round < 5; round++) // One unrecorded batch per layout.
            for (int slot = 0; slot < layouts.Length; slot++)
            {
                int i = (slot + Math.Max(round, 0)) % layouts.Length;
                using var db = new Database(); db.SetIndexes(layouts[i]);
                var watch = Stopwatch.StartNew(); db.Insert(writeRows); watch.Stop();
                if (db.Run(AccessPath.Scan, 1, 0, 2500) != Database.Reference(writeRows, 1, 0, 2500))
                    throw new InvalidOperationException("Write experiment changed the answer.");
                if (round >= 0) writes[i][round] = watch.Elapsed.TotalMilliseconds;
                sizes[i] = db.AllocatedBytes;
            }
        for (int i = 0; i < layouts.Length; i++)
            Console.WriteLine($"insert,batch,{layouts[i]},{writeRows.Length},4500," +
                $"{Database.Reference(writeRows, 1, 0, 2500).Amount},{F(Median(writes[i]))}," +
                $"{F(writes[i].Min())},{F(writes[i].Max())},{sizes[i]}");
    }
}
