public static class Experiment
{
    public static async Task Run()
    {
        using var store = new Store();
        Console.WriteLine("strategy,q2,remaining,reserved,conflicts,retries,first,second,conserves");
        foreach (int q2 in new[] { 5, 2 })
            foreach (var strategy in Enum.GetValues<Strategy>())
            {
                store.Reset(10); var r = await Schedules.Run(store.FilePath, 7, q2, strategy);
                Console.WriteLine($"{strategy},{q2},{r.Remaining},{r.Reserved},{r.Conflicts},{r.Retries}," +
                    $"{r.First},{r.Second},{r.Remaining + r.Reserved == 10}");
            }
        foreach (string point in new[] { "before", "after" })
        {
            var r = await Crash.Run(point);
            Console.WriteLine($"# crash={point}; A={r.A}; B={r.B}; noise={r.Noise}; walFramesPresent={r.WalBytes > 32}");
        }
    }
}
